"""Source101E0 -> resident acquire/real allocator; pending resource suspension."""
import argparse,ctypes as c,json,random,subprocess,os
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_media_setup_cpu as media
ROOT=media.ROOT;save=media.save;sha=media.sha
parser=argparse.ArgumentParser();parser.add_argument('--patched',action='store_true');opts=parser.parse_args()
out=ROOT/'verification/BIWN-NPC-initializer-resource-graph'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);src=ROOT/'projects/black-ice-white-noise/restoration';npc=src/'biwn_npc_cpu.c'
if opts.patched:
 npc=src/'experimental/biwn_npc_resource_wait_cpu.c';text=(src/'biwn_npc_cpu.c').read_text();old='status==6&&s->cpu.pc==0xdf60u';assert text.count(old)==1;text=text.replace(old,'status==6&&(s->cpu.pc==0xdf60u||s->cpu.pc==0xdf8cu)');npc.write_text(text)
names=[npc,src/'biwn_resource_cpu.c',src/'biwn_media_setup_cpu.c'];lib=out/'libinitializer.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(src),*[str(p)for p in names],'-o',str(lib)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr);assert not build.returncode,build.stderr
source=Path(json.loads((ROOT/'verification/natural-actor13-task-current.json').read_text())['directory']);baseline=(source/'native-RAM.bin').read_bytes();runtime=media.Runtime(lib,[]);fn=runtime.lib.biwn_npc_cpu_call;fn.argtypes=runtime.fn.argtypes;fn.restype=c.c_int;resources=runtime.lib.biwn_resource_cpu_body;resources.argtypes=runtime.fn.argtypes;resources.restype=c.c_int;rng=random.Random(0x101e0);results=[];resource_entries=[0x1af04,0x152a2,0x15200,0x1545c,0x1b002,0xe3e0,0xe3ee];coverage=set()
try:
 for scenario in ['resident','invalid_descriptor','handle_exhaustion','pending']:
  for supervisor in [False,True]:
   for references in [1,2,0xffff]:
    ram=bytearray(baseline);obj=0x49d6c;resource=24;handle=int.from_bytes(ram[0x15b536:0x15b53a],'big');payload=int.from_bytes(ram[handle:handle+4],'big')
    def put(a,w,v):ram[a:a+w]=(v&((1<<(8*w))-1)).to_bytes(w,'big')
    put(obj,2,12);put(0x15b534,2,resource);put(0x15b53a,2,references);put(0x15b53c,2,0 if scenario=='pending'else 1)
    if scenario=='invalid_descriptor':put(0x464d0+resource*12,4,0)
    if scenario=='handle_exhaustion':
     for address in range(0x112960,0x112d60,4):
      if address!=handle:put(address,4,1)
    initial=media.CPU();initial.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[0x1ff000];initial.pc=0x101e0;initial.sr=(0x2000 if supervisor else 0)|0x700|len(results)%32;initial.usp=0x1fe000 if supervisor else 0x1ff000;initial.ssp=0x1ff000 if supervisor else 0x200000;offset=0
    for width,value in [(4,0x1ffff0),(4,obj),(2,resource),(4,0x2d000),(4,0x43820)]:put(initial.registers[15]+offset,width,value);offset+=width
    views={};RAMs={}
    for mode in ['native','C']:
     runtime.reset(bytes(ram),0);calls=[];errors=[]
     if mode=='native':
      runtime.seed_cpu(initial);trace=[]
      for _ in range(50000):
       pc=runtime.cpu().pc
       if pc in [0x1ffff0,0xdf8c]:break
       coverage.add(pc);trace.append(pc)
       if pc in resource_entries:calls.append(hex(pc))
       runtime.core.m68k_execute(1)
      else:save(out/'native-bound.json',dict(scenario=scenario,PC=hex(pc),trace=list(map(hex,trace[-40:]))));raise AssertionError('Initializer graph bound')
      actual=runtime.cpu();status=6 if actual.pc==0xdf8c else 0
     else:
      def rd(w):
       def cb(_,a,v):
        if not 0<=a<=0x200000-w:errors.append(('read',hex(a)));return 1
        v[0]=runtime.read(a,w);return 0
       return cb
      def wr(w):
       def cb(_,a,v):
        if not 0<=a<=0x200000-w:errors.append(('write',hex(a)));return 1
        runtime.write(a,w,v);return 0
       return cb
      world=media.scheduler.cleanup.world;callbacks=[world.R8(rd(1)),world.R16(rd(2)),world.R32(rd(4)),world.W16(wr(2)),world.W32(wr(4)),media.W8(wr(1))];bus=media.Bus(*callbacks[:5],world.CALL(),None,0)
      def service(_,passed,cpu,target):
       if target in resource_entries:calls.append(hex(target));return resources(passed,cpu,callbacks[5],callback,None,100000,1)
       errors.append(hex(target));return 1
      callback=media.world_cpu.SERVICE(service);actual=media.CPU.from_buffer_copy(bytes(initial));status=fn(c.byref(bus),c.byref(actual),callbacks[5],callback,None,100000,1)
     views[mode]=dict(CPU=media.scheduler.cpu_dict(actual),hardware=runtime.snapshot()['hardware'],calls=calls,status=status);RAMs[mode]=runtime.device.ram()
    equal=views['native']==views['C']and RAMs['native']==RAMs['C']
    row=dict(scenario=scenario,supervisor=supervisor,references=references,equal=equal,views=views,RAM_equal=RAMs['native']==RAMs['C']);results.append(row)
    if not equal:save(out/'mismatch.json',row);raise AssertionError(str(out/'mismatch.json'))
 report=dict(status='NPC_initializer_resident_acquire_allocator_and_pending_wait_match',directory=str(out),cases=len(results),patched=opts.patched,source_sha256={p.name:sha(p.read_bytes())for p in names},compiler=cmd,results=results,limits=['Controlled fixture remaps captured resident model0 cache record to resource24; actual asset24/disk loading is not proved.','Real101E0/1AF04/152A2/1B002 control flow executes. Pendingready0 stops before sourceDF8C; scheduler wait/resumption is separate.','WholeCPU/stackbanks/RAM/checkeddevices/calls match; no full game/ordinaryboot proof.'],whole_game_complete=False);save(out/'report.json',report);save(ROOT/'verification/NPC-initializer-resource-graph-current.json',report);print(report['status'],len(results),flush=True)
except BaseException as error:save(out/'failure.json',dict(error=repr(error),cases_passed=sum(x['equal']for x in results),patched=opts.patched));raise
finally:runtime.oracle.close()
