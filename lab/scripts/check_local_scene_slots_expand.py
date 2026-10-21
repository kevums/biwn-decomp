"""Original complete 1142E caller with an explicit logical E26C service fixture."""
import ctypes as c,hashlib,itertools,json,os,random,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_local_global_animation_tick as animation
import check_biwn_media_setup_cpu as media
ROOT=animation.ROOT;SP=animation.SP;STOP=animation.STOP;w=animation.boundary.world
class Seed(c.Structure):_fields_=[(n,c.c_uint32)for n in ['D0','D4','D5','D6']]
class Script:
 def __init__(self,snapshot,case,fail=None):
  self.memory=bytearray(snapshot);self.trace=[];self.fail=fail;self.calls=0;self.changed=[];self.fail_call=False
  for a,width,value in case['initial']:self.memory[a:a+width]=value.to_bytes(width,'big')
 def read(self,a,width):
  if self.fail==len(self.trace):raise RuntimeError('Injected bus failure')
  value=int.from_bytes(self.memory[a:a+width],'big');self.trace.append(['r',a,width,value]);return value
 def write(self,a,width,value):
  if self.fail==len(self.trace):raise RuntimeError('Injected bus failure')
  self.memory[a:a+width]=value.to_bytes(width,'big');self.trace.append(['w',a,width,value])
 def call(self,args,incoming):
  if self.fail_call:raise RuntimeError('Injected GPU-service fixture failure')
  self.trace.append(['call',0xe26c,args,incoming]);self.changed=[]
  for a,width,value in self.case.get('helper_effects',{}).get(str(self.calls),[]):
   self.memory[a:a+width]=value.to_bytes(width,'big');self.changed.append((a,width,value))
  self.calls+=1;return incoming
 def set_case(self,case):self.case=case;return self

def original(script,case,coverage):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(script.memory));cpu.mem_write(SP,STOP.to_bytes(4,'big'));cpu.mem_write(0xe26c,b'\x4e\x75')
 for reg,value in zip(animation.boundary.REGS,case['incoming']):cpu.reg_write(reg,value)
 cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP)
 def code(e,a,width,_):
  if a==0xe26c:
   sp=e.reg_read(UC_M68K_REG_A7);args=[int.from_bytes(e.mem_read(sp+offset,width),'big')for offset,width in [(4,4),(8,4),(12,4),(16,4),(20,2)]]
   value=script.call(args,e.reg_read(UC_M68K_REG_D0))
   for address,width,value in script.changed:e.mem_write(address,value.to_bytes(width,'big'))
   return
  assert 0x1142e<=a<=0x11760,hex(a);coverage.add(a)
 def read(e,t,a,width,value,_):
  if SP-64<=a<SP+4 or 0x114c0<=a<0x114cc:return
  e.mem_write(a,script.read(a,width).to_bytes(width,'big'))
 def write(e,t,a,width,value,_):
  if SP-64<=a<SP+4:return
  script.write(a,width,value&((1<<(width*8))-1))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(0x1142e,STOP,count=5000,timeout=1000000)
 assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
 ram=bytearray(cpu.mem_read(0,0x200000));ram[0xe26c:0xe26e]=script.memory[0xe26c:0xe26e]
 assert ram[:SP-64]==script.memory[:SP-64]and ram[SP+4:]==script.memory[SP+4:]
 return cpu.reg_read(UC_M68K_REG_D0)

def translated(fn,script,case,missing=None,nullbus=False,nullseed=False,nullout=False,limit=8):
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
   assert target==0xe26c and count==5;out[0]=script.call(list(args[:count]),out[0]);return 0
  except Exception as error:errors.append(repr(error));return 1
 cb=[w.R8(),w.R16(read(2)),w.R32(read(4)),w.W16(write(2)),w.W32(write(4)),w.CALL(call)]
 if missing is not None:cb[missing]=type(cb[missing])()
 bus=w.Bus(*cb,None,limit);seed=Seed(*[case['incoming'][i]for i in [0,4,5,6]]);out=c.c_uint32(0xa55aa55a)
 status=fn(None if nullbus else c.byref(bus),None if nullseed else c.byref(seed),None if nullout else c.byref(out));return status,out.value,errors

def fixtures():
 snapshot=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();rng=random.Random(0x1142e);cases=[]
 for face,count,pattern in itertools.product([0,1,2,3,4,5,6,0xffff],[0,1,2,3],range(5)):
  index=8;initial=[[0x400e6,4,0x80000],[0x80000,2,index],[0x80088,2,count],[0x49b88,4,0]]
  values=[0,0xffffffff,0x7fffffff,0x80000000,0xdeadbeef];initial+=[[0x400c4+(index<<5)+off,4,values[(pattern+n)%5]]for n,off in enumerate([4,8,12,16,20,24])]
  for a in range(0x3d6ca,0x3d75a,4):initial.append([a,4,rng.getrandbits(32)])
  initial+=[[0x3d75a+n*2,2,rng.getrandbits(16)]for n in range(12)]
  initial+=[[a,2,rng.getrandbits(16)]for a in [0x49b8c,0x49b8e,0x49b90]]
  for n in range(count):
   initial+=[[0x80010+n*20,2,face],[0x80014+n*20,2,(n+pattern)%8],[0x3d772+((n+pattern)%8)*8,4,rng.getrandbits(32)]]
  cases.append(dict(initial=initial,incoming=[rng.getrandbits(32)for _ in animation.boundary.REGS],face=face,count=count,pattern=pattern))
 # Exercise saved coordinates across valid -> invalid face transitions.
 for faces in [[0,7],[4,0xffff],[5,1,7],[7,0,7]]:
  case=json.loads(json.dumps(next(x for x in cases if x['count']==len(faces)and x['face']==0)))
  for n,face in enumerate(faces):case['initial'].append([0x80010+n*20,2,face])
  cases.append(case)
 # Explicit helper RAM mutations verify post-call counter and pointer rereads.
 for effects in [{'0':[[0x49b88,4,3]]},{'0':[[0x400e6,4,0x90000],[0x90088,2,1],[0x90014,2,0]]}]:
  case=json.loads(json.dumps(next(x for x in cases if x['count']==1 and x['face']==2)));case['helper_effects']=effects;cases.append(case)
 return snapshot,cases

def preflight():
 snapshot,cases=fixtures();coverage=set();counts=[]
 for case in cases:
  script=Script(snapshot,case).set_case(case);value=original(script,case,coverage);counts.append(dict(calls=script.calls,D0=value))
 proposal=json.loads((ROOT/'verification/local-scene-slots-expand-author-current.json').read_text())if(ROOT/'verification/local-scene-slots-expand-author-current.json').exists()else None
 out=Path(proposal['directory'])if proposal else sorted((ROOT/'runs').glob('*-local-scene-slots-expand'))[-1]
 expected={int(x,16)for x in re.findall(r'^([0-9a-fA-F]{8}):',json.loads((out/'evidence.json').read_text())['assembly'],re.M)};assert expected==coverage,(len(expected),len(coverage),sorted(expected-coverage))
 report=dict(status='original_only_fixture_preflight_pass',cases=len(cases),instruction_address_coverage=[len(coverage),len(expected)],GPUservice='explicit logical E26C RTSfixture; service internals not executed',local_C_checked=False,counts=counts)
 (out/'original-preflight.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(cases),len(coverage))

def main():
 proposal=json.loads((ROOT/'verification/local-scene-slots-expand-author-current.json').read_text());out=Path(proposal['directory']);source=out/'biwn_scene_slots_expand.c';restoration=ROOT/'projects/black-ice-white-noise/restoration'
 syntax=subprocess.run(['clang','-std=c99','-I',str(restoration),'-fsyntax-only','-Xclang','-ast-dump=json',str(source)],capture_output=True,text=True);(out/'syntax.log').write_text(syntax.stderr);assert syntax.returncode==0,syntax.stderr
 tree=json.loads(syntax.stdout);functions=[n for n in tree['inner']if n['kind']=='FunctionDecl'and any(x['kind']=='CompoundStmt'for x in n.get('inner',[]))];names={n['name']for n in functions};assert 'biwn_scene_slots_expand'in names and all(n['name']=='biwn_scene_slots_expand'or n.get('storageClass')=='static'for n in functions)
 assert not any(n['kind']in ['VarDecl','FileScopeAsmDecl']for n in tree['inner'])
 def check(n):
  if not n:return
  assert n['kind']not in ['GCCAsmStmt','MSAsmStmt'];assert n.get('castKind')not in ['IntegralToPointer','PointerToIntegral','BitCast']
  if n['kind']=='CallExpr':
   target=n['inner'][0]
   while target['kind']in ['ImplicitCastExpr','ParenExpr']:target=target['inner'][0]
   assert(target['kind']=='MemberExpr'and target['name']in ['read16','read32','write16','write32','call'])or(target['kind']=='DeclRefExpr'and target['referencedDecl']['name']in names)
  for child in n.get('inner',[]):check(child)
 for f in functions:check(f)
 library=out/'libscene-slots-expand.dylib';build=subprocess.run(['clang','-std=c99','-dynamiclib','-O2','-Wall','-Wextra','-Werror','-I',str(restoration),str(source),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
 lib=c.CDLL(str(library));fn=lib.biwn_scene_slots_expand;fn.argtypes=[c.POINTER(w.Bus),c.POINTER(Seed),c.POINTER(c.c_uint32)];fn.restype=c.c_int
 snapshot,cases=fixtures()
 coverage=set();rows=[]
 for i,case in enumerate(cases):
  a=Script(snapshot,case).set_case(case);b=Script(snapshot,case).set_case(case);value=original(a,case,coverage);status,actual,errors=translated(fn,b,case)
  if status or errors or actual!=value or a.trace!=b.trace or a.memory!=b.memory:
   (out/'mismatch.json').write_text(json.dumps(dict(case=case,status=status,expected=value,actual=actual,original_trace=a.trace,C_trace=b.trace,errors=errors),indent=2)+'\n');raise AssertionError(out/'mismatch.json')
  rows.append(dict(case=i,parameters=case,full_D0=value,trace=b.trace))
 print('Unicorn cases',len(rows),flush=True)
 oracle=media.scheduler.Native(diagnostic_core=Path(json.loads((ROOT/'verification/DSP-music-context-experimental-candidate.json').read_text())['core_path']));runtime=media.Runtime.__new__(media.Runtime);runtime.oracle,runtime.device,runtime.core=oracle,oracle.device,oracle.lib;native=[]
 try:
  for row in rows[:160:5]:
   case=row['parameters'];script=Script(snapshot,case).set_case(case);memory=bytearray(script.memory);memory[SP:SP+4]=STOP.to_bytes(4,'big');memory[0xe26c:0xe26e]=b'\x4e\x75';initial=media.CPU();initial.registers[:15]=case['incoming'];initial.registers[15]=SP;initial.usp=0x180000;initial.ssp=SP;initial.sr=0x2000;initial.pc=0x1142e
   runtime.device.seed(bytes(memory),0);runtime.seed_cpu(initial)
   for _ in range(5000):
    if runtime.cpu().pc==STOP:break
    runtime.core.m68k_execute(1)
   else:raise AssertionError('Native step bound')
   state=runtime.cpu();ram=bytearray(runtime.device.ram());status,value,errors=translated(fn,script,case);ram[0xe26c:0xe26e]=script.memory[0xe26c:0xe26e]
   assert not status and not errors and state.registers[0]==value==row['full_D0']and state.registers[15]==SP+4
   assert ram[:SP-64]==script.memory[:SP-64]and ram[SP+4:]==script.memory[SP+4:]
   native.append(dict(case=row['case'],full_D0=value,face=case['face'],count=case['count']))
 finally:oracle.close()
 guards=[];case=next(x for x in cases if x['count']==1 and x['face']==0)
 for kw in [dict(missing=n)for n in [1,2,3,4,5]]+[dict(nullbus=True),dict(nullseed=True),dict(nullout=True)]:
  script=Script(snapshot,case).set_case(case);status,value,errors=translated(fn,script,case,**kw);assert status==1 and value==0xa55aa55a and not script.trace;guards.append(kw)
 script=Script(snapshot,case).set_case(case);script.fail_call=True;status,value,errors=translated(fn,script,case);assert status==3 and value==0xa55aa55a;guards.append(dict(helper_failure=True))
 for limit in [0,1,2]:
  case=next(x for x in cases if x['count']==3 and x['face']==0);script=Script(snapshot,case).set_case(case);status,value,errors=translated(fn,script,case,limit=limit);assert status==4 and value==0xa55aa55a and script.calls==limit;guards.append(dict(iteration_limit=limit,completed=script.calls))
 case=next(x for x in cases if x['count']==1 and x['face']==0);normal=Script(snapshot,case).set_case(case);status,value,errors=translated(fn,normal,case)
 for position,event in enumerate(normal.trace):
  if event[0]=='call':continue
  a=Script(snapshot,case).set_case(case);b=Script(snapshot,case,fail=position).set_case(case);status,value,errors=translated(fn,b,case);assert status==2 and value==0xa55aa55a and b.trace==normal.trace[:position]
  for event in normal.trace[:position]:
   if event[0]=='w':a.write(event[1],event[2],event[3])
  assert a.memory==b.memory;guards.append(dict(failed_access=position,prior_effects_retained=True))
 expected={int(x,16)for x in re.findall(r'^([0-9a-fA-F]{8}):',json.loads((out/'evidence.json').read_text())['assembly'],re.M)};assert expected==coverage,(len(expected),len(coverage),sorted(expected-coverage))
 (out/'fixtures.json').write_text(json.dumps(rows,indent=2)+'\n');report=dict(status='local_scene_slots_expand_original_checks_pass',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),coordinator_C_body_edits=proposal.get('coordinator_C_body_edits',False),coordinator_edit=proposal.get('coordinator_edit'),local_model_complete_function_accepted=proposal.get('local_model_complete_function_accepted',False),coordinator_patch_boundary_normalization=proposal.get('coordinator_patch_boundary_normalization',[]),host_include_added=proposal.get('host_include_added',False),local_model_repair=proposal.get('local_repair',False),cases=len(rows),original_instruction_address_coverage=[len(coverage),len(expected)],pinned_native_cases=native,host_guards=len(guards),same_weights_correlated=True,roles=[dict(role=d['role'],seconds=d['seconds'])for d in proposal['drafts']],new_training=False,native_Chat_verified=False,full_route_runtime_promoted=False,scope='Complete1142E..11760 six-way scene slot expansion, wrapped ASR32 midpoint edges, zero/multiple iterations, invalid-selector retained register seeds and helper RAM effects. FullD0,logical data/helper order,external2MBRAM versus originalUnicornM68000; native value/RAM subset uses explicit RTS atE26C. GPUserviceE26C internals and fifth-argument overread beyond its pushed zero word remain excluded, as do code/table fetches,nativebusdummyreads,CCR,otherregisters,private stack,timing,naturalgameplay.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/local-scene-slots-expand-checks-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(rows),len(native),len(coverage),flush=True)
if __name__=='__main__':
 import sys
 preflight()if '--original-preflight'in sys.argv else main()
