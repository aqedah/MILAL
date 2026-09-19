"""PROV1 runner ordering and failure propagation under installed PowerShells."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SHELLS = [s for n in ('powershell', 'pwsh') if (s := shutil.which(n))]


@unittest.skipUnless(SHELLS, 'PowerShell required')
class Prov1RunnerTests(unittest.TestCase):
    def exercise(self, shell, self_exit=0, run_exit=0, existing=False):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / 'scripts').mkdir(); (root / 'src').mkdir()
            runner = root / 'scripts/run_milal_prov1_windows.ps1'
            shutil.copyfile(ROOT / 'scripts' / runner.name, runner)
            code = """import json,sys,pathlib
root=pathlib.Path(__file__).resolve().parents[1]
with (root/'calls').open('a') as f: f.write(json.dumps(sys.argv[1:])+'\\n')
sys.exit(SELF_EXIT if '--self-test' in sys.argv else RUN_EXIT)
""".replace('SELF_EXIT', str(self_exit)).replace('RUN_EXIT', str(run_exit))
            (root / 'src/milal_prov1_signature_provenance.py').write_text(code)
            source = root / 'input'; source.write_text('unchanged')
            output = root / 'out'
            if existing: output.mkdir()
            args = [shell, '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File', str(runner),
                    '-PythonExe', sys.executable, '-OutputDir', str(output)]
            for flag in ['Generator','R2Zip','R3b2Zip','R3b3Zip','R3c3Zip']: args += ['-' + flag, str(source)]
            p = subprocess.run(args, capture_output=True, timeout=30)
            calls = [json.loads(s) for s in (root / 'calls').read_text().splitlines()] if (root / 'calls').exists() else []
            self.assertEqual('unchanged', source.read_text())
            if existing:
                self.assertNotEqual(0, p.returncode); self.assertEqual([], calls); return
            self.assertEqual(['--self-test'], calls[0])
            self.assertEqual(self_exit or run_exit, p.returncode, p.stderr)
            self.assertEqual(1 if self_exit else 2, len(calls))
            if not self_exit:
                self.assertEqual(['--generator',str(source),'--r2',str(source),'--b2',str(source),'--b3',str(source),'--c3',str(source),'--output-dir',str(output)], calls[1])

    def test_self_test_first_and_statuses(self):
        for shell in SHELLS:
            for first, second in [(0,0),(17,0),(0,23)]:
                with self.subTest(shell=shell, self_exit=first, run_exit=second):
                    self.exercise(shell, first, second)

    def test_existing_output_stops_before_execution(self):
        for shell in SHELLS:
            with self.subTest(shell=shell): self.exercise(shell, existing=True)
