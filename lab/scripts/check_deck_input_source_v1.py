"""Complete Deck input caller vs original CPU, with explicit pad/helper fixtures."""
import argparse,ctypes as c,json,os,random,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_deck_scene_source_v1 as scene
ROOT=scene.ROOT;CPU=scene.CPU;Bus=scene.Bus;SERVICE=scene.SERVICE;SP=scene.SP;STOP=scene.STOP
SRC=ROOT/'projects/black-ice-white-noise/restoration/experimental/deck-input-source'
scene.ROOTS={0x11b4c:0x11d1a};scene.HELPERS={0xe4c0,0x10c6e,0x10e72,0x10cb6,0x1102a}
save=scene.save;sha=scene.sha;cpu_dict=scene.cpu_dict
class Engine(scene.Engine):
 def helper(self,memory,state,target,case,number):
  assert target in scene.HELPERS
  for n in [0,1,8,9]:state.registers[n]=(target*0x10203+number*0x1234567+case['variant']*71+n*0x123abcd)&0xffffffff
  state.sr=(state.sr&0xffe0)|((case['variant']+number*13)&31);state.pc=target+2
  a=0x70000+number*4;memory[a:a+4]=((target<<8|number)&0xffffffff).to_bytes(4,'big')
  if target==0xe4c0:
   memory[0x49ba4:0x49ba8]=case['held'].to_bytes(4,'big');memory[0x49bac:0x49bb0]=case['pressed'].to_bytes(4,'big')
  elif target==0x10c6e:
   memory[0x403dc:0x403e0]=(number%8).to_bytes(4,'big')
   if case['variant']%7==0:memory[0x400e6:0x400ea]=(0x90000).to_bytes(4,'big')
def fixtures():
 baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rng=random.Random(0x11b4c);cases=[]
 speeds=[0,1,14,15,16,17,0xfffffff1,0xfffffff0,0xffffffef,0xffffffff,0x7fffffff,0x80000000]
 bits=[4,19,7,3,18,6]
 for i in range(2048):
  held=([0,1<<20,1<<21,(1<<20)|(1<<21)][i&3]|[0,1<<22,1<<23,(1<<22)|(1<<23)][(i>>2)&3]|((i>>4)&1)<<25|((i>>5)&1)<<9)
  mask=(i*37+i//64)&63;pressed=sum(1<<b for k,b in enumerate(bits)if mask&(1<<k))|((i>>6)&1)<<13|((i>>7)&1)<<16
  state=CPU();state.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[SP];state.pc=0x11b4c;state.sr=(0x2000 if(i//32)&1 else 0)|(i%32)|((i//256)%8)<<8
  state.usp=0x1d8000 if state.sr&0x2000 else SP;state.ssp=SP if state.sr&0x2000 else 0x1ff000
  ram=bytearray(baseline);ram[SP-256:SP+32]=rng.randbytes(288);ram[SP:SP+4]=STOP.to_bytes(4,'big')
  def put(a,w,v):ram[a:a+w]=(v&((1<<(w*8))-1)).to_bytes(w,'big')
  count=[0,1,2,3,4,5,6,0xffff][i//256];speed=speeds[(i//8)%len(speeds)]
  for a,w,v in [(0x400e6,4,0x80000),(0x80088,2,count),(0x90088,2,(count+3)&0xffff),(0x40104,4,speed),(0x403dc,4,0)]:put(a,w,v)
  for a in [0x40400,0x403cc]:put(a,2,rng.getrandbits(16))
  for a in [0x40402,0x40406,0x4040a,0x49ba4,0x49bac]:put(a,4,rng.getrandbits(32))
  for j in range(8):put(0x403e0+2*j,2,rng.getrandbits(16))
  cases.append((bytes(ram),state,dict(root=0x11b4c,variant=i,held=held,pressed=pressed,faces=count,speed=speed,mutate_later_tag=False)))
 return cases
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);ap.add_argument('--source',type=Path,default=SRC/'deck-input-source.c');ap.add_argument('--output',type=Path);args=ap.parse_args()
 out=args.output or ROOT/'verification/deck-input-source'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True,exist_ok=True);print(out,flush=True)
 state=dict(status='compiling',pid=os.getpid(),directory=str(out),source=str(args.source),whole_game_complete=False,new_training=False,authorship='Coordinator structured recovery; poll/record/texture/reset bodies separate fixtures.')
 def mark():save(out/'protocol.json',state)
 mark();library=out/'libdeck-input.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(SRC),str(args.source),'-o',str(library)]
 try:
  p=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
  fn=c.CDLL(str(library)).biwn_deck_input_call;fn.argtypes=[c.POINTER(Bus),c.POINTER(CPU),SERVICE,c.c_void_p,c.c_uint32];fn.restype=c.c_int
  engine=Engine();selected=fixtures();selected=selected[:args.limit]if args.limit else selected;rows=[];coverage=set();guards=[]
  try:
   for i,(ram,initial,case)in enumerate(selected):
    expected,cpu,entries,covered=engine.original(ram,initial,case);status,actual,got,observed,events,errors=engine.translated(fn,ram,initial,case)
    if status or errors or expected!=actual or cpu_dict(cpu)!=cpu_dict(got)or entries!=observed:
     save(out/'counterexample.json',dict(case=case,status=status,errors=errors,original_CPU=cpu_dict(cpu),C_CPU=cpu_dict(got),original_entries=entries,C_entries=observed,RAM_differences=[[hex(j),a,b]for j,(a,b)in enumerate(zip(expected,actual))if a!=b][:32]));raise AssertionError(out/'counterexample.json')
    coverage|=covered;rows.append(dict(case=case,CPU=cpu_dict(cpu),RAM=sha(expected),helper_entries=len(entries),C_events=len(events),full_CPU_RAM_helper_entry_match=True))
    if i%128==0:state.update(status='checking',completed=i+1,total=len(selected));mark();print('case',i+1,'/',len(selected),flush=True)
   if not args.limit:
    ram,initial,case=next(x for x in selected if x[2]['faces']==6 and x[2]['pressed']&16 and x[2]['pressed']&(1<<16))
    status,_,_,_,events,_=engine.translated(fn,ram,initial,case);assert status==0
    for fail in range(len(events)):
     status,_,got,_,_,errors=engine.translated(fn,ram,initial,case,fail=fail);assert status==2 and not errors and cpu_dict(got)==cpu_dict(initial),(fail,status);guards.append(dict(data_failure=fail))
    for fault,expect in [('error',3),('stack',5),('return',5)]:
     status,_,got,_,_,errors=engine.translated(fn,ram,initial,case,service_fault=fault);assert status==expect and not errors and cpu_dict(got)==cpu_dict(initial);guards.append(dict(service_fault=fault))
    for budget,expect in [(0,1),(1,4)]:
     status,_,got,_,_,errors=engine.translated(fn,ram,initial,case,budget=budget);assert status==expect and not errors and cpu_dict(got)==cpu_dict(initial);guards.append(dict(helper_budget=budget))
  finally:engine.native.close()
  baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();decoder=scene.Cs(scene.CS_ARCH_M68K,scene.CS_MODE_BIG_ENDIAN|scene.CS_MODE_M68K_000);addresses={x.address for x in decoder.disasm(baseline[0x11b4c:0x11d1a],0x11b4c)}
  assert args.limit or coverage==addresses,sorted(addresses-coverage)
  save(out/'cases.json',rows);save(out/'guards.json',guards)
  paths=[args.source,SRC/'deck-input-source.h',SRC.parent/'deck-scene-source/deck-scene-contract.h',SRC.parent/'deck-coordinate-update-v2/deck-coordinate-contract.h',Path(__file__),Path(scene.__file__),Path(scene.coordinate.__file__)]
  deps=[ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib',ROOT/'render-assets/biwn-inventory-baseline.bin']
  state.update(status='terminal_preflight_pass'if args.limit else'terminal_complete_readable_Deck_input_original_CPU_match',completed=len(rows),instruction_locations=[len(coverage),len(addresses)],host_error_cases=len(guards),source_sha256={str(p.resolve()):sha(p.read_bytes())for p in paths},native_dependencies_sha256={str(p):sha(p.read_bytes())for p in deps},scope='Complete462byte11B4Ccaller includingRTS. Finite2048cases;allheld-axis precedence/modifier/overlay combinations,64face-edge masks,dirty/reset,facecount0..6/FFFF,signedspeedbounds/INTlimits,bothbanks/allCCR,helperclobbers anddescriptor-pointer changes. FullCPU/2MBRAM/privateframes/calleeentryCPU-RAMcompare. Poll/texture/record/reset aredeclaredfixtures,notphysicalinput/fullGPU/naturalgameplay/IRQ/timingproof.');mark()
  if not args.limit:save(ROOT/'verification/Deck-input-source-current.json',state)
  print(state['status'],flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
