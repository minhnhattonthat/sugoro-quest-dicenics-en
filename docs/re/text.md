# Text engine (main script)

ROM: LoROM 2 MB (`$7FC0` header "Sugoro Quest++", map $20, type $02 ROM+SRAM, 8 KB SRAM). No prior patch exists
(searched 2026-10-14). Lots of free space: banks $21, $26, $3A fully 0xFF; $39 30 KB; $0E 24 KB; $27 21 KB; $15 17 KB.

## Messages
- Message id `$18B3` = group<<12 | index. Group table `$08:848A` (file 0x4048A), 3 bytes each: ptr16, bank. Groups 0-7
  only (0-3 bank $08, 4-7 bank $09). Each group = table of 16-bit pointers into its own bank; strings follow the table.
  Moving a group = rewrite its 3-byte entry (any free bank works; reader does PLB from the entry).
- Reader `$08:8073`. Box style `$18B5` selects per-style tables: `$84A2` (VRAM base), `$84C2` (cell position list),
  `$869C` (newline targets), `$8215` (wait lengths), `$8129` (speed).
- `$18A3` low nibble != 0: reading a RAM string buffer `$826D[n-1]` = `$0940 + 0x16*(n-1)` (E1-EF), ended by E0.

## Encoding (tbl/jp.tbl)
- 00-DF: glyph code directly (00 = space, 01 = skipped). FE xx: glyph xx (needed for E0-FF). FF xx: glyph 0x100+xx.
- Control: E0 end of RAM sub-string / name terminator; E1-EF insert RAM buffer 1-15 ({v1}..); F4 {key} (wait button);
  F5/F6/F7 {wait0..2}; FB {clr} (clear box); FC {nl}; FD {end}. F0-F3, F8-FA draw glyph 0 (unused).
- Font: bank $11 (file 0x88000), 512 glyphs x 64 bytes, 16x16 2bpp (TL TR BL BR), drawn on a 12 px pitch: even cells
  copied whole, odd cells shifted 4 px and ORed (`$08:83EA`, `$08:8342`). Glyph buffer `$7E:3604`, box buffer `$7E:3684`.
- Font already has ASCII: A-Z = 0x21-0x3A, a-z = 0x101-0x11A, 0-9 = 0x10-0x19. Kanji read off the 12 px font
  (`tools/fontview.py`); doubtful ones: 138 廃 139 虚 184 幽 185 痛 198 惚 1BD 聞 1E8 該 1F0 貸 1F4 衆 1F5 彰 1FF 稼.

## Name lists (E0-terminated, same encoding)
- Bank $04: characters (0x212A3 プリッツ..ディアナ), items/spells (0x212C7-0x21620); 8-byte records 0x21800-0x21AB7
  (+0 name ptr16, +2 ?, +4 flags, +6 ?). Tables at 0x21DB6 (11).
- Bank $06: key items 0x3312D-, table 0x333F0 (39).  Bank $08: weapons/armour 0x4077B- table 0x40AE5 (89);
  monsters 0x40BA2- table 0x40C89 (26).
- Same names also exist as pre-rendered 1bpp 64x8 bitmaps at 0x90000-0x93C00 (menus use those): graphics text.

## Other text
- Character-select bios (8x8 font) are LZSS bitmaps: asset 0x1177A3 -> `$7F:D800` -> VRAM $7000 (BG3 2bpp).
  See docs/re/graphics.md.
