Sugoro Quest++ Dicenics - English Translation v{VERSION}
=======================================================

Unofficial fan translation of Sugoro Quest++: Dicenics (Super Famicom, Technos Japan, 1994), a dice-driven board
game RPG for 1-4 players. No ROM is included or distributed; you need your own dump.

Patching
--------
Apply the .bps patch with Flips, beat or https://www.marcrobledo.com/RomPatcher.js/ to this ROM:
  Sugoro Quest++ - Dicenics (Japan).sfc  (2 MB, unheadered)
  {BASE}
Patched result:
  {PATCHED}

What is translated
------------------
- All dialogue, events, battle and board messages, the King, the ending and the staff credits (romanized).
- Item, spell, weapon, armor, key item and monster names; the menu/command labels.
- Graphics text: title menu, sub-screen menu, options, character-select bios, rule and map selection windows,
  status panel plates, load/save panels, ranking screen.
- A new proportional (variable-width) font for all dialogue.

Notes
-----
- Start from a cold boot. Savestates from the Japanese game carry old code and graphics.
- Old Japanese save data (SRAM) keeps the Japanese ranking names; delete the .srm to reset the table.
- Character names have no official romanization; they follow the Western names the katakana spell
  (Pritz, Tanguy, Ulrik, Cynthia, Dechtel, Diana). "Siland" follows the series' 2025 official English release.
- Japanese honorifics (-san, -sama, -dono) are kept.

Known issues
------------
- Not yet translated: the end-of-game results screen labels, the name-entry keyboard and the save-slot name font
  (not reached in testing yet).
- Tested in Mesen 2. Please report anything that overflows a box or still shows Japanese.

Credits
-------
Translation and hacking: fan translation project (AI-assisted: the script was translated and reviewed with Claude,
then checked in an emulator). Original game (c) 1994 Technos Japan. This patch is unofficial and not affiliated
with the rights holders. Do not distribute patched ROMs.
