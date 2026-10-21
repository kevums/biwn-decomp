"""Inspect actual source D3EC forced-GPU-IRQ under the current startup fixture.

No rebuilt shutdown acceptance: this probe identifies inherited boot state
required before reconstructing movie exit and complete D3FC caller.
"""
import ctypes as c,json
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_movie_source_overlay_AV as overlay
ROOT=overlay.ROOT;save=overlay.save

def main():
    proof=json.loads((ROOT/'verification/BIWN-movie-source-overlay-AV.json').read_text());session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    maps=[json.loads((session/n).read_text())['instructions_decoded'] for n in ['movie-fullCPU-generation.json','video-fullCPU-generation.json','media-setup-fullCPU-generation.json']]
    geometry=json.loads((session/'geometry-records-fullCPU-generation.json').read_text())['instructions_decoded'];rows=sum(maps,[])+[x for x in geometry if 0xe098<=x['address']<0xe0a6]
    runtime=overlay.Runtime(Path(proof['directory'])/'libcontroller-AV.dylib',rows,*maps)
    out=ROOT/'verification/BIWN-movie-shutdown-context'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    try:
        ram=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());ram[0x21ea8:0x22770]=(session/'media-video-gpu-21ea0/original-overlay.bin').read_bytes();runtime.start(bytes(ram),0,'native')
        before_raw,before=overlay.video.gpu_state(runtime.core);counter=runtime.gpu_counter.value
        state=overlay.media.CPU();state.registers[15]=0x1ff000;state.ssp=0x1ff000;state.usp=0x1fe000;state.pc=0xd3ec;state.sr=0x2700;runtime.device.direct(state.registers[15],4,overlay.controller.STOP)
        cpu,steps=runtime.run_native(state,set());after_raw,after=overlay.video.gpu_state(runtime.core)
        (out/'before-GPU.bin').write_bytes(before_raw);(out/'after-GPU.bin').write_bytes(after_raw)
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),status='source_shutdown_under_current_fixture_inspected_not_rebuilt_acceptance',before_GPU=before,after_GPU=after,CPU=overlay.media.scheduler.cpu_dict(cpu),native_CPU_steps=steps,original_GPU_instructions=runtime.gpu_counter.value-counter,
            source_D3EC_control_write='0x5',GPU_IRQ0_enabled=bool(before['flags_raw']&0x10) if 'flags_raw' in before else None,rebuilt_shutdown_verified=False,whole_game_complete=False,
            next_work='Establish original source mainGPU boot/IRQ enable context, then reconstruct forcedGPU IRQ/frame/vector/residentreturn before fullD3FC caller. Do not force an IRQ merely to make current fixture exit.',source_kernel_SHA=proof['source_sha256'])
        save(out/'report.json',report);save(ROOT/'verification/movie-shutdown-dependency-inspection.json',report);print(json.dumps(dict(directory=str(out),before={k:v for k,v in before.items() if k not in ['registers']},after={k:v for k,v in after.items() if k not in ['registers']})))
    finally:runtime.oracle.close()
if __name__=='__main__':main()
