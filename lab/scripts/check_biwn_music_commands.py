"""Continuous source CPU/DSP stop/reload cycles against original processors."""
import ctypes as c,json,os,subprocess,hashlib,struct,random
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_music_cold_entry_scheduled_startup as live
from check_biwn_music_DSP_engine import State,logical,dsp,media
ROOT=live.ROOT;save=live.save;sha=live.sha
class Runtime(live.Runtime):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.command_active=False;self.command_phases=[]
        self.stop_call=self.lib.biwn_music_stop_cpu_call;self.stop_body=self.lib.biwn_music_stop_cpu_body
        for f in [self.stop_call,self.stop_body]:f.argtypes=self.entry_call.argtypes;f.restype=c.c_int
        parent=self.service
        def service(_,bus,cpu,target):
            if self.command_active and target==0xea08:return self.stop_body(bus,cpu,self.callbacks[5],self.service,None,100000,0)
            return parent(_,bus,cpu,target)
        self.service=media.world_cpu.SERVICE(service)
    def command_pump(self,stop,label):
        trace=[];count=0;before=self.counter.value;begin=self.C_DSP.instructions if self.mode=='C'else 0
        for _ in range(100000):
            pc=self.core.DSPGetPC()if self.mode=='native'else self.C_DSP.pc
            if pc==stop:break
            if self.mode=='native':trace.append(pc);n=self.counter.value;self.core.DSPExec(1);count+=(self.counter.value-n)&0xffffffff
            else:
                self.engine_trace.clear();status=self.engine_step(c.byref(self.engine_bus),c.byref(self.C_DSP));assert not status,(status,label,hex(self.C_DSP.pc));trace.extend(self.engine_trace)
        else:raise AssertionError(('command DSP bound',label,hex(pc)))
        if self.mode=='C':count=self.C_DSP.instructions-begin;assert self.counter.value==before;c.memmove(self.core.DSPGetRAM(),bytes(self.C_DSP.local_RAM),8192)
        self.command_phases.append(dict(label=label,PC_trace=trace,instructions=count,DSP_sha256=sha(self.logical_DSP()),RAM_sha256=sha(self.device.ram()),hardware=self.hardware()))
    def write(self,a,w,v):
        super().write(a,w,v)
        if self.command_active and self.mode=='C'and w==4:
            if a==0xf1a114 and v==1 and self.C_DSP.pc==0xf1b126:self.command_pump(0xf1b144,'flags')
            if a==0xf1a114 and v==5:assert self.engine_irq(c.byref(self.C_DSP),0)==0;c.memmove(self.core.DSPGetRAM(),bytes(self.C_DSP.local_RAM),8192)
    def read(self,a,w):
        if self.command_active and self.mode=='C'and a==0xf1badc and w==4:self.command_pump(0xf1b144 if self.command_entry==0xe9ec else 0xf1b148,'ack')
        return super().read(a,w)
    def command_call(self,entry,case):
        self.command_active=True;self.command_entry=entry;self.command_phases=[];rng=random.Random(0xe9ec+case);s=media.CPU();s.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[0x1ff000];s.sr=(0x2000 if case%2 else 0)|(case%8);s.ssp=0x1ff000 if s.sr&0x2000 else 0x180000;s.usp=0x180000 if s.sr&0x2000 else 0x1ff000;s.pc=entry;self.device.direct(s.registers[15],4,media.STOP);before_GPU=self.gpu_counter.value;before_DSP=self.counter.value
        if self.mode=='native':
            old=self.full_running;self.full_running=True;self.seed_cpu(s);self.full_running=old
            for _ in range(10000):
                pc=self.core.m68k_get_reg(None,16)
                if pc==media.STOP:break
                assert pc in self.rows,hex(pc);self.command_CPU_coverage.add(pc)
                if pc==0xe9a8:self.command_pump(0xf1b144,'flags')
                if pc==0xea08:self.command_pump(0xf1b144 if entry==0xe9ec else 0xf1b148,'ack')
                self.core.m68k_execute(1)
            else:raise AssertionError(('command CPU bound',hex(pc)))
            final=self.cpu()
        else:
            self.C_CPU=s;f=self.stop_call if entry==0xe9ec else self.entry_call;status=f(c.byref(self.bus),c.byref(s),self.callbacks[5],self.service,None,100000,0);assert not status and not self.errors,(status,self.errors,hex(s.pc));final=s
            assert self.gpu_counter.value==before_GPU and self.counter.value==before_DSP and not self.C_original_CPU_attempts
        self.command_active=False
        assert (self.core.DSPGetPC()if self.mode=='native'else self.C_DSP.pc)==(0xf1b144 if entry==0xe9ec else 0xf1b148)
        assert self.read(0xf1badc,4)==0
        if entry==0xe9ec:
            control=self.core.DSPGetControl()if self.mode=='native'else self.C_DSP.control
            flags=self.core.DSPGetFlags()if self.mode=='native'else self.C_DSP.flags
            assert control&1 and not flags&0x60 and not self.read(0xf10000,2)and not self.read(0xf10002,2)
            self.music_engine_active=False
        else:self.music_engine_active=True;self.engine_pump('reloaded mixer')
        return dict(entry=hex(entry),CPU=media.scheduler.cpu_dict(final),RAM=sha(self.device.ram()),hardware=self.hardware(),command_phases=list(self.command_phases),mixer_calls=list(self.music_engine_calls))
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);out=ROOT/'verification/BIWN-music-command-cycles'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);src=ROOT/'projects/black-ice-white-noise/restoration';prior=json.loads((ROOT/'verification/music-cold-entry-timer-startup-loading-movie-world-checks.json').read_text());names=list(prior['source_sha256'])+['biwn_music_stop_cpu.c'];library=out/'libmusic-command.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(src/n)for n in names]+['-o',str(library)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr)
    if build.returncode:save(out/'status.json',dict(status='terminal_failed',error=build.stderr));raise AssertionError(build.stderr)
    maps=[json.loads((session/(n+'-fullCPU-generation.json')).read_text())for n in ['movie','video','media-setup','entry-setup','GPU-boot','geometry-records','startup','startup-HUD','static-factory','system','health-timeout','music-stop']];rows=sum((m['instructions_decoded']for m in maps),[]);disc=live.base.joined.Disc(session);frames=Path(json.loads((ROOT/'verification/BIWN-movie-sequence-GPU-C.json').read_text())['directory'])/'C-frames';Runtime.entry_rows=maps[3]['instructions_decoded'];runtime=Runtime(library,rows,*[m['instructions_decoded']for m in maps[:3]],disc=disc,out=out,frame_directory=frames);runtime.command_CPU_coverage=set();runtime.entry_coverage=set();runtime.entry_TOC=live.base.joined.controller.make_toc(disc.layout);stage=(session/'nextstage-68000-candidate.bin').read_bytes();ram=bytearray(0x200000);ram[0x4000:0x4000+len(stage)]=stage;ram[0x21ea8:0x22770]=(session/'media-video-gpu-21ea0/original-overlay.bin').read_bytes();results=[]
    try:
        for case in range(4):
            observed={};RAM={}
            for mode in ['native','C']:
                save(out/'status.json',dict(status='running',case=case,mode=mode));runtime.source_entry(bytes(ram),case,mode);phases=[]
                for round in range(2):
                    phases.append(runtime.command_call(0xe9ec,case*2+round));phases.append(runtime.command_call(0xe96c,case*2+round))
                observed[mode]=dict(phases=phases,final_RAM=sha(runtime.device.ram()),hardware=runtime.hardware());RAM[mode]=runtime.device.ram();save(out/f'case-{case}-{mode}.json',observed[mode]);(out/f'case-{case}-{mode}-RAM.bin').write_bytes(RAM[mode])
            assert observed['native']==observed['C']and RAM['native']==RAM['C'],str(out)
            assert json.loads((out/f'case-{case}-native.json').read_text())==json.loads((out/f'case-{case}-C.json').read_text())
            results.append(dict(case=case,cycles=2,snapshot=observed['C']));save(out/'cases.json',results)
        stop_PC={r['address']for r in maps[-1]['instructions_decoded']};assert stop_PC<=runtime.command_CPU_coverage
        report=dict(status='source_CPU_E9EC_E96C_DSP_stop_reload_mixer_restart_two_cycles_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=4,stop_reload_cycles=8,user_and_supervisor_CPU_calls_verified=True,source_stop_CPU_instruction_coverage=[len(stop_PC&runtime.command_CPU_coverage),len(stop_PC)],covered_CPU_PC=sorted(runtime.command_CPU_coverage),processor_reset_between_stop_and_reload=False,host_CPU_entry_frames_supplied=True,DSP_completion_script=False,original_CPU_GPU_DSP_instructions_on_C_path=0,source_sha256={n:sha((src/n).read_bytes())for n in names},test_script_sha256=sha(Path(__file__).read_bytes()),compiler=cmd,whole_game_complete=False,full_music_playback_verified=False,limits=['Starts at zeroRAM+pinnedstage/initialCPU/device seed/canonicalGPUbytes/BIOS-TOC adapters and source4000/live bank1 silent mixer. Four CPU/device profiles, two actual CPU stop/reload calls each; private entry frames/registers are host inputs, not a full game input path.','Command1 source disables timer/SSI and entersF1B144 withGO retained; command2 sourceE96Ccopies/reinitializes/acknowledges and actual source mixer resumes. No CPU/GPU/DSP resets between calls, no RAMboundaryrestore or mailboxcompletion script. FullCPU/bothbanks/private2MBRAM/logicalGPU-DSP/peripherals/command traces/counts and saved snapshots compare.','No audible disc music, allvoices/commands/resources, physicalperiod/globaltime/firmware/completegameplay verification.'])
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/music-command-cycles-checks.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ['source_sha256','covered_CPU_PC','compiler']}))
    except BaseException as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e),errors=runtime.errors));raise
    finally:runtime.oracle.close();disc.close()
if __name__=='__main__':main()
