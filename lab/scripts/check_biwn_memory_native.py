"""Real native allocator/compactor/blitter-copy versus C with pinned hardware."""
import argparse,ctypes as c,json,random,os,subprocess,hashlib
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_memory as checks
import check_biwn_render_display_runtime as prior
ROOT=checks.ROOT;SP=checks.SP;STOP=checks.STOP;world=checks.world
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
def masked(data):
 out=bytearray(data);out[SP-0x1000:SP+20]=bytes(0x1000+20);return bytes(out)
class Runtime(prior.Runtime):
 def __init__(self,library):
  # Only the already-pinned device/core are needed; no render library API.
  self.device=prior.render.Runtime();self.core=c.CDLL(str(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'));self.lib=c.CDLL(str(library));self.functions=checks.bind(self.lib)
  self.core.m68k_set_reg.argtypes=[c.c_int,c.c_uint32];self.core.m68k_get_reg.argtypes=[c.c_void_p,c.c_int];self.core.m68k_get_reg.restype=c.c_uint32;self.core.m68k_execute.argtypes=[c.c_int];self.core.m68k_execute.restype=c.c_int;self.core.m68k_set_irq.argtypes=[c.c_uint32]
 def hardware(self):return [self.device.read(a,4)for a in[0xf02200,0xf02204,0xf0220c,0xf02224,0xf02228,0xf02230,0xf0223c]]
 def seed(self,ram):
  self.device.seed(ram,1)
  for address in range(0xf02200,0xf022a0,4):
   if address!=0xf02238:self.device.write(address,4,0)
 def native(self,ram,case,coverage):
  self.seed(ram);self.core.m68k_pulse_reset();self.core.m68k_set_irq(0);self.core.m68k_set_reg(17,0x2000)
  for i,v in enumerate(case['incoming']):self.core.m68k_set_reg(i,v)
  self.core.m68k_set_reg(15,SP);self.core.m68k_set_reg(16,case['entry']);self.device.direct(SP,4,STOP)
  for i,value in enumerate(case['params']):self.device.direct(SP+4+i*4,4,value)
  calls=[];steps=[]
  for _ in range(50000):
   pc=self.core.m68k_get_reg(None,16)
   if pc==STOP:break
   assert any(lo<=pc<hi for lo,hi in checks.RANGES.items()),hex(pc);coverage.add(pc);steps.append(pc)
   if pc in[0x15200,0xe3e0]and pc!=case['entry']:
    sp=self.core.m68k_get_reg(None,15);args=[int.from_bytes(c.string_at(self.device.pointer+sp+4+i*4,4),'big')for i in range(3 if pc==0xe3e0 else 0)];calls.append(['call',pc,args])
   self.core.m68k_execute(1)
  else:raise AssertionError('Native memory routine did not return')
  assert self.core.m68k_get_reg(None,15)==SP+4
  for i,v in enumerate(case['incoming']):
   if i not in[0,1,8,9]:assert self.core.m68k_get_reg(None,i)==v
  return self.device.ram(),self.core.m68k_get_reg(None,0),{'calls':calls,'instructions':len(steps),'hardware':self.hardware(),'device':self.device.stats()}
 def translated(self,ram,case):
  self.seed(ram);alloc,compact,copy=self.functions;calls=[];errors=[]
  def call(_,target,args,n,out):
   try:
    values=list(args[:n]);calls.append(['call',target,values])
    if target==0x15200:assert not n;return compact(c.byref(bus),4096,out)
    assert target==0xe3e0 and n==3;return copy(c.byref(bus),self.device.write8,target,*values,out[0],4096,out)
   except Exception as error:errors.append(repr(error));return 1
  callback=world.CALL(call);bus=world.Bus(self.device.r8,self.device.r16,self.device.r32,self.device.w16,self.device.w32,callback,None,0);out=c.c_uint32(0xa55aa55a)
  if case['entry']==0x152a2:status=alloc(c.byref(bus),case['params'][0],4096,c.byref(out))
  elif case['entry']==0x15200:status=compact(c.byref(bus),4096,c.byref(out))
  else:status=copy(c.byref(bus),self.device.write8,case['entry'],*case['params'],case['incoming'][0],4096,c.byref(out))
  assert status==0 and not errors,(status,errors)
  return self.device.ram(),out.value,{'calls':calls,'hardware':self.hardware(),'device':self.device.stats()}
 def close(self):self.device.close()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opts=ap.parse_args();out=ROOT/'verification/biwn-memory-native'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';lib=out/'libmemory.dylib';subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_memory.c'),'-o',str(lib)],check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});manifest,snapshot=prior.render.assets();all_cases=checks.cases();vectors=[]
 for entry,count in [(0x152a2,320),(0x15200,80),(0xe3e0,128),(0xe3ee,128)]:vectors.extend([case for case in all_cases if case['entry']==entry][:opts.limit if opts.limit else count])
 runtime=Runtime(lib);rows=[];coverage=set()
 try:
  for i,case in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':i,'entry':hex(case['entry'])});script=checks.Script(snapshot,case);ram=bytes(script.memory)
   # Controlled rereads are covered in Unicorn; this native proof uses stable RAM.
   case={**case,'read_queues':[]};left,expected,original=runtime.native(ram,case,coverage);right,d0,rebuilt=runtime.translated(ram,case)
   if masked(left)!=masked(right)or expected!=d0 or original['calls']!=rebuilt['calls']or original['hardware']!=rebuilt['hardware']:
    differences=[hex(a)for a,(x,y)in enumerate(zip(masked(left),masked(right)))if x!=y][:32];save(out/'mismatch.json',{'case':i,'parameters':case,'original_D0':expected,'C_D0':d0,'original':original,'rebuilt':rebuilt,'RAM_differences':differences});raise AssertionError(str(out/'mismatch.json'))
   assert not rebuilt['device']['original_GPUExec1_calls']and not rebuilt['device']['game_frames_executed']
   rows.append({'case':i,'parameters':case,'full_D0':d0,'native_original':original,'rebuilt':rebuilt,'visible_RAM_hardware_and_calls_match':True})
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
 finally:runtime.close()
 save(out/'fixtures.json',rows)
 if opts.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'directory':str(out),'cases':len(rows)}));return
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'memory_management_and_full_copy_match_native_CPU_blitter_C','directory':str(out),'cases':len(rows),'allocator_cases':320,'compactor_cases':80,'copy_cases':256,'original_CPU_instruction_starts_observed':len(coverage),'C_blitter_commands':sum(r['rebuilt']['device']['blit_commands']for r in rows),'compaction_calls':sum(sum(call[1]==0x15200 for call in r['rebuilt']['calls'])for r in rows),'copy_dependency_calls':sum(sum(call[1]==0xe3e0 for call in r['rebuilt']['calls'])for r in rows),'nested_scripted_helpers':0,'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in ['biwn_memory.c','biwn_memory.h']},'asset_sha256':manifest['assets'],'matched':['Original native CPU executes allocator, compactor and E3E0/E3EE copy with actual pinned emulated blitter; C uses corresponding real kernels and same device backend, no source CPU/GPU instructions.','Full visible 2MB RAM after private stack exclusion, full D0/callee saves, nested call args/order and seven blitter registers match. Includes actual allocation, compaction/relocation, small overlap copies and large/odd/chunked device copies.'],'limits':['Finite supplied block/free-list/handle fixtures and stable RAM; not full resource loading or game startup. Controlled rereads are separately checked in Unicorn.','Private CPU stack, CCR and other caller-saved registers excluded. Pinned blitter is shared emulated hardware, not an independently rebuilt device or physical timing proof. Raw huge count prefixes are covered separately, not full native returns.']}
 save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-memory-native-checks.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
