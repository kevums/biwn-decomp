"""Busy CD/resource lock: source D414 TRAP0, resource tail, DF60 yield, user movie.

Supplied two-task ring and resource completion continuation/private frame;
DF60 is called via declared four-byte caller return. Movie private frames
and both trap/yield exception frames are original source, never host restored.
"""
import ctypes as c,json,os,struct,subprocess,argparse,wave,hashlib
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_user_full_movie_caller as user
full=user.full;ROOT=user.ROOT;media=user.media;save=user.save;sha=user.sha;controller=user.controller;video=user.video;AV=user.AV;Disc=user.Disc
class Runtime(user.Runtime):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.movie_trap=self.lib.biwn_movie_trap_dispatch;self.movie_trap.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),c.c_uint32];self.movie_trap.restype=c.c_int
        self.scheduler_yield=self.lib.biwn_scheduler_yield;self.scheduler_yield.argtypes=self.movie_trap.argtypes;self.scheduler_yield.restype=c.c_int
        self.resource=self.lib.biwn_resource_cpu_call;self.resource.argtypes=self.fn.argtypes;self.resource.restype=c.c_int
        self.busy_stages=[]
    def configure_ring(self,cpu):
        self.busy_stages=[];self.device.direct(0x47b80,2,1);self.device.direct(0x80,4,0xde08);self.device.direct(0xc0920,4,0x100000)
        for obj,next_obj,sp,pc in [(0x100000,0x101000,cpu.registers[15],0xd3fc),(0x101000,0x100000,0x1013e4,0x1b13c)]:
            for a,w,v in [(obj,4,next_obj),(obj+4,4,next_obj),(obj+12,4,sp),(obj+16,4,pc),(obj+20,2,0),(obj+22,4,0),(obj+26,4,0),(obj+34,4,0)]:self.device.direct(a,w,v)
        for i,value in enumerate([0x2202,0x3303,0xaa02,0xaa03,0xaa04,0xaa05]):self.device.direct(0x1013e4+i*4,4,value)
        self.device.direct(0x1013fc,4,0x190100)
    def record_busy(self,label,cpu):
        self.busy_stages.append(dict(label=label,CPU=media.scheduler.cpu_dict(cpu),RAM=sha(self.device.ram()),hardware=self.snapshot()['hardware'],busy=self.device.read(0x47b80,2),current_task=hex(self.device.read(0xc0920,4))))
    def prepare_yield_call(self,cpu):
        cpu.registers[15]-=4;cpu.usp=cpu.registers[15];self.device.direct(cpu.registers[15],4,0x190102);cpu.pc=0xdf60
    def C_busy_handoff(self,cpu):
        self.record_busy('movie_before_D414',cpu);assert self.movie_trap(c.byref(self.bus),c.byref(cpu),16)==0 and cpu.pc==0x1b13c;self.record_busy('resource_selected',cpu)
        assert self.resource(c.byref(self.bus),c.byref(cpu),self.callbacks[5],self.service,None,10000,1)==0 and cpu.pc==0x190100;self.record_busy('source_resource_released_lock',cpu)
        self.prepare_yield_call(cpu);assert self.scheduler_yield(c.byref(self.bus),c.byref(cpu),16)==0 and cpu.pc==0xd416;self.record_busy('movie_resumed_D416',cpu)
    def Native_busy_handoff(self):
        self.record_busy('movie_before_D414',self.cpu())
        for _ in range(1000):
            pc=self.core.m68k_get_reg(None,16)
            if pc==0x1b13c:break
            assert pc==0xd414 or 0xde08<=pc<0xde5c,hex(pc);self.native_coverage.add(pc);self.core.m68k_execute(1)
        else:raise AssertionError('Native busy trap dispatch bound')
        self.record_busy('resource_selected',self.cpu())
        for _ in range(1000):
            pc=self.core.m68k_get_reg(None,16)
            if pc==0x190100:break
            assert pc in self.rows,hex(pc);self.native_coverage.add(pc);self.core.m68k_execute(1)
        else:raise AssertionError('Native resource release bound')
        cpu=self.cpu();self.record_busy('source_resource_released_lock',cpu);self.prepare_yield_call(cpu);self.core.m68k_set_reg(15,cpu.registers[15]);self.core.m68k_set_reg(16,cpu.pc)
        for _ in range(1000):
            pc=self.core.m68k_get_reg(None,16)
            if pc==0xd416:break
            assert 0xdf60<=pc<0xdf6c or 0xde08<=pc<0xde5c,hex(pc);self.native_coverage.add(pc);self.core.m68k_execute(1)
        else:raise AssertionError('Native resource yield bound')
        self.record_busy('movie_resumed_D416',self.cpu())
    def run_C(self,cpu):
        if not self.full_running:return super().run_C(cpu)
        if cpu.pc==0xd3fc:self.configure_ring(cpu)
        self.C_CPU=cpu
        for _ in range(8):
            status=self.movie_call(c.byref(self.bus),c.byref(cpu),self.callbacks[5],self.service,None,1000000,1)
            if status==6:
                assert cpu.pc==0xd414;self.C_busy_handoff(cpu);continue
            assert status==0,(status,self.errors);return cpu,None
        raise AssertionError('C busy handoff bound')
    def full_call(self,message,base,seed,mode):
        self.full_running=False;self.pending=None;self.start(base,seed,mode)
        # Existing startup probe entered movie mode; source exit returns to
        # resident readiness before D3FC makes its own source entry request.
        s=media.CPU();s.registers[15]=s.ssp=0x1ff000;s.usp=0x1fe000;s.pc=0xd3ec;s.sr=0x2000;self.device.direct(s.registers[15],4,controller.STOP)
        self.run_native(s,set()) if mode=='native' else self.run_C(s);self.run_boot_exit('movie_exit');self.run_dispatch(True)
        self.message=message;self.rate=round(26590906/(64*(message['SCLK']+1)));self.timeline=0;self.sample_index=0;self.video_index=0;self.word_clocks=0;self.stages=[];self.audio_tokens=[];self.audio_cursor=0;self.audio_reads=0;self.pcm=bytearray();self.sound_digest=hashlib.sha256();self.last_GPU_call=len(self.gpu_calls)
        self.full_running=True
        initial=media.CPU();initial.registers[:]=[0]*15+[0x180fe4];initial.ssp=0x200000;initial.usp=0x180fe4;initial.sr=0;initial.pc=0xd3fc
        self.device.direct(initial.registers[15],4,controller.STOP)
        args=struct.pack('>6I',3,message['message_offset'],0, message['marker'],224,0);c.memmove(self.device.pointer+initial.registers[15]+4,args,len(args))
        self.begin_CPU=initial;GPU_before=self.gpu_counter.value;DSP_before=self.counter.value
        result,steps=self.run_native(initial,self.native_coverage) if mode=='native' else self.run_C(initial)
        assert self.sample_index==len(message['sample_records']) and self.video_index==message['video_samples'],('Complete sample table',self.sample_index,len(message['sample_records']))
        assert self.device.read(0xbd85c,2)==0xffff and self.device.read(0xbd85e,2)==0 and self.device.read(0x47b82,2)==0
        self.run_boot_exit('movie_exit');self.run_dispatch(True)
        if mode=='C':assert self.gpu_counter.value==GPU_before and self.counter.value==DSP_before and self.C_original_CPU_attempts==0
        name=f'message-{message["message_id"]}-{mode}.wav'
        with wave.open(str(self.out/name),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(self.rate);w.writeframes(self.pcm)
        summary=dict(busy_handoff=self.busy_stages,CPU=media.scheduler.cpu_dict(result),RAM=sha(self.device.ram()),hardware=self.snapshot()['hardware'],source_state=self.device.read(0xbd85c,2),samples=self.sample_index,frames=self.video_index,word_clocks=self.word_clocks,sound_digest=self.sound_digest.hexdigest(),PCM_sha256=sha(self.pcm),audio_enqueued=len(self.audio_tokens),queries=self.queries,deliveries=self.deliveries,final_GPU_calls=self.gpu_calls[self.last_GPU_call:])
        self.full_running=False
        return dict(summary=summary,stages=self.stages),dict(audio_reads=self.audio_reads,source_audio_tokens_reached=self.audio_cursor+1,wav=str(self.out/name))
    def run_native(self,s,coverage):
        if self.full_running and s.pc==0xd3fc:self.configure_ring(s)
        self.seed_cpu(s);steps=0
        for _ in range(20000000):
            pc=self.core.m68k_get_reg(None,16)
            if self.full_running and pc==0xd414:self.Native_busy_handoff();continue
            if pc==controller.STOP:return self.cpu(),steps
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
            steps+=1
        raise AssertionError(('Native full movie caller bound',hex(pc)))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--all',action='store_true');parser.add_argument('--native-reference',type=Path);options=parser.parse_args()
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mappings=[json.loads((session/n).read_text()) for n in ['movie-fullCPU-generation.json','video-fullCPU-generation.json','media-setup-fullCPU-generation.json']]
    poll=controller.movie.generator.loader.base.binary_tools.m68k_instructions((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()[0xe4c0:0xe53c],0xe4c0)[0];geometry=json.loads((session/'geometry-records-fullCPU-generation.json').read_text());boot_CPU=json.loads((session/'GPU-boot-fullCPU-generation.json').read_text())
    privilege=json.loads((session/'movie-privilege-fullCPU-generation.json').read_text())
    resource=json.loads((session/'resource-fullCPU-generation.json').read_text())
    rows=resource['instructions_decoded']+privilege['instructions_decoded']+boot_CPU['instructions_decoded']+sum([m['instructions_decoded'] for m in mappings],[])+poll+[x for x in geometry['instructions_decoded'] if 0xe098<=x['address']<0xe0a6]
    out=ROOT/'verification/BIWN-busy-user-movie-caller'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);src=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libfull-movie.dylib'
    previous=json.loads((ROOT/'verification/BIWN-movie-source-boot-exit-AV.json').read_text());names=list(previous['source_sha256'])+['biwn_movie_VBI_event.c','biwn_movie_privilege_cpu.c','biwn_movie_trap.c','biwn_scheduler.c','biwn_resource_cpu.c'];cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(src/n) for n in names],'-o',str(library)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
    disc=Disc(session);frames=Path(json.loads((ROOT/'verification/BIWN-movie-sequence-GPU-C.json').read_text())['directory'])/'C-frames';runtime=Runtime(library,rows,*[m['instructions_decoded'] for m in mappings],disc=disc,out=out,frame_directory=frames)
    extraction=json.loads((ROOT/'verification/BIWN-dialogue-audio-extraction.json').read_text());markers={x['message_id']:int(x['source_long_fields'][2],16) for x in json.loads((ROOT/'verification/NPC-message-video-dependency-inspection.json').read_text())['message_records']}
    base=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());base[0x21ea8:0x22770]=(session/'media-video-gpu-21ea0/original-overlay.bin').read_bytes();toc=controller.make_toc(disc.layout);base[0x2c00:0x2c00+len(toc)]=toc
    results=[];coverage=set()
    try:
        for case,m in enumerate(extraction['messages'] if options.all else extraction['messages'][:1]):
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
        report=dict(status='busy_resource_TRAP0_yield_user_source_D3FC_movie_callers_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),all_six=options.all,messages=results,frames=sum(x['video_frames'] for x in results),audio_samples=sum(x['audio_samples'] for x in results),user_mode_caller=True,busy_resource_TRAP0_handoff_verified=True,resource_tail_and_DF60_yield_verified=True,source_privilege_STOP_and_nested_IRQ_verified=True,source_CPU_coverage=[len(coverage&set(x['address'] for x in mappings[0]['instructions_decoded'])),mappings[0]['instructions']],native_PC_coverage=sorted(coverage),source_sha256={n:sha((src/n).read_bytes()) for n in names},script_sha256=sha(Path(__file__).read_bytes()),word_clocks=sum(x['word_clocks'] for x in results),source_dispatches=sum(x['source_dispatches'] for x in results),disc_requests=sum(x['disc_requests'] for x in results),whole_game_complete=False,BIOS_actual_firmware=False,physical_AV_synchronization=False,
            limits=['Source fullD3FC with resource-busy1, supplied two-task ring/resource completion continuation and declaredDF60call, repeatcount0/no cancellation. Busy resource lock released by source1B13C, actualD414/TRAP/RTE andDF60/yield resume movieD416. Source movie samples/arguments/pointers/endstate/audio-stop/exit are not host replaced.',
                    'File-backed MSF/LBA disc provider reads declaredrawtracks/swap16/+2alignment at352800Bps with bootstrap ticks; BIOS3000 no-op. No actualfirmware/timing claim.',
                    'Host nominal600unit video clock, sourceVBI progress handler and SCLK18 SSI clocks at dispatch boundaries; no global game schedule/physical scanout.',
                    'Source DSP audio pointer/bytes verified at every enqueue; everyC externalaudio byte checked against its chronological original disc token. FullCPU/RAM/GPU/DSP/peripherals and GPUtrace/counts perdispatch; allDSP/DAC/PCM/counts perwordclock in cumulative digest. Microstates excluded.'])
        save(out/'report.json',report);save(ROOT/'verification/BIWN-busy-user-movie-caller.json',report);save(out/'status.json',dict(status='terminal_pass'));print(json.dumps(dict(directory=str(out),frames=report['frames'],audio_samples=report['audio_samples'])))
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e),errors=runtime.errors[-5:]));raise
    finally:runtime.oracle.close();disc.close()
if __name__=='__main__':main()
