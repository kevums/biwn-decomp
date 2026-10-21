"""Add sampled CPU instruction starts in a separate copy of the static project."""
import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time
from collections import Counter
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
import extract_biwn_stage as stage


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def tree_hash(folder):
    return {str(p.relative_to(folder)): stage.cdi_layout.sha(p)
            for p in folder.rglob('*') if p.is_file()}


def main():
    root = stage.ROOT
    session = Path(json.loads((root / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    image = (session / 'nextstage-68000-candidate.bin').read_bytes()
    assert stage.digest(image) == stage.STAGE_SHA
    baseline = json.loads((session / 'nextstage-divu-export/manifest.json').read_text())
    known = {int(x['address'],16): x for x in baseline['instructions']}
    occupied = {address+i for address,row in known.items() for i in range(row['size'])}
    observer = json.loads((session / 'emulator-runtime/pc-observer-summary.json').read_text())
    assert observer['stage_sha256'] == stage.STAGE_SHA and observer['inputs_and_core_unchanged']
    matching = {}
    input_hashes = {}
    for run in observer['runs']:
        if run['name'] not in ['hle','hle-input']: continue
        path = Path(run['cwd']) / 'observed_pcs.csv'
        digest = stage.cdi_layout.sha(path)
        assert digest == run['artifact_sha256'][path.name]
        input_hashes[str(path)] = digest
        for row in csv.DictReader(path.open()):
            pc = int(row['pc'],16); offset = pc-0x4000
            if offset < 0 or offset+16 > len(image): continue
            if image[offset:offset+16].hex() != row['first_post_frame_bytes']: continue
            if int(row['post_frame_bytes_changed']): continue
            matching.setdefault(pc,[]).append({'run':run['name'],**row})
    missing = sorted(set(matching)-set(known))
    decoder = Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    seeds, excluded = [], []
    selected_bytes = set()
    for pc in missing:
        decoded = list(decoder.disasm(image[pc-0x4000:pc-0x4000+16],pc,count=1)) if pc%2==0 else []
        if not decoded or decoded[0].mnemonic in ['dc.w','invalid']:
            excluded.append({'address':hex(pc),'reason':'not a complete supported M68000 instruction within sixteen captured bytes'});continue
        instruction = decoded[0]; interval=set(range(pc,pc+instruction.size))
        if interval & (occupied|selected_bytes):
            excluded.append({'address':hex(pc),'reason':'overlaps another retained instruction'});continue
        selected_bytes |= interval
        seeds.append({'address':pc,'size':instruction.size,'bytes':instruction.bytes.hex(),
                      'Capstone_assembly':instruction.mnemonic+' '+instruction.op_str,
                      'observations':matching[pc]})
    out = session / ('observed-disassembly-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    out.mkdir()
    plan = {'time':datetime.now(timezone.utc).isoformat(),'stage_sha256':stage.STAGE_SHA,
            'baseline_manifest_sha256':stage.cdi_layout.sha(session/'nextstage-divu-export/manifest.json'),
            'observed_input_hashes':input_hashes,'matching_sampled_PCs':len(matching),
            'missing_instruction_starts':len(missing),'seeds':seeds,'excluded':excluded,
            'scope':'First post-frame sixteen bytes stable/matching; selected M68000 boundaries only. Not instruction-time RAM or function proof.'}
    save(out/'plan.json',plan)
    source = session/'nextstage-divu-projects'
    before = tree_hash(source)
    projects=out/'projects';shutil.copytree(source,projects)
    export=out/'export';export.mkdir()
    command=[str(root/'ghidra-headless'),str(projects),'BIWN23-divu-candidate',
             '-process','nextstage-68000-candidate.bin','-noanalysis',
             '-scriptPath',str(root/'scripts'),'-postScript','AddBiwnObservedInstructions.java',
             str(out/'plan.json'),str(out/'added-instructions.json'),
             '-postScript','ExportDecomp.java',str(export),'-max-cpu','4']
    started=time.monotonic()
    status={'status':'starting','command':command,'output':str(out),'started_at':datetime.now(timezone.utc).isoformat()}
    with (out/'ghidra.log').open('w') as log:
        process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        status.update(status='running',pid=process.pid);save(out/'status.json',status)
        print(json.dumps({'pid':process.pid,'output':str(out),'seeds':len(seeds),'excluded':len(excluded)}),flush=True)
        try:process.wait(timeout=180)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid,signal.SIGTERM)
            try:process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid,signal.SIGKILL);process.wait()
            status['wall_budget_expired']=True
    status.update(status='terminal',exit_code=process.returncode,seconds=round(time.monotonic()-started,3))
    save(out/'status.json',status)
    assert tree_hash(source)==before,'Source project changed'
    assert process.returncode==0, 'Headless export failed; inspect retained log'
    if not (out/'added-instructions.json').exists():
        status['validation']='failed: script report absent, even if headless process returned0'
        save(out/'status.json',status)
        raise ValueError('Instruction script did not complete; inspect retained log')
    added=json.loads((out/'added-instructions.json').read_text())
    after=json.loads((export/'manifest.json').read_text())
    assert not after['cancelled'] and after['functions']==baseline['functions']
    new={int(x['address'],16):x for x in after['instructions']}
    for pc,row in known.items(): assert new[pc]==row,'Retained instruction changed'
    actual=set(new)-set(known)
    expected={int(x['address'],16) for x in added['results'] if x['status']=='decoded_exact_observed_instruction'}
    assert actual==expected,'Unexpected extra disassembly'
    for pc in actual:
        row=new[pc]; decoded=next(decoder.disasm(image[pc-0x4000:pc-0x4000+16],pc,count=1))
        assert row['size']==decoded.size and row['bytes']==decoded.bytes.hex()
    report={'time':datetime.now(timezone.utc).isoformat(),'status':'separate_observed_instruction_export_checked',
            'directory':str(out),'stage_sha256':stage.STAGE_SHA,'baseline_instructions':len(known),
            'matching_sampled_PCs':len(matching),'sampled_PCs_missing_before':len(missing),
            'new_instructions':len(actual),'instructions_total':len(new),'functions_unchanged':len(after['functions']),
            'sampled_PCs_missing_after':len(set(matching)-set(new)),
            'seed_results':dict(Counter(x['status'] for x in added['results'])), 'excluded':excluded,
            'baseline_project_unchanged':True,'baseline_export_unchanged':stage.cdi_layout.sha(session/'nextstage-divu-export/manifest.json')==plan['baseline_manifest_sha256'],
            'artifact_sha256':{str(p.relative_to(out)):stage.cdi_layout.sha(p) for p in [out/'plan.json',out/'added-instructions.json',export/'manifest.json',export/'listing.asm',export/'decompiled.c']},
            'scope':'Observed instruction starts only; original functions retained, no functions inferred or C behavior validated. Sixteen-byte post-frame matches are not per-instruction capture, complete coverage or hardware proof.'}
    save(out/'review.json',report);save(session/'observed-disassembly-summary.json',report)
    print(json.dumps(report),flush=True)


if __name__=='__main__': main()
