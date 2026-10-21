"""Linked pure-CPU geometry, boundary handlers, movement and inventory."""
import argparse,ctypes as c,hashlib,json,random
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_geometry as geometry
import check_biwn_world_boundary_pipeline as previous
movement=previous.movement;world=previous.world;ROOT=world.ROOT

def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int,default=256);options=parser.parse_args()
 main_report=json.loads((ROOT/'verification/biwn-world-update-checks.json').read_text());main_lib=c.CDLL(str(Path(main_report['directory'])/'libbiwn-world-update.dylib'));fn=main_lib.biwn_world_update;fn.argtypes=[c.POINTER(world.Bus)];fn.restype=c.c_int
 br=json.loads((ROOT/'verification/biwn-boundary-handlers-checks.json').read_text());blib=c.CDLL(str(Path(br['directory'])/'libboundary-handlers.dylib'));one=blib.biwn_boundary_type1;one.argtypes=[c.POINTER(world.Bus),c.c_uint16,c.c_uint16,c.c_uint16,c.c_uint32,c.POINTER(c.c_uint32)];one.restype=c.c_int;two=blib.biwn_boundary_type2;two.argtypes=[c.POINTER(world.Bus),c.c_uint32,c.c_uint16,c.c_uint32,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];two.restype=c.c_int;boundaries={0x19f2c:one,0x19fda:two}
 gr=json.loads((ROOT/'verification/biwn-geometry-checks.json').read_text());glib=c.CDLL(str(Path(gr['directory'])/'libgeometry.dylib'));functions=geometry.bind(glib)
 old=json.loads((ROOT/'verification/biwn-world-boundary-pipeline-checks.json').read_text());old_rows=json.loads((Path(old['directory'])/'fixtures.json').read_text())
 snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();out=ROOT/'verification/biwn-world-geometry-pipeline'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);rng=random.Random(0x1028e);rows=[];device=movement.Device()
 try:
  for i,row in enumerate(old_rows[:options.limit]):
   case=dict(row['parameters']);case['initial']=list(case['initial']);actor=0x49c4c;container=0x85000;tiles=0x88000;portals=0x8a000;regions=0x8c000;node=0x82000
   case['initial'] += [[actor+0x40,2,8],[container,2,3],[container+2,2,3],[container+8,4,tiles],[container+12,4,portals],[node,2,3],[node+4,4,regions],[actor+0x1e,4,-64],[actor+0x1a,4,64],[actor+0x26,4,-64],[actor+0x22,4,64]]
   for room in range(3,14):case['initial'].append([0x49bb4+room*4,4,container])
   for index in range(3):
    tile=tiles+index*20;portal=portals+index*28;region=regions+index*24
    case['initial'] += [[tile+10,2,0],[tile+14,2,0],[tile+16,2,16],[tile+18,2,16],[portal+26,2,7],[portal+18,2,1024],[portal+20,2,0xffff],[portal+22,2,2],[portal+24,2,3],[region+2,2,1],[region+4,2,2],[region+6,2,3],[region+8,2,4]]
   # Previous parent-table keys depend on unchanged original postmovement
   # coordinates. Replace only a non-sentinel target with a valid region ID.
   case['initial']=[([a,w,1]if 0x90000<=a<0x90020 and (a-0x90000)%6==4 and w==2 and v!=0xffff else[a,w,v])for a,w,v in case['initial']]
   preliminary=previous.Script(snapshot,case);capture={};movement.original(device,bytes(preliminary.memory),preliminary,[rng.getrandbits(32)for _ in world.REGS],boundary_helpers=True,geometry_capture=capture)
   if capture.get('target')==0x10430:
    incoming=[0]*len(world.REGS);incoming[0]=capture['incoming_d0'];incoming[1]=capture['incoming_d1'];incoming[3]=capture['incoming_d3'];prefix_case={'entry':0x10430,'params':capture['args'],'incoming':incoming,'initial':[],'default_helper_return':0}
    script=geometry.boundary.Script(capture['RAM'],prefix_case);cpu=geometry.original(script,prefix_case,set(),prefix=0x104ce)
    if cpu.reg_read(world.UC_M68K_REG_PC)==0x104ce:
     key=cpu.reg_read(world.UC_M68K_REG_D1)&0xffff;index=capture['args'][1];direction=capture['args'][2];portal=portals+index*28;case['initial'].append([portal+[11,13,15,17][direction],1,key if i%2==0 else 0x80]);case['original_portal_prefix_key']=key
   save(out/'status.json',{'status':'running','case':i});a=previous.Script(snapshot,case);b=previous.Script(snapshot,case);ram=bytes(a.memory)
   oa,ta,ra,meta=movement.original(device,ram,a,[rng.getrandbits(32)for _ in world.REGS],boundary_helpers=True,geometry_helpers=True);ob,tb,rb,stats=movement.translated(fn,device,ram,b,boundaries,functions)
   equal=oa[:0x15b7a0]==ob[:0x15b7a0]and oa[0x15b7aa:]==ob[0x15b7aa:]
   if not equal or ta!=tb or ra!=rb:
    save(out/'mismatch.json',{'case':i,'parameters':case,'RAM_match':equal,'original_trace':ta,'C_trace':tb,'original_blitter_registers':ra,'C_blitter_registers':rb,'RAM_differences':[[j,oa[j],ob[j]]for j in range(len(oa))if oa[j]!=ob[j]][:100]});raise AssertionError(str(out/'mismatch.json'))
   calls=[t for t in tb if t[0]=='call'];rows.append({'case':i,'parameters':case,'original':meta,'rebuilt':stats,'calls':calls,'CPU_external_trace_and_helper_calls_match':True,'whole_RAM_except_formatter_scratch_match':True,'blitter_registers_match':True,'geometry_state_bytes':ob[actor:actor+0x58].hex(),'inventory_frame_sha256':hashlib.sha256(ob[movement.frame.FRAME_START:movement.frame.FRAME_END]).hexdigest()})
   if i<4:save(out/('trace-'+str(i)+'.json'),tb)
 finally:device.close()
 save(out/'fixtures.json',rows);calls=[t for row in rows for t in row['calls']]
 observed={hex(a):sum(t[1]==a for t in calls)for a in geometry.RANGES}
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'connected_geometry_boundary_movement_inventory_match','directory':str(out),'cases':len(rows),'geometry_function_calls':observed,'type1_calls':sum(t[1]==0x19f2c for t in calls),'type2_calls':sum(t[1]==0x19fda for t in calls),'redraw_cases':sum(t[1]==0x1b786 for t in calls),'remaining_top_level_scripted_helpers':['0xe4c0','0x191f4','0xf0fa','0xeb04','0x20820'],'remaining_nested_transition_helpers':['0x20e8c','0x20f0c','0xdf60','0x1aa40','0x20f78'],'additional_original_components':0,'rebuilt_original_CPU_instructions':0,'rebuilt_original_GPU_instructions':0,'game_frames_executed':0,
 'matched':['Original CPU executes all five geometry routines plus boundary/update/digit/inventory/text/sprite/submission code and originalGPUmovement/sprite overlays; rebuilt path uses compiledC.','Exact externalCPU read/write width/address/value/order, helper-call order/args, fullRAM except10formatter scratchbytes, finalblitterregisters and inventorypanel output.','Portal matching keys derived from originalCPU/GPU pre-helper state and originalportal prefix; old synthetic geometry replies/effects unused once implementations execute.'],
 'limits':['Five other top-level update helpers and five nested transition services remain scripted; selected rectangle/boundary geometry is implemented, not complete gameplay/collision/scene/audio.','Pinned emulatedblitter and synchronousGPUdispatcher completion model; no physicalhardware/concurrenttiming/unmodifiedBIOS proof.','PrivateCPUstack/formatter scratch/fullCCR/caller-savedABI excluded. Earlier standalonegeometry fixtures separately verify fullD0; linkedcaller consumes lowwords.']}
 save(out/'report.json',report);save(out/'status.json',{'status':'terminal','exit_code':0})
 if options.limit==256:save(ROOT/'verification/biwn-world-geometry-pipeline-checks.json',report)
 print(json.dumps(report),flush=True)
if __name__=='__main__':main()
