"""Native geometry plus six compiled helpers vs original68000 bodies.

E26C GPU remains a declared fixture;10734executes compiled C and actual MMIO/blitter. This checker executes the real original formatter/text bodies after native capture;rendered pixels are included in the wholeRAM comparison. Native algorithms execute
on68000; private arenas alone are normalized. No game/disc or IRQ claim.
"""
import argparse,ctypes as c,json,os,struct,subprocess
from collections import deque
from pathlib import Path
from datetime import datetime,timezone
import check_native_deck_shared_v4 as shared
import check_deck_geometry_connected_faces_v3 as connected
import check_deck_debug_overlay_cpu_v1 as debug
import check_debug_overlay_real_cpu_chain_v1 as real_chain
ROOT=shared.ROOT;SRC=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-shared-v22-scene-draw'
CPU=shared.CPU;CODE=0x180000;ARENA=0x1b0000;POOL=shared.POOL;SLOTS=101;STRIDE=1024
save=connected.save;sha=connected.sha;cpu_dict=connected.cpu_dict
EXTERNAL={0xe26c,0x1b45a,0x149ae}
ORIGINAL_RANGES={**connected.ORIGINAL_RANGES,0x10734:0x10968}
connected.scene.HELPERS=EXTERNAL
def file_sha(p):return sha(Path(p).read_bytes())
class Engine(connected.Engine):
    real_dependencies=False
    arguments=debug.Engine.arguments
    def entry(self,memory,state):
        value=super().entry(memory,state);value['return_PC']=int.from_bytes(memory[state.registers[15]:state.registers[15]+4],'big');return value
    def effect_external(self,state,case,gpu_number,debug_number):
        if state.pc==0xe26c:
            memory=bytearray(self.native.device.ram());connected.faces.Engine.effect(self,memory,state,case,gpu_number);self.native.device.seed(bytes(memory),0)
            return gpu_number+1,debug_number
        debug.Engine.effect(self,state,state.pc,case,debug_number);return gpu_number,debug_number+1
    def original(self,ram,initial,case):
        self.native.device.seed(ram,0);self.set_cpu(initial,True);entries=[];coverage=set();gpu_number=debug_number=0
        for step in range(1000000):
            state=self.cpu();pc=state.pc
            if pc==connected.h.STOP:break
            if pc in set(connected.h.RANGES)|{0x110d4,0x1142e,0x10734}|EXTERNAL:entries.append(self.entry(self.native.device.ram(),state))
            if pc==0xe26c or(pc in debug.WIDTHS and not self.real_dependencies):
                gpu_number,debug_number=self.effect_external(state,case,gpu_number,debug_number);state.pc=self.native.device.read(state.registers[15],4);state.registers[15]+=4
                if state.sr&0x2000:state.ssp=state.registers[15]
                else:state.usp=state.registers[15]
                self.set_cpu(state);continue
            assert any(a<=pc<b for a,b in ORIGINAL_RANGES.items())or(self.real_dependencies and any(a<=pc<b for a,b in real_chain.RANGES)),hex(pc)
            coverage.add(pc);self.core.m68k_execute(1)
        else:raise AssertionError('Original six-helper instruction bound')
        return self.native.device.ram(),self.cpu(),entries,coverage,step,self.native.device.registers()
    def compiled(self,ram,initial,case,syms,payload,expected_entries):
        task=int.from_bytes(ram[0xc0920:0xc0924],'big');slot=(task-POOL)//STRIDE;arena=ARENA+slot*STRIDE;frame=arena+16
        state=CPU.from_buffer_copy(bytes(initial));state.pc=syms['biwn_v4_geometry'];self.native.device.seed(ram,0);self.set_cpu(state,True)
        helper_return=syms['biwn_v4_geometry_helper_return'];marker=syms['biwn_v5_deeper_helper_marker'];capture_end=syms['biwn_v4_geometry_capture_end']
        trace=deque(maxlen=20);entries=[];low=1008;low_pc=0;captured=0;virtual_markers=0;original_steps=0;gpu_number=debug_number=0;guest_sp=None;real_captured=0;pending_real=None
        def entry(memory,cpu):
            normalized=bytearray(memory);normalized[ARENA:ARENA+SLOTS*STRIDE]=ram[ARENA:ARENA+SLOTS*STRIDE]
            return self.entry(normalized,cpu)
        for step in range(1000000):
            state=self.cpu();pc=state.pc;sp=state.registers[15];trace.append([hex(pc),hex(sp)])
            if pc==connected.h.STOP:break
            if arena<=sp<arena+STRIDE:
                if helper_return+12<=pc<capture_end:
                    displacement={12:0,16:0,20:64}.get(pc-helper_return,4);assert sp==frame+displacement,('capture SP',hex(pc),hex(sp))
                elif sp-arena<low:
                    low=sp-arena;low_pc=pc
                    if low<832:
                        memory=self.native.device.ram();stack=[]
                        for at in range(sp,arena+1008,2):
                            value=int.from_bytes(memory[at:at+4],'big')
                            if CODE<=value<CODE+len(payload):stack.append(dict(offset=at-arena,value=hex(value),symbol=max((a,n)for n,a in syms.items()if a<=value)))
                        save(self.debug_out/'stack-overflow.json',dict(case=case,low=low,PC=hex(pc),trace=list(trace),probable_return_addresses=stack))
            if pc in [marker,syms['service_geometry_original'],syms['service_geometry_faces'],syms['service_geometry_debug']]:
                memory=self.native.device.ram();at=int.from_bytes(memory[sp+4:sp+8],'big');target=int.from_bytes(memory[sp+(8 if pc==marker else 16):sp+(12 if pc==marker else 20)],'big');assert at==frame and target in set(connected.h.RANGES)|{0x110d4,0x1142e,0x10734}
                values=struct.unpack('>19IH',memory[at+4:at+82]);virtual=CPU();virtual.registers[:]=values[:16];virtual.pc,virtual.usp,virtual.ssp,virtual.sr=values[16:]
                # Native frame stores only the active bank. The untouched
                # physical inactive bank remains original and is checked at RTS.
                if virtual.sr&0x2000:virtual.usp=initial.usp
                else:virtual.ssp=initial.ssp
                assert virtual.pc==target and virtual.registers[15]==(virtual.ssp if virtual.sr&0x2000 else virtual.usp)
                entries.append(entry(memory,virtual));virtual_markers+=1
            if pc==helper_return:
                assert guest_sp is not None and sp==guest_sp+4;captured+=1
            if pc in EXTERNAL:
                memory=bytearray(self.native.device.ram());wanted=expected_entries[len(entries)]['CPU']['pc'];assert wanted==pc
                guest_sp=sp;physical=int.from_bytes(memory[sp:sp+4],'big');assert physical==helper_return
                # Original JSR words are restored by capture; compare logical
                # helper entry with exactly that one declared word normalized.
                expected_return=expected_entries[len(entries)]['return_PC']
                normalized=bytearray(memory);normalized[sp:sp+4]=expected_return.to_bytes(4,'big');entries.append(entry(normalized,state))
                if pc in debug.WIDTHS and self.real_dependencies:
                    assert pending_real is None;pending_real=sp
                else:
                    gpu_number,debug_number=self.effect_external(state,case,gpu_number,debug_number);state.pc=physical;state.registers[15]+=4
                    if state.sr&0x2000:state.ssp=state.registers[15]
                    else:state.usp=state.registers[15]
                    self.set_cpu(state);continue
            if pending_real is not None and pc==helper_return:
                assert sp==pending_real+4;pending_real=None;real_captured+=1
            if any(a<=pc<b for a,b in ORIGINAL_RANGES.items()):original_steps+=1
            assert CODE<=pc<CODE+len(payload)or(self.real_dependencies and pending_real is not None and any(a<=pc<b for a,b in real_chain.RANGES)),dict(PC=hex(pc),SP=hex(sp),C_stack_low=low,trace=list(trace))
            self.core.m68k_execute(1)
        else:raise AssertionError(('native instruction bound',hex(pc),list(trace)))
        assert virtual_markers==6 and captured==sum(e['CPU']['pc']in EXTERNAL for e in expected_entries)and original_steps==0
        assert pending_real is None
        memory=self.native.device.ram();assert memory[CODE:CODE+len(payload)]==payload
        for slot2 in range(SLOTS):
            at=ARENA+slot2*STRIDE
            for lo,hi in shared.FENCES:assert memory[at+lo:at+hi]==ram[at+lo:at+hi],('fence',slot2,lo,low,hex(low_pc),max((a,n)for n,a in syms.items()if a<=low_pc))
        assert low>=832,('geometry C stack exceeds partition',low,832)
        assert memory[ARENA:arena]==ram[ARENA:arena]and memory[arena+STRIDE:ARENA+SLOTS*STRIDE]==ram[arena+STRIDE:ARENA+SLOTS*STRIDE]
        assert memory[frame+114:frame+118]==bytes(4)
        allowed=set(range(16,134))|set(range(832,1008))
        assert all(i in allowed or memory[arena+i]==ram[arena+i]for i in range(STRIDE)),('other context changed',low)
        normalized=bytearray(memory);normalized[ARENA:ARENA+SLOTS*STRIDE]=ram[ARENA:ARENA+SLOTS*STRIDE]
        return bytes(normalized),self.cpu(),entries,dict(native_instructions=step,C_stack_low=low,C_stack_bytes=1008-low,lowest_PC=hex(low_pc),virtual_helper_entries=virtual_markers,original_fixture_returns=captured,original_algorithm_steps=original_steps,real_debug_dependency_returns=real_captured,debug_fixture_calls=debug_number)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);ap.add_argument('--real-dependencies',action='store_true',default=True);args=ap.parse_args()
    family='native-geometry-scene17-v1'if args.real_dependencies else'native-Deck-debug-v1'
    out=ROOT/'verification'/family/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='building',pid=os.getpid(),directory=str(out),whole_game_complete=False,new_training=False,native_disc_changed=False)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification'/(family+'-current.json'),state)
    mark()
    try:
        build=out/'build';p=subprocess.run(['make','BUILD='+str(build),'ADDRESS='+hex(CODE),'ARENA_ADDRESS='+hex(ARENA)],cwd=SRC,text=True,capture_output=True);(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
        payload=(build/'native-shared.bin').read_bytes();syms=shared.symbols(build/'symbols.txt');engine=Engine();engine.real_dependencies=args.real_dependencies;engine.debug_out=out;rows=[]
        try:
            for ram,initial,case in connected.fixtures():
                if args.limit and case['variant']%64>=args.limit:continue
                i=case['variant'];memory=bytearray(ram);memory[CODE:CODE+len(payload)]=payload;memory[ARENA:ARENA+SLOTS*STRIDE]=bytes([0xa5])*(SLOTS*STRIDE)
                for slot in range(SLOTS):
                    for _,offset,_,_ in shared.LAYOUT.values():memory[ARENA+slot*STRIDE+offset+114:ARENA+slot*STRIDE+offset+118]=bytes(4)
                task=POOL+(i%SLOTS)*STRIDE;memory[0xc0920:0xc0924]=task.to_bytes(4,'big');sp=task+[0x3c0,0x3be,0x200][i%3];memory[sp-256:sp+32]=memory[connected.h.SP-256:connected.h.SP+32]
                initial=CPU.from_buffer_copy(bytes(initial));initial.registers[15]=sp
                initial.sr=(0x2000 if i&1 else 0)|((i//2)%32)|((i//64)<<8)
                initial.usp=0x1d8000 if initial.sr&0x2000 else sp;initial.ssp=sp if initial.sr&0x2000 else 0x1ff000
                memory[0x403cc:0x403ce]=[0,1,0x8000,0xffff][i//64].to_bytes(2,'big');memory[0x403ca:0x403cc]=[0,1,2,31][i%4].to_bytes(2,'big')
                memory[0xb29d0:0xb5130]=bytes([0xa5])*(0xb5130-0xb29d0);case=dict(case,mutate_globals=i%3==0)
                if initial.sr&0x2000:initial.ssp=sp
                else:initial.usp=sp
                ram=bytes(memory);expected,cpu,entries,_,_,hardware=engine.original(ram,initial,case)
                actual,got,observed,details=engine.compiled(ram,initial,case,syms,payload,entries)
                if expected!=actual or cpu_dict(cpu)!=cpu_dict(got)or entries!=observed or hardware!=engine.native.device.registers():
                    save(out/'counterexample.json',dict(case=case,original_CPU=cpu_dict(cpu),native_CPU=cpu_dict(got),original_entries=entries,native_entries=observed,RAM_differences=[[hex(a),x,y]for a,(x,y)in enumerate(zip(expected,actual))if x!=y][:40],details=details,original_hardware=hardware,native_hardware=engine.native.device.registers()));raise AssertionError(out/'counterexample.json')
                if not args.real_dependencies:assert actual[0xb29d0:0xb5130]==bytes(0xb5130-0xb29d0)
                rows.append(dict(case=i,task=hex(task),full_CPU_nonarena_RAM_callee_entries_match=True,**details))
                if len(rows)%16==0:state.update(status='checking',completed=len(rows));mark();print('completed',len(rows),flush=True)
        finally:engine.native.close()
        save(out/'cases.json',rows);paths=[Path(__file__),Path(connected.__file__),Path(connected.h.__file__),*list(SRC.glob('native-shared.*')),*list(SRC.glob('*.inc')),SRC/'Makefile',SRC/'native-alu.h',debug.SRC/'coordinator-reference.c',debug.SRC/'debug-contract.h',Path(debug.__file__),Path(real_chain.__file__),SRC.parent.parent/'experimental/deck-geometry-faces-v1/coordinator-reference.c',SRC.parent.parent/'experimental/deck-geometry-faces-v1/faces-contract.h',SRC.parent.parent/'experimental/deck-geometry-helpers-v1/coordinator-reference.c',SRC.parent.parent/'experimental/deck-geometry-helpers-v1/helper-contract.h',SRC.parent.parent/'experimental/deck-plane-layout-v1/coordinator-reference.c',SRC.parent.parent/'experimental/deck-plane-layout-v1/plane-contract.h']
        state.update(status='terminal_native_deeper_preflight_pass'if args.limit else'terminal_native_geometry_six_deeper_helpers_match',completed=len(rows),code_bytes=len(payload),payload=str(build/'native-shared.bin'),payload_sha256=file_sha(build/'native-shared.bin'),symbols=syms,
            maximum_C_stack_bytes=max(x['C_stack_bytes']for x in rows),minimum_C_stack_offset=min(x['C_stack_low']for x in rows),private_stack_lower=832,
            helper_entries_each=len(rows),real_debug_dependencies=args.real_dependencies,original_algorithm_steps=0,source_sha256={str(p):file_sha(p)for p in paths},scope=__doc__+' Virtual helper marker compares shadowCPU with inactive bank supplied from unchanged physical bank; only arena bytes and external capture return word normalized at callee entries. Final physicalCPU both banks and nonarenaRAM match exactly.')
        mark();print(state['status'],state['maximum_C_stack_bytes'],flush=True)
    except BaseException as e:state.update(status='terminal_native_deeper_checker_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
