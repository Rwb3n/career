---
description: Go through undecided jobs with the user: good fit, stretch, or not for you, and why. The user decides which ones get a pack. Use after jobs are added, or when the user asks "which of these should I go for?"
argument-hint: "[job ...]"
---

# Triage

For each job in `profile/jobs/` with `triage: undecided` (or the ones named in `$ARGUMENTS`), give an honest read in one or two lines, and let the user decide. The kit suggests; **the user decides**.

## Step 0: Privacy check

Run `python scripts/privacy_check.py`. On exit 1 or 2: stop, show its message as it is, write nothing, and don't go on until it passes.

## Step 1: Load what's known

Read, every time:

1. The job files to triage.
2. `profile/atoms.json` (confirmed lines only) and `profile/stories.md` (confirmed stories).
3. `profile/sources/`: the CV and anything else the user handed over.
4. `profile/targets.json`, `profile/constraints.json`, `profile/decisions.json`, if they have content.

**Early on the profile is thin.** Before the recall interview there may be nothing but the job ads and the CV in `sources/`. That's fine: judge from the ad against the CV, and say plainly when you can't judge until you've talked through their experience ("I can't tell yet whether you've done much with budgets. We'll find out when we go through your jobs.").

## Step 2: Read each job against the profile

For each job, pull out what it asks for: required skills, preferred skills, years asked, level, the kind of work, salary, location and pattern.

Then check:

- **What matches**, from what's known so far: the CV in `sources/`, confirmed lines and stories.
- **What's missing or unknown**: things the ad requires that nothing so far shows. Separate "you don't seem to have this" from "I don't know yet".
- **targets.json** (if set): is the title in `role_anchor.in` or `role_anchor.out`? Is the years asked within `years_gate.apply_up_to`, within `stretch_up_to`, or beyond? `level`, `domains.in`/`domains.out`, `avoid`.
- **constraints.json** (if set): salary floor or band, location, work pattern, right to work, clearance, hours. A clash is stated plainly ("The pay is below the minimum you gave me").
- **decisions.json**: any rule the user set that this job touches.

Suggest one of:

- **Good fit**: most of what it asks for is there or very likely there.
- **Stretch**: a real chance, but one or more hard requirements are thin or missing.
- **Not for you**: a clash with what they've said they want or need, or too far from their experience.

## Step 3: Show it, one job at a time or as a short list

Plain words. For example:

```
Support Coordinator, Northwind: good fit
  Your CV shows two years handling customer queries and the rota at Acme, which is most of this.
  Missing: they want someone who's trained new staff. Have you done that?

Data Officer, Contoso: stretch
  Matches: the reporting you did at Acme. Missing: they ask for SQL, and I don't see it yet.

Account Manager, Fabrikam: not for you, I think
  It's sales targets and commission, and you said you want to move away from sales.
```

Then ask: "Which of these do you want me to make a CV and letter for?" Let them answer in their own way ("the first two", "not Fabrikam", "all of them").

If they ask why, or push back, explain and accept their call. Their decision stands even when it differs from your suggestion.

## Step 4: Record their decision

For each job:

1. Set the job file's `triage:` to `fit`, `stretch` or `not-for-me`, following the **user's** decision (a job they want that you thought was not for them is `stretch`). Set `triage-why:` to the one or two lines you gave, adjusted for anything they told you.
2. **Jobs they want:** record `queued` through `/track`, in the user's voice, with their words in `said` (for example "yes, those two").
3. **Jobs they don't want:** no ledger line. The job file keeps its `not-for-me` and the reason.
4. **Jobs they can't decide on yet:** leave `undecided`.

## Step 5: Learn from "not for you"

If a reason for turning a job down looks like a pattern (a sector, a kind of role, a pay level, travel, a commute, a company type), offer once, in plain words: "Do you want me to remember that you don't want sales roles, so I flag them straight away next time?"

With a yes, add it, with their words in `said` and today's date in `as_of`:

- a role, sector or company to steer away from: `profile/targets.json` (`role_anchor.out`, `domains.out` or `avoid`);
- a rule about how they search: `profile/decisions.json` (`kind: "targeting"`);
- a hard limit (pay, location, hours): `profile/constraints.json`.

Likewise, if what they want becomes clear ("I'd love more jobs like the Northwind one"), offer to add it to `targets.json` (`role_anchor.in`, `domains.in`).

Run `python scripts/lint_profile.py profile` after writing and fix what it reports.

## Step 6: Next

If the recall interview hasn't covered what these jobs ask for, go to `/recall` (from `/start`, that's the next step anyway). Otherwise offer to draft the packs (`/compose-cv`).

## Rules

- Honest, short, kind. One or two lines per job.
- Never round "I don't know yet" up to a match or down to a gap.
- The user's call is final. Record it, don't argue it.
- No internal words to the user: no "atoms", "targets.json", "archetype", "ledger", "years gate".
