from PIL import Image
from pathlib import Path
import csv
import hashlib
import struct

ROOT = Path(__file__).resolve().parent
TYPES = {"rgb": 2, "rgba": 6, "indexed": 3, "grayscale": 0}
CONVERTERS = ("site", "convertico")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def alpha_counts(image):
    histogram = image.convert("RGBA").getchannel("A").histogram()
    return histogram[0], sum(histogram[1:255])


def non_gray_pixel_count(image):
    rgb = image.convert("RGB")
    channels = [rgb.getchannel(channel).tobytes() for channel in "RGB"]
    return sum(1 for r, g, b in zip(*channels) if r != g or g != b)


def ico_entries(path):
    data = path.read_bytes()
    reserved, kind, count = struct.unpack_from("<HHH", data, 0)
    if reserved != 0 or kind != 1 or len(data) < 6 + count * 16:
        raise ValueError(f"Invalid ICO directory: {path.name}")
    entries = []
    for index in range(count):
        offset = 6 + index * 16
        width, height = data[offset], data[offset + 1]
        width = width or 256
        height = height or 256
        size, data_offset = struct.unpack_from("<II", data, offset + 8)
        entries.append((width, height, size, data_offset))
    return entries


sources = {
    name: Image.open(ROOT / "inputs" / f"{name}.png").convert("RGBA")
    for name in TYPES
}
if len({image.tobytes() for image in sources.values()}) != 1:
    raise ValueError("Source PNGs are not pixel-identical")

summary_rows = []
frame_rows = []
for converter in CONVERTERS:
    for name, color_type in TYPES.items():
        source_path = ROOT / "inputs" / f"{name}.png"
        output_path = ROOT / "outputs" / converter / f"{name}.ico"
        if not output_path.exists():
            summary_rows.append([
                converter, name, color_type, 64, 64, len(source_path.read_bytes()),
                sha256(source_path), "not measured", "", "", "", 0, "", "", "", "",
            ])
            continue

        output_data = output_path.read_bytes()
        output_image = Image.open(output_path)
        sizes = sorted(output_image.ico.sizes(), key=lambda size: (size[0], size[1]))
        entries = {(width, height): (size, offset) for width, height, size, offset in ico_entries(output_path)}
        alpha0_sum = 0
        partial_alpha_sum = 0
        non_gray_sum = 0
        exact_64_match = "not present"

        for width, height in sizes:
            layer = output_image.ico.getimage((width, height)).convert("RGBA")
            alpha0, partial_alpha = alpha_counts(layer)
            non_gray = non_gray_pixel_count(layer)
            exact_match = layer.tobytes() == sources[name].tobytes() if (width, height) == (64, 64) else ""
            if (width, height) == (64, 64):
                exact_64_match = "yes" if exact_match else "no"
            alpha0_sum += alpha0
            partial_alpha_sum += partial_alpha
            non_gray_sum += non_gray
            entry_size, _ = entries[(width, height)]
            frame_rows.append([
                converter, name, color_type, f"{width}x{height}", entry_size,
                alpha0, partial_alpha, non_gray,
                "yes" if exact_match is True else "no" if exact_match is False else "not applicable",
            ])

        summary_rows.append([
            converter, name, color_type, 64, 64, len(source_path.read_bytes()),
            sha256(source_path), "downloaded", output_path.name, len(output_data),
            hashlib.sha256(output_data).hexdigest(), len(sizes),
            ";".join(f"{width}x{height}" for width, height in sizes),
            alpha0_sum, partial_alpha_sum, non_gray_sum, exact_64_match,
        ])

with (ROOT / "measurements.csv").open("w", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file)
    writer.writerow([
        "converter", "source_variant", "png_color_type", "source_width_px",
        "source_height_px", "input_bytes", "input_sha256", "status", "output_file",
        "output_bytes", "output_sha256", "ico_layer_count", "ico_layer_dimensions",
        "alpha0_pixels_sum_all_layers", "partial_alpha_pixels_sum_all_layers",
        "non_gray_pixels_sum_all_layers", "64x64_exact_source_pixel_match",
    ])
    writer.writerows(summary_rows)

with (ROOT / "decoded-frames.csv").open("w", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file)
    writer.writerow([
        "converter", "source_variant", "png_color_type", "decoded_layer",
        "frame_bytes", "fully_transparent_pixels_alpha0", "partial_alpha_pixels_0_to_254",
        "non_gray_pixels", "exact_64px_source_pixel_match",
    ])
    writer.writerows(frame_rows)

for row in summary_rows:
    print(" | ".join(map(str, row)))
print(f"Pillow {Image.__version__ if hasattr(Image, '__version__') else 'version unknown'}")
