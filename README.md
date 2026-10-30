# Sugoro Quest++: Dicenics - English Translation

Unofficial fan translation of **Sugoro Quest++: Dicenics** (スゴロクエスト++ ダイセニクス, Super Famicom, Technos Japan, 1994),
a dice-driven board game RPG for 1-4 players.

**Status:** v0.96 (beta). Playable start to finish in testing; no known Japanese text left.

## Patching

No ROM is included. You need your own dump of the Japanese game:

| | CRC32 | SHA-1 |
|---|---|---|
| Original (2 MB, unheadered) | `366C84F3` | `c60efaaf506f8de27dce7af312a022ad5db19271` |
| Patched | `E1D51F08` | `ff398b5b8efcd79f5bfe9691cbde256a35c37523` |

Download the `.bps` from [Releases](../../releases) and apply it with [Flips](https://github.com/Alcaro/Flips) or
[RomPatcher.js](https://www.marcrobledo.com/RomPatcher.js/). Start from a cold boot; Japanese save states and old
save data (`.srm`) keep Japanese code, graphics and ranking names.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| Dialogue, events, battle/board messages, the King, the ending | Translated |
| Item, spell, weapon, armor, key item, monster and character names; menu and command labels | Translated |
| Graphics text: title menu, sub-screen, options, bios, rule/map windows, status panel and equipment page, load/save boxes, ranking screen, end-of-game results screen | Translated (the title logo is already English) |
| High-score name entry | Translated (English keyboard) |
| Staff credits | Translated (romanised) |

All dialogue uses a new variable-width font.

Known issues: none known (tested in Mesen 2); [report one](../../issues/new/choose) if anything overflows a box or
still shows Japanese.

## Translation notes

- Honorifics kept (hyphenated), Japanese name order. Official romaji where it exists, else Hepburn.
- Cast has no official romanization; names follow the Western spelling of the katakana (Pritz, Tanguy, Ulrik,
  Cynthia, Dechtel, Diana). "Siland" follows the series' official English spelling. See `glossary.md`.

## Building from source

Needs Python 3.12+ with Pillow, [asar](https://github.com/RPGHacker/asar) in `tools/asar/`, the
[translate-retro-game](https://github.com/minhnhattonthat/translate-retro-game) skill (Claude Code plugin, or set `SKILL`
to its directory) and your ROM at `rom/orig.sfc` (SHA-1 above; the build refuses any other dump, see `rom.sha1`).

```
python -X utf8 tools/build.py            # -> build/sq_en.sfc
python -X utf8 tools/check.py            # tests + script lint
python -X utf8 tools/release.py --version X.Y
```

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `asm/` | VWF engine (asar). |
| `font/`, `tbl/` | English font art; Japanese and English text tables. |
| `tools/` | Python build chain: extract, insert, lint, release. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Credits

Translation and hacking: fan translation project (AI-assisted with Claude; every string reviewed and checked in an
emulator). Original game (c) 1994 Technos Japan. Not affiliated with the rights holders. Do not distribute patched ROMs.
Tools and source in this repo: MIT (see `LICENSE`); game text and data remain property of their owners.
