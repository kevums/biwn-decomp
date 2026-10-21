"""Complete10734 caller plus actual recovered149AE text, explicit formatter fixture."""
import ctypes as c,hashlib,json,os,random,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_overlay as overlay
import check_biwn_text as text
ROOT=overlay.ROOT;SP=overlay.SP;STOP=overlay.STOP;SCRATCH=SP-54;w=overlay.world
WIDTHS={0x1b45a:[4,4,4],0x149ae:[2,2,4,4,4,4,2,2]}
class Script(overlay.scene.Script):
 def __init__(self,snapshot,case):super().__init__(snapshot,case);self.format_calls=0;self.text_calls=0
 def formatter(self,args,incoming):
  if self.fail_call==0x1b45a:raise RuntimeError('Injected formatter service failure')
  self.trace.append(['call',0x1b45a,args,incoming]);self.changed=[];n=self.format_calls;self.format_calls+=1
  message=('fixture'+str(n)).encode()+b'\0'
  for i,value in enumerate(message):self.put(args[0]+i,1,value)
  for ordinal,address,width,value in self.case.get('formatter_effects',[]):
   if ordinal==n:self.put(address,width,value)
  return self.case['formatter_returns'][n]
 def note_text(self,args,incoming):
  if self.fail_call==0x149ae:raise RuntimeError('Injected text service failure')
  self.trace.append(['call',0x149ae,args,incoming]);self.text_calls+=1

def original(script,case,coverage):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_map(0xf02000,0x1000);cpu.mem_write(0,bytes(script.memory));cpu.mem_write(SP,STOP.to_bytes(4,'big'));cpu.mem_write(0x1b45a,b'\x4e\x75')
 for reg,value in zip(w.REGS,case['incoming']):cpu.reg_write(reg,value)
 cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP)
 def code(e,a,width,_):
  if a in WIDTHS:
   sp=e.reg_read(UC_M68K_REG_A7);offset=4;args=[]
   for width in WIDTHS[a]:args.append(int.from_bytes(e.mem_read(sp+offset,width),'big'));offset+=width
   if a==0x1b45a:
    value=script.formatter(args,e.reg_read(UC_M68K_REG_D0))
    for address,width,value in script.changed:e.mem_write(address,value.to_bytes(width,'big'))
    e.reg_write(UC_M68K_REG_D0,script.case['formatter_returns'][script.format_calls-1]);return
   script.note_text(args,e.reg_read(UC_M68K_REG_D0))
  assert 0x10734<=a<=0x10966 or 0x14776<=a<0x14caa or 0xe540<=a<0xe588,hex(a);coverage.add(a)
 def private(a):return SP-0x1000<=a<SP+4 and not SCRATCH<=a<SCRATCH+54
 def read(e,t,a,width,value,_):
  if private(a)or 0x14800<=a<0x14842:return
  e.mem_write(a,script.read(a,width).to_bytes(width,'big'))
 def write(e,t,a,width,value,_):
  if private(a):return
  script.write(a,width,value&((1<<(8*width))-1))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(0x10734,STOP,count=100000,timeout=3000000)
 assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
 return cpu.reg_read(UC_M68K_REG_D0)

def translated(fn,draw,script,case,missing=None,nullout=False):
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
 text_callbacks=[text.R8(read(1)),text.R16(read(2)),text.W32(lambda _,a,value:write(4)(_,a,value))];text_bus=text.Bus(*text_callbacks,None,100000)
 def call(_,target,args,count,out):
  try:
   assert target in WIDTHS and count==len(WIDTHS[target]),('invalid_helper_count',hex(target),count);values=list(args[:count])
   if target==0x1b45a:out[0]=script.formatter(values,out[0]);return 0
   script.note_text(values,out[0]);arguments=text.Args(*values);value=c.c_uint32(out[0]);status=draw(c.byref(text_bus),c.byref(arguments),c.byref(value))
   if not status:out[0]=value.value
   return status
  except Exception as error:errors.append(repr(error));return 1
 cb=[w.R8(read(1)),w.R16(read(2)),w.R32(read(4)),w.W16(write(2)),w.W32(write(4)),w.CALL(call)]
 if missing is not None:cb[missing]=type(cb[missing])()
 bus=w.Bus(*cb,None,0);out=c.c_uint32(0xa55aa55a);status=fn(c.byref(bus),SCRATCH,case['incoming'][0],None if nullout else c.byref(out));return status,out.value,errors

def fixtures():
 snapshot=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();rng=random.Random(0x10734);cases=[];edges=[0,1,0x7fffffff,0x80000000,0xffffffff,0x12345678]
 for i in range(96):
  flag=[0,1,0x8000,0xffff][i%4];initial=[[0x403cc,2,flag]]+[[a,4,edges[(i+n)%len(edges)]]for n,a in enumerate([0x400ec,0x400f0,0x400f4,0x400fc,0x400f8,0x40100])]+[[0x403d0,2,[0,1,0x7fff,0x8000,0xffff][i%5]],[0x403ca,2,[0,1,31,0xffff][(i//4)%4]]]
  if i%2:
   for n,value in enumerate(bytes([3,96,8,9,32,126,0x54,0])):initial.append([0x4c3e0+n,1,value])
  effects=[[0,0x400f0,4,0xabcdef01],[5,0x403d0,2,0x8001],[6,0x403ca,2,0xffff]]if i%7==0 else[]
  cases.append(dict(initial=initial,incoming=[rng.getrandbits(32)for _ in w.REGS],formatter_returns=[rng.getrandbits(32)for _ in range(8)],formatter_effects=effects,blitter_status=[1],draw_counts=[0],read_queues=[],flag=flag,font='synthetic3'if i%2 else'frozen2'))
 return snapshot,cases

def preflight():
 snapshot,cases=fixtures();coverage=set()
 for case in cases:script=Script(snapshot,case);original(script,case,coverage);assert script.format_calls==script.text_calls==(8 if case['flag'] else 0)
 print('original preflight',len(cases),'caller PCs',sum(0x10734<=pc<=0x10966 for pc in coverage),'text PCs',sum(not 0x10734<=pc<=0x10966 for pc in coverage))

def main():
 p=json.loads((ROOT/'verification/local-debug-overlay-author-current.json').read_text());out=Path(p['directory']);source=out/'biwn_debug_overlay.c';restoration=ROOT/'projects/black-ice-white-noise/restoration';text_source=restoration/'biwn_text.c';text_hash=hashlib.sha256(text_source.read_bytes()).hexdigest()
 syntax=subprocess.run(['clang','-std=c99','-I',str(restoration),'-fsyntax-only','-Xclang','-ast-dump=json',str(source)],capture_output=True,text=True);(out/'syntax.log').write_text(syntax.stderr);assert syntax.returncode==0,syntax.stderr
 tree=json.loads(syntax.stdout);functions=[n for n in tree['inner']if n['kind']=='FunctionDecl'and any(x['kind']=='CompoundStmt'for x in n.get('inner',[]))];names={n['name']for n in functions};assert 'biwn_debug_overlay'in names and all(n['name']=='biwn_debug_overlay'or n.get('storageClass')=='static'for n in functions);assert not any(n['kind']in ['VarDecl','FileScopeAsmDecl']for n in tree['inner'])
 def check(n):
  if not n:return
  assert n['kind']not in ['GCCAsmStmt','MSAsmStmt'];assert n.get('castKind')not in ['IntegralToPointer','PointerToIntegral','BitCast']
  if n['kind']=='CallExpr':
   target=n['inner'][0]
   while target['kind']in ['ImplicitCastExpr','ParenExpr']:target=target['inner'][0]
   assert(target['kind']=='MemberExpr'and target['name']in ['read16','read32','write32','call'])or(target['kind']=='DeclRefExpr'and target['referencedDecl']['name']in names)
  for child in n.get('inner',[]):check(child)
 for f in functions:check(f)
 libpath=out/'libdebug-overlay.dylib';build=subprocess.run(['clang','-std=c99','-dynamiclib','-O2','-Wall','-Wextra','-Werror','-I',str(restoration),str(source),str(text_source),'-o',str(libpath)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
 lib=c.CDLL(str(libpath));fn=lib.biwn_debug_overlay;fn.argtypes=[c.POINTER(w.Bus),c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];fn.restype=c.c_int;draw=lib.biwn_text_draw;draw.argtypes=[c.POINTER(text.Bus),c.POINTER(text.Args),c.POINTER(c.c_uint32)];draw.restype=c.c_int
 snapshot,cases=fixtures();coverage=set();rows=[]
 for i,case in enumerate(cases):
  a=Script(snapshot,case);b=Script(snapshot,case);expected=original(a,case,coverage);status,value,errors=translated(fn,draw,b,case)
  if status or errors or value!=expected or a.trace!=b.trace or a.memory!=b.memory or a.mmio!=b.mmio:
   (out/'mismatch.json').write_text(json.dumps(dict(case=i,parameters=case,status=status,expected=expected,actual=value,original_trace=a.trace,C_trace=b.trace,errors=errors),indent=2)+'\n');raise AssertionError(out/'mismatch.json')
  rows.append(dict(case=i,parameters=case,full_D0=value,formatter_calls=b.format_calls,text_calls=b.text_calls,trace=b.trace))
 expected={int(x,16)for x in re.findall(r'^([0-9a-fA-F]{8}):',json.loads((out/'evidence.json').read_text())['assembly'],re.M)};assert expected=={x for x in coverage if 0x10734<=x<=0x10966}
 guards=[]
 for missing in [1,2,4,5]:
  script=Script(snapshot,cases[1]);status,value,errors=translated(fn,draw,script,cases[1],missing=missing);assert status==1 and value==0xa55aa55a and not script.trace;guards.append(dict(missing=missing))
 for target in WIDTHS:
  script=Script(snapshot,cases[1]);script.fail_call=target;status,value,errors=translated(fn,draw,script,cases[1]);assert status==3 and value==0xa55aa55a;guards.append(dict(dependency_failure=hex(target)))
 script=Script(snapshot,cases[1]);status,value,errors=translated(fn,draw,script,cases[1],nullout=True);assert status==1;guards.append(dict(nullout=True))
 case=cases[1]
 for kind,address,width in [('w',0xf02268,4),('r',0x403cc,2),('r',0x400ec,4),('r',0x403d0,2),('r',0x403ca,2)]:
  script=Script(snapshot,case)
  if kind=='r':script.fail_read=(address,width)
  else:script.fail_write=(address,width)
  status,value,errors=translated(fn,draw,script,case);assert status==2 and value==0xa55aa55a;guards.append(dict(bus_failure=[kind,address,width]))
 (out/'fixtures.json').write_text(json.dumps(rows,indent=2)+'\n');report=dict(status='debug_overlay_and_actual_text_original_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),text_source_sha256=text_hash,cases=len(rows),caller_instruction_address_coverage=[len(expected),len(expected)],text_instruction_addresses=len(coverage-expected),formatter_scripted=True,text_C_executed=True,roles=[dict(role=d['role'],seconds=d['seconds'])for d in p['drafts']],coordinator_C_body_edits=p.get('coordinator_C_body_edits',False),host_include_added=p.get('host_include_added',False),local_model_repair=p.get('local_repair',False),host_guards=guards,new_training=False,native_Chat_verified=False,full_route_runtime_promoted=False,scope='Complete10734debugoff/on andall8rows linked to real recovered149AEtext C, including147A6/14776andintegerhelper original instructions. FullD0,logical data/helper accesses,RAM/MMIO observations versus originalUnicornM68000. Formatter1B45A remains explicit fixture with RAM effects; text uses frozenformat2/syntheticformat3fonts and logicaldevicewrite model. PrivateCPUstack/CCR/otherregisters,nativebusdummyreads,physicalblitterpixels/timing,naturalgameplay/fullroute excluded.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/local-debug-overlay-checks-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(rows),len(expected),report['text_instruction_addresses'])
if __name__=='__main__':
 import sys
 preflight()if '--original-preflight'in sys.argv else main()
