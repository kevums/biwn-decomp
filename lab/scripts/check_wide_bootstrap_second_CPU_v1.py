"""Cross-check new integrated copy/clear against pinned native M68000 core.

Only synthetic startup payloads execute; no game frame or new CDI is run.
"""
import os
from pathlib import Path
import random
import runpy
import struct
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN
from unicorn.m68k_const import *
import check_biwn_scheduler as scheduler
from check_local_wide_bootstrap_v1 import TEMPLATE,BASE,REGS
from wide_bootstrap_support_v1 import align
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha


def main():
    proof_path=V/'local-wide-bootstrap-reviewed-v1-current.json';proof=read(proof_path)
    assert proof['native_copy_cases']==56 and proof['native_integrated_cases']==18
    for path,digest in proof['source_sha256'].items():assert sha(path)==digest,path
    candidate=Path(proof['source_profile'])/'widen_loader.py';widen=runpy.run_path(str(candidate))['widen_biwn_loader']
    out=V/'wide-bootstrap-second-CPU-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    pointer=V/'wide-bootstrap-second-CPU-v1-current.json'
    state=dict(status='running_wide_copy_clear_second_CPU',directory=str(out),pid=os.getpid(),completed=0,
        new_predictions=0,optimizer_updates=0,new_disc_built=False,game_frames=0)
    def mark():save(out/'protocol.json',state);save(pointer,state)
    mark();native=scheduler.Native();rng=random.Random(0x32d822d8);rows=[];files=[]
    try:
        for size in [131072,132096,132160]:
            staging=0xfe200-align(40+size,64);clear=align(40+size,64)
            finalizer=Path(proof['directory'])/f'integrated-{size}-00000000/clear.bin'
            blob=finalizer.read_bytes();files.append(finalizer)
            payload=bytearray(rng.randbytes(size));payload[20:26]=b'\x4e\xf9'+(BASE+size-32).to_bytes(4,'big');payload[-32:-32+len(blob)]=blob
            memory=bytearray(b'\xa5'*0x200000);memory[staging:staging+40]=widen(TEMPLATE,size)
            memory[staging+40:staging+40+size]=payload;memory[staging+40+size:staging+clear]=b'\x6c'*(clear-40-size)
            initial=[rng.getrandbits(32)for _ in REGS];usp=0x1de000
            wanted=bytearray(memory);wanted[BASE:BASE+size]=payload;wanted[staging:staging+clear]=bytes(clear)
            wanted[0x200000-60:]=struct.pack('>15I',*initial)
            cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(memory))
            cpu.reg_write(UC_M68K_REG_SR,0);cpu.reg_write(UC_M68K_REG_A7,usp);cpu.reg_write(UC_M68K_REG_SR,0x231f);cpu.reg_write(UC_M68K_REG_A7,0x1fc000)
            for reg,value in zip(REGS,initial):cpu.reg_write(reg,value)
            cpu.emu_start(staging,0x400a,count=600000,timeout=10000000)
            assert cpu.reg_read(UC_M68K_REG_PC)==0x400a and bytes(cpu.mem_read(0,0x200000))==wanted
            assert [cpu.reg_read(reg)for reg in REGS]==initial and cpu.reg_read(UC_M68K_REG_A7)==0x200000 and cpu.reg_read(UC_M68K_REG_SR)==0x2700
            native.device.seed(bytes(memory),0);assert native.device.ram()==memory
            native.lib.m68k_pulse_reset();native.lib.m68k_set_irq(0)
            native.lib.m68k_set_reg(17,0);native.lib.m68k_set_reg(15,usp);native.lib.m68k_set_reg(17,0x231f);native.lib.m68k_set_reg(15,0x1fc000)
            for i,value in enumerate(initial):native.lib.m68k_set_reg(i,value)
            native.lib.m68k_set_reg(16,staging);single=batches=0;steps=0
            loop_pcs={staging+28,staging+30,BASE+size-32+10,BASE+size-32+12}
            for _ in range(20000):
                pc=native.lib.m68k_get_reg(None,16)
                if pc==0x400a:break
                assert staging<=pc<staging+40 or BASE+20<=pc<BASE+26 or BASE+size-32<=pc<BASE+size,(hex(pc),size)
                if pc in loop_pcs and (native.lib.m68k_get_reg(None,0)&65535)>1024:
                    # 1024cycle batches cannot consume1024remaining iterations;
                    # single-step the tail to stop exactly before original400A.
                    native.lib.m68k_execute(1024);batches+=1
                else:native.lib.m68k_execute(1);single+=1
                steps+=1
            else:raise AssertionError('Native startup did not reach400A')
            assert native.device.ram()==wanted,'Native complete RAM/canary mismatch'
            assert [native.lib.m68k_get_reg(None,i)for i in range(15)]==initial
            assert native.lib.m68k_get_reg(None,15)==0x200000 and native.lib.m68k_get_reg(None,17)==0x2700
            assert native.prefix[16]==usp
            stats=native.device.stats();assert not stats['game_frames_executed']and not stats['GPUExec1_calls']and not stats['device_error']
            rows.append(dict(copy_bytes=size,clear_bytes=clear,staging=staging,native_cycle_batches=batches,
                native_single_steps=single,original400A_not_executed=True,all_RAM_all_registers_SR_SSP_USP_match=True,
                expected_RAM_sha256=__import__('hashlib').sha256(wanted).hexdigest(),device=stats))
            state['completed']=len(rows);mark()
        save(out/'cases.json',rows)
        state.update(status='terminal_wide_copy_clear_native_and_Unicorn_full_RAM_CPU_match',completed=3,
            prospective_v34_and_v37_sizes_verified=True,source_model_function_unedited=True,
            physical_console_verified=False,game_image_qualified=False,
            source_sha256={str(path):sha(path)for path in [Path(__file__),proof_path,candidate,Path(scheduler.__file__),
                ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib',out/'cases.json',*files]},
            scope='Threefreshsyntheticstartupcases131072/132096/132160copybytes. ActualpinnedM68000andUnicornexecutecopy/longclear/GPRrestoreto400A;entireRAM/canaries/allGPR/SR/SSP/USPmatchoracle. No gameframes,GPUororiginal400Aexecution;not module/arena/heaprelink or freshgame/consolequalification.')
        mark();print(state['status'],3,flush=True)
    except BaseException as error:
        save(out/'completed-before-failure.json',rows);state.update(status='terminal_wide_startup_second_CPU_failed',error=repr(error));mark();raise
    finally:native.close()


if __name__=='__main__':main()
