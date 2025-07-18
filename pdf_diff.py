#!/usr/bin/env python3
import sys, subprocess
from difflib import unified_diff

import pikepdf

def run_qpdf(args, path):
    """Возвращает список строк вывода qpdf."""
    p = subprocess.run(["qpdf", *args, path], capture_output=True, text=True)
    return p.stdout.splitlines()

def simple(v):
    """Приводит pikepdf-объект к простому представлению."""
    if v is None or isinstance(v, (bool, int, float, str)):
        return v
    try:
        return repr(v)
    except:
        return str(v)

def load_info(path):
    pdf = pikepdf.Pdf.open(path)
    info = {}
    info["version"]   = pdf.pdf_version
    info["encrypted"] = pdf.is_encrypted
    # Trailer
    try:
        tr = pdf.trailer.as_dict()
    except:
        tr = {}
    info["trailer"] = {k: simple(v) for k, v in tr.items()}
    # Info-словарь
    info["docinfo"] = {k: simple(pdf.docinfo.get(k)) for k in pdf.docinfo}
    # XREF и линейризация
    info["xref"]          = run_qpdf(["--show-xref"], path)
    info["linearization"] = run_qpdf(["--show-linearization"], path)
    # Корневой каталог (просто repr)
    info["root"] = simple(pdf.Root)
    # Первые 20 объектов
    objs = {}
    for i, obj in enumerate(pdf.objects):
        if i >= 20: break
        objs[str(i)] = simple(obj)
    info["objects"] = objs
    pdf.close()
    return info

def pretty_section(a, b, title):
    print(f"===== {title} =====")
    if isinstance(a, list) and isinstance(b, list):
        left, right = a, b
    else:
        import json
        left  = json.dumps(a,  indent=2, ensure_ascii=False).splitlines()
        right = json.dumps(b,  indent=2, ensure_ascii=False).splitlines()
    for l in unified_diff(left, right, lineterm="", fromfile="orig", tofile="mod"):
        print(l)
    print()

if __name__=="__main__":
    if len(sys.argv)!=3:
        print("Usage: pdf_diff.py original.pdf modified.pdf")
        sys.exit(1)

    orig, mod = sys.argv[1], sys.argv[2]
    a = load_info(orig)
    b = load_info(mod)

    print(f"--- DIFF {orig} vs {mod} ---\n")
    pretty_section(a["version"],   b["version"],   "PDF VERSION")
    pretty_section(a["encrypted"], b["encrypted"], "ENCRYPTED")
    pretty_section(a["trailer"],   b["trailer"],   "TRAILER")
    pretty_section(a["docinfo"],   b["docinfo"],   "DOCINFO")
    pretty_section(a["root"],      b["root"],      "ROOT CATALOG")
    pretty_section(a["xref"],      b["xref"],      "XREF TABLE")
    pretty_section(a["linearization"], b["linearization"], "LINEARIZATION")
    pretty_section(a["objects"],   b["objects"],   "FIRST 20 OBJECTS")
