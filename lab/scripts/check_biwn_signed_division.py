"""Complete normal-return original E588 signed division versus portable C."""
import argparse,ctypes as c,json,os,random,subprocess
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE
from unicorn.m68k_const import *
import check_biwn_world_update as world
ROOT=world.ROOT;SP=world.SP;STOP=world.STOP
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def cases():
 values=[0,1,2,299,300,301,0x7fff,0x8000,0xffff,0x10000,0x10001,0x7fffffff,0x80000000,0x80000001,0xffff0000,0xfffffffe,0xffffffff]
 rows=[[n,d]for n in values for d in values if d];rng=random.Random(0xe588)
 while len(rows)<2048:rows.append([rng.getrandbits(32),rng.getrandbits(32)or 1])
 return rows

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opts=ap.parse_args();out=ROOT/'verification/biwn-signed-division'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 src=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libdivision.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(src/'biwn_signed_division.c'),'-o',str(library)]
 run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
 fn=c.CDLL(str(library)).biwn_signed_division;fn.argtypes=[c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32),c.POINTER(c.c_uint32)];fn.restype=c.c_int
 snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();session=__import__('pathlib').Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();assert world.select.stage.digest(image)==world.select.stage.STAGE_SHA and snapshot[0xe588:0xe60a]==image[0xe588-0x4000:0xe60a-0x4000]
 vectors=cases();vectors=vectors[:opts.limit]if opts.limit else vectors;coverage=set();rows=[];rng=random.Random(0xe60a)
 for i,(n,d)in enumerate(vectors):
  cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,snapshot);args=n.to_bytes(4,'big')+d.to_bytes(4,'big');cpu.mem_write(SP,STOP.to_bytes(4,'big')+args);incoming=[rng.getrandbits(32)for _ in world.REGS]
  for reg,v in zip(world.REGS,incoming):cpu.reg_write(reg,v)
  cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP)
  def code(e,a,w,_):assert 0xe588<=a<0xe60a;coverage.add(a)
  cpu.hook_add(UC_HOOK_CODE,code);cpu.emu_start(0xe588,STOP,count=512,timeout=500000);assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
  for index,reg in enumerate(world.REGS):
   if index not in[0,1,8,9]:assert cpu.reg_read(reg)==incoming[index]
  assert bytes(cpu.mem_read(SP+4,8))==args
  ram=bytes(cpu.mem_read(0,0x200000));assert ram[:SP-2]==snapshot[:SP-2]and ram[SP+12:]==snapshot[SP+12:]
  q=c.c_uint32(0xa55aa55a);r=c.c_uint32(0x5aa55aa5);status=fn(n,d,c.byref(q),c.byref(r));actual=[cpu.reg_read(UC_M68K_REG_D0),cpu.reg_read(UC_M68K_REG_D1)]
  assert status==0 and[q.value,r.value]==actual,(i,hex(n),hex(d),actual,[q.value,r.value])
  rows.append({'numerator':n,'denominator':d,'quotient_D0':q.value,'remainder_D1':r.value,'original_C_preserved_registers_stack_and_RAM_match':True})
 save(out/'fixtures.json',rows);decoded,_=world.select.binary_tools.m68k_instructions(snapshot[0xe588:0xe60a],0xe588);missing=[x for x in decoded if x['address']not in coverage];save(out/'decode.json',{'instructions':decoded,'uncovered':missing})
 if opts.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'cases':len(rows),'directory':str(out)}));return
 assert[hex(x['address'])for x in missing]==['0xe606','0xe608']
 q=c.c_uint32(0xa55aa55a);r=c.c_uint32(0x5aa55aa5);guards=[]
 for n,d,qp,rp,expected in[(1,2,None,c.byref(r),1),(1,2,c.byref(q),None,1),(1,2,c.byref(q),c.byref(q),1),(1,0,c.byref(q),c.byref(r),2),(0x80000000,0,c.byref(q),c.byref(r),2)]:
  assert fn(n,d,qp,rp)==expected and q.value==0xa55aa55a and r.value==0x5aa55aa5;guards.append({'numerator':n,'denominator':d,'status':expected,'outputs_unchanged':True})
 save(out/'guards.json',guards)
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'original_signed_division_normal_returns_match_C','directory':str(out),'CPU_cases':len(rows),'CPU_instruction_coverage':[len(coverage),len(decoded)],'normal_return_instruction_coverage':[len(coverage),len(decoded)-2],'excluded_zero_divisor_exception_instructions':['0xe606','0xe608'],'host_guards':len(guards),'portable_components':1,'interval':'[0xe588,0xe60a)','original_bytes':130,'stage_sha256':world.select.stage.STAGE_SHA,'source_sha256':{name:world.select.binary_tools.sha(src/name)for name in['biwn_signed_division.c','biwn_signed_division.h']},'compiler':command,'matched':['Signed32 quotientD0/remainderD1, truncation towardzero and numerator-signed remainder for every nonzero divisor. INT_MIN/-1 rawbits wrap.','Fast DIVU and full32bit shift/ADDX/subtract paths, allnormalreturninstructions, preserved D2-D7/A2-A6, balanced stack, untouched argumentbytes and externalRAM.'],'limits':['Zero-divisor original processor exception path is excluded; C returns hosterror without outputmutation. FullCCR/caller-savedA0/A1 excluded.','Not yet connected to dispatcher/taskruntime; no complete gameframes.']}
 save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-signed-division-checks.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
