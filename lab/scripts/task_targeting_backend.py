"""Finite candidate/transform data for real original/C targeting integration."""
import task_animation_backend as base
ROOT=base.ROOT
extra_stubs=base.extra_stubs
logged=base.logged
widths=base.widths
Backend=base.Backend
Clock=base.Clock
animation_linked=True
targeting_linked=True
PRESERVE_BOUNDARY_ORIENTATION=[36, 67, 171, 172, 186, 192, 236] # Prior actual native boundary-yield cases.
class Script(base.Script):
 def call(self,target,args):
  assert target!=0x20820,'Targeting return stub is forbidden on this path'
  return super().call(target,args)
def fixture(old,index):
 case=base.fixture(old,index);initial=case['initial']
 def last(address):return next(value for a,w,value in initial[::-1]if a==address)
 x=last(0x49c50);z=last(0x49c56);distance=16+index%32
 if index not in PRESERVE_BOUNDARY_ORIENTATION:initial.append([0x49cba,1,(index%4)*64])
 else:case['preserve_boundary_fixture_orientation']=True
 initial += [[0x49d5c,2,index%2],[0x49d5e,2,0xa55a],[0x49d60,2,0xffff],[0x49d64,2,0xa55a],[0x49d66,2,0xa55a],[0x49d68,2,112],[0x49d6a,2,90]]
 for slot in range(5):initial.append([0x4c280+slot*4,4,0x7fffffff if index%5 else 1])
 for i in range(40):
  record=0x49d6c+i*206;initial += [[record,2,1 if i<4 and index%7 else 0],[record+0x6c,2,1]]
  if i>=4:continue
  dx,dz=[(0,-distance),(-distance,0),(0,distance),(distance,0)][i];matrix_index=4+i;matrix=0x47b88+matrix_index*64
  initial += [[record+4,4,(x-dx)&0xffffffff],[record+10,4,(z-dz)&0xffffffff],[record+0xc0,2,matrix_index],[matrix+0x16,2,[16,32,100,1024][i]],[matrix+0x12,2,(i*16-24)&0xffff],[matrix+0x14,2,20+i*5]]
 case['targeting_assets']='Synthetic finite candidate/transform records; producers and full actor lifecycle remain unported.'
 return case
