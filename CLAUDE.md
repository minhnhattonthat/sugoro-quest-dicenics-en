# Sugoro Quest++ Dicenics (SNES) English translation

Skill: translate-retro-game (H:/translation/sugoro-quest-dicenics/.claude/skills/translate-retro-game/SKILL.md). Read it before ROM, text or QA work.

## Commands (run from repo root; always `python -X utf8`)
- Check:   `python -X utf8 tools/check.py` (pytest tests/; the pre-commit hook runs this)
- Smoke:   `python -X utf8 .claude/skills/translate-retro-game/scripts/emu.py ROM --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Build / Release: not yet (phase 2+).
- Recon:   `tools/script.py stats|show G [FROM N]` (main script), `tools/peek.py START END` (decode E0 lists),
  `tools/fontview.py`, `tools/lz.py dec OFF OUT`, `tools/gfx_assets.py list|dump`, `tools/find_tables.py`, `tools/scan_text.py`.
- Lua (tools/lua, emu.py --script): readwatch (who reads LO..HI), ramlog (WRAM bytes per frame), padlog.

## Paths
- ROM: `rom/orig.sfc` (CRC32 366C84F3, SHA-1 c60efaaf506f8de27dce7af312a022ad5db19271, 2 MB LoROM; gitignored).
- Mesen2: tools/mesen2 (its settings.json MUST have Snes.Port1.Type=SnesController or input is ignored; copied from
  ../rokudenashi-blues). asar: tools/asar. States: work/states/ (title.mss = title screen, input-ready).
- Table tbl/jp.tbl. Glossary + rulings: glossary.md. RE notes: docs/re/text.md, docs/re/graphics.md.

## Rulings (user, 2026-10-14)
- Honorifics kept (hyphenated), Japanese name order. Official romaji else Hepburn. Credits in English.
- No abbreviations (engine work first). All graphics text in scope. Plans pre-approved (report at end).

## Status (2026-10-14)
- Done: Step 0 setup; recon of main script engine (8 groups, ~750 msgs), font, name lists, LZSS, bios bitmap.
- Next: finish recon (name-list pointer users, menus, graphics survey of 157 LZ assets), identity build, extract.
