"""Create the six-helper geometry/native integration checker without altering earlier gates."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=ROOT/'scripts/check_native_deck_debug_v1.py';assert not p.exists();s=(ROOT/'scripts/check_native_deck_clear_v1.py').read_text();s=s.replace('deck-shared-v9','deck-shared-v10').replace('native-Deck-clear-v1','native-Deck-debug-v1')
 s=s.replace('import check_deck_geometry_connected_faces_v3 as connected','import check_deck_geometry_connected_faces_v3 as connected\nimport check_deck_debug_overlay_cpu_v1 as debug\nimport check_debug_overlay_real_cpu_chain_v1 as real_chain')
 s=s.replace('connected.scene.HELPERS=set(connected.EXTERNAL)','EXTERNAL={0xe26c,0x1b45a,0x149ae}\nORIGINAL_RANGES={**connected.ORIGINAL_RANGES,0x10734:0x10968}\nconnected.scene.HELPERS=EXTERNAL')
 methods='''    real_dependencies=False
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
'''
 s=s.replace('class Engine(connected.Engine):\n','class Engine(connected.Engine):\n'+methods)
 s=s.replace('for step in range(100000):','for step in range(1000000):').replace('original_steps=0;service_number=0;guest_sp=None','original_steps=0;gpu_number=debug_number=0;guest_sp=None;real_captured=0;pending_real=None')
 s=s.replace("syms['service_geometry_faces']]:","syms['service_geometry_faces'],syms['service_geometry_debug']]:")
 s=s.replace('set(connected.h.RANGES)|{0x110d4,0x1142e}','set(connected.h.RANGES)|{0x110d4,0x1142e,0x10734}')
 s=s.replace('            if pc in connected.EXTERNAL:','            if pc in EXTERNAL:')
 s=s.replace("expected_return={0xe26c:0x11684,0x10734:0x11b44}[pc]","expected_return=expected_entries[len(entries)]['return_PC']")
 a=s.index('                self.effect(memory,state,dict(case,service_number=service_number))');b=s.index('            if any(a<=pc<b for a,b in connected.ORIGINAL_RANGES.items())',a)
 s=s[:a]+'''                if pc in debug.WIDTHS and self.real_dependencies:
                    assert pending_real is None;pending_real=sp
                else:
                    gpu_number,debug_number=self.effect_external(state,case,gpu_number,debug_number);state.pc=physical;state.registers[15]+=4
                    if state.sr&0x2000:state.ssp=state.registers[15]
                    else:state.usp=state.registers[15]
                    self.set_cpu(state);continue
            if pending_real is not None and pc==helper_return:
                assert sp==pending_real+4;pending_real=None;real_captured+=1
''' +s[b:]
 s=s.replace('connected.ORIGINAL_RANGES.items()','ORIGINAL_RANGES.items()')
 old='            assert CODE<=pc<CODE+len(payload),dict(PC=hex(pc),SP=hex(sp),C_stack_low=low,trace=list(trace))'
 new="            assert CODE<=pc<CODE+len(payload)or(self.real_dependencies and pending_real is not None and any(a<=pc<b for a,b in real_chain.RANGES)),dict(PC=hex(pc),SP=hex(sp),C_stack_low=low,trace=list(trace))"
 assert old in s;s=s.replace(old,new).replace('virtual_markers==5','virtual_markers==6').replace("e['CPU']['pc']in connected.EXTERNAL","e['CPU']['pc']in EXTERNAL")
 s=s.replace('        memory=self.native.device.ram();assert memory[CODE:CODE+len(payload)]==payload','        assert pending_real is None\n        memory=self.native.device.ram();assert memory[CODE:CODE+len(payload)]==payload')
 s=s.replace('original_algorithm_steps=original_steps)','original_algorithm_steps=original_steps,real_debug_dependency_returns=real_captured,debug_fixture_calls=debug_number)')
 s=s.replace("ap.add_argument('--limit',type=int);args=ap.parse_args()","ap.add_argument('--limit',type=int);ap.add_argument('--real-dependencies',action='store_true');args=ap.parse_args()")
 s=s.replace("out=ROOT/'verification/native-Deck-debug-v1'/", "family='native-Deck-debug-real-v1'if args.real_dependencies else'native-Deck-debug-v1'\n    out=ROOT/'verification'/family/")
 s=s.replace("save(ROOT/'verification/native-Deck-debug-v1-current.json',state)","save(ROOT/'verification'/(family+'-current.json'),state)")
 s=s.replace("engine=Engine();engine.debug_out=out;rows=[]","engine=Engine();engine.real_dependencies=args.real_dependencies;engine.debug_out=out;rows=[]")
 s=s.replace("if args.limit and case['variant']>=args.limit:continue","if args.limit and case['variant']%64>=args.limit:continue")
 anchor="                initial=CPU.from_buffer_copy(bytes(initial));initial.registers[15]=sp\n"
 assert s.count(anchor)==1;s=s.replace(anchor,"""                initial=CPU.from_buffer_copy(bytes(initial));initial.registers[15]=sp
                initial.sr=(0x2000 if i&1 else 0)|((i//2)%32)|((i//64)<<8)
                initial.usp=0x1d8000 if initial.sr&0x2000 else sp;initial.ssp=sp if initial.sr&0x2000 else 0x1ff000
                memory[0x403cc:0x403ce]=[0,1,0x8000,0xffff][i//64].to_bytes(2,'big');memory[0x403ca:0x403cc]=[0,1,2,31][i%4].to_bytes(2,'big')
                memory[0xb29d0:0xb5130]=bytes([0xa5])*(0xb5130-0xb29d0);case=dict(case,mutate_globals=i%3==0)
""")
 s=s.replace('expected,cpu,entries,_,_=engine.original(ram,initial,case)','expected,cpu,entries,_,_,hardware=engine.original(ram,initial,case)')
 s=s.replace('if expected!=actual or cpu_dict(cpu)!=cpu_dict(got)or entries!=observed:','if expected!=actual or cpu_dict(cpu)!=cpu_dict(got)or entries!=observed or hardware!=engine.native.device.registers():')
 s=s.replace("details=details));raise AssertionError(out/'counterexample.json')","details=details,original_hardware=hardware,native_hardware=engine.native.device.registers()));raise AssertionError(out/'counterexample.json')")
 s=s.replace("                rows.append(dict(case=i,", "                assert actual[0xb29d0:0xb5130]==bytes(0xb5130-0xb29d0)\n                rows.append(dict(case=i,")
 s=s.replace("SRC/'Makefile',SRC/'native-alu.h',","SRC/'Makefile',SRC/'native-alu.h',debug.SRC/'coordinator-reference.c',debug.SRC/'debug-contract.h',Path(debug.__file__),Path(real_chain.__file__),")
 s=s.replace('terminal_native_geometry_five_deeper_helpers_match','terminal_native_geometry_six_deeper_helpers_match').replace('helper_entries_each=len(rows),','helper_entries_each=len(rows),real_debug_dependencies=args.real_dependencies,')
 s=s.replace('Native geometry plus five compiled helpers vs original68000 bodies.','Native geometry plus six compiled helpers vs original68000 bodies.').replace('E26C GPU and10734debug remain declared callee fixtures;1142E executes compiled C.','E26C GPU remains a declared fixture;10734executes compiled C and actual MMIO/blitter. Formatter/text bodies are fixtures unless --real-dependencies is set.')
 p.write_text(s);print(p)
if __name__=='__main__':main()
