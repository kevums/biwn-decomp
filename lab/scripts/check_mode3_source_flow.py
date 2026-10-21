"""Prototype uninterrupted supplied11E6C source task,constructor/disc/scene/GPU.

Experimental selector13 overlay; controlled ring,BIOS and initial residentGPU
are fixtures. No boot,naturalcaller,device timing orwhole-game claim.
"""
import argparse,ctypes as c,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_media_setup_cpu as media
import check_biwn_actor_full_movement_runtime as actor
import check_biwn_movie_GPU as gpu
import check_biwn_gpu_dispatcher as dispatcher
import emulated_pad_input as pad
from biwn_disc_backend import Disc
ROOT=media.ROOT;save=media.save;sha=media.sha;SP=0x1f8000;SSP=0x1ff000;MAIN=0xc2128;IDLE=0xc5928;BOUNDARY=0x11e86

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--frames',type=int,default=3);parser.add_argument('--inline-selector',action='store_true');parser.add_argument('--inventory-entry',action='store_true');parser.add_argument('--exit-viewer',action='store_true');parser.add_argument('--world-entry',action='store_true');parser.add_argument('--world-loop',action='store_true');parser.add_argument('--recorded-machine',action='store_true');options=parser.parse_args();assert 1<=options.frames<=64;assert not options.inventory_entry or options.inline_selector;assert not options.exit_viewer or options.inventory_entry;assert not options.world_entry or options.exit_viewer;assert not options.world_loop or options.world_entry;assert not options.recorded_machine or options.world_loop
 proof_name='mode3-recorded-world-loop-roundtrip' if options.recorded_machine else 'mode3-world-loop-roundtrip' if options.world_loop else 'mode3-world-roundtrip' if options.world_entry else 'mode3-inventory-roundtrip' if options.exit_viewer else 'mode3-inventory-entry' if options.inventory_entry else 'mode3-source-flow-inline' if options.inline_selector else 'mode3-source-flow'
 selector_dir='selector13-inline' if options.inline_selector else 'selector13'
 out=ROOT/'verification'/proof_name/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_interior_loading_cpu.c','biwn_resource_cpu.c','biwn_cd_cpu.c','biwn_scheduler.c','biwn_task_loops.c','biwn_media_setup_cpu.c','biwn_gpu_projection_submit_cpu.c','biwn_gpu_draw_submit_cpu.c','biwn_render_queue_cpu.c','biwn_scene_draw_cpu.c','biwn_display_list_cpu.c','biwn_formatter_cpu.c','biwn_overlay_text_cpu.c','biwn_startup_rng_math_cpu.c','biwn_gpu4720_submit_cpu.c','biwn_rng_cpu.c','biwn_signed_division.c','biwn_camera.c','biwn_input_poll_cpu.c']
 files=[source/name for name in names]+[source/'experimental'/selector_dir/'biwn_scene_constructor_cpu.c',source/'experimental/mode3-flow/biwn_mode3_scene_flow_cpu.c'];library=out/'libmode3-flow.dylib'
 if options.inventory_entry:files += [source/'experimental/mode3-inventory/biwn_mode3_inventory_helpers_cpu.c',source/'experimental/mode3-inventory/biwn_input_dispatch_cpu.c']
 if options.world_entry:files += [source/'experimental/mode3-inventory/biwn_world_flow_cpu.c',*[source/n for n in ['biwn_camera_cpu.c','biwn_targeting_cpu.c','biwn_actor_direction.c','biwn_movement_submit_cpu.c','biwn_animation_cpu.c']]]
 compiler=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(source),*map(str,files),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(compiler.stdout+compiler.stderr);assert compiler.returncode==0,compiler.stderr
 session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mappings={'constructor':json.loads((ROOT/'verification'/('scene-constructor-selector13-inline-generation-current.json' if options.inline_selector else 'scene-constructor-selector13-generation-current.json')).read_text()),'flow':json.loads((ROOT/'verification/mode3-scene-flow-generation-current.json').read_text())}
 for group,name in [('interior','interior-loading'),('resource','resource'),('cd','cd-wrapper'),('media','media-setup'),('projection','gpu-projection-submit'),('draw','gpu-draw-submit'),('queue','render-queue'),('scene_draw','scene-draw'),('display_list','display-list'),('formatter','formatter'),('text','overlay-text')]:mappings[group]=json.loads((session/(name+'-fullCPU-generation.json')).read_text())
 if options.inventory_entry:
  mappings['inventory']=json.loads((ROOT/'verification/mode3-inventory-bridge-generation-current.json').read_text())
  mappings['input_dispatch']=json.loads((session/'input-dispatch-fullCPU-generation.json').read_text())
  import generate_biwn_input_dispatch_cpu as input_gen
  image=(session/'nextstage-68000-candidate.bin').read_bytes()
  mappings['input_dispatch']['instructions_decoded']=sum((input_gen.binary_tools.m68k_instructions(image[low-0x4000:high-0x4000],low)[0]for low,high in [(0x191f4,0x192a2),(0x192bc,0x19f2c)]),[])
 if options.world_entry:mappings['world_flow']=json.loads((session/'world-flow-fullCPU-generation.json').read_text())
 recorded=json.loads((ROOT/'verification/mode3-recorded-machine-restore-current.json').read_text())if options.recorded_machine else None
 checkpoint_core=Path(recorded['core_path'])if recorded else None
 rows={k:v.get('instructions_decoded',v.get('decoded'))for k,v in mappings.items()};sets={k:{r['address']for r in v}for k,v in rows.items()};runtime=media.Runtime(library,sum(rows.values(),[]),diagnostic_core=checkpoint_core);runtime.device.close();device_build=json.loads((ROOT/'verification'/('mode3-world-render-device-build-current.json' if options.world_entry else 'mode3-scene-render-device-build-current.json')).read_text());runtime.device=actor.Device(Path(device_build['library']),core=checkpoint_core);runtime.oracle.device=runtime.device
 lib=runtime.device.lib;submit=lib.lab_scene_render_submit;submit.argtypes=[c.c_void_p,c.c_uint32,c.c_uint32];submit.restype=c.c_int;renderer_mode=lib.lab_retained_renderer_mode;renderer_mode.argtypes=[c.c_uint];renderer_mode.restype=c.c_int;stat=lib.lab_scene_render_stat;stat.argtypes=[c.c_uint];stat.restype=c.c_uint64;pc_hash=lib.lab_scene_render_PC_hash;pc_hash.restype=c.c_uint64
 runtime.core.GPUStateLoad.argtypes=[c.c_void_p];runtime.core.GPUStateLoad.restype=c.c_size_t;runtime.core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];runtime.core.GPUReadLong.restype=c.c_uint32
 prefixes={'constructor':'scene_constructor','flow':'mode3_scene_flow','interior':'interior_loading','resource':'resource','cd':'cd','media':'media_setup','projection':'gpu_projection_submit','draw':'gpu_draw_submit','queue':'render_queue','scene_draw':'scene_draw','display_list':'display_list','formatter':'formatter','text':'overlay_text'};functions={}
 if options.inventory_entry:prefixes.update(inventory='mode3_inventory_helpers',input_dispatch='input_dispatch')
 if options.world_entry:prefixes['world_flow']='world_flow'
 for group,name in prefixes.items():
  fn=getattr(runtime.lib,'biwn_'+name+'_cpu_body');fn.argtypes=runtime.fn.argtypes;fn.restype=c.c_int;functions[group]=fn
 cube=runtime.lib.biwn_gpu4720_submit_cpu_body;cube.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),c.c_uint32];cube.restype=c.c_int
 poll=runtime.lib.biwn_input_poll_cpu_body;poll.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU)];poll.restype=c.c_int
 if options.world_entry:
  camera=runtime.lib.biwn_camera_cpu_body;camera.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),media.W8,media.world_cpu.SERVICE,c.c_void_p];camera.restype=c.c_int
  target_fn=runtime.lib.biwn_targeting_cpu_body;target_fn.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),media.world_cpu.SERVICE,c.c_void_p];target_fn.restype=c.c_int
  direction=runtime.lib.biwn_actor_direction_body;direction.argtypes=poll.argtypes;direction.restype=c.c_int
  movement=runtime.lib.biwn_movement_submit_cpu_body;movement.argtypes=cube.argtypes;movement.restype=c.c_int
  animation=runtime.lib.biwn_animation_cpu_body;animation.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),c.c_uint32];animation.restype=c.c_int
 math=runtime.lib.biwn_startup_rng_math_cpu_body;math.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU)];math.restype=c.c_int
 yielding=runtime.lib.biwn_scheduler_yield;yielding.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),c.c_uint32];yielding.restype=c.c_int
 idle=runtime.lib.biwn_task_loop_step;idle.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),c.c_void_p,c.c_void_p,c.c_uint32];idle.restype=c.c_int
 atlas=(source/'experimental'/selector_dir/'patched-test-RAM.bin').read_bytes();ram=bytearray(atlas)
 if options.inventory_entry:
  ram=bytearray((ROOT/'runs/zero-warm-whole-merchant-CPU-GPU-DSP/final-RAM.bin').read_bytes())
  for patch in mappings['constructor']['patches']:
   address=int(patch['address'],16);original=bytes.fromhex(patch['original']);replacement=bytes.fromhex(patch['replacement']);assert ram[address:address+len(original)]==original;ram[address:address+len(replacement)]=replacement
 for instructions in rows.values():
  for row in instructions:assert ram[row['address']:row['address']+row['size']].hex()==row['bytes']
 def put(a,w,v):ram[a:a+w]=(v&((1<<(w*8))-1)).to_bytes(w,'big')
 for a,w,v in [(SP,4,0x190000),(0x80,4,0xde08),(0xc0920,4,MAIN),(0x400e4,2,0),(0x403cc,2,0),(0x47b80,2,0),(0x47b82,2,0)]:put(a,w,v)
 for context,other,pc,sp in [(MAIN,IDLE,0x11e6c,SP),(IDLE,MAIN,0xf360,IDLE+0x400)]:
  for offset,width,value in [(0,4,other),(4,4,other),(8,4,pc),(12,4,sp),(16,4,pc),(20,2,0),(22,4,0),(26,4,0),(30,4,0),(34,4,0)]:put(context+offset,width,value)
 initial=media.CPU();initial.registers[15]=SP;initial.pc=0x1a544 if options.world_loop else 0x1a188 if options.world_entry else 0x191f4 if options.inventory_entry else 0x11e6c;initial.usp=SP;initial.ssp=SSP;initial.sr=0;phases={};results=[]
 def GPU_bytes():
  raw=c.create_string_buffer(8192);size=runtime.savers['GPU'](raw);assert size>4396;return raw.raw[:size]
 try:
  for mode in ['native','C']:
   if options.recorded_machine:
    assert sha(checkpoint_core.read_bytes())==recorded['core_sha256']
    runtime.device.seed(bytes(ram),int(mode=='C'))
    class Game(c.Structure):_fields_=[('path',c.c_char_p),('data',c.c_void_p),('size',c.c_size_t),('meta',c.c_char_p)]
    runtime.core.retro_load_game.argtypes=[c.POINTER(Game)];runtime.core.retro_load_game.restype=c.c_bool
    assert runtime.core.retro_load_game(c.byref(Game(str(ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi').encode(),None,0,None)))
    state_blob=Path(recorded['state_path']).read_bytes();assert sha(state_blob)==recorded['state_sha256']
    runtime.core.retro_unserialize.argtypes=[c.c_void_p,c.c_size_t];runtime.core.retro_unserialize.restype=c.c_bool;assert runtime.core.retro_unserialize(c.create_string_buffer(state_blob),len(state_blob))
    runtime.core.retro_serialize_size.restype=c.c_size_t;runtime.core.retro_serialize.argtypes=[c.c_void_p,c.c_size_t];runtime.core.retro_serialize.restype=c.c_bool;raw_state=c.create_string_buffer(runtime.core.retro_serialize_size());assert runtime.core.retro_serialize(raw_state,len(raw_state))and raw_state.raw==state_blob
    runtime.device.pointer=runtime.device.lib.lab_device_ram();assert sha(runtime.device.ram())==recorded['RAM_sha256']
    c.memmove(runtime.device.pointer,bytes(ram),len(ram));runtime.trace_count=0;runtime.trace=__import__('hashlib').sha256();runtime.bus_events=[];runtime.errors=[]
    assert renderer_mode(int(mode=='C'))==0;lib.lab_scene_render_reset()
   else:
    runtime.reset(bytes(ram),0);assert renderer_mode(int(mode=='C'))==0;lib.lab_scene_render_reset();raw=GPU_bytes();state=gpu.state_from_raw(raw);state.registers[:]=((c.c_uint32*32)*2)();state.local_RAM[:512]=ram[0x40a8:0x42a8];state.pc=0xf031be;state.control=0x2801;state.flags=0xd0;state.z=state.n=state.c=0;state.active_bank=0
    for offset,value in [(0x200,0),(0x204,0xffffffff),(0x208,0x52e0)]:state.local_RAM[offset:offset+4]=value.to_bytes(4,'big')
    supplied=gpu.logical(state)+raw[4396:];assert runtime.core.GPUStateLoad(c.create_string_buffer(supplied))==len(supplied)
    if mode=='native':
     runtime.core.GPUGetPC.restype=c.c_uint32;runtime.core.GPUExec.argtypes=[c.c_int32]
     for _ in range(32):
      if runtime.core.GPUGetPC()==0xf031ce and runtime.core.GPUReadLong(0xf03200,0)==0:break
      runtime.core.GPUExec(1)
     else:raise AssertionError('Native initial source resident idle limit')
    else:
     runtime.core.GPUWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32]
     def rd(_,a,v):v[0]=runtime.core.GPUReadLong(a,3);return 0
     def wr(_,a,v):runtime.core.GPUWriteLong(a,v,3);return 0
     cb=[dispatcher.R32(rd),dispatcher.W32(wr),dispatcher.TRACE(lambda *_:None)];db=dispatcher.Bus(*cb,None);ds=dispatcher.State();ds.registers[:]=state.registers
     for field in ['pc','z','c','n']:setattr(ds,field,getattr(state,field))
     tick=lib.biwn_gpu_dispatcher_run;tick.argtypes=[c.POINTER(dispatcher.Bus),c.POINTER(dispatcher.State),c.c_uint32,c.c_uint32];tick.restype=c.c_int;assert tick(c.byref(db),c.byref(ds),100,1)==0
     current=GPU_bytes();state=gpu.state_from_raw(current);state.registers[:]=ds.registers
     for field in ['pc','z','c','n']:setattr(state,field,getattr(ds,field))
     supplied=gpu.logical(state)+current[4396:];assert runtime.core.GPUStateLoad(c.create_string_buffer(supplied))==len(supplied)
   disc=Disc();cpu=media.CPU.from_buffer_copy(bytes(initial));events=[];bios=[];errors=[];trace=[]
   pads=pad.Backend(runtime.core,runtime.device)
   opcode_counter=c.c_uint32.in_dll(runtime.core,'gpu_exec_opcode_count');original_GPU_start=opcode_counter.value
   def read(width):
    def callback(_,a,v):v[0]=runtime.read(a,width);return 0
    return callback
   def command(value):
    status=submit(None,0xf03204,value)
    if status:save(out/'failed-command.json',dict(mode=mode,command=hex(value),status=status,header=hex(runtime.core.GPUReadLong(0xf03208,0))))
    assert not status,(mode,hex(value),status);events.append(dict(command=hex(value),GPU=sha(GPU_bytes()[:4396]),RAM=sha(runtime.device.ram()),PC_count=stat(9),PC_hash=hex(pc_hash())))
   def write(width):
    def callback(_,a,v):
     if a&0xffffff==0xf03204 and v in [0x4320,0x4720,0x52e0,0x57a0]:command(v)
     else:runtime.write(a,width,v)
     return 0
    return callback
   world=media.scheduler.cleanup.world;callbacks=[world.R8(read(1)),world.R16(read(2)),world.R32(read(4)),world.W16(write(2)),world.W32(write(4)),media.W8(write(1))];bus=media.Bus(*callbacks[:5],world.CALL(),None,0)
   def service(_,passed,state,target):
    if target==0x11e6c and options.inventory_entry:pads.set_buttons([])
    if target==0xe26c:return cube(passed,state,10000)
    if target==0xe4c0:return poll(passed,state)
    if options.world_entry:
     if target==0xf0fa:return camera(passed,state,callbacks[5],service_cb,None)
     if target==0x20820:return target_fn(passed,state,service_cb,None)
     if target==0x13440:return direction(passed,state)
     if target==0xe220:return movement(passed,state,10000)
     if target==0xeb04:return animation(passed,state,10000)
    if target in [0xe540,0xe588,0xe60a]:return math(passed,state)
    for group in sets:
     if target in sets[group]:return functions[group](passed,state,callbacks[5],service_cb,None,500000,1)
    if target==0x303c:
     args=[state.contents.registers[i]for i in [8,9,0]];bios.append([target,args]);disc.start(*args);return 0
    if target==0x3042:bios.append([target,[]]);disc.stop();return 0
    errors.append(hex(target));return 1
   service_cb=media.world_cpu.SERVICE(service)
   if options.world_entry:
    pads.set_buttons([17,18])
    if mode=='native':runtime.seed_cpu(cpu)
   elif options.inventory_entry:
    pads.set_buttons([17,18]);runtime.device.direct(SP,4,0x190000);cpu.pc=0xe4c0
    if mode=='native':
     runtime.seed_cpu(cpu)
     for _ in range(512):
      if runtime.cpu().pc==0x190000:break
      runtime.core.m68k_execute(1)
     else:raise AssertionError('Input poll prelude limit')
     cpu=runtime.cpu()
    else:
     poll_call=runtime.lib.biwn_input_poll_cpu_call;poll_call.argtypes=poll.argtypes;poll_call.restype=c.c_int;assert poll_call(c.byref(bus),c.byref(cpu))==0
    assert runtime.device.read(0x49ba4,4)&0x02002000==0x02002000
    cpu.pc=0x191f4;cpu.registers[15]=SP;cpu.usp=SP
    if mode=='native':runtime.core.m68k_set_reg(16,cpu.pc);runtime.core.m68k_set_reg(15,SP)
   elif mode=='native':runtime.seed_cpu(cpu)
   def advance():
    nonlocal cpu
    if mode=='native':
     for step in range(150000):
      pc=runtime.cpu().pc
      if step and pc in [0xdf60,BOUNDARY,0x190000,*([0x1a54a]if options.world_loop else [])]:cpu=runtime.cpu();return
      trace.append(pc)
      if pc==0x11e6c and options.inventory_entry:pads.set_buttons([])
      if pc in [0x303c,0x3042]:
       current=runtime.cpu()
       if pc==0x303c:args=[current.registers[i]for i in [8,9,0]];bios.append([pc,args]);disc.start(*args)
       else:bios.append([pc,[]]);disc.stop()
       if options.recorded_machine:
        # Mounted core intercepts BIOS before fetching an RTS. Both paths use
        # the declared preserve-register file-I/O provider instead of HLE.
        sp=current.registers[15];ret=runtime.device.read(sp,4);runtime.core.m68k_set_reg(15,sp+4);runtime.core.m68k_set_reg(16,ret)
       else:
        old=runtime.device.read(pc,2);runtime.device.direct(pc,2,0x4e75);runtime.core.m68k_execute(1);runtime.device.direct(pc,2,old)
      else:runtime.core.m68k_execute(1)
      value=runtime.core.GPUReadLong(0xf03204,0)
      if value in [0x4320,0x4720,0x52e0,0x57a0]:command(value)
     raise AssertionError(('Native flow limit',hex(pc)))
    for continuation in range(32):
     if continuation and cpu.pc in [BOUNDARY,0x190000,*([0x1a54a]if options.world_loop else [])]:return
     group=next((k for k,v in sets.items()if cpu.pc in v),None);assert group,hex(cpu.pc)
     status=functions[group](c.byref(bus),c.byref(cpu),callbacks[5],service_cb,None,500000,1)
     assert status in [0,6]and not errors,(group,status,hex(cpu.pc),errors)
     if status==6:return
     assert runtime.rows[cpu.pc]['assembly']=='rts';cpu.pc=runtime.device.read(cpu.registers[15],4);cpu.registers[15]+=4;cpu.usp=cpu.registers[15]
    raise AssertionError('C continuation limit')
   def mark(name):
    if options.recorded_machine:(out/(mode+'-'+name+'-GPU.bin')).write_bytes(GPU_bytes()[:4396])
    hardware=runtime.snapshot()['hardware'];hardware['GPU']=dict(logical_bytes=4396,sha256=sha(GPU_bytes()[:4396]))
    row=dict(CPU=media.scheduler.cpu_dict(cpu),RAM=sha(runtime.device.ram()),hardware=hardware,events=list(events),bios=list(bios),requests=list(disc.requests),completions=list(disc.completions));phases.setdefault(name,{})[mode]=row;save(out/(mode+'-'+name+'.json'),row)
   frame=0;world_returns=0
   for step in range(options.frames+64):
    save(out/'status.json',dict(status='running',mode=mode,frame=frame));advance()
    if options.world_loop and cpu.pc==0x1a54a:
     world_returns+=1;mark('world_update_returned_'+str(world_returns))
     if world_returns==2:break
     pads.set_buttons([]);continue
    if cpu.pc==BOUNDARY:
     mark('boundary_'+str(frame));frame+=1
     if frame==options.frames+1:
      if options.exit_viewer:pads.set_buttons([8])
      else:break
     continue
    if cpu.pc==0x190000:
     assert options.exit_viewer;mark('source_input_dispatch_returned');break
    if options.world_loop and cpu.pc==0xdf60 and disc.pending is None:
     assert world_returns==1;mark('world_loop_yield')
     if mode=='native':
      for _ in range(512):
       if runtime.cpu().pc==0xf360 and runtime.device.read(0xc0920,4)==IDLE:break
       trace.append(runtime.cpu().pc);runtime.core.m68k_execute(1)
      else:raise AssertionError('World loop idle selection limit')
      cpu=runtime.cpu()
     else:
      assert yielding(c.byref(bus),c.byref(cpu),128)==0
      if cpu.pc==0xf366:assert idle(c.byref(bus),c.byref(cpu),None,None,128)==0
     assert cpu.pc==0xf360;mark('world_loop_idle_selected')
     if mode=='native':
      for _ in range(512):
       if runtime.cpu().pc==0x1a550:break
       trace.append(runtime.cpu().pc);runtime.core.m68k_execute(1)
      else:raise AssertionError('World loop resume limit')
      cpu=runtime.cpu()
     else:assert idle(c.byref(bus),c.byref(cpu),None,None,128)==0
     assert cpu.pc==0x1a550;mark('world_loop_resumed');continue
    assert cpu.pc==0xdf60 and disc.pending is not None
    transfer_prefix='transfer_'+str(len(disc.requests)-1)+'_' if options.inventory_entry else ''
    mark(transfer_prefix+'loader_suspended')
    if options.inventory_entry:
     if mode=='native':
      for _ in range(512):
       if runtime.cpu().pc==0x1b0da and runtime.device.read(0xc0920,4)==MAIN:break
       trace.append(runtime.cpu().pc);runtime.core.m68k_execute(1)
      else:raise AssertionError('Frozen-ring source yield limit')
      cpu=runtime.cpu()
     else:assert yielding(c.byref(bus),c.byref(cpu),128)==0
     assert cpu.pc==0x1b0da and runtime.device.read(0xc0920,4)==MAIN;mark(transfer_prefix+'loader_yield_same_context')
     disc.tick(lambda a,data:c.memmove(runtime.device.pointer+a,data,len(data)),lambda a,v:runtime.device.direct(a,4,v));mark(transfer_prefix+'completion');continue
    if mode=='native':
     for _ in range(512):
      pc=runtime.cpu().pc
      if pc==0xf360 and runtime.device.read(0xc0920,4)==IDLE:break
      trace.append(pc);runtime.core.m68k_execute(1)
     else:raise AssertionError('Native idle selection limit')
     cpu=runtime.cpu()
    else:
     assert yielding(c.byref(bus),c.byref(cpu),128)==0
     if cpu.pc==0xf366:assert idle(c.byref(bus),c.byref(cpu),None,None,128)==0
    assert cpu.pc==0xf360;mark('idle_selected');disc.tick(lambda a,data:c.memmove(runtime.device.pointer+a,data,len(data)),lambda a,v:runtime.device.direct(a,4,v));mark('completion')
    if mode=='native':
     for _ in range(512):
      pc=runtime.cpu().pc
      if pc==0x1b0da:break
      trace.append(pc);runtime.core.m68k_execute(1)
     else:raise AssertionError('Native loader resume limit')
     cpu=runtime.cpu()
    else:assert idle(c.byref(bus),c.byref(cpu),None,None,128)==0
    assert cpu.pc==0x1b0da;mark('loader_resumed')
   assert frame==options.frames+1 and not errors
   if options.exit_viewer:
    assert cpu.pc==(0x1a54a if options.world_loop else 0x190000) and runtime.device.read(0x15b530,2)==2
    if options.world_loop:assert world_returns==2
    assert runtime.device.read(IDLE+34,4)==0
    get=lambda b,a,w=2:int.from_bytes(b[a:a+w],'big')
    before=(ROOT/'runs/zero-warm-whole-merchant-CPU-GPU-DSP/final-RAM.bin').read_bytes();after=runtime.device.ram();restored_slots=[]
    for index in range(36):
     record=0x15b4a0+index*4;references=get(before,record+2)
     if not 0<references<0x8000:continue
     assert before[record:record+4]==after[record:record+4]
     before_pointer=get(before,0x4674c+index*8,4);after_pointer=get(after,0x4674c+index*8,4)
     assert before[before_pointer:before_pointer+8192]==after[after_pointer:after_pointer+8192]
     restored_slots.append(index)
    for address,width in [(0x49b8c,2),(0x49b8e,2),(0x49b90,2),(0x778cc,4)]:assert get(before,address,width)==get(after,address,width)
   final=runtime.device.ram();(out/(mode+'-final-RAM.bin')).write_bytes(final);results.append(dict(mode=mode,CPU=media.scheduler.cpu_dict(cpu),RAM=sha(final),events=events,original_CPU_instructions=len(trace),original_CPU_addresses=sorted(set(trace)),original_GPU_opcodes=(opcode_counter.value-original_GPU_start)&0xffffffff,statistics=[stat(i)for i in range(12)],restored_active_cache_slots=restored_slots if options.exit_viewer else []))
  for name,pair in phases.items():assert pair['native']==pair['C'],('Phase mismatch',name)
  assert(out/'native-final-RAM.bin').read_bytes()==(out/'C-final-RAM.bin').read_bytes()
  assert results[1]['original_CPU_instructions']==results[1]['original_GPU_opcodes']==results[1]['statistics'][4]==results[1]['statistics'][8]==0
  observed=set(results[0]['original_CPU_addresses']);flow_addresses=sets['flow']
  report=dict(status='supplied11E6C_source_task_loading_and_render_iterations_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),render_iterations=options.frames,paired_checkpoints=len(phases),phases=phases,results=results,flow_instruction_address_coverage=[len(observed&flow_addresses),len(flow_addresses)],source_sha256={str(p):sha(p.read_bytes())for p in files},test_script_sha256=sha(Path(__file__).read_bytes()),device_library_sha256=sha(Path(device_build['library']).read_bytes()),experimental_overlay=mappings['constructor']['patches'],coordinator_authored=True,original_CPU_GPU_on_C_path=False,uninterrupted_supplied_task_to_render_iterations_verified=True,initial_CPU_entry_supplied=True,initial_GPU_resident_context_supplied=True,GPU_pipeline_private_state_verified=False,natural_source_caller_verified=False,whole_game_complete=False,native_Chat_verified=False,new_training=False,default_promoted=False,scope='Supplied11E6C task,experimental selector/count13 overlay,controlled2context ring,sourceGPUresident code/initial resetregisters supplied and resident initialization executed(native orC),BIOS/image-specificdisc completion providers. Source task/objectupdate/inputpoll/math/privateframes/constructor/loader/scheduler/geometry/projection/draw/displayswap execute without RAM/device/GPU/CPU reseed between checkpoints. FullCPU/SR/USP/SSP/privateRAM/2MBRAM/checkedTOM/JERRY/DSP/DAC/ROM hardware plus4396logicalGPUbytes and eachcommandPC/count/hash match native. GPU privatepipeline/timing bytes excluded. Source entry/ring/debugoff/initialGPU/ROM/device/clock inputs are controlled; not firmwareboot/naturalcaller/physicalcontroller/IRQtiming/OPscanout/intendedmode3format orwholegame. Finite declared iteration count and partial900block coverage only.')
  report['heap_trampoline_used']=not options.inline_selector
  report['source_inventory_dispatch_entry_verified']=options.inventory_entry
  report['source_inventory_roundtrip_verified']=options.exit_viewer
  report['initial_supplied_CPU_entry']='0x191F4 after source E4C0 B+C poll' if options.inventory_entry else '0x11E6C'
  report['source_world_update_entry_verified']=options.world_entry
  if options.world_entry:
   report['initial_supplied_CPU_entry']='0x1A188 world update'
   report['status']='captured_gameplay_source_world_update_inventory_viewer_roundtrip_native_C_match'
   report['scope']='Captured gameplay RAM and supplied source1A188 world-update caller frame. Source world routine itself polls emulated B+C,then calls191F4 which invokes11E6C; after emulated0 exit,the source world call continues camera/targeting and returns. No host-invoked input-poll prelude or direct dispatcher/viewer entry. Initial ring/residentGPU/device/ROM/clock andBIOS/disc providers remain fixtures;not freshboot or uninterrupted multi-task worldloop. '+report['scope'].replace('Initial taskring/residentGPU/device/ROM/clock andBIOS/disc providers remainfixtures. ', 'Initial task ring, CPU entry, controlled RAM edits and BIOS/disc providers remain fixtures; device state is inherited from the recorded machine. ')
  if options.inventory_entry:report['scope']='Captured gameplay RAM with existing selected item0x41; actual source E4C0 emulated B+C poll then supplied191F4 caller frame. Source dispatcher/cache snapshot/allocator/freeze invokes11E6C,not a host jump to the viewer. Experimental inline selector/count13 overlay leaves heap trampoline unused. Source freeze makes real DF60 scheduler return to MAIN; external disc completion occurs after that yield. Initial task ring/residentGPU/device/ROM/clock remain declared fixtures. '+report['scope'].replace('Initial taskring/residentGPU/device/ROM/clock andBIOS/disc providers remainfixtures. ', 'Initial task ring, CPU entry, controlled RAM edits and BIOS/disc providers remain fixtures; device state is inherited from the recorded machine. ')
  if options.inventory_entry:
   report['status']='captured_gameplay_source_inventory_dispatch_inline_viewer_native_C_match'
   report['captured_RAM_proof']=str(ROOT/'runs/zero-warm-whole-merchant-CPU-GPU-DSP/final-RAM.bin')
   report['emulated_button_sequence']=['B+C to enter','release at source viewer entry']+(['0 after declared render iterations to exit']if options.exit_viewer else [])
  if options.exit_viewer:
   report['status']='captured_gameplay_inventory_viewer_enter_render_exit_cache_restore_native_C_match'
   report['scope']+=' Emulated0 exits via source10C6E/10E72/selector sentinel; source returns through196F8,restores viewport/clock/mode2/cache,unfreezes tasks and returns to supplied dispatcher caller. Active12cache slot IDs/references andeach8192bytepayload match original gameplayRAM. Not continuation of fullworldloop or physical-input proof.'
  if options.world_entry:
   report['initial_supplied_CPU_entry']='0x1A544 world task loop' if options.world_loop else '0x1A188 world update'
   report['status']='source_world_loop_viewer_roundtrip_and_neutral_world_update_native_C_match' if options.world_loop else 'source_world_update_viewer_roundtrip_native_C_match'
   report['source_world_loop_follow_on_verified']=options.world_loop
   report['scope']='Captured gameplay RAM,existingitem41,experimental inline selector/count13 patch. Supplied '+report['initial_supplied_CPU_entry']+' polls emulatedB+C and source world/inputdispatcher callsviewer11E6C. After declared renderiterations,emulated0 exits; original source restoresmode2/cache/viewport/clock/taskeligibility and continuescamera/targeting. '+('Actualworldtask yields toidle,resumes and completes a second neutralworldupdate. Two complete worldupdates;no host supplied intercallframes orCPU/RAM/GPU/device reseed. 'if options.world_loop else 'One complete suppliedworldupdate. ')+'Initial taskring/residentGPU/device/ROM/clock andBIOS/disc providers remainfixtures. Not natural firmwareboot,physicalcontroller/scanout,DSPaudio,intendedassetformat orfullgame. FullCPU/privateframes/2MBRAM/checkedhardware/GPU4396logicalbytes pluspercommandPC/count/hash match;GPUprivatepipeline/timing excluded. Active12cachedslotIDs/references/98304bytes matchcapturedgameplay;branchcoveragefinite.'
  report['recorded_machine_state_restored']=options.recorded_machine
  if options.recorded_machine:
   report['status']='recorded_machine_source_world_viewer_roundtrip_and_follow_on_native_C_match'
   report['recorded_machine_restore_proof']=recorded
   report['initial_GPU_resident_context_supplied']=False
   report['scope']='Original recorded machine restored byte-exactly withmatching referencecore andmountedinternalCDI before identical controlled RAM/CPUentry/ring/inlinepatch/input edits. GPU/DSP/TOM/JERRY/DAC/device state inherited,not reset/seededresident fixture. OriginalcapturedGPU startsF031D2. No device/ROM reset/resident initialization afterrestoration. CPUentry1A544/stack/registers/two-contextring/debugoff andBIOS/disc completion providers remain controlled;not freshfirmwareboot/untouchedoriginal continuation. '+report['scope'].replace('Initial taskring/residentGPU/device/ROM/clock andBIOS/disc providers remainfixtures. ', 'Initial task ring, CPU entry, controlled RAM edits and BIOS/disc providers remain fixtures; device state is inherited from the recorded machine. ')
  save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification'/(proof_name+'-current.json'),report);print(report['status'],flush=True)
 except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));save(out/'failure.json',dict(error=repr(error),phases=phases));raise
 finally:runtime.oracle.close()
if __name__=='__main__':main()
