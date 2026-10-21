"""Native outer task versus original CPU at explicit semantic boundaries.

Original helper bodies are declared fixtures in this component matrix.
Internal source continuations are seeded fixtures, not deployed entry patches.
"""
import argparse,ctypes as c,json,os,subprocess
from collections import deque
from datetime import datetime,timezone
from pathlib import Path
import check_deck_task_source_v1 as original
from check_native_deck_coordinate_v1 import symbols
ROOT=original.ROOT;CPU=original.CPU;SP=original.SP;STOP=original.STOP
SRC=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-outer-v32-compact-v1'
CODE=0x179a64;ARENA=0x1947c0;DECK=0x17b3c0;POOL=0xc0928;SLOTS=101;STRIDE=384
FENCES=[(0,16),(136,144),(368,384)]
save=original.save;sha=original.sha;cpu_dict=original.cpu_dict


def prepare(row,index,payload,continuation=True):
    ram,state,case=row;memory=bytearray(ram);state=CPU.from_buffer_copy(bytes(state))
    memory[CODE:CODE+len(payload)]=payload
    memory[ARENA:ARENA+SLOTS*STRIDE]=bytes([0xa5])*(SLOTS*STRIDE)
    for slot in range(SLOTS):
        frame=ARENA+slot*STRIDE+16
        memory[frame+114:frame+118]=bytes(4)
        at=DECK+slot*1024+392;memory[at:at+4]=frame.to_bytes(4,'big')
    slot=index%SLOTS;task=POOL+slot*1024;sp=task+[0x3c0,0x280,0x200][index%3]
    memory[sp-512:sp+128]=memory[SP-512:SP+128]
    state.registers[14]=sp+64;state.registers[15]=sp
    if state.sr&0x2000:state.ssp=sp
    else:state.usp=sp
    memory[0xc0920:0xc0924]=task.to_bytes(4,'big')
    frame=ARENA+slot*STRIDE+16
    if continuation and state.pc!=0x11e6c:
        packed=b''.join(int(x).to_bytes(4,'big')for x in [*state.registers,state.pc,state.usp,state.ssp])+int(state.sr).to_bytes(2,'big')
        assert len(packed)==78
        memory[frame+4:frame+82]=packed
        memory[frame+114:frame+118]=(1).to_bytes(4,'big')
    assert len(memory)==0x200000
    return bytes(memory),state,case


class Engine(original.Engine):
    def entry(self,memory,state):
        result=super().entry(memory,state)
        result['return_PC']=int.from_bytes(memory[state.registers[15]:state.registers[15]+4],'big')
        return result
    def compiled(self,ram,initial,case,syms,expected_entries,payload):
        state=CPU.from_buffer_copy(bytes(initial))
        state.pc=syms['biwn_outer_entry']if initial.pc==0x11e6c else syms['biwn_outer_resume']
        self.native.device.seed(ram,0);self.set_cpu(state,True)
        entries=[];coverage=set();trace=deque(maxlen=24);helper_return=syms['biwn_outer_helper_return'];last_sp=None
        task=int.from_bytes(ram[0xc0920:0xc0924],'big');slot=(task-POOL)//1024;base=ARENA+slot*STRIDE;low=368;helper_returns=0
        def normalize(memory):
            out=bytearray(memory);out[ARENA:ARENA+SLOTS*STRIDE]=ram[ARENA:ARENA+SLOTS*STRIDE];return out
        for step in range(150000):
            state=self.cpu();pc=state.pc;sp=state.registers[15];trace.append([hex(pc),hex(sp)])
            if pc==STOP:status=0;break
            if pc==syms['biwn_outer_iteration_boundary']:state.pc=0x11e86;status=6;break
            if pc==syms['biwn_outer_wait_boundary']:state.pc=0x11f50;status=6;break
            if (pc>=syms['biwn_outer_asm_end']or syms['biwn_outer_capture_initialize']<=pc<helper_return)and base<=sp<base+STRIDE:
                low=min(low,sp-base)
                assert sp>=base+144,('C stack overflow',hex(pc),sp-base)
            if pc==helper_return:
                helper_returns+=1;assert sp==last_sp+4,('helper RTS SP',sp,last_sp)
            if pc in original.HELPERS:
                memory=bytearray(self.native.device.ram());sp=state.registers[15]
                assert len(entries)<len(expected_entries)
                physical=int.from_bytes(memory[sp:sp+4],'big');wanted=expected_entries[len(entries)]['return_PC']
                assert physical==helper_return,('helper return trampoline',hex(physical))
                normalized=normalize(memory);normalized[sp:sp+4]=wanted.to_bytes(4,'big')
                entries.append(self.entry(normalized,state));last_sp=sp
                result=self.helper(memory,state,pc,case,len(entries)-1)
                assert result==0,'Suspension fixtures are qualified by a separate continuation check'
                self.native.device.seed(bytes(memory),0);state.pc=physical;state.registers[15]+=4
                if state.sr&0x2000:state.ssp=state.registers[15]
                else:state.usp=state.registers[15]
                self.set_cpu(state);continue
            assert CODE<=pc<CODE+len(payload),dict(pc=hex(pc),trace=list(trace))
            coverage.add(pc);self.core.m68k_execute(1)
        else:raise AssertionError(('native instruction bound',list(trace)))
        memory=self.native.device.ram()
        assert memory[CODE:CODE+len(payload)]==payload,'Native code changed'
        for i in range(SLOTS):
            at=ARENA+i*STRIDE
            for lo,hi in FENCES:assert memory[at+lo:at+hi]==ram[at+lo:at+hi],('outer fence',i,lo,low)
        assert memory[ARENA:base]==ram[ARENA:base]and memory[base+STRIDE:ARENA+SLOTS*STRIDE]==ram[base+STRIDE:ARENA+SLOTS*STRIDE]
        allowed=set(range(16,134))|set(range(144,368))
        assert all(i in allowed or memory[base+i]==ram[base+i]for i in range(STRIDE)),'Other outer bytes changed'
        assert int.from_bytes(memory[base+130:base+134],'big')==(1 if status==6 else 0),'Active lifetime'
        assert memory[DECK:DECK+SLOTS*1024]==ram[DECK:DECK+SLOTS*1024],'Existing Deck arena changed'
        assert len(entries)==len(expected_entries)==helper_returns
        return status,bytes(normalize(memory)),state,entries,dict(instructions=step,C_stack_low=low,C_stack_bytes=368-low,helper_returns=helper_returns,covered_native_instructions=len(coverage))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);args=ap.parse_args()
    out=ROOT/'verification/native-Deck-outer-outer-compact-final-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='building',pid=os.getpid(),directory=str(out),whole_game_complete=False,new_training=False,native_disc_changed=False)
    def mark():save(out/'protocol.json',state)
    mark()
    try:
        build=out/'build';p=subprocess.run(['make','BUILD='+str(build),'ADDRESS='+hex(CODE),'ARENA_ADDRESS='+hex(ARENA),'DECK_ADDRESS='+hex(DECK)],cwd=SRC,capture_output=True,text=True)
        (out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
        payload=(build/'native-outer.bin').read_bytes();resident=Path('/Users/kevin/Documents/Codex/2026-10-10/i-now-am-using-the-following/outputs/local-ai-lab/builds/BIWN-native-outer-compact-v1/20261021T035953.106380Z/resident-with-arenas.bin').read_bytes();assert payload==resident[CODE-1437120:CODE-1437120+len(payload)],'Outer deployed bytes differ';syms=symbols(build/'symbols.txt');rows=[];engine=Engine()
        try:
            for i,row in enumerate(original.fixtures()):
                if args.limit and i>=args.limit:break
                ram,initial,case=prepare(row,i,payload)
                expected_status,expected,cpu,entries,covered=engine.original(ram,initial,case)
                status,actual,got,observed,details=engine.compiled(ram,initial,case,syms,entries,payload)
                if status!=expected_status or expected!=actual or cpu_dict(cpu)!=cpu_dict(got)or entries!=observed:
                    save(out/'counterexample.json',dict(case=case,status=status,original_status=expected_status,original_CPU=cpu_dict(cpu),native_CPU=cpu_dict(got),original_entries=entries,native_entries=observed,RAM_differences=[[hex(a),u,v]for a,(u,v)in enumerate(zip(expected,actual))if u!=v][:32],details=details));raise AssertionError(out/'counterexample.json')
                rows.append(dict(case=i,root=hex(initial.pc),mode=case['mode'],status=status,task_slot=i%SLOTS,full_CPU_nonarena_RAM_helper_entries_match=True,**details))
                if i%64==0:state.update(status='checking',completed=i+1);mark();print('case',i+1,flush=True)
        finally:engine.native.close()
        save(out/'cases.json',rows)
        paths=[Path(__file__),Path(original.__file__),SRC/'native-outer.c',SRC/'native-outer.S',SRC/'native-outer.ld',SRC/'Makefile',original.SRC/'deck-task-source.c',original.SRC/'deck-task-source.h',build/'native-outer.bin',build/'symbols.txt']
        state.update(status='terminal_native_outer_preflight_pass'if args.limit else'terminal_native_outer_semantic_boundaries_original_CPU_match',completed=len(rows),code_bytes=len(payload),payload=str(build/'native-outer.bin'),payload_sha256=sha(payload),symbols=syms,
                     maximum_C_stack_bytes=max(x['C_stack_bytes']for x in rows),minimum_C_stack_offset=min(x['C_stack_low']for x in rows),source_sha256={str(p):sha(p.read_bytes())for p in paths},
                     task_slots=len(set(x['task_slot']for x in rows)),outer_private_bytes=SLOTS*STRIDE,read_only_pointer_offset_in_existing_Deck_slot=392,
                     scope=__doc__+' FullCPU including banks, full nonarena2MBRAM, ordered complete helper-entry snapshots and native/private memory fences. All original helpers are fixtures. No actual nested five-caller execution, deep scheduler suspension, IRQ, disc relocation, fresh boot or physical fidelity claim. Internal boundary PC is normalized to its declared original continuation only.');mark()
        if not args.limit:save(ROOT/'verification/native-Deck-outer-outer-compact-final-v1-current.json',state)
        print(state['status'],len(rows),'cases',state['maximum_C_stack_bytes'],'C stack bytes',flush=True)
    except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise


if __name__=='__main__':main()
