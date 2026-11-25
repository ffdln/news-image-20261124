#!/usr/bin/env python3
"""Ship the 24 November 2026 front page.

The entry bundles one file, entry.png (a 1024x1024 PNG of the day's
front page). This program checks that the bundled image is exactly the
front page the entry promises — a real PNG, 1024 pixels on each side,
no bigger than 1 MiB — and then places a verbatim copy in the output
directory the harness gives it through MAKEFUN_OUTPUT_DIR.

It uses only the Python standard library and never touches the network.
Running it twice over the same bundle writes the same bytes twice.
"""

import os
import struct
import sys
from pathlib import Path

IMAGE_NAME = "entry.png"
SIDE = 1024
LIMIT = 1024 * 1024
SIGNATURE = b"\x89PNG\r\n\x1a\n"
# The last twelve bytes of a complete PNG: a zero-length IEND chunk.
IEND_TAIL = b"\x00\x00\x00\x00IEND\xaeB`\x82"


def abort(message):
    """Stop with the reason on stderr and a non-zero exit."""
    print(f"main.py: {message}", file=sys.stderr)
    return 1


def png_size(blob):
    """Return (width, height) from a PNG's IHDR chunk, or None."""
    if len(blob) < 33 or blob[:8] != SIGNATURE:
        return None
    if blob[12:16] != b"IHDR":
        return None
    width, height = struct.unpack(">II", blob[16:24])
    return width, height


def deliver():
    """Validate the bundled front page and copy it to the output dir."""
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        return abort("MAKEFUN_OUTPUT_DIR is not set")
    source = Path(__file__).resolve().parent / IMAGE_NAME
    if not source.is_file():
        return abort(f"bundled {IMAGE_NAME} is missing")
    blob = source.read_bytes()
    if len(blob) > LIMIT:
        return abort(f"bundled {IMAGE_NAME} is {len(blob)} bytes, over the 1 MiB cap")
    size = png_size(blob)
    if size is None:
        return abort(f"bundled {IMAGE_NAME} is not a PNG")
    if not blob.endswith(IEND_TAIL):
        return abort(f"bundled {IMAGE_NAME} is truncated (no IEND chunk)")
    if size != (SIDE, SIDE):
        return abort(f"bundled {IMAGE_NAME} is {size[0]}x{size[1]}, not {SIDE}x{SIDE}")
    target = Path(out_dir) / IMAGE_NAME
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(blob)
    print(f"wrote {target}: {len(blob)} bytes, {size[0]}x{size[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(deliver())
