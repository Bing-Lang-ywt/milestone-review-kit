import subprocess
import tempfile
import unittest
from pathlib import Path
from review import review


class ReviewTests(unittest.TestCase):
    def test_range_records_real_commits_and_changed_scope(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            def git(*args):
                return subprocess.run(["git", "-C", temp, *args], check=True,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip()
            git("init")
            git("config", "user.name", "Fixture")
            git("config", "user.email", "fixture@example.invalid")
            (repo / "README.md").write_text("initial")
            git("add", ".")
            git("commit", "-m", "Initial")
            base = git("rev-parse", "HEAD")
            (repo / "src").mkdir()
            (repo / "src" / "a.py").write_text("print('example')")
            git("add", ".")
            git("commit", "-m", "Add example")
            head = git("rev-parse", "HEAD")
            report = review(repo, base, head)
            self.assertTrue(report["base_is_ancestor"])
            self.assertEqual(report["changed_paths"], ["src/a.py"])
            self.assertEqual(report["commits_reachable_from_head_not_base"], [head])
            self.assertEqual(report["areas"], {"src": ["src/a.py"]})
            empty = review(repo, head, head)
            self.assertEqual(empty["changed_paths"], [])
            self.assertEqual(empty["commits_reachable_from_head_not_base"], [])
            reverse = review(repo, head, base)
            self.assertFalse(reverse["base_is_ancestor"])
            with self.assertRaises(subprocess.CalledProcessError):
                review(repo, "missing", head)
