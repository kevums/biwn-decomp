"""First source movie clusters drive reconstructed CPU/GPU/DSP together.

Controlled host disc delivery, overlay restart and SSI clocks remain declared.
No claim of firmware streaming, complete movie or physical A/V timing.
"""
import ctypes as c,json,os,struct,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_movie_controller_video as controller
import check_biwn_movie_audio_integration as audio
import check_biwn_dsp_media_audio as dsp
ROOT=controller.ROOT;save=controller.save;sha=controller.sha;media=controller.media

class Runtime(controller.Runtime):
    def __init__(self,*args):
        super().__init__(*args)
        self.dsp_run=self.lib.biwn_dsp_media_audio_run;self.dsp_run.argtypes=[c.POINTER(dsp.Bus),c.POINTER(dsp.State),c.c_uint32];self.dsp_run.restype=c.c_int
        self.dsp_irq=self.lib.biwn_dsp_media_audio_ssi_interrupt;self.dsp_irq.argtypes=[c.POINTER(dsp.State)];self.dsp_irq.restype=c.c_int
        self.core.DSPExec.argtypes=[c.c_int32];self.core.DSPWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];self.core.DSPSetIRQLine.argtypes=[c.c_int,c.c_int];self.core.DACWordStrobe.argtypes=[]
        self.counter=c.c_uint32.in_dll(self.core,'dsp_exec_opcode_count');self.C_DSP=None
        self.dsp_callbacks=[dsp.R8(lambda _,a,out:self.external_read8(a,out)),dsp.R32(lambda _,a,out:self.external_read32(a,out)),dsp.W32(lambda _,a,v:self.external_write32(a,v)),dsp.OBS()]
        self.dsp_bus=dsp.Bus(*self.dsp_callbacks,None)
    external_read8=audio.Runtime.external_read8
    external_read32=audio.Runtime.external_read32
    external_write32=audio.Runtime.external_write32
    raw_DSP=audio.Runtime.raw_DSP
    dac=audio.Runtime.dac
    idle_native=audio.Runtime.idle_native
    segment=audio.Runtime.segment
    logical_DSP=audio.Runtime.logical_DSP
    sound=audio.Runtime.sound
    def snapshot(self):
        result=super().snapshot()
        if self.mode=='native' or self.C_DSP is not None:result['hardware']['DSP']=dict(size=8496,sha256=sha(self.logical_DSP()))
        return result
    def write(self,a,w,v):
        super().write(a,w,v)
        if self.mode=='C' and self.C_DSP is not None and 0xf1b000<=a<=0xf1d000-w:self.C_DSP.local_RAM[a-0xf1b000:a-0xf1b000+w]=v.to_bytes(w,'big')
    def read(self,a,w):
        if self.mode=='C' and self.C_DSP is not None and 0xf1b000<=a<=0xf1d000-w:
            value=int.from_bytes(bytes(self.C_DSP.local_RAM[a-0xf1b000:a-0xf1b000+w]),'big');self.observe(0,a,w,value);return value
        return super().read(a,w)
    def start(self,ram,seed,mode):
        self.C_DSP=None;super().start(ram,seed,mode)
        if mode=='C':self.C_DSP=dsp.state_from_raw(self.raw_DSP())
        self.boot_count=self.segment();self.boot_hash=sha(self.logical_DSP())

def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    mappings=[json.loads((session/n).read_text()) for n in ['movie-fullCPU-generation.json','video-fullCPU-generation.json','media-setup-fullCPU-generation.json']]
    poll=controller.movie.generator.loader.base.binary_tools.m68k_instructions((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()[0xe4c0:0xe53c],0xe4c0)[0]
    rows=sum([m['instructions_decoded'] for m in mappings],[])+poll
    out=ROOT/'verification/BIWN-movie-controller-AV'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    src=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libcontroller-AV.dylib'
    names=['biwn_movie_cpu.c','biwn_video_cpu.c','biwn_movie_relocation_GPU.c','biwn_movie_sequence_GPU.c','biwn_media_setup_cpu.c','biwn_input_poll_cpu.c','biwn_dsp_media_audio.c']
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
                snapshots[mode]=dict(boot=[runtime.boot_count,runtime.boot_hash],parser=[{k:p[k] for k in ['state','CPU','RAM','hardware']} for p in parsed['phases']],stages=stages,queries=runtime.queries)
            if snapshots['native']!=snapshots['C']:save(out/'mismatch.json',snapshots);raise AssertionError(str(out/'mismatch.json'))
            results.append(dict(message_id=m['message_id'],snapshot=snapshots['C'],original_CPU_GPU_DSP_instructions_on_C_path=0));save(out/'fixtures.json',results);print(json.dumps(dict(message=m['message_id'],status='match')),flush=True)
        report=dict(status='source_controller_first_cluster_CPU_GPU_DSP_C_native_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),messages=len(results),video_frames=12,source_sample_dispatches=24,word_clocks=3072,
            CPU_source_coverage={name:[len(coverage&set(x['address'] for x in m['instructions_decoded'])),m['instructions']] for name,m in zip(['movie','video','media_setup'],mappings)},native_PC_coverage=sorted(coverage),source_sha256={n:sha((src/n).read_bytes()) for n in names},script_sha256=sha(Path(__file__).read_bytes()),
            original_CPU_GPU_DSP_instructions_on_C_path=False,whole_game_complete=False,
            limits=['First cluster per six movies; two audio and two video samples each. Host128KBdelivery, declared BIOS seek/progress/timer and overlay reload; no firmware or streaming/ringwrap proof.',
                    '128declaredSSI/word clocks after each sample, fullDSP8496/RAM/DAC/counts/PCM perclock; no physical A/V synchronization or full audio-chunk playback.',
                    'FullCPU/2MBRAM/logicalGPU4396/logicalDSP8496/peripherals/GPUtrace+counts percontrollerdispatch. Microstates excluded. Source STOP/GPUIRQ/RTE retained in nestedCproviders.',
                    'Movie caller D3FC/directTRAP0/residentD3C6/globalscheduler/livegameplay remain separate; registry139 unchanged. Coordinator-authored, no new training.'])
        save(out/'report.json',report);save(ROOT/'verification/BIWN-movie-controller-AV.json',report);save(out/'status.json',dict(status='terminal_pass'));print(json.dumps(dict(directory=str(out),messages=len(results),video_frames=12,word_clocks=3072)))
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:runtime.oracle.close()
if __name__=='__main__':main()
