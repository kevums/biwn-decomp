"""Native CPU/full RAM/cost oracle for the new cache instruction semantics."""
import ctypes as c
import json, random, os
from datetime import datetime, timezone
from pathlib import Path
from check_local_GPU_wait_C import Bus, R8, R16, R32, W16, W32, CALL
from check_biwn_scheduler import Native, CPU, cpu_dict
from run_biwn_native_fast_gameplay_route import ROOT, sha, save
import generate_biwn_atomic_startup_math as math
import biwn_geometry_CPU_semantics_v2 as semantics
import biwn_cache_cluster_CPU_semantics as base_semantics


def read(p):
    return json.loads(Path(p).read_text())


def main():
    bp = ROOT/'verification/geometry-C-runtime-build-current.json'
    build = read(bp)
    assert build['status'] == 'terminal_geometry_C_compiled_pending_checks'
    cp = Path(build['CPU_candidate'])
    candidate = read(cp)
    atlas = Path(candidate['instruction_RAM_source']).read_bytes()
    listing = read(Path(build['directory'])/'new-instructions.json')['instructions']
    entries = []
    for ins in listing:
        pc = int(ins['address'],16)
        row = math.base.binary_tools.m68k_instructions(atlas[pc:pc+ins['size']],pc)[0][0]
        entries.append(row)
    assert len(entries)==build['static_instruction_starts'] and len(entries)>=100
    library = c.CDLL(candidate['library'])
    fn = getattr(library,candidate['function'])
    fn.argtypes = [c.POINTER(Bus),c.POINTER(CPU),c.c_void_p,c.c_void_p,c.c_void_p]
    fn.restype = c.c_int
    costp = Path(read(ROOT/'verification/CPU-division-provider-build-current.json')['cost_candidate'])
    cost = read(costp)
    costs = c.CDLL(cost['library']).biwn_native_cycle_cost
    costs.argtypes = [c.c_uint16,c.POINTER(CPU),c.c_void_p]
    costs.restype = c.c_int
    core = ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source/virtualjaguar_libretro.dylib'
    out = ROOT/'verification/geometry-CPU-instructions'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    (out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes())
    print(out,flush=True)
    save(out/'entries.json',entries)
    fixture = bytearray(atlas)
    fixture[20:24] = (0x190000).to_bytes(4,'big')
    fixture[32:36] = (0x190100).to_bytes(4,'big')
    fixture[0x190000:0x190002] = bytes.fromhex('4e73')
    fixture[0x190100:0x190102] = bytes.fromhex('4e73')
    rng = random.Random(0x16278244)
    for at in [0x170000+i*0x1000 for i in range(7)]+[0x1d0000,0x1e0000]:
        for offset in range(-16,132,4):
            fixture[at+offset:at+offset+4] = rng.getrandbits(32).to_bytes(4,'big')
    image = bytearray(fixture)
    buffer = (c.c_uint8*len(image)).from_buffer(image)
    accesses, callback_errors = [], []
    def reader(width):
        def cb(_,a,p):
            if a>len(image)-width:
                callback_errors.append(['r',a,width]);return 1
            p[0] = int.from_bytes(image[a:a+width],'big')
            accesses.append(['r',a,width,int(p[0])]);return 0
        return cb
    def writer(width):
        def cb(_,a,value):
            if a>len(image)-width:
                callback_errors.append(['w',a,width]);return 1
            image[a:a+width] = int(value).to_bytes(width,'big')
            accesses.append(['w',a,width,int(value)]);return 0
        return cb
    W8 = c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint8)
    callbacks = [R8(reader(1)),R16(reader(2)),R32(reader(4)),W16(writer(2)),W32(writer(4)),W8(writer(1))]
    bus = Bus(*callbacks[:5],CALL(),None,0)
    n = Native(diagnostic_core=core)
    rows, mismatches = [], []
    state = dict(status='running_native_instruction_semantics_checks',pid=os.getpid(),directory=str(out),entries=len(entries),new_training=False,whole_game_complete=False)
    def mark():
        save(out/'protocol.json',state)
        save(ROOT/'verification/geometry-CPU-instructions-active.json',state)
    mark()
    values = [0,0xffffffff,0x270f270f]
    try:
        for entry in entries:
            for mode in [0,0x2000]:
                for ipl in [0,7]:
                    for flags in range(32):
                        for variant,value in enumerate(values):
                            image[:] = fixture
                            regs = [rng.getrandbits(32) for _ in range(8)]+[0x170000+i*0x1000 for i in range(7)]+[0x1d0000]
                            op,args = base_semantics.parts(entry)
                            if op in ['subx.l','subi.l','ori.l'] or op.startswith('s') and op.endswith('.b'):
                                for i in range(8):regs[i] = value
                            if op == 'divs.w':
                                source,dest = int(args[0][1]),int(args[1][1])
                                regs[dest] = value
                                divisor = [0,1,0xffff,0x8000,0x7fff,0,2,0xffff][variant]
                                regs[source] = (regs[source]&0xffff0000)|divisor
                            if op == 'move.w' and args[-1] == 'ccr' and args[0].startswith('d'):
                                regs[int(args[0][1])] = value
                            n.device.seed(bytes(fixture),0)
                            l = n.lib
                            l.m68k_pulse_reset();l.m68k_set_irq(0)
                            l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,0x1e0000)
                            l.m68k_set_reg(17,0);l.m68k_set_reg(15,0x1c0000)
                            sr = mode|(ipl<<8)|flags
                            l.m68k_set_reg(17,sr)
                            for i,v in enumerate(regs):l.m68k_set_reg(i,v)
                            l.m68k_set_reg(16,entry['address'])
                            before = CPU();before.registers[:] = regs;before.pc = entry['address'];before.sr = sr
                            before.usp = n.prefix[16] if mode else regs[15]
                            before.ssp = regs[15] if mode else n.prefix[17]
                            actual = CPU.from_buffer_copy(bytes(before))
                            accesses.clear();callback_errors.clear()
                            predicted = costs(int(entry['bytes'][:4],16),c.byref(before),buffer)
                            status = fn(c.byref(bus),c.byref(actual),c.cast(callbacks[5],c.c_void_p),None,None)
                            native_cost = l.m68k_execute(1)
                            expected = CPU();expected.registers[:] = [l.m68k_get_reg(None,i) for i in range(16)]
                            expected.pc = l.m68k_get_reg(None,16);expected.sr = l.m68k_get_reg(None,17)
                            expected.usp = n.prefix[16] if expected.sr&0x2000 else expected.registers[15]
                            expected.ssp = expected.registers[15] if expected.sr&0x2000 else n.prefix[17]
                            same_CPU = cpu_dict(actual)==cpu_dict(expected)
                            same_RAM = bytes(image)==n.device.ram()
                            passed = status in [0,11] and same_CPU and same_RAM and predicted==native_cost and not callback_errors
                            result = dict(pc=hex(entry['address']),SR=sr,variant=variant,status=status,CPU_equal=same_CPU,RAM_equal=same_RAM,C_cost=predicted,native_cost=native_cost,passed=passed)
                            rows.append(result)
                            if not passed:
                                mismatches.append(dict(**result,assembly=entry['assembly'],before=cpu_dict(before),actual=cpu_dict(actual),expected=cpu_dict(expected),C_accesses=list(accesses),callback_errors=list(callback_errors)))
                                save(out/'first-mismatches.json',mismatches)
                                raise AssertionError(('Native instruction mismatch',hex(entry['address']),entry['assembly']))
            state['completed_cases']=len(rows);mark();print(hex(entry['address']),len(rows),flush=True)
        save(out/'cases.json',rows)
        state.update(status='terminal_geometry_CPU_instructions_native_and_cost_pass',cases=len(rows),failed_cases=0,
                     CPU_candidate=str(cp),cost_candidate=str(costp),
                     source_sha256={str(p):sha(p) for p in [out/'runner-as-run.py',Path(semantics.__file__),cp,Path(candidate['library']),Path(candidate['instruction_RAM_source']),costp,Path(cost['library']),core]},
                     scope='All listed instruction emissions in the geometry extension and regenerated startup/redirect sites; all32CCR,two stack modes,IPL0/7,three operand profiles. FullD/A/PC/SR/USP/SSP,2MBRAM andpinned emulator cycles. ControlledvalidRAM only;no arbitraryalias/fault/IRQ,physicaltiming,orhigh-levelfunction recovery proof. Newsites arestaticcatalogueentries,not recoveredfunctiontotals;wholefunction coupling andgameplay areseparate checks.')
        mark();save(ROOT/'verification/geometry-CPU-instructions-current.json',state)
        print(state['status'],len(rows),flush=True)
    except BaseException as error:
        state.update(status='terminal_geometry_CPU_instructions_failed',error=repr(error),cases=len(rows));mark();raise
    finally:
        n.close()


if __name__ == '__main__':
    main()
