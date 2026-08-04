#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ahn2ged.py – Convert Ahnenblatt .ahn files (v2.x) to GEDCOM 5.5.1

Usage:
    python3 ahn2ged.py input.ahn [output.ged]

If only the input file is given, the output name is derived by replacing
the extension with .ged (or appending .ged).

This is a reverse-engineered converter for the binary .ahn format used by
Ahnenblatt (tested with version 2.99h). It is not officially supported and
may miss some obscure fields or newer version features.
"""

from __future__ import print_function
import sys
import os
import argparse
from datetime import datetime


def parse_ahn(data):
    """
    Parse the binary .ahn structure into a list of records.
    Each record is a list of (level, tag, value) tuples.
    """
    records = []
    current = []
    i = 0
    n = len(data)

    while i < n - 4:
        if data[i:i+3] == b'\xbf\x01\x00':
            level = data[i+3]
            i += 4

            tag = None
            value = None

            # Tag declaration: \xc0 <len> \x00 <TAG\x00>
            if i < n and data[i] == 0xc0:
                taglen = data[i+1]
                if 1 <= taglen <= 32 and i + 3 + taglen <= n:
                    tag_bytes = data[i+3:i+3+taglen]
                    tag = tag_bytes.rstrip(b'\x00').decode('ascii', errors='replace')
                    i += 3 + taglen
                else:
                    continue
            else:
                continue

            # Optional value
            if i < n:
                if data[i] == 0xc1:                      # cross-reference ID
                    plen = data[i+1]
                    if 1 <= plen <= 64 and i + 3 + plen <= n:
                        value = data[i+3:i+3+plen].rstrip(b'\x00').decode('ascii', errors='replace')
                        i += 3 + plen
                elif data[i] == 0xc2:                    # short string / pointer / empty
                    if data[i+1:i+3] == b'\x00\x00':
                        value = None
                        i += 3
                    else:
                        vlen = data[i+1]
                        if 1 <= vlen <= 512 and i + 3 + vlen <= n:
                            value = data[i+3:i+3+vlen].rstrip(b'\x00').decode('latin-1', errors='replace')
                            i += 3 + vlen
                        else:
                            i += 2
                elif data[i:i+3] == b'\xc3\x01\x00':     # typed string value
                    if i + 7 <= n:
                        strlen = data[i+5]
                        if 0 <= strlen <= 4000 and i + 7 + strlen <= n:
                            value = data[i+7:i+7+strlen].rstrip(b'\x00').decode('latin-1', errors='replace')
                            i += 7 + strlen
                        else:
                            i += 6
                    else:
                        i += 3

            if tag:
                # Start a new top-level record when we see a level-0 record type
                if level == 0 and tag in (
                    'INDI', 'FAM', 'SUBM', 'SOUR', 'NOTE',
                    'OBJE', 'REPO', 'HEAD', 'TRLR'
                ):
                    if current:
                        records.append(current)
                    current = [(level, tag, value)]
                else:
                    if current is not None:
                        current.append((level, tag, value))
        else:
            i += 1

    if current:
        records.append(current)
    return records


def normalize_date(s):
    """Best-effort conversion of various date formats to GEDCOM style."""
    if not s:
        return s
    s = s.strip()
    # Already looks like GEDCOM (contains month abbreviation)
    if any(m in s.upper() for m in
           ('JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
            'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC')):
        return s
    # German / European numeric dd.mm.yyyy or d.m.yyyy
    parts = s.replace('/', '.').replace('-', '.').split('.')
    if len(parts) == 3:
        try:
            d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
            months = ['', 'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                      'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
            if 1 <= m <= 12 and 1 <= d <= 31:
                return f"{d:02d} {months[m]} {y}"
        except ValueError:
            pass
    return s


def record_to_gedcom_lines(record):
    """Convert one parsed record into GEDCOM text lines."""
    lines = []
    for level, tag, value in record:
        # Skip pure internal change-tracking if desired (keep them for now)
        if value is not None and value != '':
            # Special handling for NAME: GEDCOM likes "GIVN /SURN/"
            lines.append((level, tag, value))
        else:
            lines.append((level, tag, None))
    return lines


def build_gedcom(records, source_filename):
    """Assemble a complete GEDCOM 5.5.1 document."""
    out = []
    out.append("0 HEAD")
    out.append("1 SOUR ahn2ged")
    out.append("2 NAME Ahn2Ged (Ahnenblatt .ahn → GEDCOM converter)")
    out.append("2 VERS 1.0")
    out.append("1 DEST ANY")
    out.append(f"1 DATE {datetime.now().strftime('%d %b %Y').upper()}")
    out.append("1 GEDC")
    out.append("2 VERS 5.5.1")
    out.append("2 FORM LINEAGE-LINKED")
    out.append("1 CHAR UTF-8")
    out.append(f"1 FILE {os.path.basename(source_filename)}")
    out.append("1 NOTE Converted from Ahnenblatt .ahn format by ahn2ged.py")
    out.append("2 CONT Reverse-engineered converter – some data may be incomplete.")

    for rec in records:
        if not rec:
            continue
        top_tag = rec[0][1]
        if top_tag == 'SUBM':
            continue

        # Pre-scan for GIVN / SURN so we can emit a conventional NAME line
        givn = None
        surn = None
        for level, tag, value in rec:
            if tag == 'GIVN' and value:
                givn = value
            elif tag == 'SURN' and value:
                surn = value

        name_emitted = False

        for level, tag, value in rec:
            # When we hit the NAME tag, emit a proper "Given /Surname/" line
            if tag == 'NAME' and level == 1 and not name_emitted:
                if givn or surn:
                    name_parts = []
                    if givn:
                        name_parts.append(givn)
                    if surn:
                        name_parts.append(f"/{surn}/")
                    out.append(f"1 NAME {' '.join(name_parts)}")
                    name_emitted = True
                else:
                    out.append("1 NAME")
                    name_emitted = True
                continue  # still emit the original GIVN/SURN sub-tags below

            if value is not None and value != '':
                if tag == 'DATE':
                    value = normalize_date(value)
                # Escape literal @ characters that are not pointers
                if not (value.startswith('@') and value.endswith('@')):
                    value = value.replace('@', '@@')

                # Level-0 records MUST be written as:  0 @I123@ INDI
                # (not  0 INDI @I123@) – many programs reject the latter for FAM
                if level == 0 and value.startswith('@') and value.endswith('@'):
                    out.append(f"0 {value} {tag}")
                    continue

                # Split long NOTE lines
                if tag == 'NOTE' and len(value) > 200:
                    out.append(f"{level} {tag} {value[:200]}")
                    rest = value[200:]
                    while rest:
                        chunk = rest[:200]
                        rest = rest[200:]
                        out.append(f"{level+1} CONT {chunk}")
                else:
                    out.append(f"{level} {tag} {value}")
            else:
                # Avoid emitting an empty NAME again
                if tag == 'NAME' and name_emitted:
                    continue
                out.append(f"{level} {tag}")

    out.append("0 TRLR")
    return "\n".join(out) + "\n"


def convert(input_path, output_path=None):
    if not os.path.isfile(input_path):
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        return 1

    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = base + ".ged"

    print(f"Reading: {input_path}")
    with open(input_path, "rb") as f:
        data = f.read()

    # Quick sanity check
    if not data.startswith(b'dbk'):
        print("Warning: file does not start with expected 'dbk' signature.",
              file=sys.stderr)
    if b'Ahnenblatt' not in data[:200]:
        print("Warning: 'Ahnenblatt' string not found in header – "
              "may not be a valid .ahn file.", file=sys.stderr)

    print("Parsing binary structure …")
    records = parse_ahn(data)
    print(f"Found {len(records)} top-level records")

    from collections import Counter
    types = Counter(r[0][1] for r in records if r)
    for t, c in types.most_common():
        print(f"  {t}: {c}")

    print(f"Writing GEDCOM: {output_path}")
    gedcom_text = build_gedcom(records, input_path)

    # Write as UTF-8
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(gedcom_text)

    print("Done.")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Convert Ahnenblatt .ahn files to GEDCOM 5.5.1"
    )
    parser.add_argument("input", help="Input .ahn file")
    parser.add_argument("output", nargs="?", default=None,
                        help="Output .ged file (default: input name + .ged)")
    args = parser.parse_args()

    try:
        return convert(args.input, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
