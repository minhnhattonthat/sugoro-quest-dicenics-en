# Translation reviewer brief - Sugoro Quest++ Dicenics

You review one batch of a JP->EN fan translation. Read-only: no edits, no git, no subagents. Mechanical validity
(ids, control codes, ASCII, width, lines per page) is already enforced by the check tool - judge translation quality.

## Inputs (paths in your dispatch)
- Pairs file: every translated entry as `>> id | JP` / `EN` with +-2 context lines. Read ALL of it, in passes if large.
- `glossary.md` (rulings at the top), `docs/style-reference.md`, the translator's report (unverified claims).
- Note: some kanji in the JP were read off the game font and may be wrong; judge by context.

## Judge
- Accuracy: mistranslation, omission, addition, wrong speaker or addressee, reversed meaning. Quote the JP and say
  what it means.
- Consistency: glossary names/terms exactly (a one-letter slip is what players notice); honorifics kept; voice per
  character matches the style reference (Pritz gender-neutral).
- Things players caught that reviewers missed: jokes/wordplay losing their punch; ordinal suffix after a variable
  ("1th"); abbreviated names or terms; stock phrases that read awkwardly in English ("... GET!"); "a/an" before a
  name variable.
- Naturalness: would a fan-translation reader stumble?

## Report
### Issues
#### Critical (meaning reversed, broken placeholder grammar, wrong speaker)
#### Important (clear mistranslation, glossary inconsistency, abbreviation)
#### Minor (style - deferred to one polish pass)
Each: `id - JP gist - problem - suggested EN` (suggested EN must keep the control codes and fit: use
`python -X utf8 tools/batches.py fit "..."` to check width).
### Assessment
Approved | Needs fixes - one sentence why.
