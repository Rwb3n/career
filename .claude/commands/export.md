---
description: Rebuild a pack's Word files (and PDFs, if switched on and possible) from its Markdown, then check them. Use after the user edits a CV or letter, or asks for the files.
argument-hint: "<job> [cv|cl] | all"
---

# Export

Turn a pack's CV and/or letter from Markdown into Word (`.docx`), and into PDF only when that's switched on and works here. Then check the output.

`$ARGUMENTS` is one of:

- `<job>`: the CV and letter in `profile/packs/<slug>/` (the job by slug, or by role and company in the user's words);
- `<job> cv` or `<job> cl`: one of them;
- `all`: every pack not yet sent.

## Step 0: Privacy check

Run `python scripts/privacy_check.py`. On exit 1 or 2: stop, show its message as it is, write nothing, and don't go on until it passes.

## Step 1: Resolve the files

In `profile/packs/<slug>/`: `CV-<slug>.md` and `CL-<slug>.md`.

**Sent packs are records.** If `profile/ledger.jsonl` shows the slug at `sent` or later, do not regenerate any of its files: the ledger holds a hash of what was sent. Skip it and tell the user, plainly: "The Acme pack has already been sent, so I've left its files exactly as they were."

If nothing matches, say so and list the packs there are, by role and company.

Read `profile/profile.json` for `settings.output`, `settings.paper`, `settings.cv_max_pages`, `settings.cl_max_pages`, and `profile/constraints.json` for never-names.

## Step 2: Word (always)

- `python templates/docx/generate_docx.py "profile/packs/<slug>/CV-<slug>.md" "profile/packs/<slug>/CV-<slug>.docx"`
- `python templates/docx/generate_docx.py "profile/packs/<slug>/CL-<slug>.md" "profile/packs/<slug>/CL-<slug>.docx"`

If `python-docx` is missing, run `pip install -r requirements.txt` once and retry. If one export fails, report it and carry on with the rest.

## Step 3: PDF (only if switched on and possible)

Only when `settings.output` is `docx+pdf`. First check the tools: `pandoc --version` must succeed, and `templates/pdf/export.py` must find a Chrome, Edge or Chromium browser. If either is missing, say in one line that PDF isn't available on this machine and the Word files are ready; don't try to install a browser.

If both are there:

- CV: `python templates/pdf/export.py "profile/packs/<slug>/CV-<slug>.md" cv --paper <settings.paper>`
- Letter: `python templates/pdf/export.py "profile/packs/<slug>/CL-<slug>.md" cl --paper <settings.paper>`

The PDF goes next to its source, same name, `.pdf`.

## Step 4: Check the output

For each file produced, extract its text and check:

1. **Pages:** CV within `settings.cv_max_pages`, letter within `settings.cl_max_pages` (for Word, estimate from the text length and say it's an estimate). Over the limit is flagged.
2. **Paper size** (PDF): matches `settings.paper` (A4 is 210 x 297 mm, Letter is 8.5 x 11 in).
3. **Placeholders:** any `[USER:` left. Expected while drafting; must be zero before sending.
4. **Never-names:** none present.
5. **Characters:** no replacement characters (U+FFFD) or garbled currency signs, quotes or dashes.
6. **Links:** the URLs from `identity.links` appear intact.

Record the results in `recipe.json` `scan.output_checks`.

## Step 5: Tell the user

Plain and short, for example:

```
Rebuilt the Northwind pack:
  CV-support-coordinator-northwind.docx: about one page, all clear
  CL-support-coordinator-northwind.docx: one page, one gap still to fill (why Northwind)
```

## Rules

1. **Never modify the source Markdown.** Export only reads it.
2. **Output sits beside the source**, same name, new extension.
3. **Never regenerate a sent pack's files.**
4. **Exporting is not a sign-off.** It doesn't move a pack to reviewed.
