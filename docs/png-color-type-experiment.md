# PNG color-type to ICO experiment

## Question

For one opaque 64×64 grayscale image, do PNG storage color types 0, 2, 3, and 6 produce different ICO downloads in the two tested browser converters?

## Procedure and evidence

- Run date: 2026-09-30 (Asia/Shanghai).
- The four input PNGs were generated from the same grayscale drawing and decoded to identical RGBA pixels. `data/png-color-type-inputs.csv` records their PNG color types, byte lengths, and SHA-256 hashes.
- Each input was converted once in pngtoicotool and once in ConvertICO.com. The downloaded outputs were decoded locally with Pillow 12.3.0.
- `data/png-color-type-outputs.csv` records each output's bytes, SHA-256, ICO layer count and dimensions, and aggregate alpha/pixel checks.
- `data/png-color-type-frames.csv` records the decoded frame-level checks.

## Observation

Within each converter, all four downloaded ICOs were byte-identical for this test. Each output had six directory entries: 16×16, 32×32, 48×48, 64×64, 128×128, and 256×256. The decoded 64×64 layer matched the source pixels. The measured file sizes were 14,762 bytes per pngtoicotool output and 370,070 bytes per ConvertICO output.

## Limits

This is one opaque grayscale drawing, one run per PNG type and service, and one service configuration per run. It does not test transparent or colored artwork, malformed or interlaced PNGs, other options, future service versions, or visual quality across every layer. Matching outputs here do not establish that the services share an implementation.
