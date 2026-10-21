"""Native DSP bank1 mixer/SSI/timer discovery after actual cold source4000 entry."""
import argparse,ctypes as c,json,struct
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_source_entry_boot as boot
import check_biwn_music_DSP_bootstrap as music
ROOT=boot.ROOT;save=boot.save;sha=boot.sha
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--sample-voice',action='store_true');opt=ap.parse_args()
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);maps=[json.loads((session/(n+'-fullCPU-generation.json')).read_text())for n in ['movie','video','media-setup','entry-setup','GPU-boot','geometry-records']]
    boot.Runtime.entry_rows=maps[3]['instructions_decoded'];proof=json.loads((ROOT/'verification/cold-source4000-entry-checks.json').read_text());runtime=boot.Runtime(Path(proof['directory'])/'libsource-entry.dylib',sum((m['instructions_decoded']for m in maps),[]),*[m['instructions_decoded']for m in maps[:3]]);runtime.entry_coverage=set();runtime.entry_TOC=boot.source.controller.make_toc(json.loads((session/'cdi-layout.json').read_text()));core=runtime.core;core.DSPGetReg.argtypes=[c.c_int];core.DSPGetReg.restype=c.c_uint32;core.DSPGetFlags.restype=c.c_uint32
    stage=(session/'nextstage-68000-candidate.bin').read_bytes();ram=bytearray(0x200000);ram[0x4000:0x4000+len(stage)]=stage;ram[0x21ea8:0x22770]=(session/'media-video-gpu-21ea0/original-overlay.bin').read_bytes();runtime.source_entry(bytes(ram),0,'native')
    if opt.sample_voice:
        voice=0xf1bd10;core.DSPWriteLong(voice,8,6)
        for off,value in [(4,0x80007fff),(8,0x1e0000),(12,0x100),(16,0x10000),(20,0x10000),(24,0),(76,0x3fff),(80,0)]:core.DSPWriteLong(voice+off,value,6)
        pattern=bytes([20,40,60,80,100,120,148,168,188,208,228,248,0,0,0,0]);c.memmove(runtime.device.pointer+0x1e0000,pattern*16,256)
    out=ROOT/'verification'/('BIWN-music-DSP-sample-voice-probe'if opt.sample_voice else 'BIWN-music-DSP-engine-probe')/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);initial=runtime.raw_DSP();(out/'initial-DSP.bin').write_bytes(initial);(out/'initial-RAM.bin').write_bytes(runtime.device.ram());decoded={};phases=[];PCM=[];all_trace=[]
    def decode(pc):
        if pc not in decoded:
            offset=pc-0xf1b000;assert 0<=offset<0x1210,hex(pc);b=c.string_at(core.DSPGetRAM(),8192);size=6 if int.from_bytes(b[offset:offset+2],'big')>>10==38 else 2;decoded[pc]=boot.source.controller.movie.generator.loader.base.binary_tools.jaguar_instructions(b[offset:offset+size],pc,'dsp')[0][0]
        return decoded[pc]
    def pump(label):
        trace=[];begin=runtime.counter.value
        for _ in range(100000):
            pc=core.DSPGetPC();bank=runtime.raw_DSP()[8495]
            if pc==0xf1b212 and bank==1 and not core.DSPGetFlags()&8 and core.DSPGetReg(2)==core.DSPGetReg(28)and struct.unpack_from('=I',runtime.raw_DSP(),8239+21*4)[0]==core.DSPGetReg(28):break
            row=decode(pc);before=runtime.counter.value;core.DSPExec(1);count=(runtime.counter.value-before)&0xffffffff;assert count in [1,2],(hex(pc),count)
            if count==2:decode(pc+row['size'])
            trace.append(dict(PC=pc,bank=bank,instructions=count));all_trace.append(trace[-1])
        else:raise AssertionError(('Native music wait bound',label,hex(pc),core.DSPGetReg(2),core.DSPGetReg(28)))
        phases.append(dict(label=label,blocks=len(trace),instructions=(runtime.counter.value-begin)&0xffffffff,trace=trace,DSP_sha256=sha(runtime.raw_DSP()[:8496]),RAM_sha256=sha(runtime.device.ram()),hardware=runtime.hardware()))
    try:
        pump('bank1_mixer_init')
        for tick in range(64):
            if tick%16==0:core.DSPSetIRQLine(2,1);pump('timer2-'+str(tick))
            core.DSPSetIRQLine(1,1);pump('SSI-'+str(tick));core.DACWordStrobe();PCM.append(music.dsp.strobed_pair(runtime.dac()))
            save(out/'status.json',dict(status='running',tick=tick))
        (out/'final-DSP.bin').write_bytes(runtime.raw_DSP());(out/'final-RAM.bin').write_bytes(runtime.device.ram());save(out/'phases.json',phases);save(out/'PCM.json',PCM)
        report=dict(status='native_bank1_music_mixer_SSI_timer2_source_trace_observed',directory=str(out),source4000_entry=True,initial_FrozenRAM_supplied=False,stages=len(phases),SSI_events=64,timer2_events=4,visited_rows=sorted(decoded.values(),key=lambda r:r['address']),source_instructions=sum(x['instructions']for x in all_trace),banks=sorted({x['bank']for x in all_trace}),nonzero_PCM_pairs=sum(any(x)for x in PCM),PCM_sha256=sha(b''.join(struct.pack('<hh',*x)for x in PCM)),synthetic_voice_and_sample_input=opt.sample_voice,DSP_engine_C_verified=False,full_music_playback_verified=False,whole_game_complete=False,limits=['Native discovery after source4000 startup with zeroRAM+pinnedstage, BIOS/TOC adapters and source song pointer3BCE0/index0. External SSI events and timer2 every16SSIevents are explicit test stimuli, not physicalperiod/globaltime.','Synthetic sample-voice mode supplies one type8voice and256encoded waveform bytes at1E0000 for a source interpolation-kernel test; no disc music attribution.', 'Bounded64word stereo output and complete mixer-wait cycles only; no C comparison, full song/other music/sound resources or global boot/gameplay verification yet.'])
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification'/('music-DSP-sample-voice-probe.json'if opt.sample_voice else 'music-DSP-engine-probe.json'),report);print(json.dumps({k:v for k,v in report.items()if k!='visited_rows'}));print('OPCODES',sorted({int(r['bytes'][:4],16)>>10 for r in decoded.values()}))
    except BaseException as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:runtime.oracle.close()
if __name__=='__main__':main()
