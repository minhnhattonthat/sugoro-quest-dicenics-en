# Sugoro Quest++ Dicenics (SNES) English translation

Skill: translate-retro-game (H:/translation/sugoro-quest-dicenics/.claude/skills/translate-retro-game/SKILL.md). Read it before ROM, text or QA work.

## Commands (run from repo root; always `python -X utf8`)
- Build:   `tools/build.py [--marker] [--qa ID=TEXT] [--out build/sq_en.sfc]`; `--identity` = JP repack (== original).
  Steps: font -> asar asm/main.asm (VWF) -> script groups to free banks -> names -> 1bpp labels -> LZ gfx text -> plates.
- Check:   `tools/check.py` (pytest tests/ + lint.py; the pre-commit hook runs this)
- Smoke:   `python -X utf8 .claude/skills/translate-retro-game/scripts/emu.py build/sq_en.sfc --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Text:    `tools/batches.py list|split|check|merge|pairs|apply|checkfile|fit` (b1..b7b), `tools/namelist.py split|check|merge`
- Release: `tools/release.py --version X.Y` -> release/ (BPS + README zip; local only, never publish without the user).
  After adding a new kind of ROM write: `tools/ranges.py` (allowed ranges for the romdiff test).
- RE helpers: script.py, peek.py, fontview.py, lz.py, gfx_assets.py, find_tables.py, find_tilemaps.py, strips.py,
  spans.py, winview.py, tallview.py, labels.py sheet, plates.py preview, gfxtext.py (preview). Lua: tools/lua/*.

## Paths
- ROM: `rom/orig.sfc` (CRC32 366C84F3, SHA-1 c60efaaf506f8de27dce7af312a022ad5db19271, 2 MB LoROM; gitignored).
- Mesen2: tools/mesen2 (settings.json MUST have Snes.Port1.Type=SnesController or input is ignored). asar: tools/asar.
- States (work/states): en_board.mss (EN build, board, Pritz turn), en_king.mss (EN, Diceman pick), title.mss (orig).
  States keep VRAM: after gfx changes reach the screen from a cold boot or a state taken before it loads.
- Text: script/g0-g7.json (main, 661 strings), names.json (283), labels.json (240 1bpp labels), gfxtext.json (LZ gfx
  text screens), plates.json. Tables tbl/jp.tbl, tbl/en.tbl. Glossary + rulings: glossary.md. Briefs: docs/*.md.
- RE notes: docs/re/text.md, docs/re/graphics.md.

## Rulings (user, 2026-10-14)
- Honorifics kept (hyphenated), Japanese name order. Official romaji else Hepburn (cast has no official romaji:
  Pritz, Tanguy, Ulrik, Cynthia, Dechtel, Diana - flagged to user). Siland = series' official spelling.
- Credits in English. No abbreviations (engine work first). All graphics text in scope. Plans pre-approved.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update the Status section.

## Engine
- VWF hooked at $08:8121 (asm/main.asm, bank $3A): 8x16 2bpp glyphs by text code, {atN} = jump to cell N.
  Lines 216 px (240 for 20-cell styles); lines/page <= JP page (lint). Names <= 21 bytes (RAM buffers).
- Input: B confirms Diceman picks; X/Y = Yes on the controller-wheel prompts; Start = sub-screen; Select = status.

## Status (2026-10-15)
- Done: main script translated + reviewed + fixed; names + 1bpp labels; gfx: title menu, sub-screen menu, options,
  bios, rule windows, map descriptions, name/status plates, save/load boxes, ranking. v0.9 built in release/.
- Open: results-screen labels (126313/128FED), name-entry keyboards, save-slot font 12156A (all end-game /
  saved-data screens, not reached yet; docs/re/graphics.md). Autoplay can't take a human turn yet (roll input
  unknown) - deep event QA needs the user's playtest or a found roll input.
