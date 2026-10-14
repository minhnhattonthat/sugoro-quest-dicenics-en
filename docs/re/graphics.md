# Graphics

## LZSS (tools/lz.py)
- Decompressor `$00:BE77`: u16 output size, then Okumura LZSS (flags LSB-first, 1 = literal; ref b1 b2:
  pos = b1 | (b2 & F0) << 4, len = (b2 & 0F) + 3), 4 KB ring zero-filled at `$7E:DA04`, r = 0xFEE.
- Load scripts: 7-byte ops `04 src24 dst24` (dst in $7E/$7F), list ends with 00. Example: `$10:DCE1` (file 0x85CE1)
  loads the char-select bios 0x1177A3 -> `$7F:D800`. `tools/gfx_assets.py list` finds 157 referenced blocks.

## Pre-rendered labels
- 0x90000-0x93C00: item/spell/monster/character names, 1bpp, 64x8 px each (8 tiles of 8 bytes).

## Survey (graphics text) - first pass 2026-10-14 (2bpp sheets of all LZ blocks; gist only)
LZ block ids = file offset of the compressed block (`tools/gfx_assets.py dump` -> work/gfx/<id>.bin).
| What | Where | Status |
|---|---|---|
| Title logo | already English | keep |
| Char-select bios (8x8 font) | LZ 1177A3, 118017 | todo |
| Name labels (items/spells/monsters) | 0x90000-0x93C00 1bpp 64x8 | todo |
| Title menu (large font) | LZ 11D1C4 (ゲームをはじめる/コンティニュー), 11D4F7 (キャラクターのロード/オプション) | todo |
| In-game menu | LZ 11D815 (アドバイス.., 参加, ルール変更), 11DB85 (セーブする, ゲームへもどる) | todo |
| 4bpp text windows (quest count, days, options "なし", map) | LZ 11AFE7 11B489 11B8C5 11BCBA 11BEF9 11C2C8 | todo, re-render snes4 |
| Map-select descriptions | LZ 11CA5A | todo |
| Big name font / name plates | LZ 11E23F 11E79E 120CEE | todo |
| Kana glyph sets (name entry?) | LZ 11FB6C 11FE55 120215 120526 | check use |
| Save/load panels | LZ 1210D5 | todo |
| Staff nicknames (credits) | LZ 12156A | todo (credits in English) |
| Options (ステレオ/モノラル, はやい/ふつう/おそい, 出す/出さない) | LZ 122D72 123181 | todo |
| Battle/status labels (アイテム, ダイス, 装備品, まほう, トーク) | LZ 126313 128FED | todo |
| English already | 118A2E 119038 119CB1 11A294 (MAP n), 11D0F6, 11DE49, 1260B1, 12B482 12B7F4 12BB6B | keep |
| Tilemaps (may compose text from font tiles) | 116B7E 117404 118538 11862F 11C755 11F2A1.. (see agent list) | check |
| Board layouts (not gfx) | 1B2000-1BC299 | none |
