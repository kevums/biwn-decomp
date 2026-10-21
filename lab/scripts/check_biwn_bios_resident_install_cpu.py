"""Original ROM copy versus C: fullCPU/privateRAM/peripherals, exact write span."""
import ctypes as c,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_media_setup_cpu as media
ROOT=media.ROOT;save=media.save;sha=media.sha
class Runtime(media.Runtime):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.bios=(ROOT/'render-assets/jaguarcd_bios.bin').read_bytes()
        fn=self.lib.biwn_bios_resident_install_cpu_body;fn.argtypes=self.fn.argtypes;fn.restype=c.c_int;self.fn=fn
        for name in ['CDROM','CDROMStateExt']:
            f=getattr(self.core,'CDROMStateSave'if name=='CDROM'else 'CDROMStateExtSave');f.argtypes=[c.c_void_p];f.restype=c.c_size_t;self.savers[name]=f
    def reset(self,*args):
        super().reset(*args);c.memmove(self.rom,self.bios,len(self.bios))
    def native(self,ram,initial,seed,coverage):
        self.reset(ram,seed);self.seed_cpu(initial);steps=0
        while steps<10000:
            pc=self.core.m68k_get_reg(None,16)
            if pc==0x802054:break
            assert pc in self.rows,hex(pc);coverage.add(pc);self.core.m68k_execute(1);steps+=1
        else:raise AssertionError('ROM resident-copy work bound')
        return self.device.ram(),self.cpu(),{**self.snapshot(),'CPU_steps':steps}
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'bios-resident-install-fullCPU-generation.json').read_text())
    out=ROOT/'verification/BIWN-BIOS-resident-install-CPU'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    src=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_bios_resident_install_cpu.c','biwn_media_setup_cpu.c'];lib=out/'libresident-install.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(src/n)for n in names],'-o',str(lib)]
    build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
    runtime=Runtime(lib,mapping['instructions_decoded']);rng=random.Random(0x80203e);coverage=set();results=[]
    try:
        for case in range(32):
            data=bytes(0x200000)if case<8 else bytes([case])*0x200000;s=media.CPU();s.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[0x1ff000];s.pc=0x80203e;s.sr=(0x2000 if case%2 else 0)|((case%8)<<8)|(case%32);s.usp=0x180000 if s.sr&0x2000 else 0x1ff000;s.ssp=0x1ff000 if s.sr&0x2000 else 0x1fe000
            save(out/'status.json',dict(status='running',case=case));left,a,n=runtime.native(data,s,case%3,coverage);right,b,t=runtime.translated(data,s,case%3)
            if left!=right or bytes(a)!=bytes(b)or n['hardware']!=t['hardware']or t['status']:
                save(out/'mismatch.json',dict(case=case,native_CPU=media.scheduler.cpu_dict(a),C_CPU=media.scheduler.cpu_dict(b),native_hardware=n['hardware'],C_hardware=t['hardware'],status=t['status'],RAM_differences=[hex(i)for i,(x,y)in enumerate(zip(left,right))if x!=y][:20]));raise AssertionError(str(out/'mismatch.json'))
            assert right[0x3000:0x39ec]==runtime.bios[0x84a6:0x8e92] and right[:0x3000]==data[:0x3000]and right[0x39ec:]==data[0x39ec:]
            assert a.registers[8]==0x808e92 and a.registers[9]==0x39ec and a.registers[10]==0x808e90 and n['CPU_steps']==1908
            results.append(dict(case=case,supervisor=bool(s.sr&0x2000),CPU=media.scheduler.cpu_dict(b),RAM_sha256=sha(right),hardware=t['hardware'],native_instructions=n['CPU_steps'],bytes_copied=2540,untouched_RAM_outside_copy=True));save(out/'cases.json',results)
        selected={r['address']for r in mapping['instructions_decoded']};assert selected<=coverage
        report=dict(status='actual_ROM_resident_image_copy_CPU_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(results),source_instruction_coverage=[len(selected&coverage),len(selected)],bytes_copied=2540,copy_ROM_interval=mapping['copy_ROM_interval'],copy_RAM_interval=mapping['copy_RAM_interval'],nominal_end_overshoot_bytes=2,BIOS_sha256=mapping['BIOS_sha256'],source_sha256=mapping['source_sha256'],test_script_sha256=sha(Path(__file__).read_bytes()),full_firmware_boot_verified=False,linked_into_game_startup=False,whole_game_complete=False,limits=['SourceROM routine80203E..802054 only; stops before BSR802070. Initial user BIOS mapped at800000 and CPU/RAM/device fixture supplied. Preceding graphics/mainBIOS copy, authentication, firmware boot/load/dispatch and clocks are unverified.', 'Original/C fullCPU/SR/USP/SSP/private2MBRAM/peripherals/controller baseline+9byte extension match in32fixtures; no original CPU executes on C path. Exact2540byte copy includes2byte overshoot beyond nominal end808E90.'])
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/bios-resident-install-CPU-checks.json',report);print(json.dumps(dict(status=report['status'],directory=str(out),cases=len(results),coverage=report['source_instruction_coverage'])))
    except BaseException as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:runtime.oracle.close()
if __name__=='__main__':main()
