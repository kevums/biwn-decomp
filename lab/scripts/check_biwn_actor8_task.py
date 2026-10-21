"""Compare type8 source task against original CPU; helper ABI adversaries explicit."""
import ctypes as c,json,os,random,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_media_setup_cpu as media
ROOT=media.ROOT;save=media.save;sha=media.sha
out=ROOT/'verification/BIWN-actor8-task'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);src=ROOT/'projects/black-ice-white-noise/restoration';names=[src/'experimental/biwn_actor8_task_cpu.c',src/'biwn_startup_rng_math_cpu.c',src/'biwn_media_setup_cpu.c',src/'biwn_signed_division.c',src/'biwn_camera.c'];lib=out/'libproximity.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(src),*[str(p)for p in names],'-o',str(lib)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr);assert not build.returncode,build.stderr
obs=json.loads((ROOT/'verification/task-1b4e8-observation-current.json').read_text());baseline=(Path(obs['directory'])/'task-start-RAM.bin').read_bytes();mapping=json.loads((ROOT/'verification/actor8-task-generation.json').read_text());runtime=media.Runtime(lib,mapping['instructions_decoded']);fn=runtime.lib.biwn_actor8_task_cpu_body;fn.argtypes=runtime.fn.argtypes;fn.restype=c.c_int;math_fn=runtime.lib.biwn_startup_rng_math_cpu_body;math_fn.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU)];math_fn.restype=c.c_int;results=[];coverage=set();rng=random.Random(0x1b480);boundaries=[(0,0),(32,0),(33,0),(0,32),(0,33),(23,23),(-32,0),(-33,0),(31,1),(32,1)];case=0
try:
 vectors=[]
 for entry in [0x179c0,0x179f2]:
  for slot in [None,0,39]:
   for mode in [1,2,6,7]:
    for x in [19199,19200]:
     for dead in [0,1]:
      for supervisor in [False,True]:vectors.append(dict(entry=entry,slot=slot,mode=mode,x=x,dead=dead,supervisor=supervisor,c8=2,retry=False,d4=0,d5=0,flag=0,offsets=[0,0]))
 for entry in [0x17a5c,0x17c1a]:
  for mode in list(range(9))+[9,0x8000,0xffff]:
   for offsets in [(0,0),(15,0),(16,0),(64,0),(65,0),(11,11),(12,12),(-16,0),(0x7fffffff,0),(0x80000000,0)]:
    for bits in range(8):
     for supervisor in [False,True]:vectors.append(dict(entry=entry,slot=0,mode=mode,x=19200,dead=0,supervisor=supervisor,c8=2,retry=False,d4=bits&1,d5=(bits>>1)&1,flag=(bits>>2)&1,offsets=offsets))
 for mode in [1,5,7]:
  for dead in [0,1]:
   for c8 in [0,0xffff]:
    for retry in [False,True]:vectors.append(dict(entry=0x179f2,slot=39,mode=mode,x=19200,dead=dead,supervisor=False,c8=c8,retry=retry,d4=0,d5=0,flag=1,offsets=[0,0]))
 for entry in [0x179c0,0x179f2]:
  for flag in [0,1]:
   for supervisor in [False,True]:vectors.append(dict(entry=entry,slot=39,mode=5,x=19199,dead=1,supervisor=supervisor,c8=2,retry=False,d4=0,d5=0,flag=flag,offsets=[0,0]))
 for parameters in vectors:
      entry=parameters['entry'];slot=parameters['slot'];supervisor=parameters['supervisor'];record_address=0x49d6c+(slot or 0)*206;initial=media.CPU();initial.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[0x1ff000];initial.registers[2]=parameters["mode"];initial.registers[3]=parameters["c8"];initial.registers[4]=parameters["d4"];initial.registers[5]=parameters["d5"];initial.registers[6]=0x49d6c;initial.registers[11]=0xe540;initial.registers[10]=record_address;initial.pc=entry;initial.sr=(0x2000 if supervisor else 0)|(0x700 if case%2 else 0)|(case%32);initial.usp=0x1fe000 if supervisor else 0x1ff000;initial.ssp=0x1ff000 if supervisor else 0x200000;ram=bytearray(baseline)
      for i in range(40):ram[0x49d6c+i*206:0x49d6e+i*206]=bytes(2)
      if slot is not None:
       for offset,w,v in [(0,2,8),(2,2,parameters['dead']),(0x6c,2,parameters['mode']),(0xc8,2,parameters['c8']),(0x5e,4,0x156789)]:ram[record_address+offset:record_address+offset+w]=(v&((1<<(8*w))-1)).to_bytes(w,'big')
      dx,dz=parameters['offsets']
      for address,width,value in [(record_address+4,4,parameters['x']),(record_address+10,4,0),(0x49c50,4,parameters['x']+dx),(0x49c56,4,dz),(0x43d98,2,parameters['flag'])]:ram[address:address+width]=(value&((1<<(8*width))-1)).to_bytes(width,'big')
      views={};RAMs={}
      for mode in ['native','C']:
       runtime.reset(bytes(ram),0);calls=[];errors=[]
       retries=[0]
       def provider(s,target):
        widths={0x101e0:[4,2,4,4],0x10252:[4],0x1404c:[4],0xeb04:[4],0x13c9a:[4,4],0x1545c:[4],0x1b002:[2],0x1c9e8:[2],0x207cc:[2],0x1b786:[]};args=[];offset=4
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
         if pc in [0x101e0,0x10252,0x1404c,0xeb04,0x13c9a,0x1545c,0x1b002,0x1c9e8,0x207cc,0x1b786]:
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
         if target==0xe540:return math_fn(passed,cpu)
         if target in [0x101e0,0x10252,0x1404c,0xeb04,0x13c9a,0x1545c,0x1b002,0x1c9e8,0x207cc,0x1b786]:provider(cpu.contents,target);return 0
         errors.append(hex(target));return 1
        callback=media.world_cpu.SERVICE(service);final=media.CPU.from_buffer_copy(bytes(initial));status=fn(c.byref(bus),c.byref(final),callbacks[5],callback,None,100000,1);assert status==6 and not errors,(status,errors)
       assert final.pc==0xdf60;views[mode]=dict(CPU=media.scheduler.cpu_dict(final),hardware=runtime.snapshot()['hardware'],calls=calls);RAMs[mode]=runtime.device.ram()
      if views['native']!=views['C']or RAMs['native']!=RAMs['C']:save(out/'mismatch.json',dict(case=case,entry=hex(entry),parameters=parameters,views=views,RAM_equal=RAMs['native']==RAMs['C']));raise AssertionError(str(out/'mismatch.json'))
      results.append(dict(case=case,parameters=parameters,calls=views['C']['calls']));case+=1
 report=dict(status='source_actor8_task_fixture_native_C_match',directory=str(out),cases=len(results),instructions_covered=[len({r['address']for r in mapping['instructions_decoded']}&coverage),len(mapping['instructions_decoded'])],missing_task_instruction_addresses=list(map(hex,sorted({r["address"]for r in mapping["instructions_decoded"]}-coverage))),source_E540_multiply_actual=True,helper_ABI_adversaries=True,jump_table_data_excluded=True,message_flags_and_sound_results_checked=True,actual_full_helper_graph_verified=False,source_sha256={p.name:sha(p.read_bytes())for p in names},compiler=cmd,whole_game_complete=False,limits=['Cold/warm, user/supervisor, scan, lifecycle, distance boundary fixtures. Sourcehelpercalls use declaredABIadversaries; actualNPC/resource/sound/animation/movement helpergraph separate.','WholeCPU/privateRAM/checkedperipherals/sourceargumentsandflag1match; globalclock/GPU/DSP/scheduler,fullgame/physical/ordinarybootseparate.']);save(out/'cases.json',results);save(out/'report.json',report);save(ROOT/'verification/actor8-task-current.json',report);print(report['status'],len(results),flush=True)
finally:runtime.oracle.close()
