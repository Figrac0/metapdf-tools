# extract_and_decode.py

import re
import sys

def parse_cmap_blocks(text):
    
    cmap = {}
    
    m = re.search(r'beginbfrange([\s\S]*?)endbfrange', text)
    if not m:
        print("Error: no beginbfrange block found.")
        return cmap
    block = m.group(1)
    
    for line in block.strip().splitlines():
        entry = re.match(r'<([0-9A-Fa-f]+)><([0-9A-Fa-f]+)><([0-9A-Fa-f]+)>', line.strip())
        if entry:
            start, end, uni0 = entry.groups()
            s, e, u0 = int(start, 16), int(end, 16), int(uni0, 16)
            for i, code in enumerate(range(s, e + 1)):
                cmap[f"{code:04x}"] = f"{u0 + i:04x}"
    return cmap

def extract_tj_hex(text):
    
    return re.findall(r'<([0-9A-Fa-f]+)>Tj', text)

def decode_hex_streams(hex_streams, cmap):
    
    decoded = []
    for hex_str in hex_streams:
        chars = []
        for i in range(0, len(hex_str), 4):
            code = hex_str[i:i+4].lower()
            uni_hex = cmap.get(code, "0020")  
            chars.append(chr(int(uni_hex, 16)))
        decoded.append((hex_str, ''.join(chars)))
    return decoded

def main(pdf_path):
    try:
        with open(pdf_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{pdf_path}' not found.")
        sys.exit(1)
    
    cmap = parse_cmap_blocks(content)
    if not cmap:
        print("No CMap mappings found. Exiting.")
        sys.exit(1)
    
    hex_streams = extract_tj_hex(content)
    unique_streams = list(dict.fromkeys(hex_streams))  
    decoded = decode_hex_streams(unique_streams, cmap)
    
    print("Decoded <...>Tj strings:\n")
    for idx, (hex_str, text) in enumerate(decoded, 1):
        print(f"{idx}. [{hex_str}] -> {text}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_and_decode.py full_unpacked.pdf")
        sys.exit(1)
    main(sys.argv[1])
