"""Connected CPU boundary handlers, movement and inventory vs original code."""
import argparse,ctypes as c,hashlib,json,random
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_boundary_handlers as boundary
import check_biwn_world_movement_pipeline as movement
world=movement.world;ROOT=world.ROOT

def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
class Script(world.Script):
 def call(self,target,args):
  if target not in boundary.HELPERS:return super().call(target,args)
  self.trace.append(['call',target,args])
  for helper,address,width,value in self.case.get('boundary_helper_effects',[]):
   if helper==target:self.put(address,width,value)
  return self.case['nested_helper_result']

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int,default=256);options=parser.parse_args()
 old=json.loads((ROOT/'verification/biwn-world-update-checks.json').read_text());main_lib=c.CDLL(str(Path(old['directory'])/'libbiwn-world-update.dylib'));fn=main_lib.biwn_world_update;fn.argtypes=[c.POINTER(world.Bus)];fn.restype=c.c_int
 checked=json.loads((ROOT/'verification/biwn-boundary-handlers-checks.json').read_text());lib=c.CDLL(str(Path(checked['directory'])/'libboundary-handlers.dylib'));one=lib.biwn_boundary_type1;one.argtypes=[c.POINTER(world.Bus),c.c_uint16,c.c_uint16,c.c_uint16,c.c_uint32,c.POINTER(c.c_uint32)];one.restype=c.c_int;two=lib.biwn_boundary_type2;two.argtypes=[c.POINTER(world.Bus),c.c_uint32,c.c_uint16,c.c_uint32,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];two.restype=c.c_int;functions={0x19f2c:one,0x19fda:two}
 snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();out=ROOT/'verification/biwn-world-boundary-pipeline'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);rng=random.Random(0x19fda);rows=[];device=movement.Device()
 try:
  for i,old_case in enumerate(world.cases()[:options.limit]):
   case=dict(old_case);case['initial']=list(old_case['initial']);case['nested_helper_result']=old_case['collision_result'];case['boundary_helper_effects']=[[0x102c4,0x49c8c,2,0x1337]]if i%2 else[]
   edge=[0x0001,0x0fff,0x1001,0xffff,0x2345][(i//5)%5];obj=0x81000;node=0x82000;table=0x90000
   for address in [0x80002,0x80004,0x80006,0x80008]:case['initial'].append([address,2,edge])
   layout=['target','transition','level','zero_flags','terminator','later_match','no_index'][(i//3)%7]
   case['initial'] += [[0x49c18,4,node],[node+8,4,table],[0x49c78,4,obj],[obj+6,2,7],[obj+8,2,11],[obj+0x16,2,0xffff if layout=='no_index' else 0],[0x49c62,2,1 if layout=='level' else 0],[0x49c8c,2,rng.randrange(65536)]]
   # Use original CPU+GPU pre-boundary state to build matching record keys.
   preparatory=world.Script(snapshot,case);capture={};movement.original(device,bytes(preparatory.memory),preparatory,[rng.getrandbits(32)for _ in world.REGS],boundary_capture=capture)
   if capture.get('target')==0x19fda and layout!='no_index':
    prefix_case={'initial':[],'default_helper_return':0};prefix=boundary.Script(capture['RAM'],prefix_case);cpu,_=boundary.make_cpu(prefix,0x19fda,capture['args'],[0]*len(world.REGS));cpu.emu_start(0x19fda,0x1a05a,count=64,timeout=500000);key=cpu.reg_read(world.UC_M68K_REG_D1)&0xffff
    offset=6 if layout=='later_match' else 0
    if offset:case['initial'] += [[table,2,key^1],[table+2,2,0],[table+4,2,0]]
    case['initial'] += [[table+offset,2,key^1 if layout=='terminator' else key],[table+offset+2,2,0x8000 if layout=='terminator' else 0 if layout=='zero_flags' else 0x7000],[table+offset+4,2,0xffff if layout in ['transition','level']else 0x1234]]
    case['original_prefix_record_key']=key
   save(out/'status.json',{'status':'running','case':i,'layout':layout,'edge':hex(edge)})
   a=Script(snapshot,case);b=Script(snapshot,case);ram=bytes(a.memory)
   oa,ta,ra,observed=movement.original(device,ram,a,[rng.getrandbits(32)for _ in world.REGS],boundary_helpers=True);ob,tb,rb,stats=movement.translated(fn,device,ram,b,functions)
   equal=oa[:0x15b7a0]==ob[:0x15b7a0]and oa[0x15b7aa:]==ob[0x15b7aa:]
   if not equal or ta!=tb or ra!=rb:
    save(out/'mismatch.json',{'case':i,'parameters':case,'RAM_match':equal,'original_trace':ta,'C_trace':tb,'original_blitter_registers':ra,'C_blitter_registers':rb,'RAM_differences':[[j,oa[j],ob[j]]for j in range(len(oa))if oa[j]!=ob[j]][:100]});raise AssertionError(str(out/'mismatch.json'))
   calls=[t for t in tb if t[0]=='call'];rows.append({'case':i,'parameters':case,'layout':layout,'edge':edge,'original':observed,'rebuilt':stats,'calls':calls,'CPU_bus_trace_and_helper_calls_match':True,'RAM_except_formatter_scratch_match':True,'blitter_registers_match':True,'inventory_frame_sha256':hashlib.sha256(ob[movement.frame.FRAME_START:movement.frame.FRAME_END]).hexdigest()})
   if i<4:save(out/('trace-'+str(i)+'.json'),tb)
 finally:device.close()
 save(out/'fixtures.json',rows)
 calls=[call for row in rows for call in row['calls']]
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'connected_boundary_movement_inventory_CPU_GPU_match','directory':str(out),'cases':len(rows),'type1_handler_calls':sum(t[1]==0x19f2c for t in calls),'type2_handler_calls':sum(t[1]==0x19fda for t in calls),'redraw_cases':sum(t[1]==0x1b786 for t in calls),'nested_dependency_targets_observed':sorted({hex(t[1])for t in calls if t[1]in boundary.HELPERS}),'remaining_top_level_scripted_helpers':['0xe4c0','0x191f4','0xf0fa','0xeb04','0x20820'],'remaining_nested_dependency_targets':[hex(x)for x in boundary.HELPERS],'additional_original_components':0,'rebuilt_original_CPU_instructions':0,'rebuilt_original_GPU_instructions':0,'game_frames_executed':0,
 'matched':['Original CPU caller executes both real boundary handlers, E220/digit/inventory/text/sprite routines and original GPU movement/sprite overlays; rebuilt path uses their compiled C implementations.','Whole externalRAM except10formatter scratchbytes; exact externalCPU bus and helper call args/order; finalblitterregisters and inventorypanel output.','Table match keys derived from originalCPU+GPU postmovement state and original boundary prefix, not the C key formula.'],
 'limits':['Five other top-level helper targets and ten nested geometry/transition targets remain scripted; reduced top-level stubs does not mean fewer total missing services.','Boundary CPU control/data logic verified; lower-level collision geometry and transitions remain dependencies, not complete world collision.','Caller uses onlylow16boundary result; fullD0 ABI separately checked in1450standalone cases.','Pinned blitter and synchronous GPU dispatcher model, privateCPUstack/formatter scratch and fullCCR excluded. No physical hardware, completeworldviewport/mainloop/audio/fullgame proof.']}
 save(out/'report.json',report);save(out/'status.json',{'status':'terminal','exit_code':0})
 if options.limit==256:save(ROOT/'verification/biwn-world-boundary-pipeline-checks.json',report)
 print(json.dumps(report),flush=True)
if __name__=='__main__':main()
