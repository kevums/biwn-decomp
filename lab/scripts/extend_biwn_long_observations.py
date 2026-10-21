"""Add long-run stable sampled CPU boundaries/call entries in a project copy."""
from collections import Counter
import csv
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
import extract_biwn_stage as stage
from extend_biwn_observed_disassembly import tree_hash,save
sys.path.insert(0,str(stage.ROOT))
import binary_tools


def headless(out,projects,phase,scripts):
    command=[str(stage.ROOT/'ghidra-headless'),str(projects),'BIWN23-divu-candidate','-process','nextstage-68000-candidate.bin',
             '-noanalysis','-scriptPath',str(stage.ROOT/'scripts'),*scripts,'-max-cpu','4']
    status={'phase':phase,'command':command,'status':'starting','started_at':datetime.now(timezone.utc).isoformat()}
    started=time.monotonic()
    with (out/(phase+'.log')).open('w') as log:
        p=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        status.update(status='running',pid=p.pid);save(out/(phase+'-status.json'),status)
        print(phase,p.pid,'running',flush=True)
        try:p.wait(timeout=180)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid,signal.SIGTERM)
            try:p.wait(timeout=5)
            except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
            status['wall_budget_expired']=True
    status.update(status='terminal',exit_code=p.returncode,seconds=round(time.monotonic()-started,3));save(out/(phase+'-status.json'),status)
    assert p.returncode==0,'Headless process failed; inspect retained log'
    print(phase,'terminal',status['seconds'],flush=True)


def main():
    root=stage.ROOT;session=Path(json.loads((root/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    image=(session/'nextstage-68000-candidate.bin').read_bytes();assert stage.digest(image)==stage.STAGE_SHA
    prior=json.loads((session/'shared-volatile-summary.json').read_text());assert prior['stage_sha256']==stage.STAGE_SHA
    source=Path(prior['directory']);before=tree_hash(source/'projects')
    manifest_path=source/'export/manifest.json';manifest_hash=binary_tools.sha(manifest_path)
    baseline=json.loads(manifest_path.read_text());known={int(x['address'],16):x for x in baseline['instructions']}
    occupied={pc+i for pc,row in known.items()for i in range(row['size'])}
    raw=json.loads((session/'emulator-runtime/long-audio-current.json').read_text())
    assert raw['status']=='completed_pending_coordinator_review' and raw['inputs_core_original_observer_unchanged']
    assert raw['preflight900_exact_frame_command_DSP_watch_match']
    matching={};input_hashes={};unstable=[]
    for run in raw['runs']:
        if run['name']=='preflight900':continue
        p=Path(run['directory'])/'observed_CPU_pcs.csv'
        digest=binary_tools.sha(p);assert digest==run['artifact_sha256'][p.name];input_hashes[str(p)]=digest
        for row in csv.DictReader(p.open()):
            pc=int(row['pc'],16);offset=pc-0x4000
            if offset<0 or offset+16>len(image):continue
            if int(row['post_frame_bytes_changed']) or image[offset:offset+16].hex()!=row['first_post_frame_bytes']:
                unstable.append({'run':run['name'],**row});continue
            matching.setdefault(pc,[]).append({'run':run['name'],**row})
    missing=sorted(set(matching)-set(known));seeds=[];excluded=[];selected=set()
    for pc in missing:
        try:decoded,_=binary_tools.m68k_instructions(image[pc-0x4000:pc-0x4000+16],pc)
        except ValueError:
            # Use guarded one-instruction decode; remaining bytes may end mid-instruction.
            import capstone
            md=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
            ins=next(md.disasm(image[pc-0x4000:pc-0x4000+16]+bytes(32),pc,count=1),None)
            if not ins or ins.size>16:
                excluded.append({'address':hex(pc),'reason':'no complete first instruction in16captured bytes'});continue
            decoded,_=binary_tools.m68k_instructions(image[pc-0x4000:pc-0x4000+ins.size],pc)
        first=decoded[0]
        if first['classification']!='decoded_instruction':
            excluded.append({'address':hex(pc),'reason':'unrecognized original68000word'});continue
        interval=set(range(pc,pc+first['size']))
        if interval&(occupied|selected):
            excluded.append({'address':hex(pc),'reason':'overlaps retained/selected instruction; requires separate boundary review'});continue
        selected|=interval;seeds.append({'address':pc,'size':first['size'],'bytes':first['bytes'],'Capstone_assembly':first['assembly'],'observations':matching[pc]})
    out=session/('long-observed-disassembly-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir()
    save(out/'instruction-plan.json',{'stage_sha256':stage.STAGE_SHA,'baseline_manifest_sha256':manifest_hash,'source':str(source),
                                     'input_hashes':input_hashes,'seeds':seeds,'excluded':excluded,'unstable_or_different_first_bytes':unstable,
                                     'scope':'Stable matching first16postframe bytes at sampled CPU PCs, not instruction-time memory or complete coverage.'})
    projects=out/'projects';shutil.copytree(source/'projects',projects)
    first_export=out/'instructions-export';first_export.mkdir()
    headless(out,projects,'instructions',['-postScript','AddBiwnObservedInstructions.java',str(out/'instruction-plan.json'),str(out/'added-instructions.json'),
                                        '-postScript','ExportDecomp.java',str(first_export)])
    assert (out/'added-instructions.json').is_file(),'Post-script did not complete despite process status'
    after=json.loads((first_export/'manifest.json').read_text());assert not after['cancelled']
    added=json.loads((out/'added-instructions.json').read_text());new={int(x['address'],16):x for x in after['instructions']}
    for pc,row in known.items():assert new[pc]==row,'Retained original instruction changed'
    expected={int(x['address'],16)for x in added['results']if x['status']=='decoded_exact_observed_instruction'}
    assert set(new)-set(known)==expected
    assert {f['address']for f in after['functions']}=={f['address']for f in baseline['functions']}
    entries={int(f['address'],16)for f in after['functions']};calls={}
    for pc,row in new.items():
        if pc not in matching:continue
        decoded,_=binary_tools.m68k_instructions(bytes.fromhex(row['bytes']),pc);assembly=decoded[0]['assembly']
        match=re.fullmatch(r'(?:jsr|bsr\.[bw]) \$([0-9a-f]+)(?:\.[lw])?',assembly)
        if match:
            target=int(match[1],16)
            if target in matching and target not in entries:calls.setdefault(target,[]).append({'from':hex(pc),'bytes':row['bytes'],'assembly':assembly})
    candidates=[{'address':address,'calls':refs}for address,refs in sorted(calls.items())]
    save(out/'entry-plan.json',{'stage_sha256':stage.STAGE_SHA,'candidates':candidates,'scope':'Observed direct call and target support entry candidates; no original symbols/ABI/body proof.'})
    final_export=out/'export';final_export.mkdir()
    headless(out,projects,'entries',['-postScript','DefineBiwnObservedCalls.java',str(out/'entry-plan.json'),str(out/'entries.json'),
                                   '-postScript','ExportDecomp.java',str(final_export)])
    assert (out/'entries.json').is_file(),'Entry script report absent'
    final=json.loads((final_export/'manifest.json').read_text());assert not final['cancelled'] and final['instructions']==after['instructions']
    old_functions={f['address']:f for f in after['functions']};new_functions={f['address']:f for f in final['functions']}
    assert all(new_functions[k]==v for k,v in old_functions.items())
    entry_results=json.loads((out/'entries.json').read_text())['results']
    created={int(row['address'],16)for row in entry_results if row['status']=='created_direct_call_entry_candidate'}
    assert created=={int(k,16)for k in set(new_functions)-set(old_functions)}
    assert tree_hash(source/'projects')==before and binary_tools.sha(manifest_path)==manifest_hash
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'long_run_stable_boundaries_and_direct_calls_exported',
            'directory':str(out),'stage_sha256':stage.STAGE_SHA,'baseline':str(source),'baseline_instructions':len(known),
            'matching_stable_sampled_PCs':len(matching),'missing_before':len(missing),'new_instructions':len(expected),'instructions_total':len(new),
            'missing_after':len(set(matching)-set(new)),'instruction_seed_results':dict(Counter(x['status']for x in added['results'])),
            'boundary_exclusions':excluded,'entry_candidates':len(candidates),'created_entries':len(created),'entry_results':entry_results,
            'function_count':len(new_functions),'decompiled_functions':sum(f['decompiled']for f in final['functions']),
            'baseline_project_and_manifest_unchanged':True,'original_instruction_rows_retained':True,
            'artifact_sha256':{str(p.relative_to(out)):binary_tools.sha(p)for p in [out/'instruction-plan.json',out/'entry-plan.json',out/'added-instructions.json',out/'entries.json',final_export/'manifest.json',final_export/'listing.asm',final_export/'decompiled.c']},
            'scope':'Separate project retains earlier volatile GPU words. Added exact static bytes/boundaries and direct-call entry candidates only; C bodies, original function ABI, timing and rebuilt-game behavior remain unverified.'}
    save(out/'review.json',report);save(session/'long-observed-disassembly-summary.json',report)
    print(json.dumps({k:report[k]for k in ['directory','new_instructions','instructions_total','created_entries','function_count','missing_after','boundary_exclusions']}),flush=True)


if __name__=='__main__':main()
