---
description: Re-check a pack's CV and letter for weak or AI-sounding phrasing and for names that must never appear, before sending. Reports and proposes fixes; never fixes without the user's say-so.
argument-hint: "<job> [cv|cl] | all"
---

# Scan

Quality check before sending, typically after the user has edited a pack. Scans CVs and cover letters against the anti-pattern library and the user's never-name lists.

`$ARGUMENTS` is one of:

- `<job>`: the CV and letter in that pack (slug, or role and company in the user's words)
- `<job> cv` or `<job> cl`: one of them
- `all`: every pack not yet sent

---

## Step 0: Privacy check

Run `python3 scripts/privacy_check.py`. On exit 1 or 2: stop, show its message as it is, write nothing, and don't go on until it passes. (This procedure updates `recipe.json` and may edit the pack.)

## Step 1: Load

1. `rules/anti-patterns.json`, plus any patterns in `profile/rules-local.json`.
2. `profile/constraints.json`: collect every name from every item with `kind: never-name`.
3. `profile/profile.json`: `settings.spelling`.
4. `profile/ledger.jsonl`: which slugs are at `sent` or later (scanned if named, but never edited).
5. Find the files in `profile/packs/`:
   - `<job>`: `CV-<slug>.md` and `CL-<slug>.md`; also `PACK.md` for the never-name check
   - `<job> cv|cl`: just that one
   - `all`: every pack that is not sent

If nothing matches, say so and list the packs there are, by role and company.

---

## Step 2: Scan

For each file, read it in full.

**Never-name check.** Search for each never-name, case-insensitively, including obvious short forms and initials the user listed. Any hit is reported first, as blocking. This includes `PACK.md`, since it may be pasted into a form.

**Anti-patterns.** Check every pattern in the library against the text and classify each:

- **HIT:** clearly present and it weakens the text.
- **BORDERLINE:** close, but context may justify it. The user decides.
- **CLEAN:** not present.

Use judgement, not just string matching. Consider the context of the phrase, whether it is used the way the pattern describes, and whether several borderline items together create a tone problem.

**Spelling.** Note any spelling that does not match `settings.spelling`.

---

## Step 3: Report

Record every result in the pack's `recipe.json` (`scan.anti_pattern_flags`, `scan.never_name_check`; the letter's under `cover_letter.scan`), unless the pack is sent.

To the user, plain words, worst first, quoting the exact text:

```
CV for Northwind:
  1. "Passionate team player" in the summary: says nothing a reader can check. Suggest cutting it.
  2. (Maybe) "Spearheaded the rota": sounds unlike you. Suggest "Ran the weekly rota".
Letter: all clear.
```

Never-name hits come first and are marked as must-fix. Then hits, then borderline items as "(Maybe)". Mention repeated phrasing between CV and letter, or wasted words, separately and briefly. If three or more borderline items sit in one file, say the overall tone is at risk even if none is a definite hit.

---

## Step 4: Fix

If there are hits or borderline items:

1. Offer a rewrite for each. Rewrites keep the facts and change only the wording (or replace a never-name with a neutral description).
2. Wait for the user: "do them all", "just 1 and 3", or "leave it".

Never apply a fix without the user's confirmation. Never edit a sent pack. If a fix touches a CV line that came from their history, offer the same change there too (with `amended` and `amend_reason` in `atoms.json`), so the problem doesn't come back in the next CV.

After fixes, re-run the never-name check and any rules from `rules/submission-rules.json` that the change could affect, and update the recipe's `scan` block.

## Step 5: Rebuild the files

If anything changed, rebuild the Word files with `/export <slug>`.

---

## Rules

1. **Scan against every pattern in the library**, not a subset.
2. **Never-name hits are blocking**, wherever they appear.
3. **Judgement over string matching.** A phrase that is a plain factual description in one place may be a tone problem in another.
4. **Severity sets the order.** Never-name first, then high, medium, low.
5. **Never auto-fix.** Report, propose, wait.
6. **Flag compounding.** Three or more borderline items in one file: flag the overall tone risk even if none is a definite hit.
7. **No internal words to the user.** Pattern ids stay in the recipe.
