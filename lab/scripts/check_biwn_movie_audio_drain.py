"""Source CPU movie dispatch with complete first-cluster audio-buffer drain.

BIOS3000 is a declared ABI provider; fullfirmware/CD/global clocks separate.
"""
import ctypes as c,json,os,struct,subprocess,wave
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_movie_boot_exit_AV as joined
import check_biwn_movie_source_overlay_AV as overlay
import check_biwn_movie_controller_AV as AV
import check_biwn_movie_controller_video as controller
import check_biwn_full_video_cpu_gpu as video
ROOT=joined.ROOT;media=joined.media;save=joined.save;sha=joined.sha
class Runtime(joined.Runtime):
    def __init__(self,*args):
        super().__init__(*args);self.GPU_boot_CPU=self.lib.biwn_GPU_boot_cpu_call;self.GPU_boot_CPU.argtypes=self.fn.argtypes;self.GPU_boot_CPU.restype=c.c_int
        self.source_boot_service=self.service
        def service(_,bus,cpu,target):
            if target==0x3000:self.bios(cpu.contents,target);return 0
            return self.source_boot_service(_,bus,cpu,target)
        self.service=media.world_cpu.SERVICE(service)
    def drain_audio(self, bound=10000):
        pairs=[];states=[]
        for tick in range(bound):
            p,z=self.sound(1);pairs.extend(p);states.extend(z)
            logical=self.logical_DSP();state=AV.dsp.state_from_raw(logical)
            mailbox=int.from_bytes(logical[0x138:0x13c],'big')
            # Source queue is eight entries; r14/r15 are producer/consumer
            # indices and r7 is the active sample's remaining byte count.
            if mailbox==0 and state.registers[0][7]==0 and state.registers[0][14]==state.registers[0][15]:
                p,z=self.sound(1);pairs.extend(p);states.extend(z)
                return pairs,states,dict(word_clocks=len(pairs),remaining_bytes=0,
                    mailbox_bytes=0,queue_empty=True,source_pointer=state.registers[0][4])
        raise AssertionError('Audio buffer failed to drain within declared word-clock bound')
    def snapshot(self):
        result=super().snapshot()
        # Before the C DSP engine is initialized, compare the same8496
        # logicalDSP bytes on both paths, as throughout this integration.
        if self.C_DSP is None:result['hardware']['DSP']=dict(size=8496,sha256=sha(self.raw_DSP()[:8496]))
        return result
    def run_C(self,s):
        if s.pc==0xe00a:
            status=self.GPU_boot_CPU(c.byref(self.bus),c.byref(s),self.callbacks[5],self.service,None,10000,1);assert status==0,(status,self.errors);return s,None
        return super().run_C(s)
    def start(self,ram,seed,mode):
        self.C_DSP=None;self.pending_overlay=False;video.Runtime.start(self,ram,seed,mode);self.queries=[];self.progress=0x1c0000;self.timer_arm=False;self.timer_reads=0;self.deliveries=[]
        s=media.CPU();s.registers[15]=0x1fe000;s.usp=0x1fe000;s.ssp=0x1ff000;s.pc=0xe840;s.sr=0x700;self.device.direct(s.registers[15],4,controller.STOP)
        assert self.fn(c.byref(self.bus),c.byref(s),self.callbacks[5],self.service,None,10000,0)==0
        for entry in [0xd340,0xe7aa]:self.call(entry,b'')
        # SourceE00A performs the actual159word copy/PC/GO, with BIOS3000
        # a declared no-op ABI provider. No host mainGPU payload copy.
        load=media.CPU();load.registers[15]=0x1ff000;load.ssp=0x1ff000;load.usp=0x1fe000;load.pc=0xe00a;load.sr=0x2700;self.device.direct(load.registers[15],4,controller.STOP)
        load_cpu,_=self.run_native(load,self.native_coverage) if mode=='native' else self.run_C(load)
        self.source_GPU_loader_snapshot=dict(CPU=media.scheduler.cpu_dict(load_cpu),RAM=sha(self.device.ram()),hardware=self.snapshot()['hardware'])
        self.run_boot_exit('main_boot');self.run_dispatch(True)
        request=media.CPU();request.registers[15]=0x1ff000;request.ssp=0x1ff000;request.usp=0x1fe000;request.pc=0xd3c6;request.sr=0x2700;self.device.direct(request.registers[15],4,controller.STOP)
        request_result,_=self.run_native(request,self.native_coverage) if mode=='native' else self.run_C(request)
        assert (self.core.GPUGetPC() if mode=='native' else self.gpu.pc)==0xf032c8
        if getattr(self,'clear_standalone_frame_fixture',True):
            c.memset(self.device.pointer+0x1a0000,0,80640)
        self.device.direct(0xbd85c,2,0)
        if mode=='C':self.C_DSP=AV.dsp.state_from_raw(self.raw_DSP())
        self.boot_count=self.segment();self.boot_hash=sha(self.logical_DSP());self.overlay_start=dict(CPU=media.scheduler.cpu_dict(request_result),GPU_calls=list(self.gpu_calls),RAM=sha(self.device.ram()),hardware=self.snapshot()['hardware'])
    def run_native(self,s,coverage):
        self.seed_cpu(s);steps=0
        for _ in range(1000000):
            pc=self.core.m68k_get_reg(None,16)
            if pc==controller.STOP:return self.cpu(),steps
            if pc in [0x3000,0x303c,0x304e]:
                state=self.cpu();self.bios(state,pc);self.core.m68k_set_reg(8,state.registers[8]);old=self.device.read(pc,2);self.device.direct(pc,2,0x4e75);self.core.m68k_execute(1);self.device.direct(pc,2,old)
            else:
                assert pc in self.rows,hex(pc);coverage.add(pc)
                if pc==0xd3d6 and 0xf031be<=self.core.GPUGetPC()<0xf03200:self.run_dispatch(False);assert self.core.GPUGetPC()==0xf03240;self.native_GPU(True)
                if self.timer_arm and pc in [0xd7bc,0xd7c2]:
                    self.timer_reads+=1
                    if self.timer_reads==3:self.device.direct(0xbd852,4,1)
                if pc==0x22a0e:self.core.m68k_execute(1);steps+=1;self.native_GPU(False);continue
                self.core.m68k_execute(1)
            steps+=1
        raise AssertionError(('Native source overlay/movie bound',hex(pc)))

def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    mappings=[json.loads((session/n).read_text()) for n in ['movie-fullCPU-generation.json','video-fullCPU-generation.json','media-setup-fullCPU-generation.json']]
    poll=controller.movie.generator.loader.base.binary_tools.m68k_instructions((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()[0xe4c0:0xe53c],0xe4c0)[0]
    geometry=json.loads((session/'geometry-records-fullCPU-generation.json').read_text())
    boot_CPU=json.loads((session/'GPU-boot-fullCPU-generation.json').read_text())
    rows=boot_CPU['instructions_decoded']+sum([m['instructions_decoded'] for m in mappings],[])+poll+[x for x in geometry['instructions_decoded'] if 0xe098<=x['address']<0xe0a6]
    out=ROOT/'verification/BIWN-movie-audio-drain'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    src=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libcontroller-AV.dylib'
    names=['biwn_movie_cpu.c','biwn_video_cpu.c','biwn_movie_relocation_GPU.c','biwn_movie_sequence_GPU.c','biwn_media_setup_cpu.c','biwn_input_poll_cpu.c','biwn_dsp_media_audio.c','biwn_geometry_records_cpu.c','biwn_gpu_dispatcher.c','biwn_gpu_main_boot.c','biwn_gpu_movie_exit.c','biwn_GPU_boot_cpu.c']
    cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(src/n) for n in names],'-o',str(library)]
    built=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
    runtime=Runtime(library,rows,*[m['instructions_decoded'] for m in mappings]);results=[];coverage=set()
    sequence_proof=json.loads((ROOT/'verification/BIWN-movie-sequence-GPU-C.json').read_text());frame_directory=Path(sequence_proof['directory'])/'C-frames'
    extraction=json.loads((ROOT/'verification/BIWN-dialogue-audio-extraction.json').read_text());markers={x['message_id']:int(x['source_long_fields'][2],16) for x in json.loads((ROOT/'verification/NPC-message-video-dependency-inspection.json').read_text())['message_records']}
    base=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());base[0x21ea8:0x22770]=(session/'media-video-gpu-21ea0/original-overlay.bin').read_bytes();toc=controller.make_toc(json.loads((session/'cdi-layout.json').read_text()));base[0x2c00:0x2c00+len(toc)]=toc
    try:
        for case,m in enumerate(extraction['messages']):
            with (session/'raw-tracks/track-04-raw.bin').open('rb') as f:f.seek(m['FILM_normalized_track_offset']-64);data=controller.swap16(f.read(0x20000))
            audio_bytes=Path(m['first_chunk_path']).read_bytes();message={**m,'stream_fixture':data,'first_audio_length':len(audio_bytes),'first_audio_data':audio_bytes}
            initial=media.CPU();initial.registers[:]=[0]*15+[0x1ff000];initial.usp=0x1fe000;initial.ssp=0x1ff000;initial.sr=0x2700
            ram=bytearray(base)
            for a,v in [(0xbd884,0x1c0000),(0xbd888,0x1ffc00),(0xbd890,3),(0xbd894,m['message_offset']),(0xbd8ac,markers[m['message_id']]),(0xbd880,0x802000),(0xbd852,0),(0x47b84,0x22002000),(0xbd88c,0x1a0000),(0xbd900,448)]:ram[a:a+4]=v.to_bytes(4,'big')
            ram[0xbd85c:0xbd85e]=bytes(2);snapshots={}
            for mode in ['native','C']:
                save(out/'status.json',dict(status='running',message=m['message_id'],mode=mode));parsed,_=runtime.sequence(bytes(ram),message,initial,case%3,mode,coverage)
                if mode=='native':coverage.update(runtime.native_coverage)
                counter=runtime.gpu_counter.value;DSP_counter=runtime.counter.value;stages=[]
                for sample,timer in [(0,0),(1,0),(2,0),(3,40)]:
                    calls=[];cpu=None
                    if sample:
                        runtime.device.direct(0xbd852,4,timer);s=media.CPU.from_buffer_copy(bytes(initial));s.pc=0xd4a8;runtime.device.direct(s.registers[15],4,controller.STOP);begin=len(runtime.gpu_calls)
                        cpu,steps=runtime.run_native(s,coverage) if mode=='native' else runtime.run_C(s);calls=runtime.gpu_calls[begin:]
                    record=next(x for x in m['sample_records'] if x['cluster']==0 and x['sample']==sample)
                    if sample in [1,3]:
                        assert len(calls)==2 and not record['audio']
                        frame=runtime.device.ram()[0x1a0000:0x1a0000+80640];expected=(frame_directory/f'message-{m["message_id"]}-frame-{sample//2:03d}.CRY16').read_bytes();assert frame==expected
                        sample_witness=dict(frame_sha256=sha(frame),matches_previous_all763_C_video=True)
                    else:
                        logical=runtime.logical_DSP();length=int.from_bytes(logical[0x138:0x13c],'big');pointer=int.from_bytes(logical[0x13c:0x140],'big');payload=runtime.device.ram()[pointer:pointer+length]
                        assert length==record['bytes'] and sha(payload)==record['sha256']
                        sample_witness=dict(audio_pointer=pointer,audio_length=length,audio_sha256=sha(payload),matches_extracted_disc_sample=True)
                    before=dict(sample_witness=sample_witness,CPU=media.scheduler.cpu_dict(cpu) if cpu is not None else None,RAM=sha(runtime.device.ram()),hardware=runtime.snapshot()['hardware'],GPU_calls=calls,movie_state=runtime.device.read(0xbd85c,2))
                    if record['audio']:
                        pairs,states,drain=runtime.drain_audio()
                        assert drain['source_pointer'] >= pointer+length, (drain,pointer,length)
                    else:
                        pairs,states=runtime.sound(128);drain=None
                    pcm=b''.join(struct.pack('<hh',*p) for p in pairs)
                    if mode=='C' and record['audio']:
                        wav=out/f'message-{m["message_id"]}-sample-{sample}-C.wav'
                        with wave.open(str(wav),'wb') as w:
                            w.setnchannels(2);w.setsampwidth(2);w.setframerate(round(26590906/(64*(m['SCLK']+1))));w.writeframes(pcm)
                    stages.append(dict(sample=sample,before_sound=before,word_clocks=len(pairs),
                        PCM_sha256=sha(pcm),nonzero_PCM_pairs=sum(p!=[0,0] for p in pairs),
                        drain=drain,sound_states=states))
                # SourceD3EC control5 causes the ownGPU IRQ0 frame, source
                # handler acknowledges/releases it, dispatcher reachesidle.
                exit_request=media.CPU.from_buffer_copy(bytes(initial));exit_request.pc=0xd3ec;runtime.device.direct(exit_request.registers[15],4,controller.STOP);begin=len(runtime.gpu_calls)
                exit_cpu,_=runtime.run_native(exit_request,coverage) if mode=='native' else runtime.run_C(exit_request)
                entered=dict(CPU=media.scheduler.cpu_dict(exit_cpu),RAM=sha(runtime.device.ram()),hardware=runtime.snapshot()['hardware'])
                runtime.run_boot_exit('movie_exit');runtime.run_dispatch(True)
                exit_stage=dict(IRQ_entered=entered,RAM=sha(runtime.device.ram()),hardware=runtime.snapshot()['hardware'],GPU_calls=runtime.gpu_calls[begin:])
                if mode=='C':assert runtime.gpu_counter.value==counter and runtime.counter.value==DSP_counter and runtime.C_original_CPU_attempts==0
                snapshots[mode]=dict(source_GPU_loader=runtime.source_GPU_loader_snapshot,overlay_start=runtime.overlay_start,boot=[runtime.boot_count,runtime.boot_hash],parser=[{k:p[k] for k in ['state','CPU','RAM','hardware']} for p in parsed['phases']],stages=stages,queries=runtime.queries,exit=exit_stage)
            if snapshots['native']!=snapshots['C']:save(out/'mismatch.json',snapshots);raise AssertionError(str(out/'mismatch.json'))
            results.append(dict(message_id=m['message_id'],snapshot=snapshots['C'],original_CPU_GPU_DSP_instructions_on_C_path=0));save(out/'fixtures.json',results);print(json.dumps(dict(message=m['message_id'],status='match')),flush=True)
        report=dict(status='first_cluster_source_CPU_GPU_DSP_complete_audio_buffers_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),messages=len(results),video_frames=12,source_sample_dispatches=24,word_clocks=sum(stage['word_clocks']for result in results for stage in result['snapshot']['stages']),complete_audio_buffers=12,
            CPU_source_coverage={name:[len(coverage&set(x['address'] for x in m['instructions_decoded'])),m['instructions']] for name,m in zip(['movie','video','media_setup'],mappings)},native_PC_coverage=sorted(coverage),source_sha256={n:sha((src/n).read_bytes()) for n in names},script_sha256=sha(Path(__file__).read_bytes()),
            original_CPU_GPU_DSP_instructions_on_C_path=False,whole_game_complete=False,C_source_GPU_loader_E00A=True,BIOS3000_actual_firmware=False,GPU_loader_CPU_instruction_coverage=[len(coverage&set(x['address'] for x in boot_CPU['instructions_decoded'])),boot_CPU['instructions']],source_D3C6_E098_and_GPU_dispatcher_executed=True,direct_host_movie_payload_reload=False,C_mainGPU_initializer_and_IRQ0_exit=True,source_D3EC_executed=True,
            limits=['First cluster per six movies; two audio and two video samples each. Host128KBdelivery, declared BIOS seek/progress/timer and sourceE00A GPUloader with BIOS3000 ABI provider; no firmware or streaming/ringwrap proof.',
                    'Audio word clocks continue until source mailbox, active byte count and queue indicate drained; one extra DAC strobe retained. Video gets128 clocks. Full DSP/RAM/DAC/counts/PCM compared per clock. First cluster only; no physical A/V synchronization or complete dialogue playback.',
                    'FullCPU/2MBRAM/logicalGPU4396/logicalDSP8496/peripherals/GPUtrace+counts percontrollerdispatch. Microstates excluded. Source STOP/GPUIRQ/RTE retained in nestedCproviders.',
                    'D3C6/E098 and sourceGPUdispatcher copy/start the movie overlay; CmainGPUinitializer/IRQ0handler and sourceD3EC exit nowrun; sourceE00A CPUloader nowruns; BIOS3000 remains explicitABIprovider, fullCPUboot/BIOS3000/D3FC/directTRAP0/globalscheduler/livegameplay remain separate. Registry139 unchanged; no newtraining.'])
        save(out/'report.json',report);save(ROOT/'verification/BIWN-movie-audio-drain-current.json',report);save(out/'status.json',dict(status='terminal_pass'));print(json.dumps(dict(directory=str(out),messages=len(results),video_frames=12,word_clocks=report['word_clocks'])))
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:runtime.oracle.close()
if __name__=='__main__':main()
