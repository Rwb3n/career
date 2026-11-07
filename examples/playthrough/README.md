# Playthrough: a first session, start to finish

This is the acceptance test for the kit. A tester plays **Alex Morgan**, a made-up person with a thin CV, through a whole first session in Claude Code on the web, from a fresh private copy of the repository.

## Setup

1. On GitHub: "Use this template", **Private**. Never Fork.
2. Open the copy in Claude Code on the web.
3. Say "hi" and nothing else. The kit should start.

## Play

- Give the kit `cv.md` (paste it).
- Give it the five jobs in `jobs/`. Paste 1, 2 and 4 as text; give 3 and 5 as their links if they're real postings you've chosen to stand in, or paste them too.
- Answer as Alex, using the persona sheet. It is kept OUTSIDE this repository on purpose, so the kit cannot read it; the tester gets it separately. Alex only volunteers what's on the CV. The rest comes out only if a question jogs it. Don't hand over memories the kit didn't ask for.

## Pass

The session passes when all of these hold:

1. The privacy check ran before anything was written to `profile/`, and passed.
2. Every job was triaged (fit, stretch, not for you) with a reason, and Alex decided each.
3. The recall interview asked about the things the queued jobs ask for, and at least four of the six hidden memories in the persona sheet became confirmed stories.
4. No claim in any pack goes beyond what Alex said: no invented number, outcome or responsibility. Check each line against `profile/stories.md` and `cv.md`.
5. There's one pack per queued job (CV and letter in Word, and a fit note), each `drafted`, none `reviewed` or `sent`.
6. Alex was never shown the words atom, recipe, ledger or slug.
7. `python3 scripts/lint_profile.py` passes at the end.
8. If the session is closed partway and reopened, the kit picks up where it stopped.

Then the operator reads the packs and judges whether Alex would be proud to send them.
