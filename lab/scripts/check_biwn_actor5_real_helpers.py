"""Compare type5 source task against original CPU; helper ABI adversaries explicit."""
import ctypes as c,json,os,random,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_media_setup_cpu as media
ROOT=media.ROOT;save=media.save;sha=media.sha
out=ROOT/'verification/BIWN-actor5-real-helpers'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);src=ROOT/'projects/black-ice-white-noise/restoration';names=[src/'experimental/biwn_actor5_task_cpu.c',src/'biwn_npc_cpu.c',src/'biwn_actor_direction.c',src/'biwn_rng_cpu.c',src/'biwn_startup_rng_math_cpu.c',src/'biwn_media_setup_cpu.c',src/'biwn_signed_division.c',src/'biwn_camera.c'];lib=out/'libproximity.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(src),*[str(p)for p in names],'-o',str(lib)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr);assert not build.returncode,build.stderr
obs=json.loads((ROOT/'verification/task-1b4e8-observation-current.json').read_text());baseline=(Path(obs['directory'])/'task-start-RAM.bin').read_bytes();mapping=json.loads((ROOT/'verification/actor5-task-generation.json').read_text());runtime=media.Runtime(lib,mapping['instructions_decoded']);fn=runtime.lib.biwn_actor5_task_cpu_body;fn.argtypes=runtime.fn.argtypes;fn.restype=c.c_int;math_fn=runtime.lib.biwn_startup_rng_math_cpu_body;math_fn.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU)];math_fn.restype=c.c_int;npc_fn=runtime.lib.biwn_npc_cpu_body;npc_fn.argtypes=runtime.fn.argtypes;npc_fn.restype=c.c_int;direction_fn=runtime.lib.biwn_actor_direction_body;direction_fn.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU)];direction_fn.restype=c.c_int;results=[];coverage=set();rng=random.Random(0x1b480);boundaries=[(0,0),(32,0),(33,0),(0,32),(0,33),(23,23),(-32,0),(-33,0),(31,1),(32,1)];case=0
try:
 vectors=[]
 for entry in [0x12ee0,0x12f28]:
  for slot in [None,0,39]:
   for mode in [0,1,2,0xffff]:
    for dead in [0,1]:
     for retry in [False,True]:
      for supervisor in [False,True]:vectors.append(dict(entry=entry,slot=slot,mode=mode,dead=dead,retry=retry,supervisor=supervisor,c8=2,d4=0,flag=0,room=0,distance=0,x=0x89a0,z=0x34f8,ticks=1,acc=0,orientation=0x40))
 for entry in [0x12f88,0x13438]:
  for mode in [0,1,2,3,4,5,6,0x7fff,0x8000,0xffff]:
   for distance in [-2147483648,-1,0,255,256,4095,4096,16383,16384,2147483647]:
    for dead in [0,1]:
     for c8 in [0,2]:
      for supervisor in [False,True]:vectors.append(dict(entry=entry,slot=0,mode=mode,dead=dead,retry=False,supervisor=supervisor,c8=c8,d4=len(vectors)%3,flag=len(vectors)%2,room=len(vectors)%3,distance=distance,x=0x89a0,z=0x34f8,ticks=[0,1,75,300,0xffff,0x80000000][len(vectors)%6],acc=0xffff,orientation=0x83))
 for mode in [2,3]:
  for x,z in [(0x8800,0x3481),(0x8801,0x3480),(0x8801,0x3481),(0x89bf,0x35bf),(0x89c0,0x35bf),(0x89bf,0x35c0),(0x89a0,0x34f8),(0x899e,0x34f6),(0x899d,0x34f8),(0,0),(0x7fffffff,0x80000000)]:
   for distance in [255,256,4095,4096]:
    for d4 in [0,1,2]:
     for supervisor in [False,True]:vectors.append(dict(entry=0x12f88,slot=39,mode=mode,dead=0,retry=False,supervisor=supervisor,c8=2,d4=d4,flag=1,room=2,distance=distance,x=x,z=z,ticks=[1,300,0xffff][d4],acc=[0,0xffff,0x7fffffff][d4],orientation=0x7f))
 for room in [0,1,2,3]:
  for flag in [0,1]:
   for distance in [16383,16384]:
    for supervisor in [False,True]:vectors.append(dict(entry=0x12f88,slot=0,mode=2,dead=1,retry=False,supervisor=supervisor,c8=2,d4=0,flag=flag,room=room,distance=distance,x=0x89a0,z=0x34f8,ticks=1,acc=0,orientation=0x40))
 for z in [0x4b00,0x4b01]:
  for supervisor in [False,True]:vectors.append(dict(entry=0x12f88,slot=0,mode=1,dead=0,retry=False,supervisor=supervisor,c8=2,d4=0,flag=0,room=0,distance=255,x=0x89a0,z=z,ticks=1,acc=0,orientation=0x40))
 for x in [19199,19200,19201]:
  for d5 in [0,1]:
   for local in [0,1,0xffff]:
    for dialog in [0,2]:
     for f8,fa in [(0,0),(1,0),(1,1)]:
      for supervisor in [False,True]:vectors.append(dict(entry=0x12f88,slot=0,mode=1,dead=0,retry=False,supervisor=supervisor,c8=2,d4=0,d5=d5,local=local,dialog=dialog,f8=f8,fa=fa,resource=17 if x<=19200 else 16,flag=0,room=0,distance=255,x=x,z=0x34f8,ticks=1,acc=0,orientation=0x40))
 for sound in [0,1,2,3,4,5,0xffff]:
  for supervisor in [False,True]:vectors.append(dict(entry=0x12f88,slot=39,mode=1,dead=0,retry=False,supervisor=supervisor,c8=2,d4=0,d5=0,local=0,dialog=0,f8=0,fa=0,sound=sound,resource=17,flag=0,room=0,distance=0,x=0,z=0x34f8,ticks=1,acc=0,orientation=0x40))
 for resource in [16,17]:
  for supervisor in [False,True]:vectors.append(dict(entry=0x12f88,slot=0,mode=1,dead=0,retry=False,supervisor=supervisor,c8=0,d4=0,d5=0,resource=resource,flag=0,room=0,distance=0,x=0,z=0,ticks=1,acc=0,orientation=0x40))
 for entry in [0x12ee0,0x12f28]:
  for x in [19199,19200,19201]:
   for dead in [0,1]:
    for retry in [False,True]:
     for supervisor in [False,True]:vectors.append(dict(entry=entry,slot=0,mode=1,dead=dead,retry=retry,supervisor=supervisor,c8=2,d4=0,d5=0,local=0,resource=17 if x<=19200 else 16,flag=0,room=0,distance=0,x=x,z=0x34f8,ticks=1,acc=0,orientation=0x40))
 for parameters in [v for v in vectors if not v["supervisor"]]:
      entry=parameters['entry'];slot=parameters['slot'];supervisor=parameters['supervisor'];record_address=0x49d6c+(slot or 0)*206;initial=media.CPU();initial.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[0x1ff000];initial.registers[2]=0x49d6c;initial.registers[3]=parameters['mode'];initial.registers[4]=parameters['d4'];initial.registers[5]=parameters.get('d5',0);initial.registers[6]=parameters.get('resource',16);initial.registers[10]=(parameters['c8']if parameters['c8']<0x8000 else parameters['c8']-0x10000)&0xffffffff;initial.registers[11]=record_address;initial.registers[12]=0x49c60;initial.registers[13]=0x49c56;initial.registers[14]=0x49c50;initial.pc=entry;initial.sr=(0x2000 if supervisor else 0)|(0x700 if case%2 else 0)|(case%32);initial.usp=0x1fe000 if supervisor else 0x1ff000;initial.ssp=0x1ff000 if supervisor else 0x200000;ram=bytearray(baseline)
      for i in range(40):ram[0x49d6c+i*206:0x49d6e+i*206]=bytes(2)
      if slot is not None:
       for offset,w,v in [(0,2,5),(2,2,parameters['dead']),(0x6c,2,parameters['mode']),(0xc8,2,parameters['c8']),(0x5e,4,0x156789)]:ram[record_address+offset:record_address+offset+w]=(v&((1<<(8*w))-1)).to_bytes(w,'big')
      actual_dx={-2147483648:0x80000000,-1:65535,0:0,255:15,256:16,4095:63,4096:64,16383:127,16384:128,2147483647:46340}[parameters['distance']]
      for address,width,value in [(record_address+4,4,parameters['x']),(record_address+10,4,parameters['z']),(record_address+0x16,2,parameters['room']),(record_address+0x7c,4,parameters['acc']),(0x49c50,4,parameters['x']+actual_dx),(0x49c56,4,parameters['z']),(0x49c60,2,parameters['room']),(0x45d98,2,parameters['flag']),(0x4c24c,4,parameters['ticks']),(record_address+0xc0,2,0),(record_address+0xca,2,0),(0x47b9a,2,1),(0x47b9e,2,1),(record_address+0x6e,1,0x7f),(0x49b9f,1,0x40)]:ram[address:address+width]=(value&((1<<(8*width))-1)).to_bytes(width,'big')
      ram[0x1ff02e+(12 if entry==0x13438 else 0):0x1ff030+(12 if entry==0x13438 else 0)]=(parameters.get('local',0)&0xffff).to_bytes(2,'big')
      for address,value in [(0x49d5a,parameters.get('dialog',0)),(0x41ef8,parameters.get('f8',0)),(0x41efa,parameters.get('fa',0))]:ram[address:address+2]=(value&0xffff).to_bytes(2,'big')
      views={};RAMs={}
      for mode in ['native','C']:
       runtime.reset(bytes(ram),0);calls=[];errors=[];actual_calls=[]
       retries=[0]
       def provider(s,target):
        widths={0x101e0:[4,2,4,4],0x10252:[4],0x1404c:[4],0xeb04:[4],0x13c9a:[4,4],0x1545c:[4],0x1b002:[2],0x1c9e8:[2],0x207cc:[2],0x13440:[2,2],0x1028e:[4],0x102c4:[4]};args=[];offset=4
        for w in widths[target]:args.append(runtime.device.read(s.registers[15]+offset,w));offset+=w
        calls.append(dict(target=hex(target),arguments=args))
        value=parameters['distance']if target==0x10252 else parameters['orientation']if target==0x13440 else parameters.get('sound',1)if target==0x1c9e8 else 1
        if target==0x101e0:
         value=0 if parameters['retry']and retries[0]==0 else 1;retries[0]+=1
        s.registers[0]=value;s.registers[1]=0x87654321;s.registers[8]=0x15f000;s.registers[9]=0x15e000;s.sr=(s.sr&0xffe0)|0x13
       if mode=='native':
        runtime.seed_cpu(initial);trace=[]
        for _ in range(10000):
         pc=runtime.cpu().pc
         if pc==0xdf60:break
         trace.append(pc);coverage.add(pc)
         if pc in [0x10252,0x1404c,0x13440,0xe540,0xe588]:actual_calls.append(hex(pc))
         if pc in [0x101e0,0xeb04,0x13c9a,0x1545c,0x1b002,0x1c9e8,0x207cc,0x1028e,0x102c4]:
          s=runtime.cpu();provider(s,pc)
          for r in [0,1,8,9]:runtime.core.m68k_set_reg(r,s.registers[r])
          runtime.core.m68k_set_reg(17,s.sr);old=runtime.device.read(pc,2);runtime.device.direct(pc,2,0x4e75);runtime.core.m68k_execute(1);runtime.device.direct(pc,2,old)
         else:runtime.core.m68k_execute(1)
        else:
         save(out/'native-bound.json',dict(case=case,entry=hex(entry),parameters=parameters,CPU=media.scheduler.cpu_dict(runtime.cpu()),trace_last=list(map(hex,trace[-40:])),trace_first=list(map(hex,trace[:60]))));raise AssertionError(('native task bound',hex(pc)))
        final=runtime.cpu();actual_native_entries=list(actual_calls)
       else:
        def rd(w):
         def cb(_,a,v):v[0]=runtime.read(a,w);return 0
         return cb
        def wr(w):
         def cb(_,a,v):runtime.write(a,w,v);return 0
         return cb
        world=media.scheduler.cleanup.world;callbacks=[world.R8(rd(1)),world.R16(rd(2)),world.R32(rd(4)),world.W16(wr(2)),world.W32(wr(4)),media.W8(wr(1))];bus=media.Bus(*callbacks[:5],world.CALL(),None,0)
        def service(_,passed,cpu,target):
         if target in [0x10252,0x1404c,0x13440,0xe540,0xe588]:actual_calls.append(hex(target))
         if target in [0x10252,0x1404c]:return npc_fn(passed,cpu,callbacks[5],callback,None,100000,1)
         if target==0x13440:return direction_fn(passed,cpu)
         if target in [0xe540,0xe588]:return math_fn(passed,cpu)
         if target in [0x101e0,0x10252,0x1404c,0xeb04,0x13c9a,0x1545c,0x1b002,0x1c9e8,0x207cc,0x13440,0x1028e,0x102c4]:provider(cpu.contents,target);return 0
         errors.append(hex(target));return 1
        callback=media.world_cpu.SERVICE(service);final=media.CPU.from_buffer_copy(bytes(initial));status=fn(c.byref(bus),c.byref(final),callbacks[5],callback,None,100000,1);assert status==6 and not errors,(status,errors)
       assert final.pc==0xdf60;views[mode]=dict(CPU=media.scheduler.cpu_dict(final),hardware=runtime.snapshot()['hardware'],calls=calls,actual_helper_calls=[pc for pc in actual_calls if pc!='0xe588']);RAMs[mode]=runtime.device.ram()
      if views['native']!=views['C']or RAMs['native']!=RAMs['C']:save(out/'mismatch.json',dict(case=case,entry=hex(entry),parameters=parameters,views=views,RAM_equal=RAMs['native']==RAMs['C']));raise AssertionError(str(out/'mismatch.json'))
      results.append(dict(native_internal_helper_entries=actual_native_entries,case=case,parameters=parameters,calls=views['C']['calls']));case+=1
 report=dict(status='source_actor5_task_actual_distance_direction_facing_math_native_C_match',directory=str(out),cases=len(results),instructions_covered=[len({r['address']for r in mapping['instructions_decoded']}&coverage),len(mapping['instructions_decoded'])],missing_task_instruction_addresses=list(map(hex,sorted({r["address"]for r in mapping["instructions_decoded"]}-coverage))),source_E540_multiply_actual=True,source_E588_division_actual=True,helper_ABI_adversaries=True,actual_helpers_user_mode_only=True,actual_helpers=["10252 distance","1404C facing","13440 direction","E540 multiply","E588 signed division"],jump_table_data_excluded=True,message_flags_and_sound_results_checked=True,actual_full_helper_graph_verified=False,source_sha256={p.name:sha(p.read_bytes())for p in names},compiler=cmd,whole_game_complete=False,limits=['Cold/warm, user/supervisor, scan, lifecycle, distance boundary fixtures. Sourcehelpercalls use declaredABIadversaries; actualNPC/resource/sound/animation/movement helpergraph separate.','WholeCPU/privateRAM/checkedperipherals/sourceargumentsandflag1match; globalclock/GPU/DSP/scheduler,fullgame/physical/ordinarybootseparate.']);save(out/'cases.json',results);save(out/'report.json',report);save(ROOT/'verification/actor5-real-helpers-current.json',report);print(report['status'],len(results),flush=True)
finally:runtime.oracle.close()
