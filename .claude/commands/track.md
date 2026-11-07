---
description: Record where a job stands (queued, drafted, reviewed, sent, an interview, a rejection...). Use whenever the user says they've read a pack, sent it, heard back, or given up on a job.
argument-hint: "[job] [stage] [what happened]"
---

# Track

Adds one line to `profile/ledger.jsonl` and keeps the pack's `PACK.md` status in step with it. Stages and their meanings are in `docs/stages.md`.

The user rarely types this. They say "I've sent the Acme one", "I read it, it's fine", "they turned me down", "I've got an interview on Thursday". Recognise those and run this.

## Step 0: Privacy check

Run `python3 scripts/privacy_check.py`. On exit 1 or 2: stop, show its message as it is, write nothing, and don't go on until it passes.

## Step 1: What happened

From the user's words, or by asking one short question at a time:

- **Which job.** Match what they said against `profile/jobs/*.md` (role and company) and the slugs in the ledger. If two could match, ask which. Never say "slug" to the user: call it by role and company.
- **What happened**, mapped to a stage in `docs/stages.md`.
- **When** (`as_of`; today unless they say otherwise).
- **Who says so:**
  - The user told you: `voice: "user"`, and `said` is their words, as typed.
  - A document says so (a rejection email, an interview invite they pasted): `voice: "source"`, and `source` is the file path or "email from <sender's role>, <date>". No personal names or email addresses in the line.
  - The kit itself: `voice: "assistant"`. **Only allowed for `drafted`.**

If the job has no ledger line yet, add `role` and `company` to this line.

Check the stage is in the list. If it moves backwards (for example `interview` after `declined`), ask before writing.

## Step 2: The stages only the user can move

**`reviewed` and `sent` are always in the user's voice, with their words in `said`.** Never write either because a pack looks finished, because the user went quiet, or because another procedure asked you to. If the user hasn't said it, ask: "Have you read through it and you're happy with it?" or "Have you sent it?"

### `reviewed`

The user has read the pack, edited what they wanted, and says it's ready. Before writing:

- Search the CV and letter for `[USER:`. If any are left, tell them which, plainly ("There's still a gap to fill in the letter: why this company"), and ask whether to record it as reviewed anyway. Their call.
- If they edited the `.md` files, offer to rebuild the Word files (`/export`) so they match.

### `sent`

The user has sent it themselves. The kit never sends anything.

1. Ask which files they sent. Default: the `.docx` files in `profile/packs/<slug>/`, plus any `.pdf` there. Ask if that's right.
2. Hash each one: `python3 -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" <file>`.
3. Add `files: {"packs/<slug>/CV-<slug>.docx": "<hash>", ...}`. Keys are relative to `profile/`. From now on those files are a record: the lint fails if they change, and nothing may regenerate them.

### `queued`

Written at triage, in the user's voice ("yes, go for that one").

### `drafted`

Written by the compose procedures once a pack exists, `voice: "assistant"`, `said` omitted, `note` naming what was drafted ("CV and letter").

## Step 3: Write

Append one line of compact JSON to `profile/ledger.jsonl`, with `ts` set to the current UTC time (`YYYY-MM-DDTHH:MM:SSZ`):

```json
{"ts":"2026-11-07T10:00:00Z","slug":"ba-acme","stage":"reviewed","as_of":"2026-11-07","voice":"user","said":"happy with that","note":""}
```

Never edit or remove an existing line. A correction is a new line whose `note` says what it corrects.

## Step 4: Mirror the pack status

If `profile/packs/<slug>/PACK.md` exists and the new stage is `drafted`, `reviewed` or `sent`, set its front matter `status:` to that stage. This is the only change ever made to a sent pack's files. For stages after `sent` (screen, interview, declined...), `PACK.md` stays at `sent`; the ledger holds the rest.

Then run `python3 scripts/lint_profile.py profile` and fix anything it reports in the line you just wrote.

## Step 5: Say what's next, in plain words

- `reviewed`: "Send it when you're ready, then tell me it's gone."
- `sent`: "Good luck. If you've heard nothing in two weeks, I'll ask you about it."
- `killed`: if the reason looks like a pattern (a kind of company, a kind of role, a deal-breaker), offer to remember it so similar jobs get flagged earlier. With a yes, add it to `profile/targets.json` (`avoid`, `role_anchor.out`, `domains.out`) or `profile/decisions.json` (their words in `said`).
- `declined` after an interview, or `interview`: offer to note what they were asked, while it's fresh, in `profile/packs/<slug>/NOTES.md`. That file is new, so it doesn't touch the sent record.
- Anything that sounds like a new memory ("they asked about the time I..."): offer to add it to their history (`/recall`).

Keep it to a line or two. Don't name the ledger or the stage list to the user.
