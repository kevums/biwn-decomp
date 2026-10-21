"""C mainGPU initializer, source movie startup/A-V and D3EC IRQ/resident return.

Host installs source159wordmainGPU payload and PC from E00A; CPUloader/
BIOS3000 firmware, disc transfer and physical clocks remain separate.
"""
import ctypes as c,json,hashlib,struct,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_movie_source_overlay_AV as overlay
import check_biwn_movie_controller_AV as AV
import check_biwn_movie_controller_video as controller
import check_biwn_full_video_cpu_gpu as video
from check_biwn_main_GPU_boot import Bus,W16
ROOT=overlay.ROOT;media=overlay.media;save=overlay.save;sha=overlay.sha
class Runtime(overlay.Runtime):
    def __init__(self,*args):
        super().__init__(*args)
        self.main_boot=self.lib.biwn_gpu_main_boot_run;self.movie_exit=self.lib.biwn_gpu_movie_exit_run
        for fn in [self.main_boot,self.movie_exit]:fn.argtypes=[c.POINTER(Bus),c.POINTER(video.State),c.c_uint32];fn.restype=c.c_int
        self.control5=self.lib.biwn_gpu_movie_exit_CPU_control5;self.control5.argtypes=[c.POINTER(Bus),c.POINTER(video.State)];self.control5.restype=c.c_int
        self.core.GPUWriteWord.argtypes=[c.c_uint32,c.c_uint16,c.c_uint32]
        def observer(_,pc):self.gpu_trace.update(struct.pack('>I',pc));self.gpu_blocks+=1
        self.boot_callbacks=[video.R16(lambda _,a,v:(v.__setitem__(0,self.core.GPUReadWord(a,3)),0)[1]),video.R32(lambda _,a,v:(v.__setitem__(0,self.core.GPUReadLong(a,3)),0)[1]),W16(lambda _,a,v:(self.core.GPUWriteWord(a,v,3),0)[1]),video.W32(lambda _,a,v:(self.core.GPUWriteLong(a,v,3),0)[1]),video.OBS(observer)]
        self.boot_bus=Bus(*self.boot_callbacks,None)
    def write(self,a,w,v):
        if self.mode=='C' and self.gpu is not None and a==0xf02114 and w==4 and v==5:
            # Native GPU shadow never receives the forcedIRQ request. Own
            # state performs the event and pushes the realGPU frame.
            self.observe(1,a,w,v);self.writers[w](a,v&~4)
            assert self.control5(c.byref(self.boot_bus),c.byref(self.gpu))==0
            c.memmove(self.core.GPUGetRAM(),bytes(self.gpu.local_RAM),4096)
            return
        return super().write(a,w,v)
    def run_boot_exit(self,kind):
        self.gpu_trace=hashlib.sha256();self.gpu_blocks=0;old=self.gpu_counter.value
        if self.mode=='native':
            code=c.string_at(self.core.GPUGetRAM(),4096);delays=0
            for _ in range(100):
                pc=self.core.GPUGetPC()
                if pc==0xf031be:break
                word=int.from_bytes(code[pc-0xf03000:pc-0xf03000+2],'big');self.gpu_trace.update(struct.pack('>I',pc));self.gpu_blocks+=1;self.core.GPUExec(1)
                if word>>10 in [52,53] and self.core.GPUGetPC()!=pc+2:delays+=1
            else:raise AssertionError(('Native boot/exit bound',hex(pc)))
            raw=video.gpu_state(self.core)[0][:4396];instructions=self.gpu_blocks+delays
        else:
            begin=self.gpu.instructions;assert (self.main_boot if kind=='main_boot' else self.movie_exit)(c.byref(self.boot_bus),c.byref(self.gpu),100)==0
            assert self.gpu_counter.value==old;raw=video.logical(self.gpu);instructions=self.gpu.instructions-begin;c.memmove(self.core.GPUGetRAM(),bytes(self.gpu.local_RAM),4096)
        self.gpu_calls.append(dict(program=kind,blocks=self.gpu_blocks,instructions=instructions,PC_sha256=self.gpu_trace.hexdigest(),logical_GPU_sha256=sha(raw)))
    def start(self,ram,seed,mode):
        self.C_DSP=None;self.pending_overlay=False;video.Runtime.start(self,ram,seed,mode);self.queries=[];self.progress=0x1c0000;self.timer_arm=False;self.timer_reads=0;self.deliveries=[]
        s=media.CPU();s.registers[15]=0x1fe000;s.usp=0x1fe000;s.ssp=0x1ff000;s.pc=0xe840;s.sr=0x700;self.device.direct(s.registers[15],4,controller.STOP)
        assert self.fn(c.byref(self.bus),c.byref(s),self.callbacks[5],self.service,None,10000,0)==0
        for entry in [0xd340,0xe7aa]:self.call(entry,b'')
        # Exact159word mainGPU image/entry from sourceE00A; loader/BIOS
        # remain declared fixture providers, but its GPU initializer runs.
        resident=self.device.ram()[0x40a8:0x4324]
        assert len(resident)==636
        for off in range(0,636,4):self.write(0xf03000+off,4,int.from_bytes(resident[off:off+4],'big'))
        self.write(0xf02110,4,0xf03224);self.write(0xf02114,4,1)
        self.run_boot_exit('main_boot');self.run_dispatch(True)
        request=media.CPU();request.registers[15]=0x1ff000;request.ssp=0x1ff000;request.usp=0x1fe000;request.pc=0xd3c6;request.sr=0x2700;self.device.direct(request.registers[15],4,controller.STOP)
        request_result,_=self.run_native(request,self.native_coverage) if mode=='native' else self.run_C(request)
        assert (self.core.GPUGetPC() if mode=='native' else self.gpu.pc)==0xf032c8
        c.memset(self.device.pointer+0x1a0000,0,80640);self.device.direct(0xbd85c,2,0)
        if mode=='C':self.C_DSP=AV.dsp.state_from_raw(self.raw_DSP())
        self.boot_count=self.segment();self.boot_hash=sha(self.logical_DSP());self.overlay_start=dict(CPU=media.scheduler.cpu_dict(request_result),GPU_calls=list(self.gpu_calls),RAM=sha(self.device.ram()),hardware=self.snapshot()['hardware'])

def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    mappings=[json.loads((session/n).read_text()) for n in ['movie-fullCPU-generation.json','video-fullCPU-generation.json','media-setup-fullCPU-generation.json']]
    poll=controller.movie.generator.loader.base.binary_tools.m68k_instructions((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()[0xe4c0:0xe53c],0xe4c0)[0]
    geometry=json.loads((session/'geometry-records-fullCPU-generation.json').read_text())
    rows=sum([m['instructions_decoded'] for m in mappings],[])+poll+[x for x in geometry['instructions_decoded'] if 0xe098<=x['address']<0xe0a6]
    out=ROOT/'verification/BIWN-movie-boot-exit-AV'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    src=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libcontroller-AV.dylib'
    names=['biwn_movie_cpu.c','biwn_video_cpu.c','biwn_movie_relocation_GPU.c','biwn_movie_sequence_GPU.c','biwn_media_setup_cpu.c','biwn_input_poll_cpu.c','biwn_dsp_media_audio.c','biwn_geometry_records_cpu.c','biwn_gpu_dispatcher.c','biwn_gpu_main_boot.c','biwn_gpu_movie_exit.c']
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
                    pairs,states=runtime.sound(128)
                    stages.append(dict(sample=sample,before_sound=before,word_clocks=128,PCM_sha256=sha(b''.join(struct.pack('<hh',*p) for p in pairs)),sound_states=states))
                # SourceD3EC control5 causes the ownGPU IRQ0 frame, source
                # handler acknowledges/releases it, dispatcher reachesidle.
                exit_request=media.CPU.from_buffer_copy(bytes(initial));exit_request.pc=0xd3ec;runtime.device.direct(exit_request.registers[15],4,controller.STOP);begin=len(runtime.gpu_calls)
                exit_cpu,_=runtime.run_native(exit_request,coverage) if mode=='native' else runtime.run_C(exit_request)
                entered=dict(CPU=media.scheduler.cpu_dict(exit_cpu),RAM=sha(runtime.device.ram()),hardware=runtime.snapshot()['hardware'])
                runtime.run_boot_exit('movie_exit');runtime.run_dispatch(True)
                exit_stage=dict(IRQ_entered=entered,RAM=sha(runtime.device.ram()),hardware=runtime.snapshot()['hardware'],GPU_calls=runtime.gpu_calls[begin:])
                if mode=='C':assert runtime.gpu_counter.value==counter and runtime.counter.value==DSP_counter and runtime.C_original_CPU_attempts==0
                snapshots[mode]=dict(overlay_start=runtime.overlay_start,boot=[runtime.boot_count,runtime.boot_hash],parser=[{k:p[k] for k in ['state','CPU','RAM','hardware']} for p in parsed['phases']],stages=stages,queries=runtime.queries,exit=exit_stage)
            if snapshots['native']!=snapshots['C']:save(out/'mismatch.json',snapshots);raise AssertionError(str(out/'mismatch.json'))
            results.append(dict(message_id=m['message_id'],snapshot=snapshots['C'],original_CPU_GPU_DSP_instructions_on_C_path=0));save(out/'fixtures.json',results);print(json.dumps(dict(message=m['message_id'],status='match')),flush=True)
        report=dict(status='source_GPU_boot_movie_start_first_cluster_AV_D3EC_IRQ0_exit_C_native_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),messages=len(results),video_frames=12,source_sample_dispatches=24,word_clocks=3072,
            CPU_source_coverage={name:[len(coverage&set(x['address'] for x in m['instructions_decoded'])),m['instructions']] for name,m in zip(['movie','video','media_setup'],mappings)},native_PC_coverage=sorted(coverage),source_sha256={n:sha((src/n).read_bytes()) for n in names},script_sha256=sha(Path(__file__).read_bytes()),
            original_CPU_GPU_DSP_instructions_on_C_path=False,whole_game_complete=False,source_D3C6_E098_and_GPU_dispatcher_executed=True,direct_host_movie_payload_reload=False,C_mainGPU_initializer_and_IRQ0_exit=True,source_D3EC_executed=True,
            limits=['First cluster per six movies; two audio and two video samples each. Host128KBdelivery, declared BIOS seek/progress/timer and source159wordmainGPU payload/entry fixture; no firmware or streaming/ringwrap proof.',
                    '128declaredSSI/word clocks after each sample, fullDSP8496/RAM/DAC/counts/PCM perclock; no physical A/V synchronization or full audio-chunk playback.',
                    'FullCPU/2MBRAM/logicalGPU4396/logicalDSP8496/peripherals/GPUtrace+counts percontrollerdispatch. Microstates excluded. Source STOP/GPUIRQ/RTE retained in nestedCproviders.',
                    'D3C6/E098 and sourceGPUdispatcher copy/start the movie overlay; CmainGPUinitializer/IRQ0handler and sourceD3EC exit nowrun; CPUloader/BIOS3000 remain fixtureproviders, fullCPUboot/BIOS3000/D3FC/directTRAP0/globalscheduler/livegameplay remain separate. Registry139 unchanged; no newtraining.'])
        save(out/'report.json',report);save(ROOT/'verification/BIWN-movie-boot-exit-AV.json',report);save(out/'status.json',dict(status='terminal_pass'));print(json.dumps(dict(directory=str(out),messages=len(results),video_frames=12,word_clocks=3072)))
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:runtime.oracle.close()
if __name__=='__main__':main()
