"""Snapshot strengthened connected startup proof and preserve historical reports."""
from pathlib import Path
from datetime import datetime,timezone
import json,shutil,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def main():
 session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);validation=read(session/'boot-slice-validation.json');old=validation['render_services_startup_pipeline'];linked=read(ROOT/'verification/biwn-render-services-runtime-checks.json');standalone=read(ROOT/'verification/biwn-startup-services-checks.json')
 assert validation['portable_C_component_count']==77
 assert linked['cases']==144 and linked['created_task_calls']==2448 and linked['startup_service_instruction_coverage']==[210,210]and linked['scene_call_boundary_cases']>0 and linked['C_sprite_decodes']==0
 for key in ['startup_top_level_bodies_reconstructed','startup_nested_dependencies_fully_reconstructed','startup_MMIO_video_words_compared','sprite_queue_reset_by_original_EA20','animation_producers_executed','matched','limits']:linked[key]=old[key]
 linked['matched'].append(f"All 210 startup-service instructions execute in the connected test. Actual emulated input polling runs in 144 cases; {linked['scene_call_boundary_cases']} take the bit-zero scene-call boundary, whose body remains explicitly scripted. Four emulated video words and full startup CPU compare.")
 save(ROOT/'verification/biwn-render-services-runtime-checks.json',linked);save(Path(linked['directory'])/'report.json',linked)
 validation['render_services_startup_pipeline']=linked;validation['latest_aggregate_update']=datetime.now(timezone.utc).isoformat();save(session/'boot-slice-validation.json',validation)
 for proof,checker in [(standalone,'check_biwn_startup_services.py'),(linked,'check_biwn_render_services_runtime.py')]:
  out=Path(proof['directory']);assert read(out/'status.json')['status']=='terminal_pass';snap=out/'harness-snapshot';snap.mkdir(exist_ok=True);manifest={}
  sources=[ROOT/'scripts'/checker,ROOT/'scripts/check_biwn_startup_services.py',ROOT/'scripts/check_biwn_render_display_runtime.py',ROOT/'scripts/check_biwn_rng.py',ROOT/'scripts/emulated_pad_input.py',ROOT/'animation_renderer.py']+[ROOT/'projects/black-ice-white-noise/restoration'/n for n in proof['source_sha256']]
  for src in sources:shutil.copy2(src,snap/src.name);manifest[src.name]=hashlib.sha256(src.read_bytes()).hexdigest()
  save(snap/'manifest.json',manifest)
 shutil.copy2(Path(linked['directory'])/'librender-services.dylib',ROOT/'tools/libbiwn-render-services.dylib')
 for script in ['summarize_biwn_checks.py','install_chat_runtime.py','check_startup_services_mcp.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/script)],check=True)
 print(json.dumps({'components':77,'connected_startup_instructions':[210,210],'scene_boundaries':linked['scene_call_boundary_cases']}))
if __name__=='__main__':main()
