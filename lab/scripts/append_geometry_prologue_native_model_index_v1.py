"""Append the reviewed game transcript to frozen indices;no job replay or reread."""
import json
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha

def main():
 review=read(V/'local-geometry-prologue-native-reviewed-v1-current.json');source=Path(review['directory'])/'prompts-and-responses.txt';stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');results=[]
 for root in [ROOT,P/'workbench']:
  pointer=root/'verification/current-model-work-index-v4-current.json';old=read(pointer);old_report=Path(old['report']);old_list=Path(old['source_list_snapshot']);assert sha(old_report)==old['report_sha256']and sha(old_list)==old['source_list_sha256']
  # Saved indices are copied byte-for-byte. No referenced unrelated job is read.
  source_path=source if root==ROOT else root/source.relative_to(ROOT);assert sha(source_path)==sha(source)
  config=root/'config/current-model-work-sources.json';sources=read(config);entry=['local-geometry-prologue-native-reviewed-v1-current.json','BIWN170A0: corrected local prologue passes host512+19/native512/scene772/copied SDK;unpromoted']
  if entry not in sources:sources.append(entry);save(config,sources)
  out=root/'reports/model-work-index'/stamp;out.mkdir(parents=True);report=out/'prompts-and-responses.txt';report.write_bytes(old_report.read_bytes()+b'\n\n'+('BIWN170A0 — one corrected local prologue verified as a mixed-source component, no training\nExact source: '+str(source_path)+'\n\n').encode()+source_path.read_bytes());save(out/'source-list.json',sources)
  item=dict(kind='saved_role_transcript',path=str(source_path),sha256=sha(source_path),protocol=str(root/'verification/local-geometry-prologue-native-reviewed-v1-current.json'),protocol_status=review['status'],actual_generations_in_this_transcript=1,model_generation_replayed=False)
  files=old['files']+[item];new=dict(old,recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),report=str(report),report_sha256=sha(report),source_list_snapshot=str(out/'source-list.json'),source_list_sha256=sha(out/'source-list.json'),saved_prompt_or_transcript_records=len(files),files=files,new_inference=False,native_Chat=False,previous_index_preserved=True)
  save(out/'manifest.json',new);save(pointer,new);results.append(dict(root=str(root),before=old['saved_prompt_or_transcript_records'],after=len(files),report=str(report),report_sha256=sha(report)))
 save(V/'geometry-prologue-native-model-index-append-current.json',dict(status='terminal_frozen_Root_and_copied_indices_appended_without_job_replay',results=results,new_predictions=0,new_training=False))
 print([(x['before'],x['after'])for x in results],flush=True)
if __name__=='__main__':main()
