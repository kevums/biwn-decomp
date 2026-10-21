"""Original resource callers vs C using real disc bytes and checked memory kernels."""
import argparse,ctypes as c,json,random,subprocess,os,hashlib
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_resources as resources
import check_biwn_memory as memory
import check_biwn_memory_native as prior
from biwn_disc_backend import Disc
ROOT=resources.ROOT;world=resources.world;SP=resources.SP;STOP=resources.STOP;SCRATCH=resources.SCRATCH
STUBS=[0x303c,0x3042,0xdf60,0xdf8c,0xdf9c]
WIDTHS={**resources.WIDTHS,0x15200:[]}
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
def get(r,a,w=4):return int.from_bytes(r[a:a+w],'big')
def masked(r):
 out=bytearray(r);out[SP-0x1000:SP+32]=bytes(0x1000+32);return bytes(out)
class Position(c.Structure):_fields_=[('packed',c.c_uint32),('toc_offset',c.c_uint32)]
class Runtime(prior.Runtime):
 def __init__(self,lib):
  super().__init__(lib);self.resources=resources.bind(self.lib);self.disc=Disc();self.free=self.lib.biwn_cleanup_free_handle;self.free.argtypes=[c.POINTER(world.Bus),c.c_uint32,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];self.free.restype=c.c_int
  self.cd=self.lib.biwn_cd_offset_msf;self.cd.argtypes=[c.c_uint32,c.c_uint32,c.c_void_p,c.c_size_t,c.POINTER(Position)];self.cd.restype=c.c_int
 def bulk(self,address,data):c.memmove(self.device.pointer+address,data,len(data))
 def native(self,ram,case,coverage):
  self.seed(ram);self.disc.reset()
  for target in STUBS:self.device.direct(target,2,0x4e75)
  self.core.m68k_pulse_reset();self.core.m68k_set_irq(0);self.core.m68k_set_reg(17,0x2000)
  for i,value in enumerate(case['incoming']):self.core.m68k_set_reg(i,value)
  self.core.m68k_set_reg(15,SP);self.core.m68k_set_reg(16,case['entry']);self.device.direct(SP,4,STOP)
  if 'params'in case:
   assert case['entry']==0x1b044 and len(case['params'])==5
   self.bulk(SP+4,b''.join(value.to_bytes(4,'big')for value in case['params']))
  else:self.device.direct(SP+4,2,case['id'])
  calls=[];steps=[]
  for _ in range(250000):
   pc=self.core.m68k_get_reg(None,16)
   if pc==STOP:break
   assert any(lo<=pc<hi for lo,hi in resources.RANGES.items())or any(lo<=pc<hi for lo,hi in memory.RANGES.items())or 0x1545c<=pc<0x1557a or 0xd1e0<=pc<0xd2a0 or 0xd2f0<=pc<0xd30a or pc in STUBS,hex(pc)
   coverage.add(pc);steps.append(pc)
   if pc in WIDTHS and pc!=case['entry']:
    stack=self.core.m68k_get_reg(None,15);args=[];offset=4
    for width in WIDTHS[pc]:args.append(int.from_bytes(c.string_at(self.device.pointer+stack+offset,width),'big'));offset+=width
    calls.append(['call',pc,args])
   if pc==0x303c:self.disc.start(self.core.m68k_get_reg(None,8),self.core.m68k_get_reg(None,9),self.core.m68k_get_reg(None,0))
   elif pc==0x3042:self.disc.stop()
   elif pc==0xdf60:self.disc.tick(self.bulk,lambda a,v:self.device.direct(a,4,v))
   elif pc in[0xdf8c,0xdf9c]:raise AssertionError('Unexpected ready-wait/wake; standalone checks cover these scripted boundaries')
   self.core.m68k_execute(1)
  else:raise AssertionError('Native resource caller did not return')
  assert self.core.m68k_get_reg(None,15)==SP+4
  for i,value in enumerate(case['incoming']):
   if i not in[0,1,8,9]:assert self.core.m68k_get_reg(None,i)==value
  for target in STUBS:self.device.direct(target,2,get(ram,target,2))
  return self.device.ram(),self.core.m68k_get_reg(None,0),{'calls':calls,'instructions':len(steps),'disc_requests':list(self.disc.requests),'disc_completions':list(self.disc.completions),'disc_stops':self.disc.stops,'hardware':self.hardware(),'device':self.device.stats()}
 def translated(self,ram,case):
  self.seed(ram);self.disc.reset();alloc,compact,copy=self.functions;calls=[];errors=[]
  def call(_,target,args,n,out):
   try:
    values=list(args[:n]);calls.append(['call',target,values])
    if target==0x152a2:return alloc(c.byref(bus),values[0],4096,out)
    if target==0x15200:return compact(c.byref(bus),4096,out)
    if target==0xe3e0:return copy(c.byref(bus),self.device.write8,target,*values,out[0],4096,out)
    if target==0x1545c:return self.free(c.byref(bus),values[0],out[0],4096,out)
    if target==0x1b044:return self.resources[target](c.byref(bus),*values,32768,out)
    if target==0xd206:
     toc=c.create_string_buffer(c.string_at(self.device.pointer+0x2c00,256));position=Position();status=self.cd(*values,toc,256,c.byref(position))
     if not status:out[0]=position.packed
     return status
    if target==0xd2f0:self.disc.start(*values);out[0]=values[2];return 0
    if target==0xd306:self.disc.stop();return 0
    if target==0xdf60:self.disc.tick(self.bulk,lambda a,v:self.device.direct(a,4,v));return 0
    raise AssertionError(hex(target))
   except Exception as error:errors.append(repr(error));return 1
  callback=world.CALL(call);bus=world.Bus(self.device.r8,self.device.r16,self.device.r32,self.device.w16,self.device.w32,callback,None,0);out=c.c_uint32(0xa55aa55a)
  if case['entry']==0x1b044:status=self.resources[case['entry']](c.byref(bus),*case['params'],case.get('work_budget',32768),c.byref(out))
  elif case['entry']==0x1aa40:status=self.resources[case['entry']](c.byref(bus),case['id'],SCRATCH,c.byref(out))
  else:status=self.resources[case['entry']](c.byref(bus),case['id'],32768,c.byref(out))
  if not case.get('allow_host_error'):assert status==0 and not errors,(status,errors)
  return self.device.ram(),out.value,{'status':status,'errors':errors,'calls':calls,'disc_requests':list(self.disc.requests),'disc_completions':list(self.disc.completions),'disc_stops':self.disc.stops,'hardware':self.hardware(),'device':self.device.stats()}
def seed(snapshot):
 ram=bytearray(snapshot)
 for i in range(50):
  for offset,width,value in[(0,2,0xffff),(6,2,0),(8,2,0),(10,2,0)]:a=0x15b534+i*12+offset;ram[a:a+width]=value.to_bytes(width,'big')
 ram[0x47b80:0x47b84]=bytes(4);return bytes(ram)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opts=ap.parse_args();out=ROOT/'verification/biwn-resources-native'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_resources.c','biwn_memory.c','biwn_transition_cleanup.c','biwn_cd_math.c'];lib=out/'libresources-native.dylib';subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(source/n)for n in names]+['-o',str(lib)],check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});runtime=Runtime(lib);manifest,snapshot=prior.prior.render.assets();disc_manifest=runtime.disc.manifest;resource_map={r['resource_id']:r for r in disc_manifest['resources']};rng=random.Random(0x1b044);rows=[];coverage=set();saved={};vectors=[{'entry':0x1af04,'id':i,'phase':'load'}for i in range(53)]+[{'entry':0x1aa40,'id':1,'phase':'texture'}]+[{'entry':entry,'id':i,'phase':phase}for i in [0,1,47]for entry,phase in [(0x1af04,'reuse'),(0x1b002,'release_one'),(0x1b002,'release_two'),(0x1af04,'reload')]]
 if opts.limit:vectors=vectors[:opts.limit]
 try:
  for ordinal,case in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':ordinal,'id':case['id'],'phase':case['phase']});case={**case,'incoming':[rng.getrandbits(32)for _ in world.REGS]};ram=seed(snapshot)if case['phase']in['load','texture']else saved[case['id']];left,expected,original=runtime.native(ram,case,coverage);right,d0,rebuilt=runtime.translated(ram,case)
   if masked(left)!=masked(right)or d0!=expected or any(original[k]!=rebuilt[k]for k in ['calls','disc_requests','disc_completions','disc_stops','hardware']):
    save(out/'mismatch.json',{'case':case,'original_D0':expected,'C_D0':d0,'original':original,'rebuilt':rebuilt,'RAM_differences':[hex(i)for i,(a,b)in enumerate(zip(masked(left),masked(right)))if a!=b][:32]});raise AssertionError(str(out/'mismatch.json'))
   resource=resource_map.get(case['id']);payload_pointer=None;payload_sha=None
   if case['entry']==0x1af04 and resource:
    assert d0;payload_pointer=get(right,d0);payload=right[payload_pointer:payload_pointer+resource['bytes']];payload_sha=hashlib.sha256(payload).hexdigest();assert payload_sha==resource['payload_sha256']
   elif case['entry']==0x1af04:assert d0==0 and not rebuilt['disc_requests']
   if case['phase']=='reuse':assert not rebuilt['disc_requests'] and get(right,0x15b53a,2)==2
   if case['phase']=='release_one':assert not rebuilt['disc_requests'] and get(right,0x15b53a,2)==1
   if case['phase']=='release_two':assert not rebuilt['disc_requests'] and get(right,0x15b53a,2)==0 and get(right,0x15b534,2)==0xffff
   if case['phase']=='reload':assert len(rebuilt['disc_requests'])==1 and get(right,0x15b53a,2)==1
   if case['phase']=='texture':assert hashlib.sha256(right[0x1134a0:0x1134a0+0x1e000]).hexdigest()==disc_manifest['textures']['payload_sha256']
   assert not rebuilt['device']['original_GPUExec1_calls']and not rebuilt['device']['game_frames_executed'];
   if case['phase']!='texture':saved[case['id']]=right
   rows.append({'case':ordinal,'parameters':case,'full_D0':d0,'payload_pointer':payload_pointer,'payload_sha256':payload_sha,'original':original,'rebuilt':rebuilt,'visible_RAM_disc_bytes_calls_hardware_and_return_match':True})
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
 finally:runtime.close()
 save(out/'fixtures.json',rows)
 if opts.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'directory':str(out),'cases':len(rows)}));return
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'resource_callers_load_actual_disc_payloads_match_native_CPU_C','directory':str(out),'cases':len(rows),'active_models_full_payload_checked':50,'inactive_ids_return_zero':3,'texture_payload_bytes':0x1e000,'reuse_release_reload_sequences':3,'disc_read_requests':sum(len(r['rebuilt']['disc_requests'])for r in rows),'disc_completion_ticks':sum(len(r['rebuilt']['disc_completions'])for r in rows),'C_blitter_commands':sum(r['rebuilt']['device']['blit_commands']for r in rows),'scripted_game_resource_or_memory_bodies':0,'BIOS_IO_device_adapters':['0x303c/CD_read','0x3042/CD_stop'],'yield_completion_boundary':'DF60 is an explicit completion tick/RTS adapter; no real task-context switch in this proof.','source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in names+[n.replace('.c','.h')for n in names]},'asset_sha256':manifest['assets'],'source_disc_report':str(ROOT/'verification/biwn-disc-resources.json'),'matched':['Original native CPU executes resource/cache/texture/loader callers plus allocator/free/compactor/copy/CD-position helpers; C uses checked corresponding bodies. Real normalized disc bytes, complete payload hashes, calls/args/order, fullD0/callee saves, visible2MBRAM and seven blitter registers match.','All50active model payloads,3missing IDs,complete122880byteRTXT texture payload andthree acquire/reuse/release/release/reload sequences pass. No captured model handle is substituted in these tests.'],'limits':['BIOS transfer/stop andcompletion timing are host device adapters. One completion tick occurs at aDF60yield boundary; scheduler continuations, reference wait/wake signaling, physicalCD/BIOS timing andwholegame remain unverified.','Stream phase674 is image-specific, supported by a32768byteoriginal-capture match; not a universalCDdriver. Frozen code/TOC andpreinitializedheap arefixtures.','Private stack/texture scratch,CCR andothercaller-savedregisters excluded. Original/C share thepinnedemulatedblitter. Nofullworld/render/tasklifecycle orcompletegameframe proof.']}
 save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-resources-native-checks.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
