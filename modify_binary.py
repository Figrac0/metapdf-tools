#!/usr/bin/env python3
import sys, subprocess, re

def replace_within_streams(data: bytes, old_hex: str, new_hex: str):
    # составляем regex: (?i) — регистронезависимо, \s* — любые пробелы/переносы
    old_pat = re.compile(
        rb'(?i)<'+bytes.fromhex(old_hex)+rb'>\s*Tj'
    )
    def repl(match):
        m = match.group(0)
        # внутри найденного фрагмента меняем только байты старого HEX
        return m.replace(bytes.fromhex(old_hex), bytes.fromhex(new_hex), 1)

    # разбиваем на куски: до первого stream, сами stream-блоки, после
    parts = re.split(rb'(stream[\r\n]+)', data, flags=re.IGNORECASE)
    if len(parts) == 1:
        raise RuntimeError("Не найден ни один stream-блок")
    out = parts[0]
    total = 0

    # проходим по парам (delimiter, chunk)
    for i in range(1, len(parts)-1, 2):
        delim = parts[i]
        chunk = parts[i+1]
        # находим конец этого стрима
        m = re.search(rb'(?i)(endstream)', chunk)
        if not m:
            out += delim + chunk
            continue
        body, tail = chunk[:m.start()], chunk[m.start():]
        new_body, cnt = old_pat.subn(repl, body)
        total += cnt
        out += delim + new_body + tail

    # добавляем последний кусок после всех stream…endstream
    out += parts[-1]
    return out, total

def main():
    if len(sys.argv) != 6:
        print("Usage: modify_binary.py <orig.pdf> <qdf.pdf> <old_hex> <new_hex> <out.pdf>")
        sys.exit(1)
    orig, qdf, old_hex, new_hex, outp = sys.argv[1:]

    # 1) Распаковка
    subprocess.run([
        "qpdf","--qdf","--stream-data=uncompress","--object-streams=disable",
        orig, qdf
    ], check=True)

    # 2) Читаем и делаем замену
    raw = open(qdf,"rb").read()
    patched, count = replace_within_streams(raw, old_hex, new_hex)
    print(("⚠️ Не найдено вхождений" if count==0 else f"✅ Заменено {count} вхождений"))
    open(qdf,"wb").write(patched)

    # 3) «Чинят» QDF-файл
    fixed = qdf.replace(".pdf","_fixed.qdf.pdf")
    subprocess.run(["fix-qdf", qdf, fixed], check=True)

    # 4) Сборка обратно
    subprocess.run(["qpdf","--stream-data=compress", fixed, outp], check=True)
    print("✔ Готово:", outp)

if __name__=="__main__":
    main()
