---
description: Draft a CV for one queued job from the user's confirmed CV lines, check it against every writing rule, and start its pack. Use when the user says "I need a CV for this one", or after recall for each queued job.
argument-hint: "<job> | rebuild <job>"
---

# Compose CV

Draft a targeted CV from the user's confirmed lines in `profile/atoms.json`. Every line in the CV traces to an atom id (or is a visible placeholder, or the user's own recorded words). The kit selects and arranges. It does not invent claims.

`$ARGUMENTS` is one of:

- `<job>`: a slug in `profile/jobs/`, or the role and company in the user's words (match it to a job file; ask if two could match);
- `rebuild <job>`: rebuild from the pack's saved `recipe.json` (skip to Step 4);
- nothing: every queued job without a pack, one at a time.

If the user names a job that isn't in `profile/jobs/` yet, run `/add-jobs` first, then `/triage` for it.

To the user, this is "your CV for the Acme job". Never show them atom ids, tiers, archetypes, tones, claim domains, recipes or gate tables: those go in `recipe.json`. Show them plain lines.

---

## Step 0: Privacy check

Run `python scripts/privacy_check.py`. On exit 1 or 2: stop, show its message as it is, write nothing, and don't go on until it passes.

## Step 1: Load

Read, in full:

1. `profile/profile.json`: identity, and `settings` (`spelling`, `paper`, `cv_max_pages`, `output`, `rules_on`, `rules_off`).
2. `profile/atoms.json`: the only source of CV text. **Only atoms with a `confirmed` date are used.** Roles, education and certifications confirmed during recall count as confirmed.
3. `profile/stories.md`: what each bullet's `evidence` ids point to.
4. `profile/targets.json`: role anchor, years gate, level, domains, avoid list, claim domains, archetypes.
5. `profile/constraints.json`: notice, salary, location, work pattern, right to work, and every `never-name` list.
6. `profile/decisions.json`: the user's standing decisions. They apply to this CV.
7. `profile/voice.md`: how the user writes, and their keep / cut reactions to past drafts.
8. Kit rules: `rules/composition-rules.json`, `rules/anti-patterns.json`, `rules/review-lenses.json`, `rules/submission-rules.json`.
9. `profile/rules-local.json`: the user's own rules (checked after the kit's).
10. `docs/method.md` for tone meanings and the matching method, if anything below is unclear.

Then the job: `profile/jobs/<slug>.md` (front matter gives `source-url`, `apply-url`, `deadline`, `triage`, `triage-why`).

**Is it a record?** If `profile/ledger.jsonl` shows this slug at `sent` or later, stop: a sent pack is a record and is never rewritten. If the user is applying to the same employer again, that's a new job: add it with `/add-jobs` (it gets its own slug).

**Anything new?** Ask, in plain words: "Before I draft this one: anything you've remembered since we last talked?" If yes, run `/recall` for it first. Skip this question when coming straight from the recall interview.

If a required file is missing or fails to parse, stop and say which. Suggest `python scripts/lint_profile.py profile`.

---

## Step 2: Parse the job

Triage has already happened (`/triage`); read its result from the job file, don't redo it. Extract, for the recipe:

| Field | What |
|---|---|
| Role title | Exact title from the ad |
| Company | Hiring organisation |
| Seniority | Junior / Mid / Senior / Lead, from the language and years asked for |
| Years asked | The number, if stated |
| Required skills | Must-haves |
| Preferred skills | Nice-to-haves |
| Culture signals | Values, ways of working, team shape |
| Echo keywords | Exact phrases worth mirroring where atoms support them |
| Archetype | Best fit from `targets.json` `archetypes` (compare the ad against each archetype's `select_tags`) |
| Tone | The archetype's `tone`, adjusted for culture signals; one of the tones in `docs/method.md` |
| Application route | The ATS or form, if the URL shows it (for example Workday, Greenhouse, Lever, Workable); else "generic ATS" |
| Salary, location, pattern | As stated, or "not stated" |

**No archetype yet?** Early on `targets.json` may have none. Draft one from this job (an id like `arch-customer-support`, `select_tags` from its required skills, `tone: "plain"`, `include_projects: "relevant"`, `lead_role` the most relevant role) and add it to `targets.json`. This is internal; don't ask the user about it. If later jobs keep misfitting, propose a new one the same way.

Check the job against anything in `targets.json`, `constraints.json` or `decisions.json` that triage may not have covered (a decision made since, a constraint added during recall). If something now clashes, tell the user in a line and ask whether to go ahead. If they stop here, offer to record it as not going ahead (`/track <slug> killed`, their reason in their words).

---

## Step 3: Match

### Three-tier tag matching against confirmed atoms

- **Tier 1, anchor atoms:** two or more required-skill tag matches. The backbone of the CV.
- **Tier 2, supporting atoms:** one required-skill match, or one or more preferred-skill matches.
- **Tier 3, contextual:** match culture signals or echo keywords but no skill tags.

Within each tier:

- **Tone filter:** prefer atoms in the chosen tone. Flag atoms whose tone conflicts (for example a `candid` atom for a formal employer); the user decides.
- **Strength as tiebreaker:** high, then medium, then low.
- **Claim domain:** note each atom's `claim_domain`. A CV must not let a claim borrow terms from a domain it does not belong to (see the claim-domain rule in `rules/composition-rules.json`).
- **Evidence:** note any bullet whose `evidence` is only an old CV in `sources/`. It can still be used, but the gate asks whether every claim survives a second question.

### Gap analysis

For each required skill with no atom behind it:

- **(a) Bridge:** the closest atom that partly covers it, and why.
- **(b) Cover letter:** address it in the letter instead of the CV.
- **(c) Recall:** the user may have done this but not told you yet. Ask one recall question about it (as in `/recall` Step 4), and if a confirmed story and line come out of it, use them.

A gap with none of these is **unresolved**. Never fill it with invented text.

### Match confidence

- **strong:** mostly Tier 1 anchors; gaps are nice-to-haves or bridged.
- **stretch:** solid Tier 1 and 2 coverage, but one or more hard requirements need letter work.
- **speculative:** significant gaps in required skills; applying on adjacency.

### Tell the user the plan, plainly

Keep the full match (tiers, ids, tones, domains) for the recipe. Show the user a few lines:

```
Your CV for Support Coordinator, Northwind:
  Leading with: the outage call-backs at Acme, and running the weekly rota.
  Also using: your spreadsheet tracker, first-line equipment fixes.
  Not covered: training new staff. The letter will say what's closest, honestly.
  One thing I need from you: <a recall question for a gap, if any>.
OK to go ahead?
```

Wait for a go-ahead or changes. From `/start`, one go-ahead may cover all the queued jobs ("I'll draft all three the same way: OK?").

---

## Step 4: Compose

Assemble the CV from the selected confirmed atoms only. It must be ATS-safe by default.

### Writing voice (default)

Order inside each claim: **what changed for the people who used the work, then what it did for the business, then the tools or activities last.** Prefer atoms already written this way and lead each role with them. Tools and activities with no outcome go to the Skills section or are cut. If the user's `voice.md` or `decisions.json` sets a different order, theirs wins.

### Format rules

1. **Headline** below the name, mirroring the target title: `<Target Role Title> | <one differentiator>`. The differentiator comes from a fragment or atom.
2. **Standard section names only:** Summary, Skills, Certifications, Experience, Projects, Education, Languages. Creative names make ATS parsers drop content.
3. **Skills grouped into 3 to 5 labelled lines, never one flat comma run.** Each line has a bold label chosen for this role, for example:

   ```
   **Customer service:** complaint handling, call-backs, booking systems
   **Admin:** rotas, records, filing
   **Tools:** Excel (trackers, lookups), Outlook
   ```

   Keep exact ad phrasing where an atom supports it. **Named tools and named techniques only.** Cut generic soft-skill labels ("problem solving", "team player", "stakeholder management", "attention to detail" and the like): everyone claims them and the bullets show them better. Aim for 12 to 20 items, fewer for a thin profile. Over 20, cut.
4. **Experience in flat form**, most recent first. For each role: the job title (from `title_variants` or `title_canonical`) as a heading; then company and location; then the date range in one consistent format; then bullets.
5. **Contact details in the body**, never in a document header or footer. Include location and work-pattern intent from `constraints.json` (for example "Riverton (open to hybrid)").
6. **URLs as plain text**, not markdown links: `linkedin.com/in/handle`.
7. **Languages** as its own section, from `identity.languages`.
8. **No images, tables or text boxes.**
9. **Spelling** follows `settings.spelling`. **Length** must fit `settings.cv_max_pages` once exported. A thin profile makes a short CV; one strong page is better than two padded ones.

### Section order

1. Identity: name, headline, contact, plain-text URLs.
2. Summary: from confirmed `fragments`.
3. Skills: grouped lines, from confirmed `skills`.
4. Certifications: `status: held` only, unless the user says otherwise. An in-progress one may be listed as "in progress" only with the user's agreement.
5. Experience: confirmed bullets under each role. Roles with no selected bullets show as title, company and dates only, or are reduced to an "Earlier roles" line, as the user prefers.
6. Projects: confirmed `projects`, per the archetype's `include_projects`.
7. Education: confirmed `education`.
8. Languages.

### Composition rules

- Clean markdown. No atom ids in the CV.
- No text that is not from a named confirmed atom, fragment, or the user's own words. Where the user has not supplied something the CV needs, write a visible placeholder: `[USER: what is needed]`. Placeholders are recorded in the recipe and listed in `PACK.md`.
- Atom text is the user's. Do not rewrite, paraphrase or "improve" it. If a change is needed (register, length, a confidential name), propose the exact edit, get the user's approval, and record it in `selections.compose_time_edits` with the reason. Text the kit drafted in this same session, before the user approved it, may be tidied without asking, as long as no claim changes.
- No name from any `never-name` list in `constraints.json` may appear. Where an atom carries one, propose a neutral description ("an internal reporting tool", "a client's loyalty scheme") as a compose-time edit.
- Never compose a vanity count: a number that measures output (documents written, requirements captured, tickets closed) rather than an outcome. Test: did the number change something in the world, or is it something the user produced? If produced, cut it. Measured outcomes, external validation, money and scale are allowed.
- Never present a "live" or "in production" claim the user has not confirmed is still true. Check project atoms' `live` and `url`; a dead link is worse than none.
- Title variants are chosen from `title_variants`, never invented.

---

## Step 4.5: Anti-pattern scan

Check every sentence in the Summary, the headline and any free-text section against every pattern in `rules/anti-patterns.json` and in `profile/rules-local.json` if it has any. Bullet atoms are checked by the reader-lens pass and the gate, not rewritten here.

Record every flag in the recipe's `scan.anti_pattern_flags`. Fix what you drafted yourself (fixes keep the facts and change only the rhetoric). Anything that would change the user's own wording is put to them as a plain choice: "Your summary says 'passionate about customers'. Hiring managers skim past that. Keep it, or say 'I like sorting out customers' problems'?" If the user spots a pattern that is not in the library, offer to remember it in `profile/rules-local.json`.

## Step 4.6: Reader-lens pass

Read the whole CV, bullets included, through every lens in `rules/review-lenses.json`. The voice lens reads against `profile/voice.md`. Lenses are advisory and can conflict (see the file's conflicts section): where two pull against each other, state the trade-off in plain words and let the user choose. A lens flag on an atom becomes a proposed edit for the user, never a silent change. Record flags in `scan.lens_flags`.

## Step 4.7: Submission rules gate (blocking)

**Do not show the CV until this gate has run.**

Check the assembled CV against every rule in `rules/submission-rules.json` and every rule in `rules/composition-rules.json`, then every rule in `profile/rules-local.json`. A kit rule with `"default": false` runs only if its id is in `settings.rules_on` in `profile.json`; a rule listed in `settings.rules_off` is recorded as `N/A` with the note "switched off by the user", never silently dropped. A local rule can add a check but cannot switch off a kit rule. Every rule gets its own entry in the recipe's `scan.gate` (`PASS`, `FAIL`, `PASS WITH FLAG`, `N/A`, with the offending text in `note`). Do not summarise, and do not skip rules that look obviously fine. The table goes in the recipe, not to the user.

Then these checks, always run:

- **Never-name check:** every name in every `never-name` item of `constraints.json`, searched case-insensitively in the CV. Any hit is a blocking fail. Record in `scan.never_name_check`.
- **Placeholder count:** list every `[USER: ...]`.
- **Spelling:** consistent with `settings.spelling`.

Any blocking FAIL is fixed before showing. A high-severity FAIL may be shown with the issue stated plainly for the user to decide. After any edit, re-run the gate on what changed, including rules already passed earlier in the session: fixes often bring back a pattern removed before.

---

## Step 5: Save the pack

Save to `profile/packs/<slug>/` (the slug from the job file). The pack is saved as a draft now; the user's reading and editing is the later `reviewed` step.

### CV: `CV-<slug>.md`

```yaml
---
type: cv
target-role: <title>
target-company: <company>
created: <YYYY-MM-DD>
job: jobs/<slug>.md
---
```

Then the CV in markdown.

### Recipe: `recipe.json`

Must validate against `schemas/recipe.schema.json`. In outline:

```json
{
  "meta": {
    "created": "YYYY-MM-DD",
    "status": "draft",
    "target_role": "", "target_company": "",
    "archetype": "<id from targets.json>",
    "tone": "plain",
    "match_confidence": "strong", "match_note": "",
    "triage": { "role_anchor": "in", "years": "within", "flags": [], "user_decision": "<from the job file's triage>" },
    "jd_source": "jobs/<slug>.md",
    "ats_platform": "",
    "ledger_slug": "<slug>",
    "decisions": ["<ids from decisions.json that shaped this CV>"],
    "ready_to_send": false
  },
  "selections": {
    "fragments": ["pf-..."],
    "certifications": ["cert-..."],
    "education": ["edu-..."],
    "roles": { "role-x": { "title_variant": "", "bullets": ["b-..."] } },
    "projects": ["proj-..."],
    "skills": ["sk-..."],
    "placeholders": [{ "location": "Experience, role-x, bullet 2", "needed": "..." }],
    "user_text": [{ "location": "", "text": "", "source": "the user's words, not yet a confirmed line" }],
    "compose_time_edits": [{ "atom": "b-...", "edit": "'<before>' -> '<after>'", "reason": "", "approved_by_user": true }],
    "excluded": [{ "id": "b-...", "reason": "" }]
  },
  "gaps": {
    "bridged": { "<requirement>": ["b-..."] },
    "cover_letter": ["<requirement>"],
    "unresolved": ["<requirement>"],
    "recommended_extract_atoms": ["<what to ask about in the next recall>"]
  },
  "scan": {
    "anti_pattern_flags": [],
    "lens_flags": [],
    "gate": { "<rule id>": { "result": "PASS", "note": "" } },
    "never_name_check": { "result": "PASS", "names_checked": 0, "hits": [] },
    "output_checks": []
  }
}
```

`meta.status` stays `"draft"` and `meta.ready_to_send` stays `false` in the recipe. Where the pack stands lives in the ledger and in `PACK.md`, and only the user moves it.

### Word, and PDF if switched on

Run the central generator (never a per-pack copy):

```
python templates/docx/generate_docx.py "profile/packs/<slug>/CV-<slug>.md" "profile/packs/<slug>/CV-<slug>.docx"
```

The .docx is single-column, uses system fonts, keeps contact details in the body, uses Word heading styles for sections and native list items for bullets, and has no images. If the output breaks any of this, fix `templates/docx/generate_docx.py` itself.

PDF only if `settings.output` is `docx+pdf` and the tools are there (see `/export`). Then run `/export <slug> cv` for the checks.

### `PACK.md`

Create it now; `/compose-cover-letter` adds to it. Plain words throughout: the user reads this.

```markdown
---
status: drafted
role: <title>
company: <company>
created: <YYYY-MM-DD>
---

# <Role>, <Company>

## How well it fits
<Two or three plain lines: what's strong, what's thin. From the match, in the user's terms. For example: "Strong on customer service and keeping records. They want training experience, which you haven't got yet; the letter says what's closest.">

## What only you can fill in
1. <Each [USER: ...] placeholder: which file, where, what's needed.> Search both files for `[USER:` before sending.
(or "Nothing. Read it through and change anything that doesn't sound like you.")

## Be ready to be asked about
- <Lines the ad will probe, especially ones backed only by the old CV, and the gaps left on purpose.>

## Apply
<apply-url, else source-url>. Deadline: <date or none stated>. Salary: <as stated or not stated>.

Form questions you may get:
- Notice period: <from constraints.json, or "not on file">
- Expected salary: <from constraints.json if set, otherwise your decision>
- Right to work: <from constraints.json, or "not on file">

## Files
- CV-<slug>.docx (Word, to send) and CV-<slug>.md (the source)
- CL-<slug>.docx and CL-<slug>.md (once the letter is drafted)

## Checklist
1. Read the CV and letter. Change anything that isn't how you'd say it.
2. Fill in or delete every gap marked `[USER: ...]`.
3. Tell me when you're happy with it ("I've checked the Acme one"), and I'll mark it reviewed and rebuild the Word files if you edited them.
4. Send it yourself, through the apply link.
5. Tell me it's sent ("sent the Acme one"), and I'll keep a record of exactly what went.
```

Fill form answers only from the profile. Anything not on file says "not on file", never a guess.

---

## Step 6: Show the user

Show the CV (the markdown is fine), then a few plain lines:

```
Your CV for Support Coordinator, Northwind is drafted.
  One page. Checked against the writing rules: clear.
  One gap for you to fill: a sentence on why Northwind (I left a marker).
Next: the cover letter.
```

If the gate left a high-severity flag for them to decide, say what it is in a sentence. Changes they ask for now are made, re-checked (Steps 4.5 to 4.7) and saved.

Then go on to `/compose-cover-letter <slug>`. Once the CV and letter both exist (or the user says no letter is needed), record `drafted` through `/track`, `voice: "assistant"`, note "CV and letter" (or "CV only"). That is the only stage this procedure may record.

---

## Rules

1. **Run the submission rules gate (Step 4.7) before showing anything.** It is not optional and not a summary step. Its full results go in the recipe.
2. **Only confirmed atoms.** Never write a claim not sourced from a named confirmed atom. If the user wants to add something new, take it through `/recall` first, or record it as `user_text` with their words.
3. **Atom text is the user's.** Propose edits; never make them silently. The protection covers the user's claims, not the kit's own same-session drafting.
4. **Claims lead with the change for people, then the business result, then the tools.**
5. **Claim domains do not blur.** Check `claim_domain` on every atom used.
6. **No vanity counts. No unverified live claims. No soft-skill labels in Skills. No flat comma-run skills list.**
7. **Never-name lists are absolute.**
8. **Recipes make the CV reproducible.** A recipe saved today rebuilds the same CV tomorrow.
9. **The kit never marks a pack reviewed or sent, and never sends anything.** Drafted is as far as it goes.
10. **A sent pack is a record.** Never rewrite its files.
11. **No internal words to the user.**
