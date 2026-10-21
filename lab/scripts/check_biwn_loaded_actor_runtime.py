"""Fresh C-loaded actor records through real scheduler activation and updates.

Retain the actual task ring and disc geometry. Other contexts are explicitly
blocked for this isolated actor continuation; this is not a live whole game.
"""
import argparse,ctypes as c,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_actor_full_movement_runtime as live
import check_biwn_actor_lifecycle_runtime as lifecycle
import check_biwn_scene_render_pipeline as rendering
ROOT=live.ROOT;CPU=live.CPU;world=live.world;save=live.save;get=live.get;sha=rendering.sha
NAMES=['biwn_actor_task.c','biwn_actor_navigation.c','biwn_actor_movement.c','biwn_actor_direction.c','biwn_movement_submit_cpu.c','biwn_actor_collision.c','biwn_geometry_cpu.c','biwn_rng_cpu.c','biwn_signed_division.c','biwn_camera.c','biwn_scheduler.c','biwn_task_loops.c','biwn_actor_pipeline.c']
OBSERVER=c.CFUNCTYPE(None,c.c_void_p,c.c_uint32,c.POINTER(CPU))
RANGES=[(0xf4d8,0xf712),(0xdfa6,0xdfb2),(0xdf60,0xdf6c),(0xde08,0xde5c),(0x1a77c,0x1a7f4),(0x13c9a,0x13f12)]+live.navigation.RANGES+live.rng_cpu.RANGES+live.motion.direction.RANGES+live.motion.submit_cpu.RANGES+live.motion.collision.RANGES


def ring(ram):
    first=get(ram,0xc0920);task=first;tasks=[]
    while task not in tasks:
        assert 0<=task<0x200000-0x400 and len(tasks)<64
        tasks.append(task);next_task=get(ram,task)
        assert get(ram,next_task+4)==task
        task=next_task
    assert task==first
    return tasks


def fixture(ram,task,rng):
    initial=bytearray(ram);tasks=ring(initial);assert task in tasks
    assert get(initial,task+8)==get(initial,task+16)==0xf4d8
    assert get(initial,task+12)==task+0x400 and get(initial,task+20,2)==get(initial,task+22)==get(initial,task+26)==get(initial,task+34)==0
    predecessor=get(initial,task+4);assert get(initial,predecessor)==task
    edits=[]
    for other in tasks:
        if other!=task:
            prior=get(initial,other+26);initial[other+26:other+30]=(1).to_bytes(4,'big')
            edits.append(dict(task=hex(other),prior=prior,blocked=1))
    initial[0xc0920:0xc0924]=predecessor.to_bytes(4,'big')
    stack=get(initial,predecessor+12)-4;assert predecessor+38<=stack<predecessor+0x400
    initial[stack:stack+4]=(0x1ffe00).to_bytes(4,'big')
    cpu=CPU();cpu.registers[:]=[rng.getrandbits(32)for _ in range(16)];cpu.registers[15]=stack
    cpu.usp=stack;cpu.ssp=0x1ff000;cpu.sr=rng.randrange(32);cpu.pc=0xdf60
    assert get(initial,0x80)==0xde08
    return bytes(initial),cpu,dict(task=hex(task),predecessor=hex(predecessor),original_ring_contexts=len(tasks),blocked_other_contexts=edits,supplied_yield_call_SP=hex(stack),actor_parameter=get(initial,task+30),source_time_step=get(initial,0x4c24c))


class Runtime(live.Runtime):
    def __init__(self,library):
        super().__init__(library)
        self.pipeline=self.lib.biwn_actor_pipeline_step
        self.pipeline.argtypes=[c.POINTER(world.Bus),c.POINTER(CPU),type(self.device.write8),c.c_uint32,OBSERVER,c.c_void_p]
        self.pipeline.restype=c.c_int
    def snapshot(self,cpu):
        raw=self.device.ram()
        return dict(CPU=live.prior.scheduler.cpu_dict(cpu),RAM_sha256=sha(raw),current=hex(get(raw,0xc0920)))

    def finish(self,cpu,calls,movements,boundaries,steps):
        return self.device.ram(),cpu,dict(calls=calls,movements=movements,boundaries=boundaries,CPU_instructions=len(steps),instruction_addresses=len(set(steps)),device=self.device.stats(),hardware=[self.device.read(a,4)for a in[0xf02200,0xf02204,0xf0220c,0xf02224,0xf02228,0xf02230,0xf0223c]],GPU_argument_mailboxes=[self.core.GPUReadLong(a,0)for a in[0xf03200,0xf03204,0xf0320c,0xf03210,0xf03214,0xf03218,0xf0321c]])

    def movement_event(self,obj):
        ram=self.device.ram();return dict(object=hex(obj),X=get(ram,obj+4),Y=get(ram,obj+8,2),Z=get(ram,obj+10),heading=get(ram,obj+110,1),speed=get(ram,obj+120),tile_pointer=hex(get(ram,obj+68)))

    def native(self,ram,initial,task,iterations):
        self.device.seed(ram,0);lifecycle.seed_cpu(self,initial)
        calls=[];movements=[];boundaries=[];steps=[];activated=False
        for _ in range(300000):
            pc=self.core.m68k_get_reg(None,16)
            if pc==0xf70c and len(movements)>=iterations:break
            assert any(lo<=pc<hi for lo,hi in RANGES),dict(PC=hex(pc),current=hex(self.current()),instructions=len(steps))
            if pc in live.NAV:
                stack=self.core.m68k_get_reg(None,15);args=[];offset=4
                for width in live.actor.WIDTHS[pc]:args.append(get(self.device.ram(),stack+offset,width));offset+=width
                calls.append([hex(pc),args])
                if pc==0x13c9a:movements.append(self.movement_event(args[0]))
            steps.append(pc);self.core.m68k_execute(1)
            if self.core.GPUReadLong(0xf03204,0)==0x4320:self.device.write(0xf03204,0x4320)
            if pc==0xdf6a or(pc==0xde5a and self.core.m68k_get_reg(None,16)!=0xdf66):
                cpu=self.cpu();assert self.current()==task
                boundaries.append(self.snapshot(cpu))
                if not activated:assert cpu.pc==0xf4d8 and cpu.registers[15]==task+0x400;activated=True
        else:raise AssertionError('Native loaded actor continuation did not finish')
        assert activated and len(movements)==iterations and len(boundaries)==iterations+1
        return self.finish(self.cpu(),calls,movements,boundaries,steps)

    def translated(self,ram,initial,task,iterations,with_observer=True):
        self.device.seed(ram,1);cpu=CPU.from_buffer_copy(bytes(initial));calls=[];movements=[];boundaries=[];errors=[]
        bus=world.Bus(self.device.r8,self.device.r16,self.device.r32,self.device.w16,self.device.w32,world.CALL(),None,0)
        def observe(_,target,state):
            try:
                if target not in live.NAV:return
                offset=state.contents.registers[15]+4;args=[]
                for width in live.actor.WIDTHS[target]:args.append(get(self.device.ram(),offset,width));offset+=width
                calls.append([hex(target),args])
                if target==0x13c9a:movements.append(self.movement_event(args[0]))
            except Exception as error:errors.append(repr(error))
        cb=OBSERVER(observe)if with_observer else OBSERVER()
        def step():
            status=self.pipeline(c.byref(bus),c.byref(cpu),self.device.write8,4096,cb,None)
            if status:self.pipeline_failure=dict(status=status,CPU=live.prior.scheduler.cpu_dict(cpu),observations=calls,errors=errors,device_errors=self.device.errors)
            assert status==0,getattr(self,'pipeline_failure',{})
        step()
        assert self.current()==task and cpu.pc==0xf4d8 and cpu.registers[15]==task+0x400
        boundaries.append(self.snapshot(cpu))
        for _ in range(iterations):
            step();assert cpu.pc==0xdf60
            step()
            assert self.current()==task and cpu.pc==0xf70c
            boundaries.append(self.snapshot(cpu))
        assert not errors and not self.device.errors
        return self.finish(cpu,calls,movements,boundaries,[])


def check_guards(runtime,ram,initial):
    rows=[]
    tests=['zero_budget','unsupported_PC','supervisor','null_bus','null_CPU','null_write8','missing_read16','read_failure']
    for name in tests:
        runtime.device.seed(ram,1);cpu=CPU.from_buffer_copy(bytes(initial));calls=[]
        cb=OBSERVER(lambda _,target,state:calls.append(target))
        read16=world.R16()if name=='missing_read16'else world.R16(lambda _,a,out:1)if name=='read_failure'else runtime.device.r16
        bus=world.Bus(runtime.device.r8,read16,runtime.device.r32,runtime.device.w16,runtime.device.w32,world.CALL(),None,0)
        if name=='unsupported_PC':cpu.pc=0
        if name=='supervisor':cpu.sr|=0x2000
        before=bytes(cpu)
        status=runtime.pipeline(None if name=='null_bus'else c.byref(bus),None if name=='null_CPU'else c.byref(cpu),type(runtime.device.write8)()if name=='null_write8'else runtime.device.write8,0 if name=='zero_budget'else 4096,cb,None)
        expected=3 if name=='unsupported_PC'else 2 if name=='read_failure'else 1
        assert status==expected and bytes(cpu)==before and not calls,(name,status)
        if name=='read_failure':assert runtime.device.ram()!=ram
        else:assert runtime.device.ram()==ram
        rows.append(dict(case=name,status=status,CPU_unchanged=True,earlier_RAM_effects_retained=name=='read_failure'))
    task=get(ram,get(ram,0xc0920));left,expected,_=runtime.translated(ram,initial,task,1)
    right,actual,_=runtime.translated(ram,initial,task,1,with_observer=False)
    assert left==right and bytes(expected)==bytes(actual)
    rows.append(dict(case='optional_observer',no_observer_same_CPU_and_RAM=True))
    return rows


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opt=ap.parse_args()
    proof=json.loads((ROOT/'verification/scene-queue-restoration-current.json').read_text());folder=Path(proof['directory']);source=ROOT/'projects/black-ice-white-noise/restoration'
    for name,expected in proof['source_sha256'].items():assert sha((source/name).read_bytes())==expected,name
    out=ROOT/'verification/loaded-actor-runtime'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    library=out/'libloaded-actor-runtime.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(source/name)for name in NAMES],'-o',str(library)]
    built=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
    metadata=json.loads((folder/'render-inputs.json').read_text());vectors=[]
    for i,item in enumerate(metadata):
        ram=(folder/f'render-input-{i}.bin').read_bytes();assert sha(ram)==item['RAM_sha256']
        for task in ring(ram):
            if get(ram,task+8)==0xf4d8 and get(ram,task+16)==0xf4d8 and get(ram,task+12)==task+0x400:
                for iterations in[1,8]:vectors.append((i,item,ram,task,iterations))
    if opt.limit:vectors=vectors[:opt.limit]
    assert vectors;runtime=Runtime(library);rng=random.Random(0xf4d820f78);rows=[]
    guards=[]
    try:
        for ordinal,(index,item,original_ram,task,iterations)in enumerate(vectors):
            save(out/'status.json',dict(status='running',case=ordinal,total=len(vectors),task=hex(task),iterations=iterations))
            ram,initial,fixture_info=fixture(original_ram,task,rng)
            left,expected,original=runtime.native(ram,initial,task,iterations);right,actual,rebuilt=runtime.translated(ram,initial,task,iterations)
            fields=['calls','movements','boundaries','hardware','GPU_argument_mailboxes']
            if left!=right or bytes(expected)!=bytes(actual)or any(original[k]!=rebuilt[k]for k in fields):
                (out/'native-RAM.bin').write_bytes(left);(out/'C-RAM.bin').write_bytes(right);save(out/'mismatch.json',dict(case=ordinal,scene=index,task=hex(task),iterations=iterations,fixture=fixture_info,original=original,rebuilt=rebuilt,original_CPU=live.prior.scheduler.cpu_dict(expected),C_CPU=live.prior.scheduler.cpu_dict(actual),RAM_differences=[hex(a)for a,(l,r)in enumerate(zip(left,right))if l!=r][:64]));raise AssertionError(str(out/'mismatch.json'))
            assert not rebuilt['device']['original_GPUExec1_calls']and not rebuilt['device']['device_error']
            obj=0x49d6c+fixture_info['actor_parameter']*206
            row=dict(scene=index,window=item['window'],task=hex(task),fixture=fixture_info,iterations=iterations,source_RAM_sha256=item['RAM_sha256'],initial_CPU=live.prior.scheduler.cpu_dict(initial),original=original,rebuilt=rebuilt,final_CPU=live.prior.scheduler.cpu_dict(actual),actor_before=dict(X=get(original_ram,obj+4),Z=get(original_ram,obj+10)),actor_after=dict(X=get(right,obj+4),Z=get(right,obj+10)),full_CPU_public_and_private_RAM_scheduler_boundaries_match=True)
            rows.append(row);(out/f'case-{ordinal}-C-RAM.bin').write_bytes(right)
            save(out/'cases.json',rows)
        _,_,original_ram,task,_=vectors[0];guard_ram,guard_cpu,_=fixture(original_ram,task,rng)
        guards=check_guards(runtime,guard_ram,guard_cpu);save(out/'guards.json',guards)
    except Exception as error:
        (out/'failure-RAM.bin').write_bytes(runtime.device.ram())
        save(out/'status.json',dict(status='terminal_failed',completed_cases=len(rows),error=repr(error),C_pipeline_failure=getattr(runtime,'pipeline_failure',None)));raise
    finally:runtime.close()
    report=dict(status='new_disc_scene_actors_activate_and_update_like_native',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(rows),scene_positions=len({row['scene']for row in rows}),actor_entries=len({(row['scene'],row['task'])for row in rows}),actor_updates=sum(row['iterations']for row in rows),scheduler_activations=len(rows),scheduler_resumptions=sum(row['iterations']for row in rows),cases_with_position_change=sum(row['actor_before']!=row['actor_after']for row in rows),original_CPU_instructions=sum(row['original']['CPU_instructions']for row in rows),source_sha256={name:sha((source/name).read_bytes())for name in NAMES},script_sha256=sha(Path(__file__).read_bytes()),scene_setup_proof=str(ROOT/'verification/scene-queue-restoration-current.json'),scene_setup_directory=str(folder),C_original_GPU_instructions=0,default_promoted=False,scope='Fresh Cscene-setup outputs provide real disc geometry, created task records, actor slots and linked ring. A supplied predecessor yield-call activates each selected freshF4D8task via original/C scheduler; all other actual ring contexts are explicitly blocked. Time step, world geometry, actor state and RNG are inherited without edits. F4D8initialization, realRNG/navigation/movement/collision/GPU4320math and repeated full save/TRAP0/dispatch/RTE/resume execute. FullCPU includingSR/USP/SSP, complete2MBRAM withprivateframes, eachactivation/resumption checkpoint, helperargs/movementobservations and checkeddeviceoutputs match. Pinned core is the originalCPU/GPU oracle and shared hardware device; no originalCPU/GPU instructions execute as Cgamefallback. OnlyF4D8actors, supplied callerregs/supervisorstack, othercontextsblocked, nointerrupt/clockevolution/naturalcaller/globalGPUcontext/otheractorfamilies/livewholegame/standalone proof.')
    report['guards']=guards;report['verified_API']='biwn_actor_pipeline_step';report['helper_dispatch_in_C']=True
    report['DF7A_removal_branch_tested_here']=False
    save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass',cases=len(rows)))
    save(ROOT/'verification'/('loaded-actor-runtime-preflight-current.json'if opt.limit else'loaded-actor-runtime-current.json'),report);print(json.dumps({k:report[k]for k in ['status','directory','cases','actor_entries','actor_updates','cases_with_position_change']}),flush=True)


if __name__=='__main__':main()
