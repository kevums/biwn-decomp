"""Geometry11AD4 with three recovered helpers versus actual original68000."""
import argparse,ctypes as c,json,subprocess,os
from pathlib import Path
from datetime import datetime,timezone
import check_deck_geometry_helpers_v1 as h
import check_deck_scene_source_v1 as scene
ROOT=h.ROOT;SRC=h.SRC;CPU=h.CPU;Bus=h.Bus;SERVICE=h.SERVICE
ORIGINAL_RANGES={0x11ad4:0x11b4c,**h.RANGES};EXTERNAL={0x110d4,0x1142e,0x10734}
save=h.save;sha=h.sha;cpu_dict=h.cpu_dict
class Engine(h.Engine):
    def effect(self,memory,state,case):
        if state.pc==0x110d4:self.service_effect(memory,state,case)
        else:scene.Engine.helper(self,memory,state,state.pc,case,case['service_number'])
    def original(self,ram,initial,case):
        self.native.device.seed(ram,0);self.set_cpu(initial,True);coverage=set();entries=[];service_number=0
        for step in range(10000):
            s=self.cpu();pc=s.pc
            if pc==h.STOP:break
            if pc in h.RANGES or pc in EXTERNAL:entries.append(self.entry(self.native.device.ram(),s))
            if pc in EXTERNAL:
                memory=bytearray(self.native.device.ram());self.effect(memory,s,dict(case,service_number=service_number));service_number+=1
                self.native.device.seed(bytes(memory),0);s.pc=int.from_bytes(memory[s.registers[15]:s.registers[15]+4],'big');s.registers[15]+=4
                if s.sr&0x2000:s.ssp=s.registers[15]
                else:s.usp=s.registers[15]
                self.set_cpu(s);continue
            assert any(a<=pc<b for a,b in ORIGINAL_RANGES.items()),hex(pc)
            coverage.add(pc);self.core.m68k_execute(1)
        else:raise AssertionError('connected original bound')
        return self.native.device.ram(),self.cpu(),entries,coverage,step
    def translated(self,fn,helper,ram,initial,case):
        memory=bytearray(ram);entries=[];events=[];errors=[];service_number=0
        def reader(width):
            def cb(_,a,value):
                if a+width>len(memory)or(width>1 and a&1):errors.append(['read',a,width]);return 1
                value[0]=int.from_bytes(memory[a:a+width],'big');events.append(['r',a,width]);return 0
            return cb
        def writer(width):
            def cb(_,a,value):
                if a+width>len(memory)or(width>1 and a&1):errors.append(['write',a,width]);return 1
                memory[a:a+width]=(value&((1<<(width*8))-1)).to_bytes(width,'big');events.append(['w',a,width]);return 0
            return cb
        def service(_,bus,pointer,target):
            nonlocal service_number
            try:
                state=pointer.contents;entries.append(self.entry(memory,state))
                if target in h.RANGES:return helper(bus,callbacks[5],pointer,callbacks[6],None,65536)
                assert target in EXTERNAL,hex(target)
                self.effect(memory,state,dict(case,service_number=service_number));service_number+=1;return 0
            except BaseException as e:errors.append(repr(e));return 1
        w=h.base.scheduler.cleanup.world
        callbacks=[w.R8(reader(1)),w.R16(reader(2)),w.R32(reader(4)),w.W16(writer(2)),w.W32(writer(4)),h.W8(writer(1)),SERVICE(service)]
        bus=Bus(*callbacks[:5],w.CALL(),None,0);s=CPU.from_buffer_copy(bytes(initial))
        status=fn(c.byref(bus),c.byref(s),callbacks[6],None,8)
        return status,bytes(memory),s,entries,events,errors
def fixtures():
    scene.ROOTS={0x11ad4:0x11b4c}
    for ram,initial,case in scene.fixtures():
        memory=bytearray(ram);i=case['variant']
        def put(a,w,v):memory[a:a+w]=(v&((1<<(w*8))-1)).to_bytes(w,'big')
        put(0x400e6,4,0x80000);put(0x80090,2,[0,1,0x7fff,0x8000,0xffff][i%5])
        put(0x403d4,2,[0,1,0xffff,0x7fff,0x8000][i%5]);put(0x403d0,2,[0,1,0x7fff,0x8000,0xffff][(i//3)%5]);put(0x403d2,2,[0,1,4,0x7fff,0x8000,0xffff][(i//5)%6]);put(0x403da,2,[0,1,0xffff,0x7fff,0x8000][(i//7)%5])
        for a in [0x49b8c,0x49b8e,0x49b90]:put(a,2,[0,1,0x7fff,0x8000,0xffff][(i+a)%5])
        yield bytes(memory),initial,dict(case,mutate_counter=i%2==0)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);ap.add_argument('--limit',type=int);args=ap.parse_args()
    out=ROOT/'verification/deck-geometry-connected-helpers-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='compiling',pid=os.getpid(),directory=str(out),source=str(args.source),whole_game_complete=False,new_training=False,native_disc_changed=False)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/deck-geometry-connected-helpers-v1-current.json',state)
    mark()
    try:
        library=out/'libconnected.dylib';sources=[args.source,SRC/'helper-service-adapter.c',scene.SRC/'deck-scene-source.c']
        command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(SRC),*[str(p)for p in sources],'-o',str(library)]
        p=subprocess.run(command,capture_output=True,text=True);(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
        lib=c.CDLL(str(library));fn=lib.biwn_deck_scene_call;fn.argtypes=[c.POINTER(Bus),c.POINTER(CPU),SERVICE,c.c_void_p,c.c_uint32];fn.restype=c.c_int
        helper=lib.biwn_geometry_helper_service;helper.argtypes=[c.POINTER(Bus),h.W8,c.POINTER(CPU),SERVICE,c.c_void_p,c.c_uint32];helper.restype=c.c_int
        engine=Engine();rows=[];coverage=set()
        try:
            for ram,initial,case in fixtures():
                if args.limit and case['variant']>=args.limit:continue
                expected,cpu,entries,seen,steps=engine.original(ram,initial,case)
                status,actual,got,observed,events,errors=engine.translated(fn,helper,ram,initial,case)
                if status or errors or expected!=actual or cpu_dict(cpu)!=cpu_dict(got)or entries!=observed:
                    save(out/'counterexample.json',dict(case=case,status=status,errors=errors,original_CPU=cpu_dict(cpu),C_CPU=cpu_dict(got),original_entries=entries,C_entries=observed,RAM_differences=[[hex(a),x,y]for a,(x,y)in enumerate(zip(expected,actual))if x!=y][:48]));raise AssertionError(out/'counterexample.json')
                coverage|=seen;rows.append(dict(case=case['variant'],original_steps=steps,C_events=len(events),callee_entries=len(entries),full_CPU_full_RAM_callee_entries_match=True))
                if len(rows)%32==0:state.update(status='checking',completed=len(rows));mark();print('completed',len(rows),flush=True)
        finally:engine.native.close()
        save(out/'cases.json',rows)
        paths=[Path(__file__),Path(h.__file__),*sources,SRC/'helper-contract.h',scene.SRC/'deck-scene-contract.h',SRC.parent/'deck-coordinate-update-v2/deck-coordinate-contract.h']
        state.update(status='terminal_connected_preflight_pass'if args.limit else'terminal_geometry_with_three_recovered_helpers_CPU_RAM_match',completed=len(rows),recovered_helper_calls_each=len(rows),original_110D4_fixture_calls=len(rows),remaining_original_helper_fixture_calls=2*len(rows),original_instruction_locations=len(coverage),
            source_sha256={str(p.resolve()):sha(p.read_bytes())for p in paths},scope='Geometry11AD4 caller and three recovered helper algorithms execute as C. Original68000 lane executes all four bodies;110D4,1142E,10734 are declared fixtures in both. FullCPU/RAM/orderedcalleeentry match. Not native68000compiledC,disc installation,fresh gameplay,timing,MMIO or IRQ proof.')
        mark();print(state['status'],flush=True)
    except BaseException as e:state.update(status='terminal_connected_checker_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
