# Graphics

## LZSS (tools/lz.py)
- Decompressor `$00:BE77`: u16 output size, then Okumura LZSS (flags LSB-first, 1 = literal; ref b1 b2:
  pos = b1 | (b2 & F0) << 4, len = (b2 & 0F) + 3), 4 KB ring zero-filled at `$7E:DA04`, r = 0xFEE.
- Load scripts: 7-byte ops `04 src24 dst24` (dst in $7E/$7F), list ends with 00. Example: `$10:DCE1` (file 0x85CE1)
  loads the char-select bios 0x1177A3 -> `$7F:D800`. `tools/gfx_assets.py list` finds 157 referenced blocks.

## Pre-rendered labels
- 0x90000-0x93C00: item/spell/monster/character names, 1bpp, 64x8 px each (8 tiles of 8 bytes).

## Survey (graphics text) - in progress
| What | Where | Status |
|---|---|---|
| Title logo | already English | keep |
| Char-select bios | LZSS 0x1177A3 (2bpp 8x8 font bitmaps) | todo |
| Name labels | 0x90000 1bpp | todo |
