"""Original user-BIOS3000 versus fixed C, complete CPU/RAM/device state."""
import ctypes as c,json,os,random,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_media_setup_cpu as media
ROOT=media.ROOT;save=media.save;sha=media.sha
def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'bios-setup-fullCPU-generation.json').read_text());out=ROOT/'verification/BIWN-BIOS-setup-CPU'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);src=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libbios-setup.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(src/'biwn_bios_setup_cpu.c'),str(src/'biwn_media_setup_cpu.c'),'-o',str(library)];build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(build.stdout+build.stderr)
    if build.returncode:save(out/'status.json',dict(status='terminal_failed',error=build.stderr));raise AssertionError(build.stderr)
    runtime=media.Runtime(library,mapping['instructions_decoded']);fn=runtime.lib.biwn_bios_setup_cpu_call;fn.argtypes=runtime.fn.argtypes;fn.restype=c.c_int;runtime.fn=fn
    bios=(ROOT/'render-assets/jaguarcd_bios.bin').read_bytes();resident=bios[0x84a6:0x92a6];baseline=bytearray(0x200000);baseline[0x3000:0x3e00]=resident;SP=0x1ff000;baseline[SP:SP+4]=media.STOP.to_bytes(4,'big');rng=random.Random(0x3000c);coverage=set();results=[]
    try:
        for case in range(24):
            data=bytearray(baseline);s=media.CPU();s.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[SP];s.registers[8]=[0xf03050,0xf03100,0xf03200][case%3];s.pc=0x3000;s.sr=(0x2000 if case%2 else 0)|((case%8)<<8)|rng.randrange(32);s.usp=0x180000 if s.sr&0x2000 else SP;s.ssp=SP if s.sr&0x2000 else 0x200000
            save(out/'status.json',dict(status='running',case=case));left,expected,native=runtime.native(bytes(data),s,case%3,coverage);right,actual,translated=runtime.translated(bytes(data),s,case%3)
            if left!=right or bytes(expected)!=bytes(actual)or native['hardware']!=translated['hardware']:
                save(out/'mismatch.json',dict(case=case,native_CPU=media.scheduler.cpu_dict(expected),C_CPU=media.scheduler.cpu_dict(actual),native_hardware=native['hardware'],C_hardware=translated['hardware'],RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(left,right))if a!=b][:50]));raise AssertionError(str(out/'mismatch.json'))
            assert int.from_bytes(right[0x3074:0x3078],'big')==s.registers[8]and right[0x3072]==0
            results.append(dict(case=case,A0=hex(s.registers[8]),supervisor=bool(s.sr&0x2000),CPU=media.scheduler.cpu_dict(actual),RAM_sha256=sha(right),native_instructions=native['CPU_steps'],complete_CPU_private_RAM_peripherals_match=True));save(out/'cases.json',results)
        selected={r['address']for r in mapping['instructions_decoded']};assert selected<=coverage
        report=dict(status='actual_user_BIOS3000_GPU_CD_ISR_setup_source_CPU_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=24,source_instruction_coverage=[len(selected&coverage),len(selected)],user_supervisor_and_three_GPU_area_inputs=True,BIOS_sha256=mapping['BIOS_sha256'],ROM_resident_offset=mapping['ROM_resident_offset'],source_sha256=mapping['source_sha256'],generator_sha256=mapping['generator_sha256'],test_script_sha256=sha(Path(__file__).read_bytes()),compiler=cmd,whole_game_complete=False,full_BIOS_firmware_boot_verified=False,limits=['Actual resident BIOS bytes loaded explicitly from supplied ROM84A6 intoRAM3000; source3000 installsGPUvector/CDISR code56longs andenablesGPU IRQ1. Supplied initialCPU/device state, shared pinned MMIO/BUTCH model; GPUCDISR instructions/realdisc delivery not executed.','24standalone inputs compare allCPU/SR/USP/SSP/private2MBRAM/peripherals; source firmware relocation/boot, other BIOSentries, actualtransport/timing/globalgame/physicalscanout remain unverified.'])
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/bios-setup-CPU-checks.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ['source_sha256','compiler']}))
    except BaseException as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:runtime.oracle.close()
if __name__=='__main__':main()
