# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** released beta, v0.95 (tag v0.95, a01a100, 2026-10-19; patch in release/).
- **Done:** main script translated + reviewed + fixed; names + 1bpp labels; gfx: title menu, sub-screen menu, options,
  bios, rule windows, map descriptions, name/status plates, status panel (condensed names, Diceman sprites), save/load
  boxes, ranking screen, results-screen labels, high-score name entry (English keyboard; lowercase also shows in
  ranking and save slots). No known Japanese graphics text left (12156A and the 0x6A000 mockup are never shown).
- **Next:** user to check the name-entry layout (tools/namekb.py: both pages the same, A-Z / a-z / 0-9 / . , - ! ?
  + = / : ~; no apostrophe because the ranking font has none; dakuten and kana-toggle keys left blank); then release.
- **Open bugs:** none reported.
- **Blocked:** autoplay can't take a human turn yet (roll input unknown); deep event QA needs the user's playtest or a
  found roll input.
- **Waiting on the user:** -
