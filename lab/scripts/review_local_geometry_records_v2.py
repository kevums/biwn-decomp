"""Freeze the compact Author's actual truncation and corrected workflow outcome."""
import shutil
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha

def main():
 p=V/'local-geometry-records-source-v2-current.json';r=read(p);assert r['status']=='terminal_local_records_v2_truncated_no_redundant_repair' and r['new_predictions']==1
 folder=Path(r['directory']);d=folder/'Author_Compact';response=read(d/'inference.json');feedback=read(d/'feedback.json');assert feedback['diagnostic']['kind']=='incomplete_generation' and response['usage']['completion_tokens']==6499
 assert not(d/'host-gate').exists() and not(d/'model-body.inc').exists() and not(folder/'Repair_Compact').exists()
 out=V/'local-geometry-records-reviewed-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 deps={str(p):sha(p),str(Path(__file__)):sha(__file__)}
 for f in folder.rglob('*'):
  if f.is_file():deps[str(f)]=sha(f)
 transcript=out/'prompts-and-responses.txt';shutil.copy2(folder/'prompts-and-responses.txt',transcript)
 report=ROOT/'reports/BIWN Compact Geometry Author Review.txt'
 report.write_text('BIWN — compact local Author\n\nOne actual local copied27B prediction completed in '+str(response['seconds'])+' seconds and6499tokens under a6500token cap. Output remained incomplete. The v2parser correctly classified incomplete_generation before signature checks. No Repair was run,no complete C candidate compiled,and no source installed. Zero optimizer updates.\n\nStatic output also ignores returned shifts and substitutes D-register slots for A-register slots despite explicit instructions. Those are source observations,not compiled test counterexamples. The next development task is a22-instruction prologue with explicit register mapping and a bounded output budget. No general model-quality or training-gain claim.\n\nExact prompt and response: '+str(transcript)+'\n')
 facts=dict(status='terminal_compact_local_Author_truncated_correctly_classified_no_redundant_Repair',directory=str(out),report=str(report),original_run_directory=str(folder),model_identifier=r['model_identifier'],actual_predictions=1,seconds=response['seconds'],output_tokens=6499,accepted_complete_functions=0,compiled_candidates=0,host_verified=False,native_verified=False,repair_run=False,truncation_correctly_classified=True,new_training=False,optimizer_updates=0,model_source_installed=False,native_Chat_verified=False,coordinator_target_body_supplied=False,primitive_scaffolding_supplied=True,development_task=True,held_out_benchmark=False,source_sha256=deps)
 save(out/'review.json',facts);shutil.copy2(report,out/report.name);save(V/'local-geometry-records-reviewed-v2-current.json',facts)
 for path in [*map(Path,deps),transcript,out/'review.json',report,out/report.name,V/'local-geometry-records-reviewed-v2-current.json']:
  if path.is_relative_to(ROOT):
   dest=P/'workbench'/path.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest)
 print(facts['status'],flush=True)
if __name__=='__main__':main()
