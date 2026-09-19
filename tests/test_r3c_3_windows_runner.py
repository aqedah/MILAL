"""PowerShell 5.1/7 process contracts for the BHSA-free presentation wrapper."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import venv
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SHELLS = [p for name in ("powershell", "pwsh") if (p := shutil.which(name))]


@unittest.skipUnless(os.name == "nt" and SHELLS, "Windows PowerShell required")
class R3c3WindowsRunnerTests(unittest.TestCase):
    def exercise(self, shell, default=False, self_status=0, presentation_status=0,
                 zip_failure=False, existing=None, missing=False, extra=None):
        with tempfile.TemporaryDirectory(prefix="milal r3c3 runner ") as temp:
            root = Path(temp)
            for name in ("scripts", "src", "caller"):
                (root / name).mkdir()
            runner = root / "scripts/run_milal_r3c_3_windows.ps1"
            shutil.copyfile(ROOT / "scripts" / runner.name, runner)
            interpreter = Path(sys.executable)
            if default:
                venv.EnvBuilder(with_pip=False).create(root / ".venv")
                interpreter = root / ".venv/Scripts/python.exe"
            for name in ("milal_r3c_0_2_reviewability.py", "milal_r3c_1_review_units.py", "milal_r3c_2_compact_review.py"):
                (root / "src" / name).touch()
            script = '''import json, pathlib, sys
root = pathlib.Path(__file__).resolve().parents[1]
args = sys.argv[1:]
with (root / 'calls.jsonl').open('a') as f:
    f.write(json.dumps({'args': args, 'python': sys.executable}) + '\\n')
print('Hebrew \\u05d0')
print('stderr captured', file=sys.stderr)
if '--self-test' in args:
    sys.exit(SELF_STATUS)
out = pathlib.Path(args[args.index('--output-dir') + 1])
out.mkdir()
(out / '09_review_packet_compact.md').write_text('fixture packet')
if ZIP_FAILURE:
    (root / 'output_results.zip').mkdir()
sys.exit(PRESENTATION_STATUS)
'''
            script = script.replace("SELF_STATUS", str(self_status)).replace("ZIP_FAILURE", repr(zip_failure)).replace("PRESENTATION_STATUS", str(presentation_status))
            (root / "src/milal_r3c_3_signature_context.py").write_text(script)
            source, output = root / "source r3c1.zip", root / "output"
            if not missing:
                source.write_bytes(b"frozen input placeholder")
            if existing:
                preserved = root / existing
                if existing == "output":
                    preserved.mkdir()
                    preserved = preserved / "preserved.txt"
                preserved.write_text("preserve unchanged")
            command = [shell, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(runner),
                       "-R3c1Zip", str(source), "-R3c2Zip", str(source), "-R3b2Zip", str(source), "-R3b3Zip", str(source), "-OutputDir", str(output)]
            if not default:
                command.extend(["-PythonExe", str(interpreter)])
            if extra:
                command.extend(["-ResultZip", str(output / "nested.zip")])
            result = subprocess.run(command, cwd=root / "caller", capture_output=True, timeout=60)
            log_file = root / "output_windows_run.log"
            log = log_file.read_text(encoding="utf-8-sig") if log_file.is_file() else ""
            calls_file = root / "calls.jsonl"
            calls = [json.loads(s) for s in calls_file.read_text().splitlines()] if calls_file.exists() else []
            if existing or missing or extra:
                self.assertEqual(result.returncode, 2)
                self.assertEqual(calls, [])
                if existing:
                    self.assertEqual(preserved.read_text(), "preserve unchanged")
                return
            self.assertTrue(calls, log or repr(result.stderr))
            self.assertEqual(calls[0]["args"], ["--self-test"])
            self.assertTrue(all(Path(c["python"]).resolve() == interpreter.resolve() for c in calls))
            self.assertIn("Hebrew א", log)
            self.assertIn("stderr captured", log)
            if self_status:
                self.assertEqual(result.returncode, self_status, log)
                self.assertEqual(len(calls), 1)
                self.assertFalse(output.exists())
                return
            self.assertEqual(calls[1]["args"], ["--r3c1-zip", str(source), "--r3c2-zip", str(source), "--r3b2-zip", str(source), "--r3b3-zip", str(source), "--output-dir", str(output)])
            self.assertEqual(result.returncode, presentation_status or (1 if zip_failure else 0), log)
            self.assertEqual(source.read_bytes(), b"frozen input placeholder")
            if not zip_failure:
                with zipfile.ZipFile(root / "output_results.zip") as archive:
                    self.assertEqual(archive.namelist(), ["output/09_review_packet_compact.md"])

    def test_repository_default_interpreter_from_other_cwd(self):
        for shell in SHELLS:
            with self.subTest(shell=shell):
                self.exercise(shell, default=True)

    def test_explicit_interpreter_no_bhsa_argument(self):
        for shell in SHELLS:
            with self.subTest(shell=shell):
                self.exercise(shell)

    def test_failure_statuses_preserved(self):
        for shell in SHELLS:
            for options in ({"self_status": 17}, {"presentation_status": 23}, {"zip_failure": True},
                            {"presentation_status": 23, "zip_failure": True}):
                with self.subTest(shell=shell, **options):
                    self.exercise(shell, **options)

    def test_no_overwrite_output_archive_or_log(self):
        for shell in SHELLS:
            for name in ("output", "output_results.zip", "output_windows_run.log"):
                with self.subTest(shell=shell, name=name):
                    self.exercise(shell, existing=name)

    def test_missing_input_preflight(self):
        for shell in SHELLS:
            with self.subTest(shell=shell):
                self.exercise(shell, missing=True)

    def test_archive_cannot_be_inside_manifest_tree(self):
        for shell in SHELLS:
            with self.subTest(shell=shell):
                self.exercise(shell, extra=True)
