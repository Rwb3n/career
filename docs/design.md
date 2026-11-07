# career: the design

The design the kit is built to, agreed 7 November 2026. Where the kit and this page disagree, this page wins until it's changed.

## Who it's for
Someone with a CV that's thin, who has forgotten much of what they did, and who has never used this before. They don't know the commands and won't read docs first.

## How they get in
1. They get a link to the maintainer's public GitHub repository.
2. They use **"Use this template" → private** to make their own copy. **Never "Fork"**: a fork of a public repository is public and can't be made private. The README's first lines say so.
3. They open their copy in **Claude Code on the web** (a temporary cloud machine; only what's committed to their repository lasts).
4. **Once copied, it's theirs: a snapshot.** No updates from the maintainer's repository afterwards.

## Where things live
- One repository: the product and, in its `profile/` folder, the user's profile.
- **Before anything personal is written, the product checks the repository is private.** If it's public, or it can't tell, it stops and says how to fix it.
- The README says plainly that their data sits in their GitHub repository and passes through Anthropic.

## The first session ends with real packs
1. **Welcome.** What this is, in scenarios ("I've found jobs I like", "I need a CV for this one", "I've got an interview", "I was rejected"), not commands.
2. **Paste the jobs and the current CV.** Links or the ad's text; pasting text is always as easy as a link (many job sites can't be read without a login).
3. **Triage** each job: good fit, stretch, or not for you, with why.
4. **A recall interview aimed at those jobs.** Prompts that jog memory, role by role: a normal week, what people came to them for, something that broke and what they did, what was different when they left. Questions follow what the jobs ask for. Atoms come out of their stories; they never write atoms.
5. **The queue:** one pack per job (CV, cover letter, a short note of fit and gaps), each with a status: drafted → reviewed → sent.

## Later sessions
- The profile keeps growing: "I just remembered something" works at any time.
- New jobs join the queue the same way.

## Rules it never breaks
- **The person reviews and sends every pack.** The product never sends and never marks a pack ready by itself.
- **Claims stay defensible:** helping someone remember never becomes inventing or inflating. Each atom is in their words and confirmed by them.
- **Nothing personal is written into a public repository.**

## Output
Word (.docx) by default, since it's likely to work on the web machine. PDF only if its tools are shown to work there.

## Licence
MIT.

## From the paused build
Keep: the rules, the composing method and gates, the anti-pattern and lens checks, the tracker, the schemas, the privacy scan (fixed to match whole words with a minimum length), the fictional example, and job-ad reading that falls back to pasting. Change: the profile goes into `profile/` with the privacy check; setup becomes the recall interview in the order above; triage is its own step. Drop: the separate profile-template repository and the local profile path.

## Not known yet (find out, don't assume)
- What Claude Code on the web can install and run (Word export, PDF).
- Whether it can read job links at all, and which.
- How the product reliably tells whether its repository is private.

## Done looks like
A made-up person with a thin CV and five pasted jobs, played start to finish in Claude Code on the web from a fresh private copy, ends the first session with triaged jobs and reviewable packs. Nothing personal reaches a public repository at any point. The maintainer reads the packs and judges whether they'd be proud to send them.

## Limits
Nothing is pushed or made public without the maintainer's word. The maintainer's own profile is a later step, in their own private copy.
