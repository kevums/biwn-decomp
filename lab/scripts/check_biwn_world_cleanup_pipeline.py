"""Connect real transition cleanup to geometry/boundary/movement/inventory."""
import argparse,ctypes as c,hashlib,json,random
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_transition_cleanup as cleanup
import check_biwn_world_geometry_pipeline as prior
geometry=prior.geometry;movement=prior.movement;world=prior.world;ROOT=world.ROOT
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int,default=256);opts=parser.parse_args()
 main_report=json.loads((ROOT/'verification/biwn-world-update-checks.json').read_text());main_lib=c.CDLL(str(Path(main_report['directory'])/'libbiwn-world-update.dylib'));fn=main_lib.biwn_world_update;fn.argtypes=[c.POINTER(world.Bus)];fn.restype=c.c_int
 br=json.loads((ROOT/'verification/biwn-boundary-handlers-checks.json').read_text());blib=c.CDLL(str(Path(br['directory'])/'libboundary-handlers.dylib'));one=blib.biwn_boundary_type1;one.argtypes=[c.POINTER(world.Bus),c.c_uint16,c.c_uint16,c.c_uint16,c.c_uint32,c.POINTER(c.c_uint32)];one.restype=c.c_int;two=blib.biwn_boundary_type2;two.argtypes=[c.POINTER(world.Bus),c.c_uint32,c.c_uint16,c.c_uint32,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];two.restype=c.c_int;boundaries={0x19f2c:one,0x19fda:two}
 gr=json.loads((ROOT/'verification/biwn-geometry-checks.json').read_text());glib=c.CDLL(str(Path(gr['directory'])/'libgeometry.dylib'));geometry_functions=geometry.bind(glib)
 cr=json.loads((ROOT/'verification/biwn-transition-cleanup-checks.json').read_text());clib=c.CDLL(str(Path(cr['directory'])/'libcleanup.dylib'));cleanup_functions=cleanup.bind(clib)
 old=json.loads((ROOT/'verification/biwn-world-geometry-pipeline-checks.json').read_text());old_rows=json.loads((Path(old['directory'])/'fixtures.json').read_text());snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
 out=ROOT/'verification/biwn-world-cleanup-pipeline'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);rng=random.Random(0x20e8c);rows=[];device=movement.Device()
 try:
  for i,row in enumerate(old_rows[:opts.limit]):
   case=dict(row['parameters']);case['initial']=list(case['initial']);container=0x85000;node=0x82000;ids=0x8e000
   # Geometry and cleanup share the actual original headers. Region cleanup
   # uses node+2 as a signed six-byte-table offset; place its group record
   # beyond the parent's boundary-match records without replacing that table.
   case['initial'] += [[container+6,2,i%4],[container+20,4,ids],[node+2,2,16],[0x90060,2,2],[0x90062,2,0x200],[0x90064,2,0x206],[0x112d60,4,0],[0x112d64,4,0xfffffff0]]
   for room in range(25):case['initial'].append([0x49bb4+room*4,4,container])
   for j in range(4):case['initial'].append([ids+j*2,2,0x200+j])
   for j in range(36):case['initial'] += [[0x15b4a0+j*4,2,0x200+j],[0x15b4a2+j*4,2,[0,1,64,0xffff][(i+j)%4]]]
   for j in range(40):
    handle=0x160000+j*4;block=0x170000+j*0x80
    case['initial'] += [[0x49d6e+j*206,2,0xa55a],[0x4bd9c+j*30,2,0 if(i+j)%3==0 else 1],[0x4bdb0+j*30,4,handle if j%5 else 0],[handle,4,block+8 if j%7 else 0],[block,4,0x40]]
   save(out/'status.json',{'status':'running','case':i});a=prior.previous.Script(snapshot,case);b=prior.previous.Script(snapshot,case);ram=bytes(a.memory)
   oa,ta,ra,meta=movement.original(device,ram,a,[rng.getrandbits(32)for _ in world.REGS],boundary_helpers=True,geometry_helpers=True,cleanup_helpers=True)
   ob,tb,rb,stats=movement.translated(fn,device,ram,b,boundaries,geometry_functions,cleanup_functions)
   equal=oa[:0x15b7a0]==ob[:0x15b7a0]and oa[0x15b7aa:]==ob[0x15b7aa:]
   if not equal or ta!=tb or ra!=rb:
    save(out/'mismatch.json',{'case':i,'parameters':case,'RAM_match':equal,'original_trace':ta,'C_trace':tb,'original_blitter_registers':ra,'C_blitter_registers':rb,'RAM_differences':[[j,oa[j],ob[j]]for j in range(len(oa))if oa[j]!=ob[j]][:100]});raise AssertionError(str(out/'mismatch.json'))
   calls=[t for t in tb if t[0]=='call'];rows.append({'case':i,'parameters':case,'original':meta,'rebuilt':stats,'calls':calls,'CPU_external_bus_and_outer_helper_calls_match':True,'RAM_except_formatter_scratch_match':True,'blitter_registers_match':True,'inventory_frame_sha256':hashlib.sha256(ob[movement.frame.FRAME_START:movement.frame.FRAME_END]).hexdigest()})
   if any(meta['cleanup_function_entries'].values())and not(out/'example-cleanup-trace.json').exists():save(out/'example-cleanup-trace.json',tb)
 finally:device.close()
 save(out/'fixtures.json',rows);calls=[t for row in rows for t in row['calls']];observed={hex(entry):sum(row['original']['cleanup_function_entries'].get(hex(entry),0)for row in rows)for entry in cleanup.RANGES}
 if opts.limit==256:assert all(n>0 for n in observed.values()),observed
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'connected_cleanup_geometry_movement_inventory_match','directory':str(out),'cases':len(rows),'original_cleanup_function_entries':observed,'geometry_function_calls':{hex(a):sum(t[1]==a for t in calls)for a in geometry.RANGES},'type1_calls':sum(t[1]==0x19f2c for t in calls),'type2_calls':sum(t[1]==0x19fda for t in calls),'redraw_cases':sum(t[1]==0x1b786 for t in calls),'remaining_top_level_scripted_helpers':['0xe4c0','0x191f4','0xf0fa','0xeb04','0x20820'],'remaining_nested_transition_helpers':['0xdf60','0x1aa40','0x20f78'],'additional_original_components':0,'rebuilt_original_CPU_instructions':0,'rebuilt_original_GPU_instructions':0,'game_frames_executed':0,
 'matched':['Original CPU executes real cleanup/free/reference functions plus geometry/boundary/update/render/submission and originalGPU4320/4B00; rebuilt path uses compiledC.','Exact externalCPU bus read/write value/width/address/order and outer helper calls, wholeRAM except10formatter scratchbytes, finalblitterregisters and inventorypanel pixels.','Cleanup function-entry counts reported explicitly; no internal cleanup helper stubs. Prior scripted cleanup effects/replies unused.'],
 'limits':['Five other top-level helpers and three nested trap/texture-initialization/scene-load services remain scripted; complete collision/gameplay/scene/main loop/audio/game unfinished.','PrivateCPUstack/formatter scratch/fullCCR and caller-saved ABI excluded. Standalone cleanup separately checks fullD0; current boundary caller discards resetD0.','Pinned emulatedblitter and synchronousGPUdispatcher model; no physicalhardware/unmodifiedBIOS/concurrenttiming proof.']}
 save(out/'report.json',report);save(out/'status.json',{'status':'terminal','exit_code':0})
 if opts.limit==256:save(ROOT/'verification/biwn-world-cleanup-pipeline-checks.json',report)
 print(json.dumps(report),flush=True)
if __name__=='__main__':main()
