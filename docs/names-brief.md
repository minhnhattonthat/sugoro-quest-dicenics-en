# Names + labels brief - Sugoro Quest++ Dicenics

Translate the game's name lists (characters, items, spells, traps, key items, weapons/armour, monsters) and the
small pre-rendered menu labels. Read `docs/translator-brief.md` (Style, Consistency) and `glossary.md` first:
glossary names and terms are binding. Do all translation yourself; no subagents.

## Input: `work/tl/names.tsv`
`id<TAB>kind<TAB>limit<TAB>Japanese`.
- `N..` ids are name strings inserted into dialogue (e.g. `{v1} used "{v5}"!`, `Weapon: "{v6}"`). Limits: `60px`
  (character/monster names) or `90px` (items etc.) in the dialogue font, and at most 21 bytes (ASCII chars).
- `+label64` / `label64`: the text is also (or only) drawn as a 64 px menu label in a tiny 3 px font (~14-16
  characters). It must fit there too.
- `L..` ids are menu labels only: commands (まほうをとなえる = "Cast Magic"), spell categories, party sides,
  Diceman numbers (ダイスマン1ごう = "Diceman No. 1").
- Lists are in game order: the neighbours tell you what kind of thing it is (healing spells, traps, dice, horns...).

## Consistency with the script (important)
The dialogue is already translated (`script/g*.json`, fields jp/en). Before naming an item, search the script for it,
e.g. `python -X utf8 -c "import json,glob;[print(e['id'],e['en']) for f in glob.glob('script/g*.json') for e in json.load(open(f,encoding='utf-8')) if 'jp' in e and 'ヤキトリ' in e['jp']]"`,
and reuse the English the dialogue already uses. If the dialogue uses a clumsy form, use the better one and report
`RENAME: jp -> new (script ids)` so the dialogue gets fixed.

## Style
- Full names, never abbreviated. Fantasy-RPG register; keep jokes (コタツのあし "Kotatsu Leg", ヤキトリのクシ
  "Yakitori Skewer" - silly weapons are intentional). Monster names: use the established English for real
  creatures (Lich, Medusa, Succubus...), otherwise romanize/adapt.
- Title Case for items, spells, monsters. Numbers as ASCII digits ("Amulet 1").
- Plain ASCII only; no quotes inside names; no `; * < > @`.

## Output: `work/tl/names.out.tsv` (file-write tool, not a shell heredoc)
`id<TAB>English`, every id once. Validate with `python -X utf8 tools/namelist.py check` until OK.

## Report (reply with only this)
Entry count; `NEW TERM: jp -> en` for notable names; `RENAME: ...`; `UNSURE: id - note`.
