"""Native original three-task program versus C world/task/scheduler dispatch."""
import argparse,ctypes as c,hashlib,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
import task_runtime_native as original
import task_runtime_C as rebuilt
previous=original.previous;ROOT=original.ROOT;world=original.scheduler.cleanup.world;movement=previous.movement
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int,default=256);parser.add_argument('--case',type=int);parser.add_argument('--with-input',action='store_true');parser.add_argument('--with-dispatch',action='store_true');parser.add_argument('--with-camera',action='store_true');parser.add_argument('--with-animation',action='store_true');parser.add_argument('--with-targeting',action='store_true');opts=parser.parse_args()
 if opts.with_targeting:opts.with_animation=True
 if opts.with_animation:opts.with_camera=True
 if opts.with_camera:opts.with_dispatch=True
 if opts.with_dispatch:opts.with_input=True
 out=ROOT/('verification/biwn-task-targeting-runtime'if opts.with_targeting else'verification/biwn-task-animation-runtime'if opts.with_animation else'verification/biwn-task-camera-runtime'if opts.with_camera else'verification/biwn-task-dispatch-runtime'if opts.with_dispatch else'verification/biwn-task-input-runtime'if opts.with_input else'verification/biwn-task-runtime')/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libtasks.dylib'
 command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_scheduler.c'),str(source/'biwn_task_loops.c'),'-o',str(library)];run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
 mr=json.loads((ROOT/'verification/biwn-world-update-checks.json').read_text());ml=c.CDLL(str(Path(mr['directory'])/'libbiwn-world-update.dylib'));fn=ml.biwn_world_update;fn.argtypes=[c.POINTER(world.Bus)];fn.restype=c.c_int
 br=json.loads((ROOT/'verification/biwn-boundary-handlers-checks.json').read_text());bl=c.CDLL(str(Path(br['directory'])/'libboundary-handlers.dylib'));one=bl.biwn_boundary_type1;one.argtypes=[c.POINTER(world.Bus),c.c_uint16,c.c_uint16,c.c_uint16,c.c_uint32,c.POINTER(c.c_uint32)];one.restype=c.c_int;two=bl.biwn_boundary_type2;two.argtypes=[c.POINTER(world.Bus),c.c_uint32,c.c_uint16,c.c_uint32,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];two.restype=c.c_int;boundaries={0x19f2c:one,0x19fda:two}
 gr=json.loads((ROOT/'verification/biwn-geometry-checks.json').read_text());gl=c.CDLL(str(Path(gr['directory'])/'libgeometry.dylib'));geometry=previous.geometry.bind(gl)
 cr=json.loads((ROOT/'verification/biwn-transition-cleanup-checks.json').read_text());cl=c.CDLL(str(Path(cr['directory'])/'libcleanup.dylib'));cleanup=previous.cleanup.bind(cl)
 old=json.loads((ROOT/'verification/biwn-world-cleanup-pipeline-checks.json').read_text());old_rows=json.loads((Path(old['directory'])/'fixtures.json').read_text());snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rng=random.Random(0x1a544);native=original.Native();rows=[];PCs=set()
 input_backend=None;input_function=None;input_report=None
 if opts.with_input:
  import emulated_pad_input
  input_report=json.loads((ROOT/'verification/biwn-input-poll-checks.json').read_text());input_lib=c.CDLL(str(Path(input_report['directory'])/'libinput.dylib'));input_function=input_lib.biwn_input_poll;input_function.argtypes=[c.POINTER(world.Bus)];input_function.restype=c.c_int;input_backend=emulated_pad_input.Backend(native.lib,native.device)
 dispatch_backend=None;dispatch_functions=None
 if opts.with_dispatch:
  if opts.with_targeting:import task_targeting_backend as dispatch_backend
  elif opts.with_animation:import task_animation_backend as dispatch_backend
  else:import task_dispatch_backend as dispatch_backend
  import check_biwn_input_dispatch as dispatch
  dp=json.loads((ROOT/'verification/biwn-input-dispatch-checks.json').read_text());dl=c.CDLL(str(Path(dp['directory'])/'libdispatch.dylib'));df=dl.biwn_input_dispatch;df.argtypes=[c.POINTER(world.Bus),dispatch.W8,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];df.restype=c.c_int
  dv=json.loads((ROOT/'verification/biwn-signed-division-checks.json').read_text());dvl=c.CDLL(str(Path(dv['directory'])/'libdivision.dylib'));vf=dvl.biwn_signed_division;vf.argtypes=[c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32),c.POINTER(c.c_uint32)];vf.restype=c.c_int
  dispatch_functions={'dispatch':df,'division':vf,'write8_type':dispatch.W8}
 camera_functions=None
 if opts.with_camera:
  import check_biwn_camera as camera
  cp=json.loads((ROOT/'verification/biwn-camera-checks.json').read_text());camlib=c.CDLL(str(Path(cp['directory'])/'libcamera.dylib'));camera_functions=camera.bind(camlib)
  dispatch_backend.camera_linked=True;dispatch_backend.logged=list(dispatch_backend.logged)+[0xe540,0x13440];dispatch_backend.widths={**dispatch_backend.widths,0xe540:[4,4],0x13440:[2,2]}
 animation_functions=None;animation_backend=None
 if opts.with_animation:
  import check_biwn_animation as animation
  ap=json.loads((ROOT/'verification/biwn-animation-checks.json').read_text());al=c.CDLL(str(Path(ap['directory'])/'libanimation.dylib'));animation_functions=animation.bind(al);animation_backend=dispatch_backend.Clock(native.device)
 targeting_function=None
 if opts.with_targeting:
  import check_biwn_targeting as targeting
  tp=json.loads((ROOT/'verification/biwn-targeting-checks.json').read_text());tl=c.CDLL(str(Path(tp['directory'])/'libtargeting.dylib'));targeting_function=targeting.bind(tl)
 order=[0,36,47,85,150,12,35,56]+[i for i in range(256)if i not in [0,36,47,85,150,12,35,56]]
 if opts.case is not None:order=[opts.case];opts.limit=1
 try:
  for ordinal,index in enumerate(order[:opts.limit]):
   case=(dispatch_backend.fixture if dispatch_backend is not None else original.fixture)(old_rows[index]['parameters'],index)
   if opts.with_camera:
    counter=[0,1,59,60,61,119,120,121,0x7fff,0x8000,0xffff][index%11];factor=[0,1,27,0xffff,0x10000,0x80000000,0xffffffff][index%7]
    case['initial'] += [[0x3c840,2,counter],[0x3c842,4,factor],[0x3c846,4,[0,27,0xffffffff,0x80000000][index%4]],[0x49cc0,4,index%256]]
   registers=[rng.getrandbits(32)for _ in range(16)];a=(dispatch_backend.Script if dispatch_backend is not None else previous.prior.previous.Script)(snapshot,case);b=(dispatch_backend.Script if dispatch_backend is not None else previous.prior.previous.Script)(snapshot,case);save(out/'status.json',{'status':'running','case':ordinal,'source_case':index})
   oa,ra,cpu,meta=native.run(a,registers,input_backend=input_backend,dispatch_backend=dispatch_backend,animation_backend=animation_backend);runtime=rebuilt.Runtime(library,native.device,registers)
   if input_backend is not None:input_backend.start(case)
   if animation_backend is not None:animation_backend.start(case)
   ob,tb,rb,stats=movement.translated(fn,native.device,bytes(b.memory),b,boundaries,geometry,cleanup,runtime,input_function,input_backend,dispatch_functions,camera_functions,animation_functions,animation_backend,targeting_function)
   calls=[t for t in tb if t[0]=='call'];callee=[2,3,4,5,6,7,10,11,12,13,14];state_equal=all(cpu.registers[i]==runtime.cpu.registers[i]for i in callee+[15])and all(getattr(cpu,k)==getattr(runtime.cpu,k)for k in ['pc','usp','ssp'])and(cpu.sr&0xffe0)==(runtime.cpu.sr&0xffe0)
   equal=original.masked_equal(oa,ob)
   if input_backend is not None:
    assert meta['pad_input']=={'samples':input_backend.samples,'raw_reads':input_backend.raw_reads,'selects':input_backend.selects},('emulated_pad_trace',ordinal)
   if animation_backend is not None:
    assert meta['animation_environment_events']==animation_backend.events,('animation_environment',ordinal)
    assert all(oa[address]==value and ob[address]==value for address,value in case['animation_flag_values']),('animation_asset_flags_changed',ordinal)
   if not equal or calls!=meta['calls']or ra!=rb or runtime.handoffs!=meta['handoffs']or runtime.yields!=meta['yields']or not state_equal:
    save(out/'mismatch.json',{'case':ordinal,'source_case':index,'parameters':case,'RAM_match':equal,'calls_match':calls==meta['calls'],'registers_match':ra==rb,'continuation_state_match':state_equal,'original_CPU':original.scheduler.cpu_dict(cpu),'C_CPU':original.scheduler.cpu_dict(runtime.cpu),'original_calls':meta['calls'],'C_calls':calls,'original_handoffs':meta['handoffs'],'C_handoffs':runtime.handoffs,'original_yields':meta['yields'],'C_yields':runtime.yields,'RAM_differences':[[j,oa[j],ob[j]]for j in range(len(oa))if oa[j]!=ob[j]][:200]});raise AssertionError(str(out/'mismatch.json'))
   PCs.update(meta['PCs']);rows.append({'case':ordinal,'source_case':index,'parameters':case,'native_CPU_instructions':len(meta['PCs']),'original_handoffs':meta['handoffs'],'original_yields':meta['yields'],'calls':calls,'rebuilt':runtime.metadata(),'device':stats,'RAM_except_declared_private_state_match':True,'blitter_registers_match':True,'inventory_frame_sha256':hashlib.sha256(ob[movement.frame.FRAME_START:movement.frame.FRAME_END]).hexdigest(),'emulated_pad_input':meta.get('pad_input'),'dispatch_states_observed':meta['dispatch_states'],'animation_environment_events':meta.get('animation_environment_events')})
 except Exception as error:
  save(out/'error.json',{'error':repr(error),'case':ordinal,'source_case':index});save(out/'status.json',{'status':'terminal_failed','case':ordinal,'source_case':index});raise
 finally:native.close()
 save(out/'fixtures.json',rows)
 if opts.limit!=256:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'preflight_cases':len(rows),'directory':str(out)}));return
 session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();ranges={0x1a544:0x1a552,0xf360:0xf368,0xf880:0xf888};decoded=[]
 for a,b in ranges.items():part,_=world.select.binary_tools.m68k_instructions(image[a-0x4000:b-0x4000],a);decoded+=part
 missing=[x for x in decoded if x['address']not in PCs];save(out/'task-loop-decode.json',{'instructions':decoded,'uncovered':missing});assert not missing
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'three_original_task_loops_world_scheduler_match_C','directory':str(out),'cases':len(rows),'world_update_calls':sum(x['rebuilt']['world_body_calls']for x in rows),'task_handoffs':sum(len(x['original_handoffs'])for x in rows),'world_inner_yields':sum(y['return_PC']in[0x19f8e,0x1a0bc]for x in rows for y in x['original_yields']),'inventory_redraw_calls':sum(t[1]==0x1b786 for x in rows for t in x['calls']),'new_original_components':3,'task_loop_CPU_instruction_coverage':[len(decoded),len(decoded)],'original_task_loop_bytes':30,'task_contexts':[hex(x)for x in original.CONTEXTS],'task_entries':[hex(x)for x in original.ENTRIES],'original_captured_ring_contexts':21,'other_task_bodies_unported':18,'scheduler_linked_for_three_task_runtime':True,'remaining_top_level_scripted_helpers':['0xe4c0','0x191f4','0xf0fa','0xeb04','0x20820'],'remaining_nested_scripted_helpers':['0x1aa40','0x20f78'],'rebuilt_original_CPU_instructions':0,'rebuilt_original_GPU_instructions':0,'game_frames_executed':0,'source_sha256':{name:world.select.binary_tools.sha(source/name)for name in ['biwn_task_loops.c','biwn_task_loops.h','biwn_scheduler.c','biwn_scheduler.h']},'compiler':command,
 'matched':['Native original CPU runs world update, actual scheduler/TRAP/RTE and allthree original task loops; originalGPU movement/sprite overlays complete synchronously through the pinned bridge. Rebuilt path uses C only for those game routines.','Two world updates per case, all helper-call order/args, task-switch order and selected PC/SP, final callee-saved registers/stack banks, visibleRAM under explicit exclusions, blitterregisters and inventorypixels.','Inner world-boundary yield suspends host world C, dispatches the two real yield-only task bodies, then resumes the correct boundary continuation. No immediate-return yield stub on this path.'],
 'limits':['Three-task subset of21captured game contexts;18other task bodies unported, so not complete task/main-loop/game integration. Five top-level and two scene/texture services remain scripted.','Private user/supervisor task stacks,10formatter scratchbytes and savedSR low5CCRbits excluded. World caller-saved registers/CCR are outside its prior C contract; scheduler standalone512cases separately checks fullCPUstate.','Virtual world/boundary stack depths come from original source ABI and were confirmed by native yield SP observations. Other task bodies/reentrant world calls are unsupported rather than silently executed.','Native CPU watchread values/widths unavailable; this connected check proves RAM/control flow/call order, not a new fullnativebus-width trace. Previous separate component/originalUnicorn bus checks remain evidence.','Pinned blitter and synchronousGPU completion model, no externalinterrupts/physicalhardware/unmodifiedBIOS/wholeviewport/audio or full gameframes.']}
 if opts.with_input:
  report.update(status='three_task_runtime_with_original_input_poll_matches_C',input_poll_linked=True,input_poll_calls=sum(len(x['emulated_pad_input']['samples'])for x in rows),raw_MMIO_reads=sum(len(x['emulated_pad_input']['raw_reads'])for x in rows),new_original_components=0,remaining_top_level_scripted_helpers=['0x191f4','0xf0fa','0xeb04','0x20820'],input_poll_library=str(Path(input_report['directory'])/'libinput.dylib'))
  report['limits'][0]=report['limits'][0].replace('Five top-level','Four top-level')
  report['source_sha256'].update(input_report['source_sha256']);report['matched'].append('Real original/C polling code derives held state and press edges from matching four-row emulatedpad readings; original CPU executesE4C0 rather than a return stub.')
  report['limits'].append('Existing pinned ordinarypad backend and synthetic externalclock samples at poll boundaries. Requested legacy input masks are mapped to observed supported core-button bits; unreachable bit31 is not fabricated. No physicalpad or independent hardware accuracy proof.')
 if opts.with_dispatch:
  report.update(status='three_task_runtime_with_real_input_dispatch_poll_division_matches_C',input_dispatch_linked=True,signed_division_linked=True,
   input_dispatch_calls=sum(t[1]==0x191f4 for x in rows for t in x['calls']),signed_division_calls=sum(t[1]==0xe588 for x in rows for t in x['calls']),
   dispatcher_animation_wait_yields=sum(y['return_PC']in[0x194e6,0x1968e]for x in rows for y in x['original_yields']),
   dispatcher_wait_return_PCs=sorted({hex(y['return_PC'])for x in rows for y in x['original_yields']if y['return_PC']in[0x194e6,0x1968e]}),
   program_dependency_target_call_counts={hex(a):sum(t[1]==a for x in rows for t in x['calls'])for a in dispatch.HELPERS},
   remaining_top_level_scripted_helpers=['0xf0fa','0xeb04','0x20820'],remaining_nested_scripted_helpers=sorted({hex(x)for x in[0x1aa40,0x20f78]+dispatch_backend.Backend.extra_stubs}),
   dispatcher_states_observed=sorted({state for row in rows for state in row['dispatch_states_observed']}),
   original_dispatcher_instruction_coverage=[sum(0x191f4<=x<0x192a2 or 0x192bc<=x<0x19f2c for x in PCs),816])
  assert report['dispatcher_states_observed']==list(range(13)) and report['inventory_redraw_calls']>0 and report['dispatcher_wait_return_PCs']==['0x194e6','0x1968e']
  report['source_sha256'].update(dp['source_sha256']);report['source_sha256'].update(dv['source_sha256'])
  report['limits'][0]='Three-task subset of21captured contexts;18other task bodies unported. Three top-level update services and explicitly listed nested equipment/scene/text/allocator services remain scripted. Fewer top-level stubs does not imply fewer total unfinished services.'
  report['limits'].append('Dispatcher animation/equipment data, allocator handles, completion flags and external button/clock samples are supplied fixtures. Original free-handle and signed division execute on the original path; C counterparts execute on the rebuilt path. Other equipment/scene services are explicit RTS boundaries. No original zero-divisor exception proof.')
  report['matched'].append('Complete input dispatcher executes on native original CPU and compiled C. Its two animation-wait yield continuations really dispatch both yield-only tasks and resume with matching PC/SP. Signed division and free-handle calls are linked to real original/C implementations.')
 if opts.with_camera:
  report.update(status='three_task_runtime_with_real_camera_dispatch_poll_matches_C',camera_linked=True,multiply_linked=True,direction_linked=True,
   camera_calls=sum(t[1]==0xf0fa for row in rows for t in row['calls']),multiply_calls=sum(t[1]==0xe540 for row in rows for t in row['calls']),direction_calls=sum(t[1]==0x13440 for row in rows for t in row['calls']),
   signed_division_calls=sum(t[1]==0xe588 for row in rows for t in row['calls']),remaining_top_level_scripted_helpers=['0xeb04','0x20820'],
   original_camera_instruction_coverage={hex(a):[sum(a<=x<b for x in PCs),len(world.select.binary_tools.m68k_instructions(snapshot[a:b],a)[0])]for a,b in camera.RANGES.items()if a in[0xe540,0x13440,0xf0fa]})
  report['source_sha256'].update(cp['source_sha256']);report['source_sha256'].update(mr['source_sha256'])
  report['limits'][0]='Three-task subset of21captured contexts;18other task bodies unported. Two top-level animation/entity services and15explicit nested equipment/scene/text/allocator/texture services remain scripted; cameraF0FA and its multiply/direction helpers are real original/C code.'
  report['matched'].append('CameraF0FA, multiplyE540 and direction13440 run on original nativeCPU and compiledC. Both world and camera submissions execute original GPU4320 or Cmovement, with matching fullvisibleRAM, blitter state and inventory pixels. WorldF0FA adapter exposes actual lowD2/lowD3 register seeds as logicalinputs; they are not original stackarguments.')
  report['limits'].append('Earlier terrainF0FA label was incorrect: source updates camera offsets/angles and submits movement. Normalpath returns finalshared3C846 (normally27); debugpath retains priorsharedvalue. Exact observable effects, not a recovered originalsymbol or fullterrain/scene implementation.')
 if opts.with_animation:
  report.update(status='three_task_runtime_with_real_animation_queue_camera_dispatch_matches_C',animation_update_linked=True,animation_queue_linked=True,
   animation_update_calls=sum(t[1]==0xeb04 for row in rows for t in row['calls']),animation_queue_calls=sum(t[1]==0xeac4 for row in rows for t in row['calls']),
   animation_delta_events=sum(len(row['animation_environment_events'])for row in rows),animation_completion_flags_scripted=False,animation_asset_flags_unchanged=True,immutable_animation_flags_per_case=len(rows[0]['parameters']['animation_flag_values']),
   animation_original_instruction_coverage=[sum(0xeac4<=pc<0xec04 for pc in PCs),101],remaining_top_level_scripted_helpers=['0x20820'])
  report['source_sha256'].update(ap['source_sha256'])
  report['limits'][0]='Three-task subset of21captured contexts;18other task bodies unported. One top-level entity service and15explicit nested equipment/scene/text/allocator/texture services remain scripted. Animation update/queue, camera and their linked helpers execute real original/C code.'
  report['limits']=[x.replace('animation/equipment data, allocator handles, completion flags and external button/clock samples','equipment data, allocator handles and external button/clock samples')for x in report['limits']]
  report['limits'].append('Finite synthetic animation assets and equal external delta-word samples at each EB04 entry; completion flags are immutable after seeding and no animation return/completion stub executes. The queue consumer/model/pose processing and a full hardware clock are unported. Command generation is not full animated model rendering.')
  report['matched'].append('Original/C EB04 advance real frame pointers and countdowns; EAC4 writes actual queued requests. Dispatcher waits inspect flags at the newly selected records, with matching scheduler continuations. External delta events are recorded identically and do not write frame flags.')
 if opts.with_targeting:
  report.update(status='three_task_world_direct_helpers_linked_original_C_match',targeting_linked=True,all_direct_world_helpers_linked=True,
   targeting_calls=sum(t[1]==0x20820 for row in rows for t in row['calls']),multiply_calls=sum(t[1]==0xe540 for row in rows for t in row['calls']),direction_calls=sum(t[1]==0x13440 for row in rows for t in row['calls']),
   signed_division_calls=sum(t[1]==0xe588 for row in rows for t in row['calls']),remaining_top_level_scripted_helpers=[],
   targeting_original_instruction_coverage=[sum(0x20820<=pc<0x20a9c for pc in PCs),183])
  assert report['world_inner_yields']>0
  report['source_sha256'].update(tp['source_sha256'])
  report['limits'][0]='Three-task subset of21captured contexts;18other task bodies unported. Every direct world-update helper is real original/C code, but15explicit nested equipment/scene/text/allocator/texture services remain scripted. Queue consumer/pose processing, actor/transform producers and a full hardware clock remain unfinished.'
  report['limits'].append('Finite synthetic targeting candidate/transform records; no full actorAI/collision lifecycle or renderedcrosshair/wholeviewport proof. Zero top-level stubs does not mean a complete game.')
  report['matched'].append('Original/C targeting20820 executes its40-record selection, projection/cursor fields and low-distance loop through real direction/multiply/division helpers. Full visible RAM and ordered calls remain equal with the declared task/private-state exclusions.')
 save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/('verification/biwn-task-targeting-runtime-checks.json'if opts.with_targeting else'verification/biwn-task-animation-runtime-checks.json'if opts.with_animation else'verification/biwn-task-camera-runtime-checks.json'if opts.with_camera else'verification/biwn-task-dispatch-runtime-checks.json'if opts.with_dispatch else'verification/biwn-task-input-runtime-checks.json'if opts.with_input else'verification/biwn-task-runtime-checks.json'),report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
