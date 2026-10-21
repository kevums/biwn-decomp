"""Complete10990 caller linked to real10968/11762, other3helpers explicit."""
import argparse,ctypes as c,hashlib,json,os,random,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_local_scene_record_insert as insert
import check_local_slot_clear as slot
ROOT=insert.ROOT;SP=insert.SP;STOP=insert.STOP;w=insert.w;SCRIPTED=[0x18160,0x1ac68];WIDTHS={0x1aa40:[2],0x18160:[],0x10a6a:[2],0x10968:[2,2],0x11762:[2,4,4,4],0x1ae88:[2],0x1ac68:[2]};SLOT=None;INSERT=None;TEXTURES=None;SELECT=None;RELEASE=None
sha=lambda b:hashlib.sha256(b).hexdigest()
class Script(insert.Script):
 def __init__(self,snapshot,case):super().__init__(snapshot,case);self.case=case;self.changed=[];self.fail_call=None
 def call(self,target,args,incoming):
  if self.fail_call==target:raise RuntimeError('Injected helper failure')
  self.trace.append(['call',target,args,incoming]);self.changed=[]
  for a,width,value in self.case.get('helper_effects',{}).get(str(target),[]):
   self.memory[a:a+width]=value.to_bytes(width,'big');self.changed.append([a,width,value])
  return self.case['helper_returns'][str(target)]
def original(script,case,coverage):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(script.memory));cpu.mem_write(SP,STOP.to_bytes(4,'big'))
 for reg,value in zip(insert.animation.boundary.REGS,case['incoming']):cpu.reg_write(reg,value)
 cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP)
 for target in SCRIPTED:cpu.mem_write(target,b'\x4e\x75')
 def code(e,a,width,_):
  if a in WIDTHS:
   sp=e.reg_read(UC_M68K_REG_A7);off=4;args=[]
   for size in WIDTHS[a]:args.append(int.from_bytes(e.mem_read(sp+off,size),'big'));off+=size
   if a in SCRIPTED:
    value=script.call(a,args,e.reg_read(UC_M68K_REG_D0))
    for addr,size,v in script.changed:e.mem_write(addr,v.to_bytes(size,'big'))
    e.reg_write(UC_M68K_REG_D0,value);return
   script.trace.append(['call',a,args,e.reg_read(UC_M68K_REG_D0)])
  assert 0x10990<=a<=0x10a68 or 0x10968<=a<=0x1098e or 0x11762<=a<=0x11806 or 0x1aa40<=a<0x1aade or 0x10a6a<=a<=0x10ba2 or 0x1ae88<=a<=0x1aed8,hex(a);coverage.add(a)
 def read(e,t,a,width,value,_):
  if SP-0x1000<=a<SP+4:return
  e.mem_write(a,script.read(a,width).to_bytes(width,'big'))
 def write(e,t,a,width,value,_):
  if SP-0x1000<=a<SP+4:return
  script.write(a,width,value&((1<<(width*8))-1))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(0x10990,STOP,count=10000,timeout=1000000);assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
 memory=bytearray(cpu.mem_read(0,0x200000))
 for target in SCRIPTED:memory[target:target+2]=script.memory[target:target+2]
 if case.get('index_reads'):assert memory[:0x400e4]==script.memory[:0x400e4]and memory[0x400e6:SP-0x1000]==script.memory[0x400e6:SP-0x1000]
 else:assert memory[:SP-0x1000]==script.memory[:SP-0x1000]
 assert memory[SP+4:]==script.memory[SP+4:];return cpu.reg_read(UC_M68K_REG_D0)
def translated(fn,script,case,missing=None,nullbus=False,nullout=False):
 errors=[]
 def read(width):
  def f(_,a,out):
   try:out[0]=script.read(a,width);return 0
   except Exception as error:errors.append(repr(error));return 1
  return f
 def write(width):
  def f(_,a,value):
   try:script.write(a,width,value);return 0
   except Exception as error:errors.append(repr(error));return 1
  return f
 def call(_,target,args,count,out):
  try:
   assert target in WIDTHS and count==len(WIDTHS[target]);values=list(args[:count])
   if target in SCRIPTED:out[0]=script.call(target,values,out[0]);return 0
   if script.fail_call==target:raise RuntimeError('Injected linked callee failure')
   script.trace.append(['call',target,values,out[0]]);value=c.c_uint32(out[0])
   if target==0x1aa40:status=TEXTURES(c.byref(bus),values[0],0,c.byref(value))
   elif target==0x1ae88:status=RELEASE(c.byref(bus),values[0],out[0],c.byref(value))
   elif target==0x10a6a:status=SELECT(c.byref(bus),values[0],out[0],c.byref(value))
   elif target==0x10968:
    callback=slot.W8(write(1));slotbus=slot.Bus(callback,None);status=SLOT(c.byref(slotbus),*values,c.byref(value))
   else:status=INSERT(c.byref(bus),*values,out[0],c.byref(value))
   if not status:out[0]=value.value
   return status
  except Exception as error:errors.append(repr(error));return 1
 cb=[w.R8(),w.R16(read(2)),w.R32(read(4)),w.W16(write(2)),w.W32(write(4)),w.CALL(call)]
 if missing is not None:cb[missing]=type(cb[missing])()
 bus=w.Bus(*cb,None,64);out=c.c_uint32(0xa55aa55a);status=fn(None if nullbus else c.byref(bus),case['incoming'][0],None if nullout else c.byref(out));return status,out.value,errors
def fixtures():
 snapshot,base=insert.fixtures();rng=random.Random(0x10990);cases=[]
 for i,row in enumerate(base):
  case=json.loads(json.dumps(row));coords=[rng.getrandbits(32)for _ in range(3)];case['initial']+=[[0x400e6,4,0x80000],*[ [0x80000+off,4,value]for off,value in zip([4,8,12],coords)],*[[a,4,rng.getrandbits(32)]for a in [0x403dc,0x40402,0x40406,0x4040a]],*[[a,2,rng.getrandbits(16)]for a in [0x403e0,0x403d8,0x403d0,0x40400,0x49b8c,0x49b8e,0x49b90]]];case['helper_returns']={str(target):rng.getrandbits(32)for target in SCRIPTED};case['helper_effects']={str(0x1aa40):[[0x47b88,4,rng.getrandbits(32)]],str(0x18160):[[0x403dc,4,rng.getrandbits(32)]],str(0x10a6a):[]}
  if i%5==0:case['helper_effects'][str(0x10a6a)]=[[0x400e6,4,0x90000],*[ [0x90000+off,4,rng.getrandbits(32)]for off in [4,8,12]]]
  scene_base=0x3d822+146;tag=[0,1,2,0x8000,0xffff][i%5];asset=[0,1,0xffff,0x8000,0x7fff][(i//5)%5];frame=[0,1,35,0xffff,0x7fff,0x8000,0xfffe,0x1234][(i//25)%8]
  case['initial']+=[[scene_base,2,tag],[scene_base+2,2,asset],[scene_base+0x90,2,rng.getrandbits(16)],[scene_base+0x8e,2,rng.getrandbits(16)]]
  for ptr in [0x80000,0x90000]:case['initial']+=[[ptr+2,2,asset],[ptr+0x90,2,rng.getrandbits(16)],[ptr+0x8e,2,rng.getrandbits(16)]]
  case['helper_returns'][str(0x1ac68)]=(rng.getrandbits(16)<<16)|frame;case['helper_effects']={str(0x18160):[[0x403dc,4,rng.getrandbits(32)]],str(0x1ae88):[[0x400e6,4,0x80000]]if i%2 else[],str(0x1ac68):[[0x400e6,4,0x90000]]if i%3==0 else[]};case.update(selector_tag=tag,selector_frame_word=frame)
  cases.append(case)
 return snapshot,cases
def main():
 global SLOT,INSERT,TEXTURES,SELECT,RELEASE
 ap=argparse.ArgumentParser();ap.add_argument('--original-only',action='store_true');ap.add_argument('--source');ap.add_argument('--release-source');ap.add_argument('--no-publish',action='store_true');opt=ap.parse_args();out=ROOT/'verification/local-scene-initial-setup-release'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);restore=ROOT/'projects/black-ice-white-noise/restoration';release_source=Path(opt.release_source).resolve()if opt.release_source else restore/'biwn_frame_reference_release.c';mapping=json.loads((ROOT/'verification/main_CPU_execution_coverage-current.json').read_text());manifest=json.loads(Path(mapping['static_manifest']).read_text());expected={int(x['address'],16)for x in manifest['instructions']if 0x10990<=int(x['address'],16)<0x10a6a};assert len(expected)==39;hashes={};fn=None
 if not opt.original_only:
  proposal=json.loads((ROOT/'verification/local-scene-initial-setup-author-current.json').read_text());source=Path(opt.source)if opt.source else Path(proposal['directory'])/'biwn_scene_initial_setup.c';sources=[source,restore/'biwn_slot_clear.c',restore/'biwn_scene_record_insert.c',restore/'biwn_resources.c',restore/'biwn_scene_select.c',release_source]
  for name,proof in [('biwn_slot_clear.c','local-slot-clear-checks-current.json'),('biwn_scene_record_insert.c','local-scene-record-insert-checks-current.json')]:assert sha((restore/name).read_bytes())==json.loads((ROOT/'verification'/proof).read_text())['source_sha256']
  assert sha((restore/'biwn_frame_reference_release.c').read_bytes())==json.loads((ROOT/'verification/local-frame-reference-release-checks-current.json').read_text())['source_sha256']
  assert sha((restore/'biwn_scene_select.c').read_bytes())==json.loads((ROOT/'verification/local-scene-select-checks-current.json').read_text())['source_sha256']
  assert sha((restore/'biwn_resources.c').read_bytes())==json.loads((ROOT/'verification/biwn-resources-checks.json').read_text())['source_sha256']['biwn_resources.c']
  # Same restricted source AST gate as the accepted insert routine, but caller-specific ABI/calls.
  inspection=subprocess.run(['clang','-std=c99','-I',str(source.parent),'-I',str(restore),'-fsyntax-only','-Xclang','-ast-dump=json',str(source)],capture_output=True,text=True);(out/'syntax.log').write_text(inspection.stderr);assert inspection.returncode==0,inspection.stderr;tree=json.loads(inspection.stdout);functions=[n for n in tree['inner']if n['kind']=='FunctionDecl'and any(x.get('kind')=='CompoundStmt'for x in n.get('inner',[]))];names={n['name']for n in functions};assert 'biwn_scene_initial_setup'in names and all(n['name']=='biwn_scene_initial_setup'or n.get('storageClass')=='static'for n in functions);assert not any(n['kind']in ['VarDecl','FileScopeAsmDecl']for n in tree['inner'])
  def check(n):
   if not n:return
   assert n['kind']not in ['GCCAsmStmt','MSAsmStmt'];assert n.get('castKind')not in ['IntegralToPointer','PointerToIntegral','BitCast']
   if n['kind']=='CallExpr':
    target=n['inner'][0]
    while target['kind']in ['ImplicitCastExpr','ParenExpr']:target=target['inner'][0]
    assert(target['kind']=='MemberExpr'and target['name']in ['read32','write16','write32','call'])or(target['kind']=='DeclRefExpr'and target['referencedDecl']['name']in names)
   for child in n.get('inner',[]):check(child)
  for f in functions:check(f)
  library=out/'libscene-initial-setup.dylib';build=subprocess.run(['clang','-std=c99','-dynamiclib','-O2','-Wall','-Wextra','-Werror','-I',str(source.parent),'-I',str(restore),*[str(p)for p in sources],'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(build.stdout+build.stderr);assert not build.returncode,build.stderr;lib=c.CDLL(str(library));fn=lib.biwn_scene_initial_setup;fn.argtypes=[c.POINTER(w.Bus),c.c_uint32,c.POINTER(c.c_uint32)];fn.restype=c.c_int;SLOT=lib.biwn_slot_clear;SLOT.argtypes=[c.POINTER(slot.Bus),c.c_uint16,c.c_uint16,c.POINTER(c.c_uint32)];SLOT.restype=c.c_int;INSERT=lib.biwn_scene_record_insert;INSERT.argtypes=[c.POINTER(w.Bus),c.c_uint16,*[c.c_uint32]*4,c.POINTER(c.c_uint32)];INSERT.restype=c.c_int;TEXTURES=lib.biwn_resource_textures;TEXTURES.argtypes=[c.POINTER(w.Bus),c.c_uint16,c.c_uint32,c.POINTER(c.c_uint32)];TEXTURES.restype=c.c_int;SELECT=lib.biwn_scene_select;SELECT.argtypes=[c.POINTER(w.Bus),c.c_uint16,c.c_uint32,c.POINTER(c.c_uint32)];SELECT.restype=c.c_int;RELEASE=lib.biwn_frame_reference_release;RELEASE.argtypes=[c.POINTER(w.Bus),c.c_uint16,c.c_uint32,c.POINTER(c.c_uint32)];RELEASE.restype=c.c_int;hashes={str(p):sha(p.read_bytes())for p in sources}
 snapshot,cases=fixtures();coverage=set();rows=[]
 for i,case in enumerate(cases):
  a=Script(snapshot,case);value=original(a,case,coverage)
  if fn:
   b=Script(snapshot,case);status,actual,errors=translated(fn,b,case)
   if status or errors or value!=actual or a.trace!=b.trace or a.memory!=b.memory:
    (out/'mismatch.json').write_text(json.dumps(dict(case=i,parameters=case,status=status,expected=value,actual=actual,original_trace=a.trace,C_trace=b.trace,errors=errors),indent=2)+'\n');raise AssertionError(out/'mismatch.json')
  rows.append(dict(case=i,index=case['index'],pattern=case['pattern'],full_D0=value,trace_events=len(a.trace),trace_sha256=sha(json.dumps(a.trace).encode()),RAM_sha256=sha(a.memory)))
 assert expected<=coverage and len(coverage)>98,(len(coverage),expected-coverage);guards=[];native=[];core_path=None
 if fn:
  for opts in [dict(missing=2),dict(missing=3),dict(missing=4),dict(missing=5),dict(nullbus=True),dict(nullout=True)]:
   b=Script(snapshot,cases[0]);status,value,errors=translated(fn,b,cases[0],**opts);assert status==1 and value==0xa55aa55a and not b.trace;guards.append(opts)
  for target in WIDTHS:
   b=Script(snapshot,cases[0]);b.fail_call=target;status,value,errors=translated(fn,b,cases[0]);assert status==3 and value==0xa55aa55a;guards.append(dict(failed_helper=hex(target)))
  baseline=Script(snapshot,cases[0]);original(baseline,cases[0],set())
  for i,event in enumerate(baseline.trace):
   if event[0]=='call':continue
   b=Script(snapshot,cases[0]);b.fail=i;status,value,errors=translated(fn,b,cases[0]);assert status in [2,3]and value==0xa55aa55a and b.trace==baseline.trace[:i],(i,status,value,b.trace[-2:]);guards.append(dict(failed_event=i,prior_effects_retained=True))
 if fn:
  core_path=Path(json.loads((ROOT/'verification/DSP-music-context-experimental-candidate.json').read_text())['core_path']);oracle=insert.media.scheduler.Native(diagnostic_core=core_path);runtime=insert.media.Runtime.__new__(insert.media.Runtime);runtime.oracle,runtime.device,runtime.core=oracle,oracle.device,oracle.lib;writers={}
  for width in [2,4]:
   wr=getattr(runtime.core,'m68k_write_memory_'+str(width*8));wr.argtypes=[c.c_uint32,c.c_uint32];wr.restype=None;writers[width]=wr
  try:
   for index in [0,1,14,15,16,32767,0xffff,0xfffe,0xfffd]:
    for pattern in [0,1,4]:
     case=next(row for row in cases if row['index']==index and row['pattern']==pattern);left=Script(snapshot,case);status,value,errors=translated(fn,left,case);assert status==0 and not errors;right=Script(snapshot,case);memory=bytearray(right.memory);memory[SP:SP+4]=STOP.to_bytes(4,'big')
     for target in SCRIPTED:memory[target:target+2]=b'\x4e\x75'
     cpu=insert.media.CPU();cpu.registers[:15]=case['incoming'];cpu.registers[15]=SP;cpu.pc=0x10990;cpu.sr=0x2000;cpu.usp=0x180000;cpu.ssp=SP;runtime.device.seed(bytes(memory),0);runtime.seed_cpu(cpu);steps=0;calls=[]
     while runtime.cpu().pc!=STOP and steps<10000:
      state=runtime.cpu()
      if state.pc in SCRIPTED:
       ram=runtime.device.ram();off=4;args=[]
       for width in WIDTHS[state.pc]:args.append(int.from_bytes(ram[state.registers[15]+off:state.registers[15]+off+width],'big'));off+=width
       target=state.pc;state.registers[0]=right.call(target,args,state.registers[0]);calls.append(target)
       for addr,width,v in right.changed:writers[width](addr,v)
       runtime.seed_cpu(state)
      runtime.core.m68k_execute(1);steps+=1
     actual=runtime.cpu();ram=bytearray(runtime.device.ram())
     for target in SCRIPTED:ram[target:target+2]=left.memory[target:target+2]
     assert actual.pc==STOP and actual.registers[15]==SP+4 and actual.registers[0]==value,(index,pattern,actual.pc,actual.registers[0],value)
     assert ram[:SP-0x1000]==left.memory[:SP-0x1000]and ram[SP+4:]==left.memory[SP+4:]and calls==[e[1]for e in left.trace if e[0]=='call'and e[1]in SCRIPTED]
     native.append(dict(index=index,pattern=pattern,full_D0=value,steps=steps,scripted_calls=[hex(x)for x in calls],external_RAM_match=True))
  finally:oracle.close()
 (out/'fixtures.json').write_text(json.dumps(cases,indent=2)+'\n');(out/'case-results.json').write_text(json.dumps(rows,indent=2)+'\n');report=dict(status='scene_initial_setup_release_original_preflight_pass'if opt.original_only else'local_scene_initial_setup_real_release_selector_textures_clear_insert_original_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(rows),primary_instruction_address_coverage=[39,39],linked_instruction_addresses=len(coverage),texture_mode_checked=3,texture_mode_instruction_addresses=sorted(x for x in coverage if 0x1aa40<=x<0x1aade),source_sha256=hashes,guards=guards,pinned_native_cases=native,core_path=str(core_path)if core_path else None,core_sha256=sha(core_path.read_bytes())if core_path else None,scripted_helpers=[hex(x)for x in SCRIPTED],selector_context_instruction_addresses=sorted(x for x in coverage if 0x10a6a<=x<=0x10ba2),release_context_instruction_addresses=sorted(x for x in coverage if 0x1ae88<=x<=0x1aed8),actual_C_helpers=['1AA40 texture table initialization mode3','10968 slot clear','10A6A selector','1AE88 reference release','11762 record insert'],top_level_scripted_helpers=['0x18160'],nested_selector_scripted_helpers=['0x1ac68'],new_training=False,native_Chat_verified=False,natural_gameplay_integration_verified=False,full_route_runtime_promoted=False,scope='Complete10990..10A68 linked with actual1AA40texturemode3,10968,10A6A,1AE88 and11762 versus originalUnicornM68000 plus27 pinned nativeCPU finalD0/externalRAM cases when C tested: fullD0,logical data/helper order and2MBRAM. Tophelper18160 and nestedselectorresourcehelper1AC68 can change RAM/fullD0; constructor reloads posthelpercoordinates inoriginalz/y/x order. Signed/queued index behavior preserved. PrivateCPUframes,CCR,otherregisters,nativebusdummyreads,physicaltiming and naturalgameplay excluded.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 if not opt.no_publish:(ROOT/'verification'/('local-scene-initial-setup-release-'+('preflight'if opt.original_only else'checks-current')+'.json')).write_text(json.dumps(report,indent=2)+'\n')
 print(report['status'],len(rows),len(coverage),'guards',len(guards),flush=True)
if __name__=='__main__':main()
