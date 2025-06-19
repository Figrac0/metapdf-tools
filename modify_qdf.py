#!/usr/bin/env python3
import re
import sys
import shutil
import subprocess

def load_cmap_from_pdf(pdf_bytes):
    text = pdf_bytes.decode('utf-8', errors='ignore')
    ranges = re.findall(r'beginbfrange\s+([\s\S]*?)endbfrange', text)
    if not ranges:
        raise ValueError("Не найдена таблица CMap (beginbfrange) в PDF.")
    cmap = {}
    for block in ranges:
        for line in block.strip().splitlines():
            m = re.match(r'<([0-9A-Fa-f]+)><([0-9A-Fa-f]+)><([0-9A-Fa-f]+)>', line.strip())
            if m:
                start, end, uni0 = m.groups()
                s, e, u0 = int(start,16), int(end,16), int(uni0,16)
                for i, code in enumerate(range(s, e+1)):
                    cmap[f"{code:04x}"] = f"{u0+i:04x}"
    return cmap

def replace_text_in_qdf(input_qdf, output_qdf, old_hex, new_text):
    data = open(input_qdf, "rb").read()
    cmap = load_cmap_from_pdf(data)
    inv = {v:k for k,v in cmap.items()}

    # убедимся, что hex→текст правильно работает
    old_txt = "".join(chr(int(cmap.get(old_hex[i:i+4],"0020"),16))
                      for i in range(0,len(old_hex),4))
    print(f"Исходный текст: «{old_txt}»")

    # собираем новый hex
    codes = []
    for ch in new_text:
        u = f"{ord(ch):04x}"
        codes.append(inv.get(u, "0003"))
    new_hex = "".join(codes)

    print(f"Новая hex-строка: {new_hex}")
    patt = re.compile(rb"<"+old_hex.encode()+rb">Tj")
    repl = b"<"+new_hex.encode()+b">Tj"
    new_data, cnt = patt.subn(repl, data, count=1)
    if cnt==0:
        print("⚠️  Не найдено ни одного вхождения.")
        sys.exit(1)
    print(f"✅  Заменено {cnt} вхождений.")
    open(output_qdf,"wb").write(new_data)

def fix_qdf(src, dst):
    if shutil.which("fix-qdf"):
        with open(dst, "wb") as out:
            subprocess.run(["fix-qdf", src], stdout=out, check=True)
    else:
        print(f"Запустите вручную: fix-qdf < {src} > {dst}")

def main():
    if len(sys.argv)!=3:
        print("Usage: python modify_qdf.py <in.qdf.pdf> <out.qdf.pdf>")
        sys.exit(1)
    inp, outp = sys.argv[1:]
    old = input("Введите старый hex (без <>): ").strip()
    new = input("Введите новый текст: ").strip()
    replace_text_in_qdf(inp, outp, old, new)
    fixed = outp.rsplit(".",1)[0] + "_fixed.pdf"
    fix_qdf(outp, fixed)
    print(f"🎉 Финальный QDF файл: {fixed}")

if __name__=="__main__":
    main()
