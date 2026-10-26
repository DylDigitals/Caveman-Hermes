"""Exercise the public installer against the real Hermes CLI in disposable homes."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HERMES = os.environ.get("HERMES_EXECUTABLE")


@unittest.skipUnless(HERMES, "Set HERMES_EXECUTABLE to run native installer checks")
class Install(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="caveman-installer-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "profile with spaces"
        self.home.mkdir()
        self.config = self.home / "config.yaml"
        self.config.write_text('skills:\n  auto_load: [retained-skill]\nmodel:\n  default: retained-model\nplugins:\n  enabled: []\n')
        self.env = {k: os.environ[k] for k in ("PATH", "LANG", "PYTHONPATH") if k in os.environ}
        self.env.update(HOME=str(self.root), HERMES_HOME=str(self.home), PYTHONDONTWRITEBYTECODE="1")

    def install(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "scripts/install.py"), "--home", str(self.home),
                               "--hermes", HERMES, *args], env=self.env, cwd=self.root,
                              capture_output=True, text=True, timeout=120)

    def get(self, key):
        result = subprocess.run([HERMES, "config", "get", key, "--json"], env=self.env, cwd=self.root,
                                capture_output=True, text=True, timeout=30, check=True)
        return json.loads(result.stdout)

    def test_preflight_install_and_repeat_refusal_preserve_user_state(self):
        original = self.config.read_bytes()
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.config.read_bytes(), original)
        self.assertFalse((self.home / "plugins/caveman-communication").exists())
        result = self.install("--apply", "--mode", "lite")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.get("skills.auto_load"), ["retained-skill", "caveman"])
        self.assertEqual(self.get("model.default"), "retained-model")
        self.assertEqual(self.get("plugins.entries.caveman-communication.settings.mode"), "lite")
        self.assertIn("caveman-communication", self.get("plugins.enabled"))
        self.assertEqual((self.home / "skills/caveman/SKILL.md").read_bytes(), (ROOT / "skill/SKILL.md").read_bytes())
        after = self.config.read_bytes()
        result = self.install("--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.config.read_bytes(), after)

    def test_duplicate_skill_elsewhere_is_not_overwritten(self):
        existing = self.home / "skills/productivity/caveman"
        existing.mkdir(parents=True)
        text = '---\nname: caveman\ndescription: Existing user-owned skill\n---\nKeep this unchanged.\n'
        (existing / "SKILL.md").write_text(text)
        original = self.config.read_bytes()
        result = self.install("--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("already discoverable", result.stderr)
        self.assertEqual((existing / "SKILL.md").read_text(), text)
        self.assertEqual(self.config.read_bytes(), original)
        self.assertFalse((self.home / "plugins/caveman-communication").exists())

    def test_symlink_boundary_is_refused_without_touching_other_profile(self):
        other = self.root / "other-profile"
        other.mkdir()
        (self.home / "plugins").symlink_to(other, target_is_directory=True)
        result = self.install("--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlinked", result.stderr)
        self.assertEqual(list(other.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
