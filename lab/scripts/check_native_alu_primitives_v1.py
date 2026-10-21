"""Native68000 arithmetic primitives versus independently calculated logicalCPU results.
Finite boundary/random operands,all32incomingCCR values,both physicalstackbanks.
No disc/integration,IRQ,physicaltiming or whole-game claim.
"""
import ctypes as c,json,os,random,struct,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_deck_coordinate_source_v1 as base
ROOT=base.ROOT;SRC=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-shared-v8';V=ROOT/'verification';CODE=0x180000;DATA=0x100000;STOP=0x192000;SP=0x1e8000

def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return base.sha(Path(p).read_bytes())
def expected(op,a,b,sr):
 if op<2:
  bits=[16,32][op];v=a&((1<<bits)-1);return a,(sr&0xfff0)|(4 if not v else 0)|(8 if v>>(bits-1)else 0)
 if op<10:
  bits=16 if op>=6 else 32;mode=(op-2)%4;sub=mode&1;cmp=mode>>1;mask=(1<<bits)-1;a&=mask;b&=mask;v=(a-b if sub else a+b)&mask
  carry=a<b if sub else v<a;overflow=bool(((a^b)&(a^v)if sub else ~(a^b)&(a^v))&(1<<(bits-1)))
  f=(4 if not v else 0)|(8 if v>>(bits-1)else 0)|(2 if overflow else 0)|(1 if carry else 0)
  return v,(sr&(~15 if cmp else ~31))|f|(16 if carry and not cmp else 0)
 carry=overflow=0;v=a
 for _ in range(b):
  old=v
  if op==10:carry=v>>31;v=(v<<1)&0xffffffff;overflow|=(old^v)>>31
  else:carry=v&1;v>>=1
 return v,(sr&0xffe0)|(4 if not v else 0)|(8 if v>>31 else 0)|(17 if carry else 0)|(2 if overflow else 0)
def vectors():
 vals=[0,1,2,0x7f,0x80,0xff,0x7fff,0x8000,0xffff,0x10000,0x7fffffff,0x80000000,0xffffffff]
 for ccr in range(32):
  sr=(0xa700 if ccr&1 else 0x500)|ccr
  for a in vals:
   for op in range(2):yield op,a,0,sr
   for b in vals:
    for op in range(2,10):yield op,a,b,sr
   for count in [0,1,2,3,5,6,8,16,31,32,33,63,64,65]:
    for op in [10,11]:yield op,a,count,sr
 rng=random.Random(0x68000)
 for _ in range(2048):
  op=rng.randrange(12);yield op,rng.getrandbits(32),rng.randrange(80)if op>=10 else rng.getrandbits(32),rng.getrandbits(16)
def main():
 out=V/'native-alu-primitives-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 state=dict(status='building',pid=os.getpid(),directory=str(out),new_predictions=0,new_training=False,native_disc_changed=False)
 def mark():save(out/'protocol.json',state);save(V/'native-alu-primitives-v1-current.json',state)
 mark()
 try:
  source=out/'batch.c';source.write_text('#include "'+str(SRC.parent.parent/'experimental/deck-scene-source/deck-scene-contract.h')+'"\n#include "'+str(SRC/'native-alu.h')+'"\n'+r'''
struct row {uint32_t op,a,b,sr,want,wantsr,got,gotsr;};
void run(struct row *r,uint32_t n){
 struct biwn_deck_context s;
 for(uint32_t i=0;i<n;i++,r++){
  uint32_t a=r->a,b=r->b,op=r->op,v=a;s.cpu.sr=(uint16_t)r->sr;
  if(op<2)native_deck_nz(&s,a,op?32:16);
  else if(op<6)v=native_deck_alu(&s,a,b,(op-2)&1,((op-2)>>1)&1);
  else if(op<10)v=native_scene_alu16(&s,a,b,(op-6)&1,((op-6)>>1)&1);
  else v=native_scene_shift(&s,a,b,op==10);
  r->got=v;r->gotsr=s.cpu.sr;
 }
}
''')
  prefix=ROOT/'tools/m68k-elf/bin/m68k-elf-';elf=out/'batch.elf';binary=out/'batch.bin'
  command=[str(prefix)+'gcc','-m68000','-msoft-float','-std=c11','-Os','-ffreestanding','-fno-builtin','-nostdlib','-Wall','-Wextra','-Werror','-Dinline=inline __attribute__((always_inline))','-Wl,-Ttext='+hex(CODE)+',--entry,run',str(source),'-o',str(elf)]
  p=subprocess.run(command,capture_output=True,text=True);(out/'compiler.log').write_text(p.stdout+p.stderr);assert not p.returncode,p.stderr
  subprocess.run([str(prefix)+'objcopy','-O','binary',str(elf),str(binary)],check=True)
  payload=binary.read_bytes();assert len(payload)<STOP-CODE
  allrows=[(*x,*expected(*x),0xdeadbeef,0xdeadbeef)for x in vectors()];save(out/'vectors.json',allrows)
  engine=base.Engine();records=[];completed=0
  try:
   for supervisor in [False,True]:
    for first in range(0,len(allrows),4096):
     rows=allrows[first:first+4096];data=b''.join(struct.pack('>8I',*x)for x in rows)
     memory=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());memory[CODE:CODE+len(payload)]=payload;memory[STOP:STOP+2]=bytes.fromhex('60fe');memory[DATA:DATA+len(data)]=data
     memory[SP:SP+12]=struct.pack('>3I',STOP,DATA,len(rows));engine.native.device.seed(bytes(memory),0)
     cpu=base.CPU();cpu.registers[15]=SP;cpu.pc=CODE;cpu.sr=0x2000 if supervisor else 0;cpu.usp=0x1d8000 if supervisor else SP;cpu.ssp=SP if supervisor else 0x1ff000;engine.set_cpu(cpu,True)
     for chunks in range(2000):
      engine.core.m68k_execute(10000)
      if engine.cpu().pc==STOP:break
     else:raise AssertionError(('batch execution bound',first,supervisor,hex(engine.cpu().pc)))
     got=engine.native.device.ram();assert got[CODE:CODE+len(payload)]==payload
     assert got[:DATA]==memory[:DATA]and got[DATA+len(data):SP-512]==memory[DATA+len(data):SP-512]and got[SP+12:]==memory[SP+12:],'write outside table/private stack'
     for i,row in enumerate(rows):
      actual=struct.unpack_from('>8I',got,DATA+i*32)
      if actual[:6]!=row[:6]or actual[6:]!=row[4:6]:
       save(out/'counterexample.json',dict(supervisor=supervisor,index=first+i,row=row,actual=actual));raise AssertionError(out/'counterexample.json')
     completed+=len(rows);records.append(dict(supervisor=supervisor,first=first,cases=len(rows),execute_chunks=chunks+1));state.update(status='checking',completed=completed);mark();print('completed',completed,flush=True)
  finally:engine.native.close()
  save(out/'batches.json',records);paths=[Path(__file__),SRC/'native-alu.h',source,binary,out/'vectors.json',out/'batches.json',SRC.parent.parent/'experimental/deck-scene-source/deck-scene-contract.h',SRC.parent.parent/'experimental/deck-coordinate-update-v2/deck-coordinate-contract.h']
  state.update(status='terminal_native_ALU_boundary_random_CCR_banks_match',completed=completed,vectors_per_bank=len(allrows),all_incoming_CCR=True,physical_stack_banks=2,compiler_command=command,source_sha256={str(p):sha(p)for p in paths},scope=__doc__);mark();print(state['status'],completed,flush=True)
 except BaseException as e:state.update(status='terminal_native_ALU_primitive_check_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
