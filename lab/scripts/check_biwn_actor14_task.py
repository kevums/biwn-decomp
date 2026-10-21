"""Compare type14 source task against original CPU; helper ABI adversaries explicit."""
import ctypes as c,json,os,random,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_media_setup_cpu as media
ROOT=media.ROOT;save=media.save;sha=media.sha
out=ROOT/'verification/BIWN-actor14-task'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);src=ROOT/'projects/black-ice-white-noise/restoration';names=[src/'experimental/biwn_actor14_task_cpu.c',src/'biwn_startup_rng_math_cpu.c',src/'biwn_media_setup_cpu.c',src/'biwn_signed_division.c',src/'biwn_camera.c'];lib=out/'libproximity.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(src),*[str(p)for p in names],'-o',str(lib)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr);assert not build.returncode,build.stderr
obs=json.loads((ROOT/'verification/task-1b4e8-observation-current.json').read_text());baseline=(Path(obs['directory'])/'task-start-RAM.bin').read_bytes();mapping=json.loads((ROOT/'verification/actor14-task-generation.json').read_text());runtime=media.Runtime(lib,mapping['instructions_decoded']);fn=runtime.lib.biwn_actor14_task_cpu_body;fn.argtypes=runtime.fn.argtypes;fn.restype=c.c_int;math_fn=runtime.lib.biwn_startup_rng_math_cpu_body;math_fn.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU)];math_fn.restype=c.c_int;results=[];coverage=set();rng=random.Random(0x1b480);boundaries=[(0,0),(32,0),(33,0),(0,32),(0,33),(23,23),(-32,0),(-33,0),(31,1),(32,1)];case=0
try:
 vectors=[]
 for entry in [0x1a560,0x1a58e]:
  for slot in [None,0,39]:
   for retry in [False,True]:
    for dead in [0,1]:
     for distance in [0,255,256,4096,4097]:
      for supervisor in [False,True]:vectors.append(dict(entry=entry,slot=slot,retry=retry,dead=dead,distance=distance,supervisor=supervisor,mode=1,c8=2))
 for entry in [0x1a5d4,0x1a6d2]:
  for mode in [0,1,2,3,0x8000]:
   for distance in [0,255,256,4096,4097]:
    for dead in [0,1]:
     for c8 in [0,2]:
      for supervisor in [False,True]:vectors.append(dict(entry=entry,slot=0,retry=False,dead=dead,distance=distance,supervisor=supervisor,mode=mode,c8=c8))
 for flags in range(8):
  for sound_return in [0,1,2,3,4,5,0xffff]:
   for supervisor in [False,True]:vectors.append(dict(entry=0x1a5d4,slot=0,retry=False,dead=0,distance=0,supervisor=supervisor,mode=1,c8=2,message_flags=flags,sound_return=sound_return))
 for already_found in [0,1,0x8000]:
  for slot in [0,39]:
   for supervisor in [False,True]:vectors.append(dict(entry=0x1a58e,slot=slot,retry=False,dead=0,distance=0,supervisor=supervisor,mode=1,c8=2,already_found=already_found))
 for parameters in vectors:
      entry=parameters['entry'];slot=parameters['slot'];supervisor=parameters['supervisor'];record_address=0x49d6c+(slot or 0)*206;initial=media.CPU();initial.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[0x1ff000];initial.registers[2]=parameters.get("already_found",0);initial.registers[3]=0x49d6c;initial.registers[10]=record_address;initial.pc=entry;initial.sr=(0x2000 if supervisor else 0)|(0x700 if case%2 else 0)|(case%32);initial.usp=0x1fe000 if supervisor else 0x1ff000;initial.ssp=0x1ff000 if supervisor else 0x200000;ram=bytearray(baseline)
      for i in range(40):ram[0x49d6c+i*206:0x49d6e+i*206]=bytes(2)
      if slot is not None:
       for offset,w,v in [(0,2,14),(2,2,parameters['dead']),(0x6c,2,parameters['mode']),(0xc8,2,parameters['c8']),(0x5e,4,0x156789)]:ram[record_address+offset:record_address+offset+w]=(v&((1<<(8*w))-1)).to_bytes(w,'big')
      for bit,address in enumerate([0x462c0,0x462c2,0x462c4]):ram[address:address+2]=((parameters.get('message_flags',0)>>bit)&1).to_bytes(2,'big')
      views={};RAMs={}
      for mode in ['native','C']:
       runtime.reset(bytes(ram),0);calls=[];errors=[]
       retries=[0]
       def provider(s,target):
        widths={0x101e0:[4,2,4,4],0x10252:[4],0x1404c:[4],0xeb04:[4],0x13c9a:[4,4],0x1545c:[4],0x1b002:[2],0x1c9e8:[2],0x207cc:[2]};args=[];offset=4
        for w in widths[target]:args.append(runtime.device.read(s.registers[15]+offset,w));offset+=w
        calls.append(dict(target=hex(target),arguments=args))
        value=parameters['distance']if target==0x10252 else parameters.get('sound_return',1)if target==0x1c9e8 else 1
        if target==0x101e0:
         value=0 if parameters['retry']and retries[0]==0 else 1;retries[0]+=1
        s.registers[0]=value;s.registers[1]=0x87654321;s.registers[8]=0x15f000;s.registers[9]=0x15e000;s.sr=(s.sr&0xffe0)|0x13
       if mode=='native':
        runtime.seed_cpu(initial);trace=[]
        for _ in range(10000):
         pc=runtime.cpu().pc
         if pc==0xdf60:break
         trace.append(pc);coverage.add(pc)
         if pc in [0x101e0,0x10252,0x1404c,0xeb04,0x13c9a,0x1545c,0x1b002,0x1c9e8,0x207cc]:
          s=runtime.cpu();provider(s,pc)
          for r in [0,1,8,9]:runtime.core.m68k_set_reg(r,s.registers[r])
          runtime.core.m68k_set_reg(17,s.sr);old=runtime.device.read(pc,2);runtime.device.direct(pc,2,0x4e75);runtime.core.m68k_execute(1);runtime.device.direct(pc,2,old)
         else:runtime.core.m68k_execute(1)
        else:
         save(out/'native-bound.json',dict(case=case,entry=hex(entry),parameters=parameters,CPU=media.scheduler.cpu_dict(runtime.cpu()),trace_last=list(map(hex,trace[-40:])),trace_first=list(map(hex,trace[:60]))));raise AssertionError(('native task bound',hex(pc)))
        final=runtime.cpu()
       else:
        def rd(w):
         def cb(_,a,v):v[0]=runtime.read(a,w);return 0
         return cb
        def wr(w):
         def cb(_,a,v):runtime.write(a,w,v);return 0
         return cb
        world=media.scheduler.cleanup.world;callbacks=[world.R8(rd(1)),world.R16(rd(2)),world.R32(rd(4)),world.W16(wr(2)),world.W32(wr(4)),media.W8(wr(1))];bus=media.Bus(*callbacks[:5],world.CALL(),None,0)
        def service(_,passed,cpu,target):
         if target in [0x101e0,0x10252,0x1404c,0xeb04,0x13c9a,0x1545c,0x1b002,0x1c9e8,0x207cc]:provider(cpu.contents,target);return 0
         errors.append(hex(target));return 1
        callback=media.world_cpu.SERVICE(service);final=media.CPU.from_buffer_copy(bytes(initial));status=fn(c.byref(bus),c.byref(final),callbacks[5],callback,None,100000,1);assert status==6 and not errors,(status,errors)
       assert final.pc==0xdf60;views[mode]=dict(CPU=media.scheduler.cpu_dict(final),hardware=runtime.snapshot()['hardware'],calls=calls);RAMs[mode]=runtime.device.ram()
      if views['native']!=views['C']or RAMs['native']!=RAMs['C']:save(out/'mismatch.json',dict(case=case,entry=hex(entry),parameters=parameters,views=views,RAM_equal=RAMs['native']==RAMs['C']));raise AssertionError(str(out/'mismatch.json'))
      results.append(dict(case=case,parameters=parameters,calls=views['C']['calls']));case+=1
 report=dict(status='source_actor14_task_all_source_instructions_native_C_match',directory=str(out),cases=len(results),instructions_covered=[len({r['address']for r in mapping['instructions_decoded']}&coverage),len(mapping['instructions_decoded'])],helper_ABI_adversaries=True,message_flags_and_sound_results_checked=True,actual_full_helper_graph_verified=False,source_sha256={p.name:sha(p.read_bytes())for p in names},compiler=cmd,whole_game_complete=False,limits=['Cold/warm, user/supervisor, scan, lifecycle, distance boundary fixtures. Sourcehelpercalls use declaredABIadversaries; actualNPC/resource/sound/animation/movement helpergraph separate.','WholeCPU/privateRAM/checkedperipherals/sourceargumentsandflag1match; globalclock/GPU/DSP/scheduler,fullgame/physical/ordinarybootseparate.']);save(out/'cases.json',results);save(out/'report.json',report);save(ROOT/'verification/actor14-task-current.json',report);print(report['status'],len(results),flush=True)
finally:runtime.oracle.close()
