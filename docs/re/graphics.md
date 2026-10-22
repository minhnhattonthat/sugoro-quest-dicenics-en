# Graphics

## LZSS (tools/lz.py)
- Decompressor `$00:BE77`: u16 output size, then Okumura LZSS (flags LSB-first, 1 = literal; ref b1 b2:
  pos = b1 | (b2 & F0) << 4, len = (b2 & 0F) + 3), 4 KB ring zero-filled at `$7E:DA04`, r = 0xFEE.
- Load scripts: 7-byte ops `04 src24 dst24` (dst in $7E/$7F), list ends with 00. `tools/gfx_assets.py list` finds
  the referenced blocks (ids = file offsets). gfxtext.pack recompresses edited blocks into GFX_FREE and repoints
  every op that loads them.
- Scenes (load lists): 085E3E results screen (126313 labels, 11E23F/11E79E italic names, 128FED labels);
  08604A ranking (116B7E/11F4B5 maps, 11DE49 ordinals, 11E23F, 11E79E); 0860D9 name entry (kana keyboards
  11FB6C 11FE55 120215 120526, maps 11F272 120BE1 120812); 08610B/0861D3 save/load (12156A font, 120CEE plates,
  1210D5 boxes, maps 1224AF 12210B 122307).

## Screens done (script/gfxtext.json unless noted)
| Screen | How |
|---|---|
| Title menu | canvas VRAM tile 0x100 = 11D1C4/11D4F7/11D815/11DB85, tilemap LZ 11F2A1; item = tile list |
| Sub-screen menu | same canvas; tilemap LZ 122657 rewritten so items no longer share tiles (途中, 変更) |
| Options | canvas 0x40 12293A, 0x80 122D72, 0xC0 123181 (tilemap 1234F3 untouched; shared tiles C4, E0/E1 blanked) |
| Char-select bios | 1177A3, 118017: 2bpp rows (8 tiles per half-row, one colour per character) |
| Map select | 11CA5A: 2bpp, lines at pixel y (left y19 level; right y2/12/22 per 32-px map) |
| Rule windows | 11AFE7..11C2C8 = one 128x192 sprite sheet; window k = 80x64 from rows 48k (tools/rulewin.py) |
| Name plates | 120CEE 40x16 boxes; load/save boxes 1210D5 |
| Status plates | raw 0x6B000 + c*0x280 (80x16, copied by $06:F429) - tools/plates.py, script/plates.json |
| Ranking | 11E23F/11E79E italic names (5-tile spans at tile 0x260/0x280); default names raw 0x39D7A (4 glyph codes) |
| 1bpp labels | 0x90000, 240 x 64x8 (tools/labels.py, script/labels.json) |
| Results screen | BG2 canvas 0x00 = 126313, 0xC0 = 128FED; BG2 tilemap LZ 12A6A8 widened for Spells/Equipment |
| Name entry | tools/namekb.py: key tables 0x36B50/0x36C04 (2 pages x 90 u16 codes), BG1 map LZ 120812, 8x8 4bpp font LZ 11FB6C.. (tile 0x100 + code); ranking draws names with the JP 16x16 font 0x88000 (glyph = code), so a-z copied to 0x61-0x7A |

Verified (2026-10-23, emulator): results labels, keyboard typing, ranking and save-slot display of a lowercase name.

## Not used / not visible
- 12156A (save/load scenes, -> $7F:8000 -> BG3 tiles): a pre-rendered sheet of staff names + digit strings; the game
  draws each filled slot's name/level over it from the 8x8 1bpp font ($04:F49B, font8.py) and empty slots use a blank
  tile, so it never shows.
- Raw 0x6A000 top-left: a JP status-panel mockup (たいりょう じんかく プリッツ); the in-game panel doesn't use it.

## Reaching end-game scenes (no playthrough)
Main mode $0112 (table $00:82A4), substate $0114; scene load lists by index $1D35 (table $10:DA48 via $10:800F).
`tools/lua/warp.lua --var MODE=8` from en_board.mss = end ceremony -> results -> ranking -> (top 10) name entry ->
save grid; MODE=9 sub-screen; MODE=11 load grid (add `tools/lua/srmload.lua --var SRM="abs path"` first: savestates
carry their own SRAM).

## Tools
strips.py / spans.py / winview.py / tallview.py (inspect blocks), find_tilemaps.py (tilemap runs), vramfind.py (skill).
Mid-frame OBSEL change on the board: top HUD sprites use name table at VRAM 0xA000 (OBSEL $62), not the
end-of-frame value Mesen reports.
