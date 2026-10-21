"""Host error contracts for video CPU, STOP and GPU interrupt event APIs."""
import ctypes as c,json
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_video_cpu_gpu as video
ROOT=video.ROOT;save=video.save;sha=video.sha

def main():
    proof=json.loads((ROOT/'verification/BIWN-full-video-CPU-GPU.json').read_text());session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'video-fullCPU-generation.json').read_text())
    runtime=video.Runtime(Path(proof['directory'])/'libvideo-CPU-GPU.dylib',mapping['instructions_decoded']);out=ROOT/'verification/BIWN-video-CPU-guards'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);base=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rows=[]
    try:
        tests=[dict(kind='missing',field=f) for f in ['read8','read16','read32','write16','write32']]+[dict(kind=k) for k in ['null_bus','null_CPU','null_write8','null_service','zero_budget','bad_stop_flag','bad_PC','budget_one','STOP_suspend','STOP_unimplemented','privilege']]
        for item in tests:
            runtime.start(base,0,'C');s=video.media.CPU();s.registers[:]=[0]*15+[0x1ff000];s.ssp=0x1ff000;s.usp=0x1fe000;s.sr=0x2000;s.pc=0x22780;runtime.device.direct(s.registers[15],4,video.STOP);bus=video.media.Bus.from_buffer_copy(bytes(runtime.bus));kind=item['kind']
            if kind=='missing':setattr(bus,item['field'],type(getattr(bus,item['field']))())
            if kind=='bad_PC':s.pc=0
            if kind.startswith('STOP'):s.pc=0x22a0e
            if kind=='privilege':s.pc=0xe7d0;s.sr=0x700
            before=bytes(s);status=runtime.video(None if kind=='null_bus' else c.byref(bus),None if kind=='null_CPU' else c.byref(s),video.media.W8() if kind=='null_write8' else runtime.callbacks[5],video.media.world_cpu.SERVICE() if kind=='null_service' else runtime.service,None,0 if kind=='zero_budget' else 1 if kind=='budget_one' else 10000,2 if kind=='bad_stop_flag' else 0 if kind=='STOP_unimplemented' else 1)
            expected=7 if kind=='bad_PC' else 4 if kind=='budget_one' else 6 if kind=='STOP_suspend' else 8 if kind=='STOP_unimplemented' else 9 if kind=='privilege' else 1
            assert status==expected and bytes(s)==before,(kind,status);rows.append(dict(test=item,status=status,CPU_unchanged=True))
        for kind in ['null_CPU','bad_PC','privilege','valid']:
            s=video.media.CPU();s.pc=0x22a0e;s.sr=0x2700;s.registers[15]=0x1ff000;s.ssp=0x1ff000
            if kind=='bad_PC':s.pc=0
            if kind=='privilege':s.sr=0x700
            before=bytes(s);status=runtime.stop(None if kind=='null_CPU' else c.byref(s));expected=0 if kind=='valid' else 9 if kind=='privilege' else 1
            assert status==expected
            if status:assert bytes(s)==before
            else:assert s.pc==0x22a12 and s.sr==0x2000 and s.registers[15]==0x1ff000
            rows.append(dict(STOP_event=kind,status=status))
        for kind in ['null_bus','null_CPU','bad_PC','user_mode','bad_vector','masked','valid']:
            runtime.start(base,0,'C');s=video.media.CPU();s.pc=0x22a12;s.sr=0x2000;s.registers[15]=0x1ff000;s.ssp=0x1ff000;s.usp=0x1fe000;runtime.device.direct(0x100,4,0xe7d4)
            if kind=='bad_PC':s.pc=0
            if kind=='user_mode':s.sr=0x700
            if kind=='bad_vector':runtime.device.direct(0x100,4,0)
            if kind=='masked':s.sr=0x2700
            before=bytes(s);status=runtime.interrupt(None if kind=='null_bus' else c.byref(runtime.bus),None if kind=='null_CPU' else c.byref(s));expected=7 if kind=='bad_vector' else 0 if kind in ['masked','valid'] else 1
            assert status==expected
            if kind!='valid':assert bytes(s)==before
            else:
                assert s.pc==0xe7d4 and s.sr==0x2200 and s.ssp==0x1feffa
                assert runtime.device.ram()[0x1feffa:0x1ff000]==bytes.fromhex('200000022a12')
            rows.append(dict(GPU_interrupt_event=kind,status=status))
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='video_CPU_STOP_and_GPU_interrupt_contracts_checked',directory=str(out),host_guards=len(rows),rows=rows,source_sha256=proof['source_sha256'],script_sha256=sha(Path(__file__).read_bytes()),whole_game_complete=False,new_published_components=0)
        save(out/'report.json',report);save(ROOT/'verification/BIWN-video-CPU-guards.json',report);save(out/'status.json',dict(status='terminal_pass'));print(json.dumps(dict(directory=str(out),guards=len(rows))))
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:runtime.oracle.close()

if __name__=='__main__':main()
