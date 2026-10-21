"""Complete10A6A selector versus originalCPU; two resource helpers are explicit."""
import argparse,ctypes as c,hashlib,itertools,json,os,random,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_local_global_animation_tick as animation
import check_biwn_media_setup_cpu as media
ROOT=animation.ROOT;SP=animation.SP;STOP=animation.STOP;w=animation.boundary.world;HELPERS=[0x1ae88,0x1ac68]
sha=lambda b:hashlib.sha256(b).hexdigest()
class Script:
 def __init__(self,snapshot,case,fail=None):
  self.memory=bytearray(snapshot);self.case=case;self.trace=[];self.fail=fail;self.fail_call=None;self.changed=[];self.queues={}
  for a,width,value in case['initial']:self.memory[a:a+width]=value.to_bytes(width,'big')
  for q in case.get('read_queues',[]):self.queues[(q['address'],q['width'])]=list(q['values'])
 def read(self,a,width):
  if self.fail==len(self.trace):raise RuntimeError('Injected read failure')
  values=self.queues.get((a,width));value=values.pop(0)if values else int.from_bytes(self.memory[a:a+width],'big');self.trace.append(['r',a,width,value]);return value
 def write(self,a,width,value):
  if self.fail==len(self.trace):raise RuntimeError('Injected write failure')
  self.memory[a:a+width]=value.to_bytes(width,'big');self.trace.append(['w',a,width,value])
 def call(self,target,args,incoming):
  if self.fail_call==target or self.fail==len(self.trace):raise RuntimeError('Injected helper failure')
  self.trace.append(['call',target,args,incoming]);self.changed=[]
  for a,width,value in self.case.get('helper_effects',{}).get(str(target),[]):self.memory[a:a+width]=value.to_bytes(width,'big');self.changed.append([a,width,value])
  return self.case['helper_returns'][str(target)]
def original(script,case,coverage):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(script.memory));cpu.mem_write(SP,STOP.to_bytes(4,'big')+case['id_word'].to_bytes(2,'big'))
 for reg,value in zip(animation.boundary.REGS,case['incoming']):cpu.reg_write(reg,value)
 cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP)
 for target in HELPERS:cpu.mem_write(target,b'\x4e\x75')
 def code(e,a,width,_):
  if a in HELPERS:
   sp=e.reg_read(UC_M68K_REG_A7);args=[int.from_bytes(e.mem_read(sp+4,2),'big')];value=script.call(a,args,e.reg_read(UC_M68K_REG_D0))
   for addr,size,v in script.changed:e.mem_write(addr,v.to_bytes(size,'big'))
   e.reg_write(UC_M68K_REG_D0,value);return
  assert 0x10a6a<=a<=0x10ba2,hex(a);coverage.add(a)
 def read(e,t,a,width,value,_):
  if SP-0x1000<=a<SP+6:return
  e.mem_write(a,script.read(a,width).to_bytes(width,'big'))
 def write(e,t,a,width,value,_):
  if SP-0x1000<=a<SP+6:return
  script.write(a,width,value&((1<<(8*width))-1))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(0x10a6a,STOP,count=1000,timeout=1000000);assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
 memory=bytearray(cpu.mem_read(0,0x200000))
 for target in HELPERS:memory[target:target+2]=script.memory[target:target+2]
 for q in case.get('read_queues',[]):a=q['address'];memory[a:a+q['width']]=script.memory[a:a+q['width']]
 assert memory[:SP-0x1000]==script.memory[:SP-0x1000]and memory[SP+6:]==script.memory[SP+6:];return cpu.reg_read(UC_M68K_REG_D0)
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
  try:assert target in HELPERS and count==1;out[0]=script.call(target,list(args[:count]),out[0]);return 0
  except Exception as error:errors.append(repr(error));return 1
 cb=[w.R8(),w.R16(read(2)),w.R32(read(4)),w.W16(write(2)),w.W32(write(4)),w.CALL(call)]
 if missing is not None:cb[missing]=type(cb[missing])()
 bus=w.Bus(*cb,None,64);out=c.c_uint32(0xa55aa55a);status=fn(None if nullbus else c.byref(bus),case['id_word'],case['incoming'][0],None if nullout else c.byref(out));return status,out.value,errors
def fixtures():
 snapshot=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();rng=random.Random(0x10a6a);cases=[]
 for id_word,tag,frame in itertools.product([0,1,2,255,1024,0xffff],[0,1,2,0x8000,0xffff],[0,1,35,0xffff,0x7fff,0x8000,0xfffe,0x1234]):
  i=len(cases);base=0x3d822+id_word*146;asset_word=[0,1,0xffff,0x8000,0x7fff][i%5];initial=[[a,2,rng.getrandbits(16)]for a in [0x403d6,0x403ca,0x403d8,0x403da,0x403d0,0x403d4,0x403d2]]+[[0x23f88,4,rng.getrandbits(32)],[0x400e6,4,0x80000]]
  if id_word!=0xffff:initial+=[[base,2,tag],[base+2,2,asset_word],[base+0x90,2,rng.getrandbits(16)],[base+0x8e,2,rng.getrandbits(16)]]
  for ptr in [0x80000,0x90000]:initial+=[[ptr+2,2,asset_word],[ptr+0x90,2,rng.getrandbits(16)],[ptr+0x8e,2,rng.getrandbits(16)]]
  for offset in [0,4,8,12]:word=(frame+offset)&65535;signed=word if word<32768 else word-65536;initial.append([0x4674c+signed*8,4,rng.getrandbits(32)])
  effects={str(0x1ae88):[[0x400e6,4,0x80000]]if i%2 else[],str(0x1ac68):[[0x400e6,4,0x90000]]if i%3==0 else[]};returns={str(0x1ae88):rng.getrandbits(32),str(0x1ac68):(rng.getrandbits(16)<<16)|frame};cases.append(dict(id_word=id_word,tag=tag,frame_word=frame,initial=initial,incoming=[rng.getrandbits(32)for _ in animation.boundary.REGS],helper_returns=returns,helper_effects=effects))
 base=json.loads(json.dumps(next(x for x in cases if x['id_word']==1 and x['tag']==0 and x['frame_word']==0)))
 for queues in [[dict(address=0x403da,width=2,values=[0xffff])],[dict(address=0x403da,width=2,values=[2,3,4,5,6])],[dict(address=0x4674c+4*8,width=4,values=[0x12345678,0x87654321])]]:
  case=json.loads(json.dumps(base));case['read_queues']=queues
  for index in [2,3,8,13,18]:case['initial'].append([0x4674c+index*8,4,rng.getrandbits(32)])
  cases.append(case)
 return snapshot,cases
def bind(source,out):
 restore=ROOT/'projects/black-ice-white-noise/restoration';process=subprocess.run(['clang','-std=c99','-I',str(source.parent),'-I',str(restore),'-fsyntax-only','-Xclang','-ast-dump=json',str(source)],capture_output=True,text=True);(out/'syntax.log').write_text(process.stderr);assert process.returncode==0,process.stderr;tree=json.loads(process.stdout);functions=[n for n in tree['inner']if n['kind']=='FunctionDecl'and any(x.get('kind')=='CompoundStmt'for x in n.get('inner',[]))];names={n['name']for n in functions};assert 'biwn_scene_select'in names and all(n['name']=='biwn_scene_select'or n.get('storageClass')=='static'for n in functions);assert not any(n['kind']in ['VarDecl','FileScopeAsmDecl']for n in tree['inner'])
 def check(n):
  if not n:return
  assert n['kind']not in ['GCCAsmStmt','MSAsmStmt'];assert n.get('castKind')not in ['IntegralToPointer','PointerToIntegral','BitCast'],dict(forbidden_pointer_conversion=n.get('castKind'),source_range=n.get('range'),expression_type=n.get('type'))
  if n['kind']=='CallExpr':
   target=n['inner'][0]
   while target['kind']in ['ImplicitCastExpr','ParenExpr']:target=target['inner'][0]
   assert(target['kind']=='MemberExpr'and target['name']in ['read16','read32','write16','write32','call'])or(target['kind']=='DeclRefExpr'and target['referencedDecl']['name']in names)
  for child in n.get('inner',[]):check(child)
 for f in functions:check(f)
 library=out/'libscene-select.dylib';built=subprocess.run(['clang','-std=c99','-dynamiclib','-O2','-Wall','-Wextra','-Werror','-I',str(source.parent),'-I',str(restore),str(source),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(built.stdout+built.stderr);assert not built.returncode,built.stderr;fn=c.CDLL(str(library)).biwn_scene_select;fn.argtypes=[c.POINTER(w.Bus),c.c_uint16,c.c_uint32,c.POINTER(c.c_uint32)];fn.restype=c.c_int;return fn
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--original-only',action='store_true');ap.add_argument('--source');ap.add_argument('--no-publish',action='store_true');opt=ap.parse_args();out=ROOT/'verification/local-scene-select'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);fn=None;source=None
 if not opt.original_only:source=Path(opt.source)if opt.source else Path(json.loads((ROOT/'verification/local-scene-select-author-current.json').read_text())['directory'])/'biwn_scene_select.c';fn=bind(source,out)
 snapshot,cases=fixtures();coverage=set();rows=[]
 for i,case in enumerate(cases):
  a=Script(snapshot,case);value=original(a,case,coverage)
  if fn:
   b=Script(snapshot,case);status,actual,errors=translated(fn,b,case)
   if status or errors or actual!=value or a.trace!=b.trace or a.memory!=b.memory:
    (out/'mismatch.json').write_text(json.dumps(dict(case=i,parameters=case,status=status,expected=value,actual=actual,original_trace=a.trace,C_trace=b.trace,errors=errors),indent=2)+'\n');raise AssertionError(out/'mismatch.json')
  rows.append(dict(case=i,id_word=case['id_word'],tag=case['tag'],frame_word=case['frame_word'],full_D0=value,trace_events=len(a.trace),trace_sha256=sha(json.dumps(a.trace).encode()),RAM_sha256=sha(a.memory)))
 evidence=json.loads((ROOT/'verification/scene-selector-evidence-current.json').read_text());expected={int(x,16)for x in re.findall(r'^([0-9a-fA-F]+):',json.loads((Path(evidence['directory'])/'evidence.json').read_text())['assembly'],re.M)};assert len(expected)==65 and coverage==expected,(expected-coverage,coverage-expected);guards=[];native=[];core_path=None
 if fn:
  for opts in [dict(missing=i)for i in [1,2,3,4,5]]+[dict(nullbus=True),dict(nullout=True)]:
   b=Script(snapshot,cases[0]);status,value,errors=translated(fn,b,cases[0],**opts);assert status==1 and value==0xa55aa55a and not b.trace;guards.append(opts)
  case=next(x for x in cases if x['id_word']==1 and x['tag']==0 and x['frame_word']==0);a=Script(snapshot,case);original(a,case,set())
  for i,event in enumerate(a.trace):
   b=Script(snapshot,case,fail=i);status,value,errors=translated(fn,b,case);assert status==(3 if event[0]=='call'else 2)and value==0xa55aa55a and b.trace==a.trace[:i],(i,event,status,value);guards.append(dict(failed_event=i,kind=event[0],prior_effects_retained=True))
  core_path=Path(json.loads((ROOT/'verification/DSP-music-context-experimental-candidate.json').read_text())['core_path']);oracle=media.scheduler.Native(diagnostic_core=core_path);runtime=media.Runtime.__new__(media.Runtime);runtime.oracle,runtime.device,runtime.core=oracle,oracle.device,oracle.lib;writers={}
  for width in [2,4]:
   wr=getattr(runtime.core,'m68k_write_memory_'+str(width*8));wr.argtypes=[c.c_uint32,c.c_uint32];wr.restype=None;writers[width]=wr
  try:
   chosen=[x for x in cases if x['id_word']in [0,1,0xffff]and x['tag']in [0,1,2]and x['frame_word']in [0,0xffff,0x7fff,0x8000]and not x.get('read_queues')]
   for case in chosen:
    left=Script(snapshot,case);status,value,errors=translated(fn,left,case);right=Script(snapshot,case);memory=bytearray(right.memory);memory[SP:SP+6]=STOP.to_bytes(4,'big')+case['id_word'].to_bytes(2,'big')
    for target in HELPERS:memory[target:target+2]=b'\x4e\x75'
    cpu=media.CPU();cpu.registers[:15]=case['incoming'];cpu.registers[15]=SP;cpu.pc=0x10a6a;cpu.sr=0x2000;cpu.usp=0x180000;cpu.ssp=SP;runtime.device.seed(bytes(memory),0);runtime.seed_cpu(cpu);steps=0
    while runtime.cpu().pc!=STOP and steps<1000:
     state=runtime.cpu()
     if state.pc in HELPERS:
      ram=runtime.device.ram();args=[int.from_bytes(ram[state.registers[15]+4:state.registers[15]+6],'big')];state.registers[0]=right.call(state.pc,args,state.registers[0])
      for a,width,v in right.changed:writers[width](a,v)
      runtime.seed_cpu(state)
     runtime.core.m68k_execute(1);steps+=1
    actual=runtime.cpu();ram=bytearray(runtime.device.ram())
    for target in HELPERS:ram[target:target+2]=left.memory[target:target+2]
    assert not status and not errors and actual.pc==STOP and actual.registers[15]==SP+4 and actual.registers[0]==value and ram[:SP-0x1000]==left.memory[:SP-0x1000]and ram[SP+6:]==left.memory[SP+6:]
    native.append(dict(id_word=case['id_word'],tag=case['tag'],frame_word=case['frame_word'],full_D0=value,steps=steps))
  finally:oracle.close()
 (out/'fixtures.json').write_text(json.dumps(cases,indent=2)+'\n');(out/'case-results.json').write_text(json.dumps(rows,indent=2)+'\n');report=dict(status='scene_select_original_preflight_pass'if opt.original_only else'local_scene_select_original_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),source=str(source)if source else None,source_sha256=sha(source.read_bytes())if source else None,cases=len(rows),instruction_address_coverage=[65,65],guards=guards,pinned_native_cases=native,core_path=str(core_path)if core_path else None,core_sha256=sha(core_path.read_bytes())if core_path else None,remaining_scripted_helpers=[hex(x)for x in HELPERS],new_training=False,native_Chat_verified=False,natural_gameplay_integration_verified=False,full_route_runtime_promoted=False,scope='Complete10A6A..10BA2 fullD0,logicalordereddata/helpertrace and2MBRAM against originalUnicornM68000,plus selected pinnednativeCPU finalD0/externalRAM. ID sentinel,unsigned tags,signed frameword/addwrap/highD0 and queued repeatedreads checked. Resourcehelpers1AE88/1AC68 remain explicit RAM/D0fixtures. Queued-read writes into oracleRAM are normalized only atdeclared queuedranges; authoritative logicalRAM is the modeled bus. Privateframes/CCR/otherregs,nativebusdummyreads,unmapped exceptions,physicaltiming and naturalgameplay excluded.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');
 if not opt.no_publish:(ROOT/'verification'/('local-scene-select-'+('preflight'if opt.original_only else'checks-current')+'.json')).write_text(json.dumps(report,indent=2)+'\n');
 print(report['status'],len(rows),len(coverage),'native',len(native),'guards',len(guards),flush=True)
if __name__=='__main__':main()
