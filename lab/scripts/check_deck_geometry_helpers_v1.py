"""Complete three-helper C bodies vs original68000, with110D4 declared effects."""
import argparse,ctypes as c,json,random,subprocess,os
from pathlib import Path
from datetime import datetime,timezone
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
import check_deck_coordinate_source_v1 as base
ROOT=base.ROOT;SRC=ROOT/'projects/black-ice-white-noise/restoration/experimental/deck-geometry-helpers-v1'
CPU=base.CPU;Bus=base.Bus;SERVICE=base.SERVICE;SP=base.SP;STOP=base.STOP
RANGES={0x10968:0x10990,0x10ba4:0x10c18,0x11384:0x1142e}
W8=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint8)
save=base.save;sha=base.sha;cpu_dict=base.cpu_dict
def sx16(v):return (v&32767)-(v&32768)

class Engine(base.Engine):
    def service_effect(self,memory,state,case):
        for n in [0,1,8,9]:state.registers[n]=(0x93ab7811*(n+1)+case['variant']*37)&0xffffffff
        state.sr=(state.sr&0xffe0)|((case['variant']*13)&31)
        def put(a,w,v):memory[a:a+w]=(v&((1<<(8*w))-1)).to_bytes(w,'big')
        put(0x70000,4,0x110d4000|case['variant'])
        if case['mutate_counter']:put(0x49b88,4,[0,3,0xffffffff,0xfffffffe,0x4000001][case['variant']%5])
        put(0x400c4,4,(0x5e123456+case['variant']*7)&0xffffffff)
        state.pc=0x11300 # Service body stops before its own RTS; host consumes it.
    def original(self,ram,initial,case):
        self.native.device.seed(ram,0);self.set_cpu(initial,True);coverage=set();entries=[]
        for steps in range(500000):
            s=self.cpu();pc=s.pc
            if pc==STOP:break
            if pc==0x110d4:
                memory=bytearray(self.native.device.ram());entries.append(self.entry(memory,s));self.service_effect(memory,s,case)
                self.native.device.seed(bytes(memory),0);s.pc=int.from_bytes(memory[s.registers[15]:s.registers[15]+4],'big');s.registers[15]+=4
                if s.sr&0x2000:s.ssp=s.registers[15]
                else:s.usp=s.registers[15]
                self.set_cpu(s);continue
            assert initial.pc<=pc<RANGES[initial.pc],hex(pc)
            coverage.add(pc);self.core.m68k_execute(1)
        else:raise AssertionError(('original instruction bound',hex(pc),case))
        return self.native.device.ram(),self.cpu(),entries,coverage,steps
    def translated(self,fn,ram,initial,case,fail=None,byte_budget=65536,service_fault=None):
        memory=bytearray(ram);entries=[];events=[];errors=[]
        def reader(w):
            def cb(_,a,value):
                if fail==len(events):return 1
                if a+w>len(memory)or(w>1 and a&1):errors.append(['read',a,w]);return 1
                value[0]=int.from_bytes(memory[a:a+w],'big');events.append(['r',a,w,value[0]]);return 0
            return cb
        def writer(w):
            def cb(_,a,value):
                if fail==len(events):return 1
                if a+w>len(memory)or(w>1 and a&1):errors.append(['write',a,w]);return 1
                memory[a:a+w]=(value&((1<<(8*w))-1)).to_bytes(w,'big');events.append(['w',a,w,value]);return 0
            return cb
        def service(_,bus,pointer,target):
            try:
                assert target==0x110d4,hex(target);state=pointer.contents;entries.append(self.entry(memory,state))
                if service_fault=='error':return 1
                self.service_effect(memory,state,case)
                if service_fault=='stack':state.registers[15]+=4
                if service_fault=='return':memory[state.registers[15]:state.registers[15]+4]=bytes(4)
                return 0
            except BaseException as e:errors.append(repr(e));return 1
        w=base.scheduler.cleanup.world
        callbacks=[w.R8(reader(1)),w.R16(reader(2)),w.R32(reader(4)),w.W16(writer(2)),w.W32(writer(4)),W8(writer(1)),SERVICE(service)]
        bus=Bus(*callbacks[:5],w.CALL(),None,0);s=CPU.from_buffer_copy(bytes(initial))
        status=fn(c.byref(bus),callbacks[5],c.byref(s),callbacks[6],None,1,byte_budget)
        return status,bytes(memory),s,entries,events,errors

def fixtures():
    baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rng=random.Random(0x1096810ba411384)
    for root in RANGES:
        for i in range(260 if root==0x10968 else 256):
            state=CPU();state.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[SP];state.pc=root
            state.sr=(0x2000 if i&1 else 0)|((i//2)%32)|(((i//64)%8)<<8)
            state.usp=0x1d8000 if i&1 else SP;state.ssp=SP if i&1 else 0x1ff000
            memory=bytearray(baseline);memory[SP-256:SP+32]=rng.randbytes(288);memory[SP:SP+4]=STOP.to_bytes(4,'big')
            def put(a,w,v):memory[a:a+w]=(v&((1<<(8*w))-1)).to_bytes(w,'big')
            if root==0x10968:
                start=[-1024,-1,0,1,7,15,1024][i%7]
                count=[0,1,2,7][i%4]if i<256 else[512,0xffff,0x8000,0x7fff][i-256]
                put(SP+4,2,start);put(SP+6,2,count)
                # Mark the complete maximum write region without touching code.
                at=0x47b88+start*64;memory[at:at+65536]=rng.randbytes(65536)
                put(SP,4,STOP);put(SP+4,2,start);put(SP+6,2,count)
            elif root==0x10ba4:
                descriptor=0x80000;put(0x400e6,4,descriptor)
                timer=[0,1,2,0x7fff,0x8000,0xffff][i%6];frame=[0,1,0x7ffe,0x7fff,0x8000,0xfffe,0xffff][(i//2)%7]
                limit=[0,1,2,0x7fff,0x8000,0xffff][(i//3)%6];offset=[0,1,0xffff,0x7fff,0x8000][(i//7)%5]
                put(0x403d4,2,timer);put(descriptor+0x90,2,rng.getrandbits(16));put(0x403d0,2,frame);put(0x403d2,2,limit);put(0x403da,2,offset)
                put(0x23f88,4,rng.getrandbits(32));put(0x23f8c,4,rng.getrandbits(32))
                advanced=(frame+1)&65535
                if sx16(limit)<=sx16(advanced):advanced=0
                index=sx16(((sx16(advanced)>>1)+offset)&65535);address=0x4674c+index*8
                if not 0x40000<=address<0x40500:put(address,4,rng.getrandbits(32))
            else:
                counter=[0,1,7,0xffffffff,0xfffffffe,0x4000000][i%6];put(0x49b88,4,counter)
                for a in [0x49b8c,0x49b8e,0x49b90]:put(a,2,[0,1,0x7fff,0x8000,0xffff][(i+a)%5])
                put(0x403ce,2,rng.getrandbits(16));put(0x400e6,4,0x80000);put(0x400c4,4,rng.getrandbits(32))
            yield bytes(memory),state,dict(root=root,variant=i,mutate_counter=i%2==0)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);ap.add_argument('--limit',type=int);args=ap.parse_args()
    out=ROOT/'verification/deck-geometry-helpers-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='compiling',pid=os.getpid(),directory=str(out),source=str(args.source),whole_game_complete=False,new_training=False,native_disc_changed=False)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/deck-geometry-helpers-v1-current.json',state)
    mark()
    try:
        library=out/'libgeometry-helpers.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(SRC),str(args.source),str(SRC/'helper-adapter.c'),'-o',str(library)]
        p=subprocess.run(command,capture_output=True,text=True);(out/'compiler.log').write_text(p.stdout+p.stderr)
        if p.returncode:state.update(status='terminal_source_compile_rejected',compiler_exit_code=p.returncode);mark();print(p.stderr,flush=True);return
        fn=c.CDLL(str(library)).biwn_geometry_helper_call;fn.argtypes=[c.POINTER(Bus),W8,c.POINTER(CPU),SERVICE,c.c_void_p,c.c_uint32,c.c_uint32];fn.restype=c.c_int
        engine=Engine();rows=[];covered=set();guards=[];samples={}
        try:
            for ram,initial,case in fixtures():
                if args.limit and case['variant']>=args.limit:continue
                expected,cpu,entries,seen,steps=engine.original(ram,initial,case)
                status,actual,got,observed,events,errors=engine.translated(fn,ram,initial,case)
                if status or errors or expected!=actual or cpu_dict(cpu)!=cpu_dict(got)or entries!=observed:
                    save(out/'counterexample.json',dict(case=case,status=status,errors=errors,initial_CPU=cpu_dict(initial),original_CPU=cpu_dict(cpu),C_CPU=cpu_dict(got),original_entries=entries,C_entries=observed,RAM_differences=[[hex(a),x,y]for a,(x,y)in enumerate(zip(expected,actual))if x!=y][:48]))
                    state.update(status='terminal_original_CPU_or_RAM_comparison_rejected',completed=len(rows),counterexample=str(out/'counterexample.json'));mark();return
                covered|=seen;rows.append(dict(root=hex(initial.pc),variant=case['variant'],original_steps=steps,C_events=len(events),helper_entries=len(entries),full_CPU_full_RAM_and_helper_entries_match=True))
                if case['variant']==1:samples[initial.pc]=(ram,initial,case,events)
                if len(rows)%32==0:state.update(status='checking',completed=len(rows),root=hex(initial.pc));mark();print('completed',len(rows),hex(initial.pc),flush=True)
            if not args.limit:
                for root,(ram,initial,case,events)in samples.items():
                    for index in range(len(events)):
                        status,_,got,_,_,errors=engine.translated(fn,ram,initial,case,fail=index)
                        assert status==2 and not errors and cpu_dict(got)==cpu_dict(initial),(hex(root),index,status)
                        guards.append(dict(root=hex(root),bus_failure=index))
                ram,initial,case,_=samples[0x11384]
                for fault,want in [('error',3),('stack',5),('return',5)]:
                    status,_,got,_,_,errors=engine.translated(fn,ram,initial,case,service_fault=fault)
                    assert status==want and not errors and cpu_dict(got)==cpu_dict(initial);guards.append(dict(service_fault=fault))
                ram,initial,case,_=samples[0x10968];status,_,got,_,_,errors=engine.translated(fn,ram,initial,case,byte_budget=63)
                assert status==4 and not errors and cpu_dict(got)==cpu_dict(initial);guards.append(dict(byte_budget=63))
        finally:engine.native.close()
        baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();decoder=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
        locations={x.address for a,b in RANGES.items()for x in decoder.disasm(baseline[a:b],a)}
        assert args.limit or covered==locations,[hex(x)for x in sorted(locations-covered)]
        save(out/'cases.json',rows);save(out/'guards.json',guards)
        paths=[Path(__file__),args.source,SRC/'helper-adapter.c',SRC/'helper-contract.h',SRC.parent/'deck-scene-source/deck-scene-contract.h',SRC.parent/'deck-coordinate-update-v2/deck-coordinate-contract.h',Path(base.__file__)]
        state.update(status='terminal_helper_preflight_pass'if args.limit else'terminal_three_deeper_helpers_full_CPU_RAM_match',completed=len(rows),counts={hex(a):sum(x['root']==hex(a)for x in rows)for a in RANGES},instruction_locations=[len(covered),len(locations)],guard_cases=len(guards),source_sha256={str(p.resolve()):sha(p.read_bytes())for p in paths},
            scope='Complete3helper bodies includingRTS;finite RAM fixtures,32CCR,both stack banks,partial registers,signed/frame wraps,large CLR counters,mutating110D4 service.110D4 remains fixture;MMIO,arbitrary aliases,IRQ,timing,native relocation and disc integration unverified.')
        mark();print(state['status'],state.get('counts'),flush=True)
    except BaseException as e:state.update(status='terminal_checker_failed',error=repr(e));mark();raise

if __name__=='__main__':main()
