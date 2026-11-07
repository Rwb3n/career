---
description: Add job ads to the user's list, from links or pasted text, one or many. Use whenever the user shares a job, a link, or says "I've found jobs I like".
argument-hint: "[link or pasted ad ...]"
---

# Add jobs

Turns each job the user gives you into `profile/jobs/<slug>.md`: the ad's text with front matter, `triage: undecided`. This step reads and files. It doesn't judge fit; `/triage` does.

`$ARGUMENTS` (optional): links, pasted text, or both. With nothing, ask: "Send me the jobs you're interested in. A link is fine, or copy and paste the text of the ad. Lots of job sites can't be read without logging in, so pasting is completely normal."

## Step 0: Privacy check

Run `python scripts/privacy_check.py`. On exit 1 or 2: stop, show its message as it is, write nothing, and don't go on until it passes.

## Step 1: Sort what you were given

Split the user's message into separate jobs. Each is either a **link** or **pasted text** (several ads pasted in one go are usually split by a title line or a gap; if you can't tell where one ends, ask).

Skip any job already in `profile/jobs/` (same `source-url`, or the same role and company) and say so in a few words.

## Step 2: Get the text of each link

Use the first of these the session has:

1. **Firecrawl** (if its tools are available): scrape with markdown output, main content only, and a short wait for script-heavy job boards.
2. **Any other web fetch tool** the session has (for example a built-in web fetch).
3. **Neither, or the fetch failed** (login wall, blocked, empty, a page of scripts, a cookie wall, a "job no longer available" page).

For several links you may hand this to the `research` agent with the list; it uses the same order.

On any failure, ask once, without fuss: "I couldn't open that one (job sites often need a login). Could you copy the ad's text and paste it here?" **Write nothing for that job until you have its text.** Never guess at what an ad says, and never fill one in from the company's other pages.

## Step 3: Write the job file

Once you have the text, write `profile/jobs/<slug>.md` with the front matter from `docs/profile.md`:

```yaml
---
role: "<job title as the ad gives it>"
company: "<employer, or '<agency> (client not named)' for an agency listing>"
salary: "<exact figure and period as stated, else 'not stated'>"
location: "<place and onsite/hybrid/remote, else 'not stated'>"
seniority: "<as stated, or inferred from years asked and marked '(inferred)'>"
source-url: "<the link, or empty when the user pasted the text>"
apply-url: "<the apply link if different, else the source-url, else empty>"
added: <today, YYYY-MM-DD>
deadline: "<closing date if stated, else empty>"
triage: undecided
triage-why: ""
---
```

Then the ad's text. Keep: what the company does, the role, responsibilities, requirements, nice-to-haves, pay and benefits, how to apply. Remove: navigation, "similar jobs", cookie notices, apply buttons, maps, footer boilerplate. Don't reword what's left.

**Slug:** role then company, lowercase and hyphenated, short (`ba-acme`, `support-coordinator-northwind`). If the name is taken, add a number. The slug never changes after this.

## Step 4: Tell the user

A short list in plain words, for example:

```
Added 3 jobs:
  Business Analyst, Acme (closes 20 Nov)
  Support Coordinator, Northwind
  Data Officer, Contoso (salary not stated)
Couldn't open 1 link: could you paste that one's text?
```

Then go straight to `/triage` for the new jobs, unless the user wants to add more first. If a paid fetch tool was used for many links, mention roughly how many calls it took.

## Rules

- Never invent or fill in ad content. If the text can't be fetched, the user pastes it, or the job isn't added yet.
- Don't judge fit here.
- Don't write a ledger line here. A job only enters the ledger when the user decides to go for it, at triage.
