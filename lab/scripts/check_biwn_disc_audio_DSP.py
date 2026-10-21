"""Actual disc samples through native/C DSP; controlled buffers and word clocks.

Compare logical DSP, full RAM, DAC, PCM and instruction count after every
word-clock event. This does not execute the movie CPU producer or BIOS stream.
"""
import ctypes as c
import json
import struct
import wave
from datetime import datetime, timezone
from pathlib import Path
import check_biwn_dsp_media_audio as dsp

ROOT=dsp.ROOT
save=dsp.save
sha=dsp.sha

def main():
    extraction=json.loads((ROOT/'verification/BIWN-dialogue-audio-extraction.json').read_text())
    prior=json.loads((ROOT/'verification/biwn-dsp-media-audio-checks.json').read_text())
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    mapping=json.loads((session/'media-dsp-e840/C-generation.json').read_text())
    library=Path(prior['directory'])/'libdsp-media-audio.dylib'
    runtime=dsp.Runtime(library,mapping)
    out=ROOT/'verification/BIWN-disc-audio-DSP'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    base=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
    results=[];coverage=set()
    def reference_segment():
        count=runtime.counter.value
        for _ in range(10000):
            s=dsp.state_from_raw(runtime.raw())
            if runtime.idle(s): break
            pc=s.pc;assert pc in runtime.mapping
            before=runtime.counter.value;runtime.core.DSPExec(1)
            delta=(runtime.counter.value-before)&0xffffffff
            assert delta in [1,2];coverage.add(pc)
            if delta==2:coverage.add(pc+runtime.mapping[pc]['size'])
        else: raise AssertionError('Native segment exceeded bound')
        return dict(DSP=runtime.raw()[:8496],RAM=sha(runtime.media.device.ram()),DAC=sha(runtime.dac()),instructions=(runtime.counter.value-count)&0xffffffff)
    def compare(s,ref):
        count=runtime.counter.value;before=s.instructions
        assert runtime.run(c.byref(runtime.bus),c.byref(s),10000)==0
        assert runtime.counter.value==count
        assert s.instructions-before==ref['instructions']
        assert dsp.logical(s)==ref['DSP']
        assert sha(runtime.media.device.ram())==ref['RAM'] and sha(runtime.dac())==ref['DAC']
    try:
        for case,message in enumerate(extraction['messages']):
            data=Path(message['first_chunk_path']).read_bytes()
            assert sha(data)==message['audio_chunks_manifest'][0]['sha256']
            ram=bytearray(base);ram[0x1a0000:0x1a0000+len(data)]=data;ram=bytes(ram)
            rate=message['DSP_increment'];seed=case%3;ticks=4096 if case==0 else 128
            save(out/'status.json',dict(status='running',message=message['message_id'],word_clocks=ticks))
            initial=runtime.load(ram,seed,rate)
            runtime.core.DSPWriteLong(0xf1a150,message['SCLK'],6)
            boot=reference_segment()
            runtime.core.DSPWriteLong(0xf1b13c,0x1a0000,6)
            runtime.core.DSPWriteLong(0xf1b138,len(data),6)
            refs=[];pairs=[]
            for _ in range(ticks):
                runtime.core.DACWordStrobe();pairs.append(dsp.strobed_pair(runtime.dac()))
                runtime.core.DSPSetIRQLine(1,1);refs.append(reference_segment())
            runtime.core.DSPWriteLong(0xf1b140,1,6)
            runtime.core.DACWordStrobe();runtime.core.DSPSetIRQLine(1,1);stop=reference_segment()
            s=runtime.load(ram,seed,rate);assert dsp.logical(s)==dsp.logical(initial)
            runtime.core.DSPWriteLong(0xf1a150,message['SCLK'],6)
            compare(s,boot)
            s.local_RAM[0x13c:0x140]=(0x1a0000).to_bytes(4,'big')
            s.local_RAM[0x138:0x13c]=len(data).to_bytes(4,'big')
            c_pairs=[]
            for ref in refs:
                runtime.core.DACWordStrobe();c_pairs.append(dsp.strobed_pair(runtime.dac()))
                assert runtime.interrupt(c.byref(s))==0;compare(s,ref)
            s.local_RAM[0x140:0x144]=(1).to_bytes(4,'big')
            runtime.core.DACWordStrobe();assert runtime.interrupt(c.byref(s))==0;compare(s,stop)
            assert c_pairs==pairs and not(s.control&1) and s.pc==0xf1b130
            nonzero_pairs=sum(pair!=[0,0] for pair in pairs)
            if case==0: assert nonzero_pairs > 0
            wav=out/f'message-{message["message_id"]}-first-chunk-C-DSP.wav'
            # Rounded declared NTSC master clock; not measured physical timing.
            rate_hz=round(26590906/(64*(message['SCLK']+1)))
            with wave.open(str(wav),'wb') as w:
                w.setnchannels(2);w.setsampwidth(2);w.setframerate(rate_hz)
                w.writeframes(b''.join(struct.pack('<hh',*pair) for pair in c_pairs))
            results.append(dict(message_id=message['message_id'],supplied_audio_bytes=len(data),
                source_audio_sha256=sha(data),DSP_increment=hex(rate),SCLK=message['SCLK'],
                declared_WAV_Hz=rate_hz,word_clocks=ticks+1,instructions=s.instructions,nonzero_PCM_pairs=nonzero_pairs,
                logical_DSP_sha256=sha(dsp.logical(s)),wav=str(wav),wav_sha256=sha(wav.read_bytes()),
                C_original_DSP_instructions=0,PCM_pairs_sha256=sha(b''.join(struct.pack('<hh',*p) for p in c_pairs))))
            save(out/'fixtures.json',results)
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='real_disc_sample_buffers_native_C_DSP_match',directory=str(out),
            cases=results,word_clocks=sum(x['word_clocks'] for x in results),source_instruction_coverage=[len(coverage),len(runtime.mapping)],
            extraction_report_sha256=sha((ROOT/'verification/BIWN-dialogue-audio-extraction.json').read_bytes()),
            C_library_sha256=sha(library.read_bytes()),script_sha256=sha(Path(__file__).read_bytes()),
            boundary_comparison='All 8496 logical DSP bytes, full main RAM, DAC state and source instruction count after every word-clock/idle segment; PCM pairs exact.',
            original_DSP_instructions_on_C_path=0,actual_disc_audio_samples=True,
            movie_CPU_producer_executed=False,BIOS_streaming_executed=False,in_game_playback_verified=False,whole_game_complete=False,
            limits=['Host supplies one extracted audio chunk per message at a fixed test RAM address, using its source header increment/SCLK. Five cases only test the first128wordclocks; message58 tests4096.',
                    'Explicit SSI and word clocks, rounded declared NTSC WAV rate, shared pinned DAC/bus model. No source movie scheduling/BIOS stream, full dialogue playback, physical timing or capture.',
                    'Comparison is after every clock/idle segment, unlike the earlier supplied-sample proof after every atomic instruction block.'])
        save(out/'report.json',report);save(ROOT/'verification/BIWN-disc-audio-DSP.json',report)
        save(out/'status.json',dict(status='terminal_pass'))
        print(json.dumps(dict(directory=str(out),cases=len(results),word_clocks=report['word_clocks'])))
    except Exception as error:
        save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:runtime.media.oracle.close()

if __name__=='__main__':main()
