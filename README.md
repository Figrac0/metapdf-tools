# extract_and_decode.py
- Extracts and decodes hexadecimal <...> Tj strings from a QDF file using a provided CMap for accurate character mapping.
<br/>
# extract_pdf_elements.py
- Parses a PDF to locate beginbfrange...endbfrange blocks and all <...> Tj text drawing operators. Useful for manual analysis of embedded text mappings.
<br/>
# modify_qdf.py
- Replaces a specified hex-encoded text string inside a QDF dump and reconstructs the modified PDF file. Ideal for precise, low-level text edits.
<br/>
# patch_and_redact.py
- Performs direct in-place text substitution within a PDF by masking and injecting visible replacement text. Minimal structural changes.
<br/>
# pdf_diff.py
- Compares two PDF files for differences in structure, metadata, XREF tables, and object references. Helpful for validating integrity post-modification.
<br/>
# pdf_full_metadata.py
Performs a complete audit of a PDF file, extracting structural metadata, fonts, embedded files, and all object references for inspection or logging.
