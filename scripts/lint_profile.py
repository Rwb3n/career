#!/usr/bin/env python3
"""Check a profile against the product's schemas and rules.

    python3 scripts/lint_profile.py [PROFILE_DIR]

Without an argument it checks profile/ at the repository root.
Prints errors and warnings; exits 1 if there is any error.

Checks:
  - every profile file parses and matches its schema (needs the jsonschema
    package; without it, only parsing and the checks below run)
  - atom ids are unique; every bullet's role_id is a role; every claim_domain
    is one of targets.json claim_domains; every evidence id is a story in
    stories.md or a file in sources/; unconfirmed bullets are flagged
  - every job file has a valid triage value
  - no never-name name appears in atoms.json or any composition text
  - ledger.jsonl: every line parses and matches its schema; timestamps never
    go backwards; a file recorded at submission has not changed since
  - every recipe matches schemas/recipe.schema.json
"""

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas"

try:
    import jsonschema  # type: ignore
except ImportError:
    jsonschema = None

errors, warnings = [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def load_json(path: Path, required=True):
    if not path.exists():
        if required:
            err(f"missing: {path.name}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(f"{path.name}: not valid JSON ({e})")
        return None


def check_schema(data, schema_name, label):
    if data is None or jsonschema is None:
        return
    schema_path = SCHEMAS / schema_name
    if not schema_path.exists():
        warn(f"schema {schema_name} not found; {label} not schema-checked")
        return
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    for e in sorted(validator.iter_errors(data), key=lambda x: list(x.path)):
        where = "/".join(str(p) for p in e.path) or "(top)"
        err(f"{label} {where}: {e.message}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lint(profile: Path):
    profile_json = load_json(profile / "profile.json")
    check_schema(profile_json, "profile.schema.json", "profile.json")

    atoms = load_json(profile / "atoms.json")
    check_schema(atoms, "atoms.schema.json", "atoms.json")

    targets = load_json(profile / "targets.json")
    check_schema(targets, "targets.schema.json", "targets.json")

    constraints = load_json(profile / "constraints.json")
    check_schema(constraints, "items.schema.json", "constraints.json")

    decisions = load_json(profile / "decisions.json", required=False)
    check_schema(decisions, "items.schema.json", "decisions.json")

    local_rules = load_json(profile / "rules-local.json", required=False)
    check_schema(local_rules, "rules.schema.json", "rules-local.json")

    stories_text = ""
    if (profile / "stories.md").exists():
        stories_text = (profile / "stories.md").read_text(encoding="utf-8")
    else:
        err("missing: stories.md")
    if not (profile / "voice.md").exists():
        warn("missing: voice.md (the voice lens has nothing to check against)")

    # Atom integrity
    if atoms:
        seen = {}
        def walk_ids(kind, items):
            for it in items or []:
                i = it.get("id")
                if i in seen:
                    err(f"atoms.json: id {i} used twice ({seen[i]} and {kind})")
                seen[i] = kind
        for kind in ("certifications", "education", "roles", "bullets", "projects", "fragments"):
            walk_ids(kind, atoms.get(kind))
        for cat, items in (atoms.get("skills") or {}).items():
            walk_ids(f"skills.{cat}", items)

        role_ids = {r.get("id") for r in atoms.get("roles") or []}
        domains = set((targets or {}).get("claim_domains") or [])
        evidence_ids = set(re.findall(r"^##\s+(st-[a-z0-9-]+)", stories_text, re.MULTILINE))
        for b in atoms.get("bullets") or []:
            if b.get("role_id") not in role_ids:
                err(f"atoms.json bullet {b.get('id')}: role_id {b.get('role_id')} is not a role")
            if domains and b.get("claim_domain") not in domains:
                err(f"atoms.json bullet {b.get('id')}: claim_domain '{b.get('claim_domain')}' is not in targets.json claim_domains")
            for ev in b.get("evidence") or []:
                if ev.startswith("sources/"):
                    if not (profile / ev).exists():
                        warn(f"atoms.json bullet {b.get('id')}: evidence {ev} not found")
                elif ev not in evidence_ids:
                    warn(f"atoms.json bullet {b.get('id')}: story {ev} not found in stories.md")
            if not b.get("evidence"):
                warn(f"atoms.json bullet {b.get('id')}: no story or source behind it")
            if not b.get("confirmed"):
                warn(f"atoms.json bullet {b.get('id')}: not confirmed by the user; it won't be used in a pack")
        for p in atoms.get("projects") or []:
            if domains and p.get("claim_domain") and p["claim_domain"] not in domains:
                err(f"atoms.json project {p.get('id')}: claim_domain '{p['claim_domain']}' is not in targets.json claim_domains")

    # Never-name
    names = []
    for item in (constraints or {}).get("items") or []:
        if item.get("kind") == "never-name":
            names += [n for n in item.get("names") or [] if n.strip()]
    if names:
        pattern = re.compile("|".join(re.escape(n) for n in names), re.IGNORECASE)
        if atoms:
            for b in atoms.get("bullets") or []:
                m = pattern.search(b.get("text", ""))
                if m:
                    err(f"atoms.json bullet {b.get('id')}: contains never-name '{m.group(0)}'")
        for f in (profile / "packs").glob("*/*.md"):
            m = pattern.search(f.read_text(encoding="utf-8"))
            if m:
                err(f"{f.relative_to(profile)}: contains never-name '{m.group(0)}'")

    # Ledger
    ledger = profile / "ledger.jsonl"
    if not ledger.exists():
        err("missing: ledger.jsonl (create it empty)")
    else:
        last_ts = ""
        for n, line in enumerate(ledger.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as e:
                err(f"ledger.jsonl line {n}: not valid JSON ({e})")
                continue
            check_schema(entry, "ledger-entry.schema.json", f"ledger.jsonl line {n}")
            ts = entry.get("ts", "")
            if ts < last_ts:
                err(f"ledger.jsonl line {n}: ts {ts} is earlier than the line before; the ledger only grows")
            last_ts = max(last_ts, ts)
            for rel, digest in (entry.get("files") or {}).items():
                f = profile / rel
                if not f.exists():
                    err(f"ledger.jsonl line {n}: sent file {rel} is missing")
                elif sha256(f) != digest:
                    err(f"ledger.jsonl line {n}: sent file {rel} has changed since it was sent; sent files are records")

    # Jobs
    for j in (profile / "jobs").glob("*.md"):
        m = re.search(r"^triage:\s*\"?([a-z-]*)", j.read_text(encoding="utf-8"), re.MULTILINE)
        if not m or m.group(1) not in ("fit", "stretch", "not-for-me", "undecided"):
            err(f"{j.relative_to(profile)}: triage must be fit, stretch, not-for-me or undecided")

    # Packs
    for r in (profile / "packs").glob("*/recipe.json"):
        check_schema(load_json(r), "recipe.schema.json", str(r.relative_to(profile)))
    for pk in (profile / "packs").glob("*/PACK.md"):
        m = re.search(r"^status:\s*([a-z]+)", pk.read_text(encoding="utf-8"), re.MULTILINE)
        if not m or m.group(1) not in ("drafted", "reviewed", "sent"):
            err(f"{pk.relative_to(profile)}: status must be drafted, reviewed or sent")


def main(argv):
    profile = Path(argv[0]).expanduser().resolve() if argv else ROOT / "profile"
    if not profile.is_dir():
        print(f"{profile} is not a folder")
        return 1
    lint(profile)
    if jsonschema is None:
        warn("jsonschema is not installed (pip install -r requirements.txt); schema checks skipped")
    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"error: {e}")
    print(f"{profile}: {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
