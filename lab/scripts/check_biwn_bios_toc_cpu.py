"""Original/C BIOS305A with preserved CDI controller and full state comparison."""
import ctypes as c,json,os,random,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_bios_mode_cpu as mode
media=mode.media;ROOT=mode.ROOT;save=mode.save;sha=mode.sha
POLLS={0x3910,0x392e,0x37e0}
class Runtime(mode.Runtime):
    def __init__(self,*args):
        media.Runtime.__init__(self,*args);self.mode_call=self.lib.biwn_bios_toc_cpu_call;self.mode_body=self.lib.biwn_bios_toc_cpu_body
        for f in [self.mode_call,self.mode_body]:f.argtypes=self.fn.argtypes;f.restype=c.c_int
        self.core.CDROMReset.argtypes=[];self.core.CDROMStateSave.argtypes=[c.c_void_p];self.core.CDROMStateSave.restype=c.c_size_t
        self.core.CDIntfOpenImage.argtypes=[c.c_char_p];self.core.CDIntfOpenImage.restype=c.c_bool;self.core.CDROMInit.argtypes=[];self.core.CDIntfCloseImage.argtypes=[];self.core.BUTCHExec.argtypes=[c.c_uint32]
        assert self.core.CDIntfOpenImage(str(ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi').encode());self.core.CDROMInit()
    def native(self,ram,initial,seed,coverage):
        self.reset(ram,seed);self.seed_cpu(initial);steps=0
        for _ in range(100000):
            pc=self.core.m68k_get_reg(None,16)
            if pc==media.STOP:break
            assert pc in self.rows,hex(pc);coverage.add(pc)
            if pc in POLLS:self.tick()
            self.core.m68k_execute(1);steps+=1
        else:raise AssertionError(('Native BIOS TOC limit',hex(pc)))
        return self.device.ram(),self.cpu(),{**self.snapshot(),'CPU_steps':steps,'BUTCH_ticks':self.butch_ticks}
    def translated_mode(self,ram,initial,seed):
        self.reset(ram,seed);s=media.CPU.from_buffer_copy(bytes(initial));errors=[]
        def rd(w):
            def callback(_,a,v):v[0]=self.read(a,w);return 0
            return callback
        def wr(w):
            def callback(_,a,v):self.write(a,w,v);return 0
            return callback
        types=[media.scheduler.cleanup.world.R8,media.scheduler.cleanup.world.R16,media.scheduler.cleanup.world.R32,media.scheduler.cleanup.world.W16,media.scheduler.cleanup.world.W32,media.W8];callbacks=[types[0](rd(1)),types[1](rd(2)),types[2](rd(4)),types[3](wr(2)),types[4](wr(4)),types[5](wr(1))];bus=media.Bus(*callbacks[:5],media.scheduler.cleanup.world.CALL(),None,0)
        def service(_,passed,cpu,target):
            if target==0x390e:return self.mode_body(passed,cpu,callbacks[5],callback,None,100000,0)
            errors.append(hex(target));return 1
        callback=media.world_cpu.SERVICE(service);status=self.mode_call(c.byref(bus),c.byref(s),callbacks[5],callback,None,100000,0);assert not status and not errors,(status,errors,hex(s.pc));return self.device.ram(),s,self.snapshot()
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'bios-toc-fullCPU-generation.json').read_text());out=ROOT/'verification/BIWN-BIOS-toc-CPU'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);src=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libbios-toc.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(src/'biwn_bios_toc_cpu.c'),str(src/'biwn_media_setup_cpu.c'),'-o',str(library)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr)
    if build.returncode:save(out/'status.json',dict(status='terminal_failed',error=build.stderr));raise AssertionError(build.stderr)
    runtime=Runtime(library,mapping['instructions_decoded']);bios=(ROOT/'render-assets/jaguarcd_bios.bin').read_bytes();ram=bytearray(0x200000);ram[0x3000:0x3e00]=bios[0x84a6:0x92a6];ram[0x1ff000:0x1ff004]=media.STOP.to_bytes(4,'big');rng=random.Random(0x305ac);coverage=set();results=[]
    try:
        for case in range(12):
            runtime.prequeue=[0,0x7001][case%2];s=media.CPU();s.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[0x1ff000];s.registers[8]=[0x2c00,0x10000,0x140000][case%3];s.pc=0x305a;s.sr=(0x2000 if case%2 else 0)|(case%32);s.usp=0x180000 if s.sr&0x2000 else 0x1ff000;s.ssp=0x1ff000 if s.sr&0x2000 else 0x200000
            baseline=bytearray(ram);baseline[s.registers[8]:s.registers[8]+0x400]=bytes(rng.randrange(256)for _ in range(0x400))
            save(out/'status.json',dict(status='running',case=case));left,expected,native=runtime.native(bytes(baseline),s,case%3,coverage);right,actual,translated=runtime.translated_mode(bytes(baseline),s,case%3)
            save(out/f'case-{case}-native.json',dict(CPU=media.scheduler.cpu_dict(expected),hardware=native['hardware'],RAM_sha256=sha(left),BUTCH_ticks=native['BUTCH_ticks']));save(out/f'case-{case}-C.json',dict(CPU=media.scheduler.cpu_dict(actual),hardware=translated['hardware'],RAM_sha256=sha(right),BUTCH_ticks=runtime.butch_ticks))
            if left!=right or bytes(expected)!=bytes(actual)or native['hardware']!=translated['hardware']:
                save(out/'mismatch.json',dict(case=case,native_CPU=media.scheduler.cpu_dict(expected),C_CPU=media.scheduler.cpu_dict(actual),native_hardware=native['hardware'],C_hardware=translated['hardware'],RAM_differences=[dict(address=hex(i),native=a,C=b)for i,(a,b)in enumerate(zip(left,right))if a!=b][:50]));raise AssertionError(str(out/'mismatch.json'))
            assert int.from_bytes(right[0x3e00:0x3e02],'big')==0 and native['BUTCH_ticks']==runtime.butch_ticks
            toc=right[s.registers[8]:s.registers[8]+0x400];(out/f'case-{case}-TOC.bin').write_bytes(toc)
            results.append(dict(case=case,destination=hex(s.registers[8]),prequeued_command=hex(runtime.prequeue),CPU=media.scheduler.cpu_dict(actual),RAM_sha256=sha(right),native_instructions=native['CPU_steps'],BUTCH_ticks=runtime.butch_ticks,TOC_sha256=sha(toc),TOC_header=list(toc[:8]),tracks=[list(toc[t*8:t*8+8])for t in range(1,6)],complete_CPU_RAM_BUTCH_queue_peripherals_match=True));save(out/'cases.json',results)
        selected={r['address']for r in mapping['instructions_decoded']};report=dict(status='actual_user_BIOS305A_TOC_DSA_source_CPU_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=12,source_instruction_coverage=[len(selected&coverage),len(selected)],covered_PC=sorted(coverage),uncovered_PC=sorted(selected-coverage),actual_source_TOC_generation=True,synthetic_TOC_supplied=False,BUTCH_full_state_compared=True,BIOS_sha256=mapping['BIOS_sha256'],source_sha256=mapping['source_sha256'],generator_sha256=mapping['generator_sha256'],test_script_sha256=sha(Path(__file__).read_bytes()),compiler=cmd,whole_game_complete=False,full_BIOS_firmware_boot_verified=False,limits=['Resident BIOS hostloaded from suppliedROM84A6 atRAM3000. Actual pinned BUTCH/CDI model provides tagged session/track replies. Initial controller register setup supplied; one BUTCH tick at each source3910/392E/37E0 status read, not physical/global scheduling.','Complete CPU/bothstackbanks/privateRAM/BUTCH state and prior GPU/DSP/TOM/JERRY/DAC/cart snapshots match; successful five-track BIWN TOC only. Uncovered branches/errors/other disc layouts/remaining transport/CDGPUISR/firmware boot remain unverified.'])
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/bios-toc-CPU-checks.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ['source_sha256','compiler','covered_PC','uncovered_PC']}))
    except BaseException as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:runtime.core.CDIntfCloseImage();runtime.oracle.close()
if __name__=='__main__':main()
