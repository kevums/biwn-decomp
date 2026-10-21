"""Test shared-word volatility in a separate preserved Ghidra project copy."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time
import extract_biwn_stage as stage
from extend_biwn_observed_disassembly import tree_hash, save


def function(text, address):
    begin = text.index('/* Address ' + address + ' */')
    end = text.find('/* Address ', begin + 1)
    return text[begin:end if end >= 0 else None]


def main():
    root = stage.ROOT
    session = Path(json.loads((root / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    prior = json.loads((session / 'observed-call-entries-summary.json').read_text())
    source = Path(prior['directory'])
    for name, digest in prior['artifact_sha256'].items(): assert stage.cdi_layout.sha(source / name) == digest
    before_hash = tree_hash(source / 'projects')
    manifest = json.loads((source / 'export/manifest.json').read_text())
    out = session / ('shared-volatile-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    out.mkdir()
    shutil.copytree(source / 'projects', out / 'projects')
    (out / 'export').mkdir()
    command = [str(root / 'ghidra-headless'), str(out / 'projects'), 'BIWN23-divu-candidate',
               '-process', 'nextstage-68000-candidate.bin', '-noanalysis', '-scriptPath', str(root / 'scripts'),
               '-postScript', 'AnnotateBiwnSharedVolatile.java', str(out / 'annotation.json'),
               '-postScript', 'ExportDecomp.java', str(out / 'export'), '-max-cpu', '4']
    status = {'command': command, 'status': 'starting', 'started_at': datetime.now(timezone.utc).isoformat()}
    started = time.monotonic()
    with (out / 'ghidra.log').open('w') as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        status.update(status='running', pid=process.pid)
        save(out / 'status.json', status)
        print(json.dumps({'pid': process.pid, 'output': str(out)}), flush=True)
        try: process.wait(timeout=180)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try: process.wait(timeout=5)
            except subprocess.TimeoutExpired: os.killpg(process.pid, signal.SIGKILL); process.wait()
            status['wall_budget_expired'] = True
    status.update(status='terminal', exit_code=process.returncode, seconds=round(time.monotonic() - started, 3))
    save(out / 'status.json', status)
    assert process.returncode == 0 and (out / 'annotation.json').exists(), 'Annotation script failed; inspect retained log'
    assert tree_hash(source / 'projects') == before_hash, 'Source project changed'
    after = json.loads((out / 'export/manifest.json').read_text())
    boundaries = lambda m: [(i['address'], i['size'], i['bytes']) for i in m['instructions']]
    assert boundaries(after) == boundaries(manifest), 'Instruction bytes/boundaries changed'
    entries = lambda m: [(f['address'], f['name']) for f in m['functions']]
    assert entries(after) == entries(manifest), 'Function entries/names changed'
    assert not after['cancelled'] and all(f['decompiled'] for f in after['functions'])
    old_c, new_c = (source / 'export/decompiled.c').read_text(), (out / 'export/decompiled.c').read_text()
    targets = ['0000e098', '0000e0a6', '0000e19e', '0000e202', '0000e220']
    samples = [{'address': address, 'before': function(old_c, address), 'after': function(new_c, address)} for address in targets]
    focus = next(row['after'] for row in samples if row['address'] == '0000e0a6')
    assert 'while( true )' not in focus and 'Removing unreachable block' not in focus
    assert focus.count('FUN_0000e098();') == 2, 'Initial/final polling-helper calls not retained'
    for address in ['00f03204', '00f0320c', '00f03210', '00f03214', '00f03218']:
        assert 'shared_word_' + address + '_candidate' in focus
    assert '0x4d80' in focus, 'Command/poll constant not retained'
    report = {'time': datetime.now(timezone.utc).isoformat(), 'status': 'volatile_annotation_preserves_observed_polling_in_C',
              'directory': str(out), 'stage_sha256': stage.STAGE_SHA,
              'instructions_unchanged': len(after['instructions']), 'function_entries_unchanged': len(after['functions']),
              'source_project_unchanged': True, 'annotation': json.loads((out / 'annotation.json').read_text()),
              'samples': samples, 'whole_export_warning_count_before': old_c.count('WARNING:'),
              'whole_export_warning_count_after': new_c.count('WARNING:'),
              'artifact_sha256': {name: stage.cdi_layout.sha(out / name) for name in ['annotation.json', 'export/manifest.json', 'export/decompiled.c', 'export/listing.asm']},
              'scope': 'Decompiler representation improvement only; neither device response, helper completion, whole-game behavior, inferred function bodies nor original ABI have been validated.'}
    save(out / 'review.json', report)
    save(session / 'shared-volatile-summary.json', report)
    print(json.dumps({k: report[k] for k in ['status', 'directory', 'instructions_unchanged', 'function_entries_unchanged']}), flush=True)


if __name__ == '__main__': main()
