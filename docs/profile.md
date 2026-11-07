# The profile

Your profile is everything the kit knows about you: your history, your stories, the jobs you're looking at and the packs made for them. It lives in the `profile/` folder of **your own private copy** of this repository.

**Nothing personal is written until the privacy check passes.** Every step that would write to `profile/` first runs:

```
python scripts/privacy_check.py
```

It exits 0 only when it has confirmed the repository is private. It exits 1 when the repository is public, and 2 when it can't tell. On 1 or 2 the kit stops and shows the message, which says how to fix it. See `docs/privacy.md`.

## Files

```
profile/
  profile.json        identity and settings
  sources/            what the user handed over, as given: old CVs, pasted text (one file each)
  stories.md          the user's stories from the recall interview, in their words; the evidence behind every claim
  atoms.json          the CV atom library: every line a CV or letter can be built from
  constraints.json    facts that limit the search (notice, salary floor, location, names that must never appear)
  targets.json        what the search is for: roles in and out, years, level, domains, claim domains
  decisions.json      rules the user has set for their own search and writing
  voice.md            how the user writes, with samples and keep/cut reactions to drafts
  rules-local.json    the user's own writing rules, same shape as the kit's
  ledger.jsonl        every job's status changes, one JSON object per line, append-only
  jobs/<slug>.md      each job ad, with its triage
  packs/<slug>/       one pack per job: CV, cover letter, fit note
```

The kit ships with `profile/` holding blank files. `python scripts/lint_profile.py` checks the profile against `schemas/`.

## profile.json

```json
{
  "schema_version": 1,
  "created": "YYYY-MM-DD",
  "identity": {
    "name": "", "headline": "", "location": "", "email": "", "phone": "",
    "links": [{ "label": "LinkedIn", "url": "" }],
    "languages": []
  },
  "settings": {
    "paper": "A4",
    "spelling": "en-GB",
    "cv_max_pages": 2,
    "cl_max_pages": 1,
    "output": "docx",
    "rules_on": [],
    "rules_off": []
  },
  "welcome_done": false
}
```

- `output` is `docx` (the default) or `docx+pdf`. PDF needs pandoc and a Chromium browser on the machine.
- `rules_off` switches off kit rules that ship on; `rules_on` switches on rules that ship with `"default": false`.

## stories.md

The raw material. One section per story, written down from the recall interview in the user's own words as far as possible:

```markdown
## st-01 · <role id> · <rough date>

**Prompt:** what was asked
**Story:** what they said, lightly tidied, nothing added
**Who it was for:** ...
**What changed for them:** ...
**What it did for the organisation:** ...
**How someone could check:** ... (or "nothing to point to")
**Confirmed:** YYYY-MM-DD
```

A story is only used once it's confirmed. Atoms link to stories by id.

## atoms.json

Atoms are the source of truth for CV and letter text. Packs select atoms; they never invent claims. Atoms are drafted by the kit **from stories**, and kept only when the user confirms them. The user never has to write an atom.

```json
{
  "certifications": [{ "id": "cert-x", "name": "", "issuer": "", "date": "YYYY-MM", "credential_id": "", "status": "held|in-progress|expired", "tags": [] }],
  "education":      [{ "id": "edu-x", "name": "", "institution": "", "period": "", "detail": "", "tags": [] }],
  "roles":          [{ "id": "role-x", "company": "", "company_description": "", "title_canonical": "", "period": "YYYY-MM to YYYY-MM|present", "scope": "", "is_current": false, "tags": [] }],
  "bullets":        [{ "id": "b-x", "role_id": "role-x", "text": "", "tags": [], "tone": "plain", "strength": "high|medium|low", "claim_domain": "", "evidence": ["st-01"], "confirmed": "YYYY-MM-DD", "amended": "", "amend_reason": "" }],
  "projects":       [{ "id": "proj-x", "name": "", "type": "", "platform": "", "url": "", "live": false, "description": "", "tags": [], "bullets": [], "claim_domain": "" }],
  "skills":         { "<category>": [{ "id": "sk-x", "name": "", "detail": "", "tags": [] }] },
  "fragments":      [{ "id": "pf-x", "kind": "anchor|claim|value", "text": "", "tags": [] }],
  "title_variants": { "role-x": ["Alternative title"] }
}
```

- `evidence` lists story ids. A bullet with no story behind it must be one the user wrote on their old CV (evidence `"sources/<file>"`).
- `confirmed` is the date the user said yes to the wording. Unconfirmed bullets are never used in a pack.
- `claim_domain` is one of `targets.json` `claim_domains`. `tone` is one of `formal`, `candid`, `bridging`, `impact-focused`, `minimal`, `technical`, `plain` (see `docs/method.md`).

## constraints.json and decisions.json

```json
{ "items": [
  { "id": "notice-period", "kind": "notice-period", "statement": "1 month", "voice": "user", "said": "their words", "as_of": "YYYY-MM-DD" }
] }
```

- `voice` is `user` (needs `said`: their words) or `source` (needs `source`: the document it came from).
- Constraint `kind`: `notice-period`, `available-from`, `contract-end`, `salary-floor`, `salary-band`, `location`, `work-pattern`, `right-to-work`, `clearance`, `never-name`, `hours`, `other`.
- `never-name` items carry `names: []`: words that must never appear in a pack (internal project names, clients, anything a confidentiality clause covers).
- decisions.json uses the same shape, with `kind`: `voice`, `targeting`, `process`, `other`.

## targets.json

```json
{
  "role_anchor": { "in": [], "out": [], "note": "" },
  "years_gate": { "apply_up_to": 3, "stretch_up_to": 5 },
  "level": "entry|junior|mid|senior|lead",
  "domains": { "in": [], "out": [] },
  "avoid": [],
  "claim_domains": [],
  "archetypes": [{ "id": "arch-x", "name": "", "select_tags": [], "tone": "plain", "include_projects": "none|relevant|all", "lead_role": "role-x" }]
}
```

Targets start thin. The kit fills them in from the jobs the user pastes and from triage ("not for me, because...").

## jobs/<slug>.md

YAML front matter, then the ad's text as given:

```yaml
---
role: ""
company: ""
salary: ""
location: ""
seniority: ""
source-url: ""        # empty when the user pasted the text
apply-url: ""
added: YYYY-MM-DD
deadline: ""
triage: fit|stretch|not-for-me|undecided
triage-why: ""        # one or two lines: what matches, what's missing
---
```

## packs/<slug>/

```
PACK.md           status, fit and gaps, what only the user can fill, apply link, checklist
CV-<slug>.md      the CV in Markdown (the source)
CV-<slug>.docx    the CV in Word
CL-<slug>.md      the cover letter
CL-<slug>.docx
recipe.json       which atoms were picked and why (schemas/recipe.schema.json)
```

`PACK.md` front matter carries `status: drafted|reviewed|sent`. The status only moves forward on the user's word, through `/track`.

A sent pack is a record: never rewrite it.

## ledger.jsonl

One status change per line, append-only. Never edit or delete a line; correct with a new one.

```json
{"ts":"2026-11-07T10:00:00Z","slug":"ba-acme","stage":"reviewed","as_of":"2026-11-07","voice":"user","said":"happy with that","note":""}
```

Stages are in `docs/stages.md`. A `sent` line carries `files: {"<path>": "<sha256>"}` for every file sent, and the lint fails if one of them changes afterwards.
