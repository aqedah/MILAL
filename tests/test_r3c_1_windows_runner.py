"""R3c.1 runner process contracts, independent of real BHSA/Text-Fabric."""
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
class R3c1WindowsRunnerTests(unittest.TestCase):
    def exercise(self, shell, default=False, seed=None, self_status=0, analysis_status=0,
                 zip_failure=False, existing=None, missing=None):
        with tempfile.TemporaryDirectory(prefix='milal r3c1 runner ') as temp:
            root = Path(temp)
            for name in ('scripts', 'src', 'config', 'BHSA 2021', 'caller'):
                (root / name).mkdir()
            runner = root / 'scripts/run_milal_r3c_1_windows.ps1'
            shutil.copyfile(ROOT / 'scripts' / runner.name, runner)
            interpreter = Path(sys.executable)
            if default:
                venv.EnvBuilder(with_pip=False).create(root / '.venv')
                interpreter = root / '.venv/Scripts/python.exe'
            (root / 'src/milal_r3c_0_2_reviewability.py').touch()
            config = root / 'config/r3c_1_job_pilot.json'
            config.write_text('{"seed": 111}')
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
(out / '10_review_packet.md').write_text('fixture packet')
if ZIP_FAILURE:
    (root / 'output_results.zip').mkdir()
sys.exit(ANALYSIS_STATUS)
'''
            script = script.replace('SELF_STATUS', str(self_status)).replace('ANALYSIS_STATUS', str(analysis_status)).replace('ZIP_FAILURE', repr(zip_failure))
            (root / 'src/milal_r3c_1_review_units.py').write_text(script)
            r2, r3, tf, output = root / 'r3b 2.zip', root / 'r3b 3.zip', root / 'BHSA 2021', root / 'output'
            for path in (r2, r3, tf / 'otype.tf', tf / 'oslots.tf'):
                if path.name != missing:
                    path.touch()
            if existing:
                preserved = root / existing
                if existing == 'output':
                    preserved.mkdir()
                    preserved = preserved / 'preserved.txt'
                preserved.write_text('preserve unchanged')
            command = [shell, '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File', str(runner),
                       '-R3b2Zip', str(r2), '-R3b3Zip', str(r3), '-TfDir', str(tf), '-OutputDir', str(output)]
            if not default:
                command.extend(['-PythonExe', str(interpreter)])
            if seed is not None:
                command.extend(['-Seed', str(seed)])
            result = subprocess.run(command, cwd=root / 'caller', capture_output=True, timeout=60)
            log_file = root / 'output_windows_run.log'
            log = log_file.read_text(encoding='utf-8-sig') if log_file.is_file() else ''
            calls_file = root / 'calls.jsonl'
            calls = [json.loads(s) for s in calls_file.read_text().splitlines()] if calls_file.exists() else []
            if existing or missing:
                self.assertEqual(result.returncode, 2)
                self.assertEqual(calls, [])
                if existing:
                    self.assertEqual(preserved.read_text(), 'preserve unchanged')
                if missing:
                    self.assertIn(missing, log)
                return
            self.assertTrue(calls, log or repr(result.stderr))
            self.assertEqual(calls[0]['args'], ['--self-test'])
            self.assertTrue(all(Path(c['python']).resolve() == interpreter.resolve() for c in calls))
            if default:
                self.assertTrue(all(Path(c['python']).resolve().is_relative_to(root) for c in calls))
            self.assertIn('Hebrew א', log)
            self.assertIn('stderr captured', log)
            if self_status:
                self.assertEqual(result.returncode, self_status, log)
                self.assertEqual(len(calls), 1)
                self.assertFalse(output.exists())
                return
            expected = ['--r3b2-zip', str(r2), '--r3b3-zip', str(r3), '--tf-dir', str(tf),
                        '--output-dir', str(output), '--pilot-config', str(config)]
            if seed is not None:
                expected += ['--seed', str(seed)]
            self.assertEqual(calls[1]['args'], expected)
            self.assertEqual(result.returncode, analysis_status or (1 if zip_failure else 0), log)
            if not zip_failure:
                with zipfile.ZipFile(root / 'output_results.zip') as z:
                    self.assertEqual(z.namelist(), ['output/10_review_packet.md'])
                    self.assertEqual(z.read(z.namelist()[0]), b'fixture packet')

    def test_repository_default_and_configured_seed(self):
        for shell in SHELLS:
            with self.subTest(shell=shell):
                self.exercise(shell, default=True)

    def test_explicit_python_and_seed_override(self):
        for shell in SHELLS:
            with self.subTest(shell=shell):
                self.exercise(shell, seed=24680)

    def test_failure_codes_and_diagnostic_archives(self):
        for shell in SHELLS:
            for options in ({'self_status': 17}, {'analysis_status': 23}, {'zip_failure': True},
                            {'analysis_status': 23, 'zip_failure': True}):
                with self.subTest(shell=shell, **options):
                    self.exercise(shell, **options)

    def test_existing_destinations_never_overwritten(self):
        for shell in SHELLS:
            for name in ('output', 'output_results.zip', 'output_windows_run.log'):
                with self.subTest(shell=shell, name=name):
                    self.exercise(shell, existing=name)

    def test_required_bhsa_files(self):
        for shell in SHELLS:
            for name in ('otype.tf', 'oslots.tf'):
                with self.subTest(shell=shell, name=name):
                    self.exercise(shell, missing=name)
