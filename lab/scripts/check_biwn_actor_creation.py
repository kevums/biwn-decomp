"""Actor/static factories and indoor positioning against original CPU."""
import argparse,ctypes as c,json,random,subprocess,os,hashlib
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_scene_loading as prior
world=prior.world;ROOT=prior.ROOT;SP=prior.SP;STOP=prior.STOP
RANGES={0x13ae0:0x13b5a,0x134dc:0x137e0,0x137e0:0x13ae0,0x10520:0x105da,0x105da:0x10652}
CODE_RANGES=[(0x13ae0,0x13b5a),(0x134dc,0x13620),(0x13706,0x137e0),(0x137e0,0x138bc),(0x13902,0x13ae0),(0x10520,0x105da),(0x105da,0x10652)]
WIDTHS={0x13ae0:[2,4,2,4,2],0x134dc:[2,2,4,2,4,2],0x137e0:[2,4,2,4,2],0x10520:[4],0x105da:[4],0x102c4:[4],0xdf6c:[4,4],0x152a2:[4],0xe2b8:[4,4,4]}
W8=prior.prior.W8;save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
class Script(prior.prior.boundary.Script):
 def call(self,target,args,incoming_D0):
  if self.fail_call==target:raise RuntimeError('injected dependency failure')
  self.trace.append(['call',target,args,incoming_D0])
  for a,w,v in self.case.get('helper_effects',[]):self.put(a,w,v)
  return self.case['helper_returns'].get(str(target),self.case['default_helper_return'])
def original(script,case,coverage):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(script.memory));params=b''.join(v.to_bytes(w,'big')for v,w in zip(case['params'],WIDTHS[case['entry']]));cpu.mem_write(SP,STOP.to_bytes(4,'big')+params)
 for r,v in zip(world.REGS,case['incoming']):cpu.reg_write(r,v)
 cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP);stubs=[a for a in WIDTHS if a!=case['entry']]
 for a in stubs:cpu.mem_write(a,b'\x4e\x75')
 steps=[]
 def code(e,a,w,_):
  if a in stubs:
   stack=e.reg_read(UC_M68K_REG_A7);args=[];offset=4
   for width in WIDTHS[a]:args.append(int.from_bytes(e.mem_read(stack+offset,width),'big'));offset+=width
   script.changed=[];d0=script.call(a,args,e.reg_read(UC_M68K_REG_D0))
   for address,width,value in script.changed:e.mem_write(address,value.to_bytes(width,'big'))
   e.reg_write(UC_M68K_REG_D0,d0);return
  assert any(lo<=a<hi for lo,hi in CODE_RANGES),hex(a);coverage.add(a);steps.append(a)
 def read(e,t,a,w,v,_):
  if SP-0x1000<=a<SP+32:return
  e.mem_write(a,script.read(a,w).to_bytes(w,'big'))
 def write(e,t,a,w,v,_):
  if SP-0x1000<=a<SP+32:return
  script.write(a,w,v&((1<<(w*8))-1))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(case['entry'],STOP,count=200000,timeout=5000000)
 assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4,(hex(cpu.reg_read(UC_M68K_REG_PC)),len(steps))
 assert all(cpu.reg_read(r)==case['incoming'][i]for i,r in enumerate(world.REGS)if i not in[0,1,8,9]);assert bytes(cpu.mem_read(SP+4,len(params)))==params
 ram=bytearray(cpu.mem_read(0,0x200000))
 for a in stubs:ram[a:a+2]=script.memory[a:a+2]
 assert ram[:SP-0x1000]==script.memory[:SP-0x1000]and ram[SP+32:]==script.memory[SP+32:]
 return cpu.reg_read(UC_M68K_REG_D0),len(steps)
def bind(lib):
 fn=lib.biwn_actor_service;fn.argtypes=[c.POINTER(world.Bus),W8,c.c_uint32,c.POINTER(c.c_uint32),c.c_uint32,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];fn.restype=c.c_int;return fn
def translated(fn,script,case,budget=4096,missing=None,null_bus=False,null_out=False,null_args=False,n_override=None):
 def reader(w):
  def cb(_,a,v):
   try:v[0]=script.read(a,w);return 0
   except Exception as error:script.errors.append(str(error));return 1
  return cb
 def writer(w):
  def cb(_,a,v):
   try:script.write(a,w,v);return 0
   except Exception as error:script.errors.append(str(error));return 1
  return cb
 def call(_,target,args,n,out):
  try:assert n==len(WIDTHS[target]);out[0]=script.call(target,list(args[:n]),out[0]);return 0
  except Exception as error:script.errors.append(str(error));return 1
 callbacks=[world.R8(reader(1)),world.R16(reader(2)),world.R32(reader(4)),world.W16(writer(2)),world.W32(writer(4)),world.CALL(call)];write8=W8(writer(1))
 if missing==6:write8=W8()
 elif missing is not None:callbacks[missing]=type(callbacks[missing])()
 bus=world.Bus(*callbacks,None,0);out=c.c_uint32(0xa55aa55a);args=(c.c_uint32*len(case['params']))(*case['params']);status=fn(None if null_bus else c.byref(bus),write8,case['entry'],None if null_args else args,len(case['params'])if n_override is None else n_override,case['incoming'][0],budget,None if null_out else c.byref(out));return status,out.value
def cases():
 rng=random.Random(0x13ae0);rows=[]
 for entry,total in[(0x13ae0,512),(0x134dc,768),(0x137e0,768),(0x10520,256),(0x105da,256)]:
  for i in range(total):
   initial=[]
   def put(a,w,v):initial.append([a,w,v&((1<<(w*8))-1)])
   id=([0,1,64,70,118,119,0xffff,0x8000][i%8]if entry==0x13ae0 else i%128 if entry==0x134dc else [70,0,0xffff,0x8000,104+i%35][i%5]);slot=[0,1,39,40,0xffff,0xfffe][i%6];x=rng.getrandbits(32);z=rng.getrandbits(32);heading=rng.getrandbits(16);y=rng.getrandbits(16)
   for a in[0x49c50,0x49c56,0x49c66,0x49c6a,0x49c6e,0x49c72]:put(a,4,rng.getrandbits(32))
   for a in[0x49c60,0x49c62,0x49c64]:put(a,2,[0,1,2,3,0xffff][(i+a)%5])
   free=i%41
   for j in range(40):put(0x49d6c+j*206,2,0 if j==free else 1);put(0x4bd9c+j*30,2,0 if j==free else 1)
   if entry==0x137e0:id=104+(i//2)%35 if i%2==0 else[70,0,0xffff,0x8000][(i//2)%4]
   if entry==0x137e0 and i%134==0:id=[103,139,0xffff,0][(i//134)%4]
   flags=(i//8)%2 if entry==0x13ae0 else 2 if entry==0x137e0 and i%2==0 else 0
   if entry==0x137e0 and id==111 and flags==2 and i%3==0:put(0x4bd9c+((free+1)%40)*30,2,0)
   signed_id=id if id<32768 else id-65536;put(0x4208c+(signed_id if entry==0x13ae0 else id),1,flags)
   model=0x130000;frame=[0,4,60,0x80,0xff][i%5];width=[0,1,16,127,255][(i//5)%5];put(0x6e6a8,4,rng.randrange(50000));put(0x42000+id,1,frame);signed_frame=frame if frame<128 else frame-256;put(0x6e6ac+signed_frame*4,4,model-0x6e6a0);put(model,1,width);put(model+1,1,rng.getrandbits(8));put(0x3bd20+width*4,4,rng.getrandbits(32));put(0x110000,4,0x170000)
   if entry==0x134dc:params=[id,slot,x,y,z,heading]
   elif entry in[0x13ae0,0x137e0]:params=[id,x,y,z,heading]
   else:
    obj=0x80000;scene=0x84000;table=0x100000;params=[obj];count=[0,1,2,3,0xffff,0x8000,0x8001][i%7];index=((count-1)&65535);record=table+index*24;ox=rng.getrandbits(32);oz=rng.getrandbits(32);px=[0,1,15,16,0xffff][(i//7)%5];pz=[0,1,15,16,0x8000][(i//35)%5]
    if count==0x8000:px=pz=1
    put(0x49c18,4,scene);put(scene,2,count);put(scene+4,4,table);put(obj+(4 if entry==0x10520 else 2),4,ox+px*64);put(obj+(10 if entry==0x10520 else 8),4,oz+pz*64);put(obj+30 if entry==0x10520 else 0x49c6a,4,ox);put(obj+38 if entry==0x10520 else 0x49c72,4,oz)
    if not(index&0x8000):
     for j in range(min(count,4)):
      rec=record-j*24
      for a,v in[(rec+2,0 if i%3==0 or count==0x8000 else 15),(rec+4,0),(rec+6,16),(rec+8,16)]:put(a,2,v)
   queues=[]
   if entry==0x137e0 and not flags and i%11==0:queues=[{'address':0x110000,'width':4,'values':[0x170000,0x170100,0x170200]}]
   rows.append({'entry':entry,'params':params,'incoming':[rng.getrandbits(32)for _ in world.REGS],'initial':initial,'read_queues':queues,'default_helper_return':rng.getrandbits(32),'helper_returns':{str(0x152a2):0x110000}})
 return rows

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opt=ap.parse_args();out=ROOT/'verification/biwn-actor-creation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';lib=out/'libactor-creation.dylib';subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_actor_creation.c'),'-o',str(lib)],check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});fn=bind(c.CDLL(str(lib)));snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=cases()
 if opt.limit:vectors=[r for entry in RANGES for r in [x for x in vectors if x['entry']==entry][:opt.limit]]
 rows=[];coverage=set()
 try:
  for ordinal,case in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':ordinal,'entry':hex(case['entry'])});a=Script(snapshot,case);b=Script(snapshot,case);expected,steps=original(a,case,coverage);status,d0=translated(fn,b,case)
   if status or expected!=d0 or a.memory!=b.memory or a.trace!=b.trace:
    save(out/'mismatch.json',{'case':case,'status':status,'expected_D0':expected,'C_D0':d0,'original_trace':a.trace,'C_trace':b.trace,'errors':b.errors});raise AssertionError(str(out/'mismatch.json'))
   rows.append({'case':ordinal,'parameters':case,'full_D0':d0,'instructions':steps,'trace':b.trace,'visible_RAM_accesses_calls_incoming_and_return_D0_match':True})
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','case':ordinal,'error':repr(error)});raise
 save(out/'fixtures.json',rows);session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();addresses=set()
 for lo,hi in CODE_RANGES:
  decoded,_=world.select.binary_tools.m68k_instructions(image[lo-0x4000:hi-0x4000],lo);addresses.update(r['address']for r in decoded)
 covered=addresses&coverage
 if opt.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows),'coverage':[len(covered),len(addresses)],'uncovered':[hex(a)for a in sorted(addresses-coverage)]});print(json.dumps({'directory':str(out),'cases':len(rows),'coverage':[len(covered),len(addresses)]}));return
 assert addresses<=coverage,[hex(a)for a in sorted(addresses-coverage)];guards=[]
 for entry in RANGES:
  case=next(r for r in vectors if r['entry']==entry)
  for field in range(7):
   script=Script(snapshot,case);status,d0=translated(fn,script,case,missing=field);assert status==1 and d0==0xa55aa55a and not script.trace;guards.append({'entry':hex(entry),'missing_callback':field})
  for kw in[{'null_bus':True},{'null_out':True},{'null_args':True},{'n_override':0}]:
   script=Script(snapshot,case);status,d0=translated(fn,script,case,**kw);assert status==1 and d0==0xa55aa55a and not script.trace;guards.append({'entry':hex(entry),'arguments':kw})
  if entry!=0x134dc:
   looping=next(r for r in vectors if r['entry']==entry and translated(fn,Script(snapshot,r),r,budget=0)[0]==4);script=Script(snapshot,looping);status,d0=translated(fn,script,looping,budget=0);assert status==4 and d0==0xa55aa55a;guards.append({'entry':hex(entry),'work_limit':True})
 for entry in[0x13ae0,0x134dc,0x137e0]:
  case=next(r for r,row in zip(vectors,rows)if r['entry']==entry and any(x[0]=='call'for x in row['trace']));trace=rows[vectors.index(case)]['trace'];target=next(x[1]for x in trace if x[0]=='call');script=Script(snapshot,case);script.fail_call=target;status,d0=translated(fn,script,case);assert status==3 and d0==0xa55aa55a;guards.append({'entry':hex(entry),'dependency_error':hex(target),'partial_effects_retained':True})
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'five_actor_and_indoor_position_bodies_original_CPU_C_match','directory':str(out),'CPU_cases':len(rows),'CPU_instruction_coverage':[len(covered),len(addresses)],'host_guards':len(guards),'new_components':5,'code_bytes':sum(b-a for a,b in CODE_RANGES),'inline_jump_table_bytes':300,'source_intervals':{hex(a):hex(b)for a,b in RANGES.items()},'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in ['biwn_actor_creation.c','biwn_actor_creation.h']},'helper_incoming_D0_compared':True,'nested_scripted_targets':[hex(a)for a in WIDTHS],'matched':['Entity versus static/sprite routing,40record scans, raw index actor initialization, current scene metadata/room calculation,15task-entry dispatch targets,static sprite allocation/header/decoder arguments,animated callback table/doubled-object case andtwo indoor position bodies.','External RAM byte/word/long access order, logical helper arguments/incomingD0, fullD0, callee saves andRTS stack match original CPU.300inlinejump-table bytes are read asdata andexcludedfrominstructioncoverage.'],'limits':['Nested helpers are scripts in this independent-body proof, including other members ofthis group. No actual taskcreation, sprite decoding, actor behavior orwhole startup established here.','Private stack,CCR andothercaller-savedregisters excluded. Finite validRAM andselectedhandle rereads/rawnegativeindexes. Unsupported jump targets return an explicit hosterror, not arbitrary instruction emulation. Fullgame/hardwareunfinished.']}
 save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-actor-creation-checks.json',report);print(json.dumps(report))
if __name__=='__main__':main()
