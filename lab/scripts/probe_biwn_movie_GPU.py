"""Capture source movie GPU self-relocation before interpreting main code/data."""
import ctypes as c,json,struct
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_media_setup_cpu as media
from probe_biwn_gpu_projection import gpu_state
ROOT=media.ROOT;save=media.save;sha=media.sha

def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);folder=session/'media-video-gpu-21ea0';payload=(folder/'original-overlay.bin').read_bytes()
    mapping=json.loads((folder/'initial-linear-decode.json').read_text());assert sha(payload)==mapping['payload_sha256']
    setup=json.loads((session/'media-setup-fullCPU-generation.json').read_text());proof=json.loads((ROOT/'verification/biwn-media-setup-cpu-checks.json').read_text());runtime=media.Runtime(Path(proof['directory'])/'libmedia-setup.dylib',setup['instructions_decoded'])
    out=ROOT/'verification/BIWN-movie-GPU-original'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    core=runtime.core;core.GPUExec.argtypes=[c.c_int32];core.GPUGetPC.restype=c.c_uint32;core.GPUSetPC.argtypes=[c.c_uint32];core.GPUSetFlags.argtypes=[c.c_uint32];core.GPUWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32]
    counter=c.c_uint32.in_dll(core,'gpu_exec_opcode_count');rows=[]
    try:
        runtime.reset((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes(),0)
        c.memmove(core.GPUGetRAM()+0x240,payload,len(payload));core.GPUSetFlags(0);core.GPUSetPC(0xf03258);core.GPUWriteLong(0xf02114,1,6)
        before,state=gpu_state(core);(out/'before-GPU.bin').write_bytes(before);RAM_before=sha(runtime.device.ram())
        for _ in range(20000):
            pc=core.GPUGetPC()
            if pc==0xf032c8 and rows:break
            raw=c.string_at(core.GPUGetRAM(),4096)
            assert 0xf03258<=pc<0xf032c8,hex(pc)
            word=int.from_bytes(raw[pc-0xf03000:pc-0xf03000+2],'big');size=6 if word>>10==38 else 2
            before_count=counter.value;core.GPUExec(1);delta=(counter.value-before_count)&0xffffffff
            assert delta in [1,2],(hex(pc),delta)
            rows.append(dict(pc=pc,bytes=raw[pc-0xf03000:pc-0xf03000+size].hex(),instructions=delta,after_pc=core.GPUGetPC()))
        else:raise AssertionError('Movie GPU relocation bound')
        after,state=gpu_state(core);(out/'relocated-GPU.bin').write_bytes(after)
        assert sha(runtime.device.ram())==RAM_before
        changes=[]
        for a in range(0x240,0x240+len(payload),2):
            if before[a:a+2]!=after[a:a+2]:changes.append(dict(address=hex(0xf03000+a),before=before[a:a+2].hex(),after=after[a:a+2].hex()))
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='native_movie_GPU_self_relocation_captured_C_unverified',directory=str(out),
            payload_sha256=sha(payload),source_GPU_entry='0xf03258',relocation_delta=state['registers'][0][20],after_PC=hex(state['pc']),
            instruction_blocks=len(rows),source_instructions=sum(x['instructions'] for x in rows),changed_halfwords=changes,PC_sequence=rows,
            after_logical_GPU_sha256=sha(after[:4396]),relocated_local_RAM_sha256=sha(after[:4096]),script_sha256=sha(Path(__file__).read_bytes()),
            CPU_D340_executed=False,video_frame_decoded=False,C_GPU_execution_verified=False,whole_game_complete=False,new_published_components=0)
        save(out/'report.json',report);save(ROOT/'verification/BIWN-movie-GPU-original.json',report);save(out/'status.json',dict(status='terminal_pass'))
        print(json.dumps(dict(directory=str(out),blocks=len(rows),relocation_delta=hex(report['relocation_delta']),changed_halfwords=len(changes))))
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:runtime.oracle.close()

if __name__=='__main__':main()
