"""Original CPU D3EC and GPU IRQ0 vector/handler to resident idle.

Boot/movie start use source GPU programs under declared fixture scheduling.
CD firmware/globalgameplay remain separate.
"""
import ctypes as c,json,struct
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_movie_source_overlay_AV as overlay
ROOT=overlay.ROOT;save=overlay.save;sha=overlay.sha

def main():
    source_proof=json.loads((ROOT/'verification/BIWN-movie-source-overlay-AV.json').read_text());session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);maps=[json.loads((session/n).read_text())['instructions_decoded'] for n in ['movie-fullCPU-generation.json','video-fullCPU-generation.json','media-setup-fullCPU-generation.json']]
    rows=sum(maps,[])+[x for x in json.loads((session/'geometry-records-fullCPU-generation.json').read_text())['instructions_decoded'] if 0xe098<=x['address']<0xe0a6]
    runtime=overlay.Runtime(Path(source_proof['directory'])/'libcontroller-AV.dylib',rows,*maps);out=ROOT/'verification/BIWN-movie-exit-GPU-original'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    try:
        base=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());base[0x21ea8:0x22770]=(session/'media-video-gpu-21ea0/original-overlay.bin').read_bytes();runtime.start(bytes(base),0,'native')
        program=bytes(base[0x40a8:0x4324]);c.memmove(runtime.core.GPUGetRAM(),program,636);runtime.core.GPUWriteLong(0xf02110,0xf03224,6);runtime.core.GPUWriteLong(0xf02114,1,6)
        for _ in range(100):
            if runtime.core.GPUGetPC()==0xf031ce and runtime.core.GPUReadLong(0xf03204,6)==0xffffffff and runtime.core.GPUReadLong(0xf03200,6)==0:break
            runtime.core.GPUExec(1)
        else:raise AssertionError('Boot bound')
        request=overlay.media.CPU();request.registers[15]=0x1ff000;request.ssp=0x1ff000;request.usp=0x1fe000;request.pc=0xd3c6;request.sr=0x2700;runtime.device.direct(request.registers[15],4,overlay.controller.STOP);runtime.run_native(request,set())
        before,before_state=overlay.video.gpu_state(runtime.core)
        request.pc=0xd3ec;request.registers[15]=0x1ff000;request.ssp=0x1ff000;runtime.device.direct(request.registers[15],4,overlay.controller.STOP);cpu,steps=runtime.run_native(request,set())
        entered,entered_state=overlay.video.gpu_state(runtime.core);pcs=[];delays=0;code=c.string_at(runtime.core.GPUGetRAM(),4096)
        for _ in range(1000):
            pc=runtime.core.GPUGetPC()
            if pc==0xf031ce and runtime.core.GPUReadLong(0xf03204,6)==0xffffffff and runtime.core.GPUReadLong(0xf03200,6)==0:break
            pcs.append(pc);word=int.from_bytes(code[pc-0xf03000:pc-0xf03000+2],'big');runtime.core.GPUExec(1)
            if word>>10 in [52,53] and runtime.core.GPUGetPC()!=pc+2:delays+=1
        else:raise AssertionError(('Movieexit GPU bound',hex(pc)))
        after,after_state=overlay.video.gpu_state(runtime.core)
        for name,data in [('before-GPU',before),('IRQ-entered-GPU',entered),('after-GPU',after),('executed-GPU-code',code)]: (out/(name+'.bin')).write_bytes(data)
        report=dict(status='original_source_D3EC_IRQ0_handler_residentreturn_captured_C_unverified',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),before_GPU=before_state,IRQ_entered_GPU=entered_state,after_GPU=after_state,PCs=pcs,direct_blocks=len(pcs),mandatory_delays=delays,instructions=len(pcs)+delays,source_CPU=overlay.media.scheduler.cpu_dict(cpu),source_CPU_steps=steps,BIOS3000_executed=False,whole_game_complete=False)
        save(out/'report.json',report);save(ROOT/'verification/BIWN-movie-exit-GPU-original.json',report)
        print(json.dumps(dict(directory=str(out),before_flags=hex(before_state['flags_raw']),IRQ_PC=hex(entered_state['pc']),IRQ_R31=hex(entered_state['registers'][0][31]),PCs=[hex(x) for x in pcs],instructions=len(pcs)+delays)))
    finally:runtime.oracle.close()
if __name__=='__main__':main()
