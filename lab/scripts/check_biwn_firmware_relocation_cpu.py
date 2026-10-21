"""Fresh original/C ROM bootstrap comparisons to natural relocated entry.

Compare complete CPU/both stack banks, private RAM and hardware snapshots.
The native oracle and C share the pinned peripheral bus; no processors run
on the C path. This checks relocation, not authenticated disc/game boot.
"""
import ctypes as c
import json
import os
import random
import struct
import subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_bios_resident_install_cpu as resident
import check_biwn_media_setup_cpu as media

ROOT=media.ROOT;save=media.save;sha=media.sha

class Runtime(resident.Runtime):
    def __init__(self,*args,**kwargs):
        # Parent's small resident symbol is deliberately retained for initialization.
        super().__init__(*args,**kwargs)
        fn=self.lib.biwn_firmware_relocation_cpu_call
        fn.argtypes=self.fn.argtypes;fn.restype=c.c_int;self.fn=fn

    def native(self,ram,initial,seed,coverage):
        self.reset(ram,seed);self.seed_cpu(initial);steps=0
        while steps<300000:
            pc=self.core.m68k_get_reg(None,16)
            if pc==0x500d6:break
            assert pc in self.rows,hex(pc)
            coverage.add(pc);self.core.m68k_execute(1);steps+=1
        else:raise AssertionError(('ROM relocation bound',hex(pc)))
        return self.device.ram(),self.cpu(),{**self.snapshot(),'CPU_steps':steps}

def expected_ram(data,bios):
    result=bytearray(data);intervals=[]
    for source,end,dest in [(0x81421c,0x82f1c8,0x192000),(0x808e90,0x81421c,0x80000),(0x8084a6,0x808e90,0x3000),(0x802000,0x8042a6,0x50000)]:
        length=((end-source+3)//4)*4
        result[dest:dest+length]=bios[source-0x800000:source-0x800000+length]
        intervals.append([dest,dest+length])
    dest=0xfb2f8;resources=[]
    for i in range(4):
        source,end=struct.unpack_from('>II',bios,0x20b6+i*8)
        length=((end-source+3)//4)*4
        result[0xfb2e8+4*i:0xfb2ec+4*i]=dest.to_bytes(4,'big')
        result[dest:dest+length]=bios[source-0x800000:source-0x800000+length]
        resources.append(dict(source=hex(source),nominal_end=hex(end),destination=hex(dest),bytes_copied=length,overshoot_bytes=length-(end-source)))
        dest=(dest+length+7)&0xfffffff8
    original_patch=result[0x196446:0x196448]
    result[0xfb07c:0xfb07e]=original_patch
    result[0x196446:0x196448]=bytes.fromhex('4e75')
    # Real BSR return long remains on the private stack after RTS.
    result[0x1ffffc:0x200000]=(0x802058).to_bytes(4,'big')
    return bytes(result),dict(copy_intervals=intervals,resources=resources,patch_original_word=original_patch.hex(),resource_end=hex(dest))

def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    mapping=json.loads((session/'firmware-relocation-fullCPU-generation.json').read_text())
    out=ROOT/'verification/BIWN-firmware-relocation-CPU'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    src=ROOT/'projects/black-ice-white-noise/restoration'
    names=['biwn_firmware_relocation_cpu.c','biwn_bios_resident_install_cpu.c','biwn_media_setup_cpu.c']
    lib=out/'libfirmware-relocation.dylib'
    cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(src/n)for n in names],'-o',str(lib)]
    save(out/'protocol.json',dict(compiler=cmd,source_mapping=mapping,initial_RAM='zero-filled main RAM; arbitrary repeated-byte RAM is excluded after observed teardown failures',initial_CPU='seeded ROM802000; varied supervisor/user state and CCR',stop_PC='0x500d6',implementation_authorship='coordinator',whole_game_complete=False))
    build=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'compiler.txt').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
    runtime=Runtime(lib,mapping['instructions_decoded']);rng=random.Random(0x802000);coverage=set();results=[]
    closed=False
    try:
        for case in range(12):
            data=bytes(0x200000)
            initial=media.CPU();initial.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[0x1ff000]
            initial.pc=0x802000;initial.sr=(0x2000 if case%2 else 0)|((case%8)<<8)|(case*3%32)
            initial.usp=0x180000 if initial.sr&0x2000 else 0x1ff000
            initial.ssp=0x1ff000 if initial.sr&0x2000 else 0x1fe000
            save(out/'status.json',dict(status='running',case=case))
            left,a,n=runtime.native(data,initial,case%3,coverage)
            right,b,t=runtime.translated(data,initial,case%3,budget=300000)
            if left!=right or bytes(a)!=bytes(b) or n['hardware']!=t['hardware'] or t['status']!=8:
                save(out/'mismatch.json',dict(case=case,native_CPU=media.scheduler.cpu_dict(a),C_CPU=media.scheduler.cpu_dict(b),native_hardware=n['hardware'],C_hardware=t['hardware'],status=t['status'],errors=t['errors'],RAM_differences=[hex(i)for i,(x,y)in enumerate(zip(left,right))if x!=y][:30]))
                raise AssertionError(str(out/'mismatch.json'))
            expected,spans=expected_ram(data,runtime.bios)
            assert expected==right,[hex(i)for i,(x,y)in enumerate(zip(expected,right))if x!=y][:30]
            assert b.pc==0x500d6 and b.registers[15]==0x200000
            results.append(dict(case=case,initial_CPU=media.scheduler.cpu_dict(initial),final_CPU=media.scheduler.cpu_dict(b),RAM_sha256=sha(right),hardware=t['hardware'],native_instructions=n['CPU_steps'],exact_source_copy_and_patch_RAM=True,spans=spans))
            save(out/'cases.json',results)
        selected={row['address']for row in mapping['instructions_decoded']};assert coverage==selected
        save(out/'status.json',dict(status='comparisons_matched_pending_emulator_shutdown'))
        runtime.oracle.close();closed=True
        report=dict(status='actual_ROM_bootstrap_relocation_to_RAM_entry_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(results),source_instruction_coverage=[len(coverage),len(selected)],natural_jump_PC='0x500d6',ROM_entry_PC='0x802000',BIOS_sha256=mapping['BIOS_sha256'],source_sha256=mapping['source_sha256'],generator_sha256=mapping['generator_sha256'],test_script_sha256=sha(Path(__file__).read_bytes()),compiler=cmd,implementation_authorship='coordinator',local_model_authored_bodies_added=0,whole_game_complete=False,full_firmware_boot_verified=False,linked_into_game_startup=False,emulator_shutdown_completed=True,initial_RAM_domain='zero-filled main RAM',limits=['Supplied initial ROM802000 CPU/zero-filled RAM/device fixtures; actual source relocations, BSR/RTS, resources and patch execute, stopping before relocated main500D6. Repeated-byte RAM comparison runs matched states but crashed during graphics teardown; those runs are not clean passes and their cause remains unresolved.', 'Fresh original/C comparisons share pinned CPU bus/peripheral implementation; complete CPU/SR/both stack banks/private2MB RAM/peripherals/controller baseline+9byte extension match. GPU/DSP do not execute; firmware authentication/header processing/disc loading/natural game dispatch/global physical timing remain unverified.'])
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'))
        save(ROOT/'verification/firmware-relocation-CPU-checks.json',report)
        print(json.dumps(dict(status=report['status'],directory=str(out),cases=len(results),coverage=report['source_instruction_coverage'])))
    except BaseException as error:
        save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:
        if not closed:runtime.oracle.close()

if __name__=='__main__':main()
