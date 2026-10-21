"""Six complete transition-cleanup CPU functions versus callback C, no stubs."""
import argparse,ctypes as c,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_geometry as geometry
world=geometry.world;ROOT=world.ROOT;SP=world.SP;STOP=world.STOP;REGS=world.REGS
RANGES={0x1545c:0x1557a,0x1ae56:0x1ae88,0x20cc4:0x20cf8,0x20e40:0x20e8c,0x20e8c:0x20f0c,0x20f0c:0x20f78}
NAMES={0x1545c:'biwn_cleanup_free_handle',0x1ae56:'biwn_cleanup_release_texture',0x20cc4:'biwn_cleanup_release_room',0x20e40:'biwn_cleanup_release_region',0x20e8c:'biwn_cleanup_reset_rooms',0x20f0c:'biwn_cleanup_reset_region'}
MASKS={0x1545c:[1,3],0x1ae56:[0,2],0x20cc4:[0,1,2],0x20e40:[0,1,2],0x20e8c:[0,1,2,3],0x20f0c:[0,1,2,3]}
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
class Script(geometry.boundary.Script):pass

def original(script,case,coverage):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(script.memory));entry=case['entry']
 args=b''.join(x.to_bytes(2 if entry==0x1ae56 else 4,'big')for x in case['params']);cpu.mem_write(SP,STOP.to_bytes(4,'big')+args)
 for reg,value in zip(REGS,case['incoming']):cpu.reg_write(reg,value)
 cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP);steps=[];calls=[]
 def code(engine,a,w,_):
  assert any(start<=a<end for start,end in RANGES.items()),hex(a)
  coverage.add(a);steps.append(a)
  if a in RANGES:calls.append(hex(a))
 def read(engine,access,a,w,v,_):
  if SP-0x1000<=a<SP+16:return
  engine.mem_write(a,script.read(a,w).to_bytes(w,'big'))
 def write(engine,access,a,w,v,_):
  if SP-0x1000<=a<SP+16:return
  script.write(a,w,v&((1<<(8*w))-1))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(entry,STOP,count=1000000,timeout=3000000)
 assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
 for i,reg in enumerate(REGS):
  if i not in [0,1,8,9]:assert cpu.reg_read(reg)==case['incoming'][i],(hex(entry),i)
 if args:assert bytes(cpu.mem_read(SP+4,len(args)))==args
 actual=bytes(cpu.mem_read(0,0x200000));assert actual[:SP-0x1000]==script.memory[:SP-0x1000]and actual[SP+16:]==script.memory[SP+16:]
 return cpu.reg_read(UC_M68K_REG_D0),len(steps),calls

def bind(lib):
 result={}
 for entry,name in NAMES.items():
  fn=getattr(lib,name);types=[c.POINTER(world.Bus)]
  if entry==0x1ae56:types += [c.c_uint16,c.c_uint32]
  elif entry in [0x20e8c,0x20f0c]:types += [c.c_uint32,c.c_uint32]
  else:types += [c.c_uint32,c.c_uint32,c.c_uint32]
  fn.argtypes=types+[c.POINTER(c.c_uint32)];fn.restype=c.c_int;result[entry]=fn
 return result
def translated(functions,script,case,limit=100000,missing=None,null_out=False):
 def reader(width):
  def callback(_,a,v):
   try:v[0]=script.read(a,width);return 0
   except Exception as error:script.errors.append(str(error));return 1
  return callback
 def writer(width):
  def callback(_,a,v):
   try:script.write(a,width,v);return 0
   except Exception as error:script.errors.append(str(error));return 1
  return callback
 types=[world.R16,world.R32,world.W16,world.W32];callbacks=[types[0](reader(2)),types[1](reader(4)),types[2](writer(2)),types[3](writer(4))]
 if missing is not None:callbacks[missing]=types[missing]()
 bus=world.Bus(world.R8(),*callbacks,world.CALL(),None,0);out=c.c_uint32(0xa5a55a5a);entry=case['entry'];args=[c.byref(bus),*case['params']]
 if entry!=0x1ae56:args.append(case['incoming'][0])
 args += [limit,None if null_out else c.byref(out)]
 return functions[entry](*args),out.value

def cases(snapshot):
 rng=random.Random(0x20e8c);groups={entry:[]for entry in RANGES};obj=0x82000;table=0x100000
 def make(entry,kind,params):
  return {'entry':entry,'kind':kind,'params':params,'incoming':[rng.getrandbits(32)for _ in REGS],'initial':[],'default_helper_return':0}
 def texture_table(case):
  for i in range(36):case['initial'] += [[0x15b4a0+i*4,2,0x200+i],[0x15b4a2+i*4,2,rng.choice([0,1,2,0xffff,0x8000])]]
 for match in [0,1,17,35,None]:
  for count in [0,1,2,0xffff,0x8000,0x7fff]:
   for reread in [False,True]:
    case=make(0x1ae56,'texture_reference',[0x200+match if match is not None else 0xffff]);texture_table(case)
    if match is not None:
     a=0x15b4a2+match*4;case['initial'].append([a,2,count])
     if reread and count:case['read_queues']=[{'address':a,'width':2,'values':[count,7]}]
    groups[case['entry']].append(case)
 for entry in [0x20cc4,0x20e40]:
  for count in [0,1,2,4,0xffff,0x8000]:
   for variant in range(12):
    case=make(entry,'room_or_region_rereads',[obj]);texture_table(case)
    if entry==0x20cc4:
     case['initial'] += [[obj+6,2,count],[obj+20,4,table]]+[[table+i*2,2,0x200+(i+variant)%36]for i in range(8)]
     if variant%3==1 and count in [2,4]:case['read_queues']=[{'address':obj+6,'width':2,'values':[count,1]}]
     if variant%3==2:
      case['initial'] += [[table+0x100+i*2,2,0x210+i]for i in range(8)];case['read_queues']=[{'address':obj+20,'width':4,'values':[table,table+0x100]}]
    else:
     index=[0,1,0xfffe,0xffff,0x7fff,0x8000][variant%6];record=table+(index if index<0x8000 else index-65536)*6
     case['initial'] += [[obj+2,2,index],[obj+8,4,table],[record,2,count]]+[[record+2+i*2,2,(0xfffe if variant%3==0 else 0x200+i*6)]for i in range(8)]
     if variant%3==0:
      for i in range(6):case['initial'].append([0x15b4a0+i*4,2,(0xfffe+i)&0xffff])
     if variant%3==1 and count in [1,2,4]:case['read_queues']=[{'address':record+2,'width':2,'values':[0x200,0x206,0x20c,0x212,0x218,0x21e]}]
    groups[entry].append(case)
 layouts={
  'empty':([],0x700,0x40),'before_separate':([(0x400,0x40)],0x100,0x40),
  'before_join_last':([(0x140,0x40)],0x100,0x40),'before_join_next':([(0x140,0x40),(0x400,0x40)],0x100,0x40),
  'middle_separate':([(0x100,0x40),(0x400,0x40)],0x200,0x40),
  'middle_left':([(0x100,0x40),(0x400,0x40)],0x140,0x40),
  'middle_right_last':([(0x100,0x40),(0x400,0x40)],0x3c0,0x40),
  'middle_right_next':([(0x100,0x40),(0x400,0x40),(0x700,0x40)],0x3c0,0x40),
  'middle_both_last':([(0x100,0x300),(0x440,0x40)],0x400,0x40),
  'middle_both_next':([(0x100,0x300),(0x440,0x40),(0x700,0x40)],0x400,0x40),
  'tail_join':([(0x100,0x40)],0x140,0x40),'tail_separate':([(0x100,0x40)],0x200,0x40),
  'scan_middle':([(0x100,0x40),(0x300,0x40),(0x500,0x40)],0x400,0x40),
  'scan_tail':([(0x100,0x40),(0x300,0x40),(0x500,0x40)],0x600,0x40)}
 for label,(free,offset,size)in layouts.items():
  for variant in range(16):
   base=0x170000;block=base+offset;handle=0x160000;case=make(0x1545c,label,[handle]);case['initial'] += [[handle,4,block+8],[block,4,size],[0x112d60,4,base+free[0][0]if free else 0],[0x112d64,4,rng.getrandbits(32)]]
   for i,(address,length)in enumerate(free):case['initial'] += [[base+address,4,length],[base+address+4,4,base+free[i+1][0]if i+1<len(free)else 0],[base+address+8,4,base+free[i-1][0]if i else 0]]
   if variant==1:case['params']=[0]
   if variant==2:case['initial'].append([handle,4,0])
   if variant==3 and label=='empty':case['initial'] += [[base+0x900,4,0x80]];case['read_queues']=[{'address':handle,'width':4,'values':[block+8,base+0x908]}]
   groups[0x1545c].append(case)
 for entry in [0x20e8c,0x20f0c]:
  for variant in range(64):
   case=make(entry,'complete_reset',[]);texture_table(case)
   case['initial'] += [[0x112d60,4,0],[0x112d64,4,rng.getrandbits(32)],[0x49c18,4,obj]]
   for i in range(25):
    room=obj+i*0x100;ids=table+i*0x100;count=(i+variant)%4
    case['initial'] += [[0x49bb4+i*4,4,room],[room+6,2,count],[room+20,4,ids]]+[[ids+j*2,2,0x200+(i+j)%36]for j in range(4)]
   case['initial'] += [[obj+2,2,0],[obj+8,4,0x130000],[0x130000,2,variant%3],[0x130002,2,0x200],[0x130004,2,0x206]]
   for i in range(40):
    active=0 if(i+variant)%3==0 else 1 if i%2 else 0xffff;handle=0x160000+i*4;block=0x170000+i*0x80
    case['initial'] += [[0x4bd9c+i*30,2,active],[0x4bdb0+i*30,4,handle if(i+variant)%5 else 0],[handle,4,block+8 if i%7 else 0],[block,4,0x40],[0x49d6e+i*206,2,0xa55a]]
   if variant%11==0:case['read_queues']=[{'address':0x4bdb0+30,'width':4,'values':[0x160004,0x160008]}]
   groups[entry].append(case)
 # Interleave entries so preflight exercises every complete function.
 return [group[i]for i in range(max(map(len,groups.values())))for group in groups.values()if i<len(group)]

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);opts=parser.parse_args();snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes()
 for start,end in RANGES.items():assert snapshot[start:end]==image[start-0x4000:end-0x4000]
 out=ROOT/'verification/biwn-transition-cleanup'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libcleanup.dylib'
 command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_transition_cleanup.c'),'-o',str(library)];run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
 functions=bind(c.CDLL(str(library)));vectors=cases(snapshot);coverage=set();rows=[]
 if opts.limit:vectors=vectors[:opts.limit]
 for i,case in enumerate(vectors):
  save(out/'status.json',{'status':'running','case':i,'entry':hex(case['entry'])});a=Script(snapshot,case);b=Script(snapshot,case);d0,steps,calls=original(a,case,coverage);status,actual=translated(functions,b,case)
  if status or actual!=d0 or a.trace!=b.trace or a.memory!=b.memory:
   save(out/'mismatch.json',{'case':i,'parameters':case,'original_D0':d0,'C_D0':actual,'C_status':status,'C_errors':b.errors,'original_trace':a.trace,'C_trace':b.trace,'RAM_differences':[[j,a.memory[j],b.memory[j]]for j in range(len(a.memory))if a.memory[j]!=b.memory[j]][:100]});raise AssertionError(str(out/'mismatch.json'))
  rows.append({'case':i,'parameters':case,'original_CPU_instructions':steps,'full_D0':d0,'original_function_entries':calls,'trace':b.trace,'whole_RAM_and_bus_match':True})
 save(out/'fixtures.json',rows)
 if opts.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'preflight_cases':len(rows),'directory':str(out)}));return
 guards=[]
 for entry in RANGES:
  case=next(row['parameters']for row in rows if row['parameters']['entry']==entry)
  for missing in MASKS[entry]:
   script=Script(snapshot,case);status,d0=translated(functions,script,case,missing=missing);assert status==1 and d0==0xa5a55a5a and not script.trace;guards.append({'entry':hex(entry),'missing_callback':missing,'status':status})
  for flag in ['null_out','zero_limit']:
   script=Script(snapshot,case);status,d0=translated(functions,script,case,null_out=flag=='null_out',limit=0 if flag=='zero_limit'else 100000);assert status==1 and d0==0xa5a55a5a and not script.trace;guards.append({'entry':hex(entry),'argument_guard':flag,'status':status})
 for label,event in [('failed_read','r'),('failed_write','w')]:
  row=next(row for row in rows if row['parameters']['entry']==0x20e8c);target=next(t for t in row['trace']if t[0]==event);script=Script(snapshot,row['parameters']);setattr(script,'fail_read'if event=='r'else'fail_write',(target[1],target[2]));status,d0=translated(functions,script,row['parameters']);assert status==3 and d0==0xa5a55a5a;guards.append({'guard':label,'status':status,'partial_trace':script.trace})
 case=next(row['parameters']for row in rows if row['parameters']['entry']==0x20e8c);script=Script(snapshot,case);status,d0=translated(functions,script,case,limit=2);assert status==2 and d0==0xa5a55a5a;guards.append({'guard':'shared_work_limit','status':status,'partial_trace':script.trace});save(out/'guards.json',guards)
 decoded=[]
 for start,end in RANGES.items():part,_=world.select.binary_tools.m68k_instructions(image[start-0x4000:end-0x4000],start);decoded+=part
 missing=[row for row in decoded if row['address']not in coverage];save(out/'decode.json',{'instructions':decoded,'uncovered':missing});assert not missing,str(out/'decode.json')
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'six_original_CPU_cleanup_functions_match_C','directory':str(out),'CPU_cases':len(rows),'entry_cases':{hex(entry):sum(row['parameters']['entry']==entry for row in rows)for entry in RANGES},'host_guards':len(guards),'CPU_instruction_coverage':[len(decoded),len(decoded)],'portable_components':6,'original_bytes':sum(end-start for start,end in RANGES.items()),'intervals':{hex(a):hex(b)for a,b in RANGES.items()},'nested_helper_stubs':0,'source_sha256':{name:world.select.binary_tools.sha(source/name)for name in ['biwn_transition_cleanup.c','biwn_transition_cleanup.h']},'compiler':command,
 'matched':['Six complete original CPU functions, with their real nested calls; no RTS helper stubs. FullD0, privateRTSstack/args and callee-saved registers.','Every external read/write width/address/value/order and whole visible2MBRAM.','Reference count/reread/word wrap; room/region signed counts and six-ID groups;25room/40object resets; null handles; free-list ordered insertion and left/right/both coalescing.'],
 'limits':['Finite privateRAM tables and free lists; arbitrary aliasing, concurrent mutation, physicalhardware and whole game excluded.','Added shared work limits/errors retain prior effects and leave outputD0 unchanged. FullCCR and caller-saved registers exceptD0 excluded.','Not yet connected to current world pipeline at this standalone checkpoint; scene loading and other transition services unfinished.']}
 save(out/'status.json',{'status':'terminal_pass','cases':len(rows)});save(ROOT/'verification/biwn-transition-cleanup-checks.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
