"""Original/C BIOS completion and game boot tail under declared event quanta."""
import ctypes as c,hashlib,json,os,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
import observe_biwn_relocated_firmware as host
import biwn_firmware_checkpoint as checkpoint
import check_biwn_movie_GPU as GPU
import check_biwn_dsp_media_audio as DSP
from check_biwn_main_GPU_boot import Bus as BootBus,W16
from check_biwn_game_firstboot_GPU import Bus as GameBus
from probe_biwn_gpu_projection import gpu_state
ROOT=host.ROOT;save=host.save;sha=host.sha
out=ROOT/'verification/BIWN-header-handoff-tail'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
core_path=Path(json.loads((ROOT/'verification/BIWN-GPU-IRQ-forward-candidate.json').read_text())['core_path']);capture=ROOT/'verification/BIWN-firmware-header-resume/20261015T105258.234232Z/resume-checkpoint/checkpoint.json';src=ROOT/'projects/black-ice-white-noise/restoration';lib=out/'libhandoff.dylib';sources=[src/'experimental/biwn_handoff_game_cpu.c',src/'experimental/biwn_handoff_bios_cpu.c',src/'biwn_gpu_cd_marker_ISR.c',src/'biwn_game_firstboot_GPU.c'];cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(src),*[str(p)for p in sources],'-o',str(lib)];b=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(b.stdout+b.stderr);assert not b.returncode,b.stderr
functions=c.CDLL(str(lib));native_points=[];results=[]
for mode in ['native','C']:
 rt,loaded,restore=checkpoint.restore_current(host,capture,core_override=core_path);co=rt.core;cpu=rt.cpu();g=GPU.state_from_raw(gpu_state(co)[0]);raw=c.create_string_buffer(12000);co.DSPStateSave(raw);d=DSP.state_from_raw(raw.raw);errors=[];events=[];gpu_calls=[];irq_events=[];trace=[];go=c.c_uint32.in_dll(co,'gpu_exec_opcode_count');dsp_counter=c.c_uint32.in_dll(co,'dsp_exec_opcode_count');initial_counts=(go.value,dsp_counter.value)
 co.GPUGetPC.restype=c.c_uint32;co.GPUExec.argtypes=[c.c_int32];co.GPUGetRAM.restype=c.c_void_p;co.GPUReadWord.argtypes=[c.c_uint32,c.c_uint32];co.GPUReadWord.restype=c.c_uint16;co.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];co.GPUReadLong.restype=c.c_uint32;co.GPUWriteWord.argtypes=[c.c_uint32,c.c_uint16,c.c_uint32];co.GPUWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32]
 for w in [8,16,32]:
  getattr(co,'m68k_read_memory_'+str(w)).argtypes=[c.c_uint32];getattr(co,'m68k_read_memory_'+str(w)).restype={8:c.c_uint8,16:c.c_uint16,32:c.c_uint32}[w];getattr(co,'m68k_write_memory_'+str(w)).argtypes=[c.c_uint32,c.c_uint32]
 co.GetTimeToNextEvent.argtypes=[c.c_int];co.GetTimeToNextEvent.restype=c.c_double;co.HandleNextEvent.argtypes=[c.c_int];co.EventStateSave.argtypes=[c.c_void_p];co.EventStateSave.restype=c.c_size_t
 observer_trace=[]
 def wr32(_,a,v):
  if not 0xf02100<=a<=0xf0211f:co.GPUWriteLong(a,v,3)
  return 0
 gpu_callbacks=[GPU.R8(lambda _,a,v:(v.__setitem__(0,co.JaguarReadByte(a,3)),0)[1]),GPU.R16(lambda _,a,v:(v.__setitem__(0,co.GPUReadWord(a,3)),0)[1]),GPU.R32(lambda _,a,v:(v.__setitem__(0,co.GPUReadLong(a,3)),0)[1]),W16(lambda _,a,v:(co.GPUWriteWord(a,v,3),0)[1]),GPU.W32(wr32),GPU.OBS(lambda _,pc:observer_trace.append(pc))];game_bus=GameBus(*gpu_callbacks,None);marker_bus=BootBus(*gpu_callbacks[1:],None)
 marker=functions.biwn_gpu_cd_marker_ISR_run;marker.argtypes=[c.POINTER(BootBus),c.POINTER(GPU.State),c.c_uint32,c.c_uint32];marker.restype=c.c_int;assert_marker=functions.biwn_gpu_cd_marker_ISR_assert;assert_marker.argtypes=[c.POINTER(BootBus),c.POINTER(GPU.State)];assert_marker.restype=c.c_int;main=functions.biwn_game_firstboot_GPU_run;main.argtypes=[c.POINTER(GameBus),c.POINTER(GPU.State),c.c_uint32,c.c_uint32];main.restype=c.c_int
 OWNER=c.CFUNCTYPE(c.c_int,c.c_int,c.c_int)
 def gpu_irq(irq,state):
  irq_events.append(['GPU',irq,state])
  if mode=='native':return 0
  try:
   assert 0<=irq<=4;mask=0x40<<irq;g.control &= ~mask
   if not state or not g.control&1 or g.control&8:return 1
   g.control |= mask;bits=((g.control>>6)&31)&((g.flags>>4)&31)
   if not g.flags&8 and bits:
    which=bits.bit_length()-1;assert which==1,('unhandled enabledGPU IRQ',which);assert assert_marker(c.byref(marker_bus),c.byref(g))==0
  except BaseException as e:errors.append(repr(e))
  return 1
 def dsp_irq(irq,state):
  irq_events.append(['DSP',irq,state])
  if mode=='native':return 0
  try:
   assert not(d.flags>>4)&31;mask=(0x40<<irq)if irq<5 else 0x10000;d.control=(d.control&~mask)|(mask if state else 0)
  except BaseException as e:errors.append(repr(e))
  return 1
 owners=[OWNER(gpu_irq),OWNER(dsp_irq)];co.BIWNSetGPUIRQOwner.argtypes=[OWNER];co.BIWNSetDSPIRQOwner.argtypes=[OWNER];co.BIWNSetGPUIRQOwner(owners[0]);co.BIWNSetDSPIRQOwner(owners[1])
 def current_g():return GPU.state_from_raw(gpu_state(co)[0])if mode=='native'else g
 def pump(stop,program,at_least_one=False):
  observer_trace.clear();before=go.value;begin=g.instructions
  if mode=='native':
   delays=0
   for n in range(5000):
    pc=co.GPUGetPC()
    if pc==stop and(n or not at_least_one):break
    opcode=co.GPUReadWord(pc,3)>>10;observer_trace.append(pc);co.GPUExec(1)
    if opcode in [52,53] and co.GPUGetPC()!=pc+2:delays+=1
   else:raise AssertionError(('GPU pump',hex(co.GPUGetPC())))
   instructions=len(observer_trace)+delays
  else:
   fn,bus=(marker,marker_bus)if program=='marker'else(main,game_bus);status=fn(c.byref(bus),c.byref(g),5000,stop);assert status==0,('GPU C pump',program,hex(g.pc),status);instructions=g.instructions-begin;assert go.value==before;c.memmove(co.GPUGetRAM(),bytes(g.local_RAM),4096)
  gpu_calls.append(dict(program=program,stop=hex(stop),instructions=instructions,PC_trace=list(observer_trace),GPU=sha(GPU.logical(current_g()))))
 def snapshot(pc):
  hw=rt.snapshot()['hardware'];hw['GPU']=dict(size=4396,sha256=sha(GPU.logical(current_g())));rb=c.create_string_buffer(12000);co.DSPStateSave(rb);hw['DSP']=dict(size=8496,sha256=sha(rb.raw[:8496]if mode=='native'else DSP.logical(d)));eb=c.create_string_buffer(10000);n=co.EventStateSave(eb);hw['event_queue']=dict(size=n,sha256=sha(eb.raw[:n]));return dict(pc=pc,CPU=host.media.scheduler.cpu_dict(rt.cpu()if mode=='native'else cpu),RAM=sha(rt.device.ram()),hardware=hw)
 world=host.media.scheduler.cleanup.world
 def reader(w):
  def cb(_,a,v):
   try:v[0]=int.from_bytes(bytes(g.local_RAM[a-0xf03000:a-0xf03000+w]),'big')if mode=='C'and 0xf03000<=a<=0xf04000-w else g.control if mode=='C'and a==0xf02114 and w==4 else getattr(co,'m68k_read_memory_'+str(w*8))(a);return 0
   except BaseException as e:errors.append(repr(e));return 1
  return cb
 def writer(w):
  def cb(_,a,v):
   try:
    getattr(co,'m68k_write_memory_'+str(w*8))(a,v)
    if mode=='C'and 0xf03000<=a<=0xf04000-w:g.local_RAM[a-0xf03000:a-0xf03000+w]=v.to_bytes(w,'big')
    return 0
   except BaseException as e:errors.append(repr(e));return 1
  return cb
 callbacks=[world.R8(reader(1)),world.R16(reader(2)),world.R32(reader(4)),world.W16(writer(2)),world.W32(writer(4)),host.media.W8(writer(1))];bus=host.media.Bus(*callbacks[:5],world.CALL(),None,0);service=host.media.world_cpu.SERVICE(lambda *_:0)
 cpu_fns={}
 for symbol in ['biwn_handoff_game_cpu_call','biwn_handoff_bios_cpu_call']:
  fn=getattr(functions,symbol);fn.argtypes=rt.fn.argtypes;fn.restype=c.c_int;cpu_fns[symbol]=fn
 try:
  gs=current_g();sp=gs.registers[0][31];ret=int.from_bytes(bytes(gs.local_RAM[sp-0xf03000:sp-0xf03000+4]),'big')+2;pump(ret,'marker');pump(0xf032ce,'main')
  for _ in range(100000):
   pc=rt.cpu().pc if mode=='native'else cpu.pc
   if pc==0x4000:break
   trace.append(pc)
   if pc==0x304e:
    for event in [0,1]:
     before_irqs=len(irq_events);dt=co.GetTimeToNextEvent(event);co.HandleNextEvent(event);events.append(dict(type=event,due_us=dt,IRQs=irq_events[before_irqs:]));assert not errors,errors
    if current_g().pc==0xf03010:pump(0xf032ce,'marker')
   if pc==0x180178:pump(0xf03328,'main')
   if mode=='native':co.m68k_execute(1)
   else:
    fn=cpu_fns['biwn_handoff_game_cpu_call'if pc>=0x180000 else'biwn_handoff_bios_cpu_call'];status=fn(c.byref(bus),c.byref(cpu),callbacks[5],service,None,1,0);assert status in [0,4,8]and not errors,('CPU C step',hex(pc),status,errors)
   snap=snapshot(pc)
   if mode=='native':native_points.append(snap)
   else:
    expected=native_points[len(trace)-1]
    if snap!=expected:save(out/'mismatch.json',dict(index=len(trace)-1,native=expected,C=snap));raise AssertionError(str(out/'mismatch.json'))
  else:raise AssertionError('CPU tail bound')
  assert dsp_counter.value==initial_counts[1]
  if mode=='native':save(out/'native-CPU-instruction-checkpoints.json',native_points)
  result=dict(CPU_steps=len(trace),CPU_PC_trace=trace,final=snapshot(0x4000),GPU_calls=gpu_calls,events=events,IRQ_events=irq_events,original_DSP_instructions=0,original_GPU_instructions_on_C_path=(go.value-initial_counts[0])if mode=='C'else None);save(out/(mode+'.json'),result);results.append(result)
 except BaseException as e:save(out/(mode+'-failure.json'),dict(error=repr(e),CPU=host.media.scheduler.cpu_dict(rt.cpu()if mode=='native'else cpu),GPU=hex(current_g().pc),errors=errors));raise
 finally:co.BIWNSetGPUIRQOwner(OWNER());co.BIWNSetDSPIRQOwner(OWNER());rt.oracle.close()
for key in ['CPU_steps','CPU_PC_trace','final','GPU_calls','events','IRQ_events']:assert results[0][key]==results[1][key],key
report=dict(status='captured_header_CPU_BIOS_GPU_and_main_JERRY_event_tail_to4000_native_C_match',directory=str(out),results=results,all_CPU_instruction_boundary_full_states_equal=True,initial_firmware_header_capture=str(capture),GPU_event_owner_hook=True,whole_game_complete=False,limits=['Starts at capturedCPU361E with stage bytes already loaded; firmware authentication/loading before this remains unproved.','Host source304E poll schedules one main and oneJERRY event; synchronous GPU handler/poll/shutdown boundaries remain. No full cycle interleaving/physical timing.','Original/C compare each CPU instruction plus GPU traces/logicalstates/devices/eventqueues; DSP is halted, with disabledIRQ latches only, no audible/game/boot proof.']);save(out/'report.json',report);save(ROOT/'verification/header-handoff-tail-current.json',report);print(report['status'],flush=True)
