# modify_pdf_tj.py

import re
import sys

def modify_hex_in_pdf(input_path, output_path, old_hex, new_hex):
    """
    Replace occurrences of <old_hex>Tj with <new_hex>Tj in the unpacked PDF text.
    """
    # Read the unpacked PDF as text
    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Build regex pattern to match the exact <old_hex>Tj
    pattern = re.compile(rf'<{re.escape(old_hex)}>Tj')

    # Perform replacement
    modified_content, count = pattern.subn(f'<{new_hex}>Tj', content)

    if count == 0:
        print(f"No occurrences of <{old_hex}>Tj found.")
    else:
        print(f"Replaced {count} occurrence(s) of <{old_hex}>Tj with <{new_hex}>Tj.")

    # Write modified content to output file
    with open(output_path, 'w', encoding='utf-8', errors='ignore') as f:
        f.write(modified_content)

def main():
    if len(sys.argv) != 5:
        print("Usage: python modify_pdf_tj.py <input_unpacked.pdf> <old_hex> <new_hex> <output_unpacked.pdf>")
        sys.exit(1)

    _, input_pdf, old_hex, new_hex, output_pdf = sys.argv
    modify_hex_in_pdf(input_pdf, output_pdf, old_hex, new_hex)
    print(f"Modified file written to: {output_pdf}")

if __name__ == "__main__":
    main()
