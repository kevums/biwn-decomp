"""Original source loader vs fullCPU C loader on actual interior payloads.
Complete RAM/privateframes/stageCPU/nestedhelperstates and disc transfers compare.
Direct supplied mode2 entries retain synchronous BIOS/DF60 adapters.
"""
import ctypes as c,hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_cd_cpu as cd
import generate_biwn_interior_loading_cpu as gen
from biwn_disc_backend import Disc
ROOT=gen.ROOT;CPU=cd.CPU;save=cd.save;read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest();SP=cd.SP;STOP=cd.STOP
ADAPTERS={0x303c,0x3042,0xdf60}
class Runtime(cd.Runtime):
 def __init__(self,library,rows):
  super().__init__(library,rows);self.entry_points=[0x1aa40,0x20f78];self.disc=Disc();self.bodies={};self.fullcalls={}
  entries={entry:'interior_loading'for entry in gen.RANGES};entries.update({0x1b044:'resource',0xe3e0:'resource',0xe3ee:'resource',0xd1e0:'cd',0xd206:'cd',0xd2f0:'cd',0xd306:'cd'})
  for target,name in entries.items():
   for table,suffix in [(self.bodies,'body'),(self.fullcalls,'call')]:
    fn=getattr(self.lib,'biwn_'+name+'_cpu_'+suffix);fn.argtypes=[c.POINTER(cd.world.Bus),c.POINTER(CPU),cd.dispatch.W8,cd.world_cpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];fn.restype=c.c_int;table[target]=fn
 def adapter(self,state,target):
  row=dict(target=target,actual_body=False,incoming=cd.scheduler.cpu_dict(state));self.calls.append(row)
  if target==0x303c:self.disc.start(state.registers[8],state.registers[9],state.registers[0])
  elif target==0x3042:self.disc.stop()
  elif target==0xdf60:
   assert self.disc.pending,'Loader completion adapter without pending transfer';self.disc.tick(lambda a,data:c.memmove(self.device.pointer+a,data,len(data)),lambda a,v:self.device.direct(a,4,v))
  else:raise AssertionError(hex(target))
  row['return']=cd.scheduler.cpu_dict(state)
 def prepare(self,ram,mode):
  self.device.seed(ram,mode);self.disc.reset();self.calls=[];self.trace=[];self.errors=[]
 def canonical_RAM(self,ram):
  memory=bytearray(self.device.ram())
  for a in [0x303c,0x3042]:memory[a:a+2]=ram[a:a+2]
  return bytes(memory)
 def initial_CPU(self,entry):
  state=CPU();state.registers[:]=[0]*15+[SP];state.pc=entry;state.usp=SP;state.ssp=SP;state.sr=0x2000;return state
 def native(self,ram,coverage):
  self.prepare(ram,0);stages=[];steps=[]
  for a in [0x303c,0x3042]:self.device.direct(a,2,0x4e75)
  for entry in self.entry_points:
   if hasattr(self,'before_native_entry'):self.before_native_entry(entry,ram)
   cd.lifecycle.seed_cpu(self,self.initial_CPU(entry));stack=[];pending=None
   for _ in range(1000000):
    pc=self.core.m68k_get_reg(None,16)
    if pc==STOP:break
    if pc in ADAPTERS:
     state=self.cpu();self.adapter(state,pc)
     if pc==0xdf60:
      sp=state.registers[15];self.core.m68k_set_reg(16,self.device.read(sp,4));self.core.m68k_set_reg(15,sp+4);pending=None;continue
     if pc==0x3042 and stack and stack[-1]['target']==0xd306:stack.pop()['return']=cd.scheduler.cpu_dict(self.cpu())
     self.core.m68k_execute(1);pending=None;continue
    assert pc in self.rows,hex(pc);row=self.rows[pc]
    if pending==pc:
     frame=dict(target=pc,actual_body=True,incoming=cd.scheduler.cpu_dict(self.cpu()));self.calls.append(frame);stack.append(frame);pending=None
    if row['assembly']=='rts'and stack and self.cpu().registers[15]==stack[-1]['incoming']['registers'][15]:stack.pop()['return']=cd.scheduler.cpu_dict(self.cpu())
    if row['assembly'].startswith(('jsr ','bsr.')):
     tail=row['assembly'].split(' ',1)[1]
     target=self.core.m68k_get_reg(None,gen.base.register(tail[1:-1]))if tail.startswith('(')else int(tail.split('$')[1].split('.')[0],16)
     assert target in self.bodies or target in ADAPTERS,hex(target);pending=target if target in self.bodies else None
    coverage.add(pc);steps.append(pc);self.core.m68k_execute(1)
    if hasattr(self,'after_native_instruction'):self.after_native_instruction(pc)
   else:raise AssertionError(('Original loader worklimit',hex(pc)))
   assert not stack,stack[-2:];stages.append(dict(entry=hex(entry),CPU=cd.scheduler.cpu_dict(self.cpu()),RAM_sha256=sha(self.canonical_RAM(ram))))
  for a in [0x303c,0x3042]:self.device.direct(a,2,int.from_bytes(ram[a:a+2],'big'))
  return self.device.ram(),stages,dict(calls=list(self.calls),steps=steps,disc_requests=list(self.disc.requests),disc_completions=list(self.disc.completions),disc_stops=self.disc.stops,device=self.device.stats())
 def translated(self,ram):
  self.prepare(ram,1);stages=[]
  def reader(width):
   def cb(_,a,value):
    try:value[0]=self.device.read(a,width);return 0
    except Exception as e:self.errors.append(repr(e));return 1
   return cb
  def writer(width):
   def cb(_,a,value):
    try:
     if width==1:
      assert 0<=a<0x200000;self.device.direct(a,width,value)
     elif width==2:self.device.write16(a,value)
     else:self.device.write(a,value)
     return 0
    except Exception as e:self.errors.append(repr(e));return 1
   return cb
  callbacks=[cd.world.R8(reader(1)),cd.world.R16(reader(2)),cd.world.R32(reader(4)),cd.world.W16(writer(2)),cd.world.W32(writer(4)),cd.dispatch.W8(writer(1))];bus=cd.world.Bus(*callbacks[:5],cd.world.CALL(),None,0)
  def service(_,passed,state,target):
   try:
    if target in ADAPTERS:self.adapter(state.contents,target);return 0
    assert target in self.bodies,hex(target);row=dict(target=target,actual_body=True,incoming=cd.scheduler.cpu_dict(state.contents));self.calls.append(row);
    status=self.bodies[target](passed,state,callbacks[5],callback,None,1000000,0);row['return']=cd.scheduler.cpu_dict(state.contents)
    if status:self.errors.append(dict(target=hex(target),status=status))
    return status
   except Exception as e:self.errors.append(repr(e));return 1
  callback=cd.world_cpu.SERVICE(service)
  for entry in self.entry_points:
   state=self.initial_CPU(entry);status=self.fullcalls[entry](c.byref(bus),c.byref(state),callbacks[5],callback,None,1000000,0)
   stages.append(dict(entry=hex(entry),CPU=cd.scheduler.cpu_dict(state),RAM_sha256=sha(self.device.ram())))
   if status:break
  return self.device.ram(),stages,dict(status=status,calls=list(self.calls),errors=self.errors,disc_requests=list(self.disc.requests),disc_completions=list(self.disc.completions),disc_stops=self.disc.stops,device=self.device.stats())
def main():
 out=ROOT/'verification/biwn-interior-loading-cpu'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_interior_loading_cpu.c','biwn_resource_cpu.c','biwn_cd_cpu.c'];library=out/'libinterior-loading-cpu.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(source/n)for n in names]+['-o',str(library)];run=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert not run.returncode,run.stderr
 session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'interior-loading-fullCPU-generation.json');rows=mapping['instructions_decoded']+read(session/'resource-fullCPU-generation.json')['instructions_decoded']+read(session/'cd-wrapper-fullCPU-generation.json')['instructions_decoded'];runtime=Runtime(library,rows);capture=Path(read(ROOT/'verification/biwn-interior-original-loading-probes.json')['directory']);fixtures=read(capture/'cases.json');results=[];coverage=set()
 try:
  for i,fixture in enumerate(fixtures):
   save(out/'status.json',dict(status='running',case=i));path=capture/f"interior-{fixture['interior']}-room-{fixture['selected_room']}-before-RAM.bin";ram=path.read_bytes();assert sha(ram)==fixture['before_RAM_sha256'];left,expected,native=runtime.native(ram,coverage);right,actual,rebuilt=runtime.translated(ram)
   keys=['calls','disc_requests','disc_completions','disc_stops']
   if rebuilt['status']or left!=right or expected!=actual or any(native[k]!=rebuilt[k]for k in keys):
    (out/'original-final-RAM.bin').write_bytes(left);(out/'C-final-RAM.bin').write_bytes(right);save(out/'mismatch.json',dict(case=i,fixture={k:v for k,v in fixture.items()if k not in ['source_CPU_PC_samples','calls']},native_stages=expected,C_stages=actual,native=native,C=rebuilt,RAM_differences=[hex(j)for j,(a,b)in enumerate(zip(left,right))if a!=b][:80]));raise AssertionError(str(out/'mismatch.json'))
   assert not rebuilt['device']['GPUExec1_calls']and not rebuilt['device']['game_frames_executed'];assert right==Path(fixture['after_RAM_path']).read_bytes(),'Fresh original/C loader differ from retained input capture'
   before=out/f"interior-{fixture['interior']}-room-{fixture['selected_room']}-before-RAM.bin";after=out/f"interior-{fixture['interior']}-room-{fixture['selected_room']}-C-after-RAM.bin";before.write_bytes(ram);after.write_bytes(right)
   results.append(dict(case=i,interior=fixture['interior'],selected_room=fixture['selected_room'],before_RAM_path=str(before),after_RAM_path=str(after),before_RAM_sha256=sha(ram),after_RAM_sha256=sha(right),stage_states=actual,helper_calls=rebuilt['calls'],disc_requests=rebuilt['disc_requests'],disc_completions=rebuilt['disc_completions'],disc_stops=rebuilt['disc_stops'],native_CPU_steps=len(native['steps']),whole_CPU_main2MBRAM_privateframes_nestedhelpers_and_disc_transfers_match=True));save(out/'cases.json',results)
  decoded={x['address']for x in mapping['instructions_decoded']};covered=decoded&coverage;save(out/'coverage.json',dict(instructions=mapping['instructions_decoded'],uncovered=[r for r in mapping['instructions_decoded']if r['address']not in covered]));report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='actual_mode2_C_loader_texture_cache_position_and_disc_CPU_chain_matches_original',directory=str(out),cases=len(results),source_group_instruction_coverage=[len(covered),len(decoded)],native_CPU_steps=sum(r['native_CPU_steps']for r in results),disc_transfers=sum(len(r['disc_requests'])for r in results),transferred_bytes=sum(sum(q['bytes']for q in r['disc_requests'])for r in results),original_CPU_or_GPU_execution_on_C_side=False,C_loader_verified_for_declared_cases=True,source_mode1_fullCPU_verified=False,source_interiors=[1,2,3],interior0_actor_creation_verified=False,source_boundary_transition_verified=False,source_sha256={n:sha((source/n).read_bytes())for n in names},generator_sha256=mapping['generator_sha256'],test_script_sha256=sha(Path(__file__).read_bytes()),compiler=cmd,new_published_components=0,whole_game_complete=False,limits=['Sixdeclaredmode2entries(first/largestroompositions inactualinteriors1/2/3). Both top-levelCPUstates,allD/A/SR/USP/SSP,main2MBRAM/privateLINK/MOVEM/argumentframes,allnestedhelperstates andpreserveddiscbytes/requests/completion/stop match freshoriginalCPU. SourceCloader/texture/cache/copy/CDmath/wrappers execute; no originalCPU/GPU on Cside.', 'Hostdirectly invokes1AA40then20F78 withsuppliedCPUregisters/stack/mode2/camera/origin andpriorassistedstartupRAM. BIOS303C/3042preserve-register RTSadapters andDF60synchronouscompletion remain; no source schedulerCDyield, boundarytransition/cleanup,uninterruptedboot/physicalCDtiming claim.', '807instructiongeneratedgroup includesunreachedoutdoorfunctions/branches; coverage explicitlypartial. Interior0has two actors and isunverified, not replacedbyemptylist. Rendering andscheduledindoorworld/input/audio/boot/globalGPUstate/OPscanout/fullgame remainseparate. HostDIVSzero/overflow returnerrors,notoriginalexceptions.'])
  save(out/'report.json',report);save(out/'status.json',dict(status='terminal_bounded_pass'));save(ROOT/'verification/biwn-interior-loading-cpu-checks.json',report);save(ROOT/'verification/biwn-interior-C-loading-captures.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ['compiler','source_sha256']}))
 except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
 finally:runtime.close()
if __name__=='__main__':main()
