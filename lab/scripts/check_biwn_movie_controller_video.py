"""Source movie state controller calls C video providers and C GPU.

Mastered 128KB delivery and clock/progress are declared fixture events.
CPU provider retains each real source JSR frame through STOP/IRQ/RTE.
No original CPU/GPU runs on the C side. First cluster per six movies.
"""
import ctypes as c,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_full_video_cpu_gpu as video
import check_biwn_movie_cpu as movie
from check_biwn_68000_slices import make_toc
from extract_biwn_stage import swap16
media=video.media;ROOT=video.ROOT;save=video.save;sha=video.sha;STOP=video.STOP

class Runtime(video.Runtime):
    def __init__(self,library,rows,movie_rows,video_rows,setup_rows):
        super().__init__(library,rows)
        self.movie_rows=set(x['address'] for x in movie_rows);self.video_rows=set(x['address'] for x in video_rows);self.setup_rows=set(x['address'] for x in setup_rows)
        self.movie_call=self.lib.biwn_movie_cpu_call;self.movie_body=self.lib.biwn_movie_cpu_body
        for fn in [self.movie_call,self.movie_body]:fn.argtypes=self.fn.argtypes;fn.restype=c.c_int
        self.poll=self.lib.biwn_input_poll_cpu_body;self.poll.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU)];self.poll.restype=c.c_int
        self.queries=[];self.timer_arm=False;self.timer_reads=0;self.progress=0x1c0000;self.deliveries=[]
        def service(_,bus,cpu,target):
            try:
                if target in [0x303c,0x304e]:self.bios(cpu.contents,target);return 0
                if target==0xe4c0:return self.poll(bus,cpu)
                if target in self.movie_rows:return self.movie_body(bus,cpu,self.callbacks[5],self.service,None,200000,1)
                if target in self.setup_rows:return self.body(bus,cpu,self.callbacks[5],self.service,None,200000,1)
                if target in self.video_rows:
                    saved=self.C_CPU;self.C_CPU=cpu.contents
                    try:
                        for _ in range(100):
                            status=self.body_video(bus,cpu,self.callbacks[5],self.service,None,1000000,1)
                            if status==6:
                                assert cpu.contents.pc==0x22a0e
                                assert self.stop(cpu)==0;self.C_stopped=True;self.run_C_GPU(False)
                                assert not self.C_stopped and cpu.contents.pc==0xe7d4
                                continue
                            if status:return status
                            # RTE returns to STOP continuation before its RTS.
                            if cpu.contents.pc==0x22a12:continue
                            return 0
                        raise AssertionError('Video provider continuation bound')
                    finally:self.C_CPU=saved
                raise AssertionError('Unimplemented controller provider '+hex(target))
            except Exception as e:self.errors.append(repr(e));return 1
        self.service=media.world_cpu.SERVICE(service)
        self.core.DSPReadLong.argtypes=[c.c_uint32,c.c_uint32];self.core.DSPReadLong.restype=c.c_uint32
    bios=movie.Runtime.bios
    sequence=movie.Runtime.sequence
    def read(self,a,w):
        if self.mode=='C' and a==0xbd852 and w==4 and self.timer_arm:
            self.timer_reads+=1
            if self.timer_reads==3:self.device.direct(a,4,1)
        return super().read(a,w)
    def snapshot(self):
        result=super().snapshot()
        if self.mode=='C' and self.gpu is not None:result['hardware']['GPU']=dict(size=4396,sha256=sha(video.logical(self.gpu)))
        elif self.mode=='native':result['hardware']['GPU']=dict(size=4396,sha256=sha(video.gpu_state(self.core)[0][:4396]))
        return result
    def start(self,ram,seed,mode):
        super().start(ram,seed,mode);self.queries=[];self.progress=0x1c0000;self.timer_arm=False;self.timer_reads=0;self.deliveries=[]
        # Same accepted C media loader initializes both fixture paths.
        s=media.CPU();s.registers[15]=0x1fe000;s.usp=0x1fe000;s.ssp=0x1ff000;s.pc=0xe840;s.sr=0x700;self.device.direct(s.registers[15],4,STOP)
        assert self.fn(c.byref(self.bus),c.byref(s),self.callbacks[5],self.service,None,10000,0)==0
        for entry in [0xd340,0xe7aa]:self.call(entry,b'')
        # Source resident overlay dispatcher is not yet connected.
        payload=self.device.ram()[0x21ea8:0x22770];c.memmove(self.core.GPUGetRAM()+0x240,payload,len(payload))
        self.core.GPUWriteLong(0xf02110,0xf03240,6);self.core.GPUWriteLong(0xf02114,1,6)
        if mode=='C':self.gpu.local_RAM[0x240:0x240+len(payload)]=payload;self.gpu.pc=0xf03240;self.gpu.control|=1;self.run_C_GPU(True)
        else:self.native_GPU(True)
        c.memset(self.device.pointer+0x1a0000,0,80640)
        # Movie request starts state0 after the source loader's idleFFFF.
        self.device.direct(0xbd85c,2,0)
    def run_native(self,s,coverage):
        self.seed_cpu(s);steps=0
        for _ in range(1000000):
            pc=self.core.m68k_get_reg(None,16)
            if pc==STOP:return self.cpu(),steps
            if pc in [0x303c,0x304e]:
                state=self.cpu();self.bios(state,pc);self.core.m68k_set_reg(8,state.registers[8]);old=self.device.read(pc,2);self.device.direct(pc,2,0x4e75)
                self.core.m68k_execute(1);self.device.direct(pc,2,old)
            else:
                assert pc in self.rows,hex(pc);coverage.add(pc)
                if self.timer_arm and pc in [0xd7bc,0xd7c2]:
                    self.timer_reads+=1
                    if self.timer_reads==3:self.device.direct(0xbd852,4,1)
                if pc==0x22a0e:self.core.m68k_execute(1);steps+=1;self.native_GPU(False);continue
                self.core.m68k_execute(1)
            steps+=1
        raise AssertionError(('Native controller bound',hex(pc)))
    def run_C(self,s):
        old=self.C_CPU;self.C_CPU=s
        try:
            status=self.movie_call(c.byref(self.bus),c.byref(s),self.callbacks[5],self.service,None,1000000,1)
            assert status==0,(status,hex(s.pc),self.errors)
            return s,None
        finally:self.C_CPU=old

def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    mappings=[json.loads((session/n).read_text()) for n in ['movie-fullCPU-generation.json','video-fullCPU-generation.json','media-setup-fullCPU-generation.json']]
    poll=movie.generator.loader.base.binary_tools.m68k_instructions((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()[0xe4c0:0xe53c],0xe4c0)[0]
    rows=sum([m['instructions_decoded'] for m in mappings],[])+poll
    out=ROOT/'verification/BIWN-movie-controller-video'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    src=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libcontroller-video.dylib'
    names=['biwn_movie_cpu.c','biwn_video_cpu.c','biwn_movie_relocation_GPU.c','biwn_movie_sequence_GPU.c','biwn_media_setup_cpu.c','biwn_input_poll_cpu.c']
    cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(src/n) for n in names],'-o',str(library)]
    built=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
    runtime=Runtime(library,rows,*[m['instructions_decoded'] for m in mappings]);results=[];coverage=set()
    extraction=json.loads((ROOT/'verification/BIWN-dialogue-audio-extraction.json').read_text());markers={x['message_id']:int(x['source_long_fields'][2],16) for x in json.loads((ROOT/'verification/NPC-message-video-dependency-inspection.json').read_text())['message_records']}
    base=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());base[0x21ea8:0x22770]=(session/'media-video-gpu-21ea0/original-overlay.bin').read_bytes();toc=make_toc(json.loads((session/'cdi-layout.json').read_text()));base[0x2c00:0x2c00+len(toc)]=toc
    try:
        for case,m in enumerate(extraction['messages']):
            with (session/'raw-tracks/track-04-raw.bin').open('rb') as f:f.seek(m['FILM_normalized_track_offset']-64);data=swap16(f.read(0x20000))
            audio=Path(m['first_chunk_path']).read_bytes();message={**m,'stream_fixture':data,'first_audio_length':len(audio),'first_audio_data':audio}
            initial=media.CPU();initial.registers[:]=[0]*15+[0x1ff000];initial.usp=0x1fe000;initial.ssp=0x1ff000;initial.sr=0x2700
            ram=bytearray(base)
            for a,v in [(0xbd884,0x1c0000),(0xbd888,0x1ffc00),(0xbd890,3),(0xbd894,m['message_offset']),(0xbd8ac,markers[m['message_id']]),(0xbd880,0x802000),(0xbd852,0),(0x47b84,0x22002000),(0xbd88c,0x1a0000),(0xbd900,448)]:ram[a:a+4]=v.to_bytes(4,'big')
            ram[0xbd85c:0xbd85e]=bytes(2);snapshots={}
            for mode in ['native','C']:
                save(out/'status.json',dict(status='running',message=m['message_id'],mode=mode))
                try:parsed,_=runtime.sequence(bytes(ram),message,initial,case%3,mode,coverage)
                except Exception:
                    save(out/'parser-failure.json',dict(mode=mode,message=m['message_id'],state=runtime.device.read(0xbd85c,2),length=runtime.core.DSPReadLong(0xf1b138,6),pointer=runtime.core.DSPReadLong(0xf1b13c,6),expected=len(audio),queries=runtime.queries,errors=runtime.errors));print((out/'parser-failure.json').read_text());raise
                stages=[];count=runtime.gpu_counter.value
                # Sequence consumed sample0 audio. Drive the remaining three
                # first-cluster samples through source D4A8/D896 itself.
                for sample,timer in [(1,0),(2,0),(3,40)]:
                    runtime.device.direct(0xbd852,4,timer);s=media.CPU.from_buffer_copy(bytes(initial));s.pc=0xd4a8;runtime.device.direct(s.registers[15],4,STOP)
                    begin=len(runtime.gpu_calls)
                    cpu,steps=runtime.run_native(s,coverage) if mode=='native' else runtime.run_C(s)
                    stages.append(dict(sample=sample,CPU=media.scheduler.cpu_dict(cpu),RAM=sha(runtime.device.ram()),hardware=runtime.snapshot()['hardware'],GPU_calls=runtime.gpu_calls[begin:],movie_state=runtime.device.read(0xbd85c,2)))
                if mode=='C':assert runtime.gpu_counter.value==count and runtime.C_original_CPU_attempts==0
                snapshots[mode]=dict(parser=[{k:p[k] for k in ['state','CPU','RAM','hardware']} for p in parsed['phases']],stages=stages,queries=runtime.queries)
            if snapshots['native']!=snapshots['C']:
                save(out/'mismatch.json',snapshots);raise AssertionError(str(out/'mismatch.json'))
            results.append(dict(message_id=m['message_id'],snapshots=snapshots['C'],original_CPU_GPU_instructions_on_C_path=0));save(out/'fixtures.json',results)
            print(json.dumps(dict(message=m['message_id'],status='match')),flush=True)
        report=dict(status='source_movie_controller_first_cluster_audio_and_two_video_samples_C_native_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),messages=len(results),video_frames=12,source_sample_dispatches=24,
            CPU_source_coverage={name:[len(coverage&set(x['address'] for x in m['instructions_decoded'])),m['instructions']] for name,m in zip(['movie','video','media_setup'],mappings)},native_PC_coverage=sorted(coverage),
            source_sha256={n:sha((src/n).read_bytes()) for n in names},script_sha256=sha(Path(__file__).read_bytes()),original_CPU_GPU_instructions_on_C_path=False,
            whole_game_complete=False,limits=['First cluster only; actual 128KB host disc delivery and declared progress/timer providers. No disc firmware or ring wrap proof.',
                'Source D4A8/D896 chooses sample addresses, mode/pitch/destination, advances sample table. STOP/GPUIRQ/RTE nested providers retain frames.',
                'DSP audio enqueue only; no audio engine/clocks/synchronization. Overlay reload is host event, D3C6 not integrated; no global scheduling/physical playback.'])
        save(out/'report.json',report);save(ROOT/'verification/BIWN-movie-controller-video.json',report);save(out/'status.json',dict(status='terminal_pass'));print(json.dumps(dict(directory=str(out),messages=len(results),video_frames=12)))
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:runtime.oracle.close()
if __name__=='__main__':main()
