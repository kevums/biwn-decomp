"""Finite animation assets and external delta samples for the three-task test.

No completion flags are written after seeding. Original/C EB04 changes the
current record pointer; dispatcher waits observe the selected record flags.
The request-queue consumer and a complete hardware clock remain unported.
"""
import task_dispatch_backend as base
ROOT=base.ROOT
extra_stubs=base.extra_stubs
logged=list(base.logged)+[0xeac4]
widths={**base.widths,0xeac4:[4]*4}
Backend=base.Backend
animation_linked=True
class Script(base.Script):
 def call(self,target,args):
  assert target!=0xeb04,'Animation completion return stub is forbidden on this path'
  return super().call(target,args)
TABLES=[0x45db8,0x45df4,0x45e30,0x45e6c,0x45ea8,0x45ee4,0x45f20,0x45f5c,0x45f98,0x45fd4,0x46010,0x4604c,0x46088,0x460c4,0x46100,0x4613c]

def fixture(old,index):
 case=base.fixture(old,index);case.pop('dispatch_animation_flags',None)
 case['animation_delta_samples']=[1,2,3];case['animation_assets']='Synthetic finite four-byte frame records; flags immutable after seeding.';case['animation_flag_values']=[]
 case['initial'] += [[0x49cb4,4,0],[0x49cae,2,1],[0x49d16,2,1 if index%2 else 0xffff],[0x49d18,2,index%2],[0x112940,2,[0,38,39,40,0xffff][index%5]]]
 def records(pointer,frame):
  case['animation_flag_values'].extend([[pointer+2,0],[pointer+6,1]])
  case['initial'].extend([[pointer,1,frame],[pointer+1,1,1],[pointer+2,1,0],[pointer+3,1,1],[pointer+4,1,(frame+1)&255],[pointer+5,1,1],[pointer+6,1,1],[pointer+7,1,0]])
 records(base.ANIMATION,0)
 for number,table in enumerate(TABLES):
  for actor in range(3):
   for slot in range(5):
    pointer=0x18b000+number*0x100+(actor*5+slot)*16
    case['initial'].append([table+actor*20+slot*4,4,pointer]);records(pointer,number+slot)
 return case
class Clock:
 def __init__(self,device):self.device=device
 def start(self,case):self.case=case;self.events=[];self.updates=0
 def begin_update(self):
  samples=self.case['animation_delta_samples'];delta=samples[min(self.updates,len(samples)-1)]
  self.device.direct(0x4c24e,2,delta)
  self.events.append({'update':self.updates,'external_delta_word':delta,'address':'0x4c24e'});self.updates+=1
