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

## Not done
- Results screen labels 126313 (アイテム ダイス × スコア 魔法) and 128FED (おたから 装備品 トークン(ＴＫ)): needs the
  end-of-game screen's tilemap (1273CC/125D1D/12AF5B are loaded with them).
- Name entry keyboards (11FB6C.. kana pages) - reached only on a top-10 finish; names are raw main-font codes.
- Save-slot font 12156A (kana/digits for slot info).
- Panel graphics raw 0x6A000 area has vertical "ダイスマン" text (status panel lower part?).

## Tools
strips.py / spans.py / winview.py / tallview.py (inspect blocks), find_tilemaps.py (tilemap runs), vramfind.py (skill).
Mid-frame OBSEL change on the board: top HUD sprites use name table at VRAM 0xA000 (OBSEL $62), not the
end-of-frame value Mesen reports.
