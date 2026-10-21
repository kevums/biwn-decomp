"""Source system/render/health/actor scheduling through resource startup.

Disc completion is delivered after an actual source handoff. No DF60 RTS
completion shortcut or startup CPU/RAM capture; device/timing providers remain.
"""
import argparse,ctypes as c,hashlib,json,os,subprocess,wave
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_startup_retained_GPU as base
from check_biwn_source_entry_boot import EntryBootMixin
from biwn_music_engine_runtime import MusicEngineMixin
from biwn_bios_setup_runtime import BIOSSetupMixin
from biwn_bios_controller_runtime import BIOSControllerMixin
from biwn_bios_mode_runtime import BIOSModeMixin
from biwn_bios_toc_runtime import BIOSTOCMixin
from biwn_asset_transport_runtime import AssetTransportMixin
from biwn_movie_transport_runtime import MovieTransportMixin
ROOT=base.ROOT;media=base.media;save=base.save;sha=base.sha
class Runtime(MovieTransportMixin,AssetTransportMixin,BIOSTOCMixin,BIOSModeMixin,BIOSControllerMixin,BIOSSetupMixin,MusicEngineMixin,EntryBootMixin,base.Runtime):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.scheduling_active=False
        self.timer_enabled=False
        if hasattr(self.lib,'biwn_gpu_timer_run'):
            self.timer_run=self.lib.biwn_gpu_timer_run;self.timer_run.argtypes=self.movie_exit.argtypes+[c.c_uint32];self.timer_run.restype=c.c_int
            self.timer_assert=self.lib.biwn_gpu_timer_assert;self.timer_assert.argtypes=self.control5.argtypes;self.timer_assert.restype=c.c_int
            self.core.GPUSetIRQLine.argtypes=[c.c_int,c.c_int]
        self.startup_pc_coverage=set()
        self.system_addresses={pc for pc in self.new_rows if 0xdd40<=pc<0xddfe}
        self.health_fn=self.lib.biwn_health_timeout_cpu_body;self.health_fn.argtypes=self.fn.argtypes;self.health_fn.restype=c.c_int
        self.resume_fn=self.lib.biwn_scheduler_resume_saved;self.resume_fn.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU)];self.resume_fn.restype=c.c_int
        parent=self.service
        def service(_,bus,cpu,target):
            try:
                if self.scheduling_active:
                    if target==0xdf60:return 6
                    if target in self.new_groups:return self.new_groups[target](bus,cpu,self.callbacks[5],self.service,None,1000000,1)
                    if target in self.render_groups:return self.render_CPU[self.render_groups[target]](bus,cpu,self.callbacks[5],self.service,None,1000000,1)
                return parent(_,bus,cpu,target)
            except Exception as error:self.errors.append(repr(error));return 1
        self.service=media.world_cpu.SERVICE(service)
    def source_system_clock_tick(self):
        if not self.timer_enabled:return super().clock_tick()
        before=self.core.GPUGetPC()if self.mode=='native'else self.gpu.pc
        trace=hashlib.sha256();blocks=0;delays=0
        if self.mode=='native':
            self.core.GPUSetIRQLine(2,1);assert self.core.GPUGetPC()==0xf03020
            code=c.string_at(self.core.GPUGetRAM(),4096)
            for _ in range(100):
                pc=self.core.GPUGetPC()
                if pc==before:break
                trace.update(pc.to_bytes(4,'big'));blocks+=1;opcode=int.from_bytes(code[pc-0xf03000:pc-0xf03000+2],'big');self.core.GPUExec(1)
                if opcode>>10 in [52,53]and self.core.GPUGetPC()!=pc+2:delays+=1
            else:raise AssertionError('Native source timer bound')
            raw=base.joined.video.gpu_state(self.core)[0][:4396];instructions=blocks+delays
        else:
            self.gpu_trace=trace;self.gpu_blocks=0;counter=self.gpu_counter.value;begin=self.gpu.instructions
            assert self.timer_assert(c.byref(self.boot_bus),c.byref(self.gpu))==0
            assert self.timer_run(c.byref(self.boot_bus),c.byref(self.gpu),100,before)==0
            assert self.gpu_counter.value==counter;c.memmove(self.core.GPUGetRAM(),bytes(self.gpu.local_RAM),4096);raw=base.joined.video.logical(self.gpu);blocks=self.gpu_blocks;instructions=self.gpu.instructions-begin
        self.gpu_calls.append(dict(program='source_timer_IRQ2',blocks=blocks,instructions=instructions,PC_sha256=trace.hexdigest(),logical_GPU_sha256=sha(raw)))
    def handoff_event(self,state):
        completed=None
        if self.asset_disc.pending:
            before=len(self.asset_disc.completions);self.pump_asset_transfer(state);completed=self.asset_disc.completions[before:]
        self.handoffs.append(dict(CPU=media.scheduler.cpu_dict(state),context=hex(self.current()),RAM=sha(self.device.ram()),hardware=self.hardware(),disc_completed=completed))
    def virtual_RTS(self,s):
        assert self.rows[s.pc]['assembly']=='rts',hex(s.pc)
        s.pc=self.read(s.registers[15],4);s.registers[15]+=4
        if s.sr&0x2000:s.ssp=s.registers[15]
        else:s.usp=s.registers[15]
    def source_startup(self,ram,case,mode):
        self.scheduling_active=False;self.startup_active=False;self.full_running=False;self.loading_active=False;self.prefix_running=False;self.renderer_active=False;self.pending_render=None;self.pending_movement=False;self.movie_started=False;self.asset_disc.reset();self.pad.set_buttons([])
        entry,entry_checks=self.source_entry(ram,case['id'],mode);assert self.renderer_mode(int(mode=='C'))==0
        self.startup_active=True;self.scheduling_active=True;self.loading_active=True;self.global_clock_step=0;self.pad.set_buttons(case['buttons']);self.handoffs=[];self.clock_ticks=0;start_calls=len(self.gpu_calls)
        initial=media.CPU.from_buffer_copy(bytes(self.entry_CPU))
        GPU_before=self.gpu_counter.value;DSP_before=self.counter.value;begin_hardware=self.hardware()
        if mode=='native':
            assert media.scheduler.cpu_dict(self.cpu())==media.scheduler.cpu_dict(initial);steps=0
            for _ in range(5000000):
                pc=self.core.m68k_get_reg(None,16)
                if pc==0x17dc2 and self.current()==0xc0d28:break
                if pc==0xddd8:self.clock_tick();self.clock_ticks+=1
                if pc in [0x303c,0x3042]:
                    self.native_asset_call(pc)
                else:
                    assert pc in self.rows,hex(pc);self.native_coverage.add(pc);self.startup_pc_coverage.add(pc);self.core.m68k_execute(1)
                    selected=self.core.m68k_get_reg(None,16)
                    if pc in [0xdf6a,0xdf8a]or(pc==0xde5a and selected not in [0xdf66,0xdf86]):self.handoff_event(self.cpu())
                command=self.core.GPUReadLong(0xf03204,6)
                if command==0x4b00:self.run_render_request(command)
                elif command==0x4320:self.run_movement_request()
                steps+=1
            else:raise AssertionError(('Native scheduled startup bound',hex(pc),self.current()))
            result=self.cpu()
        else:
            s=initial
            for _ in range(100000):
                if s.pc==0x17dc2 and self.current()==0xc0d28:break
                self.C_CPU=s;ctx=self.current()
                if s.pc in [0xdf60,0xdf7a]:
                    fn=self.yield_fn if s.pc==0xdf60 else self.remove_fn;status=fn(c.byref(self.bus),c.byref(s),128);assert status==0,(status,hex(s.pc));self.handoff_event(s);continue
                if s.pc==0xdf66:
                    assert self.resume_fn(c.byref(self.bus),c.byref(s))==0;self.handoff_event(s);continue
                if s.pc in self.system_addresses:
                    if s.pc==0xddd8:self.clock_tick();self.clock_ticks+=1
                    status=self.system_fn(c.byref(self.bus),c.byref(s),self.callbacks[5],self.service,None,1,0)
                    if status==6 and s.pc not in [0xdf66,0xdf86]:self.handoff_event(s)
                elif s.pc in self.health_addresses:
                    status=self.health_fn(c.byref(self.bus),c.byref(s),self.callbacks[5],self.service,None,1000000,1)
                    if status==0:self.virtual_RTS(s)
                    elif status==6 and s.pc not in [0xdf7c,0xdf7a,0xdf66,0xdf86]:self.handoff_event(s)
                    if s.pc==0x18b94:self.handoff_event(s)
                elif s.pc in self.new_groups or s.pc in self.render_groups:
                    fn=self.new_groups.get(s.pc)or self.render_CPU[self.render_groups[s.pc]];status=fn(c.byref(self.bus),c.byref(s),self.callbacks[5],self.service,None,1000000,1)
                    if status==0:self.virtual_RTS(s)
                elif ctx in [0xc1528,0xc1928]and s.pc in [0xf4d8,0xf56e,0xf70c]:
                    status=self.actor_body(c.byref(self.bus),c.byref(s),self.callbacks[5],c.cast(self.service,base.joined.actor.actor.SERVICE),None,1000000)
                else:raise AssertionError(('C scheduled startup continuation',hex(s.pc),hex(ctx)))
                assert status in [0,4,6,8]and not self.errors,(status,hex(s.pc),self.errors)
            else:raise AssertionError(('C scheduled startup budget',hex(s.pc)))
            result=s;steps=None;assert self.gpu_counter.value==GPU_before and self.counter.value==DSP_before and self.C_original_CPU_attempts==0
        assert not self.asset_disc.pending and not self.pending_render and not self.pending_movement
        final=self.device.ram();contexts=self.task_table(final)
        snapshot=dict(source_music_engine_calls=list(self.music_engine_calls),source_music_word_events=list(self.music_word_events),source_BIOS_mode_BUTCH_ticks=self.bios_mode_ticks,source_BIOS_TOC_BUTCH_ticks=self.bios_toc_ticks,actual_asset_controller_ticks=self.transport_ticks,actual_asset_GPU_IRQs=list(self.transport_IRQs),actual_asset_VBI_events=list(self.transport_VBIs),source4000_entry=entry,CPU=media.scheduler.cpu_dict(result),RAM=sha(final),hardware=self.hardware(),begin_hardware=begin_hardware,contexts=contexts,disc=dict(requests=list(self.asset_disc.requests),completions=list(self.asset_disc.completions),stops=self.asset_disc.stops),GPU_calls=self.gpu_calls[start_calls:],handoffs=list(self.handoffs),external_system_clock_ticks=self.clock_ticks)
        self.startup_final_CPU=media.CPU.from_buffer_copy(bytes(result))
        (self.out/f'case-{case["id"]}-{mode}-RAM.bin').write_bytes(final);self.startup_active=False;self.scheduling_active=False;self.loading_active=False
        return snapshot,dict(native_CPU_steps=steps,original_CPU_attempts=self.C_original_CPU_attempts)
    def seed_cpu(self,state):
        if not self.full_running:return super().seed_cpu(state)
        # Continue the live native CPU at the startup boundary. Controlled
        # later entry providers change registers/banks without a CPU reset.
        if media.scheduler.cpu_dict(self.cpu())==media.scheduler.cpu_dict(state):return
        core=self.core;core.m68k_set_reg(17,0x2000);core.m68k_set_reg(15,state.ssp);core.m68k_set_reg(17,0);core.m68k_set_reg(15,state.usp);core.m68k_set_reg(17,state.sr)
        for i,v in enumerate(state.registers):core.m68k_set_reg(i,v)
        core.m68k_set_reg(16,state.pc)
    def full_call(self,message,ram,case,mode):
        startup,startup_checks=self.source_startup(ram,case,mode)
        initial=media.CPU.from_buffer_copy(bytes(self.startup_final_CPU));before=self.device.ram();info={'CPU':media.scheduler.cpu_dict(initial)}
        planned,world_CPU=base.joined.origin.fixture(before,info,self.gate)
        planned=bytearray(planned)
        def put(a,w,v):planned[a:a+w]=(v&((1<<(8*w))-1)).to_bytes(w,'big')
        put(0xc0920,4,0xc0d28);put(base.joined.origin.WORLD+12,4,world_CPU.registers[15]);put(base.joined.origin.WORLD+16,4,world_CPU.pc);put(base.joined.origin.WORLD+20,2,world_CPU.sr)
        patches=[dict(address=hex(i),before=a,after=b)for i,(a,b)in enumerate(zip(before,planned))if a!=b]
        for change in patches:self.device.direct(int(change['address'],16),1,change['after'])
        assert self.device.ram()==bytes(planned)
        self.controlled_loading_entry=dict(kind='controlled_doorway_pose_entry_task_quiescence',patches=patches,RAM_before=sha(before),RAM_after=sha(self.device.ram()),CPU=media.scheduler.cpu_dict(initial))
        self.full_running=True;self.loading_active=True;self.prefix_running=True;self.movie_started=False;self.near_supplied=False;self.host_phase=0;self.prefix_events=[];self.renderer_active=False;self.render_complete=False;self.pending_render=None;self.pending_movement=False;self.polls=[];self.yields=[];self.handoffs=[];self.npc_yields=self.renderer_yields=self.world_yields=0;self.post_calls=[];self.pad.set_buttons([]);self.global_clock_step=8;self.clock_step=8;self.output=self.out;self.dialogue_returned=False
        self.message=message;self.rate=round(26590906/(64*(message['SCLK']+1)));self.timeline=0;self.sample_index=0;self.video_index=0;self.word_clocks=0;self.stages=[];self.audio_tokens=[];self.audio_cursor=0;self.audio_reads=0;self.pcm=bytearray();self.sound_digest=hashlib.sha256();self.last_GPU_call=len(self.gpu_calls);self.begin_CPU=initial
        GPU_before=self.gpu_counter.value;DSP_before=self.counter.value
        result,steps=self.run_native(initial,self.native_coverage)if mode=='native'else self.run_C(initial)
        assert self.sample_index==len(message['sample_records'])and self.video_index==message['video_samples']
        assert self.device.read(0xbd85c,2)==0xffff and self.device.read(0xbd85e,2)==0 and self.device.read(0x47b82,2)==0
        assert self.dialogue_returned and self.device.read(self.actor_address+0x6c,2)==2
        if mode=='C':assert self.gpu_counter.value==GPU_before and self.counter.value==DSP_before and self.C_original_CPU_attempts==0
        path=self.out/f'case-{case["id"]}-{mode}-movie.wav'
        with wave.open(str(path),'wb')as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(self.rate);w.writeframes(self.pcm)
        summary=dict(total_asset_controller_ticks=self.transport_ticks,total_asset_GPU_IRQs=list(self.transport_IRQs),total_asset_VBI_events=list(self.transport_VBIs),startup=startup,controlled_loading_entry=self.controlled_loading_entry,prefix_events=self.prefix_events,asset_disc_requests=self.asset_disc.requests,asset_disc_completions=self.asset_disc.completions,source_near_trigger_supplied=self.near_supplied,task_cycles=dict(NPC=self.npc_yields,renderer=self.renderer_yields,world=self.world_yields),polls=self.polls,yields=self.yields,handoffs=self.handoffs,renderer_begin=self.renderer_begin,renderer_end=self.renderer_end,render_queue_before=self.render_queue_before,render_queue_after=self.device.read(0x112940,2),post_dialogue_calls=self.post_calls,pre_yield_CPU=self.pre_yield_CPU,source_merchant_message=60,source_return_PC=hex(result.pc),CPU=media.scheduler.cpu_dict(result),RAM=sha(self.device.ram()),hardware=self.hardware(),source_state=self.device.read(0xbd85c,2),samples=self.sample_index,frames=self.video_index,word_clocks=self.word_clocks,sound_digest=self.sound_digest.hexdigest(),PCM_sha256=sha(self.pcm),audio_enqueued=len(self.audio_tokens),queries=self.queries,deliveries=self.deliveries,final_GPU_calls=self.gpu_calls[self.last_GPU_call:])
        (self.out/f'case-{case["id"]}-{mode}-final-RAM.bin').write_bytes(self.device.ram());self.full_running=False
        return dict(summary=summary,stages=self.stages),dict(startup_checks=startup_checks,audio_reads=self.audio_reads,source_audio_tokens_reached=self.audio_cursor+1,wav=str(path))
    def task_table(self,ram):
        # Source-created task frames may now contain actual sleep/actor state.
        get=lambda a,w=4:int.from_bytes(ram[a:a+w],'big');rows=[];seen=set();obj=0xc0d28
        while obj not in seen:
            assert obj in base.topology.CONTEXTS;seen.add(obj);rows.append(dict(context=obj,next=get(obj),prev=get(obj+4),entry=get(obj+8),SP=get(obj+12),saved_PC=get(obj+16),SR=get(obj+20,2),deadline=get(obj+22),blocked=get(obj+26),argument=get(obj+30),suspend_count=get(obj+34)));obj=get(obj)
        assert obj==0xc0d28 and len(rows)==21 and get(0xc0924)==0xc5d28
        for r in rows:assert get(r['next']+4)==r['context']and get(r['prev'])==r['context']
        return rows
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cases',type=int,default=2);ap.add_argument('--movie',action='store_true');ap.add_argument('--timer',action='store_true');opt=ap.parse_args();assert opt.cases>0
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);category=('BIWN-movie-transport-C-diagnostic-cold-entry-timer-startup-loading-movie-world'if opt.movie else 'BIWN-movie-transport-C-diagnostic-cold-entry-timer-scheduled-startup')if opt.timer else 'BIWN-movie-transport-C-diagnostic-cold-entry-startup-loading-movie-world'if opt.movie else 'BIWN-movie-transport-C-diagnostic-cold-entry-scheduled-startup';out=ROOT/'verification'/category/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);src=ROOT/'projects/black-ice-white-noise/restoration';proof=json.loads((ROOT/'verification/system-startup-retained-GPU-checks.json').read_text());names=list(proof['source_sha256'])+['biwn_health_timeout_cpu.c','biwn_entry_setup_cpu.c','biwn_dsp_music_bootstrap.c','biwn_dsp_music_engine.c','biwn_bios_setup_cpu.c','biwn_bios_controller_cpu.c','biwn_bios_mode_cpu.c','biwn_bios_toc_cpu.c','biwn_bios_transport_cpu.c','biwn_gpu_cd_ISR.c','biwn_vbi_event.c']+(['biwn_gpu_timer.c']if opt.timer else []);lib=out/'libscheduled-startup.dylib'
    cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(src/n)for n in names]+['-o',str(lib)];built=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(built.stdout+built.stderr);assert not built.returncode,built.stderr
    mappings=[json.loads((session/(n+'-fullCPU-generation.json')).read_text())for n in ['movie','video','media-setup']];rows=[]
    for p in session.glob('*-fullCPU-generation.json'):rows+=json.loads(p.read_text()).get('instructions_decoded',[])
    stage=(session/'nextstage-68000-candidate.bin').read_bytes();assert sha(stage)=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453';cold=bytearray(0x200000);cold[0x4000:0x4000+len(stage)]=stage;bios=(ROOT/'render-assets/jaguarcd_bios.bin').read_bytes();assert sha(bios)=='646a0687a01dc6c1fffff508ca25c14b78d30bdfcfa958d4c3e20f6bf78e4f1b';cold[0x3000:0x3e00]=bios[0x84a6:0x92a6];ram=bytes(cold);rows+=json.loads((session/'input-dispatch-fullCPU-workmap.json').read_text())['instructions']
    for a,b in base.joined.actor.navigation.RANGES+base.joined.actor.rng_cpu.RANGES+[(0x4088,0x408a),(0xf4d8,0xf712),(0xdfa6,0xdfb2),(0xdf60,0xdf6c),(0xde08,0xde5c),(0xdf7a,0xdf7c),(0xdeb6,0xdee2),(0xe4c0,0xe53c),(0xeac4,0xec04),(0x13440,0x134dc),(0x13c9a,0x13f12),(0xe220,0xe26c),(0x13b5a,0x13c9a),(0x1028e,0x10430),(0x10652,0x106c4),(0x191f4,0x192a2),(0x192bc,0x19f2c),(0xf360,0xf368),(0xf880,0xf888),(0xf0fa,0xf35e),(0x20820,0x20a9c)]:rows+=base.fixtures.gen.loader.base.binary_tools.m68k_instructions(ram[a:b],a)[0]
    disc=base.joined.Disc(session);frames=Path(json.loads((ROOT/'verification/BIWN-movie-sequence-GPU-C.json').read_text())['directory'])/'C-frames';Runtime.entry_rows=json.loads((session/'entry-setup-fullCPU-generation.json').read_text())['instructions_decoded'];runtime=Runtime(lib,rows,*[m['instructions_decoded']for m in mappings],disc=disc,out=out,frame_directory=frames);runtime.health_addresses={r['address']for r in json.loads((session/'health-timeout-fullCPU-generation.json').read_text())['instructions_decoded']};results=[]
    runtime.timer_enabled=opt.timer;runtime.entry_coverage=set();runtime.entry_TOC=base.joined.controller.make_toc(disc.layout)
    runtime.gate=next(g for g in json.loads((ROOT/'verification/biwn-startup-loaded-doorway-candidates.json').read_text())['candidates']if g['target']==312)
    extraction=json.loads((ROOT/'verification/BIWN-dialogue-audio-extraction.json').read_text());message=next(m for m in extraction['messages']if m['message_id']==60);record=next(r for r in json.loads((ROOT/'verification/NPC-message-video-dependency-inspection.json').read_text())['message_records']if r['message_id']==60);message={**message,'marker':int(record['source_long_fields'][2],16)}
    try:
        for _,case in base.fixtures.caller_cases(ram,opt.cases):
            initial=bytearray(ram);initial[0x21ea8:0x22770]=(session/'media-video-gpu-21ea0/original-overlay.bin').read_bytes();case['buttons']=[]if case['id']%2==0 else [3];observed={}
            for mode in ['C']:
                save(out/'status.json',dict(status='running',case=case['id'],mode=mode));observed[mode],checks=runtime.full_call(message,bytes(initial),case,mode)if opt.movie else runtime.source_startup(bytes(initial),case,mode);save(out/f'case-{case["id"]}-{mode}.json',observed[mode])
            save(out/'status.json',dict(status='terminal_diagnostic_completed_not_comparison'));return
            persisted={mode:json.loads((out/f'case-{case["id"]}-{mode}.json').read_text())for mode in ['native','C']}
            if observed['native']!=observed['C']or persisted['native']!=persisted['C']:save(out/'mismatch.json',persisted);raise AssertionError(str(out/'mismatch.json'))
            results.append(dict(case=case,snapshot=observed['C'],C_checks=checks));save(out/'cases.json',results)
        views=[r['snapshot']['summary']['startup']if opt.movie else r['snapshot']for r in results]
        report=dict(status='source_system_health_CD_scheduled_startup_retained_GPU_DSP_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(results),handoffs_per_case=[len(r['handoffs'])for r in views],disc_requests_per_case=[len(r['disc']['requests'])for r in views],source_DF60_RTS_completion_adapter=False,initial_context_or_startup_capture_supplied=False,source_health_sleep_TRAP3_verified=True,actor_task_body_reached=0xf4d8 in runtime.startup_pc_coverage,retained_GPU_DSP_state_compared=True,source_boot_verified=False,whole_game_complete=False,source_sha256={n:sha((src/n).read_bytes())for n in names},test_script_sha256=sha(Path(__file__).read_bytes()),compiler=cmd,limits=['Starts with supplied FrozenRAM/CPU/source processor setup and one-unit externally supplied ticks at systemDDD8, buttons, BIOS303C/3042/file-disc674phase and completion after actual source handoff. No source4000/globalfirmware/physical timing proof.','SourceDD40 pool/system/render creation and source scheduler/private continuations are retained through17DC2. Shared synchronous blitter/GPU completion remain. Created actor bodies are not implied executed by their creation. Later tasks/modalbranch/physicalscanout/playability remain unverified.'])
        if opt.movie:
            report.update(status='source_scheduled_startup_loading_creation_movie_world_native_C_match',frames_per_case=[r['snapshot']['summary']['frames']for r in results],audio_enqueued_per_case=[r['snapshot']['summary']['audio_enqueued']for r in results],world_cycles_per_case=[r['snapshot']['summary']['task_cycles']for r in results],source_startup_to_movie_world_connected=True,intermediate_startup_RAM_restore_or_CPU_GPU_DSP_reset=False)
            report['limits'].append('Controlled doorway/stair entries/poses/worldlooprestore,near-player/cash0/buttons/8-unit world clocks/taskquiescence remain. Source startup is continuous into loading/movie/world with live CPU/RAM/GPU/DSP; no startup boundary capture is supplied. Movie file/MSF/LBA/+2 alignment/BIOS/nominal video/SSI/VBI providers remain; no physicaltiming claim.')
        if opt.timer:
            report.update(source_system_clock_IRQ2_handler=True,source_system_clock_direct_RAM_increment=False,source_system_timer_events_per_case=[r['external_system_clock_ticks']for r in views])
            report['limits'][0]='Supplied FrozenRAM/CPU/sourceprocessor setup, externally delivered timerIRQ2 events at systemDDD8, buttons, BIOS303C/3042/file-disc674phase/completion after realhandoff. Clock updates use sourceGPUhandler, not directRAMincrement; timerperiod/globaltime/source4000boot/firmware remain unverified.'
        report.update(initial_FrozenRAM_supplied=False,initial_main_RAM_zero_plus_pinned_stage=True,initial_stage_sha256=sha(stage),source4000_entry_connected=True,DSP_music_mailbox_completion_script=False,initial_processor_setup_calls_supplied=False,initial_CPU_replaced_at_DD40=False,entry_CPU_coverage=[len(runtime.entry_coverage&runtime.entry_addresses),len(runtime.entry_addresses)])
        report['limits'][0]='Source4000 runs continuously into sourceDD40/scheduledstartup, with sourceGPU initialization and musicDSP command2 acknowledgement. Zero mainRAM plus pinned source stage, supplied initialCPU/device seed, canonical pre-relocation GPU bytes, BIOS3000/3048/3006 ABI adapters and305A syntheticTOC, externaltimer delivery and later clock/input/disc providers remain. DSP music engine is stopped atF1B148 before mixer/SSI; actualglobalboot/firmware/physicaltimer scheduling not proved.'
        assert all(len(v['source_music_word_events'])==13 and sum(2 in e['IRQs']for e in v['source_music_word_events'])==4 for v in views)
        report.update(source_bank1_music_engine_live_startup=True,source_music_word_events_per_case=[len(v['source_music_word_events'])for v in views],source_music_timer2_events_per_case=[sum(2 in e['IRQs']for e in v['source_music_word_events'])for v in views],full_music_playback_verified=False)
        report['limits'][0]=report['limits'][0].replace('DSP music engine is stopped atF1B148 before mixer/SSI;', 'Source bank1 music engine now initializes and runs under one externally deliveredSSI/DAC word per startup clockevent, with timer2 every4words. Default song3BCE0/index0 produces silence; audible music/allvoices/physical rates remain unverified;')
        report.update(actual_BIOS3000_CPU_setup_linked=True,BIOS3000_noop_adapter=False,BIOS_resident_loaded_from_supplied_ROM=True,BIOS_sha256=sha(bios),BIOS_resident_interval=['0x3000','0x3e00'])
        report['limits'][0]=report['limits'][0].replace('BIOS3000/3048/3006 ABI adapters','actual resident BIOS3000 setup and BIOS3048/3006 ABI adapters').replace('Zero mainRAM plus pinned source stage','Zero mainRAM plus pinned source stage and actual user-BIOS resident bytes at3000..3E00 (hostloaded, not firmwareboot)')
        report.update(actual_BIOS3048_controller_CPU_linked=True,BIOS3048_preserve_register_adapter=False)
        report['limits'][0]=report['limits'][0].replace('actual resident BIOS3000 setup and BIOS3048/3006 ABI adapters','actual resident BIOS3000/3048 CPU setup and BIOS3006 ABI adapter')
        report.update(actual_BIOS3006_mode_wait_linked=True,BIOS3006_adapter=False,preserved_CDI_attached_to_BUTCH_model=True,BUTCH_full_state_compared=True,source_BIOS_mode_BUTCH_ticks_per_case=[v['source_BIOS_mode_BUTCH_ticks']for v in views])
        report['limits'][0]=report['limits'][0].replace('actual resident BIOS3000/3048 CPU setup and BIOS3006 ABI adapter','actual resident BIOS3000/3048/3006 CPU setup/mode and a preserved-CDI-backed BUTCH model advancing one tick per source3544poll')
        report.update(CDROM_timing_extension_compared=True,actual_BIOS305A_TOC_CPU_linked=True,synthetic_TOC_supplied=False,initial_TOC_supplied=False,source_BIOS_TOC_BUTCH_ticks_per_case=[v['source_BIOS_TOC_BUTCH_ticks']for v in views])
        report['limits'][0]=report['limits'][0].replace('one tick per source3544poll and305A syntheticTOC','one tick per source3544/3910/392E/37E0 status poll with actual305A TOC source code')
        report.update(actual_asset_BIOS_CPU_GPU_transport_linked=True,asset_file_payload_memcpy=False,asset_scripted_progress=False,source_VBI_progress=True,asset_controller_ticks_per_case=[v['actual_asset_controller_ticks']for v in views],asset_GPU_IRQs_per_case=[len(v['actual_asset_GPU_IRQs'])for v in views],asset_VBI_events_per_case=[len(v['actual_asset_VBI_events'])for v in views])
        report.update(initial_controller_fixture_supplied=True,initial_controller_state_sha256=sha(runtime.transport_controller_input[0]),initial_controller_timing_sha256=sha(runtime.transport_controller_input[1]),asset_entry_opcode_adapters=False,movie_file_transport_remains=True)
        if opt.movie:
            summaries=[r['snapshot']['summary']for r in results]
            report.update(total_actual_asset_requests_per_case=[len(v['asset_disc_requests'])for v in summaries],total_actual_asset_bytes_per_case=[sum(x['bytes']for x in v['asset_disc_requests'])for v in summaries],total_asset_controller_ticks_per_case=[v['total_asset_controller_ticks']for v in summaries],total_asset_GPU_IRQs_per_case=[len(v['total_asset_GPU_IRQs'])for v in summaries],total_asset_VBI_events_per_case=[len(v['total_asset_VBI_events'])for v in summaries])
        report['limits'][0]+=' Actual asset BIOS303C/3042/304E and GPU IRQ1/FIFO now replace file payload/progress delivery. One controller tick per poll/pump iteration; pump after source handoff until end, then delivered TOM VBI/sourceE7D4/304E/RTE. A shared pre-execution controller baseline/timing input includes retained buffers; it is restored only at each initial fixture, not during gameplay.'
        report['limits'].append('Movie still uses file-backed transport/BIOS adapters; asset/controller/VBI event delivery and GPU MMIO shadow/pipeline tail remain supplied. Buffer padding/globaltiming/full firmware boot/playability unverified.')
        pointer=('movie-transport-music-cold-entry-timer-startup-loading-movie-world-checks.json'if opt.movie else 'movie-transport-music-cold-entry-timer-scheduled-startup-checks.json')if opt.timer else 'entry-startup-loading-movie-world-checks.json'if opt.movie else 'entry-scheduled-startup-checks.json'
        save(out/'report.json',report);save(out/'coverage.json',dict(startup_PC=sorted(runtime.startup_pc_coverage)));save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification'/pointer,report);print(json.dumps({k:v for k,v in report.items()if k not in ['source_sha256','compiler']}))
    except Exception as error:
        (out/'failed-current-RAM.bin').write_bytes(runtime.device.ram());save(out/'failure-state.json',dict(CPU=media.scheduler.cpu_dict(runtime.cpu()),source_handoffs=getattr(runtime,'handoffs',[]),disc_requests=runtime.asset_disc.requests));save(out/'status.json',dict(status='terminal_failed',error=repr(error),errors=runtime.errors[-5:]));raise
    finally:runtime.core.CDIntfCloseImage();runtime.oracle.close();disc.close()
if __name__=='__main__':main()
