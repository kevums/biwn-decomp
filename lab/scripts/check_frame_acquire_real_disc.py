"""Real-disc frame acquisition linked to existing source loader/copy/CD math."""
import ctypes as c,json,hashlib,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_resources_native as native
resources=native.resources;resources.RANGES[0x1ac68]=0x1ae56
memory=native.memory;world=native.world;ROOT=native.ROOT;SP=native.SP;STOP=native.STOP;SCRATCH=SP-8
STUBS=native.STUBS;WIDTHS={**native.WIDTHS,0x1ac68:[2]};Position=native.Position
class OriginalRetry(RuntimeError):pass
Disc=native.Disc;get=native.get;masked=native.masked;save=native.save
class Runtime(native.prior.Runtime):
 def __init__(self,lib):
  super().__init__(lib);self.acquisition=self.lib.biwn_frame_resource_acquire;self.acquisition.argtypes=[c.POINTER(world.Bus),c.c_uint16,c.c_uint32,c.POINTER(c.c_uint32)];self.acquisition.restype=c.c_int;self.resources=resources.bind(self.lib);self.disc=Disc();self.free=self.lib.biwn_cleanup_free_handle;self.free.argtypes=[c.POINTER(world.Bus),c.c_uint32,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];self.free.restype=c.c_int
  self.cd=self.lib.biwn_cd_offset_msf;self.cd.argtypes=[c.c_uint32,c.c_uint32,c.c_void_p,c.c_size_t,c.POINTER(Position)];self.cd.restype=c.c_int
 def bulk(self,address,data):c.memmove(self.device.pointer+address,data,len(data))
 def native(self,ram,case,coverage):
  self.seed(ram);self.disc.reset()
  for target in STUBS:self.device.direct(target,2,0x4e75)
  self.core.m68k_pulse_reset();self.core.m68k_set_irq(0);self.core.m68k_set_reg(17,0x2000)
  for i,value in enumerate(case['incoming']):self.core.m68k_set_reg(i,value)
  self.core.m68k_set_reg(15,SP);self.core.m68k_set_reg(16,case['entry']);self.device.direct(SP,4,STOP);self.device.direct(SP+4,2,case['id']);calls=[];steps=[]
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
  else:
   self.failure=dict(pc=hex(self.core.m68k_get_reg(None,16)),steps=len(steps),disc_requests=list(self.disc.requests),disc_completions=list(self.disc.completions),calls=calls[-20:]);raise OriginalRetry('Original loader did not return within250000 instructions')
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
  callback=world.CALL(call);bus=world.Bus(self.device.r8,self.device.r16,self.device.r32,self.device.w16,self.device.w32,callback,None,32768);out=c.c_uint32(0xa55aa55a)
  if case['entry']==0x1ac68:status=self.acquisition(c.byref(bus),case['id'],SCRATCH,c.byref(out))
  elif case['entry']==0x1aa40:status=self.resources[case['entry']](c.byref(bus),case['id'],SCRATCH,c.byref(out))
  else:status=self.resources[case['entry']](c.byref(bus),case['id'],32768,c.byref(out))
  if not case.get('allow_host_error'):assert status==0 and not errors,(status,errors)
  return self.device.ram(),out.value,{'status':status,'errors':errors,'calls':calls,'disc_requests':list(self.disc.requests),'disc_completions':list(self.disc.completions),'disc_stops':self.disc.stops,'hardware':self.hardware(),'device':self.device.stats()}
def main():
 out=ROOT/'verification/frame-acquire-real-disc'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 restore=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_frame_resource_acquire.c','biwn_resources.c','biwn_memory.c','biwn_transition_cleanup.c','biwn_cd_math.c'];library=out/'libframe-acquire-disc.dylib'
 accepted=json.loads((ROOT/'verification/local-frame-resource-acquire-checks-current.json').read_text());assert hashlib.sha256((restore/names[0]).read_bytes()).hexdigest()==accepted['source_sha256']
 subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(restore/n)for n in names],'-o',str(library)],check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
 runtime=Runtime(library);atlas=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();manifest,snapshot=native.prior.prior.render.assets();assert atlas[0x1ac68:0x1ae56]==snapshot[0x1ac68:0x1ae56]
 rng=random.Random(0x1ac681b044);rows=[];coverage=set();unresolved=[]
 try:
  for mode in [1,2,3]:
   bias=int.from_bytes(atlas[0x464c8+mode*2:0x464ca+mode*2],'big');count=int.from_bytes(atlas[0x464a0+mode*2:0x464a2+mode*2],'big')
   for group in [0,1,2]:
    ram=bytearray(native.seed(snapshot))
    for m in [1,2,3]:
     for address,width in [(0x464c8+m*2,2),(0x464a0+m*2,2),(0x464a8+m*4,4),(0x464b8+m*4,4)]:ram[address:address+width]=atlas[address:address+width]
    ram[0x15b530:0x15b532]=mode.to_bytes(2,'big');ram[0x15b532:0x15b534]=bytes(2)
    for index in range(36):
     ram[0x15b4a0+index*4:0x15b4a4+index*4]=b'\xff\xff\x00\x00';ram[0x4674c+index*8:0x46750+index*8]=(0x1134a0+index*8192).to_bytes(4,'big')
    case=dict(entry=0x1ac68,id=bias+group*count,incoming=[rng.getrandbits(32)for _ in world.REGS])
    save(out/'status.json',dict(status='running',mode=mode,group=group))
    try:left,expected,original=runtime.native(bytes(ram),case,coverage)
    except OriginalRetry:
     right,value,rebuilt=runtime.translated(bytes(ram),dict(case,allow_host_error=True));assert rebuilt['status']==3 and value==0xa55aa55a
     request=runtime.failure['disc_requests'][0];tag=get(atlas,0x464b8+mode*4)+group;start=request['normalized_track_offset'];marker=tag.to_bytes(4,'big')*16;found=runtime.disc.data.find(marker,start-0x40000,start+0x40000);first_search=runtime.disc.data[start:start+0x8000]
     assert marker not in first_search and len(runtime.failure['disc_requests'])>=2
     unresolved.append(dict(mode=mode,group=group,id=case['id'],status='original_retries_C_host_guard_no_acceptance',original=runtime.failure,C=rebuilt,C_out_D0=value,wanted_tag=hex(tag),marker_offset=found,marker_delta_from_requested_stream=found-start,first32768_has_wanted_marker=False))
     continue
    right,value,rebuilt=runtime.translated(bytes(ram),case)
    if masked(left)!=masked(right)or expected!=value or any(original[k]!=rebuilt[k]for k in ['calls','disc_requests','disc_completions','disc_stops','hardware']):
     save(out/'mismatch.json',dict(mode=mode,group=group,case=case,original_D0=expected,C_D0=value,original=original,rebuilt=rebuilt,RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(masked(left),masked(right)))if a!=b][:32]));raise AssertionError(out/'mismatch.json')
    assert value==0 and len(rebuilt['disc_requests'])>=1
    payload=right[0x1134a0:0x1134a0+count*8192];request=rebuilt['disc_requests'][-1];tag=get(atlas,0x464b8+mode*4)+group;stream=runtime.disc.data[request['normalized_track_offset']:request['normalized_track_offset']+request['bytes']];marker=tag.to_bytes(4,'big')*16;position=stream.find(marker);assert position>=0 and payload==stream[position+64:position+64+len(payload)]
    rows.append(dict(mode=mode,group=group,id=case['id'],phase='cold_load',full_D0=value,payload_bytes=len(payload),payload_sha256=hashlib.sha256(payload).hexdigest(),original=original,rebuilt=rebuilt))
    # Continue the resulting cache state; reuse must not perform another disc transfer.
    left,expected,original=runtime.native(right,case,coverage);right,value,rebuilt=runtime.translated(right,case)
    assert masked(left)==masked(right)and value==expected==0 and not rebuilt['disc_requests'] and original['calls']==rebuilt['calls']
    assert all(get(right,0x15b4a2+i*4,2)==2 for i in range(count))
    rows.append(dict(mode=mode,group=group,id=case['id'],phase='cached_reuse',full_D0=value,original=original,rebuilt=rebuilt))
 except Exception as error:
  save(out/'cases.json',rows);save(out/'status.json',dict(status='terminal_failed',error=repr(error),mode=mode,group=group,passed_cases=len(rows),diagnostic=getattr(runtime,'failure',None)));raise
 finally:runtime.close()
 save(out/'cases.json',rows)
 report=dict(status='seven_real_disc_loads_and_reuse_verified_two_groups_unresolved',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),planned_cases=18,cases=len(rows),unresolved_groups=unresolved,cold_loads=sum(r['phase']=='cold_load'for r in rows),source_sha256={n:hashlib.sha256((restore/n).read_bytes()).hexdigest()for n in names},observed_instruction_addresses=sorted(coverage),disc_requests=sum(len(r['rebuilt']['disc_requests'])for r in rows),unresolved_group_count=len(unresolved),payload_bytes=sum(r.get('payload_bytes',0)for r in rows),scripted_game_loader_or_copy_bodies=0,new_training=False,native_Chat_verified=False,natural_gameplay_integration_verified=False,full_route_runtime_promoted=False,scope='Original pinned Jaguar CPU versus locally authored acquisition linked to existing coordinator source loader/copy/CD math. Real normalized internal disc bytes, returned D0, visible RAM, calls/transfer events and checked hardware match for seven cold loads spanning all three modes plus seven cache reuses. Two mode3 groups remain unresolved: original repeatedly retries because marker is outside the first32768 searched bytes; C returns added dependency error from bounded loader, with unchanged output. No original exception/equivalent retry-state claim. This is a partial integration result, not all18 planned cases passing. Payload independently checked against the actual marker-selected disc stream. Source mode tables, initialized cache, frozen TOC/heap, BIOS303C/3042 adapters, image-specific674-byte phase and DF60 completion tick remain fixtures. Private CPU frames/scratch, other caller-saved registers/CCR, global scheduler, physical CD timing and natural gameplay excluded.')
 save(out/'report.json',report);save(out/'status.json',dict(status='terminal_partial',passed_cases=len(rows),unresolved_groups=len(unresolved)));save(ROOT/'verification/frame-acquire-real-disc-current.json',report);print(json.dumps({k:report[k]for k in ['status','cases','cold_loads','disc_requests','payload_bytes','unresolved_group_count']}),flush=True)
if __name__=='__main__':main()
