# career

> **To use it: click "Use this template", then choose Private.**
> **Never click "Fork".** A fork of a public repository is public and can't be made private, and your CV and history would be visible to anyone.

A job-hunt helper that runs in [Claude Code](https://claude.com/claude-code). You paste the jobs you like and your current CV. It helps you work out which jobs suit you, helps you remember what you've actually done (most people have done far more than their CV says), and drafts a CV and cover letter for each job. You read every one, change what you want, and send it yourself.

## How to start

1. Click **Use this template** at the top of this page, then **Create a new repository**. Give it a name and choose **Private**.
2. Open your new repository in Claude Code on the web ([claude.ai/code](https://claude.ai/code)).
3. Say hello. It takes it from there.

You don't need to know any commands. Just say what's going on: "I've found some jobs I like", "I need a CV for this one", "I've got an interview", "I was rejected", "I just remembered something".

## What happens the first time

1. **You paste the jobs** (links, or the ad's text; many job sites need a login, so pasting is normal) and **your current CV**, however thin.
2. **It sorts the jobs:** good fit, a stretch, or not for you, and says why. You decide.
3. **It asks you questions** about each job you've had, aimed at what those jobs want. A normal week. What people came to you for. Something that went wrong and what you did. It writes down your stories in your words and reads them back.
4. **It drafts a pack for each job:** a CV, a cover letter, and a short note on how well you fit and what's missing. In Word.
5. **You read, edit and send** each one, and tell it when you have.

Later, add new jobs the same way, or tell it when you remember something. Your profile keeps growing.

## What it never does

- Send anything for you, or mark a CV as ready without you saying so.
- Make things up or make them bigger than they were. Every line comes from something you said, and you confirm the wording.
- Write anything personal into a public repository. Before it saves anything, it checks your copy is private, and stops if it isn't or it can't tell.

## Your data

Everything about you is saved in the `profile/` folder of **your** repository on GitHub, and passes through Anthropic while Claude works on it. Keep the repository private. Your copy is yours: it doesn't change when this one does.

If you'd rather run it on your own computer with no GitHub copy at all, see [docs/privacy.md](docs/privacy.md).

## What's in here

```
profile/            your data (blank until you start)
.claude/commands/   what Claude follows: start, add-jobs, triage, recall, compose-cv,
                    compose-cover-letter, scan, export, track, queue
rules/              the writing rules every CV and letter is checked against
docs/               how it works: design, profile format, method, stages, privacy
templates/          Word (and optional PDF) templates
scripts/            privacy check, profile check, personal-data scan
examples/           made-up people, for testing
```

## Licence

MIT.
