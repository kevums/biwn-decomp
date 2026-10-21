"""Repeated selected-actor + scene-render C ticks against original CPU/GPU.

C RAM and actor CPU continue between ticks; device state is explicitly reset
at each comparison entry. Original reference phases consume the same entry
state. This is not a whole-game/global-GPU/interrupt scheduler proof.
"""
import argparse,ctypes as c,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_loaded_actor_runtime as actors
import check_biwn_scene_render_pipeline as render

ROOT=actors.ROOT;CPU=actors.CPU;world=actors.world;get=actors.get;sha=actors.sha;save=actors.save

class Runtime(render.Render):
    def __init__(self,library):
        super().__init__(library);self.prefix=(c.c_uint32*18).in_dll(self.core,'regs')
        self.tick=self.lib.biwn_actor_scene_tick
        self.tick.argtypes=[c.POINTER(world.Bus),c.POINTER(CPU),type(self.device.write8)]+[c.c_uint32]*2+[c.POINTER(c.c_uint32)]+[c.c_uint32]*3+[c.POINTER(c.c_uint32),actors.OBSERVER,c.c_void_p]
        self.tick.restype=c.c_int
    def cpu(self):
        state=CPU();state.registers[:]=[self.core.m68k_get_reg(None,i)for i in range(16)]
        state.pc=self.core.m68k_get_reg(None,16);state.sr=self.core.m68k_get_reg(None,17);state.usp=state.registers[15];state.ssp=self.prefix[17];return state
    def native_actor(self,ram,cpu,task):
        self.seed(ram,0);actors.lifecycle.seed_cpu(self,cpu);calls=[];steps=[];movements=0
        for _ in range(20000):
            pc=self.core.m68k_get_reg(None,16)
            if pc==0xf70c and movements:break
            assert any(a<=pc<b for a,b in actors.RANGES),hex(pc)
            if pc in actors.live.NAV:
                offset=self.core.m68k_get_reg(None,15)+4;args=[]
                for width in actors.live.actor.WIDTHS[pc]:args.append(get(self.device.ram(),offset,width));offset+=width
                calls.append([hex(pc),args])
                if pc==0x13c9a:movements+=1
            steps.append(pc);self.core.m68k_execute(1)
            if self.core.GPUReadLong(0xf03204,0)==0x4320:self.device.write(0xf03204,0x4320)
        else:raise AssertionError('Original actor tick failed to resume')
        assert movements==1 and get(self.device.ram(),0xc0920)==task
        return self.device.ram(),self.cpu(),dict(calls=calls,instructions=len(steps))
    def native_render_current(self,ram,incoming):
        seed=self.seed;self.seed=lambda ram,mode:None
        try:return super().native(ram,incoming)
        finally:self.seed=seed
    def translated_tick(self,ram,initial,expected_task,incoming,**overrides):
        self.seed(ram,1);cpu=CPU.from_buffer_copy(bytes(initial));calls=[];capture={};errors=[]
        def observe(_,target,state):
            try:
                if target not in actors.live.NAV:return
                offset=state.contents.registers[15]+4;args=[]
                for width in actors.live.actor.WIDTHS[target]:args.append(get(self.device.ram(),offset,width));offset+=width
                calls.append([hex(target),args])
            except Exception as error:errors.append(repr(error))
        observer=actors.OBSERVER(observe);old_write=self.device.write
        def write(a,v):
            if a==0xf02268 and not capture:
                capture.update(RAM=self.device.ram(),CPU=bytes(cpu))
                if overrides.get('render_failure'):raise RuntimeError('injected render write failure')
            old_write(a,v)
        self.device.write=write
        callback=world.CALL(lambda *_:1)
        bus=world.Bus(self.device.r8,self.device.r16,self.device.r32,self.device.w16,self.device.w32,callback,None,0)
        if overrides.get('missing_read16'):bus.read16=world.R16()
        if overrides.get('unsupported_PC'):cpu.pc=0
        if overrides.get('supervisor'):cpu.sr|=0x2000
        before=bytes(cpu);result=c.c_uint32(0xa55aa55a);links=(c.c_uint32*64)()
        args=dict(task=expected_task,scratch=render.SP-512,capacity=64,budget=32768);args.update({k:v for k,v in overrides.items()if k in args})
        try:
            status=self.tick(None if overrides.get('null_bus')else c.byref(bus),None if overrides.get('null_CPU')else c.byref(cpu),type(self.device.write8)()if overrides.get('null_write8')else self.device.write8,args['task'],args['scratch'],None if overrides.get('null_links')else links,args['capacity'],args['budget'],incoming,None if overrides.get('null_output')else c.byref(result),observer,None)
            return self.device.ram(),cpu,result.value,dict(status=status,CPU_unchanged=bytes(cpu)==before,calls=calls,errors=errors,device_errors=list(self.device.errors),capture=capture,render=self.state())
        finally:self.device.write=old_write

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--frames',type=int,default=64);opt=ap.parse_args();assert 1<=opt.frames<=256
    out=ROOT/'verification/actor-scene-tick'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    workflow=json.loads((ROOT/'verification/local-actor-scene-tick-workflow-current.json').read_text());candidate=Path(workflow['directory'])/'candidate.c'
    source=ROOT/'projects/black-ice-white-noise/restoration';names=list(dict.fromkeys(actors.NAMES+render.scene.SOURCES+render.EXTRA))
    library=out/'libactor-scene-tick.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(source),*[str(source/n)for n in names],str(candidate),'-o',str(library)]
    built=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(built.stdout+built.stderr);assert not built.returncode,built.stderr
    nearby=json.loads((ROOT/'verification/nearby-actor-scene-current.json').read_text());folder=Path(nearby['directory']);cases=json.loads((folder/'cases.json').read_text())
    chosen=[row for row in cases if row['actor']['scene']==0 and row['actor']['steps']==1][:2];assert len(chosen)==2
    loaded=(folder/'scene-0-loaded-C-RAM.bin').read_bytes();runtime=Runtime(library);rng=random.Random(0xf70c17e0e);rows=[];final=[]
    try:
        for ordinal,row in enumerate(chosen):
            task=int(row['actor']['task'],16);obj=int(row['actor']['object'],16);ram,cpu,fixture=actors.fixture(loaded,task,rng)
            first_ram=ram;first_cpu=CPU.from_buffer_copy(bytes(cpu));first_image=None
            for frame in range(opt.frames):
                save(out/'status.json',dict(status='running',actor=ordinal,frame=frame))
                actor_ram,expected_cpu,old_actor=runtime.native_actor(ram,cpu,task)
                incoming=[rng.getrandbits(32)for _ in render.scene.world.REGS]
                left,expected,old_render=runtime.native_render_current(actor_ram,incoming)
                right,actual,value,new=runtime.translated_tick(ram,cpu,task,incoming[0])
                assert new['status']==0 and not new['errors']and not new['device_errors'],new
                assert new['capture']['RAM']==actor_ram and new['capture']['CPU']==bytes(expected_cpu)
                assert bytes(actual)==bytes(expected_cpu)and new['calls']==old_actor['calls']
                assert value==expected and render.scene.native.masked(left)==render.scene.native.masked(right)
                assert all(old_render[k]==new['render'][k]for k in ['hardware','GPU_mailboxes','GPU_submissions'])
                assert not new['render']['device']['scene_render']['native_GPU_steps']and not new['render']['device']['original_GPUExec1_calls']and not new['render']['device']['device_error']
                fb=get(right,0xbd844);pixels=right[fb:fb+224*180*2];assert pixels==left[fb:fb+224*180*2]
                import animation_renderer
                image=out/f'actor-{ordinal}-frame-{frame:03d}.png';image.write_bytes(animation_renderer.image_png(pixels,224,180,scale=3));(out/f'actor-{ordinal}-frame-{frame:03d}.raw16be').write_bytes(pixels)
                if first_image is None:first_image=pixels
                changed=sum(first_image[i:i+2]!=pixels[i:i+2]for i in range(0,len(pixels),2))
                rows.append(dict(actor=ordinal,task=hex(task),frame=frame,coordinates=dict(X=get(right,obj+4),Y=get(right,obj+8,2),Z=get(right,obj+10)),image=str(image),framebuffer_sha256=sha(pixels),pixels_changed_from_first=changed,actor_native_instructions=old_actor['instructions'],CPU=actors.live.prior.scheduler.cpu_dict(actual),public_RAM_sha256=sha(render.scene.native.masked(right)),original_actor_calls=old_actor['calls'],native_C_actor_checkpoint_and_render_match=True))
                ram=right;cpu=actual
            (out/f'actor-{ordinal}-final-C-RAM.bin').write_bytes(ram);final.append(dict(task=hex(task),object=hex(obj),CPU=actors.live.prior.scheduler.cpu_dict(cpu),RAM_sha256=sha(ram),fixture=fixture))
        guards=[]
        for override in [dict(budget=0),dict(capacity=0),dict(scratch=0),dict(scratch=257),dict(task=0),dict(task=3),dict(null_bus=True),dict(null_CPU=True),dict(null_write8=True),dict(null_links=True),dict(null_output=True),dict(missing_read16=True),dict(supervisor=True),dict(unsupported_PC=True)]:
            after,state,value,result=runtime.translated_tick(first_ram,first_cpu,int(chosen[-1]['actor']['task'],16),0x1234,**override)
            assert result['status']==(3 if 'unsupported_PC'in override else 1)and after==first_ram and result['CPU_unchanged']and value==0xa55aa55a
            guards.append(dict(parameters=override,status=result['status']))
        task=int(chosen[-1]['actor']['task'],16);obj=int(chosen[-1]['actor']['object'],16)
        after,state,value,result=runtime.translated_tick(first_ram,first_cpu,task,0x1234,render_failure=True)
        assert result['status']==5 and state.pc==0xf70c and value==0xa55aa55a and after==result['capture']['RAM']and bytes(state)==result['capture']['CPU'];guards.append(dict(render_failure_status=5,completed_actor_effects_retained=True))
        dead=bytearray(first_ram);dead[obj+2:obj+4]=(1).to_bytes(2,'big')
        after,state,value,result=runtime.translated_tick(bytes(dead),first_cpu,task,0x1234)
        assert result['status']==4 and state.pc==0xdf7a and not get(after,obj,2)and value==0xa55aa55a and not result['capture'];guards.append(dict(death_status=4,pending_source_removal_preserved=True))
        after,state,value,result=runtime.translated_tick(first_ram,first_cpu,task+0x400,0x1234)
        assert result['status']==3 and state.pc==0xf4d8 and value==0xa55aa55a and not result['capture'];guards.append(dict(other_task_status=3,actual_handoff_retained=True))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',completed_ticks=len(rows),error=repr(error)));raise
    finally:runtime.close()
    save(out/'frames.json',rows);save(out/'final.json',final);save(out/'guards.json',guards)
    report=dict(status='linked_actor_and_scene_C_ticks_match_original_phases',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),actors=len(chosen),frames_per_actor=opt.frames,ticks=len(rows),guards=len(guards),actor_native_instructions=sum(row['actor_native_instructions']for row in rows),unique_images_per_actor=[len({row['framebuffer_sha256']for row in rows if row['actor']==i})for i in range(len(chosen))],maximum_changed_pixels=max(row['pixels_changed_from_first']for row in rows),candidate_sha256=sha(candidate.read_bytes()),source_sha256={n:sha((source/n).read_bytes())for n in names},header_sha256=sha((source/'biwn_actor_scene_tick.h').read_bytes()),script_sha256=sha(Path(__file__).read_bytes()),library_sha256=sha(library.read_bytes()),device_sha256=sha(render.DEVICE.read_bytes()),local_author_workflow=str(ROOT/'verification/local-actor-scene-tick-workflow-current.json'),nearby_scene_proof=str(ROOT/'verification/nearby-actor-scene-current.json'),default_promoted=False,scope='One Cfacade links sourceactor, actualyield/resume and linkedscene draw on sameRAM. CactorCPU/RAM carrybetween ticks, includingrenderer-writtenactorrecordindices used bynextmovement. Originalactor phase comparesallCPU/privateframes/full2MBRAM atpreclear checkpoint; originalrender comparesD0/publicRAM/7blitterregs/8GPUmailboxes/fullGPUcommandarchitectureRAMPCpaths. Reference consumescommonCentrystate eachtick. Declareddevice/GPUreset+synchronouscompletion percomparison, otherloadedringcontextsblocked, frozenclock/input/camera andcapturedresidentRAM/art remain; not uninterruptedglobalGPU/timing/interrupts/otheractors/fullmainloop/animation/standalonegame. LocalAuthorwrotefacadefromcoordinator API/algorithm; coordinatorverifier, no newweighttraining.')
    save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass',ticks=len(rows)))
    save(ROOT/'verification'/('actor-scene-tick-current.json'if opt.frames==64 else'actor-scene-tick-preflight-current.json'),report);print(json.dumps({k:report[k]for k in ['status','directory','ticks','unique_images_per_actor','maximum_changed_pixels','guards']}),flush=True)

if __name__=='__main__':main()
