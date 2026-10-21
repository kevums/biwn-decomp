"""Source movie CPU produces a real sample pointer for the C DSP engine.

DSP boots before movie parsing, retaining the source E840 increment already
loaded into R23. Header E8E2 writes its data field without editing R23.
Declared host disc deliveries/clock events remain separate from firmware.
"""
import ctypes as c
import json,struct,wave
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_movie_cpu as movie
import check_biwn_dsp_media_audio as dsp
from check_biwn_68000_slices import make_toc
from extract_biwn_stage import swap16
ROOT=movie.ROOT;save=movie.save;sha=movie.sha

class Runtime(movie.Runtime):
    def __init__(self,library,rows,dsp_library):
        super().__init__(library,rows)
        self.dsp_library=c.CDLL(str(dsp_library));self.dsp_run=self.dsp_library.biwn_dsp_media_audio_run
        self.dsp_run.argtypes=[c.POINTER(dsp.Bus),c.POINTER(dsp.State),c.c_uint32];self.dsp_run.restype=c.c_int
        self.dsp_irq=self.dsp_library.biwn_dsp_media_audio_ssi_interrupt;self.dsp_irq.argtypes=[c.POINTER(dsp.State)];self.dsp_irq.restype=c.c_int
        self.core.DSPExec.argtypes=[c.c_int32];self.core.DSPReadLong.argtypes=[c.c_uint32,c.c_uint32];self.core.DSPReadLong.restype=c.c_uint32
        self.core.DSPWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32]
        self.core.JaguarReadByte.argtypes=[c.c_uint32,c.c_uint32];self.core.JaguarReadByte.restype=c.c_uint8
        self.core.DSPSetIRQLine.argtypes=[c.c_int,c.c_int];self.core.DACWordStrobe.argtypes=[]
        self.counter=c.c_uint32.in_dll(self.core,'dsp_exec_opcode_count');self.C_DSP=None
        self.dsp_callbacks=[dsp.R8(lambda _,a,out:self.external_read8(a,out)),dsp.R32(lambda _,a,out:self.external_read32(a,out)),dsp.W32(lambda _,a,v:self.external_write32(a,v)),dsp.OBS()]
        self.dsp_bus=dsp.Bus(*self.dsp_callbacks,None)

    def external_read8(self,a,out):out[0]=self.core.JaguarReadByte(a,2);return 0
    def external_read32(self,a,out):out[0]=self.core.DSPReadLong(a,2);return 0
    def external_write32(self,a,v):self.core.DSPWriteLong(a,v,2);return 0
    def raw_DSP(self):
        raw=c.create_string_buffer(12000);size=self.savers['DSP'](raw);assert size==8729;return raw.raw[:size]
    def dac(self):
        raw=c.create_string_buffer(200000);size=self.savers['DAC'](raw);assert size==65587;return raw.raw[:size]
    def idle_native(self):
        s=dsp.state_from_raw(self.raw_DSP())
        return not(s.control&1) or (s.pc==0xf1b074 and s.registers[0][27]==0 and not(s.flags&8))
    def segment(self):
        before=self.counter.value
        if self.mode=='C':
            old=self.C_DSP.instructions
            assert self.dsp_run(c.byref(self.dsp_bus),c.byref(self.C_DSP),10000)==0
            assert self.counter.value==before
            return self.C_DSP.instructions-old
        for _ in range(10000):
            if self.idle_native():return (self.counter.value-before)&0xffffffff
            self.core.DSPExec(1)
        raise AssertionError('DSP segment bound')
    def logical_DSP(self):return dsp.logical(self.C_DSP) if self.mode=='C' else self.raw_DSP()[:8496]
    def snapshot(self):
        result=super().snapshot()
        if self.C_DSP is not None or self.mode=='native':
            # Deliberately scoped to logical DSP state: retained native
            # opcode/pipeline microstate is not a source C implementation.
            result['hardware']['DSP']=dict(bytes=8496,sha256=sha(self.logical_DSP()),scope='logical DSP state; microstate excluded')
        return result
    def write(self,a,w,v):
        super().write(a,w,v)
        if self.mode=='C' and self.C_DSP is not None and 0xf1b000<=a<=0xf1d000-w:
            self.C_DSP.local_RAM[a-0xf1b000:a-0xf1b000+w]=v.to_bytes(w,'big')
    def read(self,a,w):
        # CPU accesses to shared DSP RAM use the same C-owned byte array as
        # the sample engine. Do not copy/replace the E902 pointer afterward.
        if self.mode=='C' and self.C_DSP is not None and 0xf1b000<=a<=0xf1d000-w:
            value=int.from_bytes(bytes(self.C_DSP.local_RAM[a-0xf1b000:a-0xf1b000+w]),'big')
            self.observe(0,a,w,value);return value
        return super().read(a,w)
    def start(self,ram,seed,mode):
        self.C_DSP=None;super().start(ram,seed,mode)
        if mode=='C':self.C_DSP=dsp.state_from_raw(self.raw_DSP())
        self.boot_instructions=self.segment();self.boot_logical=sha(self.logical_DSP())
    def sound(self,ticks):
        pairs=[];states=[]
        for _ in range(ticks):
            self.core.DACWordStrobe();pairs.append(dsp.strobed_pair(self.dac()))
            if self.mode=='C':assert self.dsp_irq(c.byref(self.C_DSP))==0
            else:self.core.DSPSetIRQLine(1,1)
            instructions=self.segment()
            states.append(dict(DSP=sha(self.logical_DSP()),RAM=sha(self.device.ram()),DAC=sha(self.dac()),instructions=instructions))
        return pairs,states

def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    mapping=json.loads((session/'movie-fullCPU-generation.json').read_text());setup=json.loads((session/'media-setup-fullCPU-generation.json').read_text())
    poll=movie.generator.loader.base.binary_tools.m68k_instructions((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()[0xe4c0:0xe53c],0xe4c0)[0]
    source_proof=json.loads((ROOT/'verification/BIWN-movie-CPU.json').read_text());assert source_proof['source_sha256']==mapping['source_sha256']
    dsp_proof=json.loads((ROOT/'verification/biwn-dsp-media-audio-checks.json').read_text())
    runtime=Runtime(Path(source_proof['directory'])/'libmovie.dylib',mapping['instructions_decoded']+setup['instructions_decoded']+poll,Path(dsp_proof['directory'])/'libdsp-media-audio.dylib')
    out=ROOT/'verification/BIWN-movie-audio-integration'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    extraction=json.loads((ROOT/'verification/BIWN-dialogue-audio-extraction.json').read_text());markers={x['message_id']:int(x['source_long_fields'][2],16) for x in json.loads((ROOT/'verification/NPC-message-video-dependency-inspection.json').read_text())['message_records']}
    base=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();toc=make_toc(json.loads((session/'cdi-layout.json').read_text()));results=[]
    try:
        for case,m in enumerate(extraction['messages']):
            save(out/'status.json',dict(status='running',message=m['message_id']))
            with (session/'raw-tracks/track-04-raw.bin').open('rb') as f:f.seek(m['FILM_normalized_track_offset']-64);data=swap16(f.read(0x20000))
            audio=Path(m['first_chunk_path']).read_bytes();message={**m,'stream_fixture':data,'first_audio_length':len(audio),'first_audio_data':audio}
            initial=movie.CPU();initial.registers[:]=[0]*15+[0x1fe000];initial.usp=0x1fe000;initial.ssp=0x1ff000;initial.sr=0x700
            ram=bytearray(base);ram[0x2c00:0x2c00+len(toc)]=toc
            for a,v in [(0xbd884,0x1c0000),(0xbd888,0x1ffc00),(0xbd890,3),(0xbd894,m['message_offset']),(0xbd8ac,markers[m['message_id']]),(0xbd880,0x802000),(0xbd852,0),(0x47b84,0x22002000)]:ram[a:a+4]=v.to_bytes(4,'big')
            ram[0xbd85c:0xbd85e]=bytes(2);ram=bytes(ram);ticks=4096 if case==0 else 128
            native,left=runtime.sequence(ram,message,initial,case%3,'native',set());native_boot=(runtime.boot_instructions,runtime.boot_logical)
            original_before=dsp.state_from_raw(runtime.raw_DSP());native_logical=runtime.logical_DSP();pairs,states=runtime.sound(ticks)
            rebuilt,right=runtime.sequence(ram,message,initial,case%3,'C',set());C_before=runtime.C_DSP
            assert dsp.logical(C_before)==native_logical
            assert (runtime.boot_instructions,runtime.boot_logical)==native_boot
            assert C_before.registers[0][23]==original_before.registers[0][23]==0x0481db08
            assert int.from_bytes(bytes(C_before.local_RAM[0x144:0x148]),'big')==m['DSP_increment']
            assert left==right and native['queries']==rebuilt['queries']
            for a,b in zip(native['phases'],rebuilt['phases']):
                assert all(a[k]==b[k] for k in ['state','CPU','RAM','hardware']),('CPU integration phase',a['phase'])
            count=runtime.counter.value;c_pairs,c_states=runtime.sound(ticks)
            assert runtime.counter.value==count and c_pairs==pairs and c_states==states
            rate_hz=round(26590906/(64*(m['SCLK']+1)));wav=out/f'message-{m["message_id"]}-source-CPU-to-C-DSP.wav'
            with wave.open(str(wav),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(rate_hz);w.writeframes(b''.join(struct.pack('<hh',*p) for p in c_pairs))
            results.append(dict(message_id=m['message_id'],source_CPU_states=8,source_pointer=rebuilt['pointer'],source_length=rebuilt['length'],
                R23_increment_loaded_at_DSP_boot='0x0481db08',header_increment_field=hex(m['DSP_increment']),
                word_clocks=ticks,source_DSP_instructions=sum(x['instructions'] for x in states)+native_boot[0],
                final_logical_DSP_sha256=c_states[-1]['DSP'],PCM_sha256=sha(b''.join(struct.pack('<hh',*p) for p in c_pairs)),
                nonzero_PCM_pairs=sum(p!=[0,0] for p in pairs),wav=str(wav),wav_sha256=sha(wav.read_bytes()),C_original_DSP_instructions=0))
            save(out/'fixtures.json',results)
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='source_movie_CPU_first_real_audio_enqueue_and_C_DSP_output_native_match',directory=str(out),
            cases=results,word_clocks=sum(x['word_clocks'] for x in results),source_CPU_states=48,
            CPU_controller_source_sha256=mapping['source_sha256'],DSP_source_sha256=dsp_proof['source_sha256'],script_sha256=sha(Path(__file__).read_bytes()),
            E902_pointer_and_length_replaced_by_host=False,source_C_DSP_RAM_shared_with_C_CPU_bus=True,
            all8496logical_DSP_bytes_RAM_DAC_and_instruction_counts_compared_each_clock=True,
            movie_CPU_firmware_provider_and_host_deliveries=True,original_DSP_instructions_on_C_side=0,
            video_GPU_executed=False,BIOS_firmware_seek_verified=False,in_game_dialogue_verified=False,whole_game_complete=False,new_published_components=0,
            limits=['Source C CPU dispatches states0..7 and enqueues the first actual audio chunk into shared C-owned DSP RAM. The six-byte exception and full movie caller are separate.',
                    'DSP boots before parsing under an explicit host schedule: source R23 retains E840 increment0481DB08 even when E8E2 updates its RAM field to04924924. No source rate fix applied.',
                    'Host supplies mastered movie bytes and a clock change; BIOS seek/progress are declared providers. One first chunk per dialogue, controlled SSI/word clocks, shared pinned bus/DAC; no full video, streaming timing or physical playback.',
                    'DSP comparison includes logical8496bytes, not native opcode/pipeline microstate.'])
        save(out/'report.json',report);save(ROOT/'verification/BIWN-movie-audio-integration.json',report);save(out/'status.json',dict(status='terminal_pass'))
        print(json.dumps(dict(directory=str(out),cases=len(results),source_CPU_states=48,word_clocks=report['word_clocks'])))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:runtime.oracle.close()

if __name__=='__main__':main()
