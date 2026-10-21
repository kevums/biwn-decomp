"""Explicit dispatcher dependency fixtures, not original game service implementations."""
import ctypes as c,json
from pathlib import Path
import task_runtime_native as original
import check_biwn_input_dispatch as standalone
ROOT=original.ROOT
ANIMATION=0x180000;MODEL_HANDLE=0x181000;MODEL=0x182000;OLD_HANDLE=0x183000;OLD_BLOCK=0x184000
class Backend:
 extra_stubs=[x for x in standalone.HELPERS if x not in[0xe4c0,0xdf60,0x1545c,0xe588,0xeb04,0x1aa40]]
 logged=standalone.HELPERS
 widths=standalone.WIDTHS
class Script(original.previous.prior.previous.Script):
 def __init__(self,snapshot,case):super().__init__(snapshot,case);self.dispatch_calls={}
 def call(self,target,args):
  if target not in standalone.HELPERS or target in[0xe4c0,0xdf60,0x1545c,0xe588]:return super().call(target,args)
  self.trace.append(['call',target,args]);n=self.dispatch_calls.get(target,0);self.dispatch_calls[target]=n+1
  if target==0xeb04:
   flags=self.case.get('dispatch_animation_flags',[1]);self.put(ANIMATION+2,1,flags[min(n,len(flags)-1)])
  elif target==0x1af04:return MODEL_HANDLE
  elif target==0x152a2:
   handle=0x185000+n*4;block=0x186000+n*0x400
   self.put(handle,4,block+8);self.put(block,4,0x110);return handle
  elif target==0x1aade:return 0x18a000
  for helper,address,width,value in self.case.get('dispatch_dependency_effects',[]):
   if target==helper:self.put(address,width,value)
  return 0

def fixture(old,index):
 case=original.fixture(old,index);state=index%13
 held_choices=[0,0x00100000,0x00200000,0x00400000,0x00800000,0x02200000,0x02002000,0x02000000,0x20000000,0x02400000,0x02800000,0x02202000]
 held=held_choices[(index//13)%len(held_choices)]
 if index>=32 and index%4==0:held|=[0x200,1<<19,1<<4,0xe02fe][(index//4)%4]
 case['poll_inputs']=[held];case['dispatch_initial_state']=state;case['dispatch_kind']='state_input_matrix';case['dispatch_animation_flags']=[0,1]
 case['initial'] += [[0x49cb8,2,state],[0x49c4c,2,index%3],[0x49c4e,2,0],[0x49d5a,2,index%5],[0x49cb0,4,ANIMATION],[ANIMATION+2,1,index%4],[0x49caa,4,OLD_HANDLE],[OLD_HANDLE,4,OLD_BLOCK+8],[OLD_BLOCK,4,0x100],[MODEL_HANDLE,4,MODEL],[MODEL+8,4,0x80],[0x46250,2,300],[0x4624a,2,1],[0x4624c,2,[0,7,0x7fff,0xffff][index%4]],[0x4624e,2,[0,7,0x7fff,0xffff][index%4]]]
 # Declared bounded parent-table miss sentinel, retained from prior tests.
 # New movement may miss the old fixture's first matching key.
 case['initial'] += [[0x90012,2,0],[0x90014,2,0x8000],[0x90016,2,0]]
 # Force both animation-wait continuations and all special-item service paths.
 if index<24:
  state=1;held=0x02002000;slot=1 if index%3==0 else 0
  item=[0x41,0x42,0x43,0x44,0x45,0x46,0x66,0x70][index//3]
  case.update(dispatch_initial_state=1,dispatch_kind='equipment_and_transition',poll_inputs=[held])
  case['initial'] += [[0x49cb8,2,1],[0x49d5a,2,slot],[0x49d54,2,0],[0x49d2c,2,item],[0x461be+item,1,2 if item==0x70 else 0]]
 # Both top-level pause/repress and nested idle polling, without infinite waits.
 if index in[24,25,26,27]:
  case.update(dispatch_initial_state=1,dispatch_kind='nested_idle_poll',poll_inputs=[0x00100000,0,0x00100000,0,0x20000000])
  case['initial'] += [[0x49cb8,2,1],[0x49c60,2,2],[0x49c78,4,0x180100],[0x180100,2,0x8000],[0x46250,2,0]]
 if index in[28,29,30,31]:
  case.update(dispatch_kind='pause_release_repress',poll_inputs=[0x10000000,0,0,0x10000000,held])
 return case

extra_stubs=Backend.extra_stubs
logged=Backend.logged
widths=Backend.widths
