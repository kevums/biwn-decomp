"""Actual native volatile wait slices and resumed helper calls versus original."""
import json
from datetime import datetime,timezone
from pathlib import Path
import check_native_deck_outer_v1 as outer
ROOT=outer.ROOT;save=outer.save;sha=outer.sha;cpu_dict=outer.cpu_dict


def main():
    pointer=ROOT/'verification/native-Deck-outer-v1-current.json';gate=json.loads(pointer.read_text())
    for p,h in gate['source_sha256'].items():assert sha(Path(p).read_bytes())==h,p
    payload=Path(gate['payload']).read_bytes();syms=gate['symbols'];row=next(x for x in outer.original.fixtures()if x[1].pc==0x11f50)
    out=ROOT/'verification/native-Deck-outer-waits-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    e=outer.Engine();rows=[]
    try:
        for value in [1,0x80000000,0xffffffff]:
            for index in range(64):
                ram,initial,case=outer.prepare(row,index,payload);memory=bytearray(ram);memory[0x10a684:0x10a688]=value.to_bytes(4,'big')
                initial.sr=(0x2000 if index&1 else 0)|(index//2)
                if initial.sr&0x2000:initial.ssp=initial.registers[15];initial.usp=0x1d8000
                else:initial.usp=initial.registers[15];initial.ssp=0x1ff000
                # Continuation fixture must agree with the changed physical
                # stack bank/SR. The native resume copies returned registers.
                frame=outer.ARENA+(index%outer.SLOTS)*outer.STRIDE+16
                packed=b''.join(int(x).to_bytes(4,'big')for x in [*initial.registers,initial.pc,initial.usp,initial.ssp])+int(initial.sr).to_bytes(2,'big')
                memory[frame+4:frame+82]=packed;ram=bytes(memory)
                e.native.device.seed(ram,0);e.set_cpu(initial,True);polls=0
                for step in range(512):
                    expected=e.cpu()
                    if expected.pc==0x11f50:
                        if polls==64:break
                        polls+=1
                    assert 0x11f50<=expected.pc<0x11f58,hex(expected.pc)
                    e.core.m68k_execute(1)
                else:raise AssertionError('Original wait bound')
                expected_ram=e.native.device.ram()
                status,got_ram,got,entries,details=e.compiled(ram,initial,case,syms,[],payload)
                assert status==6 and polls==64 and expected_ram==got_ram and cpu_dict(expected)==cpu_dict(got)and not entries
                # Preserve the exact private frame from the actual suspended
                # native boundary, release the declared volatile flag only,
                # then enter the native continuation again.
                resumed=bytearray(e.native.device.ram());resumed[0x10a684:0x10a688]=bytes(4);resumed=bytes(resumed)
                expected_status,want_ram,want_cpu,want_entries,_=e.original(resumed,expected,case)
                result,actual,actual_cpu,actual_entries,more=e.compiled(resumed,got,case,syms,want_entries,payload)
                assert result==expected_status==6 and actual==want_ram and cpu_dict(actual_cpu)==cpu_dict(want_cpu)and actual_entries==want_entries
                rows.append(dict(value=hex(value),case=index,mode=initial.sr&0x2000,CCR=initial.sr&31,polls=64,wait_full_CPU_RAM_match=True,resumed_full_CPU_nonarena_RAM_helper_entries_match=True,helper_returns=more['helper_returns'],C_stack_bytes=max(details['C_stack_bytes'],more['C_stack_bytes'])))
        save(out/'cases.json',rows)
        proof=dict(status='terminal_native_outer_192_wait_and_resume_pairs_pass',directory=str(out),completed=len(rows),comparisons=len(rows)*2,maximum_C_stack_bytes=max(x['C_stack_bytes']for x in rows),
                   new_training=False,native_disc_changed=False,source_sha256={str(p):sha(p.read_bytes())for p in [Path(__file__),Path(outer.__file__),pointer,Path(gate['payload']),out/'cases.json']},
                   scope=__doc__+'192pairs, both stack banks/all32CCR and three nonzero volatile flags. Native64read slices compare to original64polls at11F50; released flag resumes actual native private context. Helpers are fixtures; no clock/IRQ event injected, no exact-cycle or real scheduler proof.')
        save(out/'protocol.json',proof);save(ROOT/'verification/native-Deck-outer-waits-v1-current.json',proof);print(proof['status'],len(rows),flush=True)
    finally:e.native.close()


if __name__=='__main__':main()
