"""Native source CPU stop/reload calls and DSP command1/2 discovery."""
import ctypes as c,json,struct
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_music_cold_entry_scheduled_startup as live
import check_biwn_source_entry_boot as boot
ROOT=boot.ROOT;save=boot.save;sha=boot.sha
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);maps=[json.loads((session/(n+'-fullCPU-generation.json')).read_text())for n in ['movie','video','media-setup','entry-setup','GPU-boot','geometry-records','startup','startup-HUD','static-factory','system','health-timeout']];rows=sum((m['instructions_decoded']for m in maps),[]);ram=bytearray(0x200000);stage=(session/'nextstage-68000-candidate.bin').read_bytes();ram[0x4000:0x4000+len(stage)]=stage;ram[0x21ea8:0x22770]=(session/'media-video-gpu-21ea0/original-overlay.bin').read_bytes();control_rows=boot.source.controller.movie.generator.loader.base.binary_tools.m68k_instructions(ram[0xe9ec:0xea16],0xe9ec)[0];rows+=control_rows
    proof=json.loads((ROOT/'verification/music-cold-entry-timer-startup-loading-movie-world-checks.json').read_text());disc=live.base.joined.Disc(session);out=ROOT/'verification/BIWN-music-command-probe'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);frames=Path(json.loads((ROOT/'verification/BIWN-movie-sequence-GPU-C.json').read_text())['directory'])/'C-frames';live.Runtime.entry_rows=maps[3]['instructions_decoded'];runtime=live.Runtime(Path(proof['directory'])/'libscheduled-startup.dylib',rows,*[m['instructions_decoded']for m in maps[:3]],disc=disc,out=out,frame_directory=frames);runtime.entry_coverage=set();runtime.entry_TOC=boot.source.controller.make_toc(disc.layout);core=runtime.core;decoded={};traces=[]
    def decode(pc):
        if pc not in decoded:
            o=pc-0xf1b000;assert 0<=o<0x1210,hex(pc);b=c.string_at(core.DSPGetRAM(),8192);size=6 if int.from_bytes(b[o:o+2],'big')>>10==38 else 2;decoded[pc]=boot.source.controller.movie.generator.loader.base.binary_tools.jaguar_instructions(b[o:o+size],pc,'dsp')[0][0]
        return decoded[pc]
    def dsp_pump(stop,label):
        trace=[]
        for _ in range(100000):
            pc=core.DSPGetPC()
            if pc==stop:break
            r=decode(pc);before=runtime.counter.value;core.DSPExec(1);count=(runtime.counter.value-before)&0xffffffff;assert count in [1,2]
            if count==2:decode(pc+r['size'])
            trace.append(dict(PC=pc,bank=runtime.raw_DSP()[8495],instructions=count))
        else:raise AssertionError(('command DSP limit',label,hex(pc)))
        return dict(label=label,trace=trace,DSP=sha(runtime.raw_DSP()[:8496]),RAM=sha(runtime.device.ram()),hardware=runtime.hardware())
    def CPU_call(entry,label):
        s=boot.media.CPU();s.registers[15]=s.ssp=0x1ff000;s.usp=0x180000;s.pc=entry;s.sr=0x2700;runtime.device.direct(s.registers[15],4,boot.media.STOP);was_running=runtime.full_running;runtime.full_running=True;runtime.seed_cpu(s);runtime.full_running=was_running;trace=[];phases=[]
        for _ in range(10000):
            pc=core.m68k_get_reg(None,16)
            if pc==boot.media.STOP:break
            assert pc in runtime.rows,hex(pc)
            if pc==0xe9a8:phases.append(dsp_pump(0xf1b144,label+' flag-init'))
            if pc==0xea08:phases.append(dsp_pump(0xf1b144 if entry==0xe9ec else 0xf1b148,label+' acknowledgement'))
            trace.append(pc);core.m68k_execute(1)
        else:raise AssertionError(('command CPU limit',label,hex(pc)))
        return dict(entry=hex(entry),CPU_trace=trace,DSP_phases=phases,CPU=boot.media.scheduler.cpu_dict(runtime.cpu()),RAM=sha(runtime.device.ram()),hardware=runtime.hardware())
    try:
        runtime.source_entry(bytes(ram),0,'native');(out/'initial-DSP.bin').write_bytes(runtime.raw_DSP());(out/'initial-RAM.bin').write_bytes(runtime.device.ram());initial_hardware=runtime.hardware()
        for round in range(2):
            traces.append(CPU_call(0xe9ec,f'stop{round}'));assert core.DSPGetPC()==0xf1b144 and core.DSPReadLong(0xf1badc,6)==0
            traces.append(CPU_call(0xe96c,f'reload{round}'));assert core.DSPGetPC()==0xf1b148 and core.DSPReadLong(0xf1badc,6)==0
            runtime.engine_pump(f'reloaded mixer{round}')
        report=dict(status='native_CPU_E9EC_stop_E96C_reload_DSP_command1_2_two_cycles_observed',directory=str(out),visited_rows=sorted(decoded.values(),key=lambda r:r['address']),CPU_control_rows=control_rows,phases=traces,initial_hardware=initial_hardware,processor_reset_between_stop_and_reload=False,host_CPU_entry_frames_supplied=True,DSP_completion_script=False,DSP_commands_C_verified=False,whole_game_complete=False,limits=['Native discovery from actual cold-stage source4000 and live default silent mixer; standalone CPU entry/privateframes supplied for E9EC/E96C, BIOS/TOC and processor alternation providers remain.','Command1 idles DSP atF1B144 with GO retained and disables music timers/SSI; command2 source reload/acknowledgement restarts mixer. No full song, other commands/voices, physicalperiod/globaltime/gameplay claim.'])
        (out/'final-DSP.bin').write_bytes(runtime.raw_DSP());(out/'final-RAM.bin').write_bytes(runtime.device.ram());save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/music-command-probe.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ['visited_rows','phases','initial_hardware','CPU_control_rows']}));print('NEW ROWS',len(decoded))
    except BaseException as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:runtime.oracle.close();disc.close()
if __name__=='__main__':main()
