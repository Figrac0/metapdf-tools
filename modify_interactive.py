# modify_interactive.py

import re
import sys

def load_cmap_from_pdf(text):
    """Extract the first beginbfrange...endbfrange block and build glyph->unicode map."""
    cmap = {}
    m = re.search(r'beginbfrange([\s\S]*?)endbfrange', text)
    if not m:
        raise ValueError("No beginbfrange block found in PDF.")
    block = m.group(1)
    for line in block.strip().splitlines():
        entry = re.match(r'<([0-9A-Fa-f]+)><([0-9A-Fa-f]+)><([0-9A-Fa-f]+)>', line.strip())
        if entry:
            start, end, uni0 = entry.groups()
            s, e, u0 = int(start, 16), int(end, 16), int(uni0, 16)
            for i, code in enumerate(range(s, e + 1)):
                cmap[f"{code:04x}".lower()] = f"{u0 + i:04x}".lower()
    return cmap

def interactive_modify(input_pdf, output_pdf):
    # Read PDF text
    with open(input_pdf, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Load CMap
    cmap = load_cmap_from_pdf(content)
    inv_cmap = {v: k for k, v in cmap.items()}

    # Prompt user for hex and new text
    old_hex = input("Enter the <...>Tj hex to replace (without < >): ").strip()
    print("Original text:", ''.join(chr(int(cmap.get(old_hex[i:i+4], '0020'), 16)) 
                                  for i in range(0, len(old_hex), 4)))
    new_text = input("Enter the replacement text: ").strip()

    # Convert new_text to hex sequence
    codes_new = []
    for ch in new_text:
        uni = f"{ord(ch):04x}"
        if uni not in inv_cmap:
            print(f"Character '{ch}' not in CMap, using space.")
            code = '0003'
        else:
            code = inv_cmap[uni]
        codes_new.append(code)
    new_hex = ''.join(codes_new)

    # Pad/truncate new_hex to match length of old_hex
    if len(new_hex) < len(old_hex):
        new_hex += '0003' * ((len(old_hex) - len(new_hex)) // 4)
    elif len(new_hex) > len(old_hex):
        new_hex = new_hex[:len(old_hex)]

    print(f"New hex sequence: {new_hex}")
    print(f"Old length: {len(old_hex)}, New length: {len(new_hex)}")

    # Replace in content
    pattern = re.compile(rf'<{re.escape(old_hex)}>Tj')
    modified_content, count = pattern.subn(f'<{new_hex}>Tj', content)

    if count == 0:
        print("No occurrences replaced.")
    else:
        print(f"Replaced {count} occurrence(s).")

    # Write out
    with open(output_pdf, 'w', encoding='utf-8', errors='ignore') as f:
        f.write(modified_content)
    print(f"Modified file saved as {output_pdf}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python modify_interactive.py <input_unpacked.pdf> <output_unpacked.pdf>")
        sys.exit(1)
    interactive_modify(sys.argv[1], sys.argv[2])
