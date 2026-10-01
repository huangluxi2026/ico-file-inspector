#!/usr/bin/env python3
"""Inspect ICO directory entries using only the Python standard library."""

from __future__ import annotations

import argparse
import csv
import struct
import sys
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
FIELDS = [
    "file", "file_bytes", "entry", "width_px", "height_px", "colors",
    "planes", "bits_per_pixel", "payload_bytes", "payload_offset",
    "payload_format", "payload_dimensions", "range_valid", "dimensions_match",
]


class IcoError(ValueError):
    """Raised when an ICO directory or an entry is malformed."""


def payload_dimensions(data: bytes) -> tuple[str, str]:
    if data.startswith(PNG_SIGNATURE):
        if len(data) < 24 or data[12:16] != b"IHDR":
            return "PNG", "invalid IHDR"
        width, height = struct.unpack_from(">II", data, 16)
        return "PNG", f"{width}x{height}"

    if len(data) >= 12:
        header_size = struct.unpack_from("<I", data, 0)[0]
        if header_size == 12:  # BITMAPCOREHEADER
            width, doubled_height = struct.unpack_from("<HH", data, 4)
            height = doubled_height // 2 if doubled_height % 2 == 0 else doubled_height
            return "DIB", f"{width}x{height}"
        if header_size >= 40 and len(data) >= 12:
            width, doubled_height = struct.unpack_from("<ii", data, 4)
            height = abs(doubled_height) // 2 if abs(doubled_height) % 2 == 0 else abs(doubled_height)
            return "DIB", f"{abs(width)}x{height}"
    return "unknown", "unknown"


def inspect(path: Path) -> list[dict[str, object]]:
    data = path.read_bytes()
    if len(data) < 6:
        raise IcoError("file is shorter than the 6-byte ICO header")

    reserved, kind, count = struct.unpack_from("<HHH", data, 0)
    if reserved != 0 or kind != 1 or count == 0:
        raise IcoError("invalid ICO header (expected reserved=0, type=1, and at least one entry)")

    table_end = 6 + count * 16
    if len(data) < table_end:
        raise IcoError(f"truncated directory: need {table_end} bytes, found {len(data)}")

    rows: list[dict[str, object]] = []
    ranges: list[tuple[int, int, int]] = []
    for index in range(count):
        entry_offset = 6 + index * 16
        width_byte, height_byte, colors, reserved_byte = struct.unpack_from("<BBBB", data, entry_offset)
        planes, bpp, payload_size, payload_offset = struct.unpack_from("<HHII", data, entry_offset + 4)
        width = width_byte or 256
        height = height_byte or 256
        range_valid = payload_size > 0 and payload_offset >= table_end and payload_offset + payload_size <= len(data)
        fmt, dimensions = "unavailable", "unavailable"
        if range_valid:
            fmt, dimensions = payload_dimensions(data[payload_offset:payload_offset + payload_size])
            ranges.append((payload_offset, payload_offset + payload_size, index + 1))
        expected = f"{width}x{height}"
        dimensions_match = dimensions == expected if dimensions != "unknown" and not dimensions.startswith("invalid") else "unknown"
        rows.append({
            "file": path.name,
            "file_bytes": len(data),
            "entry": index + 1,
            "width_px": width,
            "height_px": height,
            "colors": colors,
            "planes": planes,
            "bits_per_pixel": bpp,
            "payload_bytes": payload_size,
            "payload_offset": payload_offset,
            "payload_format": fmt,
            "payload_dimensions": dimensions,
            "range_valid": str(range_valid).lower(),
            "dimensions_match": str(dimensions_match).lower(),
        })
        if reserved_byte != 0:
            rows[-1]["range_valid"] = "false (reserved byte is nonzero)"

    for left_index, left in enumerate(ranges):
        for right in ranges[left_index + 1:]:
            if max(left[0], right[0]) < min(left[1], right[1]):
                rows[left[2] - 1]["range_valid"] = "false (overlaps another entry)"
                rows[right[2] - 1]["range_valid"] = "false (overlaps another entry)"
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Read ICO dimensions and validate directory payload ranges.")
    parser.add_argument("files", nargs="+", type=Path, help="ICO file(s) to inspect")
    args = parser.parse_args()

    all_rows: list[dict[str, object]] = []
    failures: list[str] = []
    for path in args.files:
        try:
            all_rows.extend(inspect(path))
        except (OSError, IcoError, struct.error) as error:
            failures.append(f"{path}: {error}")

    writer = csv.DictWriter(sys.stdout, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(all_rows)

    for message in failures:
        print(message, file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
