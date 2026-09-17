"""Execute the wrapper with a recording Python core; no BHSA data needed."""
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
SHELLS = [p for name in ('powershell', 'pwsh') if (p := shutil.which(name))]


@unittest.skipUnless(os.name == 'nt' and SHELLS, 'Windows PowerShell required')
class WindowsRunnerTests(unittest.TestCase):
    def run_fixture(self, shell, self_status=0, analysis_status=0, missing=None,
                    existing=False, zip_failure=False, default_python=False):
        with tempfile.TemporaryDirectory(prefix='milal runner ') as temp:
            root = Path(temp)
            expected_python = Path(sys.executable)
            if default_python:
                venv.EnvBuilder(with_pip=False).create(root / '.venv')
                expected_python = root / '.venv/Scripts/python.exe'
                self.assertTrue(expected_python.is_file())
            for directory in ('scripts', 'src', 'config', 'BHSA 2021'):
                (root / directory).mkdir()
            runner = root / 'scripts/run_milal_r3c_0_2_windows.ps1'
            shutil.copyfile(ROOT / 'scripts' / runner.name, runner)
            config = root / 'config/r3c_0_2_job_pilot.json'
            config.write_text('{}')
            core = root / 'src/milal_r3c_0_2_reviewability.py'
            core.write_text('''import json, pathlib, sys
root = pathlib.Path(__file__).resolve().parents[1]
args = sys.argv[1:]
with (root / 'interpreters.jsonl').open('a') as f:
    f.write(json.dumps(sys.executable) + '\\n')
with (root / 'calls.jsonl').open('a') as f:
    f.write(json.dumps(args) + '\\n')
print('stdout: Hebrew \\u05d0')
print('stderr captured', file=sys.stderr)
if '--self-test' in args:
    sys.exit(SELF_STATUS)
out = pathlib.Path(args[args.index('--output-dir') + 1])
out.mkdir()
(out / '09_review_packet.md').write_text('packet fixture')
if ZIP_FAILURE:
    (root / 'out_results.zip').mkdir()
sys.exit(ANALYSIS_STATUS)
'''.replace('SELF_STATUS', str(self_status))
               .replace('ANALYSIS_STATUS', str(analysis_status))
               .replace('ZIP_FAILURE', repr(zip_failure)), encoding='utf-8')
            r2, r3 = root / 'input 2.zip', root / 'input 3.zip'
            tf = root / 'BHSA 2021'
            for path in (r2, r3, tf / 'otype.tf', tf / 'oslots.tf'):
                if path.name != missing:
                    path.touch()
            out = root / 'out'
            if existing:
                out.mkdir()
                (out / 'keep.txt').write_text('preserve')
            command = [
                shell, '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
                '-File', str(runner), '-R3b2Zip', str(r2), '-R3b3Zip', str(r3),
                '-TfDir', str(tf), '-OutputDir', str(out),
                '-Seed', '12345',
            ]
            if not default_python:
                command.extend(['-PythonExe', sys.executable])
            # A different working directory also catches defaults based on cwd.
            caller = root / 'caller'
            caller.mkdir()
            result = subprocess.run(command, cwd=caller, capture_output=True, timeout=60)
            calls_file = root / 'calls.jsonl'
            calls = [json.loads(line) for line in calls_file.read_text().splitlines()] if calls_file.exists() else []
            log_path = root / 'out_windows_run.log'
            log = log_path.read_text(encoding='utf-8-sig') if log_path.exists() else ''
            if missing or existing:
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(calls, [])
                if missing:
                    self.assertIn(missing, log)
                if existing:
                    self.assertEqual((out / 'keep.txt').read_text(), 'preserve')
                return
            self.assertTrue(calls, log or repr(result.stderr))
            interpreters = [Path(json.loads(line)) for line in
                            (root / 'interpreters.jsonl').read_text().splitlines()]
            self.assertTrue(all(p.resolve() == expected_python.resolve() for p in interpreters),
                            interpreters)
            if default_python:
                self.assertTrue(all(p.resolve().is_relative_to(root.resolve()) for p in interpreters))
            self.assertEqual(calls[0], ['--self-test'])
            self.assertIn('stderr captured', log)
            self.assertIn('Hebrew א', log)
            if self_status:
                self.assertEqual(result.returncode, self_status, log)
                self.assertEqual(len(calls), 1)
                self.assertFalse(out.exists())
                return
            self.assertEqual(calls[1], [
                '--r3b2-zip', str(r2), '--r3b3-zip', str(r3), '--tf-dir', str(tf),
                '--output-dir', str(out), '--pilot-config', str(config), '--seed', '12345'])
            self.assertEqual(result.returncode, analysis_status or (1 if zip_failure else 0), log)
            if not zip_failure:
                with zipfile.ZipFile(root / 'out_results.zip') as archive:
                    self.assertEqual(archive.namelist(), ['out/09_review_packet.md'])
                    self.assertEqual(archive.read('out/09_review_packet.md'), b'packet fixture')

    def test_arguments_logging_and_archive(self):
        for shell in SHELLS:
            with self.subTest(shell=shell):
                self.run_fixture(shell)

    def test_repository_relative_default_python(self):
        for shell in SHELLS:
            with self.subTest(shell=shell):
                self.run_fixture(shell, default_python=True)

    def test_failures_preserve_status(self):
        for shell in SHELLS:
            for options in ({'self_status': 17}, {'analysis_status': 23},
                            {'zip_failure': True}, {'analysis_status': 23, 'zip_failure': True}):
                with self.subTest(shell=shell, **options):
                    self.run_fixture(shell, **options)

    def test_preflight_preserves_existing_results_and_checks_tf(self):
        for shell in SHELLS:
            for options in ({'missing': 'otype.tf'}, {'missing': 'oslots.tf'}, {'existing': True}):
                with self.subTest(shell=shell, **options):
                    self.run_fixture(shell, **options)
