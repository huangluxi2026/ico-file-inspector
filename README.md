# ICO File Inspector

`ico_inspect.py` reads the image directory inside one or more Windows `.ico` files. It reports each entry's pixel dimensions, payload size and offset, whether the payload range is inside the file, and whether recognizable PNG/DIB payload dimensions agree with the directory entry. It uses only Python's standard library.

```console
python tools/inspect_ico.py path/to/favicon.ico
python tools/inspect_ico.py icons/*.ico > report.csv
```

This is a structural check, not a full image decoder: it does not prove that pixel data decompresses or that an icon looks correct in its target application. Unknown payload encodings are reported as `unknown` instead of being guessed.

## Data

`data/` contains a reproducible browser-conversion observation recorded on 2026-09-30. Four 64×64 PNG files encode the same opaque grayscale pixels using PNG color types 0, 2, 3, and 6. Each was converted once with this project's browser-only converter and once with ConvertICO.com. Input hashes, ICO hashes, file bytes, directory layers, and decoded frame checks are in the CSV files. The notes in [the experiment record](docs/png-color-type-experiment.md) state the setup and limits.

The observed outputs were 14,762 bytes for each pngtoicotool conversion and 370,070 bytes for each ConvertICO conversion in that run. These are measurements from one input image, one run per variant, and the listed settings; they are not a general claim about either service.

For the browser-based PNG-to-ICO converter and its supported input formats, see [pngtoicotool](https://pngtoicotool.com/).

## License

The inspector source code is MIT licensed. The original test records and CSV data are dedicated to the public domain under CC0 1.0; see [DATA-LICENSE.md](DATA-LICENSE.md).
