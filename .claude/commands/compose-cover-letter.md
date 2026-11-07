---
description: Draft a cover letter for a job whose CV is drafted. It covers what the CV can't, honestly, and passes the same writing checks. Use after the CV, or when the user asks for a letter.
argument-hint: "<job>"
---

# Compose Cover Letter

Draft a targeted cover letter from the pack's `recipe.json`. The recipe gives the selection, gaps, archetype and tone. The letter does what the CV cannot: it connects the user's experience to the ad's language and addresses the gaps the match found.

`$ARGUMENTS`: a slug in `profile/jobs/`, or the role and company in the user's words. With nothing, the most recently drafted CV without a letter.

To the user, this is "your letter for the Acme job". Never show them atom ids, recipes or gate tables: those go in `recipe.json`.

**Blocking gate:** no draft is shown to the user until it has been checked against every rule in `rules/submission-rules.json` and `profile/rules-local.json` (Step 3.7). Letters are free text, so they fail these rules more often than CVs do.

---

## Step 0: Privacy check

Run `python scripts/privacy_check.py`. On exit 1 or 2: stop, show its message as it is, write nothing, and don't go on until it passes.

## Step 1: Load

1. `profile/packs/<slug>/recipe.json`. Validate it against `schemas/recipe.schema.json`; if it fails, say what is wrong and stop. If there's no recipe, the CV hasn't been drafted: run `/compose-cv <slug>` first.
2. If `profile/ledger.jsonl` shows this slug at `sent` or later, stop: a sent pack is a record.
3. `profile/atoms.json` (confirmed atoms only), `profile/stories.md`.
4. `profile/packs/<slug>/CV-<slug>.md`, so the letter does not repeat it.
5. The job: `profile/jobs/<slug>.md`.
6. `profile/profile.json` (`settings.spelling`, `settings.cl_max_pages`, `settings.output`, `rules_on`, `rules_off`, identity), `profile/constraints.json`, `profile/decisions.json`, `profile/voice.md`.
7. Kit rules: `rules/composition-rules.json`, `rules/anti-patterns.json`, `rules/review-lenses.json`, `rules/submission-rules.json`; then `profile/rules-local.json`.

If any file is missing, stop and say which.

---

## Step 2: Assemble inputs

| Input | Source |
|---|---|
| Role, company | `meta.target_role`, `meta.target_company` |
| Archetype, tone | `meta.archetype`, `meta.tone` |
| Selected atoms | `selections`, resolved to full text |
| Gaps to address | `gaps.cover_letter` |
| Bridged gaps | `gaps.bridged` (may need reinforcing) |
| Echo keywords, culture signals | re-read from the job ad |
| What the employer says about itself | the job ad, or a primary source the user or the `research` agent provided |

Tell the user the plan in a couple of plain lines, and wait for a go-ahead or a change of emphasis:

```
The letter will open with your two years at Acme, lean on the outage story and the rota,
and say plainly what's closest to the training they ask for.
Is there anything about Northwind itself you want to mention? (Fine if not.)
```

From `/start`, one go-ahead may cover all the queued jobs.

---

## Step 3: Compose

### Writing voice (default)

Each evidence claim leads with **what changed for the people who used the work**, then **what it did for the business**, and only then the tools or method. If `voice.md` or `decisions.json` says otherwise, theirs wins. Write the way the user writes, using `voice.md` samples and their keep / cut list.

### Structure

1. **Opening (2-3 sentences).** The role applied for. The user's current position and one high-value fact, from a fragment or atom.
2. **Bridge (2-3 sentences).** What in the ad connects to the user's work. Mirror one or two echo keywords where natural. Any statement about the employer must come from the ad or another primary source on file. If the user wants a "why this employer" line and none is on file, write a placeholder: `[USER: one sentence on why <company>, in your words, or delete this]`.
3. **Evidence (2-3 paragraphs).** Each paragraph: a claim, the atom behind it, and its link to the ad's language. Lead with the strongest Tier 1 atoms. Theme each paragraph around a cluster of the ad's requirements. A thin profile may need only one or two.
4. **Gaps (1 paragraph).** Address every item in `gaps.cover_letter`. State adjacent experience plainly, as a fact; do not apologise and do not oversell. Use bridged atoms as support.
5. **Close (1-2 sentences).** End on evidence or a plain offer to talk. Not on a desire statement ("I would love to...") and not on a shortcoming.

### Rules for the text

- Every factual claim traces to a confirmed atom, a fragment, the user's own words recorded in the recipe, or the job ad. Connecting language is allowed: the letter argues, the CV arranges. Invented evidence is not.
- Do not repeat the CV. Add context, connection and gap coverage.
- Match the recipe's tone.
- Under 400 words and within `settings.cl_max_pages` once exported.
- Plain letter: no headers or bullet lists in the body.
- "Dear Hiring Manager" unless the ad names a contact.
- Spelling per `settings.spelling`.
- No name from any `never-name` list in `constraints.json`.

---

## Step 3.5: Anti-pattern scan

Check every sentence of the letter against every pattern in `rules/anti-patterns.json` (and any in `rules-local.json`). Record every flag in `cover_letter.scan.anti_pattern_flags`. Fix what you drafted (fixes keep the facts and change only the rhetoric); put anything that touches the user's own wording to them as a plain choice. Offer to remember any new pattern the user spots in `profile/rules-local.json`.

## Step 3.6: Reader-lens pass

Read the whole letter through every lens in `rules/review-lenses.json`; the voice lens reads against `profile/voice.md`. Lenses are advisory and can conflict; state any trade-off in plain words and let the user decide. Lens the paragraph written last with the same care as the first: late additions are where failures hide. Record flags in `cover_letter.scan.lens_flags`.

## Step 3.7: Submission rules gate (blocking)

Every rule in `rules/submission-rules.json` and `rules/composition-rules.json` (those that apply to a letter; mark CV-only format rules `N/A`), then `profile/rules-local.json`. `settings.rules_on` and `settings.rules_off` apply as in `/compose-cv` Step 4.7. One entry per rule in `cover_letter.scan.gate`. Do not summarise, and do not skip rules that look obviously fine. The table goes in the recipe, not to the user.

Plus, always:

- **Never-name check** across the letter. Any hit is a blocking fail.
- **Employer claims:** every statement about the employer is traced to the ad or a named primary source, or is a placeholder.
- **Closing position:** the last sentence is neither a desire statement nor a deficit.
- **Placeholders:** list every `[USER: ...]`.

Fix every blocking FAIL before showing. A high-severity FAIL may be shown with the issue stated plainly. After any edit, re-run the gate, including rules that passed earlier.

---

## Step 4: Save and show

1. Save `profile/packs/<slug>/CL-<slug>.md`:

   ```yaml
   ---
   type: cover-letter
   target-role: <title>
   target-company: <company>
   created: <YYYY-MM-DD>
   cv: CV-<slug>.md
   ---
   ```

2. Add `cover_letter` to `recipe.json`, with the letter's own scan and gate results (same shape as the CV's `scan`):

   ```json
   "cover_letter": {
     "file": "CL-<slug>.md",
     "gaps_addressed": ["..."],
     "primary_atoms": ["b-..."],
     "word_count": 0,
     "employer_facts": [{ "claim": "", "source": "<the job ad or a primary source URL>" }],
     "scan": { "anti_pattern_flags": [], "lens_flags": [], "gate": { "<rule id>": { "result": "PASS" } }, "never_name_check": { "result": "PASS", "names_checked": 0, "hits": [] } }
   }
   ```

   Re-validate the recipe against `schemas/recipe.schema.json`.

3. Word, with the central generator:

   ```
   python templates/docx/generate_docx.py "profile/packs/<slug>/CL-<slug>.md" "profile/packs/<slug>/CL-<slug>.docx"
   ```

   PDF only if `settings.output` is `docx+pdf` and the tools are there: `/export <slug> cl`.

4. Update `PACK.md`: the letter's gaps for the user to fill under "What only you can fill in", the gaps the letter addresses under "Be ready to be asked about", and the letter files. Its `status:` stays `drafted`. If no `PACK.md` exists, create one in the shape given in `/compose-cv`.

5. Show the letter, then a few plain lines: what it leans on, what gaps it covers, and anything for the user to fill. If the user asks where a sentence comes from, show the story or line behind it.

6. Record `drafted` through `/track`, `voice: "assistant"`, note "CV and letter", unless it is already recorded for this slug.

Nothing here marks the pack reviewed or sent. The user reads and edits it, tells you it's ready (`reviewed`), sends it themselves, and tells you it's gone (`sent`).

---

## Rules

1. **Run the gate before showing anything.**
2. **Every factual claim traces to a source.** Connecting language is allowed; invented evidence is not.
3. **The letter complements the CV.** If the CV already covers something well, add context or skip it.
4. **Gap coverage is mandatory.** Every `gaps.cover_letter` item appears.
5. **Under 400 words.** If the case does not fit, the selection is wrong.
6. **No apologies, no overselling.** Adjacent experience is stated as a fact.
7. **Employer claims come from a primary source, or are left to the user.**
8. **The kit never marks a pack reviewed or sent, and never sends anything.**
9. **No internal words to the user.**
