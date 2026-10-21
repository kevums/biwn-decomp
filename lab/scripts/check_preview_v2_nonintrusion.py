"""Compare cloned preview runs with/without the read-only observer hook.

Both use the same checkpoint, disc, input fixture, full CPU and GPU/DSP
readbacks. This is a finite headless witness, not keyboard-window testing.
"""
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1];RT=Path.home()/'.lmstudio/local-ai-lab/native-preview-v2'
def sha(p):return __import__('hashlib').sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def main():
 out=ROOT/'verification/preview-v2-nonintrusion'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 source=RT/'scripts/run_biwn_native_keyboard_v2.py';text=source.read_text();old='ROOT=Path(__file__).resolve().parents[1]';assert text.count(old)==1;text=text.replace(old,'ROOT=Path('+repr(str(RT))+')')
 text=text.replace("def main():", "class FullCPU(c.Structure):\n _fields_=[('registers',c.c_uint32*16),('pc',c.c_uint32),('usp',c.c_uint32),('ssp',c.c_uint32),('sr',c.c_uint16)]\n\ndef main():",1)
 anchor='  if not args.headless:'
 more='''  core.BIWNReadCPUState.argtypes=[c.POINTER(FullCPU)]
  def full_CPU():
   value=FullCPU();core.BIWNReadCPUState(c.byref(value));return dict(registers=list(value.registers),pc=value.pc,usp=value.usp,ssp=value.ssp,sr=value.sr)
  def processor_digest(name):
   fn=getattr(core,name+'StateSave');fn.argtypes=[c.c_void_p];fn.restype=c.c_size_t;buffer=c.create_string_buffer(65536);size=fn(buffer);assert 0<size<=65536;return hashlib.sha256(buffer.raw[:size]).hexdigest()
'''
 assert text.count(anchor)==1;text=text.replace(anchor,more+anchor)
 text=text.replace('rows.append(dict(frame=frame,','rows.append(dict(CPU_full=full_CPU(),GPU_sha256=processor_digest(\'GPU\'),DSP_sha256=processor_digest(\'DSP\'),frame=frame,',1)
 runs={};paths=[Path(__file__),source,RT/'scripts/native_preview_observer_v2.c',RT/'artifacts/pad-input-fixture.json']
 for lane in ['observed','unobserved']:
  script=out/(lane+'.py');target=out/(lane+'-current.json');current=text.replace("pointer=ROOT/'verification/native-keyboard-v2-current.json'",'pointer=Path('+repr(str(target))+')')
  assert current!=text
  if lane=='unobserved':
   anchor='core.BIWNSetCPUExecOwner(observer,0)';assert current.count(anchor)==1;current=current.replace(anchor,'None')
  script.write_text(current);command=[str(Path.home()/'.lmstudio/local-ai-lab/.venv/bin/python3.12'),str(script),'--headless','--frames','400','--input-script',str(RT/'artifacts/pad-input-fixture.json')]
  p=subprocess.run(command,cwd='/',env={**os.environ,'PYTHONPATH':str(RT/'scripts')},capture_output=True,text=True,timeout=90);(out/(lane+'.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr[-4000:]
  receipt=json.loads(target.read_text());assert receipt['status']=='terminal_native_keyboard_frontend_stopped_pending_review';runs[lane]=receipt;paths.extend([script,target,Path(receipt['directory'])/'frames.json'])
  print(lane,'400frames complete',flush=True)
 left=json.loads((Path(runs['observed']['directory'])/'frames.json').read_text());right=json.loads((Path(runs['unobserved']['directory'])/'frames.json').read_text());keys=['frame','CPU','CPU_full','RAM_sha256','video_sha256','GPU_sha256','DSP_sha256','scene','mode','movie_flags','pressed_buttons']
 assert len(left)==len(right)==400
 for a,b in zip(left,right):assert {k:a[k]for k in keys}=={k:b[k]for k in keys},a['frame']
 assert runs['observed']['native_scan_entries']>0 and runs['unobserved']['native_scan_entries']==0
 proof=dict(status='terminal_preview_observer_400frame_nonintrusion_match',directory=str(out),frames=400,compared=keys,runs={k:v['directory']for k,v in runs.items()},observer_claims_execution=False,keyboard_window_verified=False,new_training=False,source_sha256={str(p):sha(p)for p in paths},scope=__doc__);save(out/'review.json',proof);save(ROOT/'verification/preview-v2-nonintrusion-current.json',proof);print(proof['status'],flush=True)
if __name__=='__main__':main()
