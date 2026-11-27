import os
import subprocess
import sys
from pathlib import Path

from django.test import SimpleTestCase

BASE_DIR = Path(__file__).resolve().parent.parent

VALID_ENV = {
    "SECRET_KEY": "x" * 60,
    "ALLOWED_HOSTS": "example.com",
    "POSTGRES_DB": "db",
    "POSTGRES_USER": "user",
    "POSTGRES_PASSWORD": "pw",
    "POSTGRES_HOST": "localhost",
}


def import_settings(env):
    """Import config.settings in a clean process with exactly this environment."""
    clean = {"PATH": os.environ["PATH"], **env}
    return subprocess.run(
        [sys.executable, "-c", "import config.settings"],
        cwd=BASE_DIR,
        env=clean,
        capture_output=True,
        text=True,
    )


class SettingsFailLoudlyTests(SimpleTestCase):
    def test_valid_environment_loads(self):
        result = import_settings(VALID_ENV)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_secret_key_fails(self):
        env = {k: v for k, v in VALID_ENV.items() if k != "SECRET_KEY"}
        result = import_settings(env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SECRET_KEY", result.stderr)

    def test_missing_allowed_hosts_fails_when_debug_off(self):
        env = {k: v for k, v in VALID_ENV.items() if k != "ALLOWED_HOSTS"}
        result = import_settings(env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ALLOWED_HOSTS", result.stderr)

    def test_missing_allowed_hosts_ok_when_debug_on(self):
        env = {k: v for k, v in VALID_ENV.items() if k != "ALLOWED_HOSTS"}
        result = import_settings({**env, "DEBUG": "1"})
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_database_password_fails(self):
        env = {k: v for k, v in VALID_ENV.items() if k != "POSTGRES_PASSWORD"}
        result = import_settings(env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("POSTGRES_PASSWORD", result.stderr)
