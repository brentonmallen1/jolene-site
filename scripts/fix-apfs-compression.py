#!/usr/bin/env python3
"""Rewrite APFS transparently-compressed files as plain files.

Some macOS tools write files with APFS transparent compression (UF_COMPRESSED).
Docker Desktop's VirtioFS file sharing can't read those from a bind mount —
node fails with "Unknown system error -35" (EAGAIN). Re-writing the file
content in place clears the compression flag.

Run whenever the dev container mysteriously fails to read project files:
    just fix-files
"""

import os

UF_COMPRESSED = 0x20
EXCLUDE = {"node_modules", ".git", "images", "dist"}  # top-level dirs only

fixed = 0
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for root, dirs, files in os.walk(root_dir):
    if root == root_dir:
        dirs[:] = [d for d in dirs if d not in EXCLUDE]
    for name in files:
        p = os.path.join(root, name)
        try:
            st = os.stat(p)
        except OSError:
            continue
        if st.st_flags & UF_COMPRESSED:
            with open(p, "rb") as f:
                data = f.read()
            tmp = p + ".tmpfix"
            with open(tmp, "wb") as f:
                f.write(data)
            os.chmod(tmp, st.st_mode & 0o7777)
            os.replace(tmp, p)
            fixed += 1
            print(f"  fixed {os.path.relpath(p, root_dir)}")

print(f"Rewrote {fixed} APFS-compressed file(s).")
