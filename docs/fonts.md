# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| `font/vwf.txt` | drawn for the Little Master fan translation (sibling project) | MIT, same as repo | yes | dialogue VWF (tools/font.py) | game symbols in slots * ; < > @ |
| `font/cond8.txt` | drawn for this project | MIT, same as repo | yes | condensed 8x8 menu glyphs, two per tile (labels, plates, panel) | - |
| Game 16x16 font (bank $11, file 0x88000) | original game | Technos Japan; not in this repo | not redistributed | Japanese text | - |
