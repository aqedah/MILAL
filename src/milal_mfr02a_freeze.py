"""Isolated human serialization before any historical source is loaded."""
import encodings.cp437
import json
import os
import sys
import zipfile
from pathlib import Path
import milal_mfr_common as cm
import milal_mfr02a_core as core


def guard(allowed, output):
    allowed = {str(Path(p).resolve()).casefold() for p in allowed}
    base = str(Path(output).resolve()).casefold() + os.sep
    trace = []
    def hook(event, args):
        if event == 'import' and args[0].startswith('milal_'):
            cm.require(args[0] in ('milal_mfr_common', 'milal_mfr02a_core'), 'Historical import before freeze')
        if event != 'open' or isinstance(args[0], int):return
        path = str(Path(os.fsdecode(args[0])).resolve()).casefold()
        mode, flags = args[1:3]
        writing = isinstance(mode, str) and any(c in mode for c in 'wax+') or isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT)
        cm.require(path.startswith(base) if writing else path in allowed, 'Human freeze read/write boundary violation')
        if not writing:trace.append(path)
    cm.require(not any(n.startswith('milal_') and n not in ('milal_mfr_common', 'milal_mfr02a_core', 'milal_mfr02a_freeze') for n in sys.modules), 'Pre-freeze module leakage')
    sys.addaudithook(hook)
    return trace


def run(projected, supplied_path, output):
    output = Path(output).resolve()
    cm.require(not output.exists(), 'Append-only: output already exists')
    output.mkdir(parents=True)
    allowed = [Path(projected).resolve(), Path(supplied_path).resolve()]
    trace = guard(allowed, output)
    supplied = json.loads(Path(supplied_path).read_bytes())
    with zipfile.ZipFile(projected) as z:
        h1 = cm.rows(z.read('13_h1_hierarchy_review_set.csv'))
        attachments = {h['configuration_case_id']: json.loads(z.read('case_evidence/' + h['configuration_case_id'] + '.json')) for h in h1}
    o = core.assemble(supplied, h1, attachments)
    for name, key in zip(core.FREEZE_FILES[:6], ('decisions', 'provenance', 'crosswalk', 'calibration', 'deferred', 'accepted')):
        cm.write(output/name, cm.csv_bytes(o[key]))
    cm.write(output/core.FREEZE_FILES[6], cm.js(o['representation']))
    manifest = [dict(path=n, sha256=cm.sha(cm.csv_bytes(o[k])) if k != 'representation' else cm.sha(cm.js(o[k]))) for n, k in zip(core.FREEZE_FILES, ('decisions', 'provenance', 'crosswalk', 'calibration', 'deferred', 'accepted', 'representation'))]
    cm.write(output/'14_human_decision_freeze.csv', cm.csv_bytes(manifest))
    cm.write(output/'15_freeze_read_receipt.json', cm.js(dict(event='HUMAN_DECISIONS_FROZEN',
        logical_members=['13_h1_hierarchy_review_set.csv'] + ['case_evidence/' + h['configuration_case_id'] + '.json' for h in h1],
        readset_valid=set(trace) == {str(p).casefold() for p in allowed},
        allowed_input_roles=['EXACT_H1_PROJECTION', 'RESEARCHER_DECISIONS'], historical_sources_loaded=False)))


if __name__ == '__main__':
    run(*sys.argv[1:])
