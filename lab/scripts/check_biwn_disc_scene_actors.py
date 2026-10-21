"""Two real actors in C-startup disc geometry, retaining the created21-context ring."""
import argparse
import collections
import ctypes as c
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import check_biwn_actor_full_movement_runtime as live
import check_biwn_actor_lifecycle_runtime as lifecycle
import check_biwn_render_actors_runtime as startup
import check_biwn_world_cpu as world_cpu
import emulated_pad_input as pad
import check_biwn_input_dispatch as dispatch_logic
from biwn_disc_backend import Disc
from check_biwn_resources_native import Position

ROOT = live.ROOT
CPU = live.CPU
ACTORS = [0xc1928,0xc1528]
IDLES = [0xc5928,0xc5528]
RUNNABLE = set(ACTORS+IDLES)
get = live.get
save = live.save

class Plan:
    def __init__(self, runtime):
        self.runtime=runtime;self.calls=[];self.movements=[];self.counts=collections.Counter()
    def observe(self,target,args,incoming):
        context=self.runtime.current()
        self.calls.append(['call',context,target,args,incoming])
        if target == 0x13c9a:
            self.counts[context]+=1
            obj=args[0];ram=self.runtime.device.ram()
            self.movements.append({'context':context,'iteration':self.counts[context], 'object':obj,
                                   'X':get(ram,obj+4),'Y':get(ram,obj+8,2),'Z':get(ram,obj+10),
                                   'mode':get(ram,obj+20,2),'room':get(ram,obj+64,2),'tile':get(ram,obj+66,2),
                                   'tile_pointer':get(ram,obj+68),'collision':get(ram,obj+196,2)})
    def done(self, iterations):
        return all(self.counts[context]>=iterations for context in ACTORS)

class Runtime(live.Runtime):
    def current(self):
        return int.from_bytes(c.string_at(self.device.pointer+0xc0920,4),'big')
    def event(self,state):
        if getattr(self,'real_render_queue',False):return {'context':self.current(),'CPU':live.prior.scheduler.cpu_dict(state)}
        return super().event(state)
    def enable_world(self,clock_step):
        self.world_mode=True;self.clock_step=clock_step;self.world_context=0xc2128
        self.world_body=self.lib.biwn_world_cpu_body;self.world_body.argtypes=[c.POINTER(live.world.Bus),c.POINTER(CPU),world_cpu.SERVICE,c.c_void_p,c.c_uint32];self.world_body.restype=c.c_int
        self.poll_body=self.lib.biwn_input_poll_cpu_body;self.poll_body.argtypes=[c.POINTER(live.world.Bus),c.POINTER(CPU)];self.poll_body.restype=c.c_int
    def enable_animation(self):
        self.real_animation=True;self.animation_body=self.lib.biwn_animation_cpu_body;self.animation_body.argtypes=[c.POINTER(live.world.Bus),c.POINTER(CPU),c.c_uint32];self.animation_body.restype=c.c_int
    def enable_camera(self):
        self.real_camera=True;self.camera_body=self.lib.biwn_camera_cpu_body;self.camera_body.argtypes=[c.POINTER(live.world.Bus),c.POINTER(CPU),live.actor.W8,world_cpu.SERVICE,c.c_void_p];self.camera_body.restype=c.c_int
    def enable_targeting(self):
        self.real_targeting=True;self.targeting_body=self.lib.biwn_targeting_cpu_body;self.targeting_body.argtypes=[c.POINTER(live.world.Bus),c.POINTER(CPU),world_cpu.SERVICE,c.c_void_p];self.targeting_body.restype=c.c_int
    def enable_dispatch(self):
        self.real_dispatch=True;self.dispatch_body=self.lib.biwn_input_dispatch_cpu_body;self.dispatch_body.argtypes=[c.POINTER(live.world.Bus),c.POINTER(CPU),live.actor.W8,world_cpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];self.dispatch_body.restype=c.c_int
    def enable_resource_fixture(self,button_sequence):
        self.resource_fixture_enabled=True;self.world_button_sequence=button_sequence
    def enable_resource_memory(self):
        self.real_resource_memory=True;self.resource_body=self.lib.biwn_resource_cpu_body;self.resource_body.argtypes=[c.POINTER(live.world.Bus),c.POINTER(CPU),live.actor.W8,world_cpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];self.resource_body.restype=c.c_int
    def enable_resource_disc(self):
        self.enable_resource_memory();self.real_resource_disc=True;self.disc=Disc();self.cd_math=self.lib.biwn_cd_offset_msf;self.cd_math.argtypes=[c.c_uint32,c.c_uint32,c.c_void_p,c.c_size_t,c.POINTER(Position)];self.cd_math.restype=c.c_int
    def enable_cd_cpu(self):
        self.real_cd_cpu=True;self.cd_body=self.lib.biwn_cd_cpu_body;self.cd_body.argtypes=[c.POINTER(live.world.Bus),c.POINTER(CPU),live.actor.W8,world_cpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];self.cd_body.restype=c.c_int
    def enable_loading_yields(self):
        self.loading_yields_real=True
    def enable_render_queue(self):
        self.real_render_queue=True;self.render_queue_body=self.lib.biwn_render_queue_cpu_body;self.render_queue_body.argtypes=[c.POINTER(live.world.Bus),c.POINTER(CPU),live.actor.W8,world_cpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];self.render_queue_body.restype=c.c_int
    def enable_scene_draw(self):
        self.real_scene_draw=True;self.scene_draw_body=self.lib.biwn_scene_draw_cpu_body;self.scene_draw_body.argtypes=[c.POINTER(live.world.Bus),c.POINTER(CPU),live.actor.W8,world_cpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];self.scene_draw_body.restype=c.c_int
    def enable_geometry_records(self):
        self.real_geometry_records=True;self.geometry_records_body=self.lib.biwn_geometry_records_cpu_body;self.geometry_records_body.argtypes=[c.POINTER(live.world.Bus),c.POINTER(CPU),live.actor.W8,world_cpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];self.geometry_records_body.restype=c.c_int
    def enable_GPU_geometry(self):
        self.real_GPU_geometry=True;self.GPU_geometry_submit=self.lib.biwn_gpu_geometry_submit_cpu_body;self.GPU_geometry_submit.argtypes=[c.POINTER(live.world.Bus),c.POINTER(CPU),live.actor.W8,world_cpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];self.GPU_geometry_submit.restype=c.c_int
    def enable_display_list_CPU(self):
        self.real_display_list_CPU=True;self.display_list_CPU=self.lib.biwn_display_list_cpu_body
        self.display_list_CPU.argtypes=[c.POINTER(live.world.Bus),c.POINTER(CPU),live.actor.W8,world_cpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];self.display_list_CPU.restype=c.c_int
    def enable_overlay_text_CPU(self):
        self.real_overlay_text_CPU=True;self.overlay_text_CPU=self.lib.biwn_overlay_text_cpu_body;self.formatter_CPU=self.lib.biwn_formatter_cpu_body
        for fn in [self.overlay_text_CPU,self.formatter_CPU]:
            fn.argtypes=[c.POINTER(live.world.Bus),c.POINTER(CPU),live.actor.W8,world_cpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];fn.restype=c.c_int
        self.overlay_text_entries={0x181f8,0x14776,0x147a6,0x149ae,0xe540}
        self.formatter_entries={0x1b160,0x1b1a8,0x1b212,0x1b29c,0x1b45a,0xe61c,0xe67c}
        self.overlay_text_returns={0x18552,0x147a4,0x149ac,0x14ca8,0xe586,0x1b19e,0x1b1fe,0x1b29a,0x1b458,0x1b476,0xe676,0xe68a}
    def overlay_text_begin(self,state,target):
        row={'target':target,'incoming':live.prior.scheduler.cpu_dict(state)};self.overlay_text_CPU_calls.append(row);return row
    def display_list_begin(self,state):
        row={'target':0x185b2,'incoming':live.prior.scheduler.cpu_dict(state),
             'args':[get(self.device.ram(),state.registers[15]+4+i*4)for i in range(2)]}
        self.display_list_CPU_calls.append(row);return row
    def enable_GPU_render_submissions(self):
        """Actual CPU wrappers and inherited GPU context within each render frame.

        Each geometry entry still starts from the declared isolated GPU reset
        fixture. This does not reconstruct global boot/movement GPU context.
        """
        self.real_GPU_render_submissions=True;self.GPU_render_bodies={}
        for target,name in [(0xe19e,'projection'),(0xe202,'draw')]:
            fn=getattr(self.lib,'biwn_gpu_'+name+'_submit_cpu_body')
            fn.argtypes=[c.POINTER(live.world.Bus),c.POINTER(CPU),live.actor.W8,world_cpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];fn.restype=c.c_int
            self.GPU_render_bodies[target]=fn
        lib=self.device.lib
        lib.lab_scene_render_GPU_RAM.argtypes=[c.c_void_p,c.c_uint];lib.lab_scene_render_GPU_RAM.restype=c.c_int
        fixture=(ROOT/'render-assets/biwn-geometry-GPU-RAM-fixture.bin').read_bytes()
        assert len(fixture)==4096 and hashlib.sha256(fixture).hexdigest()=='a9cad7b6078216dd31fb681b741cec9fb53a87d0e32c96cea765bc4aa0c81c6f'
        assert lib.lab_scene_render_GPU_RAM(c.create_string_buffer(fixture),len(fixture))==0
        lib.lab_scene_render_submit.argtypes=[c.c_void_p,c.c_uint32,c.c_uint32];lib.lab_scene_render_submit.restype=c.c_int
        lib.lab_scene_render_stat.argtypes=[c.c_uint];lib.lab_scene_render_stat.restype=c.c_uint64
        lib.lab_scene_render_PC_hash.restype=c.c_uint64;lib.lab_scene_render_error.restype=c.c_uint32
        self.core.GPUStateSave.argtypes=[c.c_void_p];self.core.GPUStateSave.restype=c.c_size_t
        old_write=self.device.write;old_seed=self.device.seed;old_stats=self.device.stats
        def write(address,value):
            if address&0xffffff!=0xf03204 or value not in [0x4d80,0x52e0,0x57a0]:return old_write(address,value)
            address=self.device.physical(address,4,True)
            status=lib.lab_scene_render_submit(None,address,value)
            assert status==0,{'command':hex(value),'status':status,'error':lib.lab_scene_render_error()}
            raw=c.create_string_buffer(8192);size=self.core.GPUStateSave(raw);assert 4396<size<=8192
            self.GPU_submission_events.append({'command':value,'RAM_sha256':hashlib.sha256(self.device.ram()).hexdigest(),
                'GPU_architecture_and_RAM_sha256':hashlib.sha256(raw.raw[:4396]).hexdigest(),
                'direct_PC_count':lib.lab_scene_render_stat(9),'direct_PC_hash':hex(lib.lab_scene_render_PC_hash())})
        def seed(ram,mode):
            old_seed(ram,mode);lib.lab_scene_render_reset();self.GPU_submission_events=[]
        def stats():
            row=old_stats();row['scene_render']={name:lib.lab_scene_render_stat(i)for i,name in enumerate([
                'submissions','geometry_commands','projection_commands','draw_commands','native_GPU_steps','C_dispatcher_calls',
                'C_projection_calls','C_geometry_calls','forbidden_GPU_attempts','last_direct_PC_count','C_resident_calls','C_resident_blits'])}
            return row
        self.device.write=write;self.device.seed=seed;self.device.stats=stats
    def render_script_targets(self):
        targets=[0x181f8,0xe0a6,0xe0f2,0xe148,0xe19e,0xe202,0x170a0,0x185b2]if getattr(self,'real_scene_draw',False)else[0x17e0e,0x181f8]
        if getattr(self,'real_geometry_records',False):targets=[a for a in targets if a!=0x170a0]
        if getattr(self,'real_GPU_geometry',False):targets=[a for a in targets if a!=0xe0a6]
        if getattr(self,'real_GPU_render_submissions',False):targets=[a for a in targets if a not in [0xe19e,0xe202]]
        if getattr(self,'real_display_list_CPU',False):targets=[a for a in targets if a!=0x185b2]
        if getattr(self,'real_overlay_text_CPU',False):targets=[a for a in targets if a!=0x181f8]
        return targets
    def geometry_record_begin(self,state,target):
        args=[get(self.device.ram(),state.registers[15]+4+4*i)for i in range({0x170a0:0,0xe3e0:3,0xe220:5}[target])]
        row={'target':target,'args':args,'incoming':live.prior.scheduler.cpu_dict(state)}
        if target==0x170a0:row['record_count_before']=get(self.device.ram(),0x49b88)
        self.geometry_record_calls.append(row);return row
    def geometry_record_end(self,row,state):
        row['return']=live.prior.scheduler.cpu_dict(state)
        if row['target']==0x170a0:row['record_count']=get(self.device.ram(),0x49b88)
    def scene_draw_begin(self,state,target):
        row={'target':target,'incoming':live.prior.scheduler.cpu_dict(state)};self.scene_draw_calls.append(row);return row
    def scene_draw_end(self,row,state):
        row['return']=live.prior.scheduler.cpu_dict(state)
    def render_begin(self,state,target):
        row={'target':target,'incoming':live.prior.scheduler.cpu_dict(state)}
        if target==0xea28:row['queue_count_before']=get(self.device.ram(),0x112940,2)
        if target==0xe2b8:row['args']=[get(self.device.ram(),state.registers[15]+4+4*j)for j in range(3)]
        self.render_queue_calls.append(row);return row
    def render_end(self,row,state):
        row['return']=live.prior.scheduler.cpu_dict(state)
        if row['target']==0xea28:row['queue_count_after']=get(self.device.ram(),0x112940,2)
        if row['target']==0xe2b8:
            model,index,destination=row['args'];ram=self.device.ram();frame=model+get(ram,model+12+index*4);width,height=ram[frame:frame+2];assert width and height
            raw=ram[destination:destination+width*height*2];header=ram[destination-16:destination]
            row['output']={'dimensions':[width,height],'data_destination':hex(destination),'raw_bytes':len(raw),'raw_sha256':hashlib.sha256(raw).hexdigest(),'header_sha256':hashlib.sha256(header).hexdigest()}
            self.render_last_sprite={'raw':raw,'width':width,'height':height,'metadata':row['output']}
    def render_fixture(self,state,target):
        assert target in self.render_script_targets()
        row={'target':target,'incoming':live.prior.scheduler.cpu_dict(state)};seed=(target+(len(self.render_helper_calls)+1)*1234567)&0xffffffff
        for reg in [0,1,8,9]:state.registers[reg]=(seed*(reg+1)+0xaabbccdd)&0xffffffff
        state.sr=(state.sr&0xffe0)|(seed&31);row['return']=live.prior.scheduler.cpu_dict(state);self.render_helper_calls.append(row)
    def loading_yield(self,state):
        if not getattr(self,'loading_yields_real',False):return
        ret=get(self.device.ram(),state.registers[15])
        if ret==0x1b0da:
            assert self.disc.pending
            self.loading_yield_calls.append({'context':self.current(),'CPU':live.prior.scheduler.cpu_dict(state),'return_PC':ret,'transfer_request':len(self.disc.requests)})
    def handoff(self,state,handoffs):
        handoffs.append(self.event(state))
        if getattr(self,'loading_yields_real',False)and self.disc.pending:
            assert self.current()!=self.world_context,'Complete only after actual loading context switch'
            self.loading_completion_events.append({'handoff':len(handoffs),'context':self.current(),'CPU':live.prior.scheduler.cpu_dict(state),'transfer_request':len(self.disc.requests)})
            # An explicit external device event after a scheduler handoff;
            # file bytes/progress are supplied, never a fake DF60 return.
            self.disc.tick(lambda a,data:c.memmove(self.device.pointer+a,data,len(data)),lambda a,v:self.device.direct(a,4,v))
    def cd_begin(self,state,target):
        row={'target':target,'incoming':live.prior.scheduler.cpu_dict(state)};self.cd_body_calls.append(row);return row
    def cd_end(self,row,state):
        row['return']=live.prior.scheduler.cpu_dict(state)
    def bios_cd_adapter(self,state,target):
        assert target in [0x303c,0x3042]
        args=[state.registers[8],state.registers[9],state.registers[0]]if target==0x303c else[]
        row={'target':target,'args':args,'incoming':live.prior.scheduler.cpu_dict(state)}
        if target==0x303c:
            if getattr(self,'loading_yields_real',False):assert args[1]<=state.ssp-4096,'Declared transfer must not overlap supplied supervisor stack reserve'
            self.disc.start(*args)
        else:self.disc.stop()
        seed=(target+(len(self.io_calls)+1)*1234567)&0xffffffff
        # Loader keeps its stream cursor in A2 across the tail stop wrapper.
        # Preserve A2 at that explicit BIOS boundary; start deliberately
        # clobbers it to check D2F0's actual save/restore instructions.
        for reg in [0,1,8,9]+([10]if target==0x303c else[]):state.registers[reg]=(seed*(reg+1)+0xaabbccdd)&0xffffffff
        state.sr=(state.sr&0xffe0)|(seed&31);row['return']=live.prior.scheduler.cpu_dict(state);self.io_calls.append(row)
    def resource_begin(self,state,target):
        widths={0x1b002:[2],0x1af04:[2],0x1b044:[4]*5,0x1545c:[4],0x152a2:[4],0x15200:[],0xe3e0:[4]*3,0xe3ee:[4]*3}[target];offset=4;args=[]
        for width in widths:args.append(get(self.device.ram(),state.registers[15]+offset,width));offset+=width
        row={'target':target,'args':args,'incoming':live.prior.scheduler.cpu_dict(state)};self.resource_body_calls.append(row);return row
    def resource_end(self,row,state):
        row['return']=live.prior.scheduler.cpu_dict(state)
        if row['target']==0x1b044:
            _,tag,handle,size,_=row['args'];ram=self.device.ram();pointer=get(ram,handle);payload=ram[pointer:pointer+size];request=self.disc.requests[-1];stream=self.disc.data[request['normalized_track_offset']:request['normalized_track_offset']+request['bytes']];start=stream.find(tag.to_bytes(4,'big')*16)
            expected=stream[start+64:start+64+size]
            assert start>=0 and start%4==0 and payload==expected,{'target':hex(row['target']),'args':row['args'],'pointer':hex(pointer),'tag_offset':start,'first_difference':next((i for i,(a,b)in enumerate(zip(payload,expected))if a!=b),None),'payload_sha256':hashlib.sha256(payload).hexdigest(),'expected_sha256':hashlib.sha256(expected).hexdigest(),'requests':self.disc.requests,'completions':self.disc.completions,'loading_yields':self.loading_yield_calls,'loading_events':self.loading_completion_events}
            row['payload']={'tag':hex(tag),'handle':hex(handle),'data_pointer':hex(pointer),'bytes':size,'sha256':hashlib.sha256(payload).hexdigest(),'matches_preserved_normalized_disc_payload':True}
    def io_adapter(self,state,target):
        widths={0xd206:[4,4],0xd2f0:[4]*3,0xd306:[],0xdf60:[]}[target];offset=4;args=[]
        for width in widths:args.append(get(self.device.ram(),state.registers[15]+offset,width));offset+=width
        row={'target':target,'args':args,'incoming':live.prior.scheduler.cpu_dict(state)};value=0
        if target==0xd206:
            toc=c.create_string_buffer(c.string_at(self.device.pointer+0x2c00,256));position=Position();status=self.cd_math(*args,toc,256,c.byref(position));assert status==0,status;value=position.packed
        elif target==0xd2f0:self.disc.start(*args);value=args[2]
        elif target==0xd306:self.disc.stop()
        else:
            assert self.disc.pending,'Loading completion adapter requires a pending disc transfer'
            self.disc.tick(lambda a,data:c.memmove(self.device.pointer+a,data,len(data)),lambda a,v:self.device.direct(a,4,v))
        if target!=0xdf60:
            state.registers[0]=value;seed=(target+(len(self.io_calls)+1)*1234567)&0xffffffff
            for reg in [1,8,9]:state.registers[reg]=(seed*reg+0xaabbccdd)&0xffffffff
            state.sr=(state.sr&0xffe0)|(seed&31)
        row['return']=live.prior.scheduler.cpu_dict(state);self.io_calls.append(row)
    def world_reset(self,ram):
        self.pad=pad.Backend(self.core,self.device);self.pad.set_buttons([]);self.world_clock_base=get(ram,0x46252);self.world_poll_count=0;self.world_calls=[];self.world_returns=[];self.world_times=[];self.world_script_count=0;self.animation_requests=[];self.animation_running=False;self.dispatch_running=False;self.dispatcher_calls=[];self.resource_calls=[];self.resource_body_calls=[];self.resource_frames=[];self.captured_model_handle=get(ram,0x49ca4);self.captured_output_handle=get(ram,0x49caa)
        self.io_calls=[]
        self.cd_body_calls=[];self.cd_frames=[]
        self.loading_yield_calls=[];self.loading_completion_events=[]
        self.render_queue_calls=[];self.render_queue_frames=[];self.render_helper_calls=[];self.render_last_sprite=None
        self.scene_draw_calls=[];self.scene_draw_frames=[]
        self.geometry_record_calls=[];self.geometry_record_frames=[]
        self.GPU_geometry_CPU_calls=[];self.GPU_geometry_CPU_frames=[]
        self.GPU_render_CPU_calls=[];self.GPU_render_CPU_frames=[]
        self.display_list_CPU_calls=[];self.display_list_CPU_frames=[]
        self.overlay_text_CPU_calls=[];self.overlay_text_CPU_frames=[]
        if getattr(self,'real_resource_disc',False):self.disc.reset()
    def world_poll(self):
        self.world_poll_count+=1;sequence=getattr(self,'world_button_sequence',[[]]);self.pad.set_buttons(sequence[min(self.world_poll_count-1,len(sequence)-1)]);self.device.direct(0x778cc,4,(self.world_clock_base+self.clock_step*self.world_poll_count)&0xffffffff)
    def resource_fixture(self,state,target):
        assert target in [0x1b002,0x1af04,0x1545c,0x152a2]
        width=2 if target in [0x1b002,0x1af04]else 4;args=[get(self.device.ram(),state.registers[15]+4,width)];incoming=live.prior.scheduler.cpu_dict(state)
        state.registers[0]=self.captured_model_handle if target==0x1af04 else self.captured_output_handle if target==0x152a2 else 0
        seed=(target+(len(self.resource_calls)+1)*1234567)&0xffffffff
        for reg in [1,8,9]:state.registers[reg]=(seed*reg+0xaabbccdd)&0xffffffff
        state.sr=(state.sr&0xffe0)|(seed&31);self.resource_calls.append({'target':target,'args':args,'incoming':incoming,'return':live.prior.scheduler.cpu_dict(state)})
    def world_script(self,state,target):
        assert target in [0x191f4,0x1b786,0x19f2c,0x19fda,0xf0fa,0xeb04,0x20820]
        self.world_script_count+=1;seed=(target+self.world_script_count*1234567)&0xffffffff
        state.registers[0]=1 if target in [0x19f2c,0x19fda,0xf0fa]else 0
        for reg in [1,8,9]:state.registers[reg]=(seed*reg+0xaabbccdd)&0xffffffff
        state.sr=(state.sr&0xffe0)|(seed&31)
    def world_info(self):
        info={'world_calls':self.world_calls,'world_returns':self.world_returns,'world_time_steps':self.world_times,'world_poll_count':self.world_poll_count}
        if getattr(self,'real_animation',False):info['animation_requests']=self.animation_requests
        if getattr(self,'real_dispatch',False):info['dispatcher_helper_calls']=self.dispatcher_calls
        if getattr(self,'resource_fixture_enabled',False):info['resource_fixture_calls']=self.resource_calls
        if getattr(self,'real_resource_memory',False):info['resource_body_calls']=self.resource_body_calls
        if getattr(self,'real_resource_disc',False):info.update(resource_IO_adapter_calls=self.io_calls,disc_requests=list(self.disc.requests),disc_completions=list(self.disc.completions),disc_stops=self.disc.stops)
        if getattr(self,'real_cd_cpu',False):info['cd_body_calls']=self.cd_body_calls
        if getattr(self,'loading_yields_real',False):info.update(loading_yield_calls=self.loading_yield_calls,loading_completion_events=self.loading_completion_events)
        if getattr(self,'real_render_queue',False):info.update(render_queue_calls=self.render_queue_calls,render_helper_calls=self.render_helper_calls)
        if getattr(self,'real_scene_draw',False):info.update(scene_draw_calls=self.scene_draw_calls)
        if getattr(self,'real_geometry_records',False):info.update(geometry_record_calls=self.geometry_record_calls)
        if getattr(self,'real_GPU_geometry',False):info.update(GPU_geometry_CPU_calls=self.GPU_geometry_CPU_calls,CPU_bus_alias_examples=self.device.address_aliases[:32])
        if getattr(self,'real_GPU_render_submissions',False):info.update(GPU_render_CPU_calls=self.GPU_render_CPU_calls,GPU_submission_events=self.GPU_submission_events)
        if getattr(self,'real_display_list_CPU',False):info['display_list_CPU_calls']=self.display_list_CPU_calls
        if getattr(self,'real_overlay_text_CPU',False):info['overlay_text_CPU_calls']=self.overlay_text_CPU_calls
        return info
    def native(self,ram,initial,iterations):
        self.device.seed(ram,0);lifecycle.seed_cpu(self,initial)
        world_mode=getattr(self,'world_mode',False)
        if world_mode:self.world_reset(ram)
        plan=Plan(self);steps=[];handoffs=[];yields=[];returns=[];target=None;render_pending=None
        ranges=[(0x17dc2,0x17dce),(0xf4d8,0xf712),(0xdfa6,0xdfb2),(0xdf60,0xdf6c),
                (0xde08,0xde5c),(0xf360,0xf368),(0xf880,0xf888),(0x13c9a,0x13f12)]
        ranges+=live.navigation.RANGES+live.rng_cpu.RANGES+live.motion.direction.RANGES+live.motion.submit_cpu.RANGES+live.motion.collision.RANGES
        if world_mode:ranges+=[(0x1a188,0x1a552),(0x1b718,0x1b780),(0xe4c0,0xe53c)]
        if getattr(self,'real_animation',False):ranges+=[(0xeac4,0xec04)]
        if getattr(self,'real_camera',False):ranges+=[(0xf0fa,0xf35e)]
        if getattr(self,'real_targeting',False):ranges+=[(0x20820,0x20a9c)]
        if getattr(self,'real_dispatch',False):ranges+=[(0x191f4,0x192a2),(0x192bc,0x19f2c)]
        if getattr(self,'real_resource_memory',False):ranges+=[(0x15200,0x1557a),(0x1b002,0x1b044),(0xe3e0,0xe4aa)]
        if getattr(self,'real_resource_disc',False):ranges+=[(0x1af04,0x1b154)]
        if getattr(self,'real_cd_cpu',False):ranges+=[(0xd1e0,0xd2a0),(0xd2f0,0xd30a)]
        if getattr(self,'real_render_queue',False):ranges+=[(0x17dc2,0x17e0e),(0xea20,0xeac4),(0xe2b8,0xe2f4),(0xe098,0xe0a6)]
        if getattr(self,'real_scene_draw',False):ranges+=[(0xe03a,0xe098),(0x17e0e,0x17f68)]
        if getattr(self,'real_geometry_records',False):ranges+=[(0x170a0,0x17326),(0xe220,0xe26c),(0xe3e0,0xe4aa)]
        if getattr(self,'real_GPU_geometry',False):ranges+=[(0xe0a6,0xe0f2)]
        if getattr(self,'real_GPU_render_submissions',False):ranges+=[(0xe19e,0xe220)]
        if getattr(self,'real_display_list_CPU',False):ranges+=[(0x185b2,0x18690),(0x1869a,0x18854)]
        if getattr(self,'real_overlay_text_CPU',False):ranges+=[(0x181f8,0x18554),(0x14776,0x14800),(0x14842,0x14caa),(0xe540,0xe588),(0xe61c,0xe68c),(0x1b160,0x1b1a0),(0x1b1a8,0x1b200),(0x1b212,0x1b478)]
        for _ in range(3000000 if getattr(self,'real_overlay_text_CPU',False)else 1000000):
            pc=self.core.m68k_get_reg(None,16)
            if getattr(self,'real_render_queue',False)and self.current()==startup.RENDER:
                if pc in self.render_script_targets():
                    state=self.cpu();opcode=get(self.device.ram(),pc,2);self.render_fixture(state,pc)
                    for reg in [0,1,8,9]:self.core.m68k_set_reg(reg,state.registers[reg])
                    self.core.m68k_set_reg(17,state.sr);self.device.direct(pc,2,0x4e75);steps.append(pc);self.core.m68k_execute(1);self.device.direct(pc,2,opcode);continue
                if render_pending==pc:self.render_queue_frames.append(self.render_begin(self.cpu(),pc));render_pending=None
                if pc in [0xeac2,0xe2f2,0xe0a4]:self.render_end(self.render_queue_frames.pop(),self.cpu())
                render_jsrs={0x17dce:0xea28,0xeaa4:0xe2b8,0xe2b8:0xe098,0xe2ec:0xe098}
                if getattr(self,'real_scene_draw',False):
                    if pc in [0x17e0e,0xe03a,0x17f14]:self.scene_draw_frames.append(self.scene_draw_begin(self.cpu(),pc))
                    if pc in [0x17f12,0xe096,0x17f66]:self.scene_draw_end(self.scene_draw_frames.pop(),self.cpu())
                    render_jsrs.update({0x17e64:0xe098,0x17ede:0xe098})
                if getattr(self,'real_geometry_records',False):
                    if pc in [0x170a0,0xe3e0,0xe220]:self.geometry_record_frames.append(self.geometry_record_begin(self.cpu(),pc))
                    if pc in [0x17324,0xe4a8,0xe26a]:self.geometry_record_end(self.geometry_record_frames.pop(),self.cpu())
                    render_jsrs.update({0xe220:0xe098,0xe264:0xe098})
                if getattr(self,'real_GPU_geometry',False):
                    if pc==0xe0a6:
                        row={'target':pc,'incoming':live.prior.scheduler.cpu_dict(self.cpu())};self.GPU_geometry_CPU_calls.append(row);self.GPU_geometry_CPU_frames.append(row)
                    if pc==0xe0f0:
                        row=self.GPU_geometry_CPU_frames.pop();row['return']=live.prior.scheduler.cpu_dict(self.cpu());row['record_count_after_GPU']=get(self.device.ram(),0x49b88)
                    render_jsrs.update({0xe0a6:0xe098,0xe0ea:0xe098})
                if getattr(self,'real_GPU_render_submissions',False):
                    if pc in [0xe19e,0xe202]:
                        row={'target':pc,'incoming':live.prior.scheduler.cpu_dict(self.cpu())};self.GPU_render_CPU_calls.append(row);self.GPU_render_CPU_frames.append(row)
                    if pc in [0xe200,0xe21e]:self.GPU_render_CPU_frames.pop()['return']=live.prior.scheduler.cpu_dict(self.cpu())
                    render_jsrs.update({0xe19e:0xe098,0xe1fa:0xe098,0xe202:0xe098})
                if getattr(self,'real_display_list_CPU',False):
                    if pc==0x185b2:self.display_list_CPU_frames.append(self.display_list_begin(self.cpu()))
                    if pc==0x18852:self.display_list_CPU_frames.pop()['return']=live.prior.scheduler.cpu_dict(self.cpu())
                if getattr(self,'real_overlay_text_CPU',False):
                    if pc in self.overlay_text_entries|self.formatter_entries:self.overlay_text_CPU_frames.append(self.overlay_text_begin(self.cpu(),pc))
                    if pc in self.overlay_text_returns:self.overlay_text_CPU_frames.pop()['return']=live.prior.scheduler.cpu_dict(self.cpu())
                if pc in render_jsrs:render_pending=render_jsrs[pc]
            if world_mode and self.current()==self.world_context:
                if getattr(self,'real_dispatch',False):
                    if pc==0x191f4:self.dispatch_running=True
                    if self.dispatch_running and pc in dispatch_logic.HELPERS:self.dispatcher_calls.append({'target':pc,'CPU':live.prior.scheduler.cpu_dict(self.cpu())})
                    if pc==0x19f2a:self.dispatch_running=False;self.world_returns.append({'target':0x191f4,'CPU':live.prior.scheduler.cpu_dict(self.cpu())})
                    if getattr(self,'real_resource_memory',False):
                        entries=[0x1b002,0x1545c,0x152a2,0x15200,0xe3e0,0xe3ee]+([0x1af04,0x1b044]if getattr(self,'real_resource_disc',False)else[])
                        resource_ret_pcs=[0x1b042,0x15578,0x1545a,0x152a0,0xe4a8]+([0x1b000,0x1b152]if getattr(self,'real_resource_disc',False)else[])
                        if pc in entries:self.resource_frames.append(self.resource_begin(self.cpu(),pc))
                        if pc in resource_ret_pcs:self.resource_end(self.resource_frames.pop(),self.cpu())
                    if getattr(self,'real_cd_cpu',False):
                        if pc in [0xd1e0,0xd206,0xd2f0,0xd306]:self.cd_frames.append(self.cd_begin(self.cpu(),pc))
                        if pc in [0xd1ea,0xd204,0xd29e,0xd304]:self.cd_end(self.cd_frames.pop(),self.cpu())
                    cd_adapter_targets=[0x303c,0x3042]if getattr(self,'real_cd_cpu',False)else[0xd206,0xd2f0,0xd306]
                    if getattr(self,'real_resource_disc',False)and(pc in cd_adapter_targets or(pc==0xdf60 and self.disc.pending and not getattr(self,'loading_yields_real',False))):
                        state=self.cpu();opcode=get(self.device.ram(),pc,2)
                        if pc in [0x303c,0x3042]and getattr(self,'real_cd_cpu',False):self.bios_cd_adapter(state,pc)
                        else:self.io_adapter(state,pc)
                        if pc==0x3042 and getattr(self,'real_cd_cpu',False):self.cd_end(self.cd_frames.pop(),state)
                        for reg in [0,1,8,9,10]if getattr(self,'real_cd_cpu',False)else[0,1,8,9]:self.core.m68k_set_reg(reg,state.registers[reg])
                        self.core.m68k_set_reg(17,state.sr);self.device.direct(pc,2,0x4e75);steps.append(pc);self.core.m68k_execute(1);self.device.direct(pc,2,opcode);continue
                    if getattr(self,'resource_fixture_enabled',False)and pc in [0x1b002,0x1af04,0x1545c,0x152a2]and not(getattr(self,'real_resource_memory',False)and(pc!=0x1af04 or getattr(self,'real_resource_disc',False))):
                        state=self.cpu();opcode=get(self.device.ram(),pc,2);self.resource_fixture(state,pc)
                        for reg in [0,1,8,9]:self.core.m68k_set_reg(reg,state.registers[reg])
                        self.core.m68k_set_reg(17,state.sr);self.device.direct(pc,2,0x4e75);steps.append(pc);self.core.m68k_execute(1);self.device.direct(pc,2,opcode);continue
                if pc in world_cpu.TARGETS:
                    state=self.cpu();self.world_calls.append({'target':pc,'CPU':live.prior.scheduler.cpu_dict(state)})
                    if pc==0xe4c0:self.world_poll()
                    elif pc!=0xe220 and not(pc==0xeb04 and getattr(self,'real_animation',False))and not(pc==0xf0fa and getattr(self,'real_camera',False))and not(pc==0x20820 and getattr(self,'real_targeting',False))and not(pc==0x191f4 and getattr(self,'real_dispatch',False)):
                        opcode=get(self.device.ram(),pc,2);self.world_script(state,pc)
                        for reg in [0,1,8,9]:self.core.m68k_set_reg(reg,state.registers[reg])
                        self.core.m68k_set_reg(17,state.sr);self.world_returns.append({'target':pc,'CPU':live.prior.scheduler.cpu_dict(self.cpu())})
                        self.device.direct(pc,2,0x4e75);steps.append(pc);self.core.m68k_execute(1);self.device.direct(pc,2,opcode);continue
                if pc in [0xe53a,0xe26a]:self.world_returns.append({'target':0xe4c0 if pc==0xe53a else 0xe220,'CPU':live.prior.scheduler.cpu_dict(self.cpu())})
                if pc==0xf35c and getattr(self,'real_camera',False):self.world_returns.append({'target':0xf0fa,'CPU':live.prior.scheduler.cpu_dict(self.cpu())})
                if pc==0x20a9a and getattr(self,'real_targeting',False):self.world_returns.append({'target':0x20820,'CPU':live.prior.scheduler.cpu_dict(self.cpu())})
                if getattr(self,'real_animation',False):
                    if pc==0xec02:self.world_returns.append({'target':0xeb04,'CPU':live.prior.scheduler.cpu_dict(self.cpu())})
                    if pc==0xeac4:
                        sp=self.core.m68k_get_reg(None,15);self.animation_requests.append([get(self.device.ram(),sp+4+j*4)for j in range(4)])
                if pc==0x1a542:self.world_times.append({'CPU':live.prior.scheduler.cpu_dict(self.cpu()),'time_step':get(self.device.ram(),0x4c24c)})
            assert any(a<=pc<b for a,b in ranges),hex(pc)
            steps.append(pc)
            if pc in live.NAV:
                target=pc;stack=self.core.m68k_get_reg(None,15);offset=4;args=[]
                for width in live.actor.WIDTHS[pc]:args.append(get(self.device.ram(),stack+offset,width));offset+=width
                plan.observe(pc,args,self.core.m68k_get_reg(None,0))
            if pc in live.navigation.RETURNS|{0x1a7f2,0x13f10}:
                returns.append({'context':self.current(),'target':target,'CPU':live.prior.scheduler.cpu_dict(self.cpu())});target=None
            if pc==0xdf60:
                sp=self.core.m68k_get_reg(None,15);yields.append({'context':self.current(),'SP':sp,'return_PC':get(self.device.ram(),sp)});self.loading_yield(self.cpu())
            self.core.m68k_execute(1)
            if self.core.GPUReadLong(0xf03204,0)==0x4320:self.device.write(0xf03204,0x4320)
            if getattr(self,'real_render_queue',False)and pc==0xe2d6:self.device.write(0xf03204,0x4b00)
            if getattr(self,'real_GPU_geometry',False)and pc==0xe0d4:self.device.write(0xf03204,0x4d80)
            if getattr(self,'real_GPU_render_submissions',False)and self.core.GPUReadLong(0xf03204,0)in [0x52e0,0x57a0]:self.device.write(0xf03204,self.core.GPUReadLong(0xf03204,0))
            if pc==0xdf6a or(pc==0xde5a and self.core.m68k_get_reg(None,16)!=0xdf66):
                self.handoff(self.cpu(),handoffs)
                if plan.done(iterations):break
        else:raise AssertionError('Native disc-scene actors did not complete iterations')
        info={'calls':plan.calls,'movements':plan.movements,'handoffs':handoffs,'yields':yields,'helper_returns':returns,'steps':steps,'device':self.device.stats()}
        if world_mode:info.update(self.world_info())
        return self.device.ram(),self.cpu(),info
    def translated(self,ram,initial,iterations):
        self.device.seed(ram,1);cpu=CPU.from_buffer_copy(bytes(initial));plan=Plan(self);errors=[];handoffs=[];yields=[];returns=[]
        world_mode=getattr(self,'world_mode',False)
        if world_mode:self.world_reset(ram)
        def motion_service(_,bus,state,target):
            try:
                if target==0x13440:return self.direction(bus,state)
                if target==0xe220:return self.submit(bus,state,1000)
                assert target in [0x13b5a,0x13bb0];return self.collision(bus,state,4096)
            except Exception as error:errors.append(repr(error));return 1
        motion_cb=live.motion.SERVICE(motion_service)
        def service(_,bus,state,target):
            try:
                assert target in live.NAV;stack=state.contents.registers[15];offset=4;args=[]
                for width in live.actor.WIDTHS[target]:args.append(get(self.device.ram(),stack+offset,width));offset+=width
                plan.observe(target,args,state.contents.registers[0])
                if target==0x1a77c:status=self.rng_cpu(bus,state)
                elif target==0x13c9a:status=self.movement(bus,state,motion_cb,None)
                else:status=self.navigation(bus,state)
                assert status==0,status
                returns.append({'context':self.current(),'target':target,'CPU':live.prior.scheduler.cpu_dict(state.contents)})
                return 0
            except Exception as error:errors.append(repr(error));return 1
        callback=live.actor.SERVICE(service)
        def read32(_,address,value):
            if world_mode and address==0xf14000:value[0]=self.pad.sample();return 0
            return self.device.r32(None,address,value)
        def write16(_,address,value):
            if world_mode and address==0xf14000:self.pad.select(value);return 0
            return self.device.w16(None,address,value)
        def write32(_,address,value):
            status=self.device.w32(None,address,value)
            if not status and getattr(self,'real_animation',False)and self.animation_running and value in [0xeb7a,0xebe8]and self.world_context+0x26<=address<self.world_context+0x400:
                self.animation_requests.append([get(self.device.ram(),address+4+j*4)for j in range(4)])
            return status
        r32=live.world.R32(read32);w16=live.world.W16(write16)
        w32=live.world.W32(write32);bus=live.world.Bus(self.device.r8,self.device.r16,r32,w16,w32,live.world.CALL(),None,0)
        def world_service(_,passed,state,target):
            try:
                self.world_calls.append({'target':target,'CPU':live.prior.scheduler.cpu_dict(state.contents)})
                if target==0xe4c0:self.world_poll();status=self.poll_body(passed,state)
                elif target==0xe220:status=self.submit(passed,state,1000)
                elif target==0xeb04 and getattr(self,'real_animation',False):
                    self.animation_running=True
                    try:status=self.animation_body(passed,state,512)
                    finally:self.animation_running=False
                elif target==0xf0fa and getattr(self,'real_camera',False):status=self.camera_body(passed,state,self.device.write8,camera_callback,None)
                elif target==0x20820 and getattr(self,'real_targeting',False):status=self.targeting_body(passed,state,camera_callback,None)
                elif target==0x191f4 and getattr(self,'real_dispatch',False):status=self.dispatch_body(passed,state,self.device.write8,dispatch_callback,None,200000,1)
                else:self.world_script(state.contents,target);status=0
                if target==0x191f4 and status==6:
                    self.dispatcher_calls.append({'target':0xdf60,'CPU':live.prior.scheduler.cpu_dict(state.contents)});return 6
                assert status==0,status;self.world_returns.append({'target':target,'CPU':live.prior.scheduler.cpu_dict(state.contents)});return 0
            except Exception as error:errors.append(repr(error));return 1
        world_callback=world_cpu.SERVICE(world_service)
        def camera_service(_,passed,state,target):
            try:
                if target in [0xe540,0xe588]:return self.rng_cpu(passed,state)
                if target==0x13440:return self.direction(passed,state)
                assert target==0xe220;return world_service(None,passed,state,target)
            except Exception as error:errors.append(repr(error));return 1
        camera_callback=world_cpu.SERVICE(camera_service)
        def dispatch_service(_,passed,state,target):
            try:
                self.dispatcher_calls.append({'target':target,'CPU':live.prior.scheduler.cpu_dict(state.contents)})
                if target==0xe588:return self.rng_cpu(passed,state)
                if target in [0xe4c0,0xeb04]:return world_service(None,passed,state,target)
                if getattr(self,'real_resource_memory',False)and target in [0x1b002,0x1545c,0x152a2]+([0x1af04]if getattr(self,'real_resource_disc',False)else[]):return resource_call(passed,state,target)
                if getattr(self,'resource_fixture_enabled',False)and target in [0x1b002,0x1af04,0x1545c,0x152a2]:self.resource_fixture(state.contents,target);return 0
                raise AssertionError('Unported dispatcher helper '+hex(target))
            except Exception as error:errors.append(repr(error));return 1
        dispatch_callback=world_cpu.SERVICE(dispatch_service)
        def resource_call(passed,state,target):
            row=self.resource_begin(state.contents,target)
            if getattr(self,'loading_yields_real',False):self.resource_frames.append(row)
            status=self.resource_body(passed,state,self.device.write8,resource_callback,None,300000,1 if getattr(self,'loading_yields_real',False)else 0 if getattr(self,'real_resource_disc',False)else 1)
            if not status:
                self.resource_end(row,state.contents)
                if getattr(self,'loading_yields_real',False):assert self.resource_frames.pop()is row
            elif status!=6:row['status']=status;errors.append(repr({'resource_target':hex(target),'status':status,'device_errors':self.device.errors[-3:]}))
            return status
        def resource_service(_,passed,state,target):
            try:
                if target in dispatch_logic.HELPERS:self.dispatcher_calls.append({'target':target,'CPU':live.prior.scheduler.cpu_dict(state.contents)})
                if getattr(self,'real_cd_cpu',False)and target in [0xd206,0xd2f0,0xd306]:return cd_call(passed,state,target)
                if getattr(self,'real_resource_disc',False)and target in [0xd206,0xd2f0,0xd306,0xdf60]:self.io_adapter(state.contents,target);return 0
                assert target in [0x1b002,0x1545c,0x152a2,0x15200,0xe3e0,0xe3ee]+([0x1af04,0x1b044]if getattr(self,'real_resource_disc',False)else[])
                return resource_call(passed,state,target)
            except Exception as error:errors.append(repr(error));return 1
        resource_callback=world_cpu.SERVICE(resource_service)
        def cd_call(passed,state,target):
            row=self.cd_begin(state.contents,target);status=self.cd_body(passed,state,self.device.write8,cd_callback,None,10000,0)
            if not status:self.cd_end(row,state.contents)
            return status
        def cd_service(_,passed,state,target):
            try:
                if target==0xd1e0:return cd_call(passed,state,target)
                self.bios_cd_adapter(state.contents,target);return 0
            except Exception as error:errors.append(repr(error));return 1
        cd_callback=world_cpu.SERVICE(cd_service)
        def render_call(passed,state,target):
            row=self.render_begin(state.contents,target);status=self.render_queue_body(passed,state,self.device.write8,render_callback,None,10000,0)
            if not status:self.render_end(row,state.contents)
            return status
        def render_service(_,passed,state,target):
            try:
                if target in [0xea20,0xea28,0xe2b8,0xe098]:return render_call(passed,state,target)
                if getattr(self,'real_overlay_text_CPU',False)and target in self.overlay_text_entries|self.formatter_entries:
                    row=self.overlay_text_begin(state.contents,target);fn=self.formatter_CPU if target in self.formatter_entries else self.overlay_text_CPU
                    status=fn(passed,state,self.device.write8,render_callback,None,1000000,0)
                    if not status:row['return']=live.prior.scheduler.cpu_dict(state.contents)
                    return status
                if getattr(self,'real_display_list_CPU',False)and target==0x185b2:
                    row=self.display_list_begin(state.contents)
                    status=self.display_list_CPU(passed,state,self.device.write8,render_callback,None,100000,0)
                    if not status:row['return']=live.prior.scheduler.cpu_dict(state.contents)
                    return status
                if getattr(self,'real_GPU_render_submissions',False)and target in self.GPU_render_bodies:
                    row={'target':target,'incoming':live.prior.scheduler.cpu_dict(state.contents)};self.GPU_render_CPU_calls.append(row)
                    status=self.GPU_render_bodies[target](passed,state,self.device.write8,render_callback,None,100000,0)
                    if not status:row['return']=live.prior.scheduler.cpu_dict(state.contents)
                    return status
                if getattr(self,'real_GPU_geometry',False)and target==0xe0a6:
                    row={'target':target,'incoming':live.prior.scheduler.cpu_dict(state.contents)};self.GPU_geometry_CPU_calls.append(row)
                    status=self.GPU_geometry_submit(passed,state,self.device.write8,render_callback,None,10000,0)
                    if not status:row.update(**{'return':live.prior.scheduler.cpu_dict(state.contents)},record_count_after_GPU=get(self.device.ram(),0x49b88))
                    return status
                if getattr(self,'real_geometry_records',False)and target in [0x170a0,0xe3e0,0xe220]:
                    row=self.geometry_record_begin(state.contents,target);fn=self.resource_body if target==0xe3e0 else self.geometry_records_body
                    status=fn(passed,state,self.device.write8,render_callback,None,100000,0)
                    if not status:self.geometry_record_end(row,state.contents)
                    return status
                if getattr(self,'real_scene_draw',False)and target in [0x17e0e,0xe03a,0x17f14]:
                    row=self.scene_draw_begin(state.contents,target);status=self.scene_draw_body(passed,state,self.device.write8,render_callback,None,100000,0)
                    if not status:self.scene_draw_end(row,state.contents)
                    return status
                self.render_fixture(state.contents,target);return 0
            except Exception as error:errors.append(repr(error));return 1
        render_callback=world_cpu.SERVICE(render_service)
        def world_body(_,passed,state):
            try:
                status=self.world_body(passed,state,world_callback,None,64)
                if status==6:
                    assert state.contents.pc==0xdf60
                    yields.append({'context':self.world_context,'SP':state.contents.registers[15],'return_PC':get(self.device.ram(),state.contents.registers[15])});self.loading_yield(state.contents);return 6
                assert status==0,errors
                self.world_times.append({'CPU':live.prior.scheduler.cpu_dict(state.contents),'time_step':get(self.device.ram(),0x4c24c)});return 0
            except Exception as error:errors.append(repr(error));return 1
        world_body_callback=live.prior.BODY(world_body)
        for _ in range(100000):
            current=self.current()
            if current==startup.RENDER:
                if getattr(self,'real_render_queue',False):
                    status=self.render_queue_body(c.byref(bus),c.byref(cpu),self.device.write8,render_callback,None,10000,1)
                    assert status==6 and cpu.pc==0xdf60,(status,errors,hex(cpu.pc))
                else:
                    assert cpu.pc==0x17dc2
                    cpu.registers[2]=self.device.read(0x778cc,4);cpu.sr=(cpu.sr&0xfff0)|(0 if cpu.registers[2] else 4)|(8 if cpu.registers[2]&0x80000000 else 0)
                    cpu.registers[15]-=4;cpu.usp=cpu.registers[15];self.device.direct(cpu.registers[15],4,0x17dce);cpu.pc=0xdf60
                yields.append({'context':current,'SP':cpu.registers[15],'return_PC':0x17dce})
                assert self.yield_fn(c.byref(bus),c.byref(cpu),64)==0
                self.handoff(cpu,handoffs)
            elif current in ACTORS:
                status=self.actor(c.byref(bus),c.byref(cpu),self.device.write8,callback,None,128)
                assert status==0,(status,errors,hex(cpu.pc),self.device.errors[-5:],self.device.stats(),len(self.GPU_geometry_CPU_calls),hex(self.device.read(0xf03200,4)),hex(self.device.read(0xf03204,4)));assert cpu.pc==0xdf60
                yields.append({'context':current,'SP':cpu.registers[15],'return_PC':get(self.device.ram(),cpu.registers[15])})
                assert self.yield_fn(c.byref(bus),c.byref(cpu),64)==0
                self.handoff(cpu,handoffs)
            elif world_mode and current==self.world_context:
                if getattr(self,'loading_yields_real',False)and self.resource_frames:
                    assert any(a<=cpu.pc<b for a,b in [(0x1af04,0x1b154),(0x15200,0x1557a),(0xe3e0,0xe4aa)]),hex(cpu.pc)
                    status=self.resource_body(c.byref(bus),c.byref(cpu),self.device.write8,resource_callback,None,300000,1)
                    if status==6:
                        yields.append({'context':current,'SP':cpu.registers[15],'return_PC':get(self.device.ram(),cpu.registers[15])});self.loading_yield(cpu)
                        assert self.yield_fn(c.byref(bus),c.byref(cpu),64)==0;self.handoff(cpu,handoffs);continue
                    assert status==0,(status,errors,hex(cpu.pc));self.resource_end(self.resource_frames.pop(),cpu)
                    cpu.pc=get(self.device.ram(),cpu.registers[15]);cpu.registers[15]+=4;cpu.usp=cpu.registers[15];continue
                if 0x191f4<=cpu.pc<0x19f2c:
                    status=self.dispatch_body(c.byref(bus),c.byref(cpu),self.device.write8,dispatch_callback,None,200000,1)
                    if status==6:
                        self.dispatcher_calls.append({'target':0xdf60,'CPU':live.prior.scheduler.cpu_dict(cpu)})
                        yields.append({'context':current,'SP':cpu.registers[15],'return_PC':get(self.device.ram(),cpu.registers[15])});self.loading_yield(cpu)
                        assert self.yield_fn(c.byref(bus),c.byref(cpu),64)==0;self.handoff(cpu,handoffs);continue
                    assert status==0 and cpu.pc==0x19f2a,(status,errors,hex(cpu.pc))
                    self.world_returns.append({'target':0x191f4,'CPU':live.prior.scheduler.cpu_dict(cpu)})
                    cpu.pc=get(self.device.ram(),cpu.registers[15]);cpu.registers[15]+=4;cpu.usp=cpu.registers[15];assert cpu.pc==0x1a26c
                yielding=cpu.pc==0x1a54a
                if yielding:yields.append({'context':current,'SP':cpu.registers[15]-4,'return_PC':0x1a550})
                assert self.idle(c.byref(bus),c.byref(cpu),world_body_callback,None,64)==0,errors
                if yielding or self.current()!=current:self.handoff(cpu,handoffs)
            else:
                assert current in IDLES
                yielding=cpu.pc in [0xf360,0xf880]
                if yielding:yields.append({'context':current,'SP':cpu.registers[15]-4,'return_PC':cpu.pc+6})
                assert self.idle(c.byref(bus),c.byref(cpu),live.prior.BODY(),None,64)==0
                if yielding:self.handoff(cpu,handoffs)
            if plan.done(iterations):break
        else:raise AssertionError('C disc-scene actors did not complete iterations')
        assert not errors
        info={'calls':plan.calls,'movements':plan.movements,'handoffs':handoffs,'yields':yields,'helper_returns':returns,'device':self.device.stats()}
        if world_mode:info.update(self.world_info())
        return self.device.ram(),cpu,info

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--capture',required=True,type=Path);parser.add_argument('--limit',type=int);parser.add_argument('--iterations',type=int,default=32);parser.add_argument('--time-step',type=int,action='append')
    options=parser.parse_args();capture=options.capture.resolve();meta=read(capture/'status.json')
    assert meta['status'] in ['terminal_preflight','terminal_pass']
    files=sorted(capture.glob('startup-C-*.bin'));assert files
    vectors=[(path,step)for path in files for step in (options.time_step or [0,1,8,30])][:options.limit or None]
    out=ROOT/'verification/biwn-disc-scene-actors'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    proof=read(ROOT/'verification/biwn-actor-lifecycle-runtime-checks.json');source=ROOT/'projects/black-ice-white-noise/restoration'
    for name,digest in proof['source_sha256'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==digest
    runtime=Runtime(Path(proof['directory'])/'libactor-lifecycle.dylib');rows=[]
    try:
        for i,(path,time_step)in enumerate(vectors):
            save(out/'status.json',{'status':'running','case':i});index=path.stem.split('-')[-1];info=read(capture/f'startup-capture-{index}.json');assert info['startup_fullCPU_visibleRAM_match']
            ram=bytearray(path.read_bytes());assert hashlib.sha256(ram).hexdigest()==info['C_RAM_sha256']
            for ctx in startup.CONTEXTS:ram[ctx+26:ctx+30]=(0 if ctx in RUNNABLE else 1).to_bytes(4,'big')
            ram[0x778cc:0x778d0]=bytes(4)
            ram[0x4c24c:0x4c250]=time_step.to_bytes(4,'big')
            initial=CPU();initial.registers[:]=info['CPU']['registers'];initial.pc=info['CPU']['pc'];initial.sr=info['CPU']['sr'];initial.usp=info['CPU']['usp'];initial.ssp=info['CPU']['ssp']
            seed=bytes(ram);left,expected,old=runtime.native(seed,initial,options.iterations);right,actual,new=runtime.translated(seed,initial,options.iterations)
            keys=['calls','movements','handoffs','yields','helper_returns']
            if left!=right or bytes(expected)!=bytes(actual)or any(old[k]!=new[k]for k in keys):
                save(out/'mismatch.json',{'capture':str(path),'CPU_original':live.prior.scheduler.cpu_dict(expected),'CPU_C':live.prior.scheduler.cpu_dict(actual),'RAM_differences':[hex(j)for j,(a,b)in enumerate(zip(left,right))if a!=b][:100],'original':old,'rebuilt':new})
                raise AssertionError(str(out/'mismatch.json'))
            assert len(new['movements'])==options.iterations*2 and len(new['handoffs'])==1+options.iterations*4
            assert not new['device']['original_GPUExec1_calls']and not new['device']['game_frames_executed']
            assert old['device']['original_GPUExec1_calls']>0
            actualactors=[{'slot':j,'initial_record':seed[0x49d6c+j*206:0x49d6c+(j+1)*206].hex(),'final_record':right[0x49d6c+j*206:0x49d6c+(j+1)*206].hex()}for j in range(2)]
            rows.append({'case':i,'time_step_input':time_step,'startup_capture':str(path),'startup_capture_sha256':info['C_RAM_sha256'],'initial_CPU':info['CPU'],'final_CPU':live.prior.scheduler.cpu_dict(actual),
                         'original':old,'rebuilt':new,'actor_records':actualactors,'whole2MBRAM_allCPU_privateframes_match':True})
    except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
    finally:runtime.close()
    save(out/'fixtures.json',rows)
    moved=sum(any(any(bytes.fromhex(r['initial_record'])[o:o+w]!=bytes.fromhex(r['final_record'])[o:o+w]for o,w in[(4,4),(8,2),(10,4)])for r in row['actor_records'])for row in rows)
    collision_counts={hex(target):sum(row['original']['steps'].count(target)for row in rows)for target in [0x13b5a,0x13bb0]}
    if not options.limit:assert moved and collision_counts['0x13b5a']
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'two_actors_in_disc_loaded_C_startup_geometry_match_original_CPU_GPU',
            'directory':str(out),'cases':len(rows),'actor_iterations':len(rows)*options.iterations*2,'task_handoffs':len(rows)*(1+options.iterations*4),
            'created_contexts_preserved':21,'runnable_actor_and_idle_contexts':4,'blocked_contexts':17,'actor_contexts':ACTORS,'idle_contexts':IDLES,
            'startup_C_scene_task_state_linked':True,'uninterrupted_startup_actor_execution':False,'geometry_replaced_by_synthetic_grid':False,
            'actor_helper_scripts':[],'synthetic_GPU_output_words':False,'synchronous_GPU_completion':True,
            'shared_time_step_inputs':sorted({row['time_step_input']for row in rows}),'cases_with_position_change':moved,'original_collision_entry_counts':collision_counts,
            'allCPU_SR_USP_SSP_complete2MBRAM_privateframes_compared':True,'new_components':0,
            'source_sha256':proof['source_sha256'],'startup_capture_directory':str(capture),
            'matched':['Both original/C actor paths run the two actual F4D8 contexts created by C startup, using its actor/room/tile/region/model/texture data loaded from the preserved disc. No synthetic geometry replaces these structures.',
                       'The created21-context ring is retained; only two actors/twoidles are runnable after an initial actual render yield. Full CPU/RAM/private frames, helper arguments/fullCPU returns and task handoffs compare.'],
            'limits':['Phased bridge: startup CPU/visibleRAM compare with its historical private-stack/formatter exclusions; actor phase seeds both paths from the same Cstartup2MBRAM and CPU. Not uninterrupted whole-game boot/world/render execution.',
                      'Seventeen contexts are deliberately blocked, including render/world after the initial render yield. Clock is seeded0; shared movement timestep4C24C is explicitly supplied as0/1/8/30, not generated by a running world task. Zero-step startup baseline is stationary. Startup HUD/menu3helpers,6renderhelpers and CD/loading completion adapters retain prior scope. Actor phase uses synchronousGPUcompletion, not dispatcher concurrency.',
                      'No actor deletion/reuse stimulus in this disc-scene proof; that is separately checked with synthetic scene data. Full3Ddraw/scanout/mainloop/scenes/audio/game/hardware remain unfinished.']}
    save(out/'report.json',report);save(out/'status.json',{'status':'terminal_preflight'if options.limit else'terminal_pass','cases':len(rows)})
    if not options.limit:save(ROOT/'verification/biwn-disc-scene-actors-checks.json',report)
    print(json.dumps(report))

read=lambda p:json.loads(p.read_text())
if __name__=='__main__':main()
