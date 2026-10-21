"""Original DSP versus fixed C, including source SSI frame and word-clock output.

The checked C CPU loader initializes both paths. Explicit word strobes/SSI
events and supplied sample buffers are fixtures; no movie/boot/game audio claim.
Every atomic original instruction block compares all8496logicalDSPbytes,
mainRAM and DAC state. C path executes no original DSP instructions.
"""
import ctypes as c
import hashlib
import json
import math
import os
import struct
import subprocess
import wave
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_media_setup_cpu as media

ROOT=media.ROOT
save=media.save
sha=media.sha
Row=c.c_uint32*32
class State(c.Structure):
    _fields_=[('accumulator',c.c_uint64),('registers',Row*2)]+[(name,c.c_uint32) for name in
        ['pc','z','c','n','flags','control','remainder','modulo','matrix_control','matrix_pointer','data_organization','division_control','instructions']]+[('local_RAM',c.c_uint8*8192)]
R8=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint8))
R32=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint32))
W32=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint32)
OBS=c.CFUNCTYPE(None,c.c_void_p,c.c_uint32)
class Bus(c.Structure):_fields_=[('read8',R8),('read32',R32),('write32',W32),('observe_PC',OBS),('context',c.c_void_p)]


def state_from_raw(raw):
    s=State();s.local_RAM[:]=raw[:8192];s.pc=struct.unpack_from('=I',raw,8192)[0];s.accumulator=struct.unpack_from('=Q',raw,8196)[0]
    names=['remainder','modulo','flags','matrix_control','matrix_pointer','data_organization','control','division_control']
    for name,value in zip(names,struct.unpack_from('=8I',raw,8204)):setattr(s,name,value)
    s.z,s.n,s.c=raw[8236:8239]
    values=struct.unpack_from('=64I',raw,8239)
    for i,v in enumerate(values):s.registers[i//32][i%32]=v
    assert raw[8495]==0,'Source program uses bank0'
    return s


def logical(s):
    raw=bytes(s.local_RAM)+struct.pack('=IQ8I',s.pc,s.accumulator,s.remainder,s.modulo,s.flags,s.matrix_control,s.matrix_pointer,s.data_organization,s.control,s.division_control)
    raw+=bytes([s.z,s.n,s.c])+struct.pack('=64I',*[v for bank in s.registers for v in bank])+b'\0'
    assert len(raw)==8496
    return raw


def strobed_pair(raw):
    # Pinned DACStateSave serializes two ints, bool, three uint32s and two
    # doubles, then seven hardware uint16s followed by the two int16 rings.
    holding_offset=struct.calcsize('=ii?IIIdd')
    ring_offset=holding_offset+7*2
    assert holding_offset==37 and ring_offset==51 and len(raw)==65587
    position=struct.unpack_from('=I',raw,struct.calcsize('=ii?'))[0]
    size=(len(raw)-ring_offset)//4;index=(position-1)%size
    pair=[struct.unpack_from('=h',raw,ring_offset+index*2)[0],
        struct.unpack_from('=h',raw,ring_offset+size*2+index*2)[0]]
    assert tuple(pair)==struct.unpack_from('=hh',raw,holding_offset)
    return pair


class Runtime:
    def __init__(self,library,mapping):
        proof=json.loads((ROOT/'verification/biwn-media-setup-cpu-checks.json').read_text())
        session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
        setup=json.loads((session/'media-setup-fullCPU-generation.json').read_text())
        self.media=media.Runtime(Path(proof['directory'])/'libmedia-setup.dylib',setup['instructions_decoded']);self.core=self.media.core
        self.lib=c.CDLL(str(library));self.mapping={r['address']:r for r in mapping['instructions_decoded']}
        self.step=self.lib.biwn_dsp_media_audio_step;self.step.argtypes=[c.POINTER(Bus),c.POINTER(State)];self.step.restype=c.c_int
        self.run=self.lib.biwn_dsp_media_audio_run;self.run.argtypes=[c.POINTER(Bus),c.POINTER(State),c.c_uint32];self.run.restype=c.c_int
        self.interrupt=self.lib.biwn_dsp_media_audio_ssi_interrupt;self.interrupt.argtypes=[c.POINTER(State)];self.interrupt.restype=c.c_int
        self.core.DSPExec.argtypes=[c.c_int32];self.core.DSPGetPC.restype=c.c_uint32
        self.core.DSPSetIRQLine.argtypes=[c.c_int,c.c_int]
        self.core.DSPReadLong.argtypes=[c.c_uint32,c.c_uint32];self.core.DSPReadLong.restype=c.c_uint32
        self.core.DSPWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32]
        self.core.JaguarReadByte.argtypes=[c.c_uint32,c.c_uint32];self.core.JaguarReadByte.restype=c.c_uint8
        self.core.DACWordStrobe.argtypes=[]
        self.counter=c.c_uint32.in_dll(self.core,'dsp_exec_opcode_count')
        self.errors=[];self.writes=[];self.external_reads=[]
        def read8(_,a,out):
            try:out[0]=self.core.JaguarReadByte(a,2);self.external_reads.append([a,1,out[0]]);return 0
            except Exception as e:self.errors.append(repr(e));return 1
        def read32(_,a,out):
            try:out[0]=self.core.DSPReadLong(a,2);self.external_reads.append([a,4,out[0]]);return 0
            except Exception as e:self.errors.append(repr(e));return 1
        def write32(_,a,v):
            try:self.writes.append([a,v]);self.core.DSPWriteLong(a,v,2);return 0
            except Exception as e:self.errors.append(repr(e));return 1
        self.callbacks=[R8(read8),R32(read32),W32(write32),OBS(lambda *_:None)]
        self.bus=Bus(*self.callbacks,None)

    def raw(self):
        raw=c.create_string_buffer(12000);size=self.media.savers['DSP'](raw);assert size==8729;return raw.raw[:size]

    def dac(self):
        raw=c.create_string_buffer(200000);size=self.media.savers['DAC'](raw);return raw.raw[:size]

    def load(self,ram,seed,rate):
        self.writes=[];self.external_reads=[];self.errors=[]
        initial=media.CPU();initial.registers[:]=[0]*15+[0x1fe000];initial.pc=0xe840;initial.usp=0x1fe000;initial.ssp=0x1ff000;initial.sr=0x700
        data=bytearray(ram);data[initial.registers[15]:initial.registers[15]+4]=media.STOP.to_bytes(4,'big')
        _,_,result=self.media.translated(bytes(data),initial,seed);assert result['status']==0
        self.core.DSPWriteLong(0xf1b144,rate,6)
        return state_from_raw(self.raw())

    def idle(self,s):return not(s.control&1) or (s.pc==0xf1b074 and s.registers[0][27]==0 and not(s.flags&8))

    def original_block(self,coverage):
        before=self.raw();s=state_from_raw(before);pc=s.pc;assert pc in self.mapping,hex(pc)
        count=self.counter.value;self.core.DSPExec(1);after=self.raw();delta=(self.counter.value-count)&0xffffffff
        assert delta in [1,2],(hex(pc),delta)
        coverage.add(pc)
        if delta==2:coverage.add(pc+self.mapping[pc]['size'])
        return dict(PC=pc,instructions=delta,before=sha(before[:8496]),after=sha(after[:8496]),
            after_raw=after[:8496],DAC_after_sha256=sha(self.dac()),main_RAM_after=sha(self.media.device.ram()))

    def original_segment(self,coverage):
        frames=[]
        for _ in range(10000):
            before=self.raw();s=state_from_raw(before)
            if self.idle(s):break
            frames.append(self.original_block(coverage))
        else:raise AssertionError('Native DSP segment bound')
        return frames,state_from_raw(self.raw())

    def C_segment(self,s,frames,case,tick,out,boundary=True):
        for index,frame in enumerate(frames):
            assert s.pc==frame['PC'] and sha(logical(s))==frame['before'],('before',case,tick,index,hex(s.pc))
            count=s.instructions;native_count=self.counter.value
            status=self.step(c.byref(self.bus),c.byref(s))
            if status or logical(s)!=frame['after_raw'] or sha(self.dac())!=frame['DAC_after_sha256'] or sha(self.media.device.ram())!=frame['main_RAM_after'] or s.instructions-count!=frame['instructions']:
                (out/'native-DSP-logical.bin').write_bytes(frame['after_raw']);(out/'C-DSP-logical.bin').write_bytes(logical(s))
                save(out/'mismatch.json',dict(case=case,tick=tick,index=index,PC=hex(frame['PC']),C_PC=hex(s.pc),status=status,
                    native_sha=sha(frame['after_raw']),C_sha=sha(logical(s)),DAC_match=sha(self.dac())==frame['DAC_after_sha256'],
                    DSP_diff=[i for i,(a,b) in enumerate(zip(frame['after_raw'],logical(s))) if a!=b][:40],errors=self.errors))
                raise AssertionError(str(out/'mismatch.json'))
            assert self.counter.value==native_count,'C side called original DSP'
        if boundary:assert self.idle(s)


def main():
    out=ROOT/'verification/biwn-dsp-media-audio'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=ROOT/'projects/black-ice-white-noise/restoration';session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    mapping=json.loads((session/'media-dsp-e840/C-generation.json').read_text());library=out/'libdsp-media-audio.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_dsp_media_audio.c'),'-o',str(library)]
    compiled=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'compiler.txt').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0,compiled.stderr
    runtime=Runtime(library,mapping);base=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();coverage=set();results=[]
    vectors=[(rate,length,idle_slot,40) for rate in [0,0x0481db08,0x7fffffff,0x80000000,0xffffffff] for length in [1,8,64] for idle_slot in [0,1]]
    vectors.append((0x0481db08,64,0,3196))
    try:
        for case,(rate,length,idle_slot,ticks) in enumerate(vectors):
            save(out/'status.json',dict(status='running',case=case,rate=hex(rate),length=length))
            ram=bytearray(base);waveform=bytes(int(100*math.sin(i*2*math.pi/32))&255 for i in range(1024))
            ram[0x1a0000:0x1a0400]=waveform;ram=bytes(ram);seed=case%3
            initial=runtime.load(ram,seed,rate);boot,ready=runtime.original_segment(coverage)
            segments=[];native_pairs=[];irq_frames=[];pre_irq=[]
            for tick in range(ticks):
                post=tick%60==0 if ticks>40 else tick in [0,1,2,3,4,5,6,7,8,9,10,18,25]
                pointer=0x1a0000+((tick//60)*64)%512 if ticks>40 else 0x1a0000+(tick*13)%512
                if post:
                    runtime.core.DSPWriteLong(0xf1b13c,pointer,6)
                    runtime.core.DSPWriteLong(0xf1b138,length,6)
                pre_irq.append([runtime.original_block(coverage)] if idle_slot else [])
                runtime.core.DACWordStrobe();native_pairs.append(strobed_pair(runtime.dac()))
                runtime.core.DSPSetIRQLine(1,1);irq_frames.append(runtime.raw()[:8496])
                frames,ready=runtime.original_segment(coverage);segments.append(frames)
            runtime.core.DSPWriteLong(0xf1b140,1,6)
            runtime.core.DACWordStrobe();runtime.core.DSPSetIRQLine(1,1);stop_irq=runtime.raw()[:8496]
            stop,halted=runtime.original_segment(coverage);assert not halted.control&1 and halted.pc==0xf1b130
            reference_DAC=runtime.dac();reference_RAM=runtime.media.device.ram()
            s=runtime.load(ram,seed,rate);count=runtime.counter.value
            assert logical(s)==logical(initial)
            runtime.C_segment(s,boot,case,'boot',out)
            pairs=[]
            for tick,frames in enumerate(segments):
                post=tick%60==0 if ticks>40 else tick in [0,1,2,3,4,5,6,7,8,9,10,18,25]
                pointer=0x1a0000+((tick//60)*64)%512 if ticks>40 else 0x1a0000+(tick*13)%512
                if post:
                    s.local_RAM[0x13c:0x140]=pointer.to_bytes(4,'big')
                    s.local_RAM[0x138:0x13c]=length.to_bytes(4,'big')
                runtime.C_segment(s,pre_irq[tick],case,'pre-IRQ',out,boundary=False)
                runtime.core.DACWordStrobe();pairs.append(strobed_pair(runtime.dac()))
                assert runtime.interrupt(c.byref(s))==0
                assert logical(s)==irq_frames[tick],('IRQ',case,tick)
                runtime.C_segment(s,frames,case,tick,out)
            s.local_RAM[0x140:0x144]=(1).to_bytes(4,'big');runtime.core.DACWordStrobe()
            assert runtime.interrupt(c.byref(s))==0 and logical(s)==stop_irq
            runtime.C_segment(s,stop,case,'stop',out)
            assert runtime.counter.value==count and runtime.dac()==reference_DAC and runtime.media.device.ram()==reference_RAM and pairs==native_pairs
            assert logical(s)==logical(halted)
            assert any(pair!=[0,0] for pair in pairs)
            if ticks>40:
                with wave.open(str(out/'synthetic-C-DSP-word-strobes.wav'),'wb') as w:
                    w.setnchannels(2);w.setsampwidth(2);w.setframerate(31960);w.writeframes(b''.join(struct.pack('<hh',*pair) for pair in pairs))
            row=dict(case=case,rate=hex(rate),supplied_chunk_length=length,idle_interrupt_slot=idle_slot,word_strobes=ticks+1,SSI_events=ticks+1,
                direct_instruction_blocks=len(boot)+sum(len(x) for x in segments)+sum(len(x) for x in pre_irq)+len(stop),
                DSP_source_instructions=s.instructions,C_original_DSP_executed=0,PCM_pairs=pairs,
                final_logical_DSP_sha256=sha(logical(s)),final_DAC_sha256=sha(reference_DAC))
            results.append(row);save(out/'fixtures.json',results)
        missing=[hex(x) for x in sorted(set(runtime.mapping)-coverage)]
        save(out/'coverage.json',dict(covered_PC=sorted(coverage),source_instruction_coverage=[len(coverage),len(runtime.mapping)],missing=missing))
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='source_DSP_media_program_SSI_frames_word_strobes_native_C_match',directory=str(out),cases=len(results),
            source_instruction_coverage=[len(coverage),len(runtime.mapping)],unexercised_instructions=missing,
            SSI_events=sum(x['SSI_events'] for x in results),word_strobes=sum(x['word_strobes'] for x in results),
            DSP_source_instructions=sum(x['DSP_source_instructions'] for x in results),
            all8496logical_DSP_bytes_compared_after_every_atomic_instruction_block=True,
            mandatory_branch_delays_and_source_SSI_frame_compared=True,all_main_RAM_and_DAC_state_compared_after_every_block=True,
            original_DSP_execution_on_C_side=False,source_program_code_modified=False,
            source_sha256=mapping['source_sha256'],test_script_sha256=sha(Path(__file__).read_bytes()),compiler=command,
            pinned_core_sha256=sha((ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib').read_bytes()),
            audio_playback_in_game_verified=False,movie_streaming_verified=False,global_DSP_or_physical_timing_verified=False,
            new_published_components=0,whole_game_complete=False,
            limits=['Bank0 source caller, supplied sample chunks/rate values and explicit word clocks/SSI events; no actual media streaming/game scheduler or unmasked global hardware timing.',
                'Shared pinned DAC/bus model. Synthetic comparison waveform is declared clock output, not recovered game audio or a physical capture. Opcode/pipeline microstate outside the logical8496-byte comparison; no bank1/other IRQ or whole DSP architecture claim.'])
        save(out/'report.json',report);save(ROOT/'verification/biwn-dsp-media-audio-checks.json',report);save(out/'status.json',dict(status='terminal_pass'))
        print(json.dumps(dict(directory=str(out),cases=len(results),source_instruction_coverage=report['source_instruction_coverage'],SSI_events=report['SSI_events'])))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:runtime.media.oracle.close()


if __name__=='__main__':main()
