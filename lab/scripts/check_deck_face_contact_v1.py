"""Complete Deck face-contact caller vs original CPU, with explicit pad/helper fixtures."""
import argparse,ctypes as c,json,os,random,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_deck_scene_source_v1 as scene
ROOT=scene.ROOT;CPU=scene.CPU;Bus=scene.Bus;SERVICE=scene.SERVICE;SP=scene.SP;STOP=scene.STOP
SRC=ROOT/'projects/black-ice-white-noise/restoration/experimental/deck-face-contact'
scene.ROOTS={0x1186a:0x11ad4};scene.HELPERS={0x10c6e,0x10cb6}
save=scene.save;sha=scene.sha;cpu_dict=scene.cpu_dict
class Engine(scene.Engine):
 def helper(self,memory,state,target,case,number):
  assert target in scene.HELPERS
  for n in [0,1,8,9]:state.registers[n]=(target*0x10203+number*0x1234567+case['variant']*71+n*0x123abcd)&0xffffffff
  state.sr=(state.sr&0xffe0)|((case['variant']+number*13)&31);state.pc=target+2
  a=0x70000+number*4;memory[a:a+4]=((target<<8|number)&0xffffffff).to_bytes(4,'big')
  if target==0x10c6e:
   memory[0x403dc:0x403e0]=(case['variant']%8).to_bytes(4,'big')
   if case['variant']%17==0:state.registers[2]=(state.registers[2]&0xffff0000)|(0 if case['variant']&1 else 5)
   if case['variant']%7==0:memory[0x400e6:0x400ea]=(0x90000).to_bytes(4,'big')
def fixtures():
 baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rng=random.Random(0x1186a)
 kinds=[0,1,2,3,4,5,6,0xffff];points=[(32,32,32)]
 for axis in range(3):
  for value in [-1,0,1,31,32,33,63,64,65]:
   point=[32,32,32];point[axis]=value;points.append(tuple(point))
 points += [(0x7fffffff,0,0),(0x80000000,0,0),(0,0x7fffffff,0),(0,0,0x80000000)]
 for i in range(2112):
  kind=kinds[i%8];count=i//256 if i<1792 else 0xffff if i<1856 else 1+i%6
  point=points[(i//8)%32]if i<1792 else (32,32,32)
  state=CPU();state.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[SP];state.pc=0x1186a;state.sr=(0x2000 if(i//32)&1 else 0)|(i%32)|((i//256)%8)<<8
  state.usp=0x1d8000 if state.sr&0x2000 else SP;state.ssp=SP if state.sr&0x2000 else 0x1ff000
  # Kinds >5 inherit these bounds in the original machine code.
  for register,value in [(1,0),(14,64),(13,0),(12,64),(11,0),(4,64)]:state.registers[register]=value
  ram=bytearray(baseline);ram[SP-256:SP+32]=rng.randbytes(288);ram[SP:SP+4]=STOP.to_bytes(4,'big')
  def put(a,w,v):ram[a:a+w]=(v&((1<<(w*8))-1)).to_bytes(w,'big')
  index=(i//16)%16;put(0x400e6,4,0x80000);put(0x80000,2,index)
  position=[0,0,0]if i<1792 or kind>5 else [0x7fffffe0,0xfffffff0,0x80000020]
  # High count fixtures always hit the first face, avoiding an unbounded
  # oracle walk. Signed extreme boxes/offsets are exercised below separately.
  if i>=1792:position=[0,0,0]
  for j,value in enumerate(position):put(0x80004+j*4,4,value)
  edges=[0,1,0xffffffff,0x7fffffff,0x80000000,0x80000001,0x7ffffffe]
  box=[0,0,0,64,64,64]if i<1856 else [rng.choice(edges)for _ in range(6)]
  for j,value in enumerate(box):put(0x400c4+index*32+4+j*4,4,value)
  for a in range(0x3d6ca,0x3d712,4):put(a,4,0 if i<1856 else rng.choice(edges))
  for j in range(min(count,6)):
   put(0x80010+j*20,2,(kind+j)%6 if kind<6 else kind)
  put(0x80088,2,count)
  if i>=1856:
   point=tuple(rng.choice(edges)for _ in range(3))
   for j in range(3):put(0x80004+j*4,4,rng.choice(edges))
  for j,value in enumerate(point):put(0x400ec+j*4,4,value)
  for j in range(8):put(0x403e0+j*2,2,rng.getrandbits(16))
  put(0x403dc,4,0)
  # Descriptor index1 aliases the global descriptor-pointer bytes. Keep a
  # valid descriptor after filling the box; compare the resulting aliases.
  put(0x400e6,4,0x80000)
  yield bytes(ram),state,dict(root=0x1186a,variant=i,kind=kind,count=count,point=point,mutate_later_tag=False)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);ap.add_argument('--start',type=int,default=0);ap.add_argument('--source',type=Path,default=SRC/'deck-face-contact.c');ap.add_argument('--output',type=Path);args=ap.parse_args()
 out=args.output or ROOT/'verification/deck-face-contact'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True,exist_ok=True);print(out,flush=True)
 state=dict(status='compiling',pid=os.getpid(),directory=str(out),source=str(args.source),whole_game_complete=False,new_training=False,authorship='Coordinator structured recovery;face-selection/application helper bodies separate fixtures.')
 def mark():save(out/'protocol.json',state)
 mark();library=out/'libdeck-face-contact.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(SRC),str(args.source),'-o',str(library)]
 try:
  p=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
  fn=c.CDLL(str(library)).biwn_deck_face_contact_call;fn.argtypes=[c.POINTER(Bus),c.POINTER(CPU),SERVICE,c.c_void_p,c.c_uint32];fn.restype=c.c_int
  engine=Engine();selected=list(fixtures())[args.start:];selected=selected[:args.limit]if args.limit else selected;rows=[];coverage=set();guards=[]
  try:
   for i,(ram,initial,case)in enumerate(selected):
    try:expected,cpu,entries,covered=engine.original(ram,initial,case)
    except BaseException as error:
     failed=engine.cpu();memory=engine.native.device.ram();sp=failed.registers[15];save(out/'oracle-failure.json',dict(case=case,error=repr(error),CPU=cpu_dict(failed),initial_CPU=cpu_dict(initial),stack=memory[max(0,sp-64):sp+64].hex()));raise
    status,actual,got,observed,events,errors=engine.translated(fn,ram,initial,case)
    if status or errors or expected!=actual or cpu_dict(cpu)!=cpu_dict(got)or entries!=observed:
     save(out/'counterexample.json',dict(case=case,status=status,errors=errors,original_CPU=cpu_dict(cpu),C_CPU=cpu_dict(got),original_entries=entries,C_entries=observed,RAM_differences=[[hex(j),a,b]for j,(a,b)in enumerate(zip(expected,actual))if a!=b][:32]));raise AssertionError(out/'counterexample.json')
    coverage|=covered;rows.append(dict(case=case,CPU=cpu_dict(cpu),RAM=sha(expected),helper_entries=len(entries),C_events=len(events),full_CPU_RAM_helper_entry_match=True))
    if i%128==0:state.update(status='checking',completed=i+1,total=len(selected));mark();print('case',i+1,'/',len(selected),flush=True)
   if not args.limit and not args.start:
    ram,initial,case=next(x for x in selected if x[2]['count']==1 and x[2]['kind']==0 and x[2]['point']==(32,32,32))
    status,_,_,_,events,_=engine.translated(fn,ram,initial,case);assert status==0
    for fail in range(len(events)):
     status,_,got,_,_,errors=engine.translated(fn,ram,initial,case,fail=fail);assert status==2 and not errors and cpu_dict(got)==cpu_dict(initial),(fail,status);guards.append(dict(data_failure=fail))
    for fault,expect in [('error',3),('stack',5),('return',5)]:
     status,_,got,_,_,errors=engine.translated(fn,ram,initial,case,service_fault=fault);assert status==expect and not errors and cpu_dict(got)==cpu_dict(initial);guards.append(dict(service_fault=fault))
    for budget,expect in [(0,1),(1,4)]:
     status,_,got,_,_,errors=engine.translated(fn,ram,initial,case,budget=budget);assert status==expect and not errors and cpu_dict(got)==cpu_dict(initial);guards.append(dict(helper_budget=budget))
  finally:engine.native.close()
  baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();decoder=scene.Cs(scene.CS_ARCH_M68K,scene.CS_MODE_BIG_ENDIAN|scene.CS_MODE_M68K_000);addresses={x.address for x in decoder.disasm(baseline[0x1186a:0x118b4],0x1186a)}|{x.address for x in decoder.disasm(baseline[0x118c0:0x11ad4],0x118c0)}
  assert args.limit or args.start or coverage==addresses,sorted(addresses-coverage)
  save(out/'cases.json',rows);save(out/'guards.json',guards)
  paths=[args.source,SRC/'deck-face-contact.h',SRC.parent/'deck-scene-source/deck-scene-contract.h',SRC.parent/'deck-coordinate-update-v2/deck-coordinate-contract.h',Path(__file__),Path(scene.__file__),Path(scene.coordinate.__file__)]
  deps=[ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib',ROOT/'render-assets/biwn-inventory-baseline.bin']
  state.update(status='terminal_preflight_pass'if args.limit or args.start else'terminal_complete_readable_Deck_face_contact_original_CPU_match',completed=len(rows),instruction_locations=[len(coverage),len(addresses)],host_error_cases=len(guards),source_sha256={str(p.resolve()):sha(p.read_bytes())for p in paths},native_dependencies_sha256={str(p):sha(p.read_bytes())for p in deps},scope='Complete618byte1186A..11AD4callerwithpinned12bytejumptableandouterRTS.2112finitecasesincluding256signed/overflowarithmeticfixtures,sixfacekindsplus6/FFFFstale-boundbehavior,counts0..6andFFFFearlyhit,all32CCR/bothbanks,axisboundsandsignedextremes,descriptorindices,helperclobbers/D2mutation/descriptorchanges. FullCPU/2MBRAM/privateframes/helperentrycompare. Helpersdeclaredfixtures;not timing/GPU/hardware/naturalgameplay/fullgamerebuildproof.');mark()
  if not args.limit and not args.start:save(ROOT/'verification/Deck-face-contact-current.json',state)
  print(state['status'],flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
