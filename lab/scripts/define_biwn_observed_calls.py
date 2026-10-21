"""Create direct-call entry candidates in another preserved project copy."""
from datetime import datetime, timezone
import csv
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
import extract_biwn_stage as stage
from extend_biwn_observed_disassembly import tree_hash,save


def main():
    root=stage.ROOT
    session=Path(json.loads((root/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    prior=json.loads((session/'observed-disassembly-summary.json').read_text())
    source=Path(prior['directory']); before=tree_hash(source/'projects')
    for name,digest in prior['artifact_sha256'].items():assert stage.cdi_layout.sha(source/name)==digest
    image=(session/'nextstage-68000-candidate.bin').read_bytes();assert stage.digest(image)==stage.STAGE_SHA
    manifest=json.loads((source/'export/manifest.json').read_text())
    entries={int(f['address'],16) for f in manifest['functions']}
    observed=set()
    observer=json.loads((session/'emulator-runtime/pc-observer-summary.json').read_text())
    for run in observer['runs']:
        if run['name'] not in ['hle','hle-input']:continue
        path=Path(run['cwd'])/'observed_pcs.csv'
        assert stage.cdi_layout.sha(path)==run['artifact_sha256'][path.name]
        for row in csv.DictReader(path.open()):
            address=int(row['pc'],16);offset=address-0x4000
            if offset>=0 and image[offset:offset+16].hex()==row['first_post_frame_bytes'] and not int(row['post_frame_bytes_changed']):
                observed.add(address)
    calls={};decoder=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    for row in manifest['instructions']:
        pc=int(row['address'],16)
        if pc not in observed:continue
        instruction=next(decoder.disasm(bytes.fromhex(row['bytes'])+bytes(32),pc,count=1))
        assert instruction.size==row['size']
        if instruction.mnemonic not in ['jsr','bsr.b','bsr.w']:continue
        match=re.fullmatch(r'\$([0-9a-f]+)(?:\.[lw])?',instruction.op_str)
        if not match:continue
        target=int(match[1],16)
        if target in observed and target not in entries:
            calls.setdefault(target,[]).append({'from':hex(pc),'bytes':row['bytes'],
                                                'assembly':instruction.mnemonic+' '+instruction.op_str})
    candidates=[{'address':a,'calls':c} for a,c in sorted(calls.items())]
    out=session/('observed-call-entries-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir()
    save(out/'plan.json',{'stage_sha256':stage.STAGE_SHA,'source':str(source),'candidates':candidates,
                          'scope':'Stable first-post-frame bytes at direct call sites/targets; does not prove exact instruction-time RAM or original function boundaries.'})
    projects=out/'projects';shutil.copytree(source/'projects',projects);export=out/'export';export.mkdir()
    command=[str(root/'ghidra-headless'),str(projects),'BIWN23-divu-candidate',
             '-process','nextstage-68000-candidate.bin','-noanalysis','-scriptPath',str(root/'scripts'),
             '-postScript','DefineBiwnObservedCalls.java',str(out/'plan.json'),str(out/'entries.json'),
             '-postScript','ExportDecomp.java',str(export),'-max-cpu','4']
    status={'command':command,'status':'starting','started_at':datetime.now(timezone.utc).isoformat()};start=time.monotonic()
    with (out/'ghidra.log').open('w') as log:
        process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        status.update(status='running',pid=process.pid);save(out/'status.json',status)
        print(json.dumps({'pid':process.pid,'candidates':len(candidates),'output':str(out)}),flush=True)
        try:process.wait(timeout=180)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid,signal.SIGTERM)
            try:process.wait(timeout=5)
            except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
            status['wall_budget_expired']=True
    status.update(status='terminal',exit_code=process.returncode,seconds=round(time.monotonic()-start,3));save(out/'status.json',status)
    assert tree_hash(source/'projects')==before,'Source project changed'
    assert process.returncode==0 and (out/'entries.json').exists(),'Script did not complete; inspect retained log'
    after=json.loads((export/'manifest.json').read_text());assert not after['cancelled']
    assert after['instructions']==manifest['instructions'],'Instruction export changed'
    old={f['address']:f for f in manifest['functions']};new={f['address']:f for f in after['functions']}
    assert all(new[k]==v for k,v in old.items()),'Existing function status changed'
    rows=json.loads((out/'entries.json').read_text())['results']
    created={int(row['address'],16) for row in rows if row['status']=='created_direct_call_entry_candidate'}
    assert {int(k,16) for k in set(new)-set(old)}==created
    report={'time':datetime.now(timezone.utc).isoformat(),'status':'direct_call_entry_candidates_exported',
            'directory':str(out),'stage_sha256':stage.STAGE_SHA,'candidates':len(candidates),
            'created':len(created),'results':rows,'function_count':len(new),
            'decompiled_functions':sum(f['decompiled'] for f in new.values()),
            'instructions_unchanged':len(after['instructions']),'source_project_unchanged':True,
            'new_function_status':[f for k,f in new.items() if k not in old],
            'artifact_sha256':{str(p.relative_to(out)):stage.cdi_layout.sha(p) for p in [out/'plan.json',out/'entries.json',export/'manifest.json',export/'decompiled.c',export/'listing.asm']},
            'scope':'Entry candidates supported by direct calls and sampled PCs. Bodies and C remain approximations, not original symbols/compiler ABI or validated reconstructed game.'}
    save(out/'review.json',report);save(session/'observed-call-entries-summary.json',report)
    print(json.dumps(report),flush=True)


if __name__=='__main__':main()
