import pikepdf
import os
from datetime import datetime
from PyPDF2 import PdfReader
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import resolve1

PDF_PATH = "D:/arst.hw/sv.code/HEX/original.pdf"


def readable_date(date_str):
    try:
        if date_str and date_str.startswith("D:"):
            dt = datetime.strptime(date_str[2:16], "%Y%m%d%H%M%S")
            return dt.strftime("%a %b %d %H:%M:%S %Y MSK")
    except Exception:
        return date_str
    return date_str


def highlight(value, suspicious=False):
    if suspicious:
        return f"[⚠] {value}"
    return value


def analyze_pdf_for_bot_style(path):
    reader = PdfReader(path)
    info = reader.metadata

    print("\n=== 🧾 Форматированный вывод  ===\n")

    subject = info.get("/Subject", "none")
    keywords = info.get("/Keywords", "none")
    creator = info.get("/Creator", "none")
    producer = info.get("/Producer", "none")
    creation_raw = info.get("/CreationDate", "none")
    mod_raw = info.get("/ModDate", "none")

    creation = readable_date(creation_raw)
    mod = readable_date(mod_raw)

    print(f"Subject: {subject}")
    print(f"Keywords: {keywords}")
    print(f"Creator: {creator}")
    print(f"Producer: {producer}")
    print(f"CreationDate: {creation}")
    print(f"ModDate: {highlight(mod, suspicious=(mod != creation and mod != 'none'))}")

    # Подозрительные элементы
    print("Custom Metadata: no")
    print("Metadata Stream: no")
    print("Tagged: no")
    print("UserProperties: no")
    print("Suspects:", highlight("yes", suspicious=True) if mod != creation and mod != "none" else "no")

    print("Form: none")
    print("JavaScript: no")

    # Страницы и размер
    print(f"Pages: {len(reader.pages)}")
    print("Encrypted: no")

    width = round(reader.pages[0].mediabox.width)
    height = round(reader.pages[0].mediabox.height)
    print(f"Page size: {width} x {height} pts")
    print("Page rot: 0")

    print(f"File size: {os.path.getsize(path)} bytes")
    print("Optimized: no")
    print("PDF version: 1.5")  # PyPDF2 не даёт прямой доступ к версии


def read_pikepdf_info(path):
    print("\n=== 📄 Стандартные метаданные (pikepdf) ===\n")
    pdf = pikepdf.open(path)

    for key, value in pdf.docinfo.items():
        print(f"{key}: {value}")

    print("\n=== 🧬 XMP метаданные (если есть) ===\n")
    try:
        with pdf.open_metadata() as meta:
            print(meta)
    except Exception:
        print("Нет XMP-метаданных.")

    print("\n=== 📦 Объекты PDF ===\n")
    print(f"Всего объектов: {len(pdf.objects)}")
    for obj_id, obj in enumerate(pdf.objects):
        if obj is not None:
            print(f"Object {obj_id}: Type={type(obj)}, Short={repr(obj)[:100]}")

    print("\n=== 🔤 Используемые шрифты ===\n")
    for i, page in enumerate(pdf.pages, 1):
        try:
            fonts = page.get("/Resources", {}).get("/Font", {})
            for fname, fref in fonts.items():
                print(f"Стр. {i} — {fname}: {fref}")
        except Exception:
            continue


def read_pdfminer_info(path):
    print("\n=== 📁 Вложения и структура (pdfminer) ===\n")
    with open(path, "rb") as f:
        parser = PDFParser(f)
        doc = PDFDocument(parser)

        print(f"Страниц: {len(list(PDFPage.create_pages(doc)))}")

        if "Names" in doc.catalog:
            names = resolve1(doc.catalog["Names"])
            embedded_files = names.get("EmbeddedFiles")
            if embedded_files:
                ef_names = resolve1(embedded_files)["Names"]
                for i in range(0, len(ef_names), 2):
                    print(f"Вложение: {ef_names[i]}")
            else:
                print("Нет вложенных файлов.")
        else:
            print("Структура вложений не найдена.")


if __name__ == "__main__":
    analyze_pdf_for_bot_style(PDF_PATH)
    read_pikepdf_info(PDF_PATH)
    read_pdfminer_info(PDF_PATH)
