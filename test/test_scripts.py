"""Tests for the profile lint and the personal-data scan.

    python -m unittest discover -s test
"""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = ROOT / "examples" / "sample-profile"
PY = sys.executable


def run(*args, env=None):
    return subprocess.run([PY, *args], capture_output=True, text=True, cwd=ROOT, env=env)


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


class LintTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.profile = self.tmp / "profile"
        shutil.copytree(EXAMPLE, self.profile)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def lint(self):
        return run("scripts/lint_profile.py", str(self.profile))

    def edit_json(self, name, fn):
        p = self.profile / name
        data = json.loads(p.read_text(encoding="utf-8"))
        fn(data)
        p.write_text(json.dumps(data), encoding="utf-8")

    def test_example_is_clean(self):
        r = self.lint()
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_unknown_role_id(self):
        self.edit_json("atoms.json", lambda d: d["bullets"][0].update(role_id="role-nowhere"))
        r = self.lint()
        self.assertEqual(r.returncode, 1)
        self.assertIn("is not a role", r.stdout)

    def test_claim_domain_outside_targets(self):
        self.edit_json("atoms.json", lambda d: d["bullets"][0].update(claim_domain="astrology"))
        self.assertIn("not in targets.json claim_domains", self.lint().stdout)

    def test_never_name_in_bullet(self):
        self.edit_json("atoms.json", lambda d: d["bullets"][0].update(text="Led Project Bluebird to launch."))
        self.assertIn("never-name", self.lint().stdout)

    def test_never_name_in_composition(self):
        d = self.profile / "packs" / "ba-acme"
        d.mkdir()
        (d / "CV-20260201-ba-acme.md").write_text("Worked on project bluebird.", encoding="utf-8")
        self.assertIn("never-name", self.lint().stdout)

    def test_user_voice_needs_said(self):
        self.edit_json("constraints.json", lambda d: d["items"][0].pop("said"))
        r = self.lint()
        self.assertEqual(r.returncode, 1, r.stdout)

    def test_ledger_never_goes_backwards(self):
        with open(self.profile / "ledger.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": "2025-01-01T00:00:00Z", "slug": "ba-x", "stage": "queued", "as_of": "2025-01-01", "voice": "user", "said": "x"}) + "\n")
        self.assertIn("only grows", self.lint().stdout)

    def test_sent_file_changed(self):
        d = self.profile / "packs" / "ba-acme"
        d.mkdir()
        cv = d / "CV.pdf"
        cv.write_bytes(b"sent version")
        import hashlib
        digest = hashlib.sha256(b"sent version").hexdigest()
        with open(self.profile / "ledger.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": "2026-02-01T00:00:00Z", "slug": "ba-acme", "stage": "sent", "as_of": "2026-02-01", "voice": "user", "said": "sent", "files": {"packs/ba-acme/CV.pdf": digest}}) + "\n")
        self.assertEqual(self.lint().returncode, 0)
        cv.write_bytes(b"edited after sending")
        self.assertIn("has changed since it was sent", self.lint().stdout)


class ScanTests(unittest.TestCase):
    """The scan must catch planted personal data, including data deleted from history."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.name", "Test")
        git(self.repo, "config", "user.email", "1+test@users.noreply.github.com")
        (self.repo / "README.md").write_text("A clean file about Acme.\n", encoding="utf-8")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "-m", "clean")

        self.profile = self.tmp / "profile"
        self.profile.mkdir()
        (self.profile / "profile.json").write_text(json.dumps({"identity": {"name": "Jordan Quillfeather", "email": "jq@mailhost.test"}}), encoding="utf-8")  # scan:fixture
        (self.profile / "atoms.json").write_text(json.dumps({"roles": [{"company": "Zephyrine Logistics"}]}), encoding="utf-8")
        (self.profile / "constraints.json").write_text(json.dumps({"items": [{"kind": "never-name", "names": ["Operation Lantern"]}]}), encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def scan(self, *extra):
        return run("scripts/scan_personal.py", "--repo", str(self.repo), "--profile", str(self.profile), *extra)

    def test_clean_repo_passes(self):
        r = self.scan()
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_catches_name_in_working_tree(self):
        (self.repo / "notes.md").write_text("Written by Quillfeather.\n", encoding="utf-8")
        r = self.scan()
        self.assertEqual(r.returncode, 1)
        self.assertIn("Quillfeather", r.stdout)

    def test_catches_employer_and_never_name(self):
        (self.repo / "x.json").write_text('{"a": "Zephyrine Logistics", "b": "operation lantern"}\n', encoding="utf-8")
        out = self.scan().stdout
        self.assertIn("Zephyrine Logistics", out)
        self.assertIn("operation lantern", out)

    def test_catches_data_deleted_from_history(self):
        secret = self.repo / "old.md"
        secret.write_text("Call me on 07700 900123, Jordan Quillfeather\n", encoding="utf-8")  # scan:fixture
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "-m", "oops")
        secret.unlink()
        git(self.repo, "commit", "-q", "-am", "remove")
        r = self.scan()
        self.assertEqual(r.returncode, 1)
        self.assertIn("history", r.stdout)
        self.assertEqual(self.scan("--no-history").returncode, 0)

    def test_catches_generic_patterns_without_profile(self):
        (self.repo / "c.md").write_text("mail someone@realmail.test, NI QQ 12 34 56 C, postcode SW1A 1AA\n", encoding="utf-8")  # scan:fixture
        r = run("scripts/scan_personal.py", "--repo", str(self.repo), "--no-history")
        self.assertEqual(r.returncode, 1)
        for kind in ("email", "ni-number", "uk-postcode"):
            self.assertIn(kind, r.stdout)

    def test_catches_author_email(self):
        git(self.repo, "-c", "user.email=jq@mailhost.test", "commit", "-q", "--allow-empty", "-m", "x")  # scan:fixture
        self.assertIn("author-email", self.scan().stdout)

    def test_allows_example_domain(self):
        (self.repo / "e.md").write_text("contact sam.rivera@example.com\n", encoding="utf-8")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "-m", "example")
        self.assertEqual(self.scan().returncode, 0)


class PublishAndWordTests(ScanTests):
    def test_short_terms_do_not_match_inside_words(self):
        (self.profile / "profile.json").write_text(json.dumps({"identity": {"name": "Al Ust"}}), encoding="utf-8")
        (self.repo / "w.md").write_text("You must trust the process.\n", encoding="utf-8")
        self.assertEqual(self.scan("--no-history").returncode, 0)

    def test_whole_word_only(self):
        (self.repo / "w.md").write_text("Zephyrine Logisticsbrand\n", encoding="utf-8")
        self.assertEqual(self.scan("--no-history").returncode, 0)

    def test_publish_needs_blank_profile(self):
        shutil.copytree(ROOT / "profile", self.repo / "profile")
        self.assertEqual(self.scan("--no-history", "--publish").returncode, 0)
        (self.repo / "profile" / "ledger.jsonl").write_text('{"slug": "x"}\n', encoding="utf-8")
        r = self.scan("--no-history", "--publish")
        self.assertEqual(r.returncode, 1)
        self.assertIn("profile-not-blank", r.stdout)


class PrivacyCheckTests(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        import privacy_check
        self.pc = privacy_check

    def test_parses_remotes(self):
        for url in ("https://github.com/acme/career.git", "https://github.com/acme/career", "git@github.com:acme/career.git",
                    "ssh://git@github.com/acme/career", "http://local_proxy@127.0.0.1:41923/git/acme/career"):
            self.assertEqual(self.pc.owner_repo(url), ("acme", "career"), url)
        self.assertIsNone(self.pc.owner_repo("https://gitlab.com/acme/career.git"))

    def test_no_remote_cannot_tell(self):
        import os
        tmp = Path(tempfile.mkdtemp())
        try:
            shutil.copytree(ROOT / "scripts", tmp / "scripts")
            git(tmp, "init", "-q")
            env = {k: v for k, v in os.environ.items() if k != "CAREER_LOCAL_ONLY"}
            r = subprocess.run([PY, "scripts/privacy_check.py"], capture_output=True, text=True, cwd=tmp, env=env)
            self.assertEqual(r.returncode, 2, r.stdout)
            env["CAREER_LOCAL_ONLY"] = "1"
            r = subprocess.run([PY, "scripts/privacy_check.py"], capture_output=True, text=True, cwd=tmp, env=env)
            self.assertEqual(r.returncode, 0, r.stdout)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class BlankProfileTests(unittest.TestCase):
    def test_shipped_profile_lints_clean(self):
        r = run("scripts/lint_profile.py")
        self.assertEqual(r.returncode, 0, r.stdout)


if __name__ == "__main__":
    unittest.main()
