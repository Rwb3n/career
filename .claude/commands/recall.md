---
description: The recall interview. Helps the user remember what they've done, aimed at the jobs they want, and turns their stories into CV lines they confirm. Also use any time the user says "I just remembered something" or hands over a new document (a review, a reference, an old CV).
argument-hint: "[resume | remembered | <file>]"
---

# Recall

Most people have done far more than their CV says, and have forgotten most of it. This is a conversation that helps them remember, **aimed at the jobs they want**, and turns what they say into CV lines they agree with.

It writes `profile/stories.md` (their stories, in their words), `profile/atoms.json` (CV lines drafted from those stories, kept only when they say yes), and, lightly and only as the packs need them, `profile/profile.json` identity, `profile/constraints.json` and `profile/voice.md`.

**The one rule: helping someone remember never becomes inventing.** No number they didn't give. No outcome they didn't describe. If they're unsure, the line says less.

## Three ways in

- **The interview** (from `/start`, or "help me with my CV", "let's go through my experience"): Steps 0 to 8.
- **"I just remembered something"**: Step 0, then capture that one story (Step 4), turn it into lines (Step 5), done. Ask which job or role it belongs to if it isn't clear.
- **"Here's a document"** (a performance review, a reference, a project write-up, another CV, a certificate): Step 0, keep it as given in `profile/sources/<short-name>.<ext>`, read it, and for each thing in it worth a line, ask about it as a story (Step 4): the document is a prompt, not a claim. A certificate or course goes straight to Step 7 with a date check. Then Step 5.

`resume` (or an existing `profile/.recall-state.json` without `done`) picks up where the last session stopped.

## Talking to the user

- **One question at a time.** Short, warm, plain. Wait for the answer.
- Never say "atom", "recipe", "ledger", "claim domain", "tag", "archetype" or "evidence". Say "your story", "a line for your CV", "your history".
- Let them ramble. Rambling is where the good stuff is. Write down what they say, not what you'd have said.
- If they say "I don't really remember" or "it was nothing", say that's normal, and try a different prompt. Don't push the same one.
- Small things count. "I was the one who knew how the printer worked" can become "Handled first-line fixes for the office's equipment".
- Every few stories, say where you are: "That's two good ones from Acme. One more from there, then Northwind?"

## Step 0: Privacy check

Run `python scripts/privacy_check.py`. On exit 1 or 2: stop, show its message as it is, write nothing, and don't go on until it passes.

## Step 1: Load and set up

Read `profile/sources/` (the CV and anything else), `profile/stories.md`, `profile/atoms.json`, `profile/profile.json`, `profile/constraints.json`, `profile/targets.json`, `profile/voice.md`, and `profile/.recall-state.json` if it exists.

Find the jobs this interview is aimed at: every slug whose latest ledger line is `queued` (or later stages without a pack), with its file in `profile/jobs/`. If there are none, aim at what the user says they want, or at their most recent role.

Create or update `profile/.recall-state.json`:

```json
{
  "started": "YYYY-MM-DD",
  "aimed_at": ["ba-acme", "support-coordinator-northwind"],
  "asks": [{ "ask": "handling complaints", "jobs": ["support-coordinator-northwind"], "covered_by": [] }],
  "roles": { "role-acme": "done", "role-northwind": "in-progress" },
  "basics": { "roles_from_cv": false, "identity": false, "constraints": false, "voice": false },
  "next": "role-northwind: what people came to you for",
  "done": null
}
```

If the state file has `done` set but there are queued jobs not in `aimed_at` (new jobs from a later session), reopen it: add them to `aimed_at`, append their new asks with empty `covered_by`, clear `done`, and aim the interview at those asks only.

Update it after every confirmed story and every finished step, so a session that ends halfway loses nothing. Also add a one-line note at the end of `profile/stories.md` under `## Where we got to` (overwrite that section each time).

## Step 2: What the jobs ask for

From the queued job files, list what they ask for: skills, situations ("dealing with difficult customers", "working to deadlines"), responsibilities ("managing a budget", "training new staff"), tools. Merge the same thing asked by several jobs. Put the list in `asks` in the state file.

Tell the user briefly, in plain words: "Between them, these jobs want someone who's handled complaints, kept records accurate, worked with spreadsheets, and trained people. Let's find where you've done those, even if it wasn't in your job title."

## Step 3: Roles from the CV

Read the CV in `sources/` and draft `atoms.json` `roles` (newest first: company, a one-line description of the company, title, period `YYYY-MM to YYYY-MM|present`, `is_current`), `education` and `certifications`.

Confirm with the user in one short pass, not field by field: "From your CV: Acme, Customer Adviser, March 2021 to now; Northwind, Sales Assistant, 2018 to 2021. Are those dates right? Anything missing, like a job you left off?" Fix what they correct. Dates are confirmed, not guessed: if they don't know a month, use the year only and say so.

Ask, once: "Any other title you could fairly use for the Acme job? Sometimes the official title undersells it." Record answers in `title_variants`. Only titles they could defend.

Set `basics.roles_from_cv: true`.

## Step 4: The interview, role by role

Newest role first. For each role, work through prompts like these, **one at a time**, choosing the ones most likely to hit what the jobs ask for:

**Memory-jogging prompts**

- "Walk me through a normal week at Acme. What did Monday look like?"
- "What did people come to you for? What were you the go-to person for?"
- "Tell me about something that broke, or went wrong. What did you do?"
- "What was different when you left, compared with when you started?"
- "Was there anything you set up, fixed or tidied that people kept using?"
- "Did anyone ever thank you for something, or say 'I don't know what we'd do without you'?"
- "Who did you train, help or show the ropes to?"

**Prompts aimed at what the jobs ask for** (from `asks`), for example:

- "The jobs ask about handling complaints. Was there a time at Acme when a customer was really unhappy? What happened?"
- "Two of these want someone good with spreadsheets. Did you ever keep a list, a tracker or a report for the team?"
- "Northwind wants someone who's trained new staff. Did you ever show a new starter how things worked?"

When a story comes, follow up, one question at a time, only as far as it goes:

1. **Who was it for?** (customers, a manager, the team, another department)
2. **What changed for them?** (less waiting, fewer mistakes, they knew what to do, they stopped calling back)
3. **What did it do for the organisation?** (money, time, complaints down, a customer kept)
4. **How could someone check?** (a person who'd confirm it, a document, a system, or "nothing to point to", which is fine)

Don't lead. Ask "what changed?", not "did it cut complaints by half?". If they give a number, ask where it comes from: "Is that a figure you saw, or your best guess?" A guess isn't written as a figure.

**Read it back and get a yes.** "So: at Acme, when the booking system went down for a day, you kept a paper list of every call and rang each customer back once it was fixed, and your manager used your list to sort out refunds. Have I got that right?" Fix anything they correct.

Then write it to `profile/stories.md`, in the format in `docs/profile.md`:

```markdown
## st-03 · role-acme · 2022

**Prompt:** Something that broke, and what you did
**Story:** what they said, lightly tidied, nothing added
**Who it was for:** customers who'd booked that week; the manager handling refunds
**What changed for them:** customers got a call back instead of having to chase
**What it did for the organisation:** refunds were sorted from one list
**How someone could check:** the team manager at the time (or "nothing to point to")
**Confirmed:** 2026-11-07
```

Story ids run `st-01`, `st-02`... in order. A story is only used once `Confirmed` is set. Update `asks[].covered_by` with the story id where it covers an ask, and update the state file.

Move on from a role when the asks it could cover are covered, or after three or four stories, or when the user is running dry. If a role ends with no stories, tell them plainly: "That one will show on your CV as the job title and dates only. That's fine." Stop for a breather if they're tired; the state file holds the place.

## Step 5: From stories to CV lines

From each confirmed story, draft one or more CV lines. Show them as plain CV lines, a few at a time:

```
From the booking system story, I'd put:
  1. Kept customers informed during a system outage by logging every affected booking and calling each one back once it was fixed
Does that sound like you? Change any word you like.
```

They say yes, change it, or drop it. **Only lines they say yes to are kept**, with the wording they agreed.

Drafting rules:

- **One line per fact.** Split compound stories.
- **Lead with what changed for the people, then what it did for the organisation, then the tools or method.** If the story only says what they did, the line says only what they did.
- **Only what's in the story.** No number they didn't give, no outcome they didn't say, no "significantly", "successfully", "improved" unless they said it changed. If they're unsure, the line says less.
- **No output counts.** "Wrote 40 procedures" is a count of what they produced, not a change; leave it out unless something changed because of it.
- **No names from their never-name list** (`constraints.json`). Describe confidential things neutrally ("a client's loyalty scheme").
- **Check every line** against `rules/submission-rules.json` and `profile/rules-local.json` before showing it, above all: would it survive a second question in an interview; does it have a clear subject; is it a vanity count. A line that enters the profile here can end up in every future CV.

Write each confirmed line to `atoms.json` `bullets`:

- `id`: `b-<role-shortcode>-<descriptor>` (for example `b-acme-outage-callbacks`). Other prefixes: `sk-` skills, `proj-` projects, `cert-` certifications, `edu-` education, `pf-` summary sentences.
- `role_id`, `text` (their agreed wording), `evidence: ["st-03"]`, `confirmed: "<today>"`.
- `tags`: from what the jobs ask for and the story; reuse existing tags before adding new ones.
- `tone`: usually `plain`; see `docs/method.md`.
- `strength`: `high` only for a change the user stated and someone could check; `medium` for a clear achievement without that; `low` for context or a small part.
- `claim_domain`: one of `targets.json` `claim_domains`. If there are none yet, set two to four from the jobs and the CV (for example "customer service", "administration", "data and reporting") and write them to `targets.json`. This is internal; don't ask the user about it.

Lines from the old CV that the user confirms as still true, with no story behind them, may be kept with `evidence: ["sources/<file>"]` and a `confirmed` date. Say these are weaker than lines with a story.

Also, as they come up, and confirmed the same way:

- **Skills**: named tools and techniques only, each with a one-line detail of how they used it. No "team player", "good communicator".
- **Summary sentences** (`fragments`): one `anchor` (who they are at work, in a sentence), and `claim` or `value` sentences built only from confirmed lines. Draft them near the end and get a yes.

**Existing lines are not changed** unless the user asks. Then change the text, set `amended` to today and `amend_reason` to the reason in plain words, and keep both.

After writing, run `python scripts/lint_profile.py profile` and fix what it reports in what you wrote.

## Step 6: The basics the packs need

Only what the packs need, asked lightly, near the end (or earlier if the user brings it up):

- **For the CV header** (`profile.json` `identity`): name, a town or area (as they want it shown), email, phone, LinkedIn if they have one, languages. Read what's on the old CV first and confirm it: "Your CV has your email as ... Still right?" Set `basics.identity: true`.
- **Constraints** (`constraints.json`, their words in `said`, today in `as_of`): notice period or when they could start; the lowest salary they'd accept (offer "skip" freely); where they can work and how far they'd travel; anything about hours or days. And: "Is there anything that must never appear on your CV, like a client's name or an internal project your contract says you can't mention?" Those go in one `never-name` item with `names: [...]`. Set `basics.constraints: true`.
- **Spelling and paper** (`settings`): infer from where they live and the jobs (UK: `en-GB`, A4). Only ask if unclear.

## Step 7: Education and certifications

Confirm what came from the CV (Step 3) and anything new: name, where, when, status (`held`, `in-progress`, `expired`). Credential ids are stored but never printed unless they ask.

## Step 8: Voice, a little

Enough to make the packs sound like them, no more:

1. Show two versions of one confirmed line: one plain, one more polished. "Which sounds more like you? Anything you'd never say?" Record the reaction in `voice.md` under "Keep" or "Cut", with the date.
2. If they've written something themselves (a message, an email, a bit of their old cover letter), keep a short sample under "Samples".
3. Their own description, if they offer one ("I'm quite blunt", "I don't like bragging"), under "Standard".

Set `basics.voice: true`. Say once: the packs will get closer to how they talk each time they cut a line they don't like.

## Finish

When every queued job's asks have been tried and the basics are in:

1. Tell them in plain words what you've got: "We've got 9 lines for your CV now, from 6 stories, across your three jobs. The jobs ask for training experience, and we didn't find any; the letter will handle that honestly."
2. Set `done` in `.recall-state.json` to today, and update `## Where we got to` in `stories.md`.
3. From `/start`, go on to the packs. Otherwise offer to draft or redraft packs for the queued jobs (`/compose-cv`).

A later "I just remembered something" adds to the profile at any time; packs already drafted (not sent) can be redrafted to use it.

## Rules

- One question at a time. Their words, not yours.
- Never invent or inflate. If they didn't say it, it's not in the line.
- A story is used only once they've confirmed the read-back. A line is used only once they've said yes to its wording.
- Write as you go. A session can end at any moment.
- No internal words to the user.
