#!/usr/bin/env python3
import sys
import fitz  # pip install pymupdf

def patch_and_redact(input_pdf, output_pdf, old_text, new_text,
                     fontsize=12, fontname="helv", fill=(1,1,1)):
    doc = fitz.open(input_pdf)
    # найдём только на первой странице (или по всем, если нужно)
    page = doc[0]
    insts = page.search_for(old_text)
    if not insts:
        print("❌ Не нашлось текста для замены.")
        sys.exit(1)
    # возьмём первый найденный прямоугольник
    r = insts[0]
    # создаём редакт-ант
    page.add_redact_annot(r, fill=fill)
    # применяем редактирование (удалит старый текст)
    doc.apply_redactions()
    # вставляем новый текст в ту же позицию
    page.insert_text((r.x0, r.y0), new_text,
                     fontsize=fontsize, fontname=fontname)
    # инкрементальное сохранение (append only)
    doc.save(output_pdf, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
    doc.close()
    print(f"✔️  Готово: {output_pdf}")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python patch_and_redact.py original.pdf final.pdf old_text new_text")
        sys.exit(1)
    _, inp, outp, old, new = sys.argv
    patch_and_redact(inp, outp, old, new)
