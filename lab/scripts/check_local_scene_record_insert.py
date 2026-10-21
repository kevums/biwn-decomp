"""Original11762 versus a native-Chat-authored readable C candidate.

No decompiler output is used as a behavior oracle. Logical fullD0/data order,
externalRAM compare; private frames,CCR and timing are excluded.
"""
import argparse,ctypes as c,hashlib,itertools,json,os,random,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_local_global_animation_tick as animation
import check_biwn_media_setup_cpu as media
ROOT=animation.ROOT;SP=animation.SP;STOP=animation.STOP;w=animation.boundary.world
sha=lambda b:hashlib.sha256(b).hexdigest()
class Script:
 def __init__(self,snapshot,case,fail=None):
  self.memory=bytearray(snapshot);self.trace=[];self.fail=fail;self.read_number=0;self.queues=list(case.get('index_reads',[]))
  for a,width,value in case['initial']:self.memory[a:a+width]=value.to_bytes(width,'big')
 def read(self,a,width):
  if self.fail==len(self.trace):raise RuntimeError('Injected read failure')
  value=int.from_bytes(self.memory[a:a+width],'big')
  if a==0x400e4 and width==2 and self.queues:value=self.queues.pop(0)
  self.trace.append(['r',a,width,value]);return value
 def write(self,a,width,value):
  if self.fail==len(self.trace):raise RuntimeError('Injected write failure')
  self.memory[a:a+width]=value.to_bytes(width,'big');self.trace.append(['w',a,width,value])
def original(script,case,coverage):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(script.memory))
 kind,x,y,z=case['parameters'];frame=STOP.to_bytes(4,'big')+kind.to_bytes(2,'big')+b''.join(v.to_bytes(4,'big')for v in [x,y,z]);cpu.mem_write(SP,frame)
 for reg,value in zip(animation.boundary.REGS,case['incoming']):cpu.reg_write(reg,value)
 cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP)
 def code(e,a,width,_):assert 0x11762<=a<=0x11806,hex(a);coverage.add(a)
 def read(e,t,a,width,value,_):
  if SP<=a<SP+len(frame):return
  e.mem_write(a,script.read(a,width).to_bytes(width,'big'))
 def write(e,t,a,width,value,_):script.write(a,width,value&((1<<(width*8))-1))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(0x11762,STOP,count=5000,timeout=1000000)
 assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
 memory=bytes(cpu.mem_read(0,0x200000))
 if case.get('index_reads'):
  assert memory[:0x400e4]==script.memory[:0x400e4]and memory[0x400e6:SP]==script.memory[0x400e6:SP]
 else:assert memory[:SP]==script.memory[:SP]
 assert memory[SP+len(frame):]==script.memory[SP+len(frame):]
 return cpu.reg_read(UC_M68K_REG_D0)
def translated(fn,script,case,missing=None,nullbus=False,nullout=False,limit=64):
 errors=[]
 def read(_,a,out):
  try:out[0]=script.read(a,2);return 0
  except Exception as error:errors.append(repr(error));return 1
 def write(width):
  def f(_,a,value):
   try:script.write(a,width,value);return 0
   except Exception as error:errors.append(repr(error));return 1
  return f
 cb=[w.R8(),w.R16(read),w.R32(),w.W16(write(2)),w.W32(write(4)),w.CALL()]
 if missing is not None:cb[missing]=type(cb[missing])()
 bus=w.Bus(*cb,None,limit);out=c.c_uint32(0xa55aa55a);status=fn(None if nullbus else c.byref(bus),*case['parameters'],case['incoming'][0],None if nullout else c.byref(out));return status,out.value,errors
def fixtures():
 snapshot=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();rng=random.Random(0x11762);cases=[]
 for index,pattern,ordinal in itertools.product([0,1,2,14,15,16,32767,0xffff,0xfffe,0xfffd],range(7),range(4)):
  initial=[]
  for row in range(-3,18):
   base=0x400ea+row*46
   for offset in range(0,46,2):initial.append([base+offset,2,rng.getrandbits(16)])
   occupied=[0,1,int(row!=1),int(row!=15),int(row!=16),int(row==16),rng.randrange(2)][pattern];initial.append([base,2,0xffff if occupied else 0])
  initial.append([0x400e4,2,index]);values=[0,0xffffffff,0x80000000,0x7fffffff];params=[values[ordinal]&65535,*[values[(ordinal+n)%4]for n in range(3)]]
  cases.append(dict(index=index,pattern=pattern,initial=initial,parameters=params,incoming=[rng.getrandbits(32)for _ in animation.boundary.REGS]))
 for reads in [[0,16],[16,0],[0xffff,15],[15,0xffff]]:
  case=json.loads(json.dumps(cases[0]));case['index_reads']=reads;cases.append(case)
 return snapshot,cases
def syntax_and_bind(source,out):
 restore=ROOT/'projects/black-ice-white-noise/restoration';inspection=subprocess.run(['clang','-std=c99','-I',str(source.parent),'-I',str(restore),'-fsyntax-only','-Xclang','-ast-dump=json',str(source)],capture_output=True,text=True);(out/'syntax.log').write_text(inspection.stderr);assert inspection.returncode==0,inspection.stderr
 tree=json.loads(inspection.stdout);functions=[n for n in tree['inner']if n['kind']=='FunctionDecl'and any(x['kind']=='CompoundStmt'for x in n.get('inner',[]))];names={n['name']for n in functions};assert 'biwn_scene_record_insert'in names and all(n['name']=='biwn_scene_record_insert'or n.get('storageClass')=='static'for n in functions);assert not any(n['kind']in ['VarDecl','FileScopeAsmDecl']for n in tree['inner'])
 def check(n):
  if not n:return
  assert n['kind']not in ['GCCAsmStmt','MSAsmStmt'];assert n.get('castKind')not in ['IntegralToPointer','PointerToIntegral','BitCast']
  if n['kind']=='CallExpr':
   target=n['inner'][0]
   while target['kind']in ['ImplicitCastExpr','ParenExpr']:target=target['inner'][0]
   assert(target['kind']=='MemberExpr'and target['name']in ['read16','write16','write32'])or(target['kind']=='DeclRefExpr'and target['referencedDecl']['name']in names)
  for child in n.get('inner',[]):check(child)
 for f in functions:check(f)
 library=out/'libscene-record-insert.dylib';build=subprocess.run(['clang','-std=c99','-dynamiclib','-O2','-Wall','-Wextra','-Werror','-I',str(source.parent),'-I',str(restore),str(source),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
 fn=c.CDLL(str(library)).biwn_scene_record_insert;fn.argtypes=[c.POINTER(w.Bus),c.c_uint16,*[c.c_uint32]*4,c.POINTER(c.c_uint32)];fn.restype=c.c_int;return fn
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--original-only',action='store_true');ap.add_argument('--source');ap.add_argument('--no-publish',action='store_true');opt=ap.parse_args();evidence=json.loads((ROOT/'verification/scene-record-insert-evidence-current.json').read_text());source=Path(opt.source)if opt.source else Path(evidence['directory'])/'biwn_scene_record_insert.c';out=ROOT/'verification/local-scene-record-insert'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 snapshot,cases=fixtures();coverage=set();rows=[];fn=None if opt.original_only else syntax_and_bind(source,out)
 for i,case in enumerate(cases):
  a=Script(snapshot,case);expected=original(a,case,coverage)
  if fn:
   b=Script(snapshot,case);status,value,errors=translated(fn,b,case)
   if status or errors or value!=expected or a.trace!=b.trace or a.memory!=b.memory:
    (out/'mismatch.json').write_text(json.dumps(dict(case=i,parameters=case,status=status,expected=expected,actual=value,original_trace=a.trace,C_trace=b.trace,errors=errors),indent=2)+'\n');raise AssertionError(out/'mismatch.json')
  rows.append(dict(case=i,index=case['index'],pattern=case['pattern'],index_reads=case.get('index_reads'),parameters=case['parameters'],full_D0=expected,trace_events=len(a.trace),trace_sha256=sha(json.dumps(a.trace).encode()),RAM_sha256=sha(a.memory)))
 expected_addresses={int(pc,16)for pc in re.findall(r'^([0-9a-fA-F]+):',json.loads((Path(evidence['directory'])/'evidence.json').read_text())['assembly'],re.M)};assert coverage==expected_addresses,(coverage-expected_addresses,expected_addresses-coverage)
 (out/'fixtures.json').write_text(json.dumps(cases,indent=2)+'\n');(out/'case-results.json').write_text(json.dumps(rows,indent=2)+'\n')
 guards=[];native=[];core_path=None
 if fn:
  for opts in [dict(missing=1),dict(missing=3),dict(missing=4),dict(nullbus=True),dict(nullout=True)]:
   b=Script(snapshot,cases[0]);status,value,errors=translated(fn,b,cases[0],**opts);assert status==1 and value==0xa55aa55a and not b.trace;guards.append(opts)
  selected=cases[0];a=Script(snapshot,selected);original(a,selected,set())
  for i in range(len(a.trace)):
   b=Script(snapshot,selected,fail=i);status,value,errors=translated(fn,b,selected);assert status==2 and value==0xa55aa55a and b.trace==a.trace[:i],(i,status,value);guards.append(dict(failed_event=i,prior_effects_retained=True))
  for limit in [0,1,2]:
   b=Script(snapshot,cases[4]);status,value,errors=translated(fn,b,cases[4],limit=limit);assert status==4 and value==0xa55aa55a;guards.append(dict(scan_limit=limit,output_unchanged=True))
 if fn:
  core_path=Path(json.loads((ROOT/'verification/DSP-music-context-experimental-candidate.json').read_text())['core_path']);oracle=media.scheduler.Native(diagnostic_core=core_path);runtime=media.Runtime.__new__(media.Runtime);runtime.oracle,runtime.device,runtime.core=oracle,oracle.device,oracle.lib
  try:
   for index,pattern in itertools.product([0,1,14,15,16,32767,0xffff,0xfffe,0xfffd],[0,1,4]):
    case=next(x for x in cases if x['index']==index and x['pattern']==pattern);script=Script(snapshot,case);status,value,errors=translated(fn,script,case);assert status==0 and not errors
    initial=Script(snapshot,case);memory=initial.memory;kind,x,y,z=case['parameters'];memory[SP:SP+18]=STOP.to_bytes(4,'big')+kind.to_bytes(2,'big')+b''.join(v.to_bytes(4,'big')for v in [x,y,z]);cpu=media.CPU();cpu.registers[:15]=case['incoming'];cpu.registers[15]=SP;cpu.pc=0x11762;cpu.sr=0x2000;cpu.usp=0x180000;cpu.ssp=SP;runtime.device.seed(bytes(memory),0);runtime.seed_cpu(cpu);steps=0
    while runtime.cpu().pc!=STOP and steps<5000:runtime.core.m68k_execute(1);steps+=1
    actual=runtime.cpu();ram=runtime.device.ram();assert actual.pc==STOP and actual.registers[15]==SP+4 and actual.registers[0]==value,(index,pattern,actual.pc,actual.registers[0],value)
    assert ram[:SP]==script.memory[:SP]and ram[SP+18:]==script.memory[SP+18:]
    native.append(dict(index=index,pattern=pattern,full_D0=value,steps=steps,external_RAM_match=True))
  finally:oracle.close()
 report=dict(status='original11762_fixture_preflight_pass'if opt.original_only else'native_Chat_scene_record_insert_original_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),source=str(source)if fn else None,source_sha256=sha(source.read_bytes())if fn else None,cases=len(rows),original_instruction_address_coverage=[len(coverage),len(expected_addresses)],guards=guards,pinned_native_cases=native,core_path=str(core_path)if core_path else None,core_sha256=sha(core_path.read_bytes())if core_path else None,new_training=False,native_Chat_authorship_verified=False,natural_gameplay_integration_verified=False,full_route_runtime_promoted=False,scope='Complete11762..11806 fullD0,logical ordered external reads/stores and2MBRAM against originalUnicornM68000,plus27 pinned nativeCPU finalD0/externalRAM comparisons when C is tested. Four queued initial-index rereads and negative-index aliasing retained. Private frame,CCR,otherregisters,unmapped exceptions,native dummy reads,timing,physicalhardware and naturalgameplay excluded. Model authorship requires separate native export receipt.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 if not opt.no_publish:(ROOT/'verification'/('local-scene-record-insert-'+('preflight'if opt.original_only else'checks-current')+'.json')).write_text(json.dumps(report,indent=2)+'\n')
 print(report['status'],len(rows),len(coverage),'guards',len(guards),flush=True)
if __name__=='__main__':main()
