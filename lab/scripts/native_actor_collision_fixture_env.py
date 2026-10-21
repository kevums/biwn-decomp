"""Original collision fixtures; all four geometry helpers execute actual code."""
import copy
from types import SimpleNamespace
import check_biwn_actor_collision as collision
import check_biwn_actor_creation as creation
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
prior=SimpleNamespace(Script=creation.Script,WIDTHS={0x13b5a:[4,2,2,2],0x13bb0:[4,4,2],0x1028e:[4],0x102c4:[4],0x1039c:[4,2],0x10652:[4,2]},CODE_RANGES=[(0x13b5a,0x13c9a)]+collision.geometry.RANGES,world=collision.world,__file__=__file__)
SP,STOP=collision.SP,collision.STOP
SERVICES=set();MEMBERS=set(prior.WIDTHS);PATCH_WIDTHS={0x13b5a:8,0x13bb0:6};END_BY_ENTRY={0x13b5a:0x13bb0,0x13bb0:0x13c9a}
def read(p):
 import json
 from pathlib import Path
 return json.loads(Path(p).read_text())
def cases():
 rows=[]
 for c in collision.cases():
  row=copy.deepcopy(c);row['incoming']=row['registers'][:15];row['sr']=row['SR'];offset=4;params=[]
  for width in prior.WIDTHS[row['entry']]:params.append(next(v for a,w,v in row['initial']if a==SP+offset and w==width));offset+=width
  row['params']=params;rows.append(row)
 originals=copy.deepcopy(rows)
 for entry in [0x13b5a,0x13bb0]:
  group=[x for x in originals if x['entry']==entry]
  for mode in [0,0x2000]:
   for flags in range(32):
    for i in [0,1,3,4,5,7,8,9]:
     c=copy.deepcopy(group[i]);c['sr']=mode|flags;rows.append(c)
 return rows
