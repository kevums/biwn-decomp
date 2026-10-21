"""Observe actual firstboot GPU initialization through its poll-loop boundary."""
import ctypes as c,json,struct
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_media_setup_cpu as media
import check_biwn_full_video_cpu_gpu as video
ROOT=media.ROOT;save=media.save;sha=media.sha
def main():
    s=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);boot=(s/'boot-payload-68000-candidate.bin').read_bytes();assert sha(boot)=='235b342638e4face19e82b68d1fdd6592e58dbf689792ee41d572db465cfc8a4'
    p=json.loads((ROOT/'verification/bios-marker-setup-CPU-checks.json').read_text());out=ROOT/'verification/BIWN-game-firstboot-GPU-probe'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    runtime=media.Runtime(Path(p['directory'])/'libbios-setup.dylib',[]);core=runtime.core;core.GPUGetPC.restype=c.c_uint32;core.GPUExec.argtypes=[c.c_int32];core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t
    ram=bytearray(0x200000);ram[0x180000:0x180000+len(boot)]=boot;runtime.reset(bytes(ram),0)
    raw=bytearray(video.gpu_state(core)[0]);raw[0x200:0x9d4]=boot[0x188:0x95c];bios=(ROOT/'render-assets/jaguarcd_bios.bin').read_bytes();raw[0x50:0x1a0]=bios[0x84a6+0x382:0x84a6+0x4d2];raw[0x10:0x1c]=bytes.fromhex('981e306400f0d3c0e400e400')
    regs=[0]*64;regs[31]=0xf04000;struct.pack_into('=64I',raw,4139,*regs);struct.pack_into('=I',raw,4096,0xf03200);struct.pack_into('=I',raw,4112,0x20);struct.pack_into('=I',raw,4128,1);raw[4136:4139]=bytes(3);raw[4395]=0
    assert core.GPUStateLoad(c.create_string_buffer(bytes(raw)))==len(raw);runtime.tom[6]=0;runtime.tom[7]=4
    (out/'initial-GPU.bin').write_bytes(raw);(out/'initial-RAM.bin').write_bytes(runtime.device.ram());pcs=[];coverage=set();delays=0
    try:
        for _ in range(1000000):
            pc=core.GPUGetPC()
            if pc==0xf032ce:break
            assert 0xf03200<=pc<0xf039d4,hex(pc);pcs.append(pc);coverage.add(pc);word=int.from_bytes(raw[pc-0xf03000:pc-0xf03000+2],'big');core.GPUExec(1)
            if word>>10 in [52,53] and core.GPUGetPC()!=pc+2:delays+=1;coverage.add(pc+2)
        else:raise AssertionError('Firstboot GPU initialization bound')
        final=video.gpu_state(core)[0];(out/'final-GPU.bin').write_bytes(final);(out/'final-RAM.bin').write_bytes(runtime.device.ram())
        report=dict(status='original_firstboot_GPU_initializer_to_source_poll_boundary',directory=str(out),boot_sha256=sha(boot),GPU_payload_sha256=sha(boot[0x188:0x95c]),PC_trace=pcs,selected_PC=sorted(coverage),observed_instruction_addresses=len(coverage),original_instructions=len(pcs)+delays,final_PC=hex(core.GPUGetPC()),final_GPU_sha256=sha(final[:4396]),final_RAM_sha256=sha(runtime.device.ram()),C_verified=False,limits=['Supplied initial boot payload/mainRAM/GPU code/register seed includingR31 and markerISR. Native GPU executes startup texture decode/object-list setup toF032CE. TOM VCOUNT4 is a controlled fixture; no physical video/global schedule, CPUfirstboot/complete firmware boot or stage loading proof.'])
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/game-firstboot-GPU-probe.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ['PC_trace','selected_PC']}))
    except BaseException as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error),last_PC=hex(core.GPUGetPC())));raise
    finally:runtime.oracle.close()
if __name__=='__main__':main()
