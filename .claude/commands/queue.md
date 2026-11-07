---
description: Show where every job and pack stands, what's waiting on the user, and what's gone quiet. Use when the user asks "where am I", "what's next", or opens a later session.
argument-hint: "[all]"
---

# Queue

Reads `profile/ledger.jsonl`, `profile/jobs/*.md` and `profile/packs/*/PACK.md`. Writes nothing. Any change the user agrees to goes through `/track`.

If `profile/` has no ledger or no jobs yet, say there's nothing in the queue and offer to add some jobs (`/add-jobs`).

## Step 1: Fold

For each slug, its current stage is its latest ledger line. Read the matching job file for role, company, apply link and deadline. Group:

1. **Ready for you to read** (`drafted`): days since drafted.
2. **Read, not sent yet** (`reviewed`): days since reviewed.
3. **Sent** (`sent`): date sent.
4. **Heard back** (`screen`, `interview`, `offer`): stage and date.
5. **Waiting for a pack** (`queued` with no `packs/<slug>/PACK.md`).
6. **Closed** (`accepted`, `declined`, `silent`, `killed`, `lapsed`, `withdrawn`): counts only, unless the argument is `all`.

Also list job files with `triage: undecided`: jobs the user hasn't decided on yet.

If a `PACK.md` status disagrees with the ledger, the ledger wins; say so and offer to fix the pack's status through `/track`.

## Step 2: Flags

- **Silent at 14 days.** A pack sent more than 14 days ago with no later line: ask "Have you heard anything from <company>?" If nothing, offer to record it as silent (through `/track`, in their words).
- **Drafted and not sent is piling up.** If there are more packs drafted or reviewed than sent, say so plainly and kindly: "You've got <n> packs ready and <m> sent. The next step that moves things is sending one."
- **Old drafts.** Drafted more than 7 days ago and not reviewed: ask whether they still want it, or whether the ad has closed (offer to record it as lapsed or not going ahead).
- **Deadlines** within 7 days, from the job files.

## Step 3: Show it

Plain, short, no internal words. For example:

```
Ready for you to read
  Business Analyst, Acme (2 days)
  Support Coordinator, Northwind (today)

Sent
  Data Officer, Contoso (sent 3 Nov)

Not decided yet
  Operations Assistant, Fabrikam
```

Then one line: what to do next. Pick the single most useful thing (a deadline first, then a pack ready to read, then sending a reviewed one, then deciding on undecided jobs).

## Step 4: Funnel (argument `all`)

Counts from first sight to outcome: queued, drafted, reviewed, sent, screen, interview, offer. Then the most common reason in `killed` notes, and the furthest stage reached. Don't draw conclusions from fewer than ten sent.
