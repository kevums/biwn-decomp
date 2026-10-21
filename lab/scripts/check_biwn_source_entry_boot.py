"""Actual4000 CPU caller through helpers/GPU/music acknowledgement to DD40.

BIOS ABI/TOC and processor alternation are declared providers. No mailbox
completion script, processor-setup calls or captured initialized CPU supplied.
"""
import ctypes as c,json,os,random,subprocess,hashlib
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_movie_source_boot_exit_AV as source
import check_biwn_full_video_cpu_gpu as video
import check_biwn_dsp_media_audio as dsp
from check_biwn_music_DSP_bootstrap import Bus as MusicBus,W16
ROOT=source.ROOT;media=source.media;save=source.save;sha=source.sha
BIOS={0x3000,0x3048,0x3006,0x305a}
class EntryBootMixin:
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.entry_active=False;self.music_started=False;self.music_calls=[]
        self.entry_body=self.lib.biwn_entry_setup_cpu_body;self.entry_call=self.lib.biwn_entry_setup_cpu_call
        for f in [self.entry_body,self.entry_call]:f.argtypes=self.fn.argtypes;f.restype=c.c_int
        self.GPU_boot_body=self.lib.biwn_GPU_boot_cpu_body;self.GPU_boot_body.argtypes=self.fn.argtypes;self.GPU_boot_body.restype=c.c_int
        self.music_run=self.lib.biwn_dsp_music_bootstrap_run;self.music_run.argtypes=[c.POINTER(MusicBus),c.POINTER(dsp.State),c.c_uint32,c.c_uint32];self.music_run.restype=c.c_int
        self.music_irq=self.lib.biwn_dsp_music_bootstrap_cpu_interrupt;self.music_irq.argtypes=[c.POINTER(dsp.State)];self.music_irq.restype=c.c_int
        self.core.DSPGetPC.restype=c.c_uint32;self.core.DSPWriteWord.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32]
        self.music_trace=[]
        self.music_callbacks=[dsp.R8(lambda _,a,v:(v.__setitem__(0,self.core.JaguarReadByte(a,2)),0)[1]),dsp.R32(lambda _,a,v:(v.__setitem__(0,self.core.DSPReadLong(a,2)),0)[1]),dsp.W32(lambda _,a,v:(self.core.DSPWriteLong(a,v,2),0)[1]),W16(lambda _,a,v:(self.core.DSPWriteWord(a,v,2),0)[1]),dsp.OBS(lambda _,pc:self.music_trace.append(pc))];self.music_bus=MusicBus(*self.music_callbacks,None)
        self.entry_addresses={r['address']for r in self.entry_rows};parent=self.service
        def service(_,bus,cpu,target):
            try:
                if self.entry_active:
                    if target in BIOS:self.entry_bios(cpu.contents,target);return 0
                    if target in self.entry_addresses:return self.entry_body(bus,cpu,self.callbacks[5],self.service,None,1000000,0)
                    if target==0xe00a:
                        status=self.GPU_boot_body(bus,cpu,self.callbacks[5],self.service,None,100000,0)
                        if status:return status
                        self.run_boot_exit('main_boot');self.run_dispatch(True);return 0
                return parent(_,bus,cpu,target)
            except Exception as e:self.errors.append(repr(e));return 1
        self.service=media.world_cpu.SERVICE(service)
    def entry_bios(self,s,target):
        self.BIOS_calls.append(dict(target=hex(target),D0=s.registers[0],A0=s.registers[8],A1=s.registers[9]))
        if target==0x305a:
            assert s.registers[8]==0x2c00
            for i,b in enumerate(self.entry_TOC):self.device.direct(0x2c00+i,1,b)
        #3000/3048/3006 preserve-register ABI providers, not firmware bodies.
    def music_segment(self,stop):
        trace=[];delays=0;begin=self.counter.value
        if self.mode=='native':
            for _ in range(10000):
                pc=self.core.DSPGetPC()
                if pc==stop:break
                trace.append(pc);before=self.counter.value;self.core.DSPExec(1);delta=(self.counter.value-before)&0xffffffff;assert delta in [1,2];delays+=delta-1
            else:raise AssertionError(('Native music segment bound',hex(pc)))
            logical=self.raw_DSP()[:8496];instructions=len(trace)+delays
        else:
            self.music_trace.clear();before=self.C_DSP.instructions
            assert self.music_run(c.byref(self.music_bus),c.byref(self.C_DSP),10000,stop)==0,(hex(self.C_DSP.pc),self.errors)
            instructions=self.C_DSP.instructions-before;trace=list(self.music_trace);logical=dsp.logical(self.C_DSP);assert self.counter.value==begin;c.memmove(self.core.DSPGetRAM(),bytes(self.C_DSP.local_RAM),8192)
        self.music_calls.append(dict(stop=hex(stop),PC_trace=trace,instructions=instructions,DSP_sha256=sha(logical)))
    def write(self,a,w,v):
        super().write(a,w,v)
        if not self.entry_active or self.mode!='C' or w!=4:return
        if a==0xf02100:
            self.gpu.flags=(v&~8)|((v&8)&self.gpu.flags);self.gpu.z=v&1;self.gpu.c=(v>>1)&1;self.gpu.n=(v>>2)&1;self.gpu.bank=0 if self.gpu.flags&8 else bool(v&0x4000)
        if a==0xf0210c:self.gpu.data_organization=v
        if a==0xf1a100:self.C_DSP.flags=(v&~8)|((v&8)&self.C_DSP.flags);self.C_DSP.z=v&1;self.C_DSP.c=(v>>1)&1;self.C_DSP.n=(v>>2)&1
        if a==0xf1a10c:self.C_DSP.data_organization=v
        if a==0xf1a110:self.C_DSP.pc=v
        if a==0xf1a114:
            self.C_DSP.control=(self.C_DSP.control&0x1f7c0)|(v&~0x1f7c6)
            if v==1 and self.C_DSP.pc==0xf1b126:self.music_segment(0xf1b144)
            if v==5:assert self.music_irq(c.byref(self.C_DSP))==0;self.music_started=True;c.memmove(self.core.DSPGetRAM(),bytes(self.C_DSP.local_RAM),8192)
    def read(self,a,w):
        if self.entry_active and self.mode=='C'and a==0xf1badc and w==4 and self.music_started:
            self.music_segment(0xf1b148);self.music_started=False
        return super().read(a,w)
    def source_entry(self,ram,case,mode):
        firstboot=None
        if hasattr(self,'firstboot_to_stage'):
            initial,firstboot=self.firstboot_to_stage(ram,case,mode);self.entry_active=True;self.bios_mode_ticks=0;self.bios_toc_ticks=0;self.BIOS_calls=[];self.music_calls=[];self.music_started=False
        else:
            self.entry_active=False;self.C_DSP=None;self.pending_overlay=False;video.Runtime.start(self,ram,case%3,mode);self.entry_active=True;self.music_started=False;self.music_calls=[];self.BIOS_calls=[]
            self.queries=[];self.deliveries=[];self.progress=0x1c0000;self.timer_arm=False;self.timer_reads=0
            if mode=='C':self.C_DSP=dsp.state_from_raw(self.raw_DSP())
            rng=random.Random(0x4000+case);initial=media.CPU();initial.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[0x1ff000];initial.ssp=0x1ff000;initial.usp=0x180000;initial.sr=0x2000|(case%8);initial.pc=0x4000
        GPU_before=self.gpu_counter.value;DSP_before=self.counter.value;CPU_trace=[]
        if mode=='native':
            if firstboot is None:self.seed_cpu(initial)
            for _ in range(100000):
                pc=self.core.m68k_get_reg(None,16)
                if pc==0xdd40:break
                actual_entries=getattr(self,'actual_bios_entries',{0x3000})if getattr(self,'actual_bios_setup',False)else set()
                if pc in actual_entries:self.entry_bios(self.cpu(),pc)
                if pc in BIOS and pc not in actual_entries:
                    self.entry_bios(self.cpu(),pc);old=self.device.read(pc,2);self.device.direct(pc,2,0x4e75);self.core.m68k_execute(1);self.device.direct(pc,2,old);continue
                assert pc in self.rows,hex(pc);self.entry_coverage.add(pc);CPU_trace.append(pc)
                if hasattr(self,'before_entry_CPU'):self.before_entry_CPU(pc)
                if pc==0xd384 and self.core.GPUGetPC()!=0xf032c8:self.native_GPU(True)
                if pc==0xe038:self.run_boot_exit('main_boot');self.run_dispatch(True)
                if pc==0xe9a8:self.music_segment(0xf1b144)
                if pc==0xea08 and self.core.DSPGetPC()!=0xf1b148:self.music_segment(0xf1b148)
                self.core.m68k_execute(1)
            else:raise AssertionError(('Native source entry bound',hex(pc)))
            result=self.cpu()
        else:
            self.C_CPU=initial;status=self.entry_call(c.byref(self.bus),c.byref(initial),self.callbacks[5],self.service,None,1000000,0);assert status==8 and not self.errors,(status,self.errors,hex(initial.pc));result=initial
            assert self.gpu_counter.value==GPU_before and self.counter.value==DSP_before and self.C_original_CPU_attempts==0
        assert result.pc==0xdd40 and (self.core.DSPGetPC()if mode=='native'else self.C_DSP.pc)==0xf1b148
        assert (self.core.GPUGetPC()if mode=='native'else self.gpu.pc)==0xf031ce
        self.entry_active=False;self.entry_CPU=result;entry=dict(CPU=media.scheduler.cpu_dict(result),RAM=sha(self.device.ram()),hardware=self.hardware(),BIOS_calls=self.BIOS_calls,GPU_calls=self.gpu_calls,music_calls=self.music_calls)
        if firstboot is not None:entry['game_firstboot']=firstboot
        return entry,dict(native_CPU_steps=len(CPU_trace)if mode=='native'else None,original_CPU_GPU_DSP_attempts_on_C_path=0)
class Runtime(EntryBootMixin,source.Runtime):pass
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);out=ROOT/'verification/BIWN-source4000-entry'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);src=ROOT/'projects/black-ice-white-noise/restoration'
    prior=json.loads((ROOT/'verification/BIWN-movie-source-boot-exit-AV.json').read_text());names=list(prior['source_sha256'])+['biwn_entry_setup_cpu.c','biwn_dsp_music_bootstrap.c'];library=out/'libsource-entry.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(src/n)for n in names]+['-o',str(library)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr)
    if build.returncode:save(out/'status.json',dict(status='terminal_failed',error=build.stderr));raise AssertionError(build.stderr)
    maps=[json.loads((session/(n+'-fullCPU-generation.json')).read_text())for n in ['movie','video','media-setup','entry-setup','GPU-boot','geometry-records']];rows=sum((m['instructions_decoded']for m in maps),[]);Runtime.entry_rows=maps[3]['instructions_decoded'];runtime=Runtime(library,rows,*[m['instructions_decoded']for m in maps[:3]]);runtime.entry_coverage=set();layout=json.loads((session/'cdi-layout.json').read_text());runtime.entry_TOC=source.controller.make_toc(layout);base=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());base[0x21ea8:0x22770]=(session/'media-video-gpu-21ea0/original-overlay.bin').read_bytes();results=[]
    try:
        for case in range(2):
            observed={};RAM={}
            for mode in ['native','C']:
                save(out/'status.json',dict(status='running',case=case,mode=mode));observed[mode],checks=runtime.source_entry(bytes(base),case,mode);RAM[mode]=runtime.device.ram();save(out/f'case-{case}-{mode}.json',observed[mode]);(out/f'case-{case}-{mode}-RAM.bin').write_bytes(RAM[mode])
            if observed['native']!=observed['C']or RAM['native']!=RAM['C']:save(out/'mismatch.json',observed);raise AssertionError(str(out/'mismatch.json'))
            results.append(dict(case=case,snapshot=observed['C'],checks=checks));save(out/'cases.json',results)
        report=dict(status='source4000_CPU_helpers_GPU_boot_music_command2_to_DD40_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(results),entry_CPU_coverage=[len(runtime.entry_coverage&runtime.entry_addresses),len(runtime.entry_addresses)],covered_CPU_PC=sorted(runtime.entry_coverage),source_sha256={n:sha((src/n).read_bytes())for n in names},test_script_sha256=sha(Path(__file__).read_bytes()),compiler=cmd,DSP_mailbox_completion_script=False,initial_processor_setup_calls_supplied=False,source4000_to_DD40_caller_verified_with_declared_providers=True,global_boot_verified=False,whole_game_complete=False,limits=['Supplied FrozenRAM/CPU/device seed and canonical pre-relocation GPU payload; BIOS3000/3048/3006 preserve-register adapters and305A syntheticTOC from source disc layout, not firmware. DefaultNTSC only.','Actual source4000 caller/DFF4/D340/E6A0/E00A/1557A/17340/E942/E7AA executes continuously toDD40. Native/C completeCPU/bothstackbanks/private2MBRAM/logicalGPU4396/DSP8496/peripherals/BIOSargs andGPU/DSPtraces compare.','Source musicDSP flags init beforeCPUcommand2 and handler beforeCPUmailboxpoll are explicit processor alternation boundaries; actualperiod/interleaving/global clocks/musicmixer/bank1/SSI output/fullsourceDD40startup and game/physicalscanout are not included in this standalone proof.'])
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/source4000-entry-checks.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ['source_sha256','covered_CPU_PC','compiler']}))
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e),errors=runtime.errors));raise
    finally:runtime.oracle.close()
if __name__=='__main__':main()
