"""Replay captured reference OP slices as isolated component fixtures."""
import ctypes as c,json,hashlib,struct
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_movie_source_overlay_AV as overlay
import check_biwn_movie_GPU as GPU
from check_biwn_main_GPU_boot import Bus,W16
ROOT=overlay.ROOT

def main():
    origin=Path((ROOT/'runs/OP-GPU-native-slice-trace.log').read_text().splitlines()[0])/'OP-GPU-reference-slices';reference=json.loads((origin/'report.json').read_text());candidate=json.loads((ROOT/'verification/OP-GPU-slice-candidate.json').read_text());out=ROOT/'verification/OP-GPU-slice-checks'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);old=json.loads((ROOT/'verification/BIWN-movie-source-overlay-AV.json').read_text());maps=[json.loads((session/(n+'-fullCPU-generation.json')).read_text())['instructions_decoded']for n in ['movie','video','media-setup']];runtime=overlay.Runtime(Path(old['directory'])/'libcontroller-AV.dylib',sum(maps,[]),*maps);core=runtime.core
    lib=c.CDLL(candidate['library']);fn=lib.biwn_gpu_OP_slice_run;fn.argtypes=[c.POINTER(Bus),c.POINTER(GPU.State),c.c_uint32];fn.restype=c.c_int
    results=[]
    try:
        for row in reference['records'][:64]:
            stem=f'{row["index"]:06d}';initial=(origin/(stem+'-before-GPU.bin')).read_bytes();RAM=(origin/(stem+'-before-RAM.bin')).read_bytes();expected=(origin/(stem+'-after-GPU.bin')).read_bytes()[:4396];expected_RAM=(origin/(stem+'-after-RAM.bin')).read_bytes();runtime.mode='native';runtime.gpu=None;runtime.reset(RAM,row['index']%3);assert core.GPUStateLoad(c.create_string_buffer(initial))==4416
            state=GPU.state_from_raw(initial);trace=[];writes=[]
            callbacks=[GPU.R16(lambda _,a,v:(v.__setitem__(0,core.GPUReadWord(a,3)),0)[1]),GPU.R32(lambda _,a,v:(v.__setitem__(0,core.GPUReadLong(a,3)),0)[1]),W16(lambda _,a,v:(writes.append([a,2,v]),core.GPUWriteWord(a,v,3),0)[-1]),GPU.W32(lambda _,a,v:(writes.append([a,4,v]),core.GPUWriteLong(a,v,3),0)[-1]),GPU.OBS(lambda _,pc:trace.append(pc))];bus=Bus(*callbacks,None);before=runtime.gpu_counter.value
            status=fn(c.byref(bus),c.byref(state),row['cycles']);actual=GPU.logical(state);good=status==0 and actual==expected and runtime.device.ram()==expected_RAM and runtime.gpu_counter.value==before
            if not good:
                report=dict(status='rejected_OP_GPU_slice',case=row['index'],source_PC=hex(row['before_PC']),expected_PC=hex(row['after_PC']),actual_PC=hex(state.pc),return_status=status,GPU_differences=[i for i,(a,b)in enumerate(zip(actual,expected))if a!=b],RAM_match=runtime.device.ram()==expected_RAM,trace=list(map(hex,trace)),writes=writes,original_GPU_opcode_delta=runtime.gpu_counter.value-before);(out/'mismatch.json').write_text(json.dumps(report,indent=2)+'\n');(out/'actual-GPU.bin').write_bytes(actual);(out/'expected-GPU.bin').write_bytes(expected);raise AssertionError(str(out/'mismatch.json'))
            results.append(dict(case=row['index'],source_PC=hex(row['before_PC']),actual_PC=hex(state.pc),instructions=state.instructions,outer_instructions=len(trace),full_GPU_RAM_match=True))
        report=dict(status='first64captured_OP_GPU_slices_full_GPU_and_RAM_match',directory=str(out),reference=str(origin),candidate=candidate['library'],cases=len(results),results=results,original_GPU_opcodes_on_C_side=0,fixtures_use_snapshots=True,live_game_does_not_restore_these_snapshots=True,global_cycle_scheduling_verified=False,limits=['First64original16cycleOP-requested slices only, with current disabled pipeline/DRAM timing profile. Remaining live calls, flags and queue integration separate.'])
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/OP-GPU-slice-check-current.json').write_text(json.dumps(report,indent=2)+'\n');print(out)
    finally:runtime.oracle.close()
if __name__=='__main__':main()
