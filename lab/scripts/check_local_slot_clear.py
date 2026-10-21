"""Original instruction tests for locally authored 10968 dependency."""
import ctypes as c,hashlib,itertools,json,os,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_media_setup_cpu as media
ROOT=Path(__file__).resolve().parents[1];SP=0x1ff000;STOP=0x190000
W8=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint8)
class Bus(c.Structure):_fields_=[('write8',W8),('context',c.c_void_p)]
def sx(word):return word if word<32768 else word-65536
def translated(fn,snapshot,first,count,fail=None,missing=False,nullbus=False,nullout=False):
 memory=bytearray(snapshot);writes=[];errors=[]
 def write(_,a,v):
  if len(writes)==fail:return 1
  if not 0<=a<len(memory):errors.append(a);return 1
  memory[a]=v;writes.append((a,v));return 0
 cb=W8() if missing else W8(write);bus=Bus(cb,None);out=c.c_uint32(0xa55aa55a)
 status=fn(None if nullbus else c.byref(bus),first,count,None if nullout else c.byref(out))
 return status,out.value,memory,writes,errors

def original(snapshot,first,count,coverage):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,snapshot);cpu.mem_write(SP,STOP.to_bytes(4,'big')+first.to_bytes(2,'big')+count.to_bytes(2,'big'))
 cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP);cpu.reg_write(UC_M68K_REG_D0,0xbad00bad);cpu.reg_write(UC_M68K_REG_D1,0x12345678);writes=[]
 def code(e,a,w,_):
  assert 0x10968<=a<=0x1098e,hex(a);coverage.add(a)
 def write(e,t,a,w,v,_):assert w==1;writes.append((a,v&255))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(0x10968,STOP,count=400000,timeout=15000000)
 assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
 return cpu.reg_read(UC_M68K_REG_D0),bytes(cpu.mem_read(0,0x200000)),writes

def main():
 proposal=json.loads((ROOT/'verification/local-slot-clear-author-current.json').read_text());out=Path(proposal['directory']);source=out/'biwn_slot_clear.c';restoration=ROOT/'projects/black-ice-white-noise/restoration'
 syntax=subprocess.run(['clang','-std=c99','-I',str(restoration),'-fsyntax-only','-Xclang','-ast-dump=json',str(source)],capture_output=True,text=True);(out/'syntax.log').write_text(syntax.stderr);assert syntax.returncode==0,syntax.stderr
 tree=json.loads(syntax.stdout);functions=[n for n in tree['inner'] if n['kind']=='FunctionDecl' and any(x['kind']=='CompoundStmt' for x in n.get('inner',[]))];names={n['name'] for n in functions};assert 'biwn_slot_clear' in names and all(n['name']=='biwn_slot_clear' or n.get('storageClass')=='static' for n in functions)
 assert not any(n['kind'] in ['VarDecl','FileScopeAsmDecl'] for n in tree['inner'])
 def check(n):
  assert n['kind'] not in ['GCCAsmStmt','MSAsmStmt'];assert n.get('castKind') not in ['IntegralToPointer','PointerToIntegral','BitCast']
  if n['kind']=='CallExpr':
   target=n['inner'][0]
   while target['kind'] in ['ImplicitCastExpr','ParenExpr']:target=target['inner'][0]
   assert (target['kind']=='MemberExpr' and target['name']=='write8') or (target['kind']=='DeclRefExpr' and target['referencedDecl']['name'] in names)
  for x in n.get('inner',[]):check(x)
 for n in functions:check(n)
 library=out/'libslot-clear.dylib';result=subprocess.run(['clang','-std=c99','-dynamiclib','-O2','-Wall','-Wextra','-Werror','-I',str(restoration),str(source),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
 lib=c.CDLL(str(library));fn=lib.biwn_slot_clear;fn.argtypes=[c.POINTER(Bus),c.c_uint16,c.c_uint16,c.POINTER(c.c_uint32)];fn.restype=c.c_int
 snapshot=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();coverage=set();rows=[]
 for first,count in itertools.product([0,1,0xffff,0xff00],[0,1,7,511,512,513,1023,0x7fff,0x8000,0xfffe,0xffff]):
  value,memory,writes=original(snapshot,first,count,coverage);status,actual,cmem,cwrites,errors=translated(fn,snapshot,first,count)
  assert not status and not errors and value==actual and writes==cwrites,(first,count,value,actual,len(writes),len(cwrites))
  assert memory[:SP]==cmem[:SP] and memory[SP+8:]==cmem[SP+8:]
  rows.append(dict(first_word=first,count_word=count,full_D0=actual,stores=len(writes),writes_sha256=hashlib.sha256(json.dumps(writes).encode()).hexdigest()))
 print('Unicorn cases',len(rows),flush=True)
 oracle=media.scheduler.Native(diagnostic_core=Path(json.loads((ROOT/'verification/DSP-music-context-experimental-candidate.json').read_text())['core_path']));runtime=media.Runtime.__new__(media.Runtime);runtime.oracle,runtime.device,runtime.core=oracle,oracle.device,oracle.lib;native=[]
 try:
  for first,count in [(0,0),(1,1),(0xffff,7),(0xff00,511),(0,512),(1,0xffff)]:
   status,value,cmem,writes,errors=translated(fn,snapshot,first,count);memory=bytearray(snapshot);memory[SP:SP+8]=STOP.to_bytes(4,'big')+first.to_bytes(2,'big')+count.to_bytes(2,'big');initial=media.CPU();initial.registers[0]=0xbad00bad;initial.registers[1]=0x12345678;initial.registers[15]=SP;initial.usp=0x180000;initial.ssp=SP;initial.sr=0x2000;initial.pc=0x10968
   runtime.device.seed(bytes(memory),0);runtime.seed_cpu(initial);steps=0
   while runtime.cpu().pc!=STOP and steps<400000:runtime.core.m68k_execute(1);steps+=1
   state=runtime.cpu();ram=runtime.device.ram();assert state.pc==STOP and state.registers[15]==SP+4 and state.registers[0]==value
   assert ram[:SP]==cmem[:SP] and ram[SP+8:]==cmem[SP+8:]
   native.append(dict(first_word=first,count_word=count,full_D0=value,stores=len(writes),steps=steps))
 finally:oracle.close()
 guards=[]
 for kw in [dict(missing=True),dict(nullbus=True),dict(nullout=True)]:
  status,value,mem,writes,errors=translated(fn,snapshot,1,7,**kw);assert status==1 and value==0xa55aa55a and not writes;guards.append(kw)
 for at in [0,1,63,64,447]:
  status,value,mem,writes,errors=translated(fn,snapshot,1,7,fail=at);assert status==2 and value==0xa55aa55a and len(writes)==at
  expected=bytearray(snapshot);expected[0x47bc8:0x47bc8+at]=bytes(at);assert mem==expected;guards.append(dict(failed_store=at,prior_effects_retained=True))
 evidence=json.loads((out/'evidence.json').read_text());expected={int(x,16) for x in re.findall(r'^([0-9a-fA-F]{8}):',evidence['assembly'],re.M)};assert expected==coverage
 report=dict(status='local_slot_clear_original_checks_pass',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),source_body_edited=False,original_cases=rows,original_instruction_address_coverage=[len(coverage),len(expected)],pinned_native_cases=native,guards=guards,roles=[dict(role=d['role'],seconds=d['seconds']) for d in proposal['drafts']],same_weights_correlated=True,new_training=False,native_Chat_verified=False,full_route_runtime_promoted=False,scope='Complete10968..1098E fullD0 and externalRAM, ordered logical byte stores versus Unicorn across44signed-count/slotfixtures; six pinned JaguarCPU value/RAM crosschecks. NativeCLR dummyreads,CCR,otherregisters,private stack,timing and naturalgameplay excluded.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/local-slot-clear-checks-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(rows),len(native),len(coverage),flush=True)
if __name__=='__main__':main()
