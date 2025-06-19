# extract_pdf_elements.py

import re
import sys

def extract_bfranges(text):
    """Extract all beginbfrange...endbfrange blocks."""
    pattern = re.compile(r'beginbfrange[\s\S]*?endbfrange', re.IGNORECASE)
    return pattern.findall(text)

def extract_tj_hex(text):
    """Extract all hex streams used in <...>Tj operators."""
    pattern = re.compile(r'<([0-9A-Fa-f]+)>Tj')
    return pattern.findall(text)

def main(pdf_path):
    try:
        with open(pdf_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{pdf_path}' not found.")
        sys.exit(1)
    
    # Extract and print CMap ranges
    ranges = extract_bfranges(content)
    print("=== Found beginbfrange...endbfrange blocks ===\n")
    for idx, block in enumerate(ranges, 1):
        print(f"[Block {idx}]\n{block}\n")

    # Extract and print all <...>Tj hex strings
    hex_strings = extract_tj_hex(content)
    print("=== Found <...>Tj hex streams ===\n")
    for idx, hex_str in enumerate(hex_strings, 1):
        print(f"{idx}: {hex_str}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_pdf_elements.py full_unpacked.pdf")
        sys.exit(1)
    main(sys.argv[1])
