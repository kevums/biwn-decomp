"""Replay the captured actor-init C-call prelude against an independent RAM oracle."""
import ctypes as c
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_scheduler as scheduler
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha


class Row(c.Structure):
    _fields_=[('frame',c.c_uint32),('pc',c.c_uint32),('task',c.c_uint32),('cpu',scheduler.CPU),('resource',c.c_uint64),('input',c.c_uint64),('aliases',c.c_uint64)]


def main():
    tp=V/'v40-input-transition-fault-trace-v2-current.json';trace=read(tp)
    assert trace['status']=='terminal_transition_diagnostic_fault_recorded'
    for p,h in trace['source_sha256'].items():assert sha(p)==h,p
    folder=Path(trace['directory']);ring=folder/'instruction-ring.bin';raw=ring.read_bytes()
    rows=[Row.from_buffer_copy(raw[i:i+c.sizeof(Row)])for i in range(0,len(raw),c.sizeof(Row))]
    before=next(r for r in rows if r.pc==0x163f08);detected=rows[-1]
    assert before.frame==detected.frame==8978 and before.task==detected.task==0xc2128
    assert before.cpu.registers[15]==before.task+40 and detected.pc==0x163f0a and detected.cpu.registers[15]==before.task+36
    memory_path=folder/'first-watch-RAM.bin';captured=memory_path.read_bytes()
    bp=V/'frame-acquire-phased-disc-build-v1-current.json';build=read(bp)
    assert captured[0x163f08:0x163f0e]==bytes.fromhex('2f0f6100fab8')
    out=V/'v40-actor-init-header-fault-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    n=scheduler.Native();memory=bytearray(captured);task=before.task;sp=before.cpu.registers[15]
    # These fixture bytes reveal each clobbered byte. No gameplay state is repaired.
    header=bytes((i*41+0x53)%256 for i in range(38));memory[task:task+38]=header
    expected=bytearray(memory);initial=bytes(memory);core=n.lib;results=[]
    try:
        n.device.seed(initial,0);core.m68k_pulse_reset();core.m68k_set_irq(0)
        core.m68k_set_reg(17,0x2000);core.m68k_set_reg(15,before.cpu.ssp);core.m68k_set_reg(17,0);core.m68k_set_reg(15,before.cpu.usp);core.m68k_set_reg(17,before.cpu.sr)
        for i,value in enumerate(before.cpu.registers):core.m68k_set_reg(i,value)
        core.m68k_set_reg(16,before.pc)
        expected[sp-4:sp]=sp.to_bytes(4,'big');core.m68k_execute(1)
        assert core.m68k_get_reg(None,16)==0x163f0a and n.device.ram()==expected
        changed=[i for i,(a,b)in enumerate(zip(header,n.device.ram()[task:task+38]))if a!=b];assert changed==[36,37]
        results.append(dict(instruction='MOVE.L SP,-(SP)',PC=0x163f08,metadata_offsets_overwritten=changed,full_2MB_RAM_oracle_equal=True))
        expected[sp-8:sp-4]=(0x163f0e).to_bytes(4,'big');core.m68k_execute(1)
        assert core.m68k_get_reg(None,16)==build['symbols']['biwn_native_actor_initialize_body']==0x1639c4 and n.device.ram()==expected
        changed=[i for i,(a,b)in enumerate(zip(header,n.device.ram()[task:task+38]))if a!=b];assert changed==list(range(32,38))
        results.append(dict(instruction='BSR.W actor_initialize_body',PC=0x163f0a,metadata_offsets_overwritten=changed,full_2MB_RAM_oracle_equal=True))
        expected[sp-28:sp-8]=b''.join(before.cpu.registers[i].to_bytes(4,'big')for i in [2,3,4,10,11]);core.m68k_execute(1)
        assert core.m68k_get_reg(None,16)==0x1639c8 and n.device.ram()==expected
        changed=[i for i,(a,b)in enumerate(zip(header,n.device.ram()[task:task+38]))if a!=b];assert changed==list(range(12,38))
        results.append(dict(instruction='MOVEM.L D2-D4/A2-A3,-(SP)',PC=0x1639c4,metadata_offsets_overwritten=changed,full_2MB_RAM_oracle_equal=True))
    finally:n.close()
    save(out/'instructions.json',results)
    proof=dict(status='terminal_captured_actor_init_C_argument_call_and_prologue_clobber_task_metadata_reproduced',directory=str(out),frame=8978,task=task,actor_init_entry_SP_above_task=520,logical_context_above_task=40,private_gap=448,first_argument_push_clobbers_metadata_offsets=[36,37],BSR_cumulative_metadata_bytes_clobbered=6,C_prologue_cumulative_metadata_bytes_clobbered=26,full_RAM_oracle_equal_each_instruction=True,source_defect_identified=True,all_failure_causes_resolved=False,fix_implemented=False,production_guest_state_modified=False,new_predictions=0,new_training=False,scope='Three captured machine instructions replayed on pinned CPU with an explicit fixture header pattern. First argument push clobbers physical38-byte metadata,then BSR and C prologue clobber26bytes cumulatively. This is not a patched gameplay continuation or proof of every later corruption. v40frame-acquire75/75returns with zero stack errors is separate from this actor-init defect.',source_sha256={str(p):sha(p)for p in [Path(__file__),tp,ring,memory_path,bp,Path(build['component']),out/'instructions.json']})
    save(out/'review.json',proof);save(V/'v40-actor-init-header-fault-reviewed-v1-current.json',proof);print(proof['status'],flush=True)


if __name__=='__main__':main()
