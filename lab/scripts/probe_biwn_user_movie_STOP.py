"""Original user STOP privilege handler and nested GPU IRQ/RTE path."""
import ctypes as c,json,struct
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_media_setup_cpu as media
ROOT=media.ROOT;save=media.save;sha=media.sha

def main():
    previous=json.loads((ROOT/'verification/BIWN-movie-source-boot-exit-AV.json').read_text());runtime=media.Runtime(Path(previous['directory'])/'libcontroller-AV.dylib',[])
    out=ROOT/'verification/BIWN-user-movie-STOP-original'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    try:
        ram=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();runtime.reset(ram,0);runtime.core.TOMSetPendingGPUInt.argtypes=[]
        runtime.device.direct(0x100,4,0xe7d4);runtime.device.direct(0xf000e0,2,0x303);runtime.device.direct(0x180000,4,0x190000);runtime.device.direct(0xbd850,2,0)
        initial=media.CPU();initial.pc=0x22a0e;initial.sr=0;initial.registers[15]=initial.usp=0x180000;initial.ssp=0x200000;initial.registers[8]=0xbd850;initial.registers[0]=0x12345678;runtime.seed_cpu(initial)
        snapshots=[];pcs=[]
        def snapshot(label):
            cpu=runtime.cpu();snapshots.append(dict(label=label,CPU=media.scheduler.cpu_dict(cpu),supervisor_tail=runtime.device.ram()[0x1fffc0:].hex(),RAM_sha256=sha(runtime.device.ram())))
        snapshot('before_user_STOP');runtime.core.m68k_execute(1);pcs.append(0x22a0e);snapshot('privilege_entered')
        assert runtime.core.m68k_get_reg(None,16)==0xddfe
        runtime.core.m68k_execute(1);pcs.append(0xddfe);snapshot('handler_STOP')
        runtime.core.TOMSetPendingGPUInt();runtime.core.m68k_set_irq(2);snapshot('GPU_IRQ_entered')
        for _ in range(100):
            pc=runtime.core.m68k_get_reg(None,16)
            if pc==0x190000:break
            assert pc in [0xde02,0xde06,0x22a10,0x22a12,0x22a14,0x22a16] or 0xe7d4<=pc<=0xe820,hex(pc)
            pcs.append(pc);runtime.core.m68k_execute(1)
            if pc in [0xe820,0xde02,0xde06,0x22a10]:snapshot('after_'+hex(pc))
        else:raise AssertionError('User STOP return bound')
        snapshot('helper_returned')
        report=dict(status='original_user_STOP_privilege_wait_nested_GPU_IRQ_return_captured_C_unverified',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),PCs=pcs,snapshots=snapshots,initial_CPU=media.scheduler.cpu_dict(initial),whole_game_complete=False)
        save(out/'report.json',report);save(ROOT/'verification/BIWN-user-movie-STOP-original.json',report);print(json.dumps(dict(directory=str(out),PCs=[hex(x) for x in pcs],events=[dict(label=x['label'],PC=hex(x['CPU']['pc']),SR=hex(x['CPU']['sr']),SP=hex(x['CPU']['registers'][15])) for x in snapshots])))
    finally:runtime.oracle.close()
if __name__=='__main__':main()
