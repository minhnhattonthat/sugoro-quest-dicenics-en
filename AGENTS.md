# Sugoro Quest++ Dicenics (SNES) English translation

Skill: translate-retro-game (Claude Code: plugin, enabled in .claude/settings.json; other agents: `<SKILL_DIR>/SKILL.md`; `$SKILL` = the directory holding its SKILL.md; tools find it via `tools/skill.py`, `$SKILL` env var overrides the plugin path). Read it before ROM, text or QA work.

## Commands (run from repo root; always `python -X utf8`)
- Build:    `python -X utf8 tools/build.py [--marker] [--qa ID=TEXT] [--out build/sq_en.sfc]` -> build/sq_en.sfc (checks the dump against `rom.sha1` first); `--identity` = JP repack (== original).
  Steps: font -> asar asm/main.asm (VWF) -> script groups to free banks -> names -> 1bpp labels -> LZ gfx text -> plates.
- Check:    `python -X utf8 tools/check.py`  (pytest tests/ + lint.py; the pre-commit hook runs this)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py build/sq_en.sfc --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Text:     `tools/batches.py list|split|check|merge|pairs|apply|checkfile|fit` (b1..b7b), `tools/namelist.py split|check|merge`
- Release:  `python -X utf8 tools/release.py --version X.Y` -> release/ (BPS + README zip; never publish without the user).
  After adding a new kind of ROM write: `tools/ranges.py` (allowed ranges for the romdiff test).
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)
- RE helpers: script.py, peek.py, fontview.py, lz.py, gfx_assets.py, find_tables.py, find_tilemaps.py, strips.py,
  spans.py, winview.py, tallview.py, labels.py sheet, plates.py preview, gfxtext.py (preview). Lua: tools/lua/*.

## Paths
- Original ROM: `rom/orig.sfc` (2 MB LoROM, CRC32 366C84F3; gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`). Emulator: this repo's own copy in `tools/mesen2/` (gitignored; settings.json MUST have Snes.Port1.Type=SnesController or input is ignored). asar: `tools/asar/`. Savestates: `work/states/`.
- States: en_board.mss (EN build, board, Pritz turn), en_king.mss (EN, Diceman pick), title.mss (orig),
  en_results_pre / en_ranking_pre / en_nameentry.mss (end game); warp to end-game scenes: docs/re/graphics.md.
  States keep VRAM: after gfx changes reach the screen from a cold boot or a state taken before it loads.
- Text: `script/g0-g7.json` (main, 661 strings), names.json (283), labels.json (240 1bpp labels), gfxtext.json (LZ gfx
  text screens), plates.json. Tables: `tbl/jp.tbl`, `tbl/en.tbl`. Glossary: `glossary.md`. Briefs: `docs/*-brief.md`.
  RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- VWF hooked at $08:8121 (asm/main.asm, bank $3A): 8x16 2bpp glyphs by text code, {atN} = jump to cell N.
  Lines 216 px (240 for 20-cell styles); lines/page <= JP page (lint). Names <= 21 bytes (RAM buffers).
- Input: B confirms Diceman picks; X/Y = Yes on the controller-wheel prompts; Start = sub-screen; Select = status.
- Allowed ROM write ranges: `tools/allowed_ranges.txt` (tests/test_build.py romdiff).

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
