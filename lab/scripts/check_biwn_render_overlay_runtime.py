"""Original native render continuation with actual overlay/formatter/text versus C.

Three-context fixture (render continuation + two real idle loops), not full
17C40 startup or the world-task ring. One frozen sprite request per case.
"""
import argparse,ctypes as c,json,random,subprocess,os,sys,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import animation_renderer as render
import check_biwn_scheduler as scheduler
import check_biwn_render_scene as scene
import check_biwn_overlay as overlay
world=scene.world;CPU=scheduler.CPU
RENDER=0xc0d28;IDLES=[0xc5928,0xc5528];CONTEXTS=[RENDER]+IDLES;ENTRIES=[0x17dc2,0xf360,0xf880];SSP=0x1d0000
STUBS=[0xe0a6,0xe0f2,0xe148,0xe19e,0xe202,0x170a0,0x185b2]
SERVICES=[0xea28,0x17e0e,0x181f8];LOGGED=SERVICES+[0xdf60,0xe03a,0x17f14]+[x for x in STUBS if x!=0x181f8]+[0xe2b8,0x1b45a,0x149ae]
BODY=c.CFUNCTYPE(c.c_int,c.c_void_p,c.POINTER(world.Bus),c.POINTER(CPU));SERVICE=c.CFUNCTYPE(c.c_int,c.c_void_p,c.POINTER(world.Bus),c.POINTER(CPU),c.c_uint32)
class TextBus(c.Structure):_fields_=[('read8',world.R8),('read16',world.R16),('write32',world.W32),('context',c.c_void_p),('read_budget',c.c_uint32)]
class TextArgs(c.Structure):_fields_=[('x',c.c_uint16),('y',c.c_uint16),('text',c.c_uint32),('target',c.c_uint32),('target_flags',c.c_uint32),('font',c.c_uint32),('color',c.c_uint16),('mode',c.c_uint16)]
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
def get(r,a,w=4):return int.from_bytes(r[a:a+w],'big')
def masked(r):
 out=bytearray(r)
 for a,b in [(SSP-0x1000,SSP+8),(0x15b7a0,0x15b7aa)]+[(a+0x26,a+0x400)for a in CONTEXTS]:out[a:b]=bytes(b-a)
 for a in CONTEXTS:out[a+21]&=0xe0
 return bytes(out)
def fixture(snapshot,index):
 ram,info=render.frame_ram(snapshot,index%72);ram=bytearray(ram)
 def put(a,w,v):ram[a:a+w]=(v&((1<<(w*8))-1)).to_bytes(w,'big')
 for a,w,v in [(0xc0920,4,RENDER),(0x80,4,0xde08),(0x49c60,2,index%5),(0x49c76,2,[0,0x7fff,0x8000,0xffff][index%4]),(0x10a684,4,0),(0x49b88,4,0),(0x10d688,4,0x12345678),(0x10d68c,4,1),(0x10d690,4,0xffff)]:put(a,w,v)
 for a,w,v in [(0x4451c,2,index%2),(0x44518,2,80),(0x4451a,2,100),(0x49d6a,2,100+index%30),(0x49d68,2,120+index%80),(0x49d5c,2,(index//2)%2),(0x49d5e,2,(index//4)%2),(0x113060,2,(index//8)%2),(0x49cba,1,index%256),(0x49c50,4,(index-72)*64),(0x49c56,4,(36-index)*64),(0x49c62,2,0xffff if index%3==0 else index%16),(0x4451e,2,index-72 if index%4==0 else 0x1234),(0x44520,2,36-index),(0x44522,2,0xffff if index%3==0 else index%16)]:put(a,w,v)
 for i,(obj,entry)in enumerate(zip(CONTEXTS,ENTRIES)):
  top=obj+0x400;stack=top-16 if i==0 else top
  for a,w,v in [(obj,4,CONTEXTS[(i+1)%3]),(obj+4,4,CONTEXTS[(i-1)%3]),(obj+8,4,entry),(obj+12,4,stack),(obj+16,4,entry),(obj+20,2,0),(obj+22,4,0),(obj+26,4,0),(obj+34,4,0)]:put(a,w,v)
 return bytes(ram),info
class Runtime:
 def __init__(self,library):
  self.device=render.Runtime();self.core=c.CDLL(str(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'));self.lib=c.CDLL(str(library));self.core.m68k_set_reg.argtypes=[c.c_int,c.c_uint32];self.core.m68k_get_reg.argtypes=[c.c_void_p,c.c_int];self.core.m68k_get_reg.restype=c.c_uint32;self.core.m68k_execute.argtypes=[c.c_int];self.core.m68k_execute.restype=c.c_int;self.core.m68k_set_irq.argtypes=[c.c_uint32];self.prefix=(c.c_uint32*18).in_dll(self.core,'regs');self.core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];self.core.GPUReadLong.restype=c.c_uint32
  self.render_step=self.lib.biwn_render_loop_step;self.render_step.argtypes=[c.POINTER(world.Bus),c.POINTER(CPU),SERVICE,c.c_void_p,c.c_uint32];self.render_step.restype=c.c_int
  self.idle_step=self.lib.biwn_task_loop_step;self.idle_step.argtypes=[c.POINTER(world.Bus),c.POINTER(CPU),BODY,c.c_void_p,c.c_uint32];self.idle_step.restype=c.c_int
  self.clear,self.rotate,self.scene=scene.bind(self.lib)
  self.overlay=overlay.bind(self.lib);self.format=self.lib.biwn_overlay_format;self.format.argtypes=[c.POINTER(world.Bus),render.W8,c.c_uint32,c.c_uint32,c.c_uint16,c.c_uint16,c.c_uint16,c.POINTER(c.c_uint32)];self.format.restype=c.c_int
  self.text=self.lib.biwn_text_draw;self.text.argtypes=[c.POINTER(TextBus),c.POINTER(TextArgs),c.POINTER(c.c_uint32)];self.text.restype=c.c_int
 def current(self):return get(self.device.ram(),0xc0920)
 def event(self,cpu):return{'context':self.current(),'pc':cpu.pc,'sp':cpu.registers[15]}
 def cpu(self):
  cpu=CPU();cpu.registers[:]=[self.core.m68k_get_reg(None,i)for i in range(16)];cpu.pc=self.core.m68k_get_reg(None,16);cpu.sr=self.core.m68k_get_reg(None,17);cpu.usp=cpu.registers[15];cpu.ssp=self.prefix[17];return cpu
 def scripted(self,target,args,d0):
  if target==0x170a0:self.device.direct(0x49b88,4,0);return self.return_word^0x170a0
  if target==0x185b2:return self.return_word^0x185b2
  if target==0x181f8:return self.return_word^0x181f8
  return d0
 def native(self,ram,incoming,clocks,return_word):
  self.return_word=return_word;self.device.seed(ram,0)
  for target in STUBS:self.device.direct(target,2,0x4e75)
  self.core.m68k_pulse_reset();self.core.m68k_set_irq(0);self.core.m68k_set_reg(17,0x2000);self.core.m68k_set_reg(15,SSP);self.core.m68k_set_reg(17,0)
  for i,value in enumerate(incoming):self.core.m68k_set_reg(i,value)
  self.core.m68k_set_reg(15,RENDER+0x400-16);self.core.m68k_set_reg(16,0x17dc2);calls=[];handoffs=[];steps=[];clock_index=0;begun=False
  for _ in range(200000):
   pc=self.core.m68k_get_reg(None,16)
   if pc==0x17dc2 and begun:break
   begun=True
   if pc in[0x17dc2,0x17dd4,0x17de0,0x17dec]:self.device.direct(0x778cc,4,clocks[clock_index]);clock_index+=1
   assert any(a<=pc<b for a,b in [(0x17dc2,0x17f68),(0xea28,0xeac4),(0xe2b8,0xe2f4),(0xe098,0xe0a6),(0xe03a,0xe098),(0xdf60,0xdf6c),(0xde08,0xde5c),(0xf360,0xf368),(0xf880,0xf888),(0x181f8,0x18554),(0x14776,0x14caa),(0x1b160,0x1b478),(0xe61c,0xe68c),(0xe540,0xe588)])or pc in STUBS,hex(pc)
   steps.append(pc)
   if pc in LOGGED:
    stack=self.core.m68k_get_reg(None,15);widths=overlay.WIDTHS.get(pc,[4]* (3 if pc==0xe2b8 else 2 if pc in[0xe03a,0x185b2]else 0));args=[];offset=4
    for width in widths:args.append(get(self.device.ram(),stack+offset,width));offset+=width
    calls.append(['call',pc,args])
    if pc in STUBS:self.core.m68k_set_reg(0,self.scripted(pc,args,self.core.m68k_get_reg(None,0)))
   self.core.m68k_execute(1)
   if self.core.GPUReadLong(0xf03204,0)==0x4b00:self.device.write(0xf03204,4,0x4b00)
   if pc==0xdf6a or(pc==0xde5a and self.core.m68k_get_reg(None,16)!=0xdf66):handoffs.append(self.event(self.cpu()))
  else:raise AssertionError('Original render continuation did not return to loop')
  for target in STUBS:self.device.direct(target,2,get(ram,target,2))
  assert clock_index==4
  return self.device.ram(),self.cpu(),{'calls':calls,'handoffs':handoffs,'steps':steps,'device':self.device.stats()}
 def translated(self,ram,incoming,clocks,return_word):
  self.return_word=return_word;self.device.seed(ram,1);cpu=CPU();cpu.registers[:]=incoming;cpu.registers[15]=RENDER+0x400-16;cpu.usp=cpu.registers[15];cpu.ssp=SSP;cpu.pc=0x17dc2;cpu.sr=0;calls=[];handoffs=[];errors=[];clock_index=0;steps=[]
  def call(_,target,args,n,out):
   try:
    values=list(args[:n]);calls.append(['call',target,values])
    if target==0xe03a:return self.clear(c.byref(bus),*values,4096)
    if target==0x17f14:return self.rotate(c.byref(bus),out[0],out)
    if target==0xe2b8:
     gpu=render.GpuBus(self.device.r32,self.device.w32,None,100000);return self.device.protocol(c.byref(gpu),*values)
    if target==0x1b45a:
     assert n==5;return self.format(c.byref(bus),self.device.write8,*values,out)
    if target==0x149ae:
     assert n==8;text_bus=TextBus(self.device.r8,self.device.r16,self.device.w32,None,100000);text_args=TextArgs(*values);return self.text(c.byref(text_bus),c.byref(text_args),out)
    assert target in STUBS;out[0]=self.scripted(target,values,out[0]);return 0
   except Exception as error:errors.append(repr(error));return 1
  cb=world.CALL(call);bus=world.Bus(self.device.r8,self.device.r16,self.device.r32,self.device.w16,self.device.w32,cb,None,0)
  def service(_,passed,state,target):
   try:
    calls.append(['call',target,[]]);d0=c.c_uint32(state.contents.registers[0])
    if target==0xea28:status=self.device.consumer(c.cast(c.byref(bus),c.POINTER(render.Bus)),self.device.write8,64,d0.value,c.byref(d0))
    elif target==0x17e0e:status=self.scene(c.byref(bus),4096,d0.value,c.byref(d0))
    else:assert target==0x181f8;status=self.overlay(c.byref(bus),state.contents.registers[15]-54,d0.value,c.byref(d0))
    assert status==0;state.contents.registers[0]=d0.value;return 0
   except Exception as error:errors.append(repr(error));return 1
  service_cb=SERVICE(service);begun=False
  for _ in range(1000):
   pc=cpu.pc
   if pc==0x17dc2 and begun:break
   begun=True;steps.append(pc)
   if pc in[0x17dc2,0x17dd4,0x17de0,0x17dec]:self.device.direct(0x778cc,4,clocks[clock_index]);clock_index+=1
   yielding=pc in[0x17dc2,0xf360,0xf880]
   if yielding:calls.append(['call',0xdf60,[]])
   if self.current()==RENDER:status=self.render_step(c.byref(bus),c.byref(cpu),service_cb,None,64)
   else:status=self.idle_step(c.byref(bus),c.byref(cpu),BODY(),None,64)
   assert status==0,(status,hex(pc),errors)
   if yielding:handoffs.append(self.event(cpu))
  else:raise AssertionError('C render continuation did not finish')
  assert not errors and clock_index==4
  return self.device.ram(),cpu,{'calls':calls,'handoffs':handoffs,'steps':steps,'device':self.device.stats(),'errors':errors}
 def close(self):self.device.close()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opts=ap.parse_args();out=ROOT/'verification/biwn-render-overlay-runtime'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';lib=out/'librender-loop.dylib';names=['biwn_render_loop.c','biwn_render_scene.c','biwn_scheduler.c','biwn_task_loops.c','biwn_overlay.c','biwn_overlay_format.c','biwn_text.c'];cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(source/n)for n in names]+['-o',str(lib)];subprocess.run(cmd,check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});runtime=Runtime(lib);manifest,snapshot=render.assets();rng=random.Random(0x17dc2);rows=[];coverage=set()
 try:
  for i in range(opts.limit or 144):
   save(out/'status.json',{'status':'running','case':i});ram,info=fixture(snapshot,i);incoming=[rng.getrandbits(32)for _ in range(16)];clocks=([[0,0,0,0],[0xffffffff,0,1,2],[0x7fffffff,0x80000000,0,0xffffffff],[0x80000000,0x7fffffff,0xffffffff,0]][i]if i<4 else[rng.getrandbits(32)for _ in range(4)]);word=rng.getrandbits(32)
   left,original,om=runtime.native(ram,incoming,clocks,word);right,actual,cm=runtime.translated(ram,incoming,clocks,word);coverage.update(om['steps'])
   # Component contracts do not specify A0/A1 or helper CCR. The profiling
   # tail overwrites D1/CCR, so compare those final values too; only saved
   # SR low5 bits in context records and private stacks remain masked.
   registers=[j for j in range(16)if j not in[8,9]];masked_left=masked(left);masked_right=masked(right)
   if masked_left!=masked_right or any(original.registers[j]!=actual.registers[j]for j in registers)or(original.pc,original.usp,original.ssp,original.sr)!=(actual.pc,actual.usp,actual.ssp,actual.sr)or om['calls']!=cm['calls']or om['handoffs']!=cm['handoffs']:
    save(out/'mismatch.json',{'case':i,'original_CPU':scheduler.cpu_dict(original),'C_CPU':scheduler.cpu_dict(actual),'original':om,'C':cm,'RAM_differences':[[hex(j),left[j],right[j]]for j in range(len(left))if masked_left[j]!=masked_right[j]][:100]});raise AssertionError(str(out/'mismatch.json'))
   assert om['device']['original_GPU_sprite_decodes']==1 and len(om['handoffs'])==3 and cm['device']['C_sprite_decodes']==1 and not cm['device']['original_GPUExec1_calls']and not cm['device']['original_GPU_sprite_decodes']and not cm['device']['game_frames_executed']
   output=info['output'];raw=right[output+16:output+16+info['width']*info['height']*2]
   rows.append({'case':i,'frame_index':i%72,'mode':i%5,'clocks':clocks,'helper_return_seed':word,'initial_registers':incoming,'original_CPU':scheduler.cpu_dict(original),'C_CPU':scheduler.cpu_dict(actual),'calls':cm['calls'],'handoffs':cm['handoffs'],'raw_sha256':render.sha(raw),'original':om['device'],'rebuilt':cm['device'],'whole_visible_RAM_and_selected_CPU_match':True})
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
 finally:runtime.close()
 save(out/'fixtures.json',rows);loop_coverage=sorted(a for a in coverage if 0x17dc2<=a<0x17e0e)
 if opts.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'directory':str(out),'cases':len(rows),'loop_instruction_coverage':len(loop_coverage)}));return
 assert len(loop_coverage)==16
 # Added host failures must never publish a partly advanced CPU structure.
 runtime=Runtime(lib);guards=[]
 try:
  ram,_=fixture(snapshot,0);runtime.device.seed(ram,1)
  for kind in ['null_bus','null_cpu','null_service','zero_scan_limit','unsupported_startup','supervisor_state','read_failure','write_failure','service_failure']:
   cpu=CPU();cpu.registers[:]=[0]*16;cpu.registers[15]=RENDER+0x400-16;cpu.usp=cpu.registers[15];cpu.ssp=SSP;cpu.pc=0x17dce
   if kind=='unsupported_startup':cpu.pc=0x17c40
   if kind=='supervisor_state':cpu.sr=0x2000
   if kind=='read_failure':cpu.pc=0x17dc2
   r32=world.R32(lambda *_:1)if kind=='read_failure'else runtime.device.r32
   w32=world.W32(lambda *_:1)if kind=='write_failure'else runtime.device.w32
   bus=world.Bus(runtime.device.r8,runtime.device.r16,r32,runtime.device.w16,w32,world.CALL(),None,0)
   cb=SERVICE()if kind=='null_service'else SERVICE(lambda *_:1);before=bytes(cpu)
   status=runtime.render_step(None if kind=='null_bus'else c.byref(bus),None if kind=='null_cpu'else c.byref(cpu),cb,None,0 if kind=='zero_scan_limit'else 64)
   assert status and bytes(cpu)==before,(kind,status)
   guards.append({'kind':kind,'rejected':True,'caller_CPU_unchanged':True,'status':status})
 finally:runtime.close()
 save(out/'guards.json',guards)
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'native_scheduled_render_consumer_scene_overlay_formatter_text_matches_C','directory':str(out),'public_context_header_bytes_compared':38,'cases':len(rows),'host_guards':len(guards),'distinct_sprite_frames':72,'task_handoffs':len(rows)*3,'C_sprite_decodes':len(rows),'render_loop_instruction_coverage':[16,16],'render_loop_interval':'[0x17dc2,0x17e0e)','overlay_linked':True,'text149AE_linked':True,'two_fixed_formats_linked':True,'whole_general_formatter_reconstructed':False,'formatter_calls':sum(sum(c[1]==0x1b45a for c in row['calls'])for row in rows),'text_calls':sum(sum(c[1]==0x149ae for c in row['calls'])for row in rows),'original_task_entry':'0x17c40','original_startup_reconstructed':False,'new_complete_task_bodies':0,'loop_counted_as_additional_original_component':False,'queue_consumer_linked_to_render_continuation':True,'linked_to_existing_world_three_task_ring':False,'complete_game_frames_executed':0,'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in names+['biwn_render_loop.h','biwn_render_scene.h','biwn_scheduler.h','biwn_task_loops.h','biwn_overlay.h','biwn_overlay_format.h','biwn_text.h']},'asset_sha256':manifest['assets'],'nested_scripted_targets':[hex(a)for a in STUBS],'matched':['Original native CPU executes actualTRAP/RTE/scheduler/render continuation, EA28/E2B8, E03Aclear/17E0Edispatch/17F14rotation plus full181F8overlay, original1B45Aformatter and149AE/147A6/14776text; originalGPU4B00 decodes sprite. Rebuilt C links full overlay, existing Ctext and checked two-format adapter. Cpath uses corresponding reconstructed code with zero original CPU/GPU instructions.','All visible RAM after explicit exclusions, final CPU exceptA0/A1, profiling fields, calls/arguments/order,3taskhandoffs percase, outputheaders/rawpixels. Final SRincludingCCR matches after profiling tail.'],'limits':['Bounded selected render continuation plus two real idle task loops, not17C40initialization/taskcreation or existing world-update ring. One externally seeded sprite request and4externalclock samples percase; frozenassets,mode/regionlistfixtures.','Seven nested GPU/scene/display-list targets scripted. Overlay and text are real original/C; only two fixed format outputs/fullD0 are reproduced, not generalprintf/global scratch. These tests avoid actual3Ddraw submission by scripted170A0drawcount0. Pinned emulatedblitter runs clear submission; no wholeviewport/gameframes or hardwaretiming.','Private supervisor/taskstacks, ten originalformatterglobalscratchbytes15B7A0..AA, savedcontextSRlow5CCRbits and finalA0/A1 excluded. Other callee registers/fullD0/finalD1/CCR compare; no complete scene/mainloop/audio/actorassetlifecycle.']}
 save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-render-overlay-runtime-checks.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
