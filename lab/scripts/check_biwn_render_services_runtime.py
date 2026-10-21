"""Full render caller with real RNG initialization/creation/steady loop vs native CPU.

Four supplied initial contexts plus17actual creations form21contexts.
Seven nested startup resource/scene dependencies remain explicit scripts. After startup,
18contexts are explicitly blocked so render/twoidle bodies can be checked.
"""
import argparse,ctypes as c,json,random,subprocess,os,hashlib
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_render_display_runtime as prior
import check_biwn_rng as rngcheck
import check_biwn_startup_services as helpers
import emulated_pad_input as pad
ROOT=prior.ROOT;world=prior.world;CPU=prior.CPU;RENDER=prior.RENDER;SSP=prior.SSP
SYSTEM=[0xc1928,0xc1528,0xc0928]
CREATED=[0xc1128]+[0xc1d28+i*0x400 for i in range(16)]
CONTEXTS=[RENDER]+SYSTEM+CREATED
TASKS=[0x18b86,0x21d1a,0x1a544,0x17520,0x12ee0,0x155e0,0x14cc0,0x179c0,0x17380,0x17640,0x1a560,0x1a920,0xefa0,0xec20,0x1b480,0xf880,0xf360]
RETURNS=[0x18d7c,0x17d0e,0x17d18,0x17d22,0x17d30,0x17d3a,0x17d44,0x17d4e,0x17d5c,0x17d66,0x17d70,0x17d7a,0x17d88,0x17d92,0x17d9c,0x17da6,0x17db4]
START_SERVICES=[0xe2f4,0x18160,0x21242,0x18ba8,0xdfc0]
START_STUBS=[a for a in helpers.STUBS if a!=0xdf6c]
STUBS=prior.STUBS+START_STUBS
LOGGED=list(dict.fromkeys(prior.LOGGED+START_STUBS+START_SERVICES+list(helpers.WIDTHS)+[0x4088,0xdf6c,0x1a6e0]+list(rngcheck.CALL_WIDTHS)))
get=prior.get;SERVICE=prior.SERVICE;BODY=prior.BODY
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
def masked(ram):
 data=bytearray(ram)
 for a,b in [(SSP-0x1000,SSP+8),(0x15b7a0,0x15b7aa)]+[(obj+0x26,obj+0x400)for obj in CONTEXTS]:data[a:b]=bytes(b-a)
 return bytes(data)
def fixture(snapshot,index):
 ram,info=prior.fixture(snapshot,index);ram=bytearray(ram)
 def put(a,w,v):ram[a:a+w]=(v&((1<<(w*8))-1)).to_bytes(w,'big')
 initial=[RENDER]+SYSTEM;entries=[0x17c40,0xf4d8,0xf4d8,0xddcc]
 for i,(obj,entry)in enumerate(zip(initial,entries)):
  for a,w,v in [(obj,4,initial[(i+1)%4]),(obj+4,4,initial[(i-1)%4]),(obj+8,4,entry),(obj+12,4,obj+0x400),(obj+16,4,entry),(obj+20,2,0),(obj+22,4,0),(obj+26,4,0),(obj+30,4,0),(obj+34,4,0)]:put(a,w,v)
 for i,obj in enumerate(CREATED):put(obj,4,CREATED[i+1]if i<16 else 0)
 put(0xc0920,4,RENDER);put(0xc0924,4,CREATED[0]);return bytes(ram),info
def task_table(ram):
 rows=[];seen=set();obj=RENDER
 while obj not in seen:
  assert obj in CONTEXTS;seen.add(obj);rows.append({'context':obj,'next':get(ram,obj),'prev':get(ram,obj+4),'entry':get(ram,obj+8),'SP':get(ram,obj+12),'saved_PC':get(ram,obj+16),'SR':get(ram,obj+20,2),'deadline':get(ram,obj+22),'blocked':get(ram,obj+26),'argument':get(ram,obj+30),'suspend_count':get(ram,obj+34)})
  obj=get(ram,obj)
 assert obj==RENDER and len(rows)==21 and get(ram,0xc0924)==0
 for row in rows:
  assert get(ram,row['next']+4)==row['context']and get(ram,row['prev'])==row['context']
 for obj,entry in zip(CREATED,TASKS):
  assert get(ram,obj+8)==entry and get(ram,obj+16)==entry and get(ram,obj+12)==obj+0x400
  assert all(get(ram,obj+offset,width)==0 for offset,width in [(20,2),(22,4),(26,4),(34,4)])
  assert get(ram,obj+30)==(0x1388 if entry==0x18b86 else 0)
 return rows
class Runtime(prior.Runtime):
 def __init__(self,library):
  super().__init__(library);self.start=self.lib.biwn_render_startup;self.start.argtypes=[c.POINTER(world.Bus),c.POINTER(CPU),SERVICE,c.c_void_p];self.start.restype=c.c_int;self.rng,self.div,self.mul=rngcheck.bind(self.lib);self.services,self.poll,self.reset=helpers.bind(self.lib)
  self.create=self.lib.biwn_task_create;self.create.argtypes=[c.POINTER(world.Bus),c.POINTER(CPU)];self.create.restype=c.c_int
  self.core.JaguarWriteWord.argtypes=[c.c_uint32,c.c_uint16,c.c_uint32];self.core.JaguarReadLong.argtypes=[c.c_uint32,c.c_uint32];self.core.JaguarReadLong.restype=c.c_uint32
  self.core.TOMReadWord.argtypes=[c.c_uint32,c.c_uint32];self.core.TOMReadWord.restype=c.c_uint16;self.pad=pad.Backend(self.core,self.device);mapping=json.loads((ROOT/'verification/emulated-pad-mapping.json').read_text())['button_to_game_bit'];self.bit0_buttons=[int(k)for k,v in mapping.items()if v==1]
 def hardware(self):return {'video_words':[self.core.TOMReadWord(a,6)for a in range(0xf00400,0xf00408,2)]}
 def startup_script(self,target,args,d0):
  if target==0x1af04:return 0x112d5c
  if target==0x152a2:return 0x112d58
  assert target in START_STUBS;return self.return_word^target
 def block(self):
  for obj in CONTEXTS:self.device.direct(obj+26,4,0 if obj in[RENDER,*prior.IDLES]else 1)
 def native(self,ram,incoming,clocks,word):
  self.return_word=word;self.device.seed(ram,0);self.pad.set_buttons(self.bit0_buttons if word&1 else [])
  for target in STUBS:self.device.direct(target,2,0x4e75)
  self.core.m68k_pulse_reset();self.core.m68k_set_irq(0);self.core.m68k_set_reg(17,0x2000);self.core.m68k_set_reg(15,SSP);self.core.m68k_set_reg(17,0)
  for i,value in enumerate(incoming):self.core.m68k_set_reg(i,value)
  self.core.m68k_set_reg(15,RENDER+0x400);self.core.m68k_set_reg(16,0x17c40)
  calls=[];handoffs=[];steps=[];clock_index=0;started=False;startup=None
  for _ in range(250000):
   pc=self.core.m68k_get_reg(None,16)
   if pc==0x17dc2:
    if started:break
    startup={'ram':self.device.ram(),'CPU':self.cpu(),'calls':list(calls),'hardware':self.hardware()}
    for target in STUBS:
     data=bytearray(startup['ram']);data[target:target+2]=ram[target:target+2];startup['ram']=bytes(data)
    startup['contexts']=task_table(startup['ram']);self.block();started=True
   if started and pc in[0x17dc2,0x17dd4,0x17de0,0x17dec]:self.device.direct(0x778cc,4,clocks[clock_index]);clock_index+=1
   assert any(a<=pc<b for a,b in [(0x17c40,0x17f68),(0xde5c,0xdeb6),(0xdf6c,0xdf7a),(0xea28,0xeac4),(0xe2b8,0xe2f4),(0xe098,0xe0a6),(0xe03a,0xe098),(0xdf60,0xdf6c),(0xde08,0xde5c),(0xf360,0xf368),(0xf880,0xf888),(0x181f8,0x18554),(0x14776,0x14caa),(0x1b160,0x1b478),(0xe61c,0xe68c),(0xe540,0xe588),(0x185b2,0x18854),(0x4088,0x408a),(0x1a6e0,0x1a91e),(0xe540,0xe61c)]+list(helpers.RANGES.items())+[(0xe4c0,0xe53c),(0xea20,0xea28)])or pc in STUBS,hex(pc)
   steps.append(pc)
   if pc in LOGGED and not (pc in [0xe540,0xe588,0xe60a] and not 0x1a6e0<=int.from_bytes(c.string_at(self.device.pointer+self.core.m68k_get_reg(None,15),4),'big')<0x1a91e) and not (pc==0xe588 and int.from_bytes(c.string_at(self.device.pointer+self.core.m68k_get_reg(None,15),4),'big')==0xe616):
    stack=self.core.m68k_get_reg(None,15);widths=helpers.WIDTHS.get(pc,rngcheck.CALL_WIDTHS.get(pc,prior.overlay.WIDTHS.get(pc,[4]*(3 if pc==0xe2b8 else 2 if pc in[0xe03a,0x185b2,0xdf6c]else 0))));args=[];offset=4
    for width in widths:args.append(int.from_bytes(c.string_at(self.device.pointer+stack+offset,width),'big'));offset+=width
    calls.append(['call',pc,args])
    if pc in STUBS:self.core.m68k_set_reg(0,self.scripted(pc,args,self.core.m68k_get_reg(None,0))if pc in prior.STUBS else self.startup_script(pc,args,self.core.m68k_get_reg(None,0)))
   self.core.m68k_execute(1)
   if self.core.GPUReadLong(0xf03204,0)==0x4b00:self.device.write(0xf03204,4,0x4b00)
   if pc==0xdf6a or(pc==0xde5a and self.core.m68k_get_reg(None,16)!=0xdf66):handoffs.append(self.event(self.cpu()))
  else:raise AssertionError('Original startup/loop did not reach backedge')
  for target in STUBS:self.device.direct(target,2,get(ram,target,2))
  assert startup and clock_index==4;return self.device.ram(),self.cpu(),{'startup':startup,'calls':calls,'handoffs':handoffs,'steps':steps,'device':self.device.stats()}
 def translated(self,ram,incoming,clocks,word,guard=None):
  self.return_word=word;self.device.seed(ram,1);self.pad.set_buttons(self.bit0_buttons if word&1 else []);cpu=CPU();cpu.registers[:]=incoming;cpu.registers[15]=RENDER+0x400;cpu.usp=cpu.registers[15];cpu.ssp=SSP;cpu.pc=0x17c40;cpu.sr=0;calls=[];handoffs=[];errors=[];creations=0;service_stack=0
  def write32(_,address,value):
   nonlocal creations
   if guard=='write_error':return 1
   status=self.device.w32(None,address,value)
   if not status and creations<17 and value==RETURNS[creations]and RENDER+0x26<=address<RENDER+0x400:
    values=[get(self.device.ram(),address+4),get(self.device.ram(),address+8)];assert values==[TASKS[creations],0];calls.append(['call',0xdf6c,values]);creations+=1
   return status
  w32=world.W32(write32)
  def write16(_,address,value):
   if address>=0xf00000:self.core.JaguarWriteWord(address,value,6);return 0
   return self.device.w16(None,address,value)
  w16=world.W16(write16)
  def read32(_,address,out):
   if address==0xf14000:out[0]=self.core.JaguarReadLong(address,6);return 0
   return self.device.r32(None,address,out)
  wrapped_r32=world.R32(read32)
  def call(_,target,args,n,out):
   nonlocal creations
   try:
    values=list(args[:n]);calls.append(['call',target,values])
    if target in START_STUBS:out[0]=self.startup_script(target,values,out[0]);return 0
    if target in [0x1aeda,0xf0c0]:return self.services(c.byref(bus),self.device.write8,target,out[0],out)
    if target==0xea20:return self.reset(c.byref(bus))
    if target==0xe4c0:return self.poll(c.byref(bus))
    if target==0xdf6c:
     assert creations==0 and values==[0x18b86,0x1388];nested=CPU.from_buffer_copy(bytes(cpu));nested.registers[15]=service_stack-30;nested.usp=nested.registers[15];nested.pc=0xdf6c
     self.device.direct(nested.registers[15],4,0x18d7c);self.device.direct(nested.registers[15]+4,4,values[0]);self.device.direct(nested.registers[15]+8,4,values[1])
     status=self.create(c.byref(bus),c.byref(nested))
     if not status:out[0]=nested.registers[0];creations+=1
     return status
    if target==0xe60a:assert n==2;return self.rng[target](*values,out)
    if target==0xe588:
     assert n==2;q=c.c_uint32();r=c.c_uint32();status=self.div(*values,c.byref(q),c.byref(r))
     if not status:out[0]=q.value
     return status
    if target==0xe540:assert n==2;out[0]=self.mul(*values);return 0
    if target==0x1a87a:assert n==1;return self.rng[target](c.byref(bus),values[0],out[0],out)
    if target==0x1a8c6:assert n==1;return self.rng[target](c.byref(bus),values[0],out)
    if target==0x1a7f4:assert n==0;return self.rng[target](c.byref(bus),255,out)
    if target==0xe03a:return self.clear(c.byref(bus),*values,4096)
    if target==0x17f14:return self.rotate(c.byref(bus),out[0],out)
    if target==0xe2b8:
     gpu=prior.render.GpuBus(self.device.r32,w32,None,100000);return self.device.protocol(c.byref(gpu),*values)
    if target==0x185b2:
     links=(c.c_uint32*64)();return self.display(c.byref(bus),*values,links,64,4096,out)
    if target==0x1b45a:return self.format(c.byref(bus),self.device.write8,*values,out)
    if target==0x149ae:
     text_bus=prior.TextBus(self.device.r8,self.device.r16,w32,None,100000);args=prior.TextArgs(*values);return self.text(c.byref(text_bus),c.byref(args),out)
    assert target in prior.STUBS;out[0]=self.scripted(target,values,out[0]);return 0
   except Exception as error:errors.append(repr(error));return 1
  cb=world.CALL(call);r32=world.R32(lambda *_:1)if guard=='read_error'else wrapped_r32
  bus=world.Bus(self.device.r8,self.device.r16,r32,w16,w32,cb,None,0)
  def startup_service(_,passed,state,target):
   nonlocal service_stack
   try:
    if guard=='service_error':return 1
    stack=state.contents.registers[15];service_stack=stack;n=2 if target in[0xe03a,0x185b2]else 0;values=[get(self.device.ram(),stack+4+i*4)for i in range(n)];calls.append(['call',target,values]);d0=c.c_uint32(state.contents.registers[0])
    if target==0x4088:status=0
    elif target==0x1a6e0:status=self.rng[target](c.byref(bus),d0.value,c.byref(d0));state.contents.sr&=0xffe0
    elif target==0xe03a:status=self.clear(c.byref(bus),*values,4096);state.contents.sr=(state.contents.sr&0xffe0)|0x10
    elif target==0x185b2:
     links=(c.c_uint32*64)();status=self.display(c.byref(bus),*values,links,64,4096,c.byref(d0));state.contents.sr&=0xffe0
    else:
     assert target in START_SERVICES;status=self.services(c.byref(bus),self.device.write8,target,d0.value,c.byref(d0))
     if target==0xe2f4:state.contents.sr=(state.contents.sr&0xfff0)|4
     elif target==0x18160:state.contents.sr&=0xfff0
     elif target==0x21242:state.contents.sr=(state.contents.sr&0xffe0)|4;state.contents.registers[1]=50
     elif target==0x18ba8:state.contents.sr&=0xffe0;state.contents.registers[1]=0
     elif target==0xdfc0:state.contents.sr=(state.contents.sr&0xfff0)|4
    state.contents.registers[0]=d0.value
    if guard=='bad_return':state.contents.registers[15]+=4
    return status
   except Exception as error:errors.append(repr(error));return 1
  service_cb=SERVICE(startup_service);before=bytes(cpu)
  status=self.start(c.byref(bus),c.byref(cpu),service_cb,None)
  if guard:
   assert status and bytes(cpu)==before;return status,errors
  assert status==0 and not errors,(status,errors);startup={'ram':self.device.ram(),'CPU':CPU.from_buffer_copy(bytes(cpu)),'calls':list(calls),'hardware':self.hardware()};startup['contexts']=task_table(startup['ram']);assert creations==17;self.block()
  def service(_,passed,state,target):
   try:
    calls.append(['call',target,[]]);d0=c.c_uint32(state.contents.registers[0])
    if target==0xea28:status=self.device.consumer(c.cast(c.byref(bus),c.POINTER(prior.render.Bus)),self.device.write8,64,d0.value,c.byref(d0))
    elif target==0x17e0e:status=self.scene(c.byref(bus),4096,d0.value,c.byref(d0))
    else:assert target==0x181f8;status=self.overlay(c.byref(bus),state.contents.registers[15]-54,d0.value,c.byref(d0))
    assert status==0;state.contents.registers[0]=d0.value;return 0
   except Exception as error:errors.append(repr(error));return 1
  loop_cb=SERVICE(service);begun=False;clock_index=0;steps=[]
  for _ in range(1000):
   pc=cpu.pc
   if pc==0x17dc2 and begun:break
   begun=True;steps.append(pc)
   if pc in[0x17dc2,0x17dd4,0x17de0,0x17dec]:self.device.direct(0x778cc,4,clocks[clock_index]);clock_index+=1
   yielding=pc in[0x17dc2,0xf360,0xf880]
   if yielding:calls.append(['call',0xdf60,[]])
   status=self.render_step(c.byref(bus),c.byref(cpu),loop_cb,None,64)if self.current()==RENDER else self.idle_step(c.byref(bus),c.byref(cpu),BODY(),None,64)
   assert status==0,(status,hex(pc),errors)
   if yielding:handoffs.append(self.event(cpu))
  else:raise AssertionError('C startup/loop did not finish')
  assert not errors and clock_index==4;return self.device.ram(),cpu,{'startup':startup,'calls':calls,'handoffs':handoffs,'steps':steps,'device':self.device.stats()}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opts=ap.parse_args();out=ROOT/'verification/biwn-render-services-runtime'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';lib=out/'librender-services.dylib';names=['biwn_render_startup.c','biwn_task_create.c','biwn_render_loop.c','biwn_render_scene.c','biwn_scheduler.c','biwn_task_loops.c','biwn_overlay.c','biwn_overlay_format.c','biwn_text.c','biwn_display_list.c','biwn_rng.c','biwn_signed_division.c','biwn_camera.c','biwn_startup_services.c','biwn_input_poll.c','biwn_animation_images.c'];cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(source/n)for n in names]+['-o',str(lib)];subprocess.run(cmd,check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});runtime=Runtime(lib);manifest,snapshot=prior.render.assets();rng=random.Random(0x17c40);rows=[];coverage=set()
 try:
  for i in range(opts.limit or 144):
   save(out/'status.json',{'status':'running','case':i});ram,info=fixture(snapshot,i);incoming=[rng.getrandbits(32)for _ in range(16)];clocks=[rng.getrandbits(32)for _ in range(4)];word=rng.getrandbits(32)
   left,original,om=runtime.native(ram,incoming,clocks,word);right,actual,cm=runtime.translated(ram,incoming,clocks,word);coverage.update(om['steps']);a=om['startup'];b=cm['startup']
   startup_equal=masked(a['ram'])==masked(b['ram'])and bytes(a['CPU'])==bytes(b['CPU'])and a['calls']==b['calls']and a['contexts']==b['contexts']and a['hardware']==b['hardware']
   registers=[j for j in range(16)if j not in[8,9]]
   final_equal=masked(left)==masked(right)and all(original.registers[j]==actual.registers[j]for j in registers)and(original.pc,original.usp,original.ssp,original.sr)==(actual.pc,actual.usp,actual.ssp,actual.sr)and om['calls']==cm['calls']and om['handoffs']==cm['handoffs']
   if not startup_equal or not final_equal:
    save(out/'mismatch.json',{'case':i,'startup_equal':startup_equal,'final_equal':final_equal,'original_startup_CPU':prior.scheduler.cpu_dict(a['CPU']),'C_startup_CPU':prior.scheduler.cpu_dict(b['CPU']),'original_final_CPU':prior.scheduler.cpu_dict(original),'C_final_CPU':prior.scheduler.cpu_dict(actual),'original_calls':om['calls'],'C_calls':cm['calls'],'original_handoffs':om['handoffs'],'C_handoffs':cm['handoffs']});raise AssertionError(str(out/'mismatch.json'))
   assert len(om['handoffs'])==3 and cm['device']['C_sprite_decodes']==0 and om['device']['original_GPU_sprite_decodes']==0 and not cm['device']['original_GPUExec1_calls']and not cm['device']['game_frames_executed']
   rows.append({'case':i,'frame_index':i%72,'initial_registers':incoming,'clocks':clocks,'helper_seed':word,'startup_CPU':prior.scheduler.cpu_dict(b['CPU']),'startup_calls':b['calls'],'startup_contexts':b['contexts'],'startup_hardware':b['hardware'],'requested_game_input_bit0':bool(word&1),'final_CPU':prior.scheduler.cpu_dict(actual),'calls':cm['calls'],'handoffs':cm['handoffs'],'original':om['device'],'rebuilt':cm['device'],'startup_whole_CPU_and_visible_RAM_match':True,'public_context_header_bytes_compared':38,'final_visible_RAM_selected_CPU_match':True})
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
 finally:runtime.close()
 save(out/'fixtures.json',rows);session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();decoded,_=world.select.binary_tools.m68k_instructions(image[0x17c40-0x4000:0x17e0e-0x4000],0x17c40);addresses={x['address']if isinstance(x['address'],int)else int(x['address'],16)for x in decoded};covered=addresses&coverage
 if opts.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows),'coverage':[len(covered),len(addresses)]});print(json.dumps({'directory':str(out),'cases':len(rows),'coverage':[len(covered),len(addresses)]}));return
 assert addresses<=coverage
 helper_addresses=set()
 for lo,hi in helpers.RANGES.items():
  decoded,_=world.select.binary_tools.m68k_instructions(image[lo-0x4000:hi-0x4000],lo);helper_addresses.update(row['address']for row in decoded)
 assert helper_addresses<=coverage
 runtime=Runtime(lib);guards=[]
 try:
  ram,_=fixture(snapshot,0)
  for guard in['read_error','write_error','service_error','bad_return']:
   status,errors=runtime.translated(ram,[0]*16,[0]*4,0,guard=guard);guards.append({'kind':guard,'status':status,'caller_CPU_unchanged':True,'partial_effects_retained':True})
  for kind in['null_bus','null_cpu','null_service','missing_read32','missing_write16','missing_write32','unsupported_PC','supervisor_mode']:
   runtime.device.seed(ram,1);cpu=CPU();cpu.registers[15]=RENDER+0x400;cpu.usp=cpu.registers[15];cpu.ssp=SSP;cpu.pc=0x17c40
   if kind=='unsupported_PC':cpu.pc=0x17dc2
   if kind=='supervisor_mode':cpu.sr=0x2000
   r32=world.R32()if kind=='missing_read32'else runtime.device.r32
   w16=world.W16()if kind=='missing_write16'else runtime.device.w16
   w32=world.W32()if kind=='missing_write32'else runtime.device.w32
   bus=world.Bus(runtime.device.r8,runtime.device.r16,r32,w16,w32,world.CALL(),None,0)
   cb=SERVICE()if kind=='null_service'else SERVICE(lambda *_:0);before=bytes(cpu);before_ram=runtime.device.ram()
   status=runtime.start(None if kind=='null_bus'else c.byref(bus),None if kind=='null_cpu'else c.byref(cpu),cb,None)
   assert status==1 and bytes(cpu)==before and runtime.device.ram()==before_ram
   guards.append({'kind':kind,'rejected':True,'caller_CPU_and_RAM_unchanged':True})
 finally:runtime.close()
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'full_render_caller_all_startup_bodies_and_loop_match_native_C','directory':str(out),'cases':len(rows),'created_tasks_per_case':17,'supplied_contexts':4,'created_task_calls':len(rows)*17,'contexts_after_startup':21,'startup_complete_caller':True,'startup_services_fully_reconstructed':False,'startup_service_instruction_coverage':[len(helper_addresses&coverage),len(helper_addresses)],'emulated_pad_poll_cases':len(rows),'scene_call_boundary_cases':sum(any(call[1]==0x11e6c for call in row['startup_calls'])for row in rows),'render_task_caller_instruction_coverage':[len(covered),len(addresses)],'render_task_interval':'[0x17c40,0x17e0e)','new_complete_caller_components':0,'new_rng_components':0,'new_startup_service_components':7,'RNG_initializations':sum(sum(call[1]==0x1a6e0 for call in row['calls'])for row in rows),'RNG_fill_iterations':sum(sum(call[1]==0xe60a for call in row['startup_calls'])for row in rows),'additional_noop4088_components_counted':0,'implemented_captured_task_callers_total':4,'other_captured_task_callers_unported':17,'public_context_header_bytes_compared':38,'saved_context_CCR_bits_compared':True,'blocked_contexts_after_startup':18,'runnable_task_bodies_in_test':3,'task_handoffs':len(rows)*3,'C_sprite_decodes':sum(row['rebuilt']['C_sprite_decodes']for row in rows),'display_list_calls':sum(sum(c[1]==0x185b2 for c in r['calls'])for r in rows),'text_calls':sum(sum(c[1]==0x149ae for c in r['calls'])for r in rows),'host_guards':len(guards),'linked_to_existing_world_runtime':False,'complete_game_frames_executed':0,'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in names+[n.replace('.c','.h')for n in names]},'asset_sha256':manifest['assets'],'startup_scripted_targets':[],'startup_nested_scripted_targets':[hex(a)for a in START_STUBS],'render_scripted_targets':[hex(a)for a in prior.STUBS],'matched':['Actual startup/RNG/sevennewstartupbodies/17realcreations followed uninterrupted by scheduledrendercontinuation, consumer/scene/display/overlay/text: originalnativeCPU/GPU vsC; full startupCPU/SR/SP/PC, contextlist/headers and allvisibleRAM/calls match.','At startup4supplied plus17createdcontexts form exact21context bidirectional ring,17entries/savedPC/SP/args/readinessfields match source andfreeheadzero. Eighteen contexts are then explicitly blocked; render/twoidle execute432handoffs across144cases.','FinalCPU exceptA0/A1 andprivate-stack/formatter10byte exclusions; all38publiccontextheaderbytes including savedCCR now compared, unlike earlier overbroad26byte boundary. Existing display runtime also rerun with corrected boundary.'],'limits':['All top-level startup callers execute real code, but seven nested resource/allocator/scene services and six render services remain scripted. Four supplied contexts/freepool and frozen assets are fixtures, not full system boot or asset lifecycles. EA20 now clears the seeded sprite queue; no animation producers run, so no sprite decodes are claimed in this test.','All caller controlflow is reconstructed; callee internals/worldrender integration, actor/assetlifecycles, unportedtaskbodies, full3Ddraw/scanout/mainloop/scenes/audio/game/hardware unfinished. Newly created nonidle tasks remain blocked in this bounded runtime.','Startup source-body/RNG/clear/display adapters supply checked finalCCR effects for known finite source paths; other helper caller-saved effects are outside their contracts. Host errors retain partialeffects/unchangedCPU.']}
 save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-render-services-runtime-checks.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
