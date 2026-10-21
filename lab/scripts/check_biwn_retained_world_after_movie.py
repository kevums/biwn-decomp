"""Retained movie/NPC/renderer then source world/input/camera and repeated task cycles.

Ready world capture remains initial input. No intermediate trigger capture,
TCB replacement or peripheral reset between trigger/movie/post-dialogue.
"""
import ctypes as c,json,os,struct,subprocess,argparse,wave,hashlib
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_merchant_movie_bridge as bridge
import check_biwn_animation_cpu as animation
import check_biwn_actor_movement_collision as motion
import check_biwn_movie_GPU as fullGPU
import check_biwn_actor_full_movement_runtime as actor
import emulated_pad_input as pad
ROOT=bridge.ROOT;media=bridge.media;save=bridge.save;sha=bridge.sha;controller=bridge.controller;video=bridge.video;AV=bridge.AV;Disc=bridge.Disc
W16=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint16)
class MovementBus(c.Structure):
    _fields_=[("read16",fullGPU.R16),("read32",fullGPU.R32),("write16",W16),("write32",fullGPU.W32),("observe_PC",fullGPU.OBS),("context",c.c_void_p)]
class SpriteBus(c.Structure):
    _fields_=[('read8',fullGPU.R8)]+MovementBus._fields_
class Runtime(bridge.Runtime):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.npc_body=self.lib.biwn_npc_cpu_body;self.npc_body.argtypes=self.npc_call.argtypes;self.npc_body.restype=c.c_int
        self.math=self.lib.biwn_rng_cpu_body;self.math.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU)];self.math.restype=c.c_int
        self.direction=self.lib.biwn_actor_direction_body;self.direction.argtypes=self.math.argtypes;self.direction.restype=c.c_int
        self.yield_fn=self.lib.biwn_scheduler_yield;self.yield_fn.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),c.c_uint32];self.yield_fn.restype=c.c_int
        self.animation=animation.bind(self.lib,body=True)
        self.movement=motion.bind(self.lib)
        self.submit=motion.submit_cpu.bind(self.lib)
        self.collision=motion.collision.bind(self.lib)
        self.movementGPU=self.lib.biwn_movement_fullGPU_run
        self.movementGPU.argtypes=[c.POINTER(MovementBus),c.POINTER(fullGPU.State),c.c_uint32];self.movementGPU.restype=c.c_int
        self.core.GPUWriteWord.argtypes=[c.c_uint32,c.c_uint16,c.c_uint32]
        def w16(_,a,v):self.core.GPUWriteWord(a,v,3);return 0
        self.movement_w16=W16(w16)
        self.movement_bus=MovementBus(self.gpu_callbacks[1],self.gpu_callbacks[2],self.movement_w16,self.gpu_callbacks[3],self.gpu_callbacks[4],None)
        self.pending_movement=False;self.post_calls=[]
        self.device.close();self.device=actor.Device(ROOT/'tools/libbiwn-retained-interior-render-device.dylib');self.oracle.device=self.device
        self.scene_submit=self.device.lib.lab_scene_render_submit;self.scene_submit.argtypes=[c.c_void_p,c.c_uint32,c.c_uint32];self.scene_submit.restype=c.c_int
        self.scene_stat=self.device.lib.lab_scene_render_stat;self.scene_stat.argtypes=[c.c_uint];self.scene_stat.restype=c.c_uint64
        self.scene_hash=self.device.lib.lab_scene_render_PC_hash;self.scene_hash.restype=c.c_uint64
        self.renderer_mode=self.device.lib.lab_retained_renderer_mode;self.renderer_mode.argtypes=[c.c_uint];self.renderer_mode.restype=c.c_int
        self.spriteGPU=self.lib.biwn_sprite_fullGPU_run;self.spriteGPU.argtypes=[c.POINTER(SpriteBus),c.POINTER(fullGPU.State),c.c_uint32];self.spriteGPU.restype=c.c_int
        self.sprite_bus=SpriteBus(self.gpu_callbacks[0],*list(getattr(self.movement_bus,name) for name,_ in MovementBus._fields_))
        self.render_groups={};self.render_CPU={};self.render_complete=False;self.renderer_active=False;self.pending_render=None
        session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
        for name,manifest in [('world_flow','world-flow'),('input_dispatch','input-dispatch'),('resource','resource'),('render_queue','render-queue'),('scene_draw','scene-draw'),('gpu_interior_submit','gpu-interior-submit'),('gpu_projection_submit','gpu-projection-submit'),('gpu_draw_submit','gpu-draw-submit'),('geometry_records','geometry-records'),('display_list','display-list'),('formatter','formatter'),('overlay_text','overlay-text')]:
            fn=getattr(self.lib,'biwn_'+name+'_cpu_body');fn.argtypes=self.fn.argtypes;fn.restype=c.c_int;self.render_CPU[name]=fn
            mapping=json.loads((session/(manifest+'-fullCPU-generation.json')).read_text())
            decoded=mapping.get('instructions_decoded')
            if name=='input_dispatch':
                decoded=[row for pc,row in self.rows.items() if 0x191f4<=pc<0x192a2 or 0x192bc<=pc<0x19f2c]
            for row in decoded:self.render_groups[row['address']]=name
        self.world_camera=self.lib.biwn_camera_cpu_body;self.world_camera.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),media.W8,media.world_cpu.SERVICE,c.c_void_p];self.world_camera.restype=c.c_int
        self.world_target=self.lib.biwn_targeting_cpu_body;self.world_target.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),media.world_cpu.SERVICE,c.c_void_p];self.world_target.restype=c.c_int
        self.poll_body=self.lib.biwn_input_poll_cpu_body;self.poll_body.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU)];self.poll_body.restype=c.c_int
        self.idle_body=self.lib.biwn_task_loop_step;self.idle_body.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),actor.prior.BODY,c.c_void_p,c.c_uint32];self.idle_body.restype=c.c_int
        self.pad=pad.Backend(self.core,self.device);self.global_clock_step=8;self.task_cycles=12;self.idle_pending=None
        self.retained_service=self.service
        def service(_,bus,cpu,target):
            try:
                if target in [0x10252,0x1404c,0x207cc]:
                    result=self.npc_body(bus,cpu,self.callbacks[5],self.service,None,1000000,1)
                    if target==0x207cc and not result:
                        assert cpu.contents.pc==0x20810;self.dialogue_returned=True
                        self.run_boot_exit('movie_exit');self.run_dispatch(True)
                    return result
                if target in [0xe540,0xe588,0xe60a]:return self.math(bus,cpu)
                if self.renderer_active and target==0xe4c0:
                    self.begin_poll();result=self.poll_body(bus,cpu);self.end_poll();return result
                if self.renderer_active and target==0xf0fa:return self.world_camera(bus,cpu,self.callbacks[5],self.service,None)
                if self.renderer_active and target==0x20820:return self.world_target(bus,cpu,self.service,None)
                if target==0x13440:return self.direction(bus,cpu)
                if target in [0xeb04,0x13c9a,0xe220,0x13b5a,0x13bb0]:
                    assert self.dialogue_returned
                    self.post_calls.append(hex(target))
                    if target==0xeb04:return self.animation(bus,cpu,4096)
                    if target==0x13c9a:return self.movement(bus,cpu,c.cast(self.service,motion.SERVICE),None)
                    if target==0xe220:return self.submit(bus,cpu,10000)
                    return self.collision(bus,cpu,4096)
                if self.renderer_active and target in self.render_groups:
                    return self.render_CPU[self.render_groups[target]](bus,cpu,self.callbacks[5],self.service,None,1000000,1)
                return self.retained_service(_,bus,cpu,target)
            except Exception as e:self.errors.append(repr(e));return 1
        self.service=media.world_cpu.SERVICE(service)
    def player_state(self):
        return {hex(a):self.device.read(a,w) for a,w in [(0x49c50,4),(0x49c54,2),(0x49c56,4),(0x49c5a,2),(0x49c5c,2),(0x49c5e,2),(0x49c60,2),(0x49cc4,4)]}
    def begin_poll(self):
        sequence=[[],[0],[0],[],[3],[3],[],[1],[2],[],[],[]]
        buttons=sequence[min(len(self.polls),len(sequence)-1)];self.pad.set_buttons(buttons)
        clock=(self.device.read(0x778cc,4)+self.global_clock_step)&0xffffffff;self.device.direct(0x778cc,4,clock)
        self.polls.append(dict(poll=len(self.polls),buttons=buttons,clock=clock,player_before=self.player_state()))
    def end_poll(self):
        assert self.polls;self.polls[-1].update(held=self.device.read(0x49ba4,4),pressed=self.device.read(0x49bac,4))
    def task_yield(self,s):
        ctx=self.device.read(0xc0920,4)
        if ctx==0xc1528:
            if not self.renderer_active:self.pre_yield_CPU=media.scheduler.cpu_dict(s);self.enable_renderer_context()
            self.npc_yields+=1
        if ctx==0xc0d28:
            self.renderer_end=media.scheduler.cpu_dict(s);self.renderer_yields+=1;self.render_complete=True
        if ctx==0xc2128:self.world_yields+=1
        self.yields.append(dict(context=hex(ctx),CPU=media.scheduler.cpu_dict(s),player=self.player_state(),queue=self.device.read(0x112940,2)))
    def handoff(self,s):
        if self.renderer_active:
            self.handoffs.append(dict(context=hex(self.device.read(0xc0920,4)),CPU=media.scheduler.cpu_dict(s),RAM=sha(self.device.ram()),hardware=self.hardware(),player=self.player_state()))
    def finished(self,s):
        return s.pc==0xef88 and self.device.read(0xc0920,4)==0xc1528 and min(self.npc_yields,self.renderer_yields,self.world_yields)>=self.task_cycles
    def run_C(self,s):
        if self.full_running and s.pc==0xdf60:
            assert self.yield_fn(c.byref(self.bus),c.byref(s),128)==0 and s.pc==0xef88
            self.C_CPU=s
            for _ in range(8192):
                if self.finished(s):return s,None
                ctx=self.device.read(0xc0920,4)
                if s.pc==0xdf60:
                    self.task_yield(s);assert self.yield_fn(c.byref(self.bus),c.byref(s),128)==0;self.handoff(s);continue
                if ctx==0xc1528:
                    status=self.npc_call(c.byref(self.bus),c.byref(s),self.callbacks[5],self.service,None,1000000,1)
                elif ctx==0xc0d28:
                    if s.pc==0x17dce:self.renderer_begin=media.scheduler.cpu_dict(s)
                    status=self.render_CPU['render_queue'](c.byref(self.bus),c.byref(s),self.callbacks[5],self.service,None,1000000,1)
                elif ctx in [0xc5928,0xc5528]:
                    yielding=s.pc in [0xf360,0xf880]
                    if yielding:self.idle_pending=media.CPU.from_buffer_copy(bytes(s))
                    status=self.idle_body(c.byref(self.bus),c.byref(s),actor.prior.BODY(),None,128)
                    if yielding:
                        assert self.idle_pending is None
                        self.handoff(s)
                elif ctx==0xc2128:
                    if s.pc==0xf0fa:status=self.world_camera(c.byref(self.bus),c.byref(s),self.callbacks[5],self.service,None)
                    elif s.pc==0x20820:status=self.world_target(c.byref(self.bus),c.byref(s),self.service,None)
                    else:
                        assert s.pc in self.render_groups,('world continuation',hex(s.pc))
                        status=self.render_CPU[self.render_groups[s.pc]](c.byref(self.bus),c.byref(s),self.callbacks[5],self.service,None,1000000,1)
                    if not status:
                        assert self.rows[s.pc]['assembly']=='rts';s.pc=self.read(s.registers[15],4);s.registers[15]+=4
                        if s.sr&0x2000:s.ssp=s.registers[15]
                        else:s.usp=s.registers[15]
                else:raise AssertionError(('Unexpected runnable context',hex(ctx),hex(s.pc)))
                assert status in [0,6] and not self.errors,(status,hex(s.pc),self.errors)
            raise AssertionError('Source task cycle budget')
        return super().run_C(s)
    def enable_renderer_context(self):
        assert not self.renderer_active
        for task in [0xc0d28,0xc2128,0xc5928,0xc5528]:self.device.direct(task+26,4,0)
        self.renderer_active=True;self.render_queue_before=self.device.read(0x112940,2)
    def start(self,ram,seed,mode):
        super().start(ram,seed,mode)
        assert self.renderer_mode(int(mode=='C'))==0
    def run_render_request(self,command):
        if command==0x4b00:
            self.run_dispatch(False)
            trace=hashlib.sha256();blocks=0;delays=0
            if self.mode=='native':
                image=c.string_at(self.core.GPUGetRAM(),4096)
                for _ in range(2500000):
                    pc=self.core.GPUGetPC()
                    if pc==0xf031be:break
                    trace.update(struct.pack('>I',pc));blocks+=1;word=int.from_bytes(image[pc-0xf03000:pc-0xf03000+2],'big');self.core.GPUExec(1)
                    if word>>10 in [52,53] and self.core.GPUGetPC()!=pc+2:delays+=1
                else:raise AssertionError('Sprite GPU budget')
                raw=video.gpu_state(self.core)[0][:4396];instructions=blocks+delays
            else:
                self.gpu_trace=trace;self.gpu_blocks=0;count=self.gpu_counter.value;begin=self.gpu.instructions
                status=self.spriteGPU(c.byref(self.sprite_bus),c.byref(self.gpu),2500000)
                assert status==0 and self.gpu_counter.value==count,(status,hex(self.gpu.pc))
                c.memmove(self.core.GPUGetRAM(),bytes(self.gpu.local_RAM),4096);blocks=self.gpu_blocks;instructions=self.gpu.instructions-begin;raw=video.logical(self.gpu)
            self.gpu_calls.append(dict(program='sprite_4B00',blocks=blocks,instructions=instructions,PC_sha256=trace.hexdigest(),logical_GPU_sha256=sha(raw)))
            self.run_dispatch(True)
        else:
            # Transfer owned architecture to the shared MMIO/blitter shadow;
            # bridge C kernels preserve it and never execute original GPU.
            if self.mode=='C':
                raw=video.gpu_state(self.core)[0];buf=c.create_string_buffer(video.logical(self.gpu)+raw[4396:]);assert self.core.GPUStateLoad(buf)==len(raw)
            old=self.gpu_counter.value
            status=self.scene_submit(None,0xf03204,command);assert not status,('Scene GPU',hex(command),status)
            raw=video.gpu_state(self.core)[0][:4396]
            if self.mode=='C':
                assert self.gpu_counter.value==old
                count=self.gpu.instructions;self.gpu=fullGPU.state_from_raw(raw);self.gpu.instructions=count
            self.gpu_calls.append(dict(program='retained_scene',command=hex(command),outer_PC_count=self.scene_stat(9),outer_PC_hash=hex(self.scene_hash()),logical_GPU_sha256=sha(raw)))
    def write(self,a,w,v):
        super().write(a,w,v)
        # Observe the existing source idle body after its actual JSR store,
        # before its source scheduler call. No replacement idle instruction.
        if self.idle_pending is not None and w==4 and a==self.idle_pending.registers[15]-4:
            prospective=media.CPU.from_buffer_copy(bytes(self.idle_pending))
            assert v==prospective.pc+6
            prospective.registers[15]-=4;prospective.usp=prospective.registers[15];prospective.pc=0xdf60
            self.task_yield(prospective);self.idle_pending=None
        if self.mode=='C' and a==0xf03204 and w==4 and v==0x4320:self.pending_movement=True
        if self.mode=='C' and a==0xf03204 and w==4 and v in [0x4b00,0x4d80,0x52e0,0x57a0,0x6ae0,0x6da0]:self.pending_render=v
    def read(self,a,w):
        if self.mode=='C' and self.renderer_active and self.device.read(0xc0920,4)==0xc0d28 and a==0x778cc and w==4:
            self.device.direct(a,w,(self.device.read(a,w)+self.global_clock_step)&0xffffffff)
        if self.mode=='C' and self.pending_render is not None and a in [0xf03200,0xf03204]:
            command=self.pending_render;self.pending_render=None;self.run_render_request(command)
        if self.mode=='C' and self.pending_movement and a==0xf03204:
            self.run_movement_request();self.pending_movement=False
        return super().read(a,w)
    def run_movement_request(self):
        self.run_dispatch(False)
        assert (self.core.GPUGetPC() if self.mode=='native' else self.gpu.pc)==0xf03240
        trace=hashlib.sha256();blocks=0;delays=0
        if self.mode=='native':
            image=c.string_at(self.core.GPUGetRAM(),4096)
            for _ in range(100000):
                pc=self.core.GPUGetPC()
                if pc==0xf031be:break
                trace.update(struct.pack('>I',pc));blocks+=1
                word=int.from_bytes(image[pc-0xf03000:pc-0xf03000+2],'big');self.core.GPUExec(1)
                if word>>10 in [52,53] and self.core.GPUGetPC()!=pc+2:delays+=1
            else:raise AssertionError('Native movement GPU budget')
            raw=video.gpu_state(self.core)[0][:4396];instructions=blocks+delays
        else:
            self.gpu_trace=trace;self.gpu_blocks=0;count=self.gpu_counter.value;begin=self.gpu.instructions
            status=self.movementGPU(c.byref(self.movement_bus),c.byref(self.gpu),100000)
            assert status==0 and self.gpu_counter.value==count,(status,hex(self.gpu.pc))
            c.memmove(self.core.GPUGetRAM(),bytes(self.gpu.local_RAM),4096)
            blocks=self.gpu_blocks;instructions=self.gpu.instructions-begin;raw=video.logical(self.gpu)
        self.gpu_calls.append(dict(program='movement_4320',blocks=blocks,instructions=instructions,PC_sha256=trace.hexdigest(),logical_GPU_sha256=sha(raw)))
        self.run_dispatch(True)
    def full_call(self,message,base,seed,mode):
        self.full_running=False;self.pending=None;self.renderer_active=False;self.render_complete=False;self.pending_render=None;self.polls=[];self.yields=[];self.handoffs=[];self.npc_yields=self.renderer_yields=self.world_yields=0;self.pad.set_buttons([]);self.start(base,seed,mode)
        # Existing startup probe entered movie mode; source exit returns to
        # resident readiness before D3FC makes its own source entry request.
        s=media.CPU();s.registers[15]=s.ssp=0x1ff000;s.usp=0x1fe000;s.pc=0xd3ec;s.sr=0x2000;self.device.direct(s.registers[15],4,controller.STOP)
        self.run_native(s,set()) if mode=='native' else self.run_C(s);self.run_boot_exit('movie_exit');self.run_dispatch(True)
        self.message=message;self.rate=round(26590906/(64*(message['SCLK']+1)));self.timeline=0;self.sample_index=0;self.video_index=0;self.word_clocks=0;self.stages=[];self.audio_tokens=[];self.audio_cursor=0;self.audio_reads=0;self.pcm=bytearray();self.sound_digest=hashlib.sha256();self.last_GPU_call=len(self.gpu_calls)
        self.full_running=True;self.pending_movement=False;self.post_calls=[]
        initial=media.CPU();data=self.ready['CPU'];initial.registers[:]=data['registers'];initial.ssp=0x200000;initial.usp=data['usp'];initial.sr=data['sr'];initial.pc=data['pc'];assert initial.pc==0xdf60
        self.dialogue_returned=False
        self.begin_CPU=initial;GPU_before=self.gpu_counter.value;DSP_before=self.counter.value
        result,steps=self.run_native(initial,self.native_coverage) if mode=='native' else self.run_C(initial)
        assert self.sample_index==len(message['sample_records']) and self.video_index==message['video_samples'],('Complete sample table',self.sample_index,len(message['sample_records']))
        assert self.device.read(0xbd85c,2)==0xffff and self.device.read(0xbd85e,2)==0 and self.device.read(0x47b82,2)==0
        assert self.dialogue_returned and self.device.read(self.actor_address+0x6c,2)==2
        if mode=='C':assert self.gpu_counter.value==GPU_before and self.counter.value==DSP_before and self.C_original_CPU_attempts==0
        name=f'message-{message["message_id"]}-{mode}.wav'
        with wave.open(str(self.out/name),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(self.rate);w.writeframes(self.pcm)
        summary=dict(task_cycles=dict(NPC=self.npc_yields,renderer=self.renderer_yields,world=self.world_yields),polls=self.polls,yields=self.yields,handoffs=self.handoffs,renderer_begin=self.renderer_begin,renderer_end=self.renderer_end,render_queue_before=self.render_queue_before,render_queue_after=self.device.read(0x112940,2),post_dialogue_calls=self.post_calls,pre_yield_CPU=self.pre_yield_CPU,source_merchant_message=60,source_return_PC=hex(result.pc),CPU=media.scheduler.cpu_dict(result),RAM=sha(self.device.ram()),hardware=self.snapshot()['hardware'],source_state=self.device.read(0xbd85c,2),samples=self.sample_index,frames=self.video_index,word_clocks=self.word_clocks,sound_digest=self.sound_digest.hexdigest(),PCM_sha256=sha(self.pcm),audio_enqueued=len(self.audio_tokens),queries=self.queries,deliveries=self.deliveries,final_GPU_calls=self.gpu_calls[self.last_GPU_call:])
        (self.out/f'message-{message["message_id"]}-{mode}-final-RAM.bin').write_bytes(self.device.ram())
        self.full_running=False
        return dict(summary=summary,stages=self.stages),dict(audio_reads=self.audio_reads,source_audio_tokens_reached=self.audio_cursor+1,wav=str(self.out/name))
    def run_native(self,s,coverage):
        self.seed_cpu(s);steps=0
        for _ in range(20000000):
            pc=self.core.m68k_get_reg(None,16)
            if pc==controller.STOP:return self.cpu(),steps
            if self.full_running and self.dialogue_returned and self.renderer_active and self.finished(self.cpu()):
                return self.cpu(),steps
            if self.full_running and self.dialogue_returned and pc==0xdf60:self.task_yield(self.cpu())
            if self.renderer_active and self.device.read(0xc0920,4)==0xc2128 and pc==0xe4c0:self.begin_poll()
            if self.renderer_active and self.device.read(0xc0920,4)==0xc2128 and pc==0xe53a:self.end_poll()
            if self.renderer_active and self.device.read(0xc0920,4)==0xc0d28 and pc==0x17dce:self.renderer_begin=media.scheduler.cpu_dict(self.cpu())
            if self.renderer_active and self.device.read(0xc0920,4)==0xc0d28 and pc in [0x17dc2,0x17dd4,0x17de0,0x17dec]:self.device.direct(0x778cc,4,(self.device.read(0x778cc,4)+self.global_clock_step)&0xffffffff)
            if self.full_running and self.dialogue_returned and pc in [0xeb04,0x13c9a,0xe220,0x13b5a,0x13bb0]:
                self.post_calls.append(hex(pc))
            if self.full_running and pc==0xeea8 and not self.dialogue_returned:
                self.dialogue_returned=True;self.run_boot_exit('movie_exit');self.run_dispatch(True)
            if self.full_running and pc==0xd4a8:self.before_dispatch(self.cpu())
            if self.full_running and pc==0xd4de:self.after_dispatch(self.cpu())
            if pc in [0x3000,0x303c,0x304e]:
                state=self.cpu();self.bios(state,pc);self.core.m68k_set_reg(8,state.registers[8]);self.core.m68k_set_reg(9,state.registers[9]);old=self.device.read(pc,2);self.device.direct(pc,2,0x4e75);self.core.m68k_execute(1);self.device.direct(pc,2,old)
            else:
                assert pc in self.rows,hex(pc);coverage.add(pc)
                if pc==0xd3d6 and 0xf031be<=self.core.GPUGetPC()<0xf03200:self.run_dispatch(False);assert self.core.GPUGetPC()==0xf03240;self.native_GPU(True)
                if self.timer_arm and pc in [0xd7bc,0xd7c2]:
                    self.timer_reads+=1
                    if self.timer_reads==3:self.device.direct(0xbd852,4,1)
                if self.full_running and pc==0xe926:
                    raw=self.logical_DSP()
                    if int.from_bytes(raw[0x140:0x144],'big') and self.core.DSPGetControl()&1:self.sound_stream(1)
                if pc==0x22a0e:
                    supervisor=bool(self.core.m68k_get_reg(None,17)&0x2000);self.core.m68k_execute(1);steps+=1
                    if supervisor:self.native_GPU(False)
                    continue
                if pc==0xddfe:self.core.m68k_execute(1);steps+=1;self.native_GPU(False);continue
                self.core.m68k_execute(1)
                if self.renderer_active and pc==0xdf6a:self.handoff(self.cpu())
                if self.full_running and self.dialogue_returned and self.core.GPUReadLong(0xf03204,6)==0x4320:self.run_movement_request()
                if self.renderer_active and self.core.GPUReadLong(0xf03204,6) in [0x4b00,0x4d80,0x52e0,0x57a0,0x6ae0,0x6da0]:self.run_render_request(self.core.GPUReadLong(0xf03204,6))
            steps+=1
        raise AssertionError(('Native full movie caller bound',hex(pc)))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--all',action='store_true');parser.add_argument('--native-reference',type=Path);options=parser.parse_args()
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mappings=[json.loads((session/n).read_text()) for n in ['movie-fullCPU-generation.json','video-fullCPU-generation.json','media-setup-fullCPU-generation.json']]
    poll=controller.movie.generator.loader.base.binary_tools.m68k_instructions((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()[0xe4c0:0xe53c],0xe4c0)[0];geometry=json.loads((session/'geometry-records-fullCPU-generation.json').read_text());boot_CPU=json.loads((session/'GPU-boot-fullCPU-generation.json').read_text())
    privilege=json.loads((session/'movie-privilege-fullCPU-generation.json').read_text())
    npc=json.loads((session/'npc-fullCPU-generation.json').read_text())
    ram_rows=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
    extra=controller.movie.generator.loader.base.binary_tools.m68k_instructions(ram_rows[0xe540:0xe60a],0xe540)[0]+controller.movie.generator.loader.base.binary_tools.m68k_instructions(ram_rows[0x13440:0x134dc],0x13440)[0]+controller.movie.generator.loader.base.binary_tools.m68k_instructions(ram_rows[0xdf60:0xdf6c],0xdf60)[0]+controller.movie.generator.loader.base.binary_tools.m68k_instructions(ram_rows[0xde08:0xde5c],0xde08)[0]
    for lo,hi in [(0x191f4,0x192a2),(0x192bc,0x19f2c),(0xf360,0xf368),(0xf880,0xf888),(0xf0fa,0xf35e),(0x20820,0x20a9c),(0xeac4,0xec04),(0x13c9a,0x13f12),(0xe220,0xe26c),(0x13b5a,0x13c9a),(0x1028e,0x10430),(0x10652,0x106c4)]:
        extra+=controller.movie.generator.loader.base.binary_tools.m68k_instructions(ram_rows[lo:hi],lo)[0]
    for name in ['world-flow','resource','render-queue','scene-draw','gpu-interior-submit','gpu-projection-submit','gpu-draw-submit','geometry-records','display-list','formatter','overlay-text']:
        extra+=json.loads((session/(name+'-fullCPU-generation.json')).read_text())['instructions_decoded']
    rows=extra+npc['instructions_decoded']+privilege['instructions_decoded']+boot_CPU['instructions_decoded']+sum([m['instructions_decoded'] for m in mappings],[])+poll+[x for x in geometry['instructions_decoded'] if 0xe098<=x['address']<0xe0a6]
    out=ROOT/'verification/BIWN-retained-world-after-movie'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);src=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libfull-movie.dylib'
    previous=json.loads((ROOT/'verification/BIWN-movie-source-boot-exit-AV.json').read_text());names=list(previous['source_sha256'])+['biwn_world_flow_cpu.c','biwn_input_dispatch_cpu.c','biwn_camera_cpu.c','biwn_targeting_cpu.c','biwn_task_loops.c']+['biwn_resource_cpu.c']+['biwn_render_queue_cpu.c','biwn_scene_draw_cpu.c','biwn_gpu_interior_submit_cpu.c','biwn_gpu_projection_submit_cpu.c','biwn_gpu_draw_submit_cpu.c','biwn_display_list_cpu.c','biwn_formatter_cpu.c','biwn_overlay_text_cpu.c','biwn_sprite_fullGPU.c']+['biwn_animation_cpu.c','biwn_actor_movement.c','biwn_movement_submit_cpu.c','biwn_actor_collision.c','biwn_geometry_cpu.c','biwn_movement_fullGPU.c','biwn_movie_VBI_event.c','biwn_movie_privilege_cpu.c','biwn_npc_cpu.c','biwn_scheduler.c','biwn_rng_cpu.c','biwn_camera.c','biwn_signed_division.c','biwn_actor_direction.c'];cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(src/n) for n in names],'-o',str(library)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
    disc=Disc(session);frames=Path(json.loads((ROOT/'verification/BIWN-movie-sequence-GPU-C.json').read_text())['directory'])/'C-frames';runtime=Runtime(library,rows,*[m['instructions_decoded'] for m in mappings],disc=disc,out=out,frame_directory=frames)
    extraction=json.loads((ROOT/'verification/BIWN-dialogue-audio-extraction.json').read_text());markers={x['message_id']:int(x['source_long_fields'][2],16) for x in json.loads((ROOT/'verification/NPC-message-video-dependency-inspection.json').read_text())['message_records']}
    ready=json.loads((ROOT/'verification/BIWN-dialogue-ready-NPC.json').read_text());runtime.ready=ready
    base=bytearray(Path(ready['RAM_file']).read_bytes());assert sha(base)==ready['RAM_sha256'];current=int(ready['current_task'],16);actor_address=0x49d6c+206*ready['actor_slot'];runtime.actor_address=actor_address
    def put(a,w,v):base[a:a+w]=v.to_bytes(w,'big')
    obj=current
    for _ in range(128):
        put(obj+26,4,0 if obj==current else 1);obj=int.from_bytes(base[obj:obj+4],'big')
        if obj==current:break
    else:raise AssertionError('Captured task ring bound')
    put(0x49c50,4,int.from_bytes(base[actor_address+4:actor_address+8],'big'));put(0x49c56,4,int.from_bytes(base[actor_address+10:actor_address+14],'big'));put(0x49d1e,4,0)
    base[0x21ea8:0x22770]=(session/'media-video-gpu-21ea0/original-overlay.bin').read_bytes();toc=controller.make_toc(disc.layout);base[0x2c00:0x2c00+len(toc)]=toc
    results=[];coverage=set()
    try:
        for case,m in enumerate([x for x in extraction['messages'] if x['message_id']==60]):
            message={**m,'marker':markers[m['message_id']]};snapshots={};checks={}
            if options.native_reference:
                snapshots['native']=json.loads((options.native_reference/f'message-{m["message_id"]}-native.json').read_text());checks['native']={}
            for mode in (['C'] if options.native_reference else ['native','C']):
                save(out/'status.json',dict(status='running',message=m['message_id'],mode=mode));snapshot,check=runtime.full_call(message,bytes(base),case%3,mode);snapshots[mode]=snapshot;checks[mode]=check
                save(out/f'message-{m["message_id"]}-{mode}.json',snapshot)
                if mode=='native':coverage.update(runtime.native_coverage)
            if snapshots['native']!=snapshots['C']:
                save(out/'mismatch.json',snapshots);raise AssertionError(str(out/'mismatch.json'))
            results.append(dict(message_id=m['message_id'],samples=len(m['sample_records']),audio_samples=m['audio_chunks'],video_frames=m['video_samples'],source_dispatches=len(snapshots['C']['stages']),word_clocks=snapshots['C']['summary']['word_clocks'],disc_requests=len(snapshots['C']['summary']['deliveries']),PCM_sha256=snapshots['C']['summary']['PCM_sha256'],C_checks=checks['C'],original_CPU_GPU_DSP_instructions_on_C_path=0));save(out/'fixtures.json',results);print(json.dumps(dict(message=m['message_id'],status='complete_source_caller_match',frames=m['video_samples'])),flush=True)
        report=dict(status='retained_movie_NPC_renderer_world_input_camera_source_tasks_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),all_six=options.all,messages=results,frames=sum(x['video_frames'] for x in results),audio_samples=sum(x['audio_samples'] for x in results),user_mode_caller=True,source_created_merchant_task=True,source_selected_message=60,source_message_wrapper_and_merchant_return_verified=True,intermediate_trigger_capture_or_reset=False,post_dialogue_state2_facing_verified=True,post_dialogue_animation_movement_sourceyield_verified=True,source_renderer_iteration_verified=True,repeated_world_tasks_verified=True,source_world_cycles=12,renderer_geometry_GPU_reset=False,source_return_PC="0xef88",source_privilege_STOP_and_nested_IRQ_verified=True,source_CPU_coverage=[len(coverage&set(x['address'] for x in mappings[0]['instructions_decoded'])),mappings[0]['instructions']],native_PC_coverage=sorted(coverage),source_sha256={n:sha((src/n).read_bytes()) for n in names},script_sha256=sha(Path(__file__).read_bytes()),word_clocks=sum(x['word_clocks'] for x in results),source_dispatches=sum(x['source_dispatches'] for x in results),disc_requests=sum(x['disc_requests'] for x in results),whole_game_complete=False,BIOS_actual_firmware=False,physical_AV_synchronization=False,
            limits=['Initial source-created readymerchant capture aftercheckedworldload; controllednearplayer/cash0/taskquiescence. No intermediate triggercapture/peripheralreset; actualselfyield/loop choosesmessage60, fullmovie returns, source setsmerchantstate2, runsfacing/EB04 animation/13C9A movement with actualresidentGPU4320 loading/inheritedC GPUstate, then DF60selfyield returnsEF88. Source-created renderer/world/NPC/twoidle contexts cycle on actual frames and scheduler; controlled emulated-pad inputs/globalclock8 ticks remain. Other15 taskcontexts stay quiescent; fullboot/globaltiming/hardware remain unverified. Actual207CCwrapper/18160display/message table args/fullD3FC/merchantreturnEEA8. Other task quiescence, repeats0/no cancellation/busyTRAP0 test. Source movie samples/arguments/pointers/endstate/audio-stop/exit are not host replaced.',
                    'File-backed MSF/LBA disc provider reads declaredrawtracks/swap16/+2alignment at352800Bps with bootstrap ticks; BIOS3000 no-op. No actualfirmware/timing claim.',
                    'GPU movement completion at sourceacknowledgement poll is synchronous; source dispatcher loads its actual overlay; no GPU register/context reset after movie. Renderer geometry keeps inherited GPUstate with source dispatcher program loading; no geometry reseed. Collision helper linkage is not proof of a reached edge branch. Host nominal600unit video clock, sourceVBI progress handler and SCLK18 SSI clocks at dispatch boundaries; no global game schedule/physical scanout.',
                    'Source DSP audio pointer/bytes verified at every enqueue; everyC externalaudio byte checked against its chronological original disc token. FullCPU/RAM/GPU/DSP/peripherals and GPUtrace/counts perdispatch; allDSP/DAC/PCM/counts perwordclock in cumulative digest. Microstates excluded.'])
        save(out/'report.json',report);save(ROOT/'verification/BIWN-retained-world-after-movie.json',report);save(out/'status.json',dict(status='terminal_pass'));print(json.dumps(dict(directory=str(out),frames=report['frames'],audio_samples=report['audio_samples'])))
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e),errors=runtime.errors[-5:]));raise
    finally:runtime.oracle.close();disc.close()
if __name__=='__main__':main()
