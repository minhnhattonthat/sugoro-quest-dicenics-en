# Fix-pass brief - Sugoro Quest++ Dicenics

You apply a reviewer's findings to one translated batch. Read `docs/translator-brief.md` (style), `glossary.md`
(rulings at the top are binding) and the review `work/tl/<batch>.review.md`. Current English is in
`work/tl/<batch>.pairs.txt` (`>> id | JP` / `>> EN`). Do the work yourself; no subagents.

## Apply
1. Every Critical and Important finding. If you disagree (the reviewer misread), skip it and say why.
2. Minor findings when they clearly improve the line and fit.
3. House conventions on every entry of the batch, even ones the reviewer didn't list:
   - 「 speech: close the quote at the end of each page (`..."{key}`). If one speech continues on the next page, open
     it again there (`{clr}"...`).
   - Named speaker `Name『...`: `Name: "..."` (also `{v1}: "..."`).
   - Glossary capitalisation exactly (Luck Dice, Power Dice, Magic Dice, Speed Dice, Move Dice; Demon Realm...).
   - No "(s)" stub plurals: rephrase ("Turns left: {v9}").
   - Ulrik: archaic old-woman cadence but no thee/thou.

## Output: `work/tl/<batch>.fix.tsv` (file-write tool, not a shell heredoc)
`id<TAB>full corrected English` for changed entries only (whole string, all control codes). Validate with
`python -X utf8 tools/batches.py checkfile work/tl/<batch>.fix.tsv` until it prints OK. Never edit script/ or any
other file.

## Report (reply with only this)
Number of entries changed; `SKIPPED: id - why` for findings not applied; `UNSURE: id - note`.
