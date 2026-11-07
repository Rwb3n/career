#!/usr/bin/env python3
"""Confirm this repository is private before anything personal is written.

    python scripts/privacy_check.py

Exit codes:
  0  private (confirmed), or local-only by explicit choice (see below)
  1  PUBLIC: stop; nothing personal may be written
  2  can't tell: stop; treat as public until it can be confirmed

How it decides, in order, from the `origin` remote:
  1. the GitHub CLI, if it's installed and signed in (`gh api repos/OWNER/REPO`);
  2. the GitHub API with a token from GH_TOKEN or GITHUB_TOKEN, if one is set;
  3. the GitHub API without a token: a public repository answers 200 with
     "private": false; a private one is invisible and answers 404.
A network error, a rate limit, or a remote that isn't on GitHub gives 2.

Local only: with no remote at all, it gives 2, unless CAREER_LOCAL_ONLY=1 is
set. Then it gives 0 for as long as the repository has no remote.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FIX_PUBLIC = """This repository is PUBLIC, so nothing personal can be written to it.

To fix it:
  - If you made it with "Use this template": on GitHub open the repository,
    Settings > General > Danger Zone > Change visibility > Private.
  - If you made it with "Fork": a fork of a public repository can't be made
    private. Make a new copy with "Use this template" and choose Private,
    then delete the fork.
Then run this check again."""

FIX_UNKNOWN = """Can't confirm this repository is private, so nothing personal will be written yet.

{why}

Check on GitHub that the repository shows a "Private" label next to its
name. If it does and this check still can't tell, see docs/privacy.md."""


def git(*args):
    r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def owner_repo(url: str):
    """Return (owner, repo) for a GitHub remote, or None.

    Handles https://github.com/o/r(.git), git@github.com:o/r(.git),
    ssh://git@github.com/o/r, and proxied remotes whose path ends /git/o/r
    (as used by hosted sandboxes).
    """
    m = re.match(r"^(?:https?://(?:[^@/]+@)?github\.com/|git@github\.com:|ssh://git@github\.com/)([^/]+)/([^/]+?)(?:\.git)?/?$", url)
    if m:
        return m.group(1), m.group(2)
    m = re.search(r"/git/([^/]+)/([^/]+?)(?:\.git)?/?$", url)
    if m:
        return m.group(1), m.group(2)
    return None


def via_gh(owner, repo):
    if not shutil.which("gh"):
        return None
    r = subprocess.run(["gh", "api", f"repos/{owner}/{repo}", "--jq", ".private"], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    out = r.stdout.strip()
    if out in ("true", "false"):
        return out == "true", "the GitHub CLI"
    return None


def via_api(owner, repo, token=None, tries=3):
    """Ask the GitHub API; retry network errors, which can be intermittent."""
    result = ("unknown", "not tried")
    for _ in range(tries):
        result = _via_api_once(owner, repo, token)
        if result[0] != "unknown" or not result[1].startswith("couldn't reach"):
            return result
    return result


def _via_api_once(owner, repo, token=None):
    req = urllib.request.Request(f"https://api.github.com/repos/{owner}/{repo}",
                                 headers={"Accept": "application/vnd.github+json", "User-Agent": "career-privacy-check"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if isinstance(data.get("private"), bool):
                return data["private"], "the GitHub API" + (" (signed in)" if token else "")
            return "unknown", "the GitHub API gave no visibility field"
    except urllib.error.HTTPError as e:
        if e.code == 404 and not token:
            return True, "the GitHub API (not visible publicly)"
        return "unknown", f"the GitHub API answered {e.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return "unknown", f"couldn't reach the GitHub API ({e})"


def main():
    remotes = git("remote").split()
    if not remotes:
        if os.environ.get("CAREER_LOCAL_ONLY") == "1":
            print("Local only: no remote, and CAREER_LOCAL_ONLY=1. Nothing can be pushed until a remote is added; add one and this check runs again.")
            return 0
        print(FIX_UNKNOWN.format(why="This copy has no GitHub remote, so there's nothing to check. If you're using it only on your own computer, set CAREER_LOCAL_ONLY=1."))
        return 2

    url = git("remote", "get-url", "origin") or git("remote", "get-url", remotes[0])
    parsed = owner_repo(url)
    if not parsed:
        print(FIX_UNKNOWN.format(why="The remote isn't a GitHub address this check understands."))
        return 2
    owner, repo = parsed

    result = via_gh(owner, repo)
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if result is None and token:
        r = via_api(owner, repo, token)
        result = r if r[0] != "unknown" else None
    if result is None:
        r = via_api(owner, repo)
        if r[0] == "unknown":
            print(FIX_UNKNOWN.format(why=f"Checked {owner}/{repo}: {r[1]}."))
            return 2
        result = r

    is_private, how = result
    if is_private:
        print(f"Private: {owner}/{repo} (checked with {how}).")
        return 0
    print(f"{owner}/{repo} is public (checked with {how}).\n")
    print(FIX_PUBLIC)
    return 1


if __name__ == "__main__":
    sys.exit(main())
