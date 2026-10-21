"""Check the real movement caller's neighboring80byte context and task bounds.
The direction entry is48bytes below the movement root; its caller's context is
therefore entrySP-312..entrySP-232. No interrupt/concurrency bound is inferred.
"""
import copy,json,os
from pathlib import Path
from datetime import datetime,timezone
import native_actor_direction_engine_v1 as e
ROOT=e.ROOT;V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 gate=read(V/'native-actor-direction-current.json');assert gate['cases']==2560
 for p,h in gate['source_sha256'].items():assert e.g.sha(p)==h,p
 out=V/'native-actor-direction-contexts'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);e.g.save(out/'component-gate.json',gate)
 payload=Path(gate['binary']).read_bytes();symbols=gate['symbols'];snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();native=e.Native();rows=[]
 state=dict(status='checking_actual_direction_caller_context',pid=os.getpid(),directory=str(out),completed=0,planned=2560)
 def mark():e.g.save(out/'protocol.json',state);e.g.save(V/'native-actor-direction-contexts-active.json',state)
 mark()
 def execute(case,low,high,compiled):
  case=copy.deepcopy(case);canary=bytes(((i*43+case['sr']+17)&255)for i in range(high-low));case['initial']+=[[low+i,1,value]for i,value in enumerate(canary)]
  expected=e.execute(snapshot,case,payload,symbols,compiled);result=e.replay(native,snapshot,case,payload,symbols,compiled,expected);ram=native.device.ram()
  return result,expected['private_depth'],ram[low:high]==canary,ram[low:high]
 try:
  for index,case in enumerate(e.vectors()):
   left,original_depth,a,_=execute(case,e.SP-312,e.SP-232,False);right,depth,b,_=execute(case,e.SP-312,e.SP-232,True)
   assert left==right and a and b and depth<232,(index,depth,a,b)
   rows.append(dict(index=index,compiled_private_depth=depth,original_private_depth=original_depth,caller_context_clearance=232-depth,task_headroom=870-depth))
   if index%128==0:state['completed']=len(rows);mark();print('Context',index+1,'/2560',flush=True)
  witness=max(rows,key=lambda row:row['compiled_private_depth']);case=e.vectors()[witness['index']];_,depth,good,actual=execute(case,e.SP-230,e.SP-150,True)
  assert not good,'Deliberately overlapping parent context must detect actual stores'
  e.g.save(out/'negative-control.json',dict(defect='parent_context_moved_into_actual_direction_private_frame',rejected=True,index=witness['index'],range=[e.SP-230,e.SP-150],actual_bytes=actual.hex(),scope='Separate fixture changes only the declared parent-canary placement; no originalCPU behavior claim.'))
  e.g.save(out/'results.json',rows);inputs=[Path(__file__),Path(e.__file__),Path(e.g.__file__),out/'component-gate.json',out/'results.json',out/'negative-control.json',Path(gate['binary']),Path(gate['ELF'])]
  state.update(status='terminal_direction_caller_context_canaries_and_task_bounds_pass',completed=len(rows),cases=len(rows),caller_context_range=[e.SP-312,e.SP-232],max_private_depth=max(row['compiled_private_depth']for row in rows),minimum_caller_context_clearance=min(row['caller_context_clearance']for row in rows),minimum_task_headroom=min(row['task_headroom']for row in rows),overlapping_context_negative_rejected=True,source_sha256={str(p):e.g.sha(p)for p in inputs},scope=__doc__);mark();e.g.save(V/'native-actor-direction-contexts-current.json',state);print(json.dumps(state))
 except BaseException as error:state.update(status='terminal_direction_context_failed',error=repr(error));mark();raise
 finally:native.close()
if __name__=='__main__':main()
