# Method

How a CV or cover letter is built from atoms. The file shapes are in [`profile.md`](profile.md); the rules that govern composition are in `rules/composition-rules.json`, and the checks on the finished text are in `rules/submission-rules.json`, `rules/anti-patterns.json` and `rules/review-lenses.json`.

## Atoms

An atom is the smallest reusable piece of career content: one bullet, one role, one certification, one skill, one sentence of a summary. All of the user's CV content is broken into atoms and kept in one file, `profile/atoms.json`.

This replaces keeping a separate CV for every kind of job. There is one source of truth, and each application is a selection from it. When a claim is corrected, it is corrected once, in the atom, and every later CV picks up the correction.

Three principles follow:

- **Compositions select; they do not invent.** Every sentence in a CV traces back to an atom. If a CV needs something no atom says, the answer is a new atom, proposed to the user and confirmed by them, not a sentence written into the CV.
- **Atom text is the user's.** The assistant may propose new atoms and edits. The user confirms. Corrections are recorded with `amended` and `amend_reason` so an old error does not come back.
- **Atoms link to evidence.** A bullet's `evidence` field points at stories in `profile/stories.md` (or, for a line kept from an old CV, at the file in `profile/sources/`). A claim with evidence behind it can be defended at interview.

## Component types

| Component | What it is | Id prefix |
|---|---|---|
| `certifications` | Formal credentials, with issuer, date, credential id and status | `cert-` |
| `education` | Degrees, courses and qualifications | `edu-` |
| `roles` | One entry per job: company, canonical title, period, scope | `role-` |
| `bullets` | One achievement line, tied to a role, with tags, tone, strength, claim domain and evidence | `b-` |
| `projects` | Work outside a job (or a distinct piece within one): what it is, where it lives, whether it is live | `proj-` |
| `skills` | Named tools and techniques, grouped by category | `sk-` |
| `fragments` | Reusable summary sentences: `anchor` (who the user is professionally), `claim` (what they have done), `value` (what they offer this kind of employer) | `pf-` |
| `title_variants` | Alternative, truthful titles for a role, keyed by role id | (role id) |

Identity and contact details are not atoms; they live in `profile/profile.json`.

Each bullet carries:

- **tags**: the keywords it can be selected by (skills, domains, kinds of work);
- **tone**: one of the tone modifiers below;
- **strength**: `high`, `medium` or `low`, used as a tiebreaker;
- **claim_domain**: exactly one of the claim domains in `targets.json` (see rule CR-01).

## Composing by archetype

An archetype is a kind of role the user applies for repeatedly. The user's archetypes are defined in `profile/targets.json` under `archetypes`. Each one names:

- `select_tags`: the tags that make an atom relevant to this kind of role;
- `tone`: the default tone modifier;
- `include_projects`: `none`, `relevant` (only projects whose tags match) or `all`;
- `lead_role`: the role to put first and give the most bullets to.

To compose:

1. **Parse the job description.** Pull out the role title, required skills, preferred skills, culture signals, keywords worth echoing exactly, and the applicant tracking system if the posting URL reveals it.
2. **Pick the archetype** that best fits. If none fits, use the closest and say so; if the same misfit keeps happening, propose a new archetype for `targets.json`.
3. **Select atoms by tag** (below), then run the gap analysis.
4. **Choose title variants.** For each role, use `title_canonical` or one of its `title_variants`, whichever best mirrors the target. Titles are chosen, never invented, and every variant must be one the user could defend.
5. **Assemble** in the order and format set by the composition rules (CR-08 to CR-14).
6. **Check** against the submission rules, the anti-patterns and the review lenses, and report every result to the user.
7. **Save the recipe.**

## Selecting atoms by tag

Match atom tags against the job description in three tiers:

- **Tier 1, anchor atoms:** two or more required-skill matches. These are the backbone of the CV.
- **Tier 2, supporting atoms:** one required-skill match, or one or more preferred-skill matches. These fill out sections.
- **Tier 3, contextual atoms:** match culture signals or echo keywords, but no skill tags.

Within each tier:

- Prefer atoms whose tone matches the recommended tone. Flag atoms with a conflicting tone; the user decides whether to include them. If an included atom's tone differs from the target, use its text as it is; do not rewrite it.
- Rank by strength, `high` before `medium` before `low`.
- Check each atom's `claim_domain` before placing it next to atoms from another domain.

Roles with no selected bullets are left out of the CV.

## Tone modifiers

Every bullet has one tone, and every archetype has a default tone. The tone guides language consistency across a document.

| Tone | Meaning |
|---|---|
| `formal` | Standard professional CV language with the first person implied; the safe default. |
| `candid` | Direct first person that names limitations plainly; for employers that say they value openness. |
| `bridging` | Explicitly connects experience from another field to what the target role needs; for career changes and adjacent moves. |
| `impact-focused` | Leads with the measured outcome or number; for roles that ask for a track record of results. |
| `minimal` | The bare facts, stripped down; for entry-level and trainee roles where less is more. |
| `technical` | Puts tools, platforms and architecture first; for developer and engineering roles. |
| `plain` | Short first-person declaratives, problem before solution, no self-description, no idiom; the closest to how most people speak. |

## Recipes

A recipe records exactly which atoms a composition used and why. It is saved in the pack next to the CV as `profile/packs/<slug>/recipe.json` (shape in `schemas/recipe.schema.json`).

A recipe holds:

- the target: role, company, archetype, tone, job description source, ATS platform;
- the selections: fragments, certifications, roles (each with its chosen title variant and bullet ids), projects, skills;
- the gaps, and how each was handled.

A recipe makes a composition replayable: the same recipe against the same atoms produces the same CV. When an atom is corrected later, replaying an old recipe shows what would change. A sent pack and its recipe are a record and are never rewritten.

## Gap analysis

For each required skill in the job description that no atom covers, choose one of three responses:

- **Bridge:** name the closest atom that partly covers the gap, and say why. The bridge must stay inside that atom's claim domain.
- **Cover letter:** treat the gap as a cover letter point rather than CV content. Name it once, early, and plainly (see SR-15).
- **Extract:** the user may have done this but it is not yet an atom. Ask, and if so, add the atom (with evidence) before composing.

Then rate the overall fit:

- **strong:** most matches are Tier 1 anchors; the gaps are nice-to-haves or easily bridged.
- **stretch:** solid Tier 1 and Tier 2 coverage, but one or more hard requirements need cover letter work.
- **speculative:** significant gaps in required skills; the application rests on adjacent experience and direction of travel.

Record the rating and every gap in the recipe. Over many applications, gaps that keep recurring show where the user's next piece of evidence should come from.
