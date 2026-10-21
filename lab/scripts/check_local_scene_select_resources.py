"""Scene selector with real release/acquisition; only disk loader is scripted."""
import argparse,ctypes as c,hashlib,itertools,json,os,random,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_local_global_animation_tick as animation
import check_biwn_media_setup_cpu as media
import check_local_frame_resource_acquire as acquire
ROOT=animation.ROOT;SP=animation.SP;STOP=animation.STOP;w=animation.boundary.world;HELPERS=[0x1b044];ENTRIES=[0x1ae88,0x1ac68,0x1b044];RELEASE=None;ACQUIRE=None;SCRATCH=SP-20
sha=lambda b:hashlib.sha256(b).hexdigest()
class Script:
 def __init__(self,snapshot,case,fail=None):
  self.memory=bytearray(snapshot);self.case=case;self.trace=[];self.fail=fail;self.fail_call=None;self.changed=[];self.queues={};self.contexts=[]
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
  if a in [0x1ae88,0x1ac68]:
   sp=e.reg_read(UC_M68K_REG_A7);script.trace.append(['call',a,[int.from_bytes(e.mem_read(sp+4,2),'big')],e.reg_read(UC_M68K_REG_D0)]);script.contexts.append('call')
  if a in HELPERS:
   sp=e.reg_read(UC_M68K_REG_A7);args=[int.from_bytes(e.mem_read(sp+4+i*4,4),'big')for i in range(5)];assert args[2]==SCRATCH;value=script.call(a,args,e.reg_read(UC_M68K_REG_D0))
   for addr,size,v in script.changed:e.mem_write(addr,v.to_bytes(size,'big'))
   e.reg_write(UC_M68K_REG_D0,value);script.contexts.append('call');return
  assert 0x10a6a<=a<=0x10ba2 or 0x1ae88<=a<=0x1aed8 or 0x1ac68<=a<=0x1ae54,hex(a);coverage.add(a)
 def read(e,t,a,width,value,_):
  if SP-0x1000<=a<SP+6 and not (SCRATCH<=a<SCRATCH+4 and 0x1ac68<=e.reg_read(UC_M68K_REG_PC)<=0x1ae54):return
  e.mem_write(a,script.read(a,width).to_bytes(width,'big'));script.contexts.append('release'if 0x1ae88<=e.reg_read(UC_M68K_REG_PC)<=0x1aed8 else('acquire'if 0x1ac68<=e.reg_read(UC_M68K_REG_PC)<=0x1ae54 else'selector'))
 def write(e,t,a,width,value,_):
  if SP-0x1000<=a<SP+6 and not (SCRATCH<=a<SCRATCH+4 and 0x1ac68<=e.reg_read(UC_M68K_REG_PC)<=0x1ae54):return
  script.write(a,width,value&((1<<(8*width))-1));script.contexts.append('release'if 0x1ae88<=e.reg_read(UC_M68K_REG_PC)<=0x1aed8 else('acquire'if 0x1ac68<=e.reg_read(UC_M68K_REG_PC)<=0x1ae54 else'selector'))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(0x10a6a,STOP,count=20000,timeout=2000000);assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
 memory=bytearray(cpu.mem_read(0,0x200000))
 for target in HELPERS:memory[target:target+2]=script.memory[target:target+2]
 for q in case.get('read_queues',[]):a=q['address'];memory[a:a+q['width']]=script.memory[a:a+q['width']]
 assert memory[:SP-0x1000]==script.memory[:SP-0x1000]and memory[SP+6:]==script.memory[SP+6:]and (not any(x[0]=='w'and x[1]==SCRATCH for x in script.trace)or memory[SCRATCH:SCRATCH+4]==script.memory[SCRATCH:SCRATCH+4]);return cpu.reg_read(UC_M68K_REG_D0)
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
   assert target in ENTRIES and count==(5 if target==0x1b044 else 1)
   if target==0x1ae88:
    if script.fail_call==target or script.fail==len(script.trace):raise RuntimeError('Injected realrelease entry failure')
    script.trace.append(['call',target,list(args[:count]),out[0]]);value=c.c_uint32(out[0]);status=RELEASE(c.byref(bus),args[0],out[0],c.byref(value))
    if not status:out[0]=value.value
    return status
   if target==0x1ac68:
    if script.fail_call==target or script.fail==len(script.trace):raise RuntimeError('Injected real acquisition entry failure')
    script.trace.append(['call',target,list(args[:count]),out[0]]);value=c.c_uint32(out[0]);status=ACQUIRE(c.byref(bus),args[0],SCRATCH,c.byref(value))
    if not status:out[0]=value.value
    return status
   out[0]=script.call(target,list(args[:count]),out[0]);return 0
  except Exception as error:errors.append(repr(error));return 1
 cb=[w.R8(),w.R16(read(2)),w.R32(read(4)),w.W16(write(2)),w.W32(write(4)),w.CALL(call)]
 if missing is not None:cb[missing]=type(cb[missing])()
 bus=w.Bus(*cb,None,500);out=c.c_uint32(0xa55aa55a);status=fn(None if nullbus else c.byref(bus),case['id_word'],case['incoming'][0],None if nullout else c.byref(out));return status,out.value,errors
def fixtures():
 snapshot,resource_cases=acquire.fixtures();cases=[]
 for i,resource in enumerate(resource_cases):
  case=json.loads(json.dumps(resource));id_word=[1,2,0,255][i%4];base=0x3d822+id_word*146
  # Selector shifts the descriptor asset word by four before acquisition.
  # Preserve the standalone modes/counts/cache patterns but use reachable IDs.
  acquired=(resource['id_word']+15)&0xfff0
  if resource['adjusted_word']==0x8000:acquired=0x8000
  bias=[x[2]for x in case['initial']if x[:2]==[0x464c8+max(1,min(3,resource['mode_word']))*2,2]][0]
  if resource['pattern']==0:
   for row in case['initial']:
    if 0x15b4a0<=row[0]<0x15b530 and (row[0]-0x15b4a0)%4==0:
     j=(row[0]-0x15b4a0)//4
     if j>=resource['reserved_word']:row[2]=(acquired+j-resource['reserved_word'])&65535
  case.update(id_word=id_word,tag=0,frame_word=resource['reserved_word'],resource_id=acquired)
  case['initial']=[row for row in case['initial']if row[0]!=acquire.SCRATCH]
  case['initial']+=[[SCRATCH,4,0x77223344],[0x403d8,2,[0xffff,0,1,0x8000][i%4]],
                   [0x403da,2,0],[0x400e6,4,base],[0x23f88,4,0x12345678],
                   [base,2,0],[base+2,2,acquired>>4],[base+0x90,2,17],[base+0x8e,2,23],
                   [0x90000+0x90,2,31],[0x90000+0x8e,2,47]]
  for j in range(36,48):case['initial'].append([0x4674c+j*8,4,0x1134a0+j*8192])
  # Count-zero existing-cache hit must remain a hit after descriptor quantization.
  if resource['count_word']==0:
   case['initial']+=[[0x464c8+6,2,0],[0x15b4a0,2,acquired]]
  case['helper_returns']={str(0x1b044):resource['loader_return']}
  case['helper_effects']={str(0x1b044):[[SCRATCH,4,0x8899aabb],[0x15b532,2,31],[0x400e6,4,0x90000]]}
  # Negative-count standalone case uses a queued second index; retained.
  cases.append(case)
 for id_word,tag in [(0xffff,0),(1,1),(1,2),(1,0x8000),(1,0xffff)]:
  case=json.loads(json.dumps(cases[0]));case.update(id_word=id_word,tag=tag)
  if id_word!=0xffff:case['initial']+=[[0x3d822+id_word*146,2,tag]]
  cases.append(case)
 return snapshot,cases
def bind(source,out):
 global RELEASE,ACQUIRE
 restore=ROOT/'projects/black-ice-white-noise/restoration';assert sha((restore/'biwn_frame_resource_acquire.c').read_bytes())==json.loads((ROOT/'verification/local-frame-resource-acquire-checks-current.json').read_text())['source_sha256'];assert sha((restore/'biwn_frame_reference_release.c').read_bytes())==json.loads((ROOT/'verification/local-frame-reference-release-checks-current.json').read_text())['source_sha256'];process=subprocess.run(['clang','-std=c99','-I',str(source.parent),'-I',str(restore),'-fsyntax-only','-Xclang','-ast-dump=json',str(source)],capture_output=True,text=True);(out/'syntax.log').write_text(process.stderr);assert process.returncode==0,process.stderr;tree=json.loads(process.stdout);functions=[n for n in tree['inner']if n['kind']=='FunctionDecl'and any(x.get('kind')=='CompoundStmt'for x in n.get('inner',[]))];names={n['name']for n in functions};assert 'biwn_scene_select'in names and all(n['name']=='biwn_scene_select'or n.get('storageClass')=='static'for n in functions);assert not any(n['kind']in ['VarDecl','FileScopeAsmDecl']for n in tree['inner'])
 def check(n):
  if not n:return
  assert n['kind']not in ['GCCAsmStmt','MSAsmStmt'];assert n.get('castKind')not in ['IntegralToPointer','PointerToIntegral','BitCast']
  if n['kind']=='CallExpr':
   target=n['inner'][0]
   while target['kind']in ['ImplicitCastExpr','ParenExpr']:target=target['inner'][0]
   assert(target['kind']=='MemberExpr'and target['name']in ['read16','read32','write16','write32','call'])or(target['kind']=='DeclRefExpr'and target['referencedDecl']['name']in names)
  for child in n.get('inner',[]):check(child)
 for f in functions:check(f)
 library=out/'libscene-select.dylib';built=subprocess.run(['clang','-std=c99','-dynamiclib','-O2','-Wall','-Wextra','-Werror','-I',str(source.parent),'-I',str(restore),str(source),str(restore/'biwn_frame_reference_release.c'),str(restore/'biwn_frame_resource_acquire.c'),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(built.stdout+built.stderr);assert not built.returncode,built.stderr;lib=c.CDLL(str(library));RELEASE=lib.biwn_frame_reference_release;RELEASE.argtypes=[c.POINTER(w.Bus),c.c_uint16,c.c_uint32,c.POINTER(c.c_uint32)];RELEASE.restype=c.c_int;ACQUIRE=lib.biwn_frame_resource_acquire;ACQUIRE.argtypes=[c.POINTER(w.Bus),c.c_uint16,c.c_uint32,c.POINTER(c.c_uint32)];ACQUIRE.restype=c.c_int;fn=lib.biwn_scene_select;fn.argtypes=[c.POINTER(w.Bus),c.c_uint16,c.c_uint32,c.POINTER(c.c_uint32)];fn.restype=c.c_int;return fn
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--original-only',action='store_true');opt=ap.parse_args();out=ROOT/'verification/local-scene-select-resources'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);fn=None;source=None
 if not opt.original_only:source=Path(json.loads((ROOT/'verification/local-scene-select-author-current.json').read_text())['directory'])/'biwn_scene_select.c';fn=bind(source,out)
 snapshot,cases=fixtures();coverage=set();rows=[]
 for i,case in enumerate(cases):
  a=Script(snapshot,case);value=original(a,case,coverage)
  if fn:
   b=Script(snapshot,case);status,actual,errors=translated(fn,b,case)
   if status or errors or actual!=value or a.trace!=b.trace or a.memory!=b.memory:
    (out/'mismatch.json').write_text(json.dumps(dict(case=i,parameters=case,status=status,expected=value,actual=actual,original_trace=a.trace,C_trace=b.trace,errors=errors),indent=2)+'\n');raise AssertionError(out/'mismatch.json')
  rows.append(dict(case=i,id_word=case['id_word'],tag=case['tag'],frame_word=case['frame_word'],full_D0=value,trace_events=len(a.trace),trace_sha256=sha(json.dumps(a.trace).encode()),RAM_sha256=sha(a.memory)))
 evidence=json.loads((ROOT/'verification/scene-selector-evidence-current.json').read_text());expected={int(x,16)for x in re.findall(r'^([0-9a-fA-F]+):',json.loads((Path(evidence['directory'])/'evidence.json').read_text())['assembly'],re.M)};assert len(expected)==65 and expected<=coverage ,(expected-coverage,coverage-expected);guards=[];native=[];core_path=None
 if fn:
  for opts in [dict(missing=i)for i in [1,2,3,4,5]]+[dict(nullbus=True),dict(nullout=True)]:
   b=Script(snapshot,cases[0]);status,value,errors=translated(fn,b,cases[0],**opts);assert status==1 and value==0xa55aa55a and not b.trace;guards.append(opts)
  case=next(x for x in cases if x['mode_word']==3 and x['count_word']==2 and x['pattern']==1 and x['reserved_word']==0 and x['resource_id']>=300);a=Script(snapshot,case);original(a,case,set())
  for i,event in enumerate(a.trace):
   b=Script(snapshot,case,fail=i);status,value,errors=translated(fn,b,case);assert status==(3 if event[0]=='call'or a.contexts[i]in ['release','acquire']else 2)and value==0xa55aa55a and b.trace==a.trace[:i],(i,event,status,value);guards.append(dict(failed_event=i,kind=event[0],prior_effects_retained=True))
  core_path=Path(json.loads((ROOT/'verification/DSP-music-context-experimental-candidate.json').read_text())['core_path']);oracle=media.scheduler.Native(diagnostic_core=core_path);runtime=media.Runtime.__new__(media.Runtime);runtime.oracle,runtime.device,runtime.core=oracle,oracle.device,oracle.lib;writers={}
  for width in [2,4]:
   wr=getattr(runtime.core,'m68k_write_memory_'+str(width*8));wr.argtypes=[c.c_uint32,c.c_uint32];wr.restype=None;writers[width]=wr
  try:
   chosen=[x for x in cases if x['mode_word']==3 and x['count_word']in [1,2,36]and not x.get('read_queues')][::4][:25]
   for case in chosen:
    left=Script(snapshot,case);status,value,errors=translated(fn,left,case);right=Script(snapshot,case);memory=bytearray(right.memory);memory[SP:SP+6]=STOP.to_bytes(4,'big')+case['id_word'].to_bytes(2,'big')
    for target in HELPERS:memory[target:target+2]=b'\x4e\x75'
    cpu=media.CPU();cpu.registers[:15]=case['incoming'];cpu.registers[15]=SP;cpu.pc=0x10a6a;cpu.sr=0x2000;cpu.usp=0x180000;cpu.ssp=SP;runtime.device.seed(bytes(memory),0);runtime.seed_cpu(cpu);steps=0
    while runtime.cpu().pc!=STOP and steps<20000:
     state=runtime.cpu()
     if state.pc in HELPERS:
      ram=runtime.device.ram();args=[int.from_bytes(ram[state.registers[15]+4+j*4:state.registers[15]+8+j*4],'big')for j in range(5)];assert args[2]==SCRATCH;state.registers[0]=right.call(state.pc,args,state.registers[0])
      for a,width,v in right.changed:writers[width](a,v)
      runtime.seed_cpu(state)
     runtime.core.m68k_execute(1);steps+=1
    actual=runtime.cpu();ram=bytearray(runtime.device.ram())
    for target in HELPERS:ram[target:target+2]=left.memory[target:target+2]
    assert not status and not errors and actual.pc==STOP and actual.registers[15]==SP+4 and actual.registers[0]==value and ram[:SP-0x1000]==left.memory[:SP-0x1000]and ram[SP+6:]==left.memory[SP+6:]and (not any(x[0]=='w'and x[1]==SCRATCH for x in left.trace)or ram[SCRATCH:SCRATCH+4]==left.memory[SCRATCH:SCRATCH+4])
    native.append(dict(id_word=case['id_word'],tag=case['tag'],frame_word=case['frame_word'],full_D0=value,steps=steps))
  finally:oracle.close()
 (out/'fixtures.json').write_text(json.dumps(cases,indent=2)+'\n');(out/'case-results.json').write_text(json.dumps(rows,indent=2)+'\n');report=dict(status='scene_select_real_resources_original_preflight_pass'if opt.original_only else'local_scene_select_real_resources_original_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),source=str(source)if source else None,source_sha256=sha(source.read_bytes())if source else None,cases=len(rows),selector_instruction_address_coverage=[65,65],linked_instruction_addresses=len(coverage),release_instruction_addresses=sorted(x for x in coverage if 0x1ae88<=x<=0x1aed8),release_source_sha256=sha((ROOT/'projects/black-ice-white-noise/restoration/biwn_frame_reference_release.c').read_bytes())if fn else None,guards=guards,pinned_native_cases=native,core_path=str(core_path)if core_path else None,core_sha256=sha(core_path.read_bytes())if core_path else None,acquire_instruction_addresses=sorted(x for x in coverage if 0x1ac68<=x<=0x1ae54),acquire_source_sha256=sha((ROOT/'projects/black-ice-white-noise/restoration/biwn_frame_resource_acquire.c').read_bytes())if fn else None,guest_scratch=hex(SCRATCH),remaining_scripted_helpers=[hex(x)for x in HELPERS],new_training=False,native_Chat_verified=False,natural_gameplay_integration_verified=False,full_route_runtime_promoted=False,scope='Complete10A6A..10BA2 fullD0,logicalordereddata/helpertrace and2MBRAM against originalUnicornM68000,plus selected pinnednativeCPU finalD0/externalRAM. ID sentinel, unsigned tags, reachable descriptor IDs, mode/count/cache patterns, full D0 and queued reserved-index rereads checked. Broader signed frame-index and repeated selector-global cases remain in the separate isolated-selector proof. Actual1AE88 release and1AC68 acquisition execute inside selector; only1B044 diskloader remains explicit RAM/D0fixture. Guest scratch SP-20 is exposed only during acquisition and checked after modeled writes; release reuses overlapping private frame bytes which are excluded. Untouched scratch and other privateframes excluded. Queued-read writes into oracleRAM are normalized only atdeclared queuedranges; authoritative logicalRAM is the modeled bus. Privateframes/CCR/otherregs,nativebusdummyreads,unmapped exceptions,physicaltiming and naturalgameplay excluded.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification'/('local-scene-select-resources-'+('preflight'if opt.original_only else'checks-current')+'.json')).write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(rows),len(coverage),'native',len(native),'guards',len(guards),flush=True)
if __name__=='__main__':main()
