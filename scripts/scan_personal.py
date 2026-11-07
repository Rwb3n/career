#!/usr/bin/env python3
"""Scan a repository for personal data before it is shared.

    python scripts/scan_personal.py [--repo DIR] [--profile DIR] [--denylist FILE]
                                    [--allow FILE] [--no-history]

It looks in every tracked and untracked file in the working tree, and (unless
--no-history) in every line ever added in any commit on any branch, plus the
author and committer email of every commit.

What it looks for:
  1. Terms from a denylist. Build it from a profile with --profile (name and
     its parts, email, phone, links, location, employers, institutions,
     credential ids, never-name names, salary figures) and/or pass a plain
     text file with --denylist (one term per line, # comments). Keep that file
     OUTSIDE the repository: it is personal data itself.
  2. Generic patterns: email addresses, phone numbers, UK postcodes, UK
     National Insurance numbers, long digit runs.

Denylist terms match whole words only, and terms shorter than 4 characters
are ignored (they match inside ordinary words). Allowed terms (the fictional
example, placeholder emails) are read from scripts/scan-allow.txt and from
--allow. A line containing the marker scan:fixture is skipped: use it only
for deliberately fake data in tests.

--publish also checks that profile/ is blank, as the kit must ship.

Any hit exits 1.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_ALLOW = HERE / "scan-allow.txt"

GENERIC = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "phone": re.compile(r"(?<![\w.])(?:\+44\s?7\d{3}|07\d{3})\s?\d{3}\s?\d{3}(?!\d)|(?<![\w.])\+\d{1,3}[\s-]?\(?\d{2,4}\)?[\s-]?\d{3,4}[\s-]?\d{3,4}(?!\d)"),
    "uk-postcode": re.compile(r"\b(?:[A-PR-UWYZ][A-HK-Y]?\d[A-Z\d]?)\s?\d[ABD-HJLNP-UW-Z]{2}\b"),
    "ni-number": re.compile(r"\b[A-Z]{2}\s?\d{2}\s?\d{2}\s?\d{2}\s?[A-D]\b"),
    "long-digits": re.compile(r"(?<![\w.#-])\d{9,}(?![\w.-])"),
}

MIN_TERM = 4
FIXTURE_MARK = "scan:" + "fixture"

TEXT_SUFFIXES = {".md", ".json", ".jsonl", ".py", ".txt", ".css", ".yml", ".yaml", ".toml", ".cfg", ".ini", ".sh", ".ps1", ".js", ".ts", ".html", ".csv", ""}


def read_terms(path: Path):
    if not path or not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.append(line)
    return out


def terms_from_profile(profile: Path):
    """Collect identifying strings from a profile."""
    terms = set()

    def add(s):
        if isinstance(s, str):
            s = s.strip()
            if len(s) >= 3:
                terms.add(s)

    def load(name):
        p = profile / name
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return None
        return None

    prof = load("profile.json") or {}
    ident = prof.get("identity") or {}
    name = ident.get("name", "")
    add(name)
    for part in name.split():
        if len(part) >= 4:
            add(part)
    for k in ("email", "phone", "location"):
        add(ident.get(k))
    for link in ident.get("links") or []:
        url = (link or {}).get("url", "")
        add(url)
        handle = url.rstrip("/").rsplit("/", 1)[-1]
        if len(handle) >= 4:
            add(handle)

    atoms = load("atoms.json") or {}
    for r in atoms.get("roles") or []:
        add(r.get("company"))
    for e in atoms.get("education") or []:
        add(e.get("institution"))
    for c in atoms.get("certifications") or []:
        add(c.get("credential_id"))

    for fname in ("constraints.json", "decisions.json"):
        data = load(fname) or {}
        for item in data.get("items") or []:
            for n in item.get("names") or []:
                add(n)
            if item.get("kind") in ("salary-floor", "salary-band"):
                for num in re.findall(r"\d[\d,.]*\d", item.get("statement", "")):
                    add(num)
    return sorted(terms, key=len, reverse=True)


def allowed(hit: str, allow):
    """Exact match, or an address/host at an allowed domain."""
    h = hit.lower()
    for a in allow:
        a = a.lower()
        if h == a or h.endswith("@" + a) or h.endswith("." + a):
            return True
    return False


def scan_text(text, where, deny_re, allow, hits):
    for n, line in enumerate(text.splitlines(), 1):
        if FIXTURE_MARK in line:
            continue
        if deny_re:
            for m in deny_re.finditer(line):
                if not allowed(m.group(0), allow):
                    hits.append((f"{where}:{n}", "denylist", m.group(0)))
        for kind, rx in GENERIC.items():
            for m in rx.finditer(line):
                if not allowed(m.group(0), allow):
                    hits.append((f"{where}:{n}", kind, m.group(0)))


def profile_not_blank(profile: Path):
    """Reasons profile/ isn't the blank profile the kit ships with."""
    out = []
    if not profile.is_dir():
        return ["profile/ is missing"]

    def load(name):
        try:
            return json.loads((profile / name).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            out.append(f"{name} missing or unreadable")
            return {}

    ident = (load("profile.json").get("identity") or {})
    for k, v in ident.items():
        if v not in ("", [], None):
            out.append(f"profile.json identity.{k} is filled in")
    for k, v in load("atoms.json").items():
        if v not in ([], {}, "", None):
            out.append(f"atoms.json {k} has entries")
    for name in ("constraints.json", "decisions.json"):
        if load(name).get("items"):
            out.append(f"{name} has items")
    if (load("rules-local.json").get("rules")):
        out.append("rules-local.json has rules")
    ledger = profile / "ledger.jsonl"
    if ledger.exists() and ledger.read_text(encoding="utf-8").strip():
        out.append("ledger.jsonl has lines")
    stories = profile / "stories.md"
    if stories.exists() and re.search(r"^##\s", stories.read_text(encoding="utf-8"), re.MULTILINE):
        out.append("stories.md has stories")
    for d in ("jobs", "packs", "sources"):
        extra = [p.name for p in (profile / d).glob("*") if p.name != ".gitkeep"] if (profile / d).is_dir() else []
        if extra:
            out.append(f"{d}/ holds {len(extra)} item(s)")
    return out


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout


def working_tree_files(repo: Path):
    listed = git(repo, "ls-files", "--cached", "--others", "--exclude-standard")
    if listed.strip():
        return [repo / p for p in listed.splitlines()]
    return [p for p in repo.rglob("*") if p.is_file() and ".git" not in p.parts]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=str(HERE.parent))
    ap.add_argument("--profile", help="build the denylist from this profile folder")
    ap.add_argument("--denylist", help="extra terms, one per line (keep this file outside the repo)")
    ap.add_argument("--allow", help="extra allowed terms, one per line")
    ap.add_argument("--no-history", action="store_true", help="scan the working tree only")
    ap.add_argument("--publish", action="store_true", help="also require profile/ to be blank")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    deny = []
    if args.profile:
        deny += terms_from_profile(Path(args.profile).expanduser().resolve())
    if args.denylist:
        deny += read_terms(Path(args.denylist))
    allow = read_terms(DEFAULT_ALLOW) + (read_terms(Path(args.allow)) if args.allow else [])
    deny = [d for d in dict.fromkeys(deny) if d and len(d) >= MIN_TERM]
    deny_re = re.compile(r"(?<![A-Za-z0-9])(?:" + "|".join(re.escape(d) for d in sorted(deny, key=len, reverse=True)) + r")(?![A-Za-z0-9])", re.IGNORECASE) if deny else None

    if not deny:
        print("warning: no denylist given (--profile or --denylist); only generic patterns are checked")

    hits = []
    for f in working_tree_files(repo):
        if not f.exists() or f.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        scan_text(text, str(f.relative_to(repo)), deny_re, allow, hits)
        if deny_re and deny_re.search(str(f.relative_to(repo))):
            hits.append((str(f.relative_to(repo)), "denylist-in-path", deny_re.search(str(f.relative_to(repo))).group(0)))

    if not args.no_history and (repo / ".git").exists():
        meta = git(repo, "log", "--all", "--format=%H %ae %ce")
        for line in meta.splitlines():
            sha, *emails = line.split()
            for e in emails:
                if not allowed(e, allow) and not e.endswith("@users.noreply.github.com"):
                    hits.append((f"commit {sha[:10]}", "author-email", e))
        current = "?"
        for line in git(repo, "log", "--all", "-p", "--format=COMMIT %H").splitlines():
            if line.startswith("COMMIT "):
                current = line.split()[1][:10]
            elif line.startswith("+") and not line.startswith("+++"):
                scan_text(line[1:], f"history {current}", deny_re, allow, hits)

    if args.publish:
        hits += [("profile/", "profile-not-blank", why) for why in profile_not_blank(repo / "profile")]

    seen = set()
    for where, kind, hit in hits:
        key = (where, kind, hit.lower())
        if key in seen:
            continue
        seen.add(key)
        print(f"{kind:16} {where}  {hit}")
    print(f"{len(seen)} hits in {repo}" + ("" if args.no_history else " (working tree and history)"))
    return 1 if seen else 0


if __name__ == "__main__":
    sys.exit(main())
