"""Full CPU/full RAM fallback ABI; no arena normalization or helper bridge."""
import json
from datetime import datetime,timezone
from pathlib import Path
import native_outer_final_checker as outer
ROOT=outer.ROOT;save=outer.save;sha=outer.sha;cpu_dict=outer.cpu_dict


def main():
    pointer=ROOT/'verification/native-Deck-outer-scene17-direct-dispatch-final-v1-current.json';gate=json.loads(pointer.read_text())
    for p,h in gate['source_sha256'].items():assert sha(Path(p).read_bytes())==h,p
    payload=Path(gate['payload']).read_bytes();syms=gate['symbols'];row=next(outer.original.fixtures());e=outer.Engine();rows=[]
    out=ROOT/'verification/native-Deck-outer-fallback-scene17-direct-dispatch-final-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    try:
        for lane in ['zero','before','unaligned','after','maximum','busy']:
            for index in range(64):
                ram,initial,case=outer.prepare(row,index,payload);memory=bytearray(ram)
                initial.sr=(0x2000 if index&1 else 0)|(index//2)
                if initial.sr&0x2000:initial.ssp=initial.registers[15];initial.usp=0x1d8000
                else:initial.usp=initial.registers[15];initial.ssp=0x1ff000
                task=int.from_bytes(memory[0xc0920:0xc0924],'big')
                selected={'zero':0,'before':outer.POOL-1024,'unaligned':outer.POOL+1,'after':outer.POOL+outer.SLOTS*1024,'maximum':0xffffffff,'busy':task}[lane]
                memory[0xc0920:0xc0924]=selected.to_bytes(4,'big')
                if lane=='busy':at=outer.ARENA+(index%outer.SLOTS)*outer.STRIDE+130;memory[at:at+4]=(1).to_bytes(4,'big')
                ram=bytes(memory);expected_status,expected,want,entries,_=e.original(ram,initial,case)
                state=outer.CPU.from_buffer_copy(bytes(initial));state.pc=syms['biwn_outer_entry'];e.native.device.seed(ram,0);e.set_cpu(state,True);observed=[];old_steps=0
                for step in range(4000):
                    state=e.cpu();pc=state.pc
                    if pc==0x11e86 and step:break
                    if pc in outer.original.HELPERS:
                        memory=bytearray(e.native.device.ram());observed.append(e.entry(memory,state));assert e.helper(memory,state,pc,case,len(observed)-1)==0
                        state.pc=int.from_bytes(memory[state.registers[15]:state.registers[15]+4],'big');state.registers[15]+=4
                        if state.sr&0x2000:state.ssp=state.registers[15]
                        else:state.usp=state.registers[15]
                        e.native.device.seed(bytes(memory),0);e.set_cpu(state);continue
                    if 0x11e6c<=pc<0x11f6c:old_steps+=1
                    else:assert outer.CODE<=pc<outer.CODE+len(payload),hex(pc)
                    e.core.m68k_execute(1)
                else:raise AssertionError('Fallback did not reach original iteration boundary')
                assert expected_status==6 and cpu_dict(state)==cpu_dict(want)and e.native.device.ram()==expected and observed==entries,(lane,index)
                assert old_steps>0
                rows.append(dict(lane=lane,case=index,task=hex(selected),sr=initial.sr,full_CPU_and_full_RAM_byte_identical=True,original_steps=old_steps))
        save(out/'cases.json',rows)
        proof=dict(status='terminal_native_outer_384_full_CPU_RAM_fallback_cases_pass',directory=str(out),completed=len(rows),new_training=False,native_disc_changed=False,
                   source_sha256={str(p):sha(p.read_bytes())for p in [Path(__file__),Path(outer.__file__),pointer,Path(gate['payload']),out/'cases.json']},
                   scope=__doc__+' Six invalid/busy classes, both banks/all32CCR; constructor helper is a declared fixture. Entry fallback replays twelve whole original bytes, then jumps to11E78. No deployed disc or arbitrary reentry claim.')
        save(out/'protocol.json',proof);save(ROOT/'verification/native-Deck-outer-fallback-scene17-direct-dispatch-final-v1-current.json',proof);print(proof['status'],len(rows),flush=True)
    finally:e.native.close()


if __name__=='__main__':main()
