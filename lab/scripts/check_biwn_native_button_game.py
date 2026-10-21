"""Native compiled keypad routine inside actual clocked game frames.
Both lanes reserve identical heap bytes. Candidate replaces only entry with
handle trampoline. Original CPU emulator executes retained game and new
compiled code; this is partial native-code integration, not source-owned CPU.
"""
from datetime import datetime,timezone
from pathlib import Path
import json,subprocess,os
import numpy as np
from check_biwn_native_button_digit import ROOT,sha,save
from check_biwn_natural_coordinate_scheduler import DTYPE

def main():
 out=ROOT/'verification/native-button-game'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 proof=ROOT/'verification/native-button-movable-current.json';p=json.loads(proof.read_text());assert p['status']=='terminal_native_movable_component_ABI_matches'
 for path,digest in p['source_sha256'].items():assert sha(path)==digest
 overlay=json.loads(Path(p['overlay']).read_text());reference=json.loads(json.dumps(overlay));entry=0x1b718;end=entry+p['trampoline_bytes']
 # Overlay diffs can split on identical bytes; remove every entry fragment.
 reference['patches']=[x for x in reference['patches']if not entry<=int(x['address'],16)<end]
 save(out/'candidate-overlay.json',overlay);save(out/'reference-overlay.json',reference)
 natural=json.loads((ROOT/'verification/natural-coordinate-gameplay-current.json').read_text());confirm=next(x for x in natural['cases']if x['case']=='confirm');baseline=Path(confirm['source_trace']).parent.parent
 protocol=json.loads((baseline/'protocol.json').read_text());command=next(x['command'][:]for x in protocol['commands']if x['phase']=='reference')
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),movable_proof=str(proof),movable_proof_sha256=sha(proof),commands=[],whole_game_complete=False,disc_modified=False,preview_changed=False,retained_original_CPU_emulator=True,new_compiled_native_component=True)
 def checkpoint():save(out/'protocol.json',state);save(ROOT/'verification/native-button-game-active.json',state)
 checkpoint();print(out,flush=True)
 try:
  for lane in ['reference','candidate']:
   run=command[:];run[run.index('--output')+1]=str(out/lane);run+=['--experimental-code-overlay',str(out/(lane+'-overlay.json'))]
   state['commands'].append(dict(lane=lane,command=run));state.update(status='running_'+lane);checkpoint()
   with(out/(lane+'.log')).open('w')as log:
    child=subprocess.Popen(run,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;checkpoint();print(lane,child.pid,flush=True);code=child.wait()
   assert code==0,(lane,out/(lane+'.log'));report=json.loads((out/lane/'report.json').read_text());assert not report['errors'],report['errors']
  reports={lane:json.loads((out/lane/'report.json').read_text())for lane in ['reference','candidate']}
  traces={lane:np.memmap(out/lane/'CPU-before-instructions.bin',dtype=DTYPE,mode='r')for lane in reports}
  calls={lane:np.flatnonzero(t['pc']==entry)for lane,t in traces.items()};assert len(calls['reference'])==len(calls['candidate'])>0
  pairs=[]
  # Capture ABI at each ordinary caller entry and its original return PC/SP.
  for ordinal,(left,right)in enumerate(zip(calls['reference'],calls['candidate'])):
   boundaries={}
   for lane,index in [('reference',left),('candidate',right)]:
    t=traces[lane];start=t[index];sp=int(start['registers'][15]);found=None
    for j in range(int(index)+1,min(len(t),int(index)+200)):
     if int(t[j]['registers'][15])==sp+4 and int(t[j]['pc'])not in range(entry,end):found=t[j];break
    assert found is not None,(lane,ordinal)
    boundaries[lane]=dict(incoming_registers=start['registers'].tolist(),incoming_SR=int(start['sr']),returned_registers=found['registers'].tolist(),return_PC=int(found['pc']),returned_SR=int(found['sr']))
   assert boundaries['reference']==boundaries['candidate'],('call_boundary',ordinal,boundaries)
   pairs.append(dict(ordinal=ordinal,**boundaries['candidate']))
  addr=p['allocated_address'];inside=int(np.count_nonzero((traces['candidate']['pc']>=addr)&(traces['candidate']['pc']<addr+p['payload_bytes'])))
  assert inside>0
  names=['final-video.bin','frontend-PCM.s16le'];equal={name:sha(out/'reference'/name)==sha(out/'candidate'/name)for name in names}
  # Frame images and semantic coordinate input fields are separately checked.
  frames=[1,60,350,600,900,960,1200,1500];frame_rows=[]
  for frame in frames:
   video_equal=sha(out/'reference'/f'frame-{frame}.png')==sha(out/'candidate'/f'frame-{frame}.png')
   a=(out/'reference'/f'frame-{frame}-RAM.bin').read_bytes();b=(out/'candidate'/f'frame-{frame}-RAM.bin').read_bytes()
   frame_rows.append(dict(frame=frame,video_equal=video_equal,player_and_inventory_equal=a[0x49b80:0x49e00]==b[0x49b80:0x49e00],different_RAM_bytes=sum(x!=y for x,y in zip(a,b))))
  save(out/'call-boundaries.json',pairs);save(out/'frame-comparison.json',frame_rows)
  state.update(status='terminal_native_component_game_experiment',frames_per_lane=1500,actual_game_calls=len(pairs),all_call_boundary_registers_PC_SR_match=True,compiled_instructions_executed=inside,final_artifacts_equal=equal,frame_comparison=frame_rows,CPU_instructions={lane:len(t)for lane,t in traces.items()},scope='Explicit setup overlay allocates identical payload in both lanes; candidate entry resolves game handle. Retained original native CPU emulator executes new GCC C routine amid game frames. Finite ordinary coordinate-keypad sequence; not a source-CPU-owned run, cold-loader integration, bootable disc, standalone game or hardware test.')
  checkpoint();save(ROOT/'verification/native-button-game-current.json',state);print(json.dumps({k:state[k]for k in ['status','actual_game_calls','compiled_instructions_executed','final_artifacts_equal','frame_comparison']}),flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));checkpoint();raise
if __name__=='__main__':main()
