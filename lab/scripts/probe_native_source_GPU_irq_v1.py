"""Probe actual core/TOM delivery to the game's installed GPU IRQ handler."""
import ctypes as c
import os
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_scheduler as scheduler
from publish_scene_reset_fresh_v1 import ROOT,V,save,sha


def main():
    out=V/'native-source-GPU-irq-probe-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    n=scheduler.Native();core=n.lib;dev=n.device
    state=dict(status='probing',directory=str(out),pid=os.getpid(),new_predictions=0,optimizer_updates=0)
    try:
        memory=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes())
        memory[0x6000:0x6004]=bytes.fromhex('4e714e71');memory[0x100:0x104]=(0xe7d4).to_bytes(4,'big')
        dev.seed(bytes(memory),0);core.m68k_pulse_reset();core.m68k_set_irq(0)
        core.m68k_set_reg(17,0x2000);core.m68k_set_reg(15,0x1d0000);core.m68k_set_reg(17,0);core.m68k_set_reg(15,0xc0d00);core.m68k_set_reg(16,0x6000)
        core.TOMWriteWord.argtypes=[c.c_uint32,c.c_uint16,c.c_uint32];core.TOMReadWord.argtypes=[c.c_uint32,c.c_uint32];core.TOMReadWord.restype=c.c_uint16
        core.TOMSetPendingGPUInt.argtypes=[];core.TOMIRQRequestActive.restype=c.c_int
        core.TOMWriteWord(0xf000e0,3,0);core.TOMSetPendingGPUInt();core.m68k_set_irq(2)
        pending=core.TOMReadWord(0xf000e0,0);active=core.TOMIRQRequestActive();steps=[]
        for _ in range(100):
            pc=core.m68k_get_reg(None,16);sr=core.m68k_get_reg(None,17);sp=core.m68k_get_reg(None,15)
            if steps and pc==0x6000 and not sr&0x2000:break
            assert pc==0x6000 or 0xe7d4<=pc<0xe822,hex(pc)
            steps.append(dict(PC=pc,SR=sr,SP=sp));core.m68k_execute(1)
        else:raise AssertionError('IRQ did not resume interrupted PC')
        assert any(0xe7d4<=r['PC']<0xe822 for r in steps)
        assert dev.read(0xbd850,2)==0xffff
        assert core.m68k_get_reg(None,15)==0xc0d00 and n.prefix[17]==0x1d0000
        state.update(status='terminal_actual_TOM_GPU_pending_level2_vector64_source_handler_RTE_resumes',initial_INT1=pending,initial_TOM_request=active,final_INT1=core.TOMReadWord(0xf000e0,0),final_TOM_request=core.TOMIRQRequestActive(),steps=steps,source_GPU_IRQ_flag=dev.read(0xbd850,2),source_handler=0xe7d4,resolved_vector=64,source_sha256={str(p):sha(p)for p in [Path(__file__),Path(scheduler.__file__),ROOT/'render-assets/biwn-inventory-baseline.bin',ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib']},scope='OneexplicitTOMGPU-pendingeventwithINT1enable3andCPUlevel2. Actualnativeexceptionentry/sourcehandler/RTE,no fabricatedframe. IdleNOPboundaryonly;notresourcearena,firmwarebit0,arbitraryIRQorconsolequalification.')
    except BaseException as error:
        state.update(status='terminal_native_GPU_irq_probe_failed',error=repr(error));raise
    finally:
        save(out/'protocol.json',state);save(V/'native-source-GPU-irq-probe-v1-current.json',state);n.close()
    print({k:state[k]for k in ['status','initial_INT1','final_INT1','final_TOM_request']},flush=True)


if __name__=='__main__':main()
