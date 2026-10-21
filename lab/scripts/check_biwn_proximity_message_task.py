"""Original/C task branches, real multiply, declared message ABI adversary."""
import ctypes as c,json,os,random,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_media_setup_cpu as media
ROOT=media.ROOT;save=media.save;sha=media.sha
out=ROOT/'verification/BIWN-proximity-message-task'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);src=ROOT/'projects/black-ice-white-noise/restoration';names=[src/'experimental/biwn_proximity_message_task_cpu.c',src/'biwn_startup_rng_math_cpu.c',src/'biwn_media_setup_cpu.c',src/'biwn_signed_division.c',src/'biwn_camera.c'];lib=out/'libproximity.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(src),*[str(p)for p in names],'-o',str(lib)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr);assert not build.returncode,build.stderr
obs=json.loads((ROOT/'verification/task-1b4e8-observation-current.json').read_text());baseline=(Path(obs['directory'])/'task-start-RAM.bin').read_bytes();mapping=json.loads((ROOT/'verification/proximity-message-task-generation.json').read_text());runtime=media.Runtime(lib,mapping['instructions_decoded']);fn=runtime.lib.biwn_proximity_message_task_cpu_body;fn.argtypes=runtime.fn.argtypes;fn.restype=c.c_int;math_fn=runtime.lib.biwn_startup_rng_math_cpu_body;math_fn.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU)];math_fn.restype=c.c_int;results=[];coverage=set();rng=random.Random(0x1b480);boundaries=[(0,0),(32,0),(33,0),(0,32),(0,33),(23,23),(-32,0),(-33,0),(31,1),(32,1)];case=0
try:
 for entry in [0x1b480,0x1b4e8]:
  for enable in [0,1,0xffff]:
   for once in [0,1]:
    for dx,dz in boundaries:
     for supervisor in [False,True]:
      initial=media.CPU();initial.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[0x1ff000];initial.registers[10]=0xe540;initial.pc=entry;initial.sr=(0x2000 if supervisor else 0)|(0x700 if case%2 else 0)|(case%32);initial.usp=0x1fe000 if supervisor else 0x1ff000;initial.ssp=0x1ff000 if supervisor else 0x200000;ram=bytearray(baseline)
      for a,w,v in [(0x43d98,2,enable),(0x46880,2,once),(0x49c50,4,24380+dx),(0x49c56,4,26784+dz)]:ram[a:a+w]=(v&((1<<(8*w))-1)).to_bytes(w,'big')
      views={};RAMs={}
      for mode in ['native','C']:
       runtime.reset(bytes(ram),0);calls=[];errors=[]
       def provider(s):
        assert runtime.device.read(s.registers[15]+4,2)==3;calls.append(dict(target='0x207cc',argument=3,SP=hex(s.registers[15])));s.registers[0]=0x12345678;s.registers[1]=0x87654321;s.registers[8]=0x15f000;s.registers[9]=0x15e000;s.sr=(s.sr&0xffe0)|0x13
       if mode=='native':
        runtime.seed_cpu(initial);trace=[]
        for _ in range(10000):
         pc=runtime.cpu().pc
         if pc==0xdf60:break
         trace.append(pc);coverage.add(pc)
         if pc==0x207cc:
          s=runtime.cpu();provider(s)
          for r in [0,1,8,9]:runtime.core.m68k_set_reg(r,s.registers[r])
          runtime.core.m68k_set_reg(17,s.sr);old=runtime.device.read(pc,2);runtime.device.direct(pc,2,0x4e75);runtime.core.m68k_execute(1);runtime.device.direct(pc,2,old)
         else:runtime.core.m68k_execute(1)
        else:
         save(out/'native-bound.json',dict(case=case,entry=hex(entry),enable=enable,once=once,dx=dx,dz=dz,supervisor=supervisor,CPU=media.scheduler.cpu_dict(runtime.cpu()),trace_last=list(map(hex,trace[-40:])),trace_first=list(map(hex,trace[:60]))));raise AssertionError(('native task bound',hex(pc)))
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
         if target==0xe540:return math_fn(passed,cpu)
         if target==0x207cc:provider(cpu.contents);return 0
         errors.append(hex(target));return 1
        callback=media.world_cpu.SERVICE(service);final=media.CPU.from_buffer_copy(bytes(initial));status=fn(c.byref(bus),c.byref(final),callbacks[5],callback,None,100000,1);assert status==6 and not errors,(status,errors)
       assert final.pc==0xdf60;views[mode]=dict(CPU=media.scheduler.cpu_dict(final),hardware=runtime.snapshot()['hardware'],calls=calls);RAMs[mode]=runtime.device.ram()
      if views['native']!=views['C']or RAMs['native']!=RAMs['C']:save(out/'mismatch.json',dict(case=case,entry=hex(entry),enable=enable,once=once,dx=dx,dz=dz,views=views,RAM_equal=RAMs['native']==RAMs['C']));raise AssertionError(str(out/'mismatch.json'))
      expect=int(bool(enable)and not once and dx*dx+dz*dz<=1024);assert len(views['C']['calls'])==expect;results.append(dict(case=case,entry=hex(entry),enable=enable,once=once,dx=dx,dz=dz,supervisor=supervisor,message3_calls=expect));case+=1
 report=dict(status='source_proximity_message_task_all28instructions_native_C_match',directory=str(out),cases=len(results),instructions_covered=[len({r['address']for r in mapping['instructions_decoded']}&coverage),28],source_math_E540_executed=True,message207CC_ABI_adversary=True,message3_full_movie_verified=False,source_sha256={p.name:sha(p.read_bytes())for p in names},compiler=cmd,whole_game_complete=False,limits=['Standalonetaskcold/warm,user/supervisor,enable/onceanddistanceboundaryfixtures. RealE540multiply executes;207CCisdeclaredregister/CCR-preserving-stackadversary,notmessage3movie.','WholeCPU/privateRAM/checkedperipherals/sourceargumentsandflag1match; globalclock/GPU/DSP/scheduler,fullgame/physical/ordinarybootseparate.']);save(out/'cases.json',results);save(out/'report.json',report);save(ROOT/'verification/proximity-message-task-current.json',report);print(report['status'],len(results),flush=True)
finally:runtime.oracle.close()
