# Translator brief - Sugoro Quest++ Dicenics (SNES, Technos Japan 1994)

You translate part of the Japanese script of this game into English for a fan patch. It's a sugoroku (board game)
RPG for up to four players: six quirky adventurers (Pritz, Tanguy, Ulrik, Cynthia, Dechtel, Diana) roll dice across
the Kingdom of Siland, fight monsters, run quests for townsfolk, collect treasure and TK (money), and compete for
first place in the King's ranking. Tone: light, jokey fantasy comedy; system messages are a friendly game-show host.
Work only on the batch named in your dispatch. Do all translation yourself; do not dispatch subagents.

## Read first
1. `docs/style-reference.md` - voices, approved pairs and mechanics. Match this voice.
2. `work/tl/terms_<batch>.txt` - binding glossary rows for this batch (`glossary.md` has rulings and full tables).

## Input: `work/tl/<batch>.tsv`
`id<TAB>limit<TAB>hint<TAB>Japanese`. The Japanese is raw, with control codes in braces. Entries are in ROM order,
which mostly follows events: use neighbours for context and work out the speaker from content (no speaker field).
- `limit` = lines per page / px per line, e.g. `3+2L/216px` = page 1 max 3 lines, page 2 max 2 lines, 216 px each.
  Pages are separated by `{clr}`; lines by `{nl}`. A trailing `{nl}` before `{end}` counts as an (empty) line.
- `hint` = `choice:{at4}はい{at11}いいえ` for choice rows: write the options at the same `{atN}` columns
  (`{at4}Yes{at11}No`), because the cursor sprite sits there.

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (never a shell heredoc)
`id<TAB>English`, every input id exactly once, same order. Plain ASCII: straight quotes, `...`, `~`; no tabs or
backslashes, no Japanese or fullwidth characters, no `\uXXXX`. Do not use `; * < > @` (those slots hold other glyphs).
- **Copy every control code exactly and in the same order**: `{clr} {key} {wait0} {wait1} {wait2} {end} {v1}..{v15}`.
  Only `{nl}` may differ (you place line breaks) and you may add `{atN}`.
- The game does NOT wrap: insert `{nl}` yourself so every line fits. Keep the same number of `{clr}` pages.
- `{v9}` is a number; `{v1}` `{v2}` `{v3}` `{v4}` `{v7}` are names of characters or monsters; `{v5}` `{v6}` `{v8}` `{v10}` are
  item/spell names. Write grammar that works for any of them: no "a/an" right before a variable, no suffix glued to
  one ("{v9}th" -> "No. {v9}"), no he/she for `{v1}` (rephrase, or use the name again).
- Drop the Japanese centering spaces.

## Validate
`python -X utf8 tools/batches.py fit "line one{nl}line two"` prints px per line - use it while drafting.
Then run `python -X utf8 tools/batches.py check <batch>` from the repo root and fix every reported id until it
prints OK. It checks ids, control codes, characters, line widths, lines per page and glossary terms.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add details the Japanese doesn't
  state; don't summarise or skip. Jokes, puns and silly names must still land in English (adapt; no translator notes).
- Names and terms exactly as in the glossary; never abbreviate a name or term to fit - rephrase instead, and if it
  truly can't fit, keep the meaning, and report `LONG: id`.
- Honorifics kept, hyphenated: Pritz-san, Diana-chan, -sama. Japanese name order.
- Punctuation: 「」 -> "...", 『』 -> "..." (spell/item names in quotes), …/・・・ -> `...`, ！？ -> `!?`, ～ at the
  end of a drawn-out line -> `~`. Stammers `I-I...`. Onomatopoeia -> English equivalents.
- Money: "500 TK". HP/EXP as is.
- Kanji in this dump were read off the game's font; if a word looks wrong (one odd kanji), trust context and report
  `UNSURE: id - kanji`.

## Consistency
Never edit `glossary.md` or any file except your output. For a recurring name or term not in the glossary (item,
spell, monster, townsperson, place), pick a form, use it consistently, and report it.

## Report (reply with only this)
Files written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.
