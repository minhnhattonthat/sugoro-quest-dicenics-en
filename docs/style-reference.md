# Style reference - Sugoro Quest++ Dicenics

Approved pilot: batch b7a (game setup, intro poem, the King's audience, banter, announcements). Match its voice.

## Voices
| Who | JP markers | English voice | Example (id) |
|---|---|---|---|
| Pritz | ボク, ～だね | playful, teasing, gender-neutral (never he/she; use the name or "they") | 701E "All right! / This match is mine, no question!" |
| Tanguy | オイラ, ～ぜ, 強ェ | brash young dragon, boastful, kiddish drawl | 7020 "Knew it! I'm the strongest, y'know!" |
| Ulrik | ～のじゃ, ～かのう | old woman, archaic and stately | 7024 "I must gather more money, I must." |
| Cynthia | 私, ～わ, ～かしら | gloomy, sighing, self-pitying | 702A "Can I never win without better luck?" |
| Dechtel | オレ様, ガハハ | swaggering vampire braggart | 702B "Don't you dare attack the great me!" |
| Diana | ～ですぅ, ～わ～ | airy, sweet, overly polite, trailing "~" | 702F "Oh dear~, whatever shall I do~?" |
| The King | ワシ, ～じゃ, おぬしら | regal, grandfatherly, "Ho ho ho." | 7034 "Welcome, four adventurers. / I am the King of Siland." |
| Narrator / system | です・ます | plain, friendly game-show announcer | 7043 "The Map 1 adventure begins!" |

## Pairs
- 7005 `{v1}は、何もないマスにとまった。` -> `{v1} stopped on an empty space.`
- 7006 `{v1}はワープマスへ入った！…不思議な力で他のワープマスへ運ばれます！` -> `{v1} entered a warp space! / A mysterious force carries {v1} / off to another warp space!`
- 7013 `これでよろしいでしょうか？ / はい いいえ` -> `Is this all right? / {at4}Yes{at11}No` (choice columns copied from the hint)
- 7022 `トホホホ、次は何をすればいいんだ～ / トホホホのホ～！` -> `Waaah, what am I s'posed to do next~? / Woe is meeee~!` (gag kept, not literal)
- 7036-7039 item lists: `Weapon: "{v6}"`, `Armor: "{v6}"`, `Shield: "{v6}"`.
- 7040 death: "they"-free phrasing around `{v1}` (the name may be any character or monster).
- 7048 `プリッツさん、がんばって下さいね！` -> `Good luck, Pritz-san!` (honorific kept, hyphenated)
- Corrected example: 7002 first draft ran 238 px; fixed by trimming to `Power in the sword, magic in the staff...` (199 px).

## Mechanics learned
- Text never wraps by itself: put `{nl}` where each line ends. Each line <= its px limit, and each page ({clr}) has
  at most as many lines as the Japanese page (count includes a trailing empty line after a final `{nl}`).
- `{atN}` jumps to cell N (12 px units) of the line: use it for choice columns (copy the hint) and, optionally, to
  centre short title-card lines (7000-7004). Never needed for normal dialogue.
- Leading spaces in the Japanese are centering; drop them.
