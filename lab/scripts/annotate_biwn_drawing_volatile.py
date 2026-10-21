"""Preserve original drawing-word store order in a separate Ghidra copy."""
from datetime import datetime,timezone
import json
from pathlib import Path
import shutil
import extract_biwn_stage as stage
from extend_biwn_observed_disassembly import tree_hash,save
from extend_biwn_long_observations import headless
from annotate_biwn_shared_volatile import function


def main():
    root=stage.ROOT;session=Path(json.loads((root/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    prior=json.loads((session/'long-observed-data-repair-summary.json').read_text());source=Path(prior['directory'])
    for name,digest in prior['artifact_sha256'].items():assert stage.cdi_layout.sha(source/name)==digest
    before=tree_hash(source/'projects');manifest=json.loads((source/'export/manifest.json').read_text())
    out=session/('drawing-volatile-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir();projects=out/'projects';shutil.copytree(source/'projects',projects);export=out/'export';export.mkdir()
    headless(out,projects,'drawing-volatile',['-postScript','AnnotateBiwnDrawingVolatile.java',str(out/'annotation.json'),'-postScript','ExportDecomp.java',str(export)])
    assert (out/'annotation.json').is_file(),'Annotation report absent; inspect log'
    after=json.loads((export/'manifest.json').read_text());assert not after['cancelled']
    assert [(i['address'],i['size'],i['bytes'])for i in after['instructions']]==[(i['address'],i['size'],i['bytes'])for i in manifest['instructions']]
    assert [(f['address'],f['name'])for f in after['functions']]==[(f['address'],f['name'])for f in manifest['functions']]
    assert tree_hash(source/'projects')==before
    old_c=(source/'export/decompiled.c').read_text();new_c=(export/'decompiled.c').read_text();old_fn=function(old_c,'0001b786');new_fn=function(new_c,'0001b786')
    (out/'function-before.c').write_text(old_fn);(out/'function-after.c').write_text(new_fn)
    assert 'drawing_word_00f02200_candidate'in new_fn and 'drawing_word_00f02238_candidate'in new_fn
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'drawing_volatile_export_created_pending_order_review','directory':str(out),
            'stage_sha256':stage.STAGE_SHA,'source':str(source),'instructions_unchanged':len(after['instructions']),'function_entries_unchanged':len(after['functions']),
            'baseline_project_unchanged':True,'annotation':json.loads((out/'annotation.json').read_text()),'before_function':old_fn,'after_function':new_fn,
            'artifact_sha256':{name:stage.cdi_layout.sha(out/name)for name in ['annotation.json','export/manifest.json','export/listing.asm','export/decompiled.c','function-before.c','function-after.c']},
            'scope':'Separate decompiler annotation only. External words marked uninitialized/volatile to preserve possible sideeffects and ordering. No hardware register layout, device completion, original ABI or rendered-game equivalence claimed.'}
    save(out/'review.json',report);save(session/'drawing-volatile-summary.json',report)
    print(json.dumps({k:report[k]for k in ['directory','instructions_unchanged','function_entries_unchanged']}),flush=True)


if __name__=='__main__':main()
