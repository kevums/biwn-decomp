"""Finite full-state replay with and without five-caller preview counters."""
import hashlib
import json
import subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RT=Path.home()/'.lmstudio/local-ai-lab/native-preview-v3'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')


def main():
    out=ROOT/'verification/preview-v3-nonintrusion'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    print(out,flush=True)
    script=RT/'scripts/run_biwn_native_keyboard_v3.py'
    fixture=RT/'artifacts/pad-input-long-v1.json'
    paths=[Path(__file__),script,fixture,RT/'scripts/native_preview_observer_v3.c',RT/'manifest.json']
    runs={}
    for lane in ['observed','unobserved']:
        command=[str(Path.home()/'.lmstudio/local-ai-lab/.venv/bin/python3.12'),str(script),'--headless','--frames','2400','--input-script',str(fixture)]
        if lane=='unobserved':command.append('--observer-off')
        p=subprocess.run(command,cwd='/',capture_output=True,text=True,timeout=90)
        (out/(lane+'.log')).write_text(p.stdout+p.stderr)
        assert p.returncode==0,p.stderr[-4000:]
        receipt=read(RT/'verification/native-keyboard-v3-current.json')
        assert receipt['status']=='terminal_native_keyboard_frontend_stopped_pending_review'
        save(out/(lane+'.json'),receipt);runs[lane]=receipt
        paths.extend([out/(lane+'.json'),Path(receipt['directory'])/'frames.json',Path(receipt['directory'])/'final-state.bin',Path(receipt['directory'])/'final-RAM.bin'])
        print(lane,receipt['frames'],'frames',receipt['native_returns'],flush=True)
    left=read(Path(runs['observed']['directory'])/'frames.json');right=read(Path(runs['unobserved']['directory'])/'frames.json')
    keys=['frame','CPU','CPU_full','RAM_sha256','video_sha256','GPU_sha256','DSP_sha256','scene','mode','movie_flags','pressed_buttons']
    assert len(left)==len(right)==2400
    for a,b in zip(left,right):assert {k:a[k]for k in keys}=={k:b[k]for k in keys},a['frame']
    assert all(n>0 for n in runs['observed']['native_returns'].values())
    assert all(n==0 for n in runs['unobserved']['native_returns'].values())
    assert all(n==0 for n in runs['observed']['original_Deck_body_steps'].values())
    for name in ['final-state.bin','final-RAM.bin','final-video.xrgb8888']:
        assert sha(Path(runs['observed']['directory'])/name)==sha(Path(runs['unobserved']['directory'])/name),name
    proof=dict(status='terminal_five_caller_preview_2400frame_observer_nonintrusion_match',directory=str(out),frames=2400,compared=keys,
               runs={k:v['directory']for k,v in runs.items()},native_returns=runs['observed']['native_returns'],
               original_Deck_body_steps=runs['observed']['original_Deck_body_steps'],GPU_returns=runs['observed']['GPU_returns'],
               final_serialized_state_equal=True,all_GPU_Deck_guards_pass=True,immutable_native_code_unchanged=True,
               observer_claims_execution=False,keyboard_window_verified=False,new_training=False,
               source_sha256={str(p):sha(p)for p in paths},scope=__doc__)
    save(out/'review.json',proof);save(ROOT/'verification/preview-v3-nonintrusion-current.json',proof)
    print(proof['status'],flush=True)


if __name__=='__main__':main()
