"""Scheduled loading followed by world/input/camera, NPC and renderer together.

Host enters 19F2C on the captured world task with a controlled player position.
Six contexts initially run, including renderer; fifteen other contexts are blocked.
Disc completion is an external event after actual scheduler handoff. Full
CPU/private RAM and helper/yield/removal/disc events compare against original.
"""
import ctypes as c
import hashlib
import json
import os
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import check_biwn_interior_loading_cpu as loading
import check_biwn_actor_full_movement_runtime as actor
import generate_biwn_interior_loading_cpu as loader_gen
import generate_biwn_transition_cpu as transition_gen
import generate_biwn_actor_factory_cpu as factory_gen
import generate_biwn_resource_cpu as resource_gen
import check_biwn_render_actors_runtime as startup
import generate_biwn_npc_cpu as npc_gen
import check_biwn_animation_cpu as animation
import generate_biwn_world_flow_cpu as world_gen
import check_biwn_world_cpu as world_cpu
import check_biwn_input_dispatch as dispatch_logic
import emulated_pad_input as pad

ROOT, CPU = loading.ROOT, loading.CPU
save, read, sha = loading.save, loading.read, loading.sha
WORLD, STOP, SSP = 0xc2128, 0x1ffe00, 0x1ff000
RUNNABLE = {WORLD, 0xc1928, 0xc1528, 0xc5928, 0xc5528, startup.RENDER}


class Runtime(loading.Runtime):
    def __init__(self, library, rows, generated):
        super().__init__(library, rows)
        self.device.close()
        self.device = actor.Device(ROOT / 'tools/libbiwn-interior-render-device.dylib')
        self.native_oracle.device = self.device
        self.generated = {row['address']: row for row in generated}
        self.owner = {}
        self.functions = {}
        self.return_functions = {}
        groups = {'interior_loading': loader_gen.RANGES, 'transition': transition_gen.RANGES,
                  'actor_factory': factory_gen.RANGES, 'resource': resource_gen.RANGES,
                  'doorway': {0x10430: 0x10520}, 'npc': npc_gen.RANGES, 'world_flow': world_gen.RANGES}
        session = Path(read(ROOT / 'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
        cd_rows = read(session / 'cd-wrapper-fullCPU-generation.json')['instructions_decoded']
        groups['cd'] = {row['address']: row['address'] + row['size'] for row in cd_rows}
        for name, ranges in groups.items():
            fn = getattr(self.lib, 'biwn_' + name + '_cpu_body')
            fn.argtypes = self.bodies[0x1aa40].argtypes
            fn.restype = c.c_int
            self.functions[name] = fn
            call = getattr(self.lib, 'biwn_' + name + '_cpu_call')
            call.argtypes = fn.argtypes
            call.restype = c.c_int
            self.return_functions[name] = call
            for lo, hi in ranges.items():
                for row in generated:
                    if lo <= row['address'] < hi:
                        self.owner[row['address']] = name
        self.actor_fn = actor.actor.bind(self.lib)
        self.rng = actor.rng_cpu.bind(self.lib)
        self.navigation = actor.navigation.bind(self.lib)
        self.yield_fn = self.lib.biwn_scheduler_yield
        self.remove_fn = self.lib.biwn_scheduler_remove
        for fn in [self.yield_fn, self.remove_fn]:
            fn.argtypes = [c.POINTER(loading.cd.world.Bus), c.POINTER(CPU), c.c_uint32]
            fn.restype = c.c_int
        self.idle_fn = self.lib.biwn_task_loop_step
        self.idle_fn.argtypes = [c.POINTER(loading.cd.world.Bus), c.POINTER(CPU), actor.prior.BODY, c.c_void_p, c.c_uint32]
        self.idle_fn.restype = c.c_int
        self.provider_targets = set(loader_gen.RANGES) | set(transition_gen.RANGES) | set(factory_gen.RANGES)
        self.provider_targets |= set(resource_gen.RANGES) | {0x20e8c, 0x20f0c, 0xe3ee, 0xd1e0, 0xd206, 0xd2f0, 0xd306, 0x10430,
                                                          0x1a77c, 0xe540, 0xe588, 0xe60a,
                                                          0xf368, 0x13f12, 0x13f7c, 0x13fea}

        self.provider_targets |= set(npc_gen.RANGES) | {0x13440,0xe220,0x13c9a,0x13b5a,0x13bb0,0xeb04}
        self.movement = actor.motion.bind(self.lib)
        self.direction = actor.motion.direction.bind(self.lib)
        self.submit = actor.motion.submit_cpu.bind(self.lib)
        self.collision = actor.motion.collision.bind(self.lib)
        self.animation = animation.bind(self.lib,body=True)
        self.functions['npc_movement'] = lambda b,cpu,w8,svc,ctx,budget,flag: self.movement(b,cpu,c.cast(svc,actor.motion.SERVICE),ctx)
        self.functions['npc_direction'] = lambda b,cpu,w8,svc,ctx,budget,flag: self.direction(b,cpu)
        self.functions['npc_submit'] = lambda b,cpu,w8,svc,ctx,budget,flag: self.submit(b,cpu,10000)
        self.functions['npc_collision'] = lambda b,cpu,w8,svc,ctx,budget,flag: self.collision(b,cpu,4096)
        self.functions['npc_animation'] = lambda b,cpu,w8,svc,ctx,budget,flag: self.animation(b,cpu,4096)
        self.owner.update({0x13c9a:'npc_movement',0x13440:'npc_direction',0xe220:'npc_submit',0x13b5a:'npc_collision',0x13bb0:'npc_collision',0xeb04:'npc_animation'})
        self.core.GPUReadLong.argtypes = [c.c_uint32,c.c_uint32]
        self.core.GPUReadLong.restype = c.c_uint32
        original_execute = self.core.m68k_execute
        def execute(cycles):
            result = original_execute(cycles)
            if self.core.GPUReadLong(0xf03204,0) == 0x4320:
                self.device.write(0xf03204,0x4320)
            return result
        self.core.m68k_execute = execute
        self.enable_renderer(session)
        self.enable_world(session)

    def enable_renderer(self, session):
        manifests = {'render_queue':'render-queue', 'scene_draw':'scene-draw',
            'gpu_interior_submit':'gpu-interior-submit','gpu_projection_submit':'gpu-projection-submit',
            'gpu_draw_submit':'gpu-draw-submit','geometry_records':'geometry-records',
            'display_list':'display-list','formatter':'formatter','overlay_text':'overlay-text'}
        for name, manifest in manifests.items():
            mapping = read(session/(manifest+'-fullCPU-generation.json'))
            body = getattr(self.lib,'biwn_'+name+'_cpu_body')
            full = getattr(self.lib,'biwn_'+name+'_cpu_call')
            for fn in [body,full]:
                fn.argtypes = self.bodies[0x1aa40].argtypes
                fn.restype = c.c_int
            self.functions[name] = body
            self.return_functions[name] = full
            for row in mapping['instructions_decoded']:
                self.owner[row['address']] = name
        self.provider_targets |= {0xea20,0xea28,0xe2b8,0xe098,0x17e0e,0xe03a,0x17f14,
            0xe0f2,0xe148,0xe19e,0xe202,0x170a0,0x185b2,0x181f8,0x14776,0x147a6,0x149ae,
            0x1b160,0x1b1a8,0x1b212,0x1b29c,0x1b45a,0xe61c,0xe67c}
        lib = self.device.lib
        lib.lab_scene_render_GPU_RAM.argtypes=[c.c_void_p,c.c_uint]
        lib.lab_scene_render_GPU_RAM.restype=c.c_int
        fixture=(ROOT/'render-assets/biwn-geometry-GPU-RAM-fixture.bin').read_bytes()
        assert lib.lab_scene_render_GPU_RAM(c.create_string_buffer(fixture),4096)==0
        lib.lab_scene_render_submit.argtypes=[c.c_void_p,c.c_uint32,c.c_uint32]
        lib.lab_scene_render_submit.restype=c.c_int
        lib.lab_scene_render_stat.argtypes=[c.c_uint]
        lib.lab_scene_render_stat.restype=c.c_uint64
        lib.lab_scene_render_PC_hash.restype=c.c_uint64
        lib.lab_interior_render_stat.argtypes=[c.c_uint]
        lib.lab_interior_render_stat.restype=c.c_uint64
        self.core.GPUStateSave.argtypes=[c.c_void_p]
        self.core.GPUStateSave.restype=c.c_size_t
        previous_write=self.device.write
        def write(address,value):
            if address&0xffffff==0xf03204 and value in [0x4d80,0x52e0,0x57a0,0x6ae0,0x6da0]:
                return self.render_submit(value)
            return previous_write(address,value)
        self.device.write=write
        previous_read=self.device.read
        def read_value(address,width):
            if self.is_C_run and address&0xffffff==0x778cc and width==4 and self.current()==startup.RENDER:
                value=previous_read(address,width)
                self.device.direct(address,width,(value+self.clock_step)&0xffffffff)
            return previous_read(address,width)
        self.device.read=read_value
        previous_execute=self.core.m68k_execute
        def execute(cycles):
            pc=self.core.m68k_get_reg(None,16)
            if self.current()==startup.RENDER and pc in [0x17dc2,0x17dd4,0x17de0,0x17dec]:
                self.device.direct(0x778cc,4,(self.device.read(0x778cc,4)+self.clock_step)&0xffffffff)
            result=previous_execute(cycles)
            command=self.core.GPUReadLong(0xf03204,0)
            if command==0x4b00:
                self.device.write(0xf03204,command)
            if command in [0x4d80,0x52e0,0x57a0,0x6ae0,0x6da0]:
                self.render_submit(command)
            return result
        self.core.m68k_execute=execute

    def enable_world(self, session):
        # Existing accepted full-CPU providers; the separate world-flow
        # candidate retains source continuations across any nested yield.
        groups = {'input_dispatch':[(0x191f4,0x192a2),(0x192bc,0x19f2c)],
            'input_poll':[(0xe4c0,0xe53c)], 'camera':[(0xf0fa,0xf35e)],
            'targeting':[(0x20820,0x20a9c)]}
        for name, ranges in groups.items():
            body=getattr(self.lib,'biwn_'+name+'_cpu_body')
            if name=='input_dispatch':
                body.argtypes=self.bodies[0x1aa40].argtypes
                wrapper=body
            elif name=='input_poll':
                body.argtypes=[c.POINTER(loading.cd.world.Bus),c.POINTER(CPU)]
                wrapper=lambda b,state,w8,svc,ctx,budget,flag,fn=body:fn(b,state)
            elif name=='camera':
                body.argtypes=[c.POINTER(loading.cd.world.Bus),c.POINTER(CPU),actor.actor.W8,world_cpu.SERVICE,c.c_void_p]
                wrapper=lambda b,state,w8,svc,ctx,budget,flag,fn=body:fn(b,state,w8,c.cast(svc,world_cpu.SERVICE),ctx)
            else:
                body.argtypes=[c.POINTER(loading.cd.world.Bus),c.POINTER(CPU),world_cpu.SERVICE,c.c_void_p]
                wrapper=lambda b,state,w8,svc,ctx,budget,flag,fn=body:fn(b,state,c.cast(svc,world_cpu.SERVICE),ctx)
            body.restype=c.c_int
            self.functions['world_'+name]=wrapper
            for lo,hi in ranges:
                for address in self.rows:
                    if lo<=address<hi:self.owner[address]='world_'+name
        self.provider_targets |= {0x1a188,0x1b718,0xe4c0,0x191f4,0xf0fa,0x20820,0x19fda,0x1a0f8}
        previous_read=self.device.read
        def read_value(address,width):
            if address&0xffffff==0xf14000:
                assert width==4
                return self.pad.sample()
            return previous_read(address,width)
        self.device.read=read_value
        previous_write16=self.device.write16
        def write16(address,value):
            if address&0xffffff==0xf14000:
                self.pad.select(value)
                return
            return previous_write16(address,value)
        self.device.write16=write16

    def player_state(self):
        return {hex(address):self.device.read(address,width) for address,width in
            [(0x49c50,4),(0x49c54,2),(0x49c56,4),(0x49c5a,2),(0x49c5c,2),
             (0x49c5e,2),(0x49c60,2),(0x49c64,2),(0x49c78,4),(0x49cc4,4),(0x49d16,2)]}

    def begin_poll(self):
        sequence=[[],[0],[0],[],[3],[3],[],[1],[2],[]]
        buttons=sequence[min(len(self.poll_inputs),len(sequence)-1)]
        self.pad.set_buttons(buttons)
        clock=(self.device.read(0x778cc,4)+self.clock_step)&0xffffffff
        self.device.direct(0x778cc,4,clock)
        self.poll_inputs.append({'poll':len(self.poll_inputs),'buttons':buttons,'clock':clock})

    def render_submit(self, command):
        lib=self.device.lib
        status=lib.lab_scene_render_submit(None,0xf03204,command)
        if status:
            save(self.output/'failed-render-GPU.json',{'command':hex(command),'status':status,
                'header':hex(self.core.GPUReadLong(0xf03208,0))})
        assert status==0,('render GPU',hex(command),status)
        raw=c.create_string_buffer(8192)
        size=self.core.GPUStateSave(raw)
        assert size>4396
        self.GPU_events.append({'command':hex(command),'RAM_sha256':sha(self.device.ram()),
            'GPU_architecture_and_RAM_sha256':sha(raw.raw[:4396]),
            'direct_PC_count':lib.lab_scene_render_stat(9),
            'direct_PC_hash':hex(lib.lab_scene_render_PC_hash())})

    def statistics(self):
        row=self.device.stats()
        row['scene_render']=[self.device.lib.lab_scene_render_stat(i)for i in range(12)]
        row['interior_render']=[self.device.lib.lab_interior_render_stat(i)for i in range(4)]
        return row

    def begin_frame(self, frame):
        if frame['target']==0xe4c0:
            self.begin_poll()
        if frame['target']==0x1a188:
            frame['player_before']=self.player_state()
        if frame['target']==0xea28:
            frame['queue_count_before']=self.device.read(0x112940,2)
        if frame['target']==0xe2b8:
            sp=frame['incoming']['registers'][15]
            frame['sprite_args']=[self.device.read(sp+4+j*4,4)for j in range(3)]
            index=self.device.read(0xc1528+30,4)
            handle=self.device.read(0x49d6c+index*206+88,4)
            frame['NPC_model_payload']=self.device.read(handle,4) if handle else 0
        return frame

    def current(self):
        return self.device.read(0xc0920, 4)

    def reset_run(self, ram, translated):
        self.device.seed(ram, int(translated))
        self.disc.reset()
        self.calls, self.events, self.errors = [], [], []
        self.frames = defaultdict(list)
        self.idle_pending = None
        self.host_phase = 0
        self.npc_iterations = 0
        self.npc_done = False
        self.npc_remove_pending = False
        self.npc_kill_pending = False
        self.loading_context = None
        self.is_C_run = bool(translated)
        self.GPU_events=[]
        self.sprite_previews=[]
        self.world_updates=[]
        self.poll_inputs=[]
        self.post_removal_renderer_yield=False
        self.post_removal_renderer_pending=False
        self.pad=pad.Backend(self.core,self.device)
        self.pad.set_buttons([])
        self.device.lib.lab_scene_render_reset()

    def event(self, kind, state):
        row = {'kind': kind, 'context': self.current(), 'CPU': loading.cd.scheduler.cpu_dict(state),
               'RAM_sha256': sha(self.device.ram())}
        if kind=='yield' and self.npc_done and self.current()==startup.RENDER:
            assert self.device.read(0x112940,2)==0
            self.post_removal_renderer_pending=True
        if self.host_phase >= 5 and self.current() == 0xc1528:
            if kind == 'yield' and self.device.read(state.registers[15],4) == 0xef88:
                self.npc_iterations += 1
                row['npc_iteration'] = self.npc_iterations
                if self.npc_iterations == self.requested_iterations:
                    self.npc_kill_pending = True
            if kind == 'remove':
                self.npc_remove_pending = True
        self.events.append(row)
        return row

    def handoff(self, state):
        row = self.event('handoff', state)
        if self.post_removal_renderer_pending:
            assert self.current()!=startup.RENDER
            self.post_removal_renderer_yield=True
            self.post_removal_renderer_pending=False
        if self.disc.pending:
            assert self.current() != self.loading_context, 'Completion requires a real loading-task switch'
            row['complete_disc_request'] = len(self.disc.requests)
            self.disc.tick(lambda a, data: c.memmove(self.device.pointer + a, data, len(data)),
                           lambda a, value: self.device.direct(a, 4, value))
            row['RAM_after_external_completion_sha256'] = sha(self.device.ram())
        if self.npc_kill_pending:
            index = self.device.read(0xc1528+30,4)
            self.device.direct(0x49d6c+index*206+2,2,1)
            row['supplied_NPC_kill_stimulus'] = {'actor_slot':index,'flag_word':1,'after_iterations':self.npc_iterations}
            row['RAM_after_host_kill_stimulus_sha256'] = sha(self.device.ram())
            self.npc_kill_pending = False
        if self.npc_remove_pending:
            self.npc_done = True
            self.npc_remove_pending = False

    def bios(self, state, target):
        row = {'target': target, 'context': self.current(), 'actual_body': False,
               'incoming': loading.cd.scheduler.cpu_dict(state)}
        if target == 0x303c:
            assert state.registers[9] <= SSP - 4096
            self.loading_context = self.current()
            self.disc.start(state.registers[8], state.registers[9], state.registers[0])
        else:
            assert target == 0x3042
            self.disc.stop()
        row['return'] = loading.cd.scheduler.cpu_dict(state)
        self.calls.append(row)

    def observe_return(self, state):
        frames = self.frames[self.current()]
        if frames and state.registers[15] == frames[-1]['incoming']['registers'][15]:
            frame = frames.pop()
            frame['return'] = loading.cd.scheduler.cpu_dict(state)
            if frame['target']==0x1a188:
                frame['player_after']=self.player_state()
                frame['time_step']=self.device.read(0x4c24c,4)
                self.world_updates.append(frame)
            if frame['target']==0xe4c0:
                self.poll_inputs[-1]['held']=self.device.read(0x49ba4,4)
                self.poll_inputs[-1]['pressed']=self.device.read(0x49bac,4)
            if frame['target']==0xea28:
                frame['queue_count_after']=self.device.read(0x112940,2)
            if frame['target']==0xe2b8:
                model,index,destination=frame['sprite_args']
                sprite=model+self.device.read(model+12+index*4,4)
                width,height=self.device.read(sprite,1),self.device.read(sprite+1,1)
                assert width and height
                raw=self.device.ram()[destination:destination+width*height*2]
                frame['decoded_sprite']={'dimensions':[width,height],'raw_sha256':sha(raw),
                    'destination':hex(destination),'model_payload':hex(model),'frame_index':index,
                    'matches_source_created_NPC_model':model==frame['NPC_model_payload']}
                self.sprite_previews.append({'raw':raw,'metadata':frame['decoded_sprite']})
            if frame['target'] == 0xdf6c:
                frame['created_context'] = hex(state.registers[0])

    def next_host_stage(self, state):
        """Controlled pose/button entries; source positioning selects the room.

        No scene/gate/actor records or task pool are changed by the host.
        These entries are explicit fixtures, not natural walking/input polling.
        """
        if self.gate['target'] != 312 or self.host_phase >= 5:
            return False
        if self.host_phase == 4:
            self.event('host_stage_return',state)
            assert self.device.read(WORLD+26,4)==0
            state.usp = state.registers[15]
            state.pc = 0x1a544
            self.host_phase = 5
            self.event('host_restore_world_task_entry',state)
            return True
        self.event('host_stage_return', state)
        if self.host_phase % 2 == 0:
            scene = self.device.read(0x49c18, 4)
            count, records = self.device.read(scene, 2), self.device.read(scene + 4, 4)
            stairs = next(records + index * 24 for index in range(count)
                          if self.device.read(records + index * 24, 2) & 0x8000)
            for source_offset, origin, coordinate in [(2, 0x49c6a, 0x49c50), (4, 0x49c72, 0x49c56)]:
                offset = self.device.read(stairs + source_offset, 2)
                if offset & 0x8000:
                    offset -= 65536
                self.device.direct(coordinate, 4, self.device.read(origin, 4) + offset * 64 + 32)
            state.registers[15] -= 4
            self.device.direct(state.registers[15], 4, STOP)
            self.device.direct(state.registers[15] + 4, 4, 0x49c4c)
            state.pc = 0x10520
        else:
            assert state.registers[0] & 65535 == 1, 'Source positioning must find the real stair room'
            room = self.device.read(0x49c78, 4)
            assert self.device.read(room, 2) & 0x8000
            scene = self.device.read(0x49c18, 4)
            assert self.device.read(scene + 12, 2) & 0x8000
            self.device.direct(0x49ba5, 1, 0x10)
            state.registers[15] -= 4
            self.device.direct(state.registers[15], 4, STOP)
            state.pc = 0x1a0f8
        state.usp = state.registers[15]
        self.host_phase += 1
        self.event('host_controlled_entry', state)
        return True

    def native(self, ram, initial, coverage):
        self.reset_run(ram, False)
        loading.cd.lifecycle.seed_cpu(self, initial)
        pending = {}
        steps = []
        for _ in range(2000000):
            if self.npc_done and self.post_removal_renderer_yield:
                break
            pc = self.core.m68k_get_reg(None, 16)
            if pc == STOP:
                state = self.cpu()
                if self.next_host_stage(state):
                    loading.cd.lifecycle.seed_cpu(self, state)
                    continue
                break
            context = self.current()
            assert pc in self.rows, hex(pc)
            if pending.get(context) == pc:
                frame = {'target': pc, 'context': context, 'actual_body': True,
                         'incoming': loading.cd.scheduler.cpu_dict(self.cpu())}
                self.begin_frame(frame)
                self.calls.append(frame)
                self.frames[context].append(frame)
                pending.pop(context)
            if pc in [0x303c, 0x3042]:
                state = self.cpu()
                self.bios(state, pc)
                if pc == 0x3042:
                    self.observe_return(state)
                opcode = self.device.read(pc, 2)
                self.device.direct(pc, 2, 0x4e75)
                self.core.m68k_execute(1)
                self.device.direct(pc, 2, opcode)
                continue
            row = self.rows[pc]
            if row['assembly'] == 'rts':
                self.observe_return(self.cpu())
            if (pc in self.owner or 0xf4d8 <= pc < 0xf712 or 0x13c9a <= pc < 0x13f12) and row['assembly'].startswith(('jsr ', 'bsr.')):
                operand = row['assembly'].split(' ', 1)[1]
                if operand.startswith('('):
                    target = self.core.m68k_get_reg(None, loader_gen.base.register(operand[1:-1]))
                else:
                    target = int(operand.split('$')[1].split('.')[0], 16)
                if target in self.provider_targets and not (target == 0xdfa6 and 0xf4d8 <= pc < 0xf712):
                    pending[context] = target
                elif target not in [0xdf60, 0xdf7a, 0xdfa6, 0x303c, 0x3042]:
                    raise AssertionError(('Unimplemented native source provider', hex(pc), hex(target)))
            if pc in [0xdf60, 0xdf7a]:
                self.event('yield' if pc == 0xdf60 else 'remove', self.cpu())
            steps.append(pc)
            coverage.add(pc)
            self.core.m68k_execute(1)
            if pc == 0xdf6a or (pc == 0xde5a and self.core.m68k_get_reg(None, 16) != 0xdf66):
                self.handoff(self.cpu())
        else:
            raise AssertionError(('Native entrance work bound', hex(pc)))
        if self.current() not in RUNNABLE or any(self.frames.values()) or self.disc.pending or not self.npc_done:
            save(self.output / 'native-open-frames.json', {'CPU': loading.cd.scheduler.cpu_dict(self.cpu()),
                 'context': hex(self.current()), 'frames': dict(self.frames), 'disc_pending': bool(self.disc.pending),
                 'calls': self.calls, 'events': self.events})
            raise AssertionError(str(self.output / 'native-open-frames.json'))
        return self.device.ram(), self.cpu(), {'steps': steps, 'calls': self.calls, 'events': self.events,
               'disc_requests': self.disc.requests, 'disc_completions': self.disc.completions,
               'disc_stops': self.disc.stops, 'device': self.statistics(), 'GPU_submission_events': list(self.GPU_events), 'world_updates': list(self.world_updates), 'poll_inputs': list(self.poll_inputs)}

    def translated(self, ram, initial):
        self.reset_run(ram, True)
        state = CPU.from_buffer_copy(bytes(initial))

        def writer(_, address, value):
            try:
                self.device.write(address, value)
                if self.idle_pending and address == self.idle_pending.registers[15] - 4:
                    prospective = CPU.from_buffer_copy(bytes(self.idle_pending))
                    assert value == prospective.pc + 6
                    prospective.registers[15] -= 4
                    prospective.usp = prospective.registers[15]
                    prospective.pc = 0xdf60
                    self.event('yield', prospective)
                    self.idle_pending = None
                return 0
            except Exception as error:
                self.errors.append(repr(error))
                return 1

        w32 = loading.cd.world.W32(writer)
        bus = loading.cd.world.Bus(self.device.r8, self.device.r16, self.device.r32,
                                  self.device.w16, w32, loading.cd.world.CALL(), None, 0)

        def body(passed, cpu):
            pc = cpu.contents.pc
            if pc in self.owner:
                return self.functions[self.owner[pc]](passed, cpu, self.device.write8, callback, None, 1000000, 1)
            if pc in [0x1a77c, 0xe540, 0xe588, 0xe60a]:
                return self.rng(passed, cpu)
            if pc in [0xf368, 0x13f12, 0x13f7c, 0x13fea]:
                return self.navigation(passed, cpu)
            raise AssertionError(('Unimplemented C source provider', hex(pc)))

        def service(_, passed, cpu, target):
            try:
                if target in [0x303c, 0x3042]:
                    self.bios(cpu.contents, target)
                    return 0
                assert target in self.provider_targets, hex(target)
                context = self.current()
                frame = {'target': target, 'context': context, 'actual_body': True,
                         'incoming': loading.cd.scheduler.cpu_dict(cpu.contents)}
                self.begin_frame(frame)
                self.calls.append(frame)
                self.frames[context].append(frame)
                status = body(passed, cpu)
                if not status:
                    assert self.frames[context][-1] is frame
                    self.observe_return(cpu.contents)
                return status
            except Exception as error:
                self.errors.append(repr(error))
                return 1

        callback = loading.cd.world_cpu.SERVICE(service)
        actor_callback = c.cast(callback, actor.actor.SERVICE)
        for _ in range(10000):
            if self.npc_done and self.post_removal_renderer_yield:
                break
            pc = state.pc
            if pc == STOP:
                if self.next_host_stage(state):
                    continue
                break
            if pc in [0xdf60, 0xdf7a]:
                self.event('yield' if pc == 0xdf60 else 'remove', state)
                fn = self.yield_fn if pc == 0xdf60 else self.remove_fn
                status = fn(c.byref(bus), c.byref(state), 128)
                assert not status, ('Scheduler', status, self.errors)
                self.handoff(state)
                continue
            if pc in [0xf360, 0xf880, 0xf366, 0xf886]:
                yielding = pc in [0xf360, 0xf880]
                if yielding:
                    self.idle_pending = CPU.from_buffer_copy(bytes(state))
                status = self.idle_fn(c.byref(bus), c.byref(state), actor.prior.BODY(), None, 128)
                assert not status, ('Idle', status, self.errors)
                if yielding:
                    assert self.idle_pending is None
                    self.handoff(state)
                continue
            if pc in [0xf4d8, 0xf56e, 0xf70c]:
                status = self.actor_fn(c.byref(bus), c.byref(state), self.device.write8, actor_callback, None, 100000)
                assert status in [0, 6], ('Actor', status, self.errors)
                assert state.pc in [0xdf60, 0xdf7a]
                continue
            status = body(c.byref(bus), c.pointer(state))
            if status == 6:
                assert state.pc in [0xdf60,0xdf7a]
                continue
            assert not status, ('Source body', hex(pc), status, self.errors)
            self.observe_return(state)
            assert self.rows[state.pc]['assembly'] == 'rts', hex(state.pc)
            status = self.return_functions[self.owner[state.pc]](c.byref(bus), c.byref(state),
                     self.device.write8, callback, None, 1, 1)
            assert not status, ('Source RTS', status)
        else:
            raise AssertionError(('C entrance work bound', hex(state.pc), self.errors))
        assert self.current() in RUNNABLE and not any(self.frames.values()) and not self.disc.pending and self.npc_done
        return self.device.ram(), state, {'calls': self.calls, 'events': self.events,
               'disc_requests': self.disc.requests, 'disc_completions': self.disc.completions,
               'disc_stops': self.disc.stops, 'errors': self.errors, 'device': self.statistics(), 'GPU_submission_events': list(self.GPU_events), 'world_updates': list(self.world_updates), 'poll_inputs': list(self.poll_inputs)}


def fixture(capture, info, gate):
    ram = bytearray(capture)
    put = lambda a, w, v: ram.__setitem__(slice(a, a + w), (v & ((1 << (8 * w)) - 1)).to_bytes(w, 'big'))
    for context in startup.CONTEXTS:
        put(context + 26, 4, 0 if context in RUNNABLE else 1)
    put(0xc0920, 4, WORLD)
    put(0x80, 4, 0xde08)
    put(0x88, 4, 0xdeb6)
    put(0x49c8c, 2, gate['tile'])
    direction = gate['directions'][0]
    record = bytes.fromhex(gate['record_hex'])
    key = record[[11, 13, 15, 17][direction]]
    left, right = [(6, 0x4e), (0x4a, 6), (0x52, 12), (12, 0x56)][direction]
    value = int.from_bytes(ram[0x49c4c + right:0x49c4c + right + 2], 'big')
    put(0x49c4c + left, 2, value + key * 64)
    state = CPU()
    state.registers[:] = info['CPU']['registers']
    state.registers[15] = WORLD + 0x3d0
    state.usp, state.ssp, state.sr, state.pc = state.registers[15], SSP, 0x71f, 0x19f2c
    for offset, width, value in [(0, 4, STOP), (4, 2, 0x1000 | gate['gate']), (6, 2, direction), (8, 2, 0)]:
        put(state.registers[15] + offset, width, value)
    return bytes(ram), state


def main():
    out = ROOT / 'verification/biwn-scheduled-world-NPC-render' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    source = ROOT / 'projects/black-ice-white-noise/restoration'
    names = ['biwn_interior_loading_cpu.c', 'biwn_transition_cpu.c', 'biwn_doorway_cpu.c',
             'biwn_actor_factory_cpu.c', 'biwn_resource_cpu.c', 'biwn_cd_cpu.c', 'biwn_actor_task.c',
             'biwn_actor_navigation.c', 'biwn_rng_cpu.c', 'biwn_signed_division.c', 'biwn_camera.c',
             'biwn_scheduler.c', 'biwn_task_loops.c', 'biwn_npc_cpu.c', 'biwn_animation_cpu.c', 'biwn_actor_movement.c', 'biwn_actor_direction.c', 'biwn_movement_submit_cpu.c', 'biwn_actor_collision.c', 'biwn_geometry_cpu.c', 'biwn_render_queue_cpu.c', 'biwn_scene_draw_cpu.c', 'biwn_geometry_records_cpu.c', 'biwn_gpu_interior_submit_cpu.c', 'biwn_gpu_projection_submit_cpu.c', 'biwn_gpu_draw_submit_cpu.c', 'biwn_display_list_cpu.c', 'biwn_formatter_cpu.c', 'biwn_overlay_text_cpu.c', 'biwn_world_flow_cpu.c', 'biwn_input_poll_cpu.c', 'biwn_input_dispatch_cpu.c', 'biwn_camera_cpu.c', 'biwn_targeting_cpu.c']
    library = out / 'libscheduled-world-NPC-render.dylib'
    command = ['clang', '-dynamiclib', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror'] + [str(source / name) for name in names] + ['-o', str(library)]
    compiler = subprocess.run(command, capture_output=True, text=True,
                             env={**os.environ, 'DEVELOPER_DIR': '/Library/Developer/CommandLineTools'})
    (out / 'compiler.txt').write_text(compiler.stdout + compiler.stderr)
    assert compiler.returncode == 0, compiler.stderr
    session = Path(read(ROOT / 'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    generated = []
    for name in ['interior-loading-fullCPU-generation.json', 'transition-fullCPU-generation.json',
                 'doorway-fullCPU-generation.json', 'actor-factory-fullCPU-generation.json',
                 'resource-fullCPU-generation.json', 'cd-wrapper-fullCPU-generation.json', 'npc-fullCPU-generation.json', 'render-queue-fullCPU-generation.json', 'scene-draw-fullCPU-generation.json', 'geometry-records-fullCPU-generation.json', 'gpu-interior-submit-fullCPU-generation.json', 'gpu-projection-submit-fullCPU-generation.json', 'gpu-draw-submit-fullCPU-generation.json', 'display-list-fullCPU-generation.json', 'formatter-fullCPU-generation.json', 'overlay-text-fullCPU-generation.json', 'world-flow-fullCPU-generation.json']:
        generated += read(session / name)['instructions_decoded']
    snapshot = (ROOT / 'render-assets/biwn-inventory-baseline.bin').read_bytes()
    generated += loader_gen.base.binary_tools.m68k_instructions(snapshot[0x13c9a:0x13f12],0x13c9a)[0]
    rows = {row['address']: row for row in generated}
    for lo, hi in actor.navigation.RANGES + actor.rng_cpu.RANGES + [(0xf4d8, 0xf712), (0xdfa6, 0xdfb2),
                   (0xdf60, 0xdf6c), (0xdf7a, 0xdf7c), (0xde08, 0xde5c), (0xdeb6, 0xdee2),
                   (0xf360, 0xf368), (0xf880, 0xf888), (0xeac4,0xec04), (0xeb04,0xeb3a)] + actor.motion.direction.RANGES + actor.motion.submit_cpu.RANGES + actor.motion.collision.RANGES + [(0x1028e,0x10430),(0x10652,0x106c4),(0xe4c0,0xe53c),(0xf0fa,0xf35e),(0x20820,0x20a9c),(0x191f4,0x192a2),(0x192bc,0x19f2c)]:
        rows.update({row['address']: row for row in loader_gen.base.binary_tools.m68k_instructions(snapshot[lo:hi], lo)[0]})
    for address in [0x303c, 0x3042]:
        rows[address] = {'address': address, 'assembly': 'declared BIOS preserve-register RTS adapter'}
    runtime = Runtime(library, list(rows.values()), generated)
    runtime.output = out
    capture_dir = ROOT / 'verification/biwn-render-actors-runtime/20261013T190116.161377Z'
    capture = (capture_dir / 'startup-C-0.bin').read_bytes()
    info = read(capture_dir / 'startup-capture-0.json')
    assert sha(capture) == info['C_RAM_sha256']
    gates = [(gate,n) for gate in read(ROOT / 'verification/biwn-startup-loaded-doorway-candidates.json')['candidates'] if gate['target']==312 for n in [2,8]]
    results, coverage = [], set()
    try:
        for index, (gate,iterations) in enumerate(gates):
            save(out / 'status.json', {'status': 'running', 'case': index, 'gate': gate})
            ram, world_cpu = fixture(capture, info, gate)
            ram=bytearray(ram)
            put=lambda a,w,v:ram.__setitem__(slice(a,a+w),(v&((1<<(w*8))-1)).to_bytes(w,'big'))
            put(0xc0920,4,startup.RENDER)
            put(WORLD+12,4,world_cpu.registers[15])
            put(WORLD+16,4,world_cpu.pc)
            put(WORLD+20,2,world_cpu.sr)
            initial=CPU()
            initial.registers[:]=info['CPU']['registers']
            initial.pc=info['CPU']['pc']
            initial.sr=info['CPU']['sr']
            initial.usp=info['CPU']['usp']
            initial.ssp=SSP
            assert initial.pc==0x17dc2
            ram=bytes(ram)
            runtime.clock_step=8
            runtime.gate = gate
            runtime.requested_iterations = iterations
            (out / f'case-{index}-before-RAM.bin').write_bytes(ram)
            left, expected, native = runtime.native(ram, initial, coverage)
            right, actual, rebuilt = runtime.translated(ram, initial)
            keys = ['calls', 'events', 'disc_requests', 'disc_completions', 'disc_stops', 'GPU_submission_events', 'world_updates', 'poll_inputs']
            if left != right or bytes(expected) != bytes(actual) or any(native[key] != rebuilt[key] for key in keys):
                (out / 'original-final-RAM.bin').write_bytes(left)
                (out / 'C-final-RAM.bin').write_bytes(right)
                save(out / 'mismatch.json', {'case': index, 'gate': gate, 'CPU_original': loading.cd.scheduler.cpu_dict(expected),
                     'CPU_C': loading.cd.scheduler.cpu_dict(actual), 'native': native, 'C': rebuilt,
                     'RAM_diff': [hex(i) for i, (a, b) in enumerate(zip(left, right)) if a != b][:80]})
                raise AssertionError(str(out / 'mismatch.json'))
            assert runtime.device.read(0x49c60, 2) == 2
            assert runtime.device.read(0x49c64, 2) == (314 if gate['target'] == 312 else 17)
            if gate['target'] == 17:
                assert actual.registers[0] == 2
            creations = [call for call in rebuilt['calls'] if call['target'] == 0xdf6c]
            assert len(creations) == 1 and creations[0]['created_context'] == '0xc1528'
            assert runtime.npc_iterations == iterations and runtime.npc_done
            assert len([event for event in rebuilt['events'] if event['kind']=='remove']) == 3
            assert 0xedc4 in native['steps'] and 0xedc4 in runtime.generated
            assert runtime.device.read(0xc0924,4) == 0xc1528
            actor_index = runtime.device.read(0xc1528+30,4)
            assert runtime.device.read(0x49d6c+actor_index*206,2) == 0
            assert not rebuilt['device']['original_GPUExec1_calls'] and not rebuilt['device']['game_frames_executed']
            assert rebuilt['device']['C_sprite_decodes']>0
            assert native['device']['original_GPU_sprite_decodes']==rebuilt['device']['C_sprite_decodes']
            assert rebuilt['GPU_submission_events'] and not rebuilt['device']['scene_render'][8]
            assert rebuilt['world_updates'] and rebuilt['poll_inputs']
            assert all(row['player_after']['0x49c60']==2 for row in rebuilt['world_updates'])
            (out / f'case-{index}-C-final-RAM.bin').write_bytes(right)
            if index==0:
                import animation_renderer
                pointer=runtime.device.read(0x43daa,4)
                assert pointer==runtime.device.read(0xbd844,4)
                raw=right[pointer:pointer+80640]
                (out/'C-final-geometry.raw16be').write_bytes(raw)
                (out/'C-final-geometry.png').write_bytes(animation_renderer.image_png(raw,224,180,3))
                NPC_previews=[p for p in runtime.sprite_previews if p['metadata']['matches_source_created_NPC_model']]
                if NPC_previews:
                    sprite=NPC_previews[-1]
                    width,height=sprite['metadata']['dimensions']
                    (out/'C-decoded-NPC-sprite.raw16be').write_bytes(sprite['raw'])
                    (out/'C-decoded-NPC-sprite.png').write_bytes(animation_renderer.image_png(sprite['raw'],width,height,3))
                    save(out/'NPC-sprite-preview.json',sprite['metadata'])
            results.append({'case': index, 'gate': gate, 'CPU': loading.cd.scheduler.cpu_dict(actual),
                            'NPC_iterations': iterations, 'before_RAM_sha256': sha(ram), 'after_RAM_sha256': sha(right), 'native': native, 'C': rebuilt})
            save(out / 'fixtures.json', results)
        generated_addresses = {row['address'] for row in generated}
        groups = {}
        for name in ['interior-loading', 'transition', 'doorway', 'actor-factory', 'resource', 'cd-wrapper', 'npc', 'world-flow']:
            mapping = read(session / (name + '-fullCPU-generation.json'))
            addresses = {row['address'] for row in mapping['instructions_decoded']}
            groups[name] = [len(addresses & coverage), len(addresses)]
        save(out / 'coverage.json', {'generated_instruction_count': len(generated_addresses),
                   'exercised_generated_instructions': len(generated_addresses & coverage),
                   'source_group_instruction_coverage': groups, 'native_PC_coverage': sorted(coverage)})
        report = {'recorded_at': datetime.now(timezone.utc).isoformat(), 'status': 'scheduled_source_loading_world_input_camera_NPC_and_mode2_renderer_native_C_match',
                  'directory': str(out), 'cases': len(results), 'source_interiors': [312, 313, 314],
                  'disc_transfers': sum(len(row['C']['disc_requests']) for row in results),
                  'transferred_bytes': sum(sum(req['bytes'] for req in row['C']['disc_requests']) for row in results),
                  'task_removals': sum(sum(event['kind'] == 'remove' for event in row['C']['events']) for row in results),
                  'task_creations': sum(sum(call['target'] == 0xdf6c for call in row['C']['calls']) for row in results),
                  'source_stair_transitions_312_to_313_to_314': len(results)*2,
                  'NPC_iterations': sum(row['NPC_iterations'] for row in results),
                  'NPC_task_execution_verified_for_declared_cases':True,
                  'world_updates':sum(len(row['C']['world_updates']) for row in results),
                  'input_polls':sum(len(row['C']['poll_inputs']) for row in results),
                  'world_task_runnable_after_loading':True,
                  'emulated_pad_poll_and_source_dispatch_camera_targeting_linked':True,
                  'renderer_sprite_consumer_and_interior_scene_linked':True,
                  'GPU_submissions':sum(len(row['C']['GPU_submission_events'])for row in results),
                  'C_sprite_decodes':sum(row['C']['device']['C_sprite_decodes']for row in results),
                  'C_resident_blits':sum(row['C']['device']['scene_render'][11]for row in results),
                  'whole_GPU_architecture_RAM_direct_PC_count_hash_per_render_command_compared':True,
                  'dialogue_and_transaction_branches_verified':False,
                  'native_CPU_steps': sum(len(row['native']['steps']) for row in results),
                  'source_sha256': {name: sha((source / name).read_bytes()) for name in names}, 'compiler': command,
                  'test_script_sha256': sha(Path(__file__).read_bytes()), 'source_group_instruction_coverage': groups,
                  'full_CPU_RAM_privateframes_helper_yield_removal_disc_events_match': True,
                  'source_boundary_transition_and_scheduled_loading_verified_for_declared_fixtures': True,
                  'original_CPU_or_GPU_execution_on_C_side': False, 'new_published_components': 0,
                  'whole_game_complete': False, 'playable': False,
                  'limits': ['Controlled startup gate/stair entries retain captured CPU and host pose/button/kill fixtures. After loading, the world task runs its source loop alongside NPC/renderer/idles, polls externally supplied emulated-pad buttons, dispatches input and updates movement/camera/targeting. Fifteen other task contexts stay blocked; initial world-loop entry/clock/BIOS completion remain fixtures.',
                             'Actual EA28 queue consumer/E2B8 decode,17E0E interior scene,geometry/projection/draw wrappers,displaylist,overlay/formatter/text execute together with source-created EDC4 and resource lifetimes. Main2MBRAM/fullCPU/private frames/helper/disc/scheduler events and each renderGPU logical4396-byte architecture/RAM/directPC count/hash compare.',
                             'GPU6AE0 geometry retains per-frame reset/seed/fixed4KB RAM/resident injection; context thereafter inherited through actor geometry/projection/draw. Movement/sprite programs keep existing synchronous adapters; globalGPUarchitecture across kernels/boot is not proved. Shared pinned blitter; decoded sprite/geometry planes are not objectprocessor scanout or physical display/FPS.',
                             'Merchant dialogue/messages/purchases, physical controller input, uninterrupted boot/full-world lifecycle, other tasks/audio/scanout/backendaccuracy/fullplayablegame remain unfinished. Source world-flow candidate/guard/coverage scope must be reviewed separately. No new model-generated instruction bodies/training/default/preset changes.']}
        save(out / 'report.json', report)
        save(out / 'status.json', {'status': 'terminal_pass'})
        save(ROOT / 'verification/biwn-scheduled-world-NPC-render-checks.json', report)
        print(json.dumps(report))
    except Exception as error:
        save(out / 'status.json', {'status': 'terminal_failed', 'error': repr(error), 'errors': runtime.errors})
        raise
    finally:
        runtime.close()


if __name__ == '__main__':
    main()
