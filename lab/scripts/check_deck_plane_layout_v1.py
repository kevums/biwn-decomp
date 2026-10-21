"""Complete110D4 six-layout routine vs original68000, CPU/banks and full2MBRAM.

Finite seeded RAM aliases; instruction/jump-table bytes remain immutable.
No helper fixtures, emulator instruction interpreter in C, MMIO or IRQ claim.
"""
import argparse,ctypes as c,json,os,random,subprocess
from pathlib import Path
from datetime import datetime,timezone
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
import check_deck_geometry_helpers_v1 as h
ROOT=h.ROOT;CPU=h.CPU;Bus=h.Bus;SP=h.SP;STOP=h.STOP;save=h.save;sha=h.sha;cpu_dict=h.cpu_dict
SRC=ROOT/'projects/black-ice-white-noise/restoration/experimental/deck-plane-layout-v1'
RTS={0x11178,0x111e2,0x1124c,0x11382}
class Engine(h.Engine):
 def original(self,ram,initial,case):
  self.native.device.seed(ram,0);self.set_cpu(initial,True);seen=set()
  for steps in range(1000):
   state=self.cpu();pc=state.pc
   assert 0x110d4<=pc<0x11104 or 0x11110<=pc<0x11384,hex(pc)
   seen.add(pc);self.core.m68k_execute(1)
   if pc in RTS:break
  else:raise AssertionError('original plane layout work bound')
  return self.native.device.ram(),self.cpu(),seen,steps+1
 def translated(self,fn,ram,initial,fail=None):
  memory=bytearray(ram);events=[];errors=[]
  def reader(w):
   def cb(_,a,out):
    if fail==len(events):return 1
    if a+w>len(memory)or a&1:errors.append(['read',a,w]);return 1
    out[0]=int.from_bytes(memory[a:a+w],'big');events.append(['r',a,w,out[0]]);return 0
   return cb
  def writer(w):
   def cb(_,a,value):
    if fail==len(events):return 1
    if a+w>len(memory)or a&1:errors.append(['write',a,w]);return 1
    memory[a:a+w]=(value&((1<<(w*8))-1)).to_bytes(w,'big');events.append(['w',a,w,value]);return 0
   return cb
  w=h.base.scheduler.cleanup.world;callbacks=[w.R16(reader(2)),w.R32(reader(4)),w.W16(writer(2)),w.W32(writer(4))]
  bus=Bus(w.R8(),*callbacks,w.CALL(),None,0);state=CPU.from_buffer_copy(bytes(initial));status=fn(c.byref(bus),c.byref(state))
  return status,bytes(memory),state,events,errors
def fixtures():
 baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rng=random.Random(0x110d411110)
 for selector in [0,1,2,3,4,5,6,7,0x7fff,0x8000,0xffff]:
  for i in range(128):
   memory=bytearray(baseline);state=CPU();state.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[SP];state.pc=0x110d4;state.sr=(0x2000 if i&1 else 0)|((i//2)%32)|(0x100 if i>=64 else 0);state.usp=0x1d8000 if i&1 else SP;state.ssp=SP if i&1 else 0x1ff000
   index=[0,1,7,0x7ff,0x1000,0x3fff,0x7fff][(i//8)%7];base=0x400c4+index*32
   destination=[0x90000,base-0x24,base-0x20,base-0x12,base,base+2,0x80000-0x24,SP-0x20][i%8]
   values=[0,1,0xfff,0x1000,0x7fff,0x8000,0xffff,0xfffe]
   for n in range(16):memory[base+2*n:base+2*n+2]=values[(i+n)%len(values)].to_bytes(2,'big')
   memory[SP-128:SP+128]=rng.randbytes(256)
   memory[0x80000:0x80002]=index.to_bytes(2,'big')
   for a,w,v in [(SP,4,STOP),(SP+4,4,0x80000),(SP+8,4,destination),(SP+12,2,selector)]:memory[a:a+w]=v.to_bytes(w,'big')
   assert len(memory)==0x200000
   yield bytes(memory),state,dict(selector=selector,variant=i,index=index,source=base,destination=destination,alias_kind=i%8)
def compile_source(source,out,label):
 lib=out/(label+'.dylib');p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(SRC),str(source),str(SRC/'plane-adapter.c'),'-o',str(lib)],capture_output=True,text=True);(out/(label+'-compiler.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 fn=c.CDLL(str(lib)).biwn_plane_layout_call;fn.argtypes=[c.POINTER(Bus),c.POINTER(CPU)];fn.restype=c.c_int;return fn,lib
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);ap.add_argument('--source',type=Path,default=SRC/'coordinator-reference.c');args=ap.parse_args()
 out=ROOT/'verification/deck-plane-layout-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);state=dict(status='compiling',directory=str(out),pid=os.getpid(),whole_game_complete=False,new_training=False,native_disc_changed=False)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/deck-plane-layout-v1-current.json',state)
 mark()
 try:
  fn,lib=compile_source(args.source,out,'plane');e=Engine();rows=[];seen=set();samples={};guards=[];negative=[]
  try:
   for ram,initial,case in fixtures():
    if args.limit and case['variant']>=args.limit:continue
    expected,cpu,covered,steps=e.original(ram,initial,case);status,actual,got,events,errors=e.translated(fn,ram,initial)
    if status or errors or expected!=actual or cpu_dict(cpu)!=cpu_dict(got):
     save(out/'counterexample.json',dict(case=case,status=status,errors=errors,original_CPU=cpu_dict(cpu),C_CPU=cpu_dict(got),RAM_differences=[[hex(a),x,y]for a,(x,y)in enumerate(zip(expected,actual))if x!=y][:32]));raise AssertionError(out/'counterexample.json')
    seen|=covered;rows.append(dict(case=case,original_steps=steps,C_events=len(events),full_CPU_banks_and_RAM_match=True))
    if case['variant']==0 and case['selector']in [0,1,6]:samples[case['selector']]=(ram,initial,events)
    if len(rows)%64==0:state.update(status='checking',completed=len(rows));mark();print('completed',len(rows),flush=True)
   if not args.limit:
    for selector,(ram,initial,events)in samples.items():
     for index in range(len(events)):
      status,_,got,_,errors=e.translated(fn,ram,initial,fail=index);assert status==2 and not errors and cpu_dict(got)==cpu_dict(initial),(selector,index,status)
      guards.append(dict(selector=selector,failure_at=index))
    # Compile whole-function mutations and require the same CPU/RAM gate to
    # reject each, including aliases that expose cached source snapshots.
    original=args.source.read_text();mutations={
     'shift_scale':('n<3;n++','n<2;n++'),
     'D1_high_word':('(r[1]&0xffff0000u)|v','v'),
     'lost_X':('s->cpu.pc=end[selector];','s->cpu.sr&=~0x10u;s->cpu.pc=end[selector];'),
     'cached_source':('for(unsigned n=0;n<12;n++){\n  unsigned field=fields[selector][n];v=deck_read(s,r[8]+(field&127u),2);','uint32_t cached[12];for(unsigned n=0;n<12;n++)cached[n]=deck_read(s,r[8]+(fields[selector][n]&127u),2);\n for(unsigned n=0;n<12;n++){\n  unsigned field=fields[selector][n];v=cached[n];')}
    for name,(old,new)in mutations.items():
     assert original.count(old)==1,name;source=out/(name+'.c');source.write_text(original.replace(old,new));bad,_=compile_source(source,out,name);rejected=None
     for ram,initial,case in fixtures():
      expected,cpu,_,_=e.original(ram,initial,case);status,actual,got,_,errors=e.translated(bad,ram,initial)
      if status or errors or expected!=actual or cpu_dict(cpu)!=cpu_dict(got):rejected=dict(case=case,status=status,CPU_match=cpu_dict(cpu)==cpu_dict(got),RAM_match=expected==actual);break
     assert rejected,name;negative.append(dict(mutation=name,rejected=True,counterexample=rejected))
  finally:e.native.close()
  baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();decoder=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000);addresses={x.address for a,b in [(0x110d4,0x11104),(0x11110,0x11384)]for x in decoder.disasm(baseline[a:b],a)}
  assert args.limit or seen==addresses,[hex(a)for a in addresses-seen]
  save(out/'cases.json',rows);save(out/'guards.json',guards);save(out/'negative-controls.json',negative)
  paths=[Path(__file__),args.source,SRC/'plane-contract.h',SRC/'plane-adapter.c',Path(h.__file__),out/'cases.json',out/'guards.json',out/'negative-controls.json',lib]
  state.update(status='terminal_plane_layout_preflight_pass'if args.limit else'terminal_complete_plane_layout_CPU_RAM_match',completed=len(rows),instruction_locations=[len(seen),len(addresses)],bus_error_cases=len(guards),negative_controls=len(negative),source_sha256={str(p):sha(p.read_bytes())for p in paths},baseline_sha256=sha(baseline),source=str(args.source),scope=__doc__+' Six valid and five invalid selectors;128cases each,bothbanks/all32CCR,seven source indices,eight alias patterns. Full instruction coverage excludes12jump-table data bytes. Native relocation,physical integration and full-game fidelity remain unverified.')
  mark();print(state['status'],len(rows),state['instruction_locations'],flush=True)
 except BaseException as error:state.update(status='terminal_plane_layout_checker_failed',error=repr(error));mark();raise
if __name__=='__main__':main()
