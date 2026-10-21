"""Original mainGPU entry from sourceE00A establishes resident IRQ context.

Host installs exactly the preserved159words and entryF03224 from CPUsource;
BIOS3000 and full CPU startup are not executed or claimed here.
"""
import ctypes as c,json,struct,hashlib
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_movie_source_overlay_AV as overlay
ROOT=overlay.ROOT;save=overlay.save;sha=overlay.sha

def main():
    proof=json.loads((ROOT/'verification/BIWN-movie-source-overlay-AV.json').read_text());session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    maps=[json.loads((session/n).read_text())['instructions_decoded'] for n in ['movie-fullCPU-generation.json','video-fullCPU-generation.json','media-setup-fullCPU-generation.json']];rows=sum(maps,[])
    runtime=overlay.Runtime(Path(proof['directory'])/'libcontroller-AV.dylib',rows,*maps);out=ROOT/'verification/BIWN-main-GPU-boot-original'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    try:
        ram=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();runtime.mode='native';runtime.reset(ram,0)
        destination,dbra=struct.unpack('>II',ram[0x40a0:0x40a8]);payload=ram[0x40a8:0x40a8+4*(dbra+1)];assert (destination,dbra,len(payload))==(0xf03000,158,636)
        c.memmove(runtime.core.GPUGetRAM(),payload,len(payload));runtime.core.GPUWriteLong(0xf02100,0,6);runtime.core.GPUWriteLong(0xf02110,0xf03224,6);runtime.core.GPUWriteLong(0xf02114,1,6)
        before,before_state=overlay.video.gpu_state(runtime.core);pcs=[];delays=0;states=[];code=c.string_at(runtime.core.GPUGetRAM(),4096)
        for _ in range(10000):
            pc=runtime.core.GPUGetPC()
            if pc==0xf031ce and runtime.core.GPUReadLong(0xf03204,6)==0xffffffff and runtime.core.GPUReadLong(0xf03200,6)==0:break
            pcs.append(pc);word=int.from_bytes(code[pc-0xf03000:pc-0xf03000+2],'big');runtime.core.GPUExec(1)
            if word>>10 in [52,53] and runtime.core.GPUGetPC()!=pc+2:delays+=1
        else:raise AssertionError(('MainGPUstartup bound',hex(pc)))
        after,after_state=overlay.video.gpu_state(runtime.core);(out/'before-GPU.bin').write_bytes(before);(out/'after-GPU.bin').write_bytes(after);(out/'source-program.bin').write_bytes(payload)
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='original_mainGPU_source_entry_to_idle_captured_C_unverified',directory=str(out),before_GPU=before_state,after_GPU=after_state,source_words=dbra+1,source_payload_sha256=sha(payload),PCs=pcs,direct_blocks=len(pcs),mandatory_delay_instructions=delays,source_instructions=len(pcs)+delays,GPU_IRQ0_enabled=bool(after_state['flags_raw']&0x10),CPU_source_entry='E00A writes PCF03224/GO1 after159wordcopy and BIOS3000',BIOS3000_executed=False,C_mainGPU_boot_verified=False,whole_game_complete=False)
        save(out/'report.json',report);save(ROOT/'verification/BIWN-main-GPU-boot-original.json',report);print(json.dumps(dict(directory=str(out),blocks=len(pcs),delays=delays,after={k:v for k,v in after_state.items() if k!='registers'})))
    finally:runtime.oracle.close()
if __name__=='__main__':main()
