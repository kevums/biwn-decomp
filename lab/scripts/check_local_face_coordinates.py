"""Complete six-way original routine compared to unedited local C."""
import ctypes as c,hashlib,itertools,json,os,random,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_local_global_animation_tick as animation
import check_biwn_media_setup_cpu as media
ROOT=animation.ROOT;SP=animation.SP;STOP=animation.STOP;w=animation.boundary.world
class Script:
 def __init__(self,snapshot,case,fail=None):
  self.memory=bytearray(snapshot);self.trace=[];self.fail=fail
  for a,width,value in case['initial']:self.memory[a:a+width]=value.to_bytes(width,'big')
 def read(self,a,width):
  if self.fail==len(self.trace):raise RuntimeError('Injected bus failure')
  value=int.from_bytes(self.memory[a:a+width],'big');self.trace.append(['r',a,width,value]);return value
 def write(self,a,width,value):
  if self.fail==len(self.trace):raise RuntimeError('Injected bus failure')
  self.memory[a:a+width]=value.to_bytes(width,'big');self.trace.append(['w',a,width,value])
def original(script,case,coverage):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(script.memory));cpu.mem_write(SP,STOP.to_bytes(4,'big')+case['source'].to_bytes(4,'big')+case['destination'].to_bytes(4,'big')+case['face'].to_bytes(2,'big'))
 cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP);cpu.reg_write(UC_M68K_REG_D0,0xbad00bad)
 def code(e,a,width,_):assert 0x110d4<=a<=0x11382,hex(a);coverage.add(a)
 def read(e,t,a,width,value,_):
  if SP<=a<SP+14 or 0x11104<=a<0x11110:return
  e.mem_write(a,script.read(a,width).to_bytes(width,'big'))
 def write(e,t,a,width,value,_):script.write(a,width,value&((1<<(width*8))-1))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(0x110d4,STOP,count=150,timeout=1000000)
 assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
 return cpu.reg_read(UC_M68K_REG_D0)
def translated(fn,script,case,missing=None,nullbus=False,nullout=False):
 errors=[]
 def read(_,a,out):
  try:out[0]=script.read(a,2);return 0
  except Exception as error:errors.append(repr(error));return 1
 def write(_,a,value):
  try:script.write(a,2,value);return 0
  except Exception as error:errors.append(repr(error));return 1
 cb=[w.R8(),w.R16(read),w.R32(),w.W16(write),w.W32(),w.CALL()]
 if missing is not None:cb[missing]=type(cb[missing])()
 bus=w.Bus(*cb,None,0);out=c.c_uint32(0xa55aa55a);status=fn(None if nullbus else c.byref(bus),case['source'],case['destination'],case['face'],None if nullout else c.byref(out));return status,out.value,errors

def main():
 proposal=json.loads((ROOT/'verification/local-face-coordinates-author-current.json').read_text());out=Path(proposal['directory']);source=out/'biwn_face_coordinates.c';restoration=ROOT/'projects/black-ice-white-noise/restoration'
 syntax=subprocess.run(['clang','-std=c99','-I',str(restoration),'-fsyntax-only','-Xclang','-ast-dump=json',str(source)],capture_output=True,text=True);(out/'syntax.log').write_text(syntax.stderr);assert syntax.returncode==0,syntax.stderr
 tree=json.loads(syntax.stdout);functions=[n for n in tree['inner']if n['kind']=='FunctionDecl'and any(x['kind']=='CompoundStmt'for x in n.get('inner',[]))];names={n['name']for n in functions};assert 'biwn_face_coordinates'in names and all(n['name']=='biwn_face_coordinates'or n.get('storageClass')=='static'for n in functions)
 assert not any(n['kind']in ['VarDecl','FileScopeAsmDecl']for n in tree['inner'])
 def check(n):
  if not n:return # Clang emits empty optional nodes, e.g. absent ForStmt clauses.
  assert n['kind']not in ['GCCAsmStmt','MSAsmStmt'];assert n.get('castKind')not in ['IntegralToPointer','PointerToIntegral','BitCast']
  if n['kind']=='CallExpr':
   target=n['inner'][0]
   while target['kind']in ['ImplicitCastExpr','ParenExpr']:target=target['inner'][0]
   assert(target['kind']=='MemberExpr'and target['name']in ['read16','write16'])or(target['kind']=='DeclRefExpr'and target['referencedDecl']['name']in names)
  for child in n.get('inner',[]):check(child)
 for f in functions:check(f)
 library=out/'libface-coordinates.dylib';result=subprocess.run(['clang','-std=c99','-dynamiclib','-O2','-Wall','-Wextra','-Werror','-I',str(restoration),str(source),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
 lib=c.CDLL(str(library));fn=lib.biwn_face_coordinates;fn.argtypes=[c.POINTER(w.Bus),c.c_uint32,c.c_uint32,c.c_uint16,c.POINTER(c.c_uint32)];fn.restype=c.c_int
 snapshot=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();rng=random.Random(0x110d4);cases=[]
 for face,index,alias in itertools.product([0,1,2,3,4,5,6,0x7fff,0x8000,0xffff],[0,1,100,0x7fff,0x8000],[None,-0x24,-0x12,0]):
  base=0x400c4+(index<<5);destination=0xa0000 if alias is None else base+alias
  initial=[[base+i*2,2,rng.getrandbits(16)]for i in range(16)]+[[0x80000,2,index]]
  cases.append(dict(source=0x80000,destination=destination,face=face,initial=initial,alias=alias,index=index))
 # Explicit word-shift boundary values supplement independently random fixtures.
 for face,value in itertools.product(range(6),[0,1,0x1fff,0x2000,0x7fff,0x8000,0xffff]):
  cases.append(dict(source=0x80000,destination=0xa0000,face=face,initial=[[0x400c4+i*2,2,value]for i in range(16)]+[[0x80000,2,0]],alias=None,index=0))
 coverage=set();rows=[]
 for i,case in enumerate(cases):
  a=Script(snapshot,case);b=Script(snapshot,case);value=original(a,case,coverage);status,actual,errors=translated(fn,b,case)
  if status or errors or actual!=value or a.trace!=b.trace or a.memory!=b.memory:
   (out/'mismatch.json').write_text(json.dumps(dict(case=case,status=status,expected=value,actual=actual,original_trace=a.trace,C_trace=b.trace,errors=errors),indent=2)+'\n');raise AssertionError(out/'mismatch.json')
  rows.append(dict(case=i,parameters=case,full_D0=value,trace=b.trace))
 print('Unicorn cases',len(rows),flush=True)
 oracle=media.scheduler.Native(diagnostic_core=Path(json.loads((ROOT/'verification/DSP-music-context-experimental-candidate.json').read_text())['core_path']));runtime=media.Runtime.__new__(media.Runtime);runtime.oracle,runtime.device,runtime.core=oracle,oracle.device,oracle.lib;native=[]
 try:
  for row in rows[::7]:
   case=row['parameters'];script=Script(snapshot,case);memory=bytearray(script.memory);memory[SP:SP+14]=STOP.to_bytes(4,'big')+case['source'].to_bytes(4,'big')+case['destination'].to_bytes(4,'big')+case['face'].to_bytes(2,'big');initial=media.CPU();initial.registers[0]=0xbad00bad;initial.registers[15]=SP;initial.usp=0x180000;initial.ssp=SP;initial.sr=0x2000;initial.pc=0x110d4
   runtime.device.seed(bytes(memory),0);runtime.seed_cpu(initial)
   for _ in range(150):
    if runtime.cpu().pc==STOP:break
    runtime.core.m68k_execute(1)
   else:raise AssertionError('Native step bound')
   state=runtime.cpu();ram=runtime.device.ram();status,value,errors=translated(fn,script,case)
   assert not status and not errors and state.registers[0]==value==row['full_D0'] and state.registers[15]==SP+4
   assert ram[:SP]==script.memory[:SP] and ram[SP+14:]==script.memory[SP+14:]
   native.append(dict(case=row['case'],face=case['face'],full_D0=value))
 finally:oracle.close()
 guards=[]
 for kw in [dict(missing=1),dict(missing=3),dict(nullbus=True),dict(nullout=True)]:
  script=Script(snapshot,cases[0]);status,value,errors=translated(fn,script,cases[0],**kw);assert status==1 and value==0xa55aa55a and not script.trace;guards.append(kw)
 for row in [rows[0],rows[20],rows[40],rows[60],rows[80],rows[100]]:
  case=row['parameters']
  for position in range(len(row['trace'])):
   a=Script(snapshot,case);b=Script(snapshot,case,fail=position);status,value,errors=translated(fn,b,case);assert status==2 and value==0xa55aa55a and b.trace==row['trace'][:position]
   for event in row['trace'][:position]:
    if event[0]=='w':a.write(event[1],event[2],event[3])
   assert a.memory==b.memory
   guards.append(dict(case=row['case'],failed_access=position,prior_effects_retained=True))
 evidence=json.loads((out/'evidence.json').read_text());expected={int(x,16)for x in re.findall(r'^([0-9a-fA-F]{8}):',evidence['assembly'],re.M)};assert expected==coverage,(len(expected),len(coverage),sorted(expected-coverage))
 (out/'fixtures.json').write_text(json.dumps(rows,indent=2)+'\n');report=dict(status='local_face_coordinates_original_checks_pass',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),source_body_edited=bool(proposal.get('local_repair')),coordinator_C_body_edits=False,local_model_repair=bool(proposal.get('local_repair')),first_draft_failed_compilation=proposal.get('first_draft_failed_compilation',False),cases=len(rows),original_instruction_address_coverage=[len(coverage),len(expected)],pinned_native_cases=native,host_guards=len(guards),same_weights_correlated=True,roles=[dict(role=d['role'],seconds=d['seconds'])for d in proposal['drafts']],new_training=False,native_Chat_verified=False,full_route_runtime_promoted=False,scope='Complete110D4..11382 including six dispatch paths and invalid selectors, sequential aliased data accesses, word-shift boundaries. FullD0,logical data reads/writes and externalRAM match originalUnicornM68000; pinned native CPU value/RAM subset also checked. Immutable code/jumptable fetches,CCR,otherregisters,private stack,timing,nativebusdummyreads and naturalgameplay excluded.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/local-face-coordinates-checks-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(rows),len(native),len(coverage),flush=True)
if __name__=='__main__':main()
