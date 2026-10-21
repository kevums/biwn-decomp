"""Original four navigation fixtures and native public-root metadata."""
import copy
from types import SimpleNamespace
import check_biwn_actor_navigation as navigation
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
SP,STOP=navigation.SP,navigation.STOP
PATCH_WIDTHS={0xf368:8,0x13f12:6,0x13f7c:6,0x13fea:6}
END_BY_ENTRY={0xf368:0xf4d8,0x13f12:0x13f7c,0x13f7c:0x13fea,0x13fea:0x1404c}
SYMBOL_BY_ENTRY={0xf368:'biwn_native_actor_waypoint',0x13f12:'biwn_native_actor_nav_left_entry',0x13f7c:'biwn_native_actor_nav_right_entry',0x13fea:'biwn_native_actor_nav_front_entry'}
class Script(navigation.Memory):
    def __init__(self,snapshot,case):
        super().__init__(snapshot,case)
        self.memory=self.ram
prior=SimpleNamespace(Script=Script,WIDTHS={0xf368:[4],0x13f12:[4,4],0x13f7c:[4,4],0x13fea:[4]},CODE_RANGES=navigation.RANGES,world=navigation.world,__file__=__file__)
SERVICES=set();MEMBERS=set(PATCH_WIDTHS)
def read(p):
    import json
    from pathlib import Path
    return json.loads(Path(p).read_text())
def cases():
    rows=[]
    for original in navigation.cases():
        row=copy.deepcopy(original);row['incoming']=row['registers'][:15];row['sr']=row['SR'];row['params']=[];offset=4
        for width in prior.WIDTHS[row['entry']]:
            row['params'].append(next(v for a,w,v in row['initial']if a==SP+offset and w==width));offset+=width
        rows.append(row)
    originals=copy.deepcopy(rows)
    for entry in PATCH_WIDTHS:
        group=[row for row in originals if row['entry']==entry]
        for mode in[0,0x2000]:
            for flags in range(32):
                for index in[0,1,3,4,5,7,8,9]:
                    row=copy.deepcopy(group[index]);row['sr']=mode|flags;rows.append(row)
    return rows
