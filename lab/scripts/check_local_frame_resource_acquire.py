"""Original173instructioncaller versus local C; explicit loader and guestscratch."""
import argparse,ctypes as c,hashlib,itertools,json,os,random,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_local_global_animation_tick as animation
import check_biwn_media_setup_cpu as media
ROOT=animation.ROOT;SP=animation.SP;STOP=animation.STOP;SCRATCH=SP-8;w=animation.boundary.world;LOADER=0x1b044
sha=lambda b:hashlib.sha256(b).hexdigest()
class Script:
 def __init__(self,snapshot,case,fail=None):
  self.memory=bytearray(snapshot);self.case=case;self.trace=[];self.fail=fail;self.fail_call=False;self.changed=[];self.queues={}
  for a,width,value in case['initial']:self.memory[a:a+width]=value.to_bytes(width,'big')
  for q in case.get('read_queues',[]):self.queues[(q['address'],q['width'])]=list(q['values'])
 def read(self,a,width):
  if self.fail==len(self.trace):raise RuntimeError('Injected read failure')
  q=self.queues.get((a,width));v=q.pop(0)if q else int.from_bytes(self.memory[a:a+width],'big');self.trace.append(['r',a,width,v]);return v
 def write(self,a,width,value):
  if self.fail==len(self.trace):raise RuntimeError('Injected write failure')
  self.memory[a:a+width]=value.to_bytes(width,'big');self.trace.append(['w',a,width,value])
 def call(self,args,incoming):
  if self.fail_call or self.fail==len(self.trace):raise RuntimeError('Injected loader failure')
  self.trace.append(['call',LOADER,args,incoming]);self.changed=[];assert args[2]==SCRATCH and len(args)==5
  for a,width,value in self.case.get('loader_effects',[]):self.memory[a:a+width]=value.to_bytes(width,'big');self.changed.append([a,width,value])
  return self.case['loader_return']
def original(script,case,coverage):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(script.memory));cpu.mem_write(SP,STOP.to_bytes(4,'big')+case['id_word'].to_bytes(2,'big'));cpu.mem_write(LOADER,b'\x4e\x75')
 for reg,value in zip(animation.boundary.REGS,case['incoming']):cpu.reg_write(reg,value)
 cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP)
 def code(e,a,width,_):
  script.last_PC=a
  if a==LOADER:
   sp=e.reg_read(UC_M68K_REG_A7);args=[int.from_bytes(e.mem_read(sp+4+i*4,4),'big')for i in range(5)];value=script.call(args,e.reg_read(UC_M68K_REG_D0))
   for addr,size,v in script.changed:e.mem_write(addr,v.to_bytes(size,'big'))
   e.reg_write(UC_M68K_REG_D0,value);return
  assert 0x1ac68<=a<=0x1ae54,hex(a);coverage.add(a)
 def private(a):return SP-0x1000<=a<SP+6 and not SCRATCH<=a<SCRATCH+4
 def read(e,t,a,width,value,_):
  if private(a):return
  e.mem_write(a,script.read(a,width).to_bytes(width,'big'))
 def write(e,t,a,width,value,_):
  if private(a):return
  script.write(a,width,value&((1<<(8*width))-1))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(0x1ac68,STOP,count=20000,timeout=2000000);assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
 memory=bytearray(cpu.mem_read(0,0x200000));memory[LOADER:LOADER+2]=script.memory[LOADER:LOADER+2]
 for q in case.get('read_queues',[]):a=q['address'];memory[a:a+q['width']]=script.memory[a:a+q['width']]
 assert memory[:SP-0x1000]==script.memory[:SP-0x1000]and memory[SP+6:]==script.memory[SP+6:]and memory[SCRATCH:SCRATCH+4]==script.memory[SCRATCH:SCRATCH+4];return cpu.reg_read(UC_M68K_REG_D0)
def translated(fn,script,case,limit=500,missing=None,nullbus=False,nullout=False,scratch=SCRATCH):
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
  try:assert target==LOADER and count==5;out[0]=script.call(list(args[:count]),out[0]);return 0
  except Exception as error:errors.append(repr(error));return 1
 cb=[w.R8(),w.R16(read(2)),w.R32(read(4)),w.W16(write(2)),w.W32(write(4)),w.CALL(call)]
 if missing is not None:cb[missing]=type(cb[missing])()
 bus=w.Bus(*cb,None,limit);out=c.c_uint32(0xa55aa55a);status=fn(None if nullbus else c.byref(bus),case['id_word'],scratch,None if nullout else c.byref(out));return status,out.value,errors
def fixtures():
 snapshot=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();rng=random.Random(0x1ac68);cases=[]
 def make(mode,count,reserved,pattern,adjusted):
  bias=mode*100 if 1<=mode<=3 else 100;id_word=(bias+adjusted)&65535;initial=[[0x15b530,2,mode],[0x15b532,2,reserved],[SCRATCH,4,rng.getrandbits(32)]]
  for m in [1,2,3]:initial+=[[0x464c8+m*2,2,m*100],[0x464a0+m*2,2,count],[0x464a8+m*4,4,0x10000+m*0x1000],[0x464b8+m*4,4,0x414e3030+m*16]]
  for i in range(36):
   stored=(id_word+(i-reserved))&65535 if pattern==0 and i>=reserved else(0xffff if pattern==1 else 0x4000+i);refs=0 if pattern in [1,2]else 2;initial+=[[0x15b4a0+i*4,2,stored],[0x15b4a2+i*4,2,refs],[0x4674c+i*8,4,0x1134a0+i*8192]]
  return dict(mode_word=mode,count_word=count,reserved_word=reserved,pattern=pattern,adjusted_word=adjusted,id_word=id_word,initial=initial,incoming=[rng.getrandbits(32)for _ in animation.boundary.REGS],loader_return=rng.getrandbits(32),loader_effects=[[SCRATCH,4,rng.getrandbits(32)],[0x15b532,2,31]])
 for mode,count,reserved,pattern in itertools.product([1,2,3],[1,2,3,4,36],[0,1,15,34,35,36],range(4)):
  adjusted=[0,1,31,0x7fff,0x8000][len(cases)%5];cases.append(make(mode,count,reserved,pattern,adjusted))
 for mode in [0,4,0x7fff,0x8000,0xffff]:cases.append(make(mode,2,0,1,1))
 for adjusted in [0,1,0x7fff]:cases.append(make(3,0,0,0,adjusted))
 # Negative group: firstsearch skipped,queuedsecondindex0 permitsloader; fill skipped.
 neg=make(3,0xffff,40,1,3);neg['read_queues']=[dict(address=0x15b532,width=2,values=[40,0])];cases.append(neg)
 # Existingsearch must use initialindex; empty/eviction phases reread separately.
 q=make(2,2,0,1,7);q['read_queues']=[dict(address=0x15b532,width=2,values=[0,4])];cases.append(q)
 return snapshot,cases
def bind(source,out):
 restore=ROOT/'projects/black-ice-white-noise/restoration';result=subprocess.run(['clang','-std=c99','-I',str(source.parent),'-I',str(restore),'-fsyntax-only','-Xclang','-ast-dump=json',str(source)],capture_output=True,text=True);(out/'syntax.log').write_text(result.stderr);assert not result.returncode,result.stderr;tree=json.loads(result.stdout);functions=[n for n in tree['inner']if n['kind']=='FunctionDecl'and any(x.get('kind')=='CompoundStmt'for x in n.get('inner',[]))];names={n['name']for n in functions};assert 'biwn_frame_resource_acquire'in names and all(n['name']=='biwn_frame_resource_acquire'or n.get('storageClass')=='static'for n in functions);assert not any(n['kind']in ['VarDecl','FileScopeAsmDecl']for n in tree['inner'])
 def check(n):
  if not n:return
  assert n['kind']not in ['GCCAsmStmt','MSAsmStmt'];assert n.get('castKind')not in ['IntegralToPointer','PointerToIntegral','BitCast'],dict(forbidden_pointer_conversion=n.get('castKind'),source_range=n.get('range'),expression_type=n.get('type'))
  if n['kind']=='CallExpr':
   target=n['inner'][0]
   while target['kind']in ['ImplicitCastExpr','ParenExpr']:target=target['inner'][0]
   assert(target['kind']=='MemberExpr'and target['name']in ['read16','read32','write16','write32','call'])or(target['kind']=='DeclRefExpr'and target['referencedDecl']['name']in names)
  for child in n.get('inner',[]):check(child)
 for f in functions:check(f)
 library=out/'libframe-resource-acquire.dylib';built=subprocess.run(['clang','-std=c99','-dynamiclib','-O2','-Wall','-Wextra','-Werror','-I',str(source.parent),'-I',str(restore),str(source),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(built.stdout+built.stderr);assert not built.returncode,built.stderr;fn=c.CDLL(str(library)).biwn_frame_resource_acquire;fn.argtypes=[c.POINTER(w.Bus),c.c_uint16,c.c_uint32,c.POINTER(c.c_uint32)];fn.restype=c.c_int;return fn
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--original-only',action='store_true');ap.add_argument('--source');ap.add_argument('--no-publish',action='store_true');opt=ap.parse_args();out=ROOT/'verification/local-frame-resource-acquire'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);fn=None;source=None
 if not opt.original_only:source=Path(opt.source)if opt.source else Path(json.loads((ROOT/'verification/local-frame-resource-acquire-author-current.json').read_text())['directory'])/'biwn_frame_resource_acquire.c';fn=bind(source,out)
 snapshot,cases=fixtures();coverage=set();rows=[]
 for i,case in enumerate(cases):
  a=Script(snapshot,case);value=original(a,case,coverage)
  if fn:
   b=Script(snapshot,case);status,actual,errors=translated(fn,b,case)
   if status or errors or value!=actual or a.trace!=b.trace or a.memory!=b.memory:
    (out/'mismatch.json').write_text(json.dumps(dict(case=i,parameters=case,status=status,expected=value,actual=actual,original_trace=a.trace,C_trace=b.trace,errors=errors),indent=2)+'\n');raise AssertionError(out/'mismatch.json')
  rows.append(dict(case=i,mode_word=case['mode_word'],count_word=case['count_word'],reserved_word=case['reserved_word'],pattern=case['pattern'],adjusted_word=case['adjusted_word'],full_D0=value,loader_calls=sum(x[0]=='call'for x in a.trace),trace_events=len(a.trace),trace_sha256=sha(json.dumps(a.trace).encode()),RAM_sha256=sha(a.memory)))
 evidence=json.loads((ROOT/'verification/frame-resource-acquire-evidence-current.json').read_text());expected={int(x,16)for x in re.findall(r'^([0-9a-fA-F]+):',json.loads((Path(evidence['directory'])/'evidence.json').read_text())['assembly'],re.M)};assert len(expected)==173 and expected<=coverage,(expected-coverage,coverage-expected)
 guards=[];native=[];core_path=None
 if fn:
  for opts in [dict(missing=i)for i in [1,2,3,4,5]]+[dict(nullbus=True),dict(nullout=True),dict(scratch=0)]:
   b=Script(snapshot,cases[0]);status,value,errors=translated(fn,b,cases[0],**opts);assert status==1 and value==0xa55aa55a and not b.trace;guards.append(opts)
  selected=next(x for x in cases if x['mode_word']==3 and x['count_word']==2 and x['reserved_word']==0 and x['pattern']==1 and x['adjusted_word']<32768);left=Script(snapshot,selected);original(left,selected,set())
  for i,event in enumerate(left.trace):
   b=Script(snapshot,selected,fail=i);status,value,errors=translated(fn,b,selected);assert status==(3 if event[0]=='call'else 2)and value==0xa55aa55a and b.trace==left.trace[:i],(i,event,status,value);guards.append(dict(failed_event=i,kind=event[0],prior_effects_retained=True))
  for limit in [0,1,3]:
   b=Script(snapshot,selected);status,value,errors=translated(fn,b,selected,limit=limit);assert status==4 and value==0xa55aa55a;guards.append(dict(work_limit=limit,output_unchanged=True))
  zero=json.loads(json.dumps(selected));zero['initial']+=[[0x464a0+6,2,0],[0x15b532,2,40]];zero.update(count_word=0,reserved_word=40);b=Script(snapshot,zero);status,value,errors=translated(fn,b,zero);assert status==5 and value==0xa55aa55a;guards.append(dict(dividezero_status=5,output_unchanged=True,original_exception_execution_not_modeled=True))
  core_path=Path(json.loads((ROOT/'verification/DSP-music-context-experimental-candidate.json').read_text())['core_path']);oracle=media.scheduler.Native(diagnostic_core=core_path);runtime=media.Runtime.__new__(media.Runtime);runtime.oracle,runtime.device,runtime.core=oracle,oracle.device,oracle.lib;writers={}
  for width in [2,4]:
   wr=getattr(runtime.core,'m68k_write_memory_'+str(width*8));wr.argtypes=[c.c_uint32,c.c_uint32];wr.restype=None;writers[width]=wr
  try:
   chosen=[x for x in cases if x['mode_word']==3 and x['count_word']in [1,2,3,36]and x['reserved_word']in [0,15]and x['adjusted_word']<32768 and not x.get('read_queues')]
   for case in chosen:
    left=Script(snapshot,case);status,value,errors=translated(fn,left,case);right=Script(snapshot,case);memory=bytearray(right.memory);memory[SP:SP+6]=STOP.to_bytes(4,'big')+case['id_word'].to_bytes(2,'big');memory[LOADER:LOADER+2]=b'\x4e\x75';cpu=media.CPU();cpu.registers[:15]=case['incoming'];cpu.registers[15]=SP;cpu.pc=0x1ac68;cpu.sr=0x2000;cpu.usp=0x180000;cpu.ssp=SP;runtime.device.seed(bytes(memory),0);runtime.seed_cpu(cpu);steps=0;calls=[]
    while runtime.cpu().pc!=STOP and steps<20000:
     state=runtime.cpu()
     if state.pc==LOADER:
      ram=runtime.device.ram();sp=state.registers[15];args=[int.from_bytes(ram[sp+4+n*4:sp+8+n*4],'big')for n in range(5)];calls.append(args);state.registers[0]=right.call(args,state.registers[0])
      for addr,width,v in right.changed:writers[width](addr,v)
      runtime.seed_cpu(state)
     runtime.core.m68k_execute(1);steps+=1
    state=runtime.cpu();ram=bytearray(runtime.device.ram());ram[LOADER:LOADER+2]=left.memory[LOADER:LOADER+2];wanted=[e[2]for e in left.trace if e[0]=='call'];assert not status and not errors and state.pc==STOP and state.registers[15]==SP+4 and state.registers[0]==value and calls==wanted
    assert ram[:SP-0x1000]==left.memory[:SP-0x1000]and ram[SP+6:]==left.memory[SP+6:]and ram[SCRATCH:SCRATCH+4]==left.memory[SCRATCH:SCRATCH+4];native.append(dict(mode_word=case['mode_word'],count_word=case['count_word'],reserved_word=case['reserved_word'],pattern=case['pattern'],adjusted_word=case['adjusted_word'],full_D0=value,steps=steps,loader_calls=calls))
  finally:oracle.close()
 (out/'fixtures.json').write_text(json.dumps(cases,indent=2)+'\n');(out/'case-results.json').write_text(json.dumps(rows,indent=2)+'\n');report=dict(status='frame_resource_acquire_original_preflight_pass'if opt.original_only else'local_frame_resource_acquire_original_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(rows),instruction_address_coverage=[173,173],source=str(source)if source else None,source_sha256=sha(source.read_bytes())if source else None,loader_calls=sum(x['loader_calls']for x in rows),host_guards=guards,pinned_native_cases=native,core_path=str(core_path)if core_path else None,core_sha256=sha(core_path.read_bytes())if core_path else None,new_training=False,native_Chat_verified=False,pinned_native_CPU_verified=bool(fn),host_guards_verified=bool(fn),natural_gameplay_integration_verified=False,full_route_runtime_promoted=False,scope='Complete1AC68..1AE54 fullD0,logicalorderedreads/writes/loaderargs andmodeled2MBRAM plus4bytesguestscratch versus originalUnicornM68000. Existing/free/eviction/failure,invalidmode/negativeadjusted,count0existinghit,negativecountwithqueuedindex andReservedIndexreread covered. 1B044 loader is RAM/D0fixture. Privateframesotherthanscratch,CCR/otherregs,originalDIVSzeroexception,hostlimitmapping/nativeCPU/hardware/gameplay remain separatelyunverified.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');
 if not opt.no_publish:(ROOT/'verification'/('local-frame-resource-acquire-'+('preflight'if opt.original_only else'checks-current')+'.json')).write_text(json.dumps(report,indent=2)+'\n');
 print(report['status'],len(rows),len(coverage),'loadercalls',report['loader_calls'],flush=True)
if __name__=='__main__':main()
