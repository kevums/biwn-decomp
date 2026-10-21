"""Freeze small contract answers from original CPU execution for local-model evaluation."""
import ctypes as c,json,random
from pathlib import Path
import check_biwn_world_update as world
import check_biwn_inventory_select as select
ROOT=world.ROOT

def main():
 report=json.loads((ROOT/'verification/biwn-world-update-checks.json').read_text());lib=c.CDLL(str(Path(report['directory'])/'libbiwn-world-update.dylib'));fn=lib.biwn_world_update;fn.argtypes=[c.POINTER(world.Bus)];fn.restype=c.c_int
 snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();s=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(s/'nextstage-68000-candidate.bin').read_bytes()
 template=world.cases()[1];rng=random.Random(14);rows=[]
 def check(name,clock=0,extra=None,effects=None,result=1):
  case=dict(template);case.update(clock=clock&0xffffffff,poll_inputs=[0],collision_result=result,terrain_result=0,movement_effects=effects or [[0x49cde+i*2,2,0]for i in range(3)]+[[0x49ce6+i*2,2,0]for i in range(3)])
  case['initial']=list(template['initial'])+[[0x46252,4,0],[0x49c60,2,0]]+(extra or [])
  a=world.Script(snapshot,case);b=world.Script(snapshot,case);world.original(image,a,[rng.getrandbits(32)for _ in world.REGS],set());assert world.translated(fn,b)==0 and a.trace==b.trace and a.memory==b.memory
  row={'name':name,'parameters':case,'trace':a.trace,'final_delta':a.get(0x4c24c,4),'primary_X':a.get(0x49c50,4),'primary_Y':a.get(0x49c54,2),'secondary_X':a.get(0x49b8c,2),'fraction_X':a.get(0x49c5a,2)};rows.append(row);return row
 ticks=[-1,0,30,31,-2147483648,2147483647];answers=[]
 for tick in ticks:
  raw=check('signed-clock-'+str(tick),clock=tick)['final_delta'];answers.append(raw-(1<<32)if raw&0x80000000 else raw)
 assert answers==[-1,0,30,30,-2147483648,30]
 initial=[[0x49c60,2,1],[0x49c50,4,0],[0x49c54,2,0],[0x49c56,4,200],[0x49c5a,2,0x3fff],[0x49c5c,2,0x3fff],[0x49c5e,2,0],[0x49b8c,2,0xffff],[0x49b92,2,0x3fff]]
 effects=[[0x49cde,2,0xffff],[0x49ce0,2,0xffff],[0x49ce2,2,0],[0x49ce6,2,1],[0x49ce8,2,1],[0x49cea,2,0]]
 fraction=check('fraction-and-signed-integer',extra=initial,effects=effects);assert [fraction[k]for k in ['primary_X','primary_Y','secondary_X','fraction_X']]==[0,0,65535,0]
 outcomes=[]
 for decision in [0,1,2]:
  extra=[[0x49c60,2,1],[0x49c50,4,10],[0x49c56,4,200],[0x49c5a,2,0],[0x49b8c,2,20],[0x49b92,2,0]]
  effects=[[0x49cde,2,1],[0x49ce0,2,0],[0x49ce2,2,0],[0x49ce6,2,0],[0x49ce8,2,0],[0x49cea,2,0]]
  row=check('collision-'+str(decision),extra=extra,effects=effects,result=decision);outcomes.append([row['primary_X'],row['secondary_X']])
 assert outcomes==[[10,20],[11,21],[11,20]]
 block=lib.biwn_inventory_select;block.argtypes=[c.POINTER(select.Bus),c.POINTER(select.State)];block.restype=c.c_int
 selection=[]
 for input_word,start in [((1<<9)|(1<<19),4),(1<<19,4),(1<<9,9),(1<<4,0)]:
  incoming=[rng.getrandbits(32)for _ in select.REGS];a=select.Script(input_word,start,start);b=select.Script(input_word,start,start);select.original_block(image,a,incoming);status,_=select.translated(block,b,incoming);assert status==0 and a.memory==b.memory and a.trace==b.trace
  selected=int.from_bytes(a.memory[0x49d54-select.BASE:0x49d56-select.BASE],'big');selection.append(selected)
 assert selection==[5,0,0,9]
 cases=[{'id':'signed-clock','question':'For signed clock differences [-1,0,30,31,-2147483648,2147483647], what values remain in0x4c24c after the clamp? Return JSON with one key values, a list of signed integers.','expected':{'values':answers}},
 {'id':'fraction-width','question':'PrimaryX32bit=0, primaryY16bit=0, secondaryX16bit=0xffff. Their fractions are0x3fff, delta fractions1, integer delta words0xffff. Collision returns1. What are final primary_X, primary_Y, secondary_X, fraction_X? Return those four JSON keys as unsigned integers.','expected':{k:fraction[k]for k in ['primary_X','primary_Y','secondary_X','fraction_X']}},
 {'id':'collision-results','question':'PrimaryX starts10 and secondaryX starts20, all relevant fractions0 and integer Xdelta1. A boundary helper is called. For its low-word results0,1,2 respectively, give final [primaryX,secondaryX] pairs in one JSON key pairs.','expected':{'pairs':outcomes}},
 {'id':'selection-priority','question':'Internal slots0..9. Give final slots for these independent cases in order: simultaneous cycle(bit9)+digit1(bit19) from4; digit1 alone from4; cycle alone from9; digit0(bit4) alone from0. Return JSON with one key slots, a list of integers.','expected':{'slots':selection}}]
 out={'scope':'Ten original-vs-C full CPU caller examples with scripted helpers, plus four original-vs-C selection block examples. Not model-generated answers or full-game proof. Frozen before model comparison.','world_examples':rows,'selection_expected':selection,'cases':cases}
 (ROOT/'verification/world-update-contract-examples.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'world_examples':len(rows),'selection_examples':4,'model_questions':len(cases)}))
if __name__=='__main__':main()
