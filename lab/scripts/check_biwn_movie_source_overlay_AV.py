"""Source D3C6/E098 and C GPU dispatcher load movie overlay before controller A/V.

Fixture establishes the source resident dispatcher at idle; full GPU boot is
separate. Source CPU publishes21EA0; actual dispatcher copies its562words,
then source GPU header starts decoder. No direct host payload reload.
"""
import ctypes as c,json,hashlib,struct
from pathlib import Path
import check_biwn_movie_controller_AV as AV
import check_biwn_movie_controller_video as controller
import check_biwn_full_video_cpu_gpu as video
import check_biwn_gpu_dispatcher as dispatcher
from datetime import datetime,timezone
import os,subprocess
ROOT=AV.ROOT;save=AV.save;sha=AV.sha;media=AV.media
class Runtime(AV.Runtime):
    def __init__(self,*args):
        super().__init__(*args)
        self.geometry_body=self.lib.biwn_geometry_records_cpu_body;self.geometry_body.argtypes=self.fn.argtypes;self.geometry_body.restype=c.c_int
        self.dispatch=self.lib.biwn_gpu_dispatcher_run;self.dispatch.argtypes=[c.POINTER(dispatcher.Bus),c.POINTER(dispatcher.State),c.c_uint32,c.c_uint32];self.dispatch.restype=c.c_int
        self.pending_overlay=False;self.dispatch_trace=hashlib.sha256();self.dispatch_blocks=0
        self.saved_service=self.service
        def service(_,bus,cpu,target):
            if target==0xe098:return self.geometry_body(bus,cpu,self.callbacks[5],self.service,None,10000,1)
            return self.saved_service(_,bus,cpu,target)
        self.service=media.world_cpu.SERVICE(service)
        def read32(_,a,out):
            if 0xf03000<=a<=0xf03ffc:out[0]=int.from_bytes(bytes(self.gpu.local_RAM[a-0xf03000:a-0xf03000+4]),'big')
            else:out[0]=self.core.GPUReadLong(a,3)
            return 0
        def write32(_,a,v):
            self.core.GPUWriteLong(a,v,3)
            if 0xf03000<=a<=0xf03ffc:self.gpu.local_RAM[a-0xf03000:a-0xf03000+4]=v.to_bytes(4,'big')
            return 0
        def observe(_,pc,z,carry,n):self.dispatch_trace.update(struct.pack('>I',pc));self.dispatch_blocks+=1
        self.dispatch_callbacks=[dispatcher.R32(read32),dispatcher.W32(write32),dispatcher.TRACE(observe)];self.dispatch_bus=dispatcher.Bus(*self.dispatch_callbacks,None)
    def read(self,a,w):
        if self.mode=='C' and self.pending_overlay and a==0xf03204:
            self.run_dispatch(False);assert self.gpu.pc==0xf03240;self.run_C_GPU(True);self.pending_overlay=False
        return super().read(a,w)
    def write(self,a,w,v):
        super().write(a,w,v)
        if self.mode=='C' and a==0xf03204 and w==4 and v==0x21ea0:self.pending_overlay=True
    def run_dispatch(self,idle):
        self.dispatch_trace=hashlib.sha256();self.dispatch_blocks=0
        if self.mode=='native':
            code=c.string_at(self.core.GPUGetRAM(),4096);delays=0
            for _ in range(10000):
                pc=self.core.GPUGetPC()
                if not(0xf031be<=pc<0xf03200) or (idle and pc==0xf031ce and self.core.GPUReadLong(0xf03204,6)==0xffffffff and self.core.GPUReadLong(0xf03200,6)==0):break
                self.dispatch_trace.update(struct.pack('>I',pc));self.dispatch_blocks+=1;word=int.from_bytes(code[pc-0xf03000:pc-0xf03000+2],'big');self.core.GPUExec(1)
                if word>>10 in [52,53] and self.core.GPUGetPC()!=pc+2:delays+=1
            else:raise AssertionError('Native resident dispatcher bound')
            instructions=self.dispatch_blocks+delays;raw=video.gpu_state(self.core)[0][:4396]
        else:
            count=self.gpu_counter.value;s=dispatcher.State();s.registers[:]=self.gpu.registers
            for field in ['pc','z','c','n']:setattr(s,field,getattr(self.gpu,field))
            assert self.dispatch(c.byref(self.dispatch_bus),c.byref(s),10000,int(idle))==0
            self.gpu.registers[:]=s.registers
            for field in ['pc','z','c','n']:setattr(self.gpu,field,getattr(s,field))
            self.gpu.instructions+=s.instructions;instructions=s.instructions;raw=video.logical(self.gpu);assert self.gpu_counter.value==count
        self.gpu_calls.append(dict(resident_dispatcher=True,idle=idle,blocks=self.dispatch_blocks,PC_sha256=self.dispatch_trace.hexdigest(),instructions=instructions,logical_GPU_sha256=sha(raw)))
    def start(self,ram,seed,mode):
        self.C_DSP=None;self.pending_overlay=False;video.Runtime.start(self,ram,seed,mode);self.queries=[];self.progress=0x1c0000;self.timer_arm=False;self.timer_reads=0;self.deliveries=[]
        s=media.CPU();s.registers[15]=0x1fe000;s.usp=0x1fe000;s.ssp=0x1ff000;s.pc=0xe840;s.sr=0x700;self.device.direct(s.registers[15],4,controller.STOP)
        assert self.fn(c.byref(self.bus),c.byref(s),self.callbacks[5],self.service,None,10000,0)==0
        for entry in [0xd340,0xe7aa]:self.call(entry,b'')
        resident=self.device.ram()[0x40a8:0x42a8]
        assert sha(resident[0x1be:0x200])=='5d07965cfc182ea1614da0a176e242312d934a414d46959d5a286c702b1ddf0d'
        # Declared initial resident GPU context, not reconstructed full boot.
        for off in range(0,512,4):self.write(0xf03000+off,4,int.from_bytes(resident[off:off+4],'big'))
        for a,v in [(0xf03200,0x12345678),(0xf03204,0xffffffff),(0xf03208,0x52e0),(0xf02110,0xf031be),(0xf02114,0x2801)]:self.write(a,4,v)
        self.run_dispatch(True)
        request=media.CPU();request.registers[15]=0x1ff000;request.ssp=0x1ff000;request.usp=0x1fe000;request.pc=0xd3c6;request.sr=0x2700;self.device.direct(request.registers[15],4,controller.STOP)
        request_result,_=self.run_native(request,self.native_coverage) if mode=='native' else self.run_C(request)
        assert (self.core.GPUGetPC() if mode=='native' else self.gpu.pc)==0xf032c8
        c.memset(self.device.pointer+0x1a0000,0,80640);self.device.direct(0xbd85c,2,0)
        if mode=='C':self.C_DSP=AV.dsp.state_from_raw(self.raw_DSP())
        self.boot_count=self.segment();self.boot_hash=sha(self.logical_DSP());self.overlay_start=dict(CPU=media.scheduler.cpu_dict(request_result),GPU_calls=list(self.gpu_calls),RAM=sha(self.device.ram()),hardware=self.snapshot()['hardware'])
    def run_native(self,s,coverage):
        self.seed_cpu(s);steps=0
        for _ in range(1000000):
            pc=self.core.m68k_get_reg(None,16)
            if pc==controller.STOP:return self.cpu(),steps
            if pc in [0x303c,0x304e]:
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
    rows=sum([m['instructions_decoded'] for m in mappings],[])+poll+[x for x in geometry['instructions_decoded'] if 0xe098<=x['address']<0xe0a6]
    out=ROOT/'verification/BIWN-movie-source-overlay-AV'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    src=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libcontroller-AV.dylib'
    names=['biwn_movie_cpu.c','biwn_video_cpu.c','biwn_movie_relocation_GPU.c','biwn_movie_sequence_GPU.c','biwn_media_setup_cpu.c','biwn_input_poll_cpu.c','biwn_dsp_media_audio.c','biwn_geometry_records_cpu.c','biwn_gpu_dispatcher.c']
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
                if mode=='C':assert runtime.gpu_counter.value==counter and runtime.counter.value==DSP_counter and runtime.C_original_CPU_attempts==0
                snapshots[mode]=dict(overlay_start=runtime.overlay_start,boot=[runtime.boot_count,runtime.boot_hash],parser=[{k:p[k] for k in ['state','CPU','RAM','hardware']} for p in parsed['phases']],stages=stages,queries=runtime.queries)
            if snapshots['native']!=snapshots['C']:save(out/'mismatch.json',snapshots);raise AssertionError(str(out/'mismatch.json'))
            results.append(dict(message_id=m['message_id'],snapshot=snapshots['C'],original_CPU_GPU_DSP_instructions_on_C_path=0));save(out/'fixtures.json',results);print(json.dumps(dict(message=m['message_id'],status='match')),flush=True)
        report=dict(status='source_D3C6_E098_dispatcher_movie_overlay_and_first_cluster_AV_C_native_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),messages=len(results),video_frames=12,source_sample_dispatches=24,word_clocks=3072,
            CPU_source_coverage={name:[len(coverage&set(x['address'] for x in m['instructions_decoded'])),m['instructions']] for name,m in zip(['movie','video','media_setup'],mappings)},native_PC_coverage=sorted(coverage),source_sha256={n:sha((src/n).read_bytes()) for n in names},script_sha256=sha(Path(__file__).read_bytes()),
            original_CPU_GPU_DSP_instructions_on_C_path=False,whole_game_complete=False,source_D3C6_E098_and_GPU_dispatcher_executed=True,direct_host_movie_payload_reload=False,
            limits=['First cluster per six movies; two audio and two video samples each. Host128KBdelivery, declared BIOS seek/progress/timer and initial resident GPU context; no firmware or streaming/ringwrap proof.',
                    '128declaredSSI/word clocks after each sample, fullDSP8496/RAM/DAC/counts/PCM perclock; no physical A/V synchronization or full audio-chunk playback.',
                    'FullCPU/2MBRAM/logicalGPU4396/logicalDSP8496/peripherals/GPUtrace+counts percontrollerdispatch. Microstates excluded. Source STOP/GPUIRQ/RTE retained in nestedCproviders.',
                    'D3C6/E098 and sourceGPUdispatcher copy/start the movie overlay; initialresidentcontext is fixture, fullboot/D3FC/directTRAP0/globalscheduler/livegameplay remain separate. Registry139 unchanged; no newtraining.'])
        save(out/'report.json',report);save(ROOT/'verification/BIWN-movie-source-overlay-AV.json',report);save(out/'status.json',dict(status='terminal_pass'));print(json.dumps(dict(directory=str(out),messages=len(results),video_frames=12,word_clocks=3072)))
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:runtime.oracle.close()
if __name__=='__main__':main()
