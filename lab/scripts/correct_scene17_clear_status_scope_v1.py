"""Correct inherited scene status fields without changing immutable prior reviews."""
import shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic

def main():
    wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
    for p,h in w['dependencies_sha256'].items():assert sha(p)==h,p
    packet=read(w['packet']);scene=packet['native_scene_draw_progress'];assert scene['profile']=='deck-shared-v26-scene-clear'
    proof=read(V/'scene17-clear-final-bridge-v1-current.json');assert proof['completed']==772 and proof['original_clear_instructions_executed']==0
    out=V/'scene17-clear-status-scope-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    save(out/'previous-wrapper.json',w);save(out/'previous-status-packet.json',packet)
    scene.update(final_scene_cases=772,final_existing_alias_cases=256,final_geometry_alias_cases=128,native_clear_host_cases=256,native_clear_host_guards=14,
       earlier_standalone_component_scope='The64standalone/64inplace and original1024host scene recovery matrices predate internal clear/rotation replacement; their original helper effects are explicit fixtures. They are historical prerequisites, not newv26targetcases.',
       scope='Current v26 exact native scene module:772cases, structured native E03Aclear and17F14rotation, real shared68000bridge, remaining185B2and other services declared as component fixtures. Actual MMIOreads execute; controlled clear busy values replace only the MOVE destination after the read. Trace compares read address/count/order and write values, not read values. Host clear256dualCPU/RAM/order plus14guards separate. Fresh route uses real original remaining services. Normal completed-call proof only; arbitraryIRQ/intermediate-state/wholegame/consolefidelity unproved.')
    packet['latest_source_development']=scene
    summary=packet['checked_current_summary'].replace('V26native clear and rotation completes','V26 native clear and rotation complete').replace('/24,963fresh','/24,963 fresh').replace('5,360native','5,360 native').replace('differs279frames','differs on 279 frames').replace('with33control-layout','with 33 control-layout')
    for key in ['checked_current_summary','checked_answer','current_verified_route_summary']:packet[key]=summary
    save(out/'current-status-packet.json',packet);shutil.copy2(__file__,out/'corrector-source.py')
    deps={str(p):sha(p)for p in out.iterdir()if p.is_file()}
    w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps});atomic(wp,w)
    for p,h in deps.items():
        dest=P/'workbench'/Path(p).relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    shutil.copy2(wp,P/'workbench'/wp.relative_to(ROOT))
    save(V/'scene17-clear-status-scope-v1-current.json',dict(status='terminal_v26_inherited_case_count_and_helper_scope_corrected',directory=str(out),game_bytes_changed=False,new_predictions=0,new_training=False,dependencies_sha256=deps))
    print('Current status: final scene772; native clear/rotation scope; historical prototype scope explicit.',flush=True)
if __name__=='__main__':main()
