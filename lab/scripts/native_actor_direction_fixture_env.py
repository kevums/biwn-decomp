"""Original direction fixtures and actual signed-division helper metadata."""
import copy
from types import SimpleNamespace
import check_biwn_actor_direction as direction
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
SP,STOP=direction.SP,direction.STOP
PATCH_WIDTHS={0x13440:8};END_BY_ENTRY={0x13440:0x134dc}
SYMBOL_BY_ENTRY={0x13440:'biwn_native_actor_direction'}
class Script(direction.prior.Memory):
 def __init__(self,snapshot,case):
  super().__init__(snapshot,case);self.memory=self.ram
prior=SimpleNamespace(Script=Script,WIDTHS={0x13440:[2,2],0xe588:[4,4]},CODE_RANGES=direction.RANGES,world=direction.world,__file__=__file__)
SERVICES=set();MEMBERS={0x13440,0xe588}
navigation=direction
def cases():
 rows=[]
 for original in direction.cases():
  row=copy.deepcopy(original);row['incoming']=row['registers'][:15];row['sr']=row['SR'];row['params']=[next(v for a,w,v in row['initial']if a==SP+offset and w==2)for offset in [4,6]];rows.append(row)
 originals=copy.deepcopy(rows)
 for mode in [0,0x2000]:
  for flags in range(32):
   for index in [0,1,3,4,5,7,8,9]:
    row=copy.deepcopy(originals[index]);row['sr']=mode|flags;rows.append(row)
 return rows
