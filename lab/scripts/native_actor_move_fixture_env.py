"""Original13C9Afinite fixtures adapted to ordered native ABI checking."""
import copy
from types import SimpleNamespace
import check_biwn_actor_movement as movement
import check_biwn_actor_creation as creation
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
class Script(creation.Script):
 def call(self,target,args,incoming_D0):
  self.trace.append(['call',target,args,incoming_D0]);effects=self.case['GPU_effects']if target==0xe220 else self.case['collision_effects']if target in[0x13b5a,0x13bb0]else[]
  for a,w,v in effects:self.write(a,w,v)
  return self.case['returns'][str(target)]
prior=SimpleNamespace(Script=Script,WIDTHS={0x13c9a:[4,4],**movement.WIDTHS},CODE_RANGES=[(0x13c9a,0x13f12)],world=movement.world,__file__=__file__)
SP,STOP=movement.SP,movement.STOP
SERVICES=set(movement.WIDTHS);MEMBERS={0x13c9a}
def read(p):
 import json
 from pathlib import Path
 return json.loads(Path(p).read_text())
def cases():
 result=[]
 for c in movement.cases():
  row=copy.deepcopy(c);row['entry']=0x13c9a;row['incoming']=row['registers'][:15];row['sr']=row['SR'];row['params']=[next(v for a,w,v in row['initial']if a==SP+off and w==4)for off in [4,8]];result.append(row)
 originals=copy.deepcopy(result)
 for mode in [0,0x2000]:
  for flags in range(32):
   for i in [0,1,2,3,5,32,80,160,400]:
    c=copy.deepcopy(originals[i]);c['sr']=mode|flags;result.append(c)
 return result
