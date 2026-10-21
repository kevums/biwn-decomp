"""Four actor navigation bodies: complete CPU, flags, RAM and data bus comparisons."""
import argparse
import ctypes as c
import hashlib
import json
import os
import random
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_actor_task as prior

ROOT=prior.ROOT; world=prior.world; CPU=prior.CPU; SP=prior.SP; STOP=prior.STOP
RANGES=[(0xf368,0xf4d8),(0x13f12,0x13f3e),(0x13f48,0x13f7c),
        (0x13f7c,0x13fac),(0x13fb6,0x13fea),(0x13fea,0x1400e),(0x14018,0x1404c)]
RETURNS={0xf4d6,0x13f58,0x13f7a,0x13fc6,0x13fe8,0x14028,0x1404a}


def save(path,value): path.write_text(json.dumps(value,indent=2)+'\n')


class Memory:
 def __init__(self,snapshot,case):
  self.ram=bytearray(snapshot);self.trace=[];self.errors=[]
  for a,w,v in case['initial']:self.put(a,w,v)
 def put(self,a,w,v):self.ram[a:a+w]=(v&((1<<(w*8))-1)).to_bytes(w,'big')
 def read(self,a,w):
  if a<0 or a+w>len(self.ram):raise ValueError(hex(a))
  value=int.from_bytes(self.ram[a:a+w],'big');self.trace.append(['read',a,w,value]);return value
 def write(self,a,w,v):
  if a<0 or a+w>len(self.ram):raise ValueError(hex(a))
  self.trace.append(['write',a,w,v]);self.put(a,w,v)


def original(memory,case,coverage):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
 cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(memory.ram))
 for r,v in zip(world.REGS,case['registers']):cpu.reg_write(r,v)
 cpu.reg_write(UC_M68K_REG_SR,case['SR']);cpu.reg_write(UC_M68K_REG_A7,SP);steps=[]
 def code(engine,address,width,_):
  assert any(lo<=address<hi for lo,hi in RANGES),hex(address)
  coverage.add(address);steps.append(address)
 def read(engine,access,address,width,value,_):engine.mem_write(address,memory.read(address,width).to_bytes(width,'big'))
 def write(engine,access,address,width,value,_):memory.write(address,width,value&((1<<(8*width))-1))
 hook=cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write)
 cpu.emu_start(case['entry'],STOP,count=1000,timeout=500000)
 pc=cpu.reg_read(UC_M68K_REG_PC);assert pc==STOP
 registers=[cpu.reg_read(r)for r in world.REGS]+[cpu.reg_read(UC_M68K_REG_A7)]
 assert bytearray(cpu.mem_read(0,0x200000))==memory.ram
 cpu.hook_del(hook);cpu.mem_write(STOP,b'\x40\xc7');cpu.emu_start(STOP,STOP+2,count=1)
 sr=cpu.reg_read(UC_M68K_REG_D7)&65535
 return {'registers':registers,'PC':pc,'SR':sr,'USP':SP+4,'SSP':0x1d0000},len(steps)


def bind(library,full_call=False):
 fn=library.biwn_actor_navigation_call if full_call else library.biwn_actor_navigation_body;fn.argtypes=[c.POINTER(world.Bus),c.POINTER(CPU)];fn.restype=c.c_int;return fn


def translated(fn,memory,case,missing=None,fail=None,null_bus=False,null_cpu=False):
 def reader(width):
  def call(_,a,out):
   if fail==('read',width):return 1
   try:out[0]=memory.read(a,width);return 0
   except Exception as error:memory.errors.append(repr(error));return 1
  return call
 def writer(_,a,v):
  if fail==('write',4):return 1
  try:memory.write(a,4,v);return 0
  except Exception as error:memory.errors.append(repr(error));return 1
 callbacks=[world.R8(reader(1)),world.R16(reader(2)),world.R32(reader(4)),world.W32(writer)]
 if missing is not None:callbacks[missing]=type(callbacks[missing])()
 bus=world.Bus(callbacks[0],callbacks[1],callbacks[2],world.W16(),callbacks[3],world.CALL(),None,0)
 cpu=CPU();cpu.registers[:]=case['registers'];cpu.pc=case['entry'];cpu.sr=case['SR'];cpu.usp=SP;cpu.ssp=0x1d0000
 before=bytes(cpu);status=fn(None if null_bus else c.byref(bus),None if null_cpu else c.byref(cpu))
 return status,{'registers':list(cpu.registers),'PC':cpu.pc,'SR':cpu.sr,'USP':cpu.usp,'SSP':cpu.ssp},before==bytes(cpu)


def cases():
 rng=random.Random(0xf36813f);rows=[];obj=0x80000;record=0x120000
 for i in range(1024):
  heading=[0,64,128,192,1,65,129,255][i%8];kind=[0,1,2,3,4,0x7fff,0x8000,0xffff][(i//8)%8]
  offset=[0,1,15,16,511,512,1023,1024,0x7fff,0x8000,0xffff,0xfff0,0x1234,0x400,0x8400,0xfc00][(i//64)%16]
  registers=[rng.getrandbits(32)for _ in range(16)];registers[15]=SP
  coord=rng.choice([0,1,1023,1024,0x7fffffff,0x80000000,0xfffffc00,0xffffffff,rng.getrandbits(32)])
  if i==4:registers[0]=0xaabbccdd;registers[2]=0x80000000
  if i==8:coord=0xaabb1234;offset=0xffff;registers[1]=0x12345678
  rows.append({'entry':0xf368,'registers':registers,'SR':rng.randrange(32)|((i%8)<<8),
   'initial':[[SP,4,STOP],[SP+4,4,obj],[obj+111,1,heading],[obj+68,4,record],[obj+4,4,coord],
              [obj+10,4,coord],[record+16,2,kind],[record+18,2,kind],[record+10,2,offset],[record+14,2,offset]]})
  if i==4:rows[-1]['SR']=0x0011
 for entry in [0x13f12,0x13f7c,0x13fea]:
  for heading in range(256):
   for n in range(4):
    registers=[rng.getrandbits(32)for _ in range(16)];registers[15]=SP
    initial=[[SP,4,STOP],[SP+4,4,obj],[SP+8,4,(rng.getrandbits(30)<<2)|n],
             [obj+110,1,heading],[obj+68,4,record]]
    for off in [2,4,6,8]:initial.append([record+off,2,(rng.getrandbits(12)|(0xf000 if (heading+n+off//2)%2 else 0))])
    rows.append({'entry':entry,'registers':registers,'SR':rng.randrange(32)|((heading%8)<<8),'initial':initial})
 return rows


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);options=parser.parse_args()
 out=ROOT/'verification/biwn-actor-navigation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libactor-navigation.dylib'
 subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_actor_navigation.c'),'-o',str(library)],check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
 fn=bind(c.CDLL(str(library)),full_call=True);snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=cases();vectors=vectors[:options.limit]if options.limit else vectors;coverage=set();rows=[]
 try:
  for i,case in enumerate(vectors):
   save(out/'status.json',{'status':'running','case':i});left=Memory(snapshot,case);right=Memory(snapshot,case)
   expected,steps=original(left,case,coverage);status,actual,_=translated(fn,right,case)
   if status or expected!=actual or left.ram!=right.ram or left.trace!=right.trace:
    save(out/'mismatch.json',{'case':case,'status':status,'expected':expected,'actual':actual,'original_trace':left.trace,'C_trace':right.trace,'errors':right.errors,
                             'RAM_diff':[hex(j)for j,(a,b)in enumerate(zip(left.ram,right.ram))if a!=b][:32]})
    raise AssertionError(str(out/'mismatch.json'))
   rows.append({'case':i,'parameters':case,'CPU':actual,'instructions':steps,'trace':right.trace,'complete_CPU_RAM_and_bus_match':True})
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
 save(out/'fixtures.json',rows)
 if options.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(out);return
 session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);data=(session/'nextstage-68000-candidate.bin').read_bytes();addresses=set()
 for start,end in RANGES:
  decoded,_=world.select.binary_tools.m68k_instructions(data[start-0x4000:end-0x4000],start);addresses.update(r['address']for r in decoded)
 assert addresses<=coverage,[hex(a)for a in sorted(addresses-coverage)]
 guards=[]
 for index in range(4):
  case=vectors[0];memory=Memory(snapshot,case);status,_,unchanged=translated(fn,memory,case,missing=index);assert status==1 and unchanged and not memory.trace;guards.append({'missing_callback':index})
 for kwargs in [{'null_bus':True},{'null_cpu':True}]:
  memory=Memory(snapshot,vectors[0]);status,_,unchanged=translated(fn,memory,vectors[0],**kwargs);assert status==1 and unchanged and not memory.trace;guards.append(kwargs)
 for case in [{**vectors[0],'entry':0},{**vectors[0],'SR':0x2000}]:
  memory=Memory(snapshot,case);status,_,unchanged=translated(fn,memory,case);assert status==1 and unchanged and not memory.trace;guards.append({'unsupported_entry_or_supervisor':True})
 for fail in [('read',1),('read',2),('read',4),('write',4)]:
  case=vectors[0];memory=Memory(snapshot,case);status,_,unchanged=translated(fn,memory,case,fail=fail);assert status==2 and unchanged;guards.append({'bus_error':fail,'CPU_unchanged':True})
 for entry,table in [(0x13f12,0x13f3e),(0x13f7c,0x13fac),(0x13fea,0x1400e)]:
  case=next(x for x in vectors if x['entry']==entry and int.from_bytes(Memory(snapshot,x).ram[SP+8:SP+12],'big')&3==(3 if entry==0x13f7c else 0))
  memory=Memory(snapshot,case)
  for j in range(5):memory.put(table+j*2,2,0xffff)
  status,_,unchanged=translated(fn,memory,case);assert status==3 and unchanged;guards.append({'invalid_inline_table':hex(entry),'CPU_unchanged':True})
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'four_actor_navigation_bodies_match_original_CPU',
  'directory':str(out),'CPU_cases':len(rows),'CPU_instruction_coverage':[len(coverage&addresses),len(addresses)],
  'host_guards':len(guards),'new_components':4,'entries':['0xf368','0x13f12','0x13f7c','0x13fea'],
  'code_bytes':sum(b-a for a,b in RANGES),'inline_jump_table_bytes':30,
  'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in ['biwn_actor_navigation.c','biwn_actor_navigation.h']},
  'full_CPU_flags_RAM_private_stack_and_bus_compared':True,
  'matched':['All registers, materialized SR/CCR, complete RTS return PC/SP, stack banks, complete RAM including save frames and ordered data accesses match.',
             'All byte headings, all steering RNG selector residues, pass/blocked neighbor words, raw waypoint types, signed word shifts and wrapped coordinate sums covered.'],
  'complete_function_RTS_executed':True,
  'limits':['Standalone calls include RTS. The integrated body API stops at the RTS boundary and the actual actor caller performs the return. No movement, scheduler, GPU, scene or game completion is implied.',
            'The original inline jump tables select only their four known destinations. Modified tables causing other jumps return host errors; CPU exceptions/timing are not emulated.']}
 save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-actor-navigation-checks.json',report);print(json.dumps(report))


if __name__=='__main__':main()
