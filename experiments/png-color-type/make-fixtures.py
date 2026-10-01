from PIL import Image, ImageDraw
from pathlib import Path
import csv
import hashlib

ROOT = Path(__file__).resolve().parent
INPUTS = ROOT / "inputs"
INPUTS.mkdir(parents=True, exist_ok=True)

# An opaque, grayscale drawing keeps the decoded pixels identical while the
# PNG storage type changes. This deliberately does not test alpha preservation.
base = Image.new("L", (64, 64), 255)
draw = ImageDraw.Draw(base)
draw.ellipse((8, 8, 55, 55), fill=30)
draw.ellipse((17, 17, 46, 46), fill=255)
draw.rectangle((28, 22, 35, 42), fill=30)
draw.rectangle((22, 29, 41, 35), fill=30)

variants = {
    "rgb": base.convert("RGB"),
    "rgba": base.convert("RGBA"),
    "indexed": base.convert("P"),
    "grayscale": base,
}
expected_color_types = {"rgb": 2, "rgba": 6, "indexed": 3, "grayscale": 0}
rows = []

for name, image in variants.items():
    if image.mode == "P":
        palette = []
        for value in range(256):
            palette.extend((value, value, value))
        image.putpalette(palette)

    path = INPUTS / f"{name}.png"
    image.save(path, format="PNG", optimize=False)
    data = path.read_bytes()
    color_type = data[25]
    if color_type != expected_color_types[name]:
        raise ValueError(f"{name}: expected PNG color type {expected_color_types[name]}, got {color_type}")
    rows.append([
        name, color_type, data[24], image.width, image.height, len(data),
        hashlib.sha256(data).hexdigest(), path.name,
    ])

decoded = [Image.open(INPUTS / f"{name}.png").convert("RGBA").tobytes() for name in variants]
if len(set(decoded)) != 1:
    raise ValueError("PNG variants do not decode to identical pixels")

with (ROOT / "inputs.csv").open("w", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file)
    writer.writerow([
        "source_variant", "png_color_type", "bit_depth", "width_px", "height_px",
        "input_bytes", "input_sha256", "input_file",
    ])
    writer.writerows(rows)

print("PASS: four 64x64 input PNGs decode to identical opaque pixels.")
for row in rows:
    print(",".join(map(str, row)))
