"""Byte/proof-linked wholefunction training candidates,no splits/truncation/weights."""
import json,hashlib,re
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];RESTORE=ROOT/'projects/black-ice-white-noise/restoration';sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 mp=Path(json.loads((ROOT/'verification/main_CPU_execution_coverage-current.json').read_text())['static_manifest']);manifest=json.loads(mp.read_text());by_pc={int(r['address'],16):r for r in manifest['instructions']};snapshot=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();six=json.loads((ROOT/'verification/local-six-function-scene-integration-current.json').read_text());seven=json.loads((ROOT/'verification/seven-function-scene-GPU-current.json').read_text());rows=[]
 specs=[('scene_caller','source','local-global-scene-author-current.json',0x11ad4),('animation_tick','tick_source','local-global-animation-checks-current.json',0x10ba4),('slot_clear','slot_source','local-slot-clear-checks-current.json',0x10968),('slot_prepare','prepare_source','local-scene-slot-prepare-checks-current.json',0x11384),('coordinates','face_source','local-face-coordinates-checks-current.json',0x110d4),('slot_expand','expand_source','local-scene-slots-expand-checks-current.json',0x1142e)]
 for name,key,file,entry in specs:
  witness=json.loads((ROOT/'verification'/file).read_text());evidence=json.loads((Path(witness['directory'])/'evidence.json').read_text());source=Path(six[key]);assert sha(source.read_bytes())==seven['source_sha256'][str(source)];rows.append((name,entry,source,evidence,ROOT/'verification/seven-function-scene-GPU-current.json',seven['scope']))
 overlay=json.loads((ROOT/'verification/local-debug-overlay-checks-current.json').read_text());evidence=json.loads((Path(overlay['directory'])/'evidence.json').read_text());source=RESTORE/'biwn_debug_overlay.c';assert sha(source.read_bytes())==seven['source_sha256'][str(source)];rows.append(('debug_overlay',0x10734,source,evidence,ROOT/'verification/seven-function-scene-GPU-current.json',seven['scope']))
 for name,entry,source_name,proof_name,author_name in [('record_insert',0x11762,'biwn_scene_record_insert.c','local-scene-record-insert-checks-current.json','local-scene-record-insert-author-current.json'),('scene_initialize',0x10990,'biwn_scene_initial_setup.c','local-scene-initial-setup-devices-checks-current.json','local-scene-initial-setup-author-current.json'),('scene_select',0x10a6a,'biwn_scene_select.c','local-scene-select-checks-current.json','local-scene-select-author-current.json'),('frame_release',0x1ae88,'biwn_frame_reference_release.c','local-frame-reference-release-checks-current.json','local-frame-reference-release-author-current.json'),('frame_acquire',0x1ac68,'biwn_frame_resource_acquire.c','local-frame-resource-acquire-checks-current.json','local-frame-resource-acquire-author-current.json'),('scene_devices',0x18160,'biwn_scene_device_initialize.c','local-scene-device-initialize-checks-current.json','local-scene-device-initialize-author-current.json')]:
  proof_path=ROOT/'verification'/proof_name;proof=json.loads(proof_path.read_text());author=json.loads((ROOT/'verification'/author_name).read_text());evidence=json.loads((Path(author['directory'])/'evidence.json').read_text());source=RESTORE/source_name;digest=sha(source.read_bytes());expected=proof['source_sha256']
  if isinstance(expected,dict):assert digest in expected.values()
  else:assert digest==expected
  rows.append((name,entry,source,evidence,proof_path,proof['scope']))
 out=ROOT/'training/game'/('proof-mapped-functions-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir(parents=True);records=[];all_pcs=set()
 for name,entry,source,evidence,proof_path,scope in rows:
  pcs=[int(x,16)for x in re.findall(r'^([0-9a-fA-F]{4,8}):',evidence['assembly'],re.M)];assert entry in pcs
  instructions=[]
  for pc in pcs:
   row=by_pc[pc];assert snapshot[pc:pc+row['size']]==bytes.fromhex(row['bytes']);instructions.append(row)
  all_pcs.update(pcs);headers={}
  def visit(file):
   for include in re.findall(r'^\s*#\s*include\s*"([^"]+)"',file.read_text(),re.M):
    p=next((p.resolve()for p in [file.parent/include,RESTORE/include]if p.is_file()),None);assert p is not None,include
    if str(p)in headers:continue
    headers[str(p)]=dict(sha256=sha(p.read_bytes()),text=p.read_text());visit(p)
  visit(source)
  record=dict(id=name,original_entry=hex(entry),instruction_addresses=len(pcs),instructions=instructions,assembly=evidence['assembly'],source=str(source),source_sha256=sha(source.read_bytes()),complete_source=source.read_text(),headers=headers,contract=evidence.get('contract'),proof=str(proof_path),proof_sha256=sha(proof_path.read_bytes()),proof_scope=scope,symbol_names='Analyst names,not recoveredoriginal symbols',training_ready=False,review_required=['Family grouping and nearclone separation before splitting','Token preflight; whole targets must not be truncated','Review original instruction boundary/contract and helper/privateframe limits'])
  records.append(record);(out/(name+'.json')).write_text(json.dumps(record,indent=2)+'\n')
 (out/'records.jsonl').write_text('\n'.join(json.dumps(x)for x in records)+'\n');report=dict(status='thirteen_byte_and_proof_mapped_training_candidates',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),functions=len(records),unique_original_instruction_addresses=len(all_pcs),source_manifest_sha256=sha(mp.read_bytes()),snapshot_sha256=sha(snapshot),records_sha256=sha((out/'records.jsonl').read_bytes()),training_ready=False,weights_trained=False,split_created=False,scope='Thirteen complete accepted portableC bundles paired with exact original bytes/listings,recursiveheaders,proofhashes and explicit proof limits. No automaticlabels/splits,wholegame readiness,newweights or independentgeneralization claim. Acquisition173instruction body now accepted; nested loader remains a fixture.')
 (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/proof-mapped-training-functions-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(records),len(all_pcs))
if __name__=='__main__':main()
