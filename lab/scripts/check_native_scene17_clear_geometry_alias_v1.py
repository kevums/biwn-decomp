"""Coordinate/geometry alias fallback with six real original/native helpers.

One injected helper JSR per direction. GPU/formatter/text effects remain
fixtures. Compare CPU/nonarenaRAM/entries and exact suspended frame bytes.
"""
import argparse,json,os,struct
from pathlib import Path
from datetime import datetime,timezone
import check_native_deck_scene_reset_v1 as m
import check_deck_geometry_helpers_v1 as h
import check_deck_debug_overlay_cpu_v1 as debug
import fixture_ram_delta_v1 as delta
ROOT=m.ROOT;CPU=m.CPU;save=m.save;sha=m.sha
RANGES={**h.RANGES,0x110d4:0x11384,0x1142e:0x11762,0x10734:0x10968}
EXTERNAL={0xe26c,0x1b45a,0x149ae}
class Engine(h.Engine):
    arguments=debug.Engine.arguments
    def entry(self,memory,state):
        x=super().entry(memory,state);sp=state.registers[15];x['return_PC']=int.from_bytes(memory[sp:sp+4],'big');return x
    def effect(self,memory,state,target,case,index):
        if target==0xe26c:self.gpu_fixture(memory,state,case)
        else:raise AssertionError(target)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=64);args=ap.parse_args();assert 1<=args.limit<=64
    out=ROOT/'verification/native-scene17-clear-geometry-alias-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='preparing',pid=os.getpid(),directory=str(out),whole_game_complete=False,new_training=False,native_disc_changed=False)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-scene17-clear-geometry-alias-v1-current.json',state)
    mark()
    try:
        bp=ROOT/'verification/native-scene17-clear-disc-build-v1-current.json';b=json.loads(bp.read_text());gp=ROOT/'verification/native-Deck-scene17-clear-final-geometry-v1-current.json';g=json.loads(gp.read_text())
        assert g['completed']==256 and g['deployed_module_byte_identity'];m.CODE=b['shared_Deck_code_address'];m.ARENA=b['deck_arena_address']
        payload=Path(g['payload']).read_bytes();syms=g['symbols'];assert sha(payload)==g['payload_sha256']and len(payload)==b['shared_Deck_code_bytes']
        resident=Path(b['component']).read_bytes();assert payload==resident[m.CODE-b['resident_address']:m.CODE-b['resident_address']+len(payload)]
        save(out/'build-as-run.json',b);save(out/'gate-as-run.json',g)
        coordinate_ram,coordinate_cpu,coordinate_case=m.coordinate.fixtures()[0]
        _,geometry_cpu,geometry_case=m.fixtures('geometry')[0]
        m.scene.HELPERS=EXTERNAL;engine=Engine();rows=[]
        def run(ram,initial,case,outer,native):
            inner='geometry'if outer=='coordinate'else'coordinate';injection=0xe26c if outer=='coordinate'else 0x1b45a;continuation=injection+6
            memory=bytearray(ram);patches={m.LAYOUT[n][0]:(8 if n=='geometry'else 6)for n in ['coordinate','geometry']}
            if native:
                for name in ['coordinate','geometry']:
                    a=m.LAYOUT[name][0];n=patches[a];memory[a:a+n]=b'\x4e\xf9'+syms['biwn_v4_'+name].to_bytes(4,'big')+bytes.fromhex('4e71')*(n//2-3)
            task=int.from_bytes(ram[0xc0920:0xc0924],'big');base=m.ARENA+task-m.POOL
            engine.native.device.seed(bytes(memory),0);engine.set_cpu(initial,True);active={};entries=[];injected=0;protected=None
            counts=dict(coordinate=0,geometry=0);fallbacks=dict(counts);returns=dict(counts);markers=0;original_helper_steps=0
            def normalize(raw,final=False):
                result=bytearray(raw);result[m.ARENA:m.ARENA+m.SLOTS*1024]=ram[m.ARENA:m.ARENA+m.SLOTS*1024]
                for a,n in patches.items():result[a:a+n]=ram[a:a+n]
                for sp,(physical,logical)in active.items():
                    if int.from_bytes(result[sp:sp+4],'big')==physical:
                        assert not final,'Outstanding compiled helper return';result[sp:sp+4]=logical.to_bytes(4,'big')
                return result
            def finish(memory,cpu,target):
                if target in debug.WIDTHS:
                    debug.Engine.effect(engine,cpu,target,case,len(entries)-1)
                else:
                    before=engine.native.device.ram();engine.effect(memory,cpu,target,case,len(entries)-1);delta.apply(engine.native.device,before,bytes(memory))
                sp=cpu.registers[15];cpu.pc=engine.native.device.read(sp,4);cpu.registers[15]+=4
                if cpu.sr&0x2000:cpu.ssp=cpu.registers[15]
                else:cpu.usp=cpu.registers[15]
                engine.set_cpu(cpu)
            for steps in range(300000):
                cpu=engine.cpu();pc=cpu.pc;sp=cpu.registers[15]
                if pc==m.STOP:break
                if native:
                    for name in counts:
                        if pc==syms['biwn_v4_'+name]:counts[name]+=1
                        if pc==syms['biwn_v4_'+name+'_original_fallback']:fallbacks[name]+=1
                        if pc==syms['biwn_v4_'+name+'_return']:returns[name]+=1
                    if pc in [syms['biwn_v5_deeper_helper_marker'],syms['service_geometry_original'],syms['service_geometry_faces'],syms['service_geometry_debug']]:
                        raw=engine.native.device.ram();frame=int.from_bytes(raw[sp+4:sp+8],'big');target=int.from_bytes(raw[sp+(8 if pc==syms['biwn_v5_deeper_helper_marker']else 16):sp+(12 if pc==syms['biwn_v5_deeper_helper_marker']else 20)],'big');assert frame==base+16 and target in RANGES
                        values=struct.unpack('>19IH',raw[frame+4:frame+82]);virtual=CPU();virtual.registers[:]=values[:16];virtual.pc,virtual.usp,virtual.ssp,virtual.sr=values[16:]
                        # This native record stores only its active stack bank.
                        if virtual.sr&0x2000:assert cpu.usp==initial.usp;virtual.usp=cpu.usp
                        else:assert cpu.ssp==initial.ssp;virtual.ssp=cpu.ssp
                        assert virtual.pc==target;entries.append(engine.entry(normalize(raw),virtual));markers+=1
                if pc==continuation:
                    raw=bytearray(engine.native.device.ram())
                    if native:assert protected==[bytes(raw[base+16:base+134]),bytes(raw[base+832:base+1008])],'Alias child changed suspended native frame/stack'
                    finish(raw,cpu,injection);continue
                if pc in patches or pc in RANGES or pc in EXTERNAL or pc==0xe540:
                    raw=bytearray(engine.native.device.ram())
                    if native and pc in EXTERNAL|{0xe540}:
                        physical=int.from_bytes(raw[sp:sp+4],'big');ret=syms['biwn_v4_'+outer+'_helper_return']
                        if physical==ret:
                            frame=base+16;assert int.from_bytes(raw[frame+106:frame+110],'big')==sp;active[sp]=(ret,int.from_bytes(raw[frame+110:frame+114],'big'))
                    entries.append(engine.entry(normalize(raw),cpu))
                    if pc in EXTERNAL:
                        if pc==injection and not injected:
                            injected+=1
                            if native:protected=[bytes(raw[base+16:base+134]),bytes(raw[base+832:base+1008])]
                        else:finish(raw,cpu,pc);continue
                if any(a<=pc<b for a,b in RANGES.items()):original_helper_steps+=1
                allowed=0x11ad4<=pc<0x11b4c or 0x11d1a<=pc<0x11e64 or 0xe540<=pc<0xe588 or any(a<=pc<b for a,b in RANGES.items())or pc==injection
                assert allowed or(native and m.CODE<=pc<m.CODE+len(payload)),hex(pc);engine.core.m68k_execute(1)
            else:raise AssertionError(('alias work bound',hex(pc)))
            raw=engine.native.device.ram();assert injected==1
            for slot in range(m.SLOTS):
                a=m.ARENA+slot*1024
                for lo,hi in m.FENCES:assert raw[a+lo:a+hi]==ram[a+lo:a+hi]
            if native:
                assert counts==dict(coordinate=1,geometry=1)and returns[outer]==1 and returns[inner]==0 and fallbacks[inner]==1 and fallbacks[outer]==0,(counts,returns,fallbacks)
                assert markers==(6 if outer=='geometry'else 0)
                assert raw[base+130:base+134]==bytes(4)
                assert raw[m.ARENA:base]==ram[m.ARENA:base]and raw[base+1024:m.ARENA+m.SLOTS*1024]==ram[base+1024:m.ARENA+m.SLOTS*1024]
                allowed=set(range(16,134))|set(range(832,1008));assert all(i in allowed or raw[base+i]==ram[base+i]for i in range(1024))
                assert raw[m.CODE:m.CODE+len(payload)]==payload
            return bytes(normalize(raw,True)),engine.cpu(),entries,dict(instructions=steps,native_entries=counts,native_returns=returns,fallback_entries=fallbacks,native_deeper_helper_markers=markers,original_deeper_helper_steps=original_helper_steps,suspended_alias_frame_preserved=native)
        try:
            for outer in ['coordinate','geometry']:
                for i in range(args.limit):
                    memory=bytearray(coordinate_ram);memory[0x90000:0x90094]=memory[0x80000:0x80094];memory[0x80000:0x80002]=bytes(2);memory[0x90000:0x90002]=bytes(2);memory[0x80088:0x8008a]=bytes(2);memory[0x90088:0x9008a]=bytes(2);memory[m.CODE:m.CODE+len(payload)]=payload;memory[m.ARENA:m.ARENA+m.SLOTS*1024]=bytes([0xa5])*(m.SLOTS*1024)
                    for slot in range(m.SLOTS):
                        for _,off,_,_ in m.LAYOUT.values():memory[m.ARENA+slot*1024+off+114:m.ARENA+slot*1024+off+118]=bytes(4)
                    task=m.POOL+[0,1,6,100][i%4]*1024;sp=task+[0x3c0,0x3be,0x200][i%3];memory[sp-256:sp+32]=coordinate_ram[m.SP-256:m.SP+32];memory[sp:sp+4]=m.STOP.to_bytes(4,'big');memory[0xc0920:0xc0924]=task.to_bytes(4,'big')
                    initial=CPU.from_buffer_copy(bytes(coordinate_cpu if outer=='coordinate'else geometry_cpu));initial.pc=m.LAYOUT[outer][0];initial.sr=(0x2000 if i>=32 else 0)|(i%32);initial.registers[15]=sp;initial.usp=0x1d8000 if initial.sr&0x2000 else sp;initial.ssp=sp if initial.sr&0x2000 else 0x1ff000
                    injection=0xe26c if outer=='coordinate'else 0x1b45a;inner='geometry'if outer=='coordinate'else'coordinate';memory[injection:injection+6]=b'\x4e\xb9'+m.LAYOUT[inner][0].to_bytes(4,'big')
                    memory[0x403cc:0x403ce]=(1).to_bytes(2,'big');memory[0x403ca:0x403cc]=(i%4).to_bytes(2,'big')
                    case={**coordinate_case,**geometry_case,'variant':i,'held':0,'pressed':0,'mutate_counter':i%2==0,'mutate_globals':False};ram=bytes(memory)
                    expected,cpu,entries,_=run(ram,initial,case,outer,False);actual,got,observed,details=run(ram,initial,case,outer,True)
                    if expected!=actual or m.cpu_dict(cpu)!=m.cpu_dict(got)or entries!=observed:
                        save(out/'counterexample.json',dict(outer=outer,case=i,original_CPU=m.cpu_dict(cpu),native_CPU=m.cpu_dict(got),original_entries=entries,native_entries=observed,RAM_differences=[[hex(a),x,y]for a,(x,y)in enumerate(zip(expected,actual))if x!=y][:40]));raise AssertionError(out/'counterexample.json')
                    rows.append(dict(outer=outer,case=i,mode=initial.sr&0x2000,flags=i%32,task=hex(task),full_CPU_nonarena_RAM_entries_match=True,**details))
                    if i%8==0:state.update(status='checking',completed=len(rows));mark();print(outer,i+1,flush=True)
        finally:engine.native.close()
        save(out/'cases.json',rows);paths=[Path(__file__),Path(h.__file__),Path(m.__file__),Path(debug.__file__),Path(delta.__file__),out/'build-as-run.json',out/'gate-as-run.json',Path(g['payload']),out/'cases.json']
        state.update(status='terminal_deeper_coordinate_geometry_alias_fallback_match',completed=len(rows),source_sha256={str(p):sha(p.read_bytes())for p in paths},scope=__doc__+'64eachdirection covers bothbanks/allCCR,4taskslots,3guestSPdepths. Nativegeometry executes6compiledhelpers;busy innergeometry executes6original bodies. Face-count zero path only in this alias matrix;nonzero counts are covered by separate256native geometry cases. Injected1B45AorE26C JSR is an explicit fixture;remaining effects declared. No natural reentry/IRQ/fresh gameplay proof.')
        mark();print(state['status'],len(rows),flush=True)
    except BaseException as e:state.update(status='terminal_deeper_alias_checker_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
