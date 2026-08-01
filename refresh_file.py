#!/usr/bin/env python3
"""
Refresh a Pythonista file by creating a new file identity
(so that cached editor/breakpoint state is cleared).

Usage:
    python3 refresh_file.py path/to/script.py
    python3 refresh_file.py script1.py script2.py ...
"""

import os
import sys
import shutil
import filecmp


def refresh_file(path: str) -> None:
    path = os.path.abspath(path)

    if not os.path.isfile(path):
        raise FileNotFoundError(f"File does not exist: {path}")

    backup = path + ".bak"

    if os.path.exists(backup):
        raise FileExistsError(
            f"Backup file already exists: {backup}\n"
            "Please remove or rename it before running this command."
        )

    # 1. Rename original → backup
    os.rename(path, backup)

    try:
        # 2. Copy backup → original path (creates a brand-new file identity)
        shutil.copyfile(backup, path)

        # 3. Verify the copy
        if not filecmp.cmp(backup, path, shallow=False):
            raise RuntimeError(f"Verification failed after copying: {path}")

        # 4. Only delete the backup once everything succeeded
        os.remove(backup)

        print(f"Refreshed: {path}")

    except Exception:
        # Restore the original file if anything went wrong
        if os.path.exists(path):
            os.remove(path)
        os.rename(backup, path)
        raise


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 refresh_file.py <file> [file ...]", file=sys.stderr)
        sys.exit(1)

    errors = 0
    for arg in sys.argv[1:]:
        try:
            refresh_file(arg)
        except Exception as e:
            print(f"Error processing {arg}: {e}", file=sys.stderr)
            errors += 1

    sys.exit(1 if errors else 0)
