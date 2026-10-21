"""Explain the captured header overlap and reproduce only its entry stores."""
import ctypes as c
from datetime import datetime, timezone
from pathlib import Path
import check_biwn_scheduler as scheduler
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha


class Row(c.Structure):
    _fields_=[('frame',c.c_uint32),('pc',c.c_uint32),('task',c.c_uint32),('cpu',scheduler.CPU),('resource',c.c_uint64),('input',c.c_uint64),('aliases',c.c_uint64)]


def main():
    trace_path=V/'v39-input-transition-fault-trace-v2-current.json';trace=read(trace_path)
    assert trace['status']=='terminal_transition_diagnostic_fault_recorded'
    for path,digest in trace['source_sha256'].items():assert sha(path)==digest,path
    folder=Path(trace['directory']);ring=folder/'instruction-ring.bin';raw=ring.read_bytes()
    assert c.sizeof(Row)==trace['fault']['row_bytes']==120 and len(raw)==2048*120
    rows=[Row.from_buffer_copy(raw[i:i+120])for i in range(0,len(raw),120)]
    odd=next(r for r in rows if r.pc&1);entries=[r for r in rows if r.pc==0x162730]
    assert len(entries)==2 and odd.frame==8959 and odd.pc==0x4f13
    user=[r for r in rows if not r.cpu.sr&0x2000];low=min(user,key=lambda r:r.cpu.registers[15])
    assert low.cpu.registers[15]==0xc209e and low.task==0xc2128
    build_path=V/'native-input-arena-disc-build-v1-current.json';build=read(build_path)
    resident=Path(build['component']).read_bytes();base=build['resident_address']
    assert resident[0x16272c-base:0x162734-base]==bytes.fromhex('4feffe0048d77fff')
    out=V/'v39-frame-acquire-header-fault-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    memory_path=folder/'candidate/diagnostic-RAM.bin';captured=memory_path.read_bytes();native=scheduler.Native()
    cases=[]
    try:
        for index,r in enumerate(entries):
            task,sp=r.task,r.cpu.registers[15]
            assert task==0xc2128 and sp==task-26
            memory=bytearray(captured)
            # Distinct fixture bytes make every metadata byte's overwrite visible.
            expected_registers=b''.join(x.to_bytes(4,'big')for x in r.cpu.registers[:15])
            memory[task:task+38]=bytes(x^0xff for x in (expected_registers[26:60]+(sp+556).to_bytes(4,'big')))
            before=bytes(memory);expected=bytearray(memory)
            expected[sp:sp+60]=expected_registers
            expected[sp+60:sp+64]=(sp+556).to_bytes(4,'big')
            expected[sp+64:sp+66]=bytes(2)
            expected[sp+66:sp+68]=r.cpu.sr.to_bytes(2,'big')
            native.device.seed(before,0);core=native.lib;core.m68k_pulse_reset();core.m68k_set_irq(0)
            core.m68k_set_reg(17,0x2000);core.m68k_set_reg(15,r.cpu.ssp);core.m68k_set_reg(17,0);core.m68k_set_reg(15,r.cpu.usp);core.m68k_set_reg(17,r.cpu.sr)
            for i,value in enumerate(r.cpu.registers):core.m68k_set_reg(i,value)
            core.m68k_set_reg(16,r.pc);executed=[]
            while core.m68k_get_reg(None,16)!=0x162744:
                pc=core.m68k_get_reg(None,16);assert len(executed)<6 and 0x162730<=pc<0x162744
                executed.append(pc);core.m68k_execute(1)
            actual=native.device.ram();assert actual==expected,'Entry stores differ from full-RAM oracle'
            assert core.m68k_get_reg(None,8)==sp+556 and core.m68k_get_reg(None,15)==sp
            assert all(core.m68k_get_reg(None,i)==r.cpu.registers[i]for i in range(16)if i!=8)
            changed=[i for i,(a,b)in enumerate(zip(before[task:task+38],actual[task:task+38]))if a!=b]
            assert changed==list(range(38))
            cases.append(dict(captured_entry=index,source_frame=r.frame,task=task,entry_stack=sp,logical_context_starts_before_task_bytes=26,metadata_bytes_overwritten=38,full_RAM_oracle_equal=True,instructions=executed,fixture_header_pattern=True))
    finally:native.close()
    detail=dict(status='terminal_actual_captured_frame_acquire_entry_overwrites_all38_task_metadata_bytes',directory=str(out),captured_frame=8959,first_odd_PC=odd.pc,frame_end_loop_PC=trace['fault']['pc'],task=low.task,minimum_observed_user_SP=low.cpu.registers[15],minimum_SP_below_task_bytes=138,frame_acquire_context=entries[0].cpu.registers[15],frame_acquire_context_before_task_bytes=26,frame_acquire_reserve=512,original_task_metadata_bytes=38,isolated_native_entry_cases=2,metadata_bytes_overwritten_each_case=38,full_RAM_oracle_equal=True,source_defect_identified=True,all_failure_causes_resolved=False,fix_implemented=False,new_image_built=False,fresh_replay_fixed=False,production_guest_state_modified=False,scope='Actual fresh instruction ring contains two compiled1AC68entries with context at task-26. Executed MOVEM stores overlap first34metadata bytes; logical-SP store overlaps last4. Two isolated entry-store replays on pinnedCPU reproduce all38byte overwrites and match entire2MBoracle. These use an explicit fixture header pattern,not a patched gameplay continuation. The captured scheduler later follows corrupted task links before the odd-PC exception loop. No fix or full-game equivalence is claimed.',source_sha256={str(p):sha(p)for p in [Path(__file__),trace_path,ring,memory_path,build_path,Path(build['component']),ROOT/'projects/black-ice-white-noise/restoration/native-m68k/frame-acquire-lean-shim.S']})
    save(out/'entry-cases.json',cases);detail['source_sha256'][str(out/'entry-cases.json')]=sha(out/'entry-cases.json')
    save(out/'review.json',detail);save(V/'v39-frame-acquire-header-fault-reviewed-v1-current.json',detail)
    print(detail['status'],flush=True)


if __name__=='__main__':main()
