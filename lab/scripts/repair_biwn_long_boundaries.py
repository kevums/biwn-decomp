"""Resolve three stable observed CPU starts conflicting with Ghidra data."""
from datetime import datetime,timezone
import json
from pathlib import Path
import shutil
import extract_biwn_stage as stage
from extend_biwn_observed_disassembly import tree_hash,save
from extend_biwn_long_observations import headless


def main():
    root=stage.ROOT;session=Path(json.loads((root/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    prior=json.loads((session/'long-observed-disassembly-summary.json').read_text());source=Path(prior['directory'])
    for name,digest in prior['artifact_sha256'].items():assert stage.cdi_layout.sha(source/name)==digest
    before=tree_hash(source/'projects');manifest=json.loads((source/'export/manifest.json').read_text())
    original_plan=json.loads((source/'instruction-plan.json').read_text());selected={0x1851e,0x18522,0x18526}
    seeds=[row for row in original_plan['seeds']if row['address']in selected]
    assert len(seeds)==3 and sum(row['size']for row in seeds)==14
    for row in seeds:assert all(int(o['history_slot_observations'])>=2 and o['post_frame_bytes_changed']=='0'for o in row['observations'])
    known={int(i['address'],16):i for i in manifest['instructions']}
    assert all(not(set(range(pc,pc+row['size']))&set(range(0x1851e,0x1852c)))for pc,row in known.items())
    out=session/('long-observed-data-repair-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir()
    plan={'stage_sha256':stage.STAGE_SHA,'start':0x1851e,'end_inclusive':0x1852b,'seeds':seeds,'source':str(source),
          'scope':'Three contiguous stable twice-sampled CPU boundaries conflict with data/undefined-unit classification; no retained instruction overlaps.'}
    save(out/'plan.json',plan);projects=out/'projects';shutil.copytree(source/'projects',projects);export=out/'export';export.mkdir()
    headless(out,projects,'repair',['-postScript','RepairBiwnObservedData.java',str(out/'plan.json'),str(out/'reclassified.json'),'-postScript','ExportDecomp.java',str(export)])
    assert (out/'reclassified.json').is_file(),'Repair report absent; inspect retained log'
    after=json.loads((export/'manifest.json').read_text());assert not after['cancelled']
    new={int(i['address'],16):i for i in after['instructions']}
    for pc,row in known.items():assert new[pc]==row
    assert set(new)-set(known)==selected
    assert after['functions']==manifest['functions'],'Function metadata changed unexpectedly'
    assert tree_hash(source/'projects')==before
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'three_observed_data_conflicts_reclassified',
            'directory':str(out),'source':str(source),'stage_sha256':stage.STAGE_SHA,
            'reclassified_interval':'[0x1851e,0x1852c)','reclassified_bytes':14,'new_instructions':3,
            'total_new_instructions_since_18225':prior['new_instructions']+3,'instructions_total':len(new),'function_count':len(after['functions']),
            'long_stable_sampled_PCs_missing_after':prior['missing_after']-3,'old_instruction_rows_unchanged':True,'baseline_project_unchanged':True,
            'reclassification':json.loads((out/'reclassified.json').read_text()),
            'artifact_sha256':{str(p.relative_to(out)):stage.cdi_layout.sha(p)for p in [out/'plan.json',out/'reclassified.json',export/'manifest.json',export/'listing.asm',export/'decompiled.c']},
            'scope':'Observed instruction boundaries in separate copy, not recovered original names/ABI, full CPU coverage, executable reconstruction or hardware verification.'}
    save(out/'review.json',report);save(session/'long-observed-data-repair-summary.json',report)
    print(json.dumps({k:report[k]for k in ['directory','instructions_total','function_count','long_stable_sampled_PCs_missing_after']}),flush=True)


if __name__=='__main__':main()
