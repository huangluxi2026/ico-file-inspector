# Reading an ICO directory

An ICO file starts with a 6-byte header followed by one 16-byte directory entry for each image. Each entry stores dimensions as one byte; a zero dimension encodes 256 pixels. The entry also gives color count, planes, bits per pixel, payload length, and payload offset. The image payload can be PNG data or a DIB bitmap.

`tools/inspect_ico.py` checks the header, entry-table length, payload boundaries, overlapping payload ranges, and dimensions when a PNG or common DIB header is recognizable. It deliberately does not claim that a payload fully decodes.

For Microsoft's overview of icon files and their multiple image resources, see [About Icons](https://learn.microsoft.com/en-us/windows/win32/menurc/about-icons) and the [ICO format overview](https://learn.microsoft.com/en-us/windows/win32/wic/ico-format-overview). This utility performs structural checks only; consult an implementation-level format reference when validating unusual legacy DIB payloads.
