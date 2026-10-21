"""Movement+collision+geometry with actual CPU helpers; only GPU effects prescribed."""
import copy
from types import SimpleNamespace
import check_biwn_actor_movement_collision as motion
import check_biwn_actor_creation as creation
import check_biwn_actor_direction as direction
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
class Script(creation.Script):
 def __init__(self,snapshot,case):
  super().__init__(snapshot,case);self.memory=bytearray(motion.Memory(snapshot,case).ram);self.changed=[]
 def call(self,target,args,incoming):
  assert target==0xe220;self.trace.append(['call',target,args,incoming])
  for a,w,v in self.case['GPU_effects']:self.write(a,w,v)
  return self.case['returns'][str(target)]
prior=SimpleNamespace(Script=Script,WIDTHS={0x13c9a:[4,4],0x13b5a:[4,2,2,2],0x13bb0:[4,4,2],0x13440:[2,2],0xe588:[4,4],0xe220:[4,4,4,4,4],0x1028e:[4],0x102c4:[4],0x1039c:[4,2],0x10652:[4,2]},CODE_RANGES=[(0x13b5a,0x13f12)]+direction.RANGES+motion.collision.geometry.RANGES,world=motion.world,__file__=__file__)
SP,STOP=motion.SP,motion.STOP;SERVICES={0xe220};MEMBERS=set(prior.WIDTHS)-SERVICES;COLL_PATCH_WIDTHS={0x13b5a:8,0x13bb0:6}
def read(p):
 import json
 from pathlib import Path
 return json.loads(Path(p).read_text())
def cases():
 rows=[]
 for c in motion.cases():
  row=copy.deepcopy(c);row['entry']=0x13c9a;row['incoming']=row['registers'][:15];row['sr']=row['SR'];row['params']=[next(v for a,w,v in row['initial']if a==SP+off and w==4)for off in [4,8]];rows.append(row)
 original=copy.deepcopy(rows)
 for mode in [0,0x2000]:
  for flags in range(32):
   for i in [0,16,32,80,96,112,160,176]:
    row=copy.deepcopy(original[i]);row['sr']=mode|flags;rows.append(row)
 return rows
