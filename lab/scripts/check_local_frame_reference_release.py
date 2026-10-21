"""Original1AE88 reference release versus readable local C; no helper stubs."""
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
  self.memory=bytearray(snapshot);self.trace=[];self.fail=fail;self.queues={}
  for a,width,value in case['initial']:self.memory[a:a+width]=value.to_bytes(width,'big')
  for q in case.get('read_queues',[]):self.queues[(q['address'],q['width'])]=list(q['values'])
 def read(self,a,width):
  if self.fail==len(self.trace):raise RuntimeError('Injected read failure')
  q=self.queues.get((a,width));value=q.pop(0)if q else int.from_bytes(self.memory[a:a+width],'big');self.trace.append(['r',a,width,value]);return value
 def write(self,a,width,value):
  if self.fail==len(self.trace):raise RuntimeError('Injected write failure')
  self.memory[a:a+width]=value.to_bytes(width,'big');self.trace.append(['w',a,width,value])
def original(script,case,coverage):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(script.memory));cpu.mem_write(SP,STOP.to_bytes(4,'big')+case['id_word'].to_bytes(2,'big'))
 for reg,value in zip(animation.boundary.REGS,case['incoming']):cpu.reg_write(reg,value)
 cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP)
 def code(e,a,width,_):assert 0x1ae88<=a<=0x1aed8,hex(a);coverage.add(a)
 def read(e,t,a,width,value,_):
  if SP-0x1000<=a<SP+6:return
  e.mem_write(a,script.read(a,width).to_bytes(width,'big'))
 def write(e,t,a,width,value,_):
  if SP-0x1000<=a<SP+6:return
  script.write(a,width,value&((1<<(8*width))-1))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(0x1ae88,STOP,count=5000,timeout=1000000);assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
 memory=bytearray(cpu.mem_read(0,0x200000))
 for q in case.get('read_queues',[]):a=q['address'];memory[a:a+q['width']]=script.memory[a:a+q['width']]
 assert memory[:SP-0x1000]==script.memory[:SP-0x1000]and memory[SP+6:]==script.memory[SP+6:];return cpu.reg_read(UC_M68K_REG_D0)
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
 bus=w.Bus(*cb,None,64);out=c.c_uint32(0xa55aa55a);status=fn(None if nullbus else c.byref(bus),case['id_word'],case['incoming'][0],None if nullout else c.byref(out));return status,out.value,errors
def fixtures():
 snapshot=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();rng=random.Random(0x1ae88);cases=[]
 for id_word,mode,count,pattern in itertools.product([0,1,0x7fff,0x8000,0xffff],[0,1,3,0x7fff,0x8000,0xffff],[0,1,2,36,0x7fff,0x8000,0xffff],range(5)):
  sx=mode if mode<32768 else mode-65536;initial=[[0x15b530,2,mode],[0x464a0+sx*2,2,count]]
  for i in range(36):
   stored=0xfffe
   if pattern==1:stored=(id_word+i)&65535
   elif pattern==2 and i>=30:stored=(id_word+i-30)&65535
   elif pattern==3 and i%2==0:stored=(id_word+i//2)&65535
   elif pattern==4:stored=(id_word+35-i)&65535
   refs=[0,1,2,0x7fff,0x8000,0xffff][i%6];initial+=[[0x15b4a0+i*4,2,stored],[0x15b4a2+i*4,2,refs]]
  cases.append(dict(id_word=id_word,mode_word=mode,count_word=count,pattern=pattern,initial=initial,incoming=[rng.getrandbits(32)for _ in animation.boundary.REGS]))
 seed=json.loads(json.dumps(next(x for x in cases if x['id_word']==1 and x['mode_word']==3 and x['count_word']==1 and x['pattern']==1)))
 for values in [[1,0],[1,0xffff],[0x7fff,0x8000],[0xffff],[0]]:
  case=json.loads(json.dumps(seed));case['read_queues']=[dict(address=0x15b4a2,width=2,values=values)];cases.append(case)
 return snapshot,cases
def bind(source,out):
 restore=ROOT/'projects/black-ice-white-noise/restoration';result=subprocess.run(['clang','-std=c99','-I',str(source.parent),'-I',str(restore),'-fsyntax-only','-Xclang','-ast-dump=json',str(source)],capture_output=True,text=True);(out/'syntax.log').write_text(result.stderr);assert not result.returncode,result.stderr;tree=json.loads(result.stdout);functions=[n for n in tree['inner']if n['kind']=='FunctionDecl'and any(x.get('kind')=='CompoundStmt'for x in n.get('inner',[]))];names={n['name']for n in functions};assert 'biwn_frame_reference_release'in names and all(n['name']=='biwn_frame_reference_release'or n.get('storageClass')=='static'for n in functions);assert not any(n['kind']in ['VarDecl','FileScopeAsmDecl']for n in tree['inner'])
 def check(n):
  if not n:return
  assert n['kind']not in ['GCCAsmStmt','MSAsmStmt'];assert n.get('castKind')not in ['IntegralToPointer','PointerToIntegral','BitCast'],dict(forbidden_pointer_conversion=n.get('castKind'),source_range=n.get('range'),expression_type=n.get('type'))
  if n['kind']=='CallExpr':
   target=n['inner'][0]
   while target['kind']in ['ImplicitCastExpr','ParenExpr']:target=target['inner'][0]
   assert(target['kind']=='MemberExpr'and target['name']in ['read16','write16'])or(target['kind']=='DeclRefExpr'and target['referencedDecl']['name']in names)
  for child in n.get('inner',[]):check(child)
 for f in functions:check(f)
 library=out/'libframe-reference-release.dylib';built=subprocess.run(['clang','-std=c99','-dynamiclib','-O2','-Wall','-Wextra','-Werror','-I',str(source.parent),'-I',str(restore),str(source),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(built.stdout+built.stderr);assert not built.returncode,built.stderr;fn=c.CDLL(str(library)).biwn_frame_reference_release;fn.argtypes=[c.POINTER(w.Bus),c.c_uint16,c.c_uint32,c.POINTER(c.c_uint32)];fn.restype=c.c_int;return fn
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--original-only',action='store_true');ap.add_argument('--source');ap.add_argument('--no-publish',action='store_true');opt=ap.parse_args();out=ROOT/'verification/local-frame-reference-release'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);fn=None;source=None
 if not opt.original_only:source=Path(opt.source)if opt.source else Path(json.loads((ROOT/'verification/local-frame-reference-release-author-current.json').read_text())['directory'])/'biwn_frame_reference_release.c';fn=bind(source,out)
 snapshot,cases=fixtures();coverage=set();rows=[]
 for i,case in enumerate(cases):
  a=Script(snapshot,case);value=original(a,case,coverage)
  if fn:
   b=Script(snapshot,case);status,actual,errors=translated(fn,b,case)
   if status or errors or value!=actual or a.trace!=b.trace or a.memory!=b.memory:
    (out/'mismatch.json').write_text(json.dumps(dict(case=i,parameters=case,status=status,expected=value,actual=actual,original_trace=a.trace,C_trace=b.trace,errors=errors),indent=2)+'\n');raise AssertionError(out/'mismatch.json')
  rows.append(dict(case=i,id_word=case['id_word'],mode_word=case['mode_word'],count_word=case['count_word'],pattern=case['pattern'],full_D0=value,trace_events=len(a.trace),trace_sha256=sha(json.dumps(a.trace).encode()),RAM_sha256=sha(a.memory)))
 evidence=json.loads((ROOT/'verification/frame-reference-release-evidence-current.json').read_text());expected={int(x,16)for x in re.findall(r'^([0-9a-fA-F]+):',json.loads((Path(evidence['directory'])/'evidence.json').read_text())['assembly'],re.M)};assert len(expected)==29 and expected==coverage;guards=[];native=[];core_path=None
 if fn:
  for opts in [dict(missing=1),dict(missing=3),dict(nullbus=True),dict(nullout=True)]:
   b=Script(snapshot,cases[0]);status,value,errors=translated(fn,b,cases[0],**opts);assert status==1 and value==0xa55aa55a and not b.trace;guards.append(opts)
  selected=next(x for x in cases if x['id_word']==1 and x['mode_word']==3 and x['count_word']==36 and x['pattern']==1);a=Script(snapshot,selected);original(a,selected,set())
  for i in range(len(a.trace)):
   b=Script(snapshot,selected,fail=i);status,value,errors=translated(fn,b,selected);assert status==2 and value==0xa55aa55a and b.trace==a.trace[:i],(i,status,value);guards.append(dict(failed_event=i,prior_effects_retained=True))
  core_path=Path(json.loads((ROOT/'verification/DSP-music-context-experimental-candidate.json').read_text())['core_path']);oracle=media.scheduler.Native(diagnostic_core=core_path);runtime=media.Runtime.__new__(media.Runtime);runtime.oracle,runtime.device,runtime.core=oracle,oracle.device,oracle.lib
  try:
   chosen=[x for x in cases if x['id_word']in [1,0x7fff,0xffff]and x['mode_word']in [3,0xffff]and x['count_word']in [0,1,36,0x8000]and x['pattern']in [1,2]and not x.get('read_queues')]
   for case in chosen:
    left=Script(snapshot,case);status,value,errors=translated(fn,left,case);initial=Script(snapshot,case);memory=initial.memory;memory[SP:SP+6]=STOP.to_bytes(4,'big')+case['id_word'].to_bytes(2,'big');cpu=media.CPU();cpu.registers[:15]=case['incoming'];cpu.registers[15]=SP;cpu.pc=0x1ae88;cpu.sr=0x2000;cpu.usp=0x180000;cpu.ssp=SP;runtime.device.seed(bytes(memory),0);runtime.seed_cpu(cpu);steps=0
    while runtime.cpu().pc!=STOP and steps<5000:runtime.core.m68k_execute(1);steps+=1
    actual=runtime.cpu();ram=runtime.device.ram();assert not status and not errors and actual.pc==STOP and actual.registers[15]==SP+4 and actual.registers[0]==value and ram[:SP-0x1000]==left.memory[:SP-0x1000]and ram[SP+6:]==left.memory[SP+6:];native.append(dict(id_word=case['id_word'],mode_word=case['mode_word'],count_word=case['count_word'],pattern=case['pattern'],full_D0=value,steps=steps))
  finally:oracle.close()
 (out/'fixtures.json').write_text(json.dumps(cases,indent=2)+'\n');(out/'case-results.json').write_text(json.dumps(rows,indent=2)+'\n');report=dict(status='frame_reference_release_original_preflight_pass'if opt.original_only else'local_frame_reference_release_original_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),source=str(source)if source else None,source_sha256=sha(source.read_bytes())if source else None,cases=len(rows),instruction_address_coverage=[29,29],guards=guards,pinned_native_cases=native,core_path=str(core_path)if core_path else None,core_sha256=sha(core_path.read_bytes())if core_path else None,remaining_scripted_helpers=[],new_training=False,native_Chat_verified=False,natural_gameplay_integration_verified=False,full_route_runtime_promoted=False,scope='Complete1AE88..1AED8 fullD0,logicalorderedreads/stores and2MBRAM against originalUnicornM68000,plusselected pinnednativeCPU finalD0/externalRAM. SignedIDs/modes/counts/refs,wantedword7FFFto8000wrap,sparse/reversed36entries,and separateTST/SUBQqueuedreads covered. Nohelpers. Queued oracleRAMreadpatches normalized atdeclaredranges; modeled busRAM remains authoritative. Privateframes/CCR/otherregs,nativebusdummyreads,physicaltiming andnaturalgameplay excluded.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');
 if not opt.no_publish:(ROOT/'verification'/('local-frame-reference-release-'+('preflight'if opt.original_only else'checks-current')+'.json')).write_text(json.dumps(report,indent=2)+'\n');
 print(report['status'],len(rows),len(coverage),'native',len(native),'guards',len(guards),flush=True)
if __name__=='__main__':main()
