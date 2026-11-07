# Privacy

Your CV, your history, your salary floor and your notice period are personal. This kit keeps them in the `profile/` folder of your own copy of the repository, so that copy must be **private**.

## Making your copy

Use **"Use this template"** and choose **Private**. Don't use **Fork**: GitHub makes a fork of a public repository public, and it can't be made private afterwards.

## The privacy check

Before anything is written to `profile/`, the kit runs:

```
python scripts/privacy_check.py
```

It reads your repository's GitHub address and asks GitHub whether it's private:

1. with the GitHub CLI, if it's installed and signed in;
2. with a token in `GH_TOKEN` or `GITHUB_TOKEN`, if one is set;
3. without signing in: a public repository answers, a private one is invisible to the public (GitHub answers "not found").

| Result | Meaning | What happens |
|---|---|---|
| exit 0 | private, confirmed | the kit carries on |
| exit 1 | public | the kit stops and says how to make it private |
| exit 2 | can't tell (no network, no GitHub address, an error) | the kit stops; it treats "can't tell" as public |

**Known limit:** the third way can't tell "private" from "doesn't exist". It relies on the address being your repository's real address, which it is when you opened the repository from GitHub.

## Using it on your own computer only

If you clone your private copy to your own computer, the check works the same way. If you want no GitHub copy at all, delete the remote (`git remote remove origin`) and set `CAREER_LOCAL_ONLY=1`. The check then passes for as long as there's no remote. Add a remote later and it checks again.

## Where your data goes

- **GitHub**, in your private repository: everything in `profile/` that's committed.
- **Anthropic**: whatever Claude reads or writes while you work, as with any Claude Code session.
- Nowhere else. The kit doesn't send applications, emails or data to anyone.

## For maintainers: before publishing the kit

```
python scripts/scan_personal.py --publish --profile <a real profile folder> [--denylist <file>]
```

- It builds a list of identifying terms from the profile (name, email, phone, links, location, employers, institutions, credential ids, never-name names, salary figures). Add your own with `--denylist`; keep that file outside the repository, because it's personal data too.
- It searches every file, every line ever added in any commit on any branch, and every commit's author and committer email, for those terms (whole words, 4 characters or more) and for email addresses, phone numbers, UK postcodes, National Insurance numbers and long digit runs.
- `--publish` also fails if `profile/` isn't blank.
- Lines marked `scan:fixture` are skipped. They're for deliberately fake data in tests only.

Any hit fails it. A file deleted in a later commit still fails it, because it's still in history. If history has a hit, start a new repository rather than rewriting the old one. Commit with a noreply email address (`<id>+<user>@users.noreply.github.com`).
