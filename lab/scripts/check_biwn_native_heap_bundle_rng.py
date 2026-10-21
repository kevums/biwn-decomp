"""Compile a proposed native RNG engine and compare original CPU behavior.

The native oracle runs the retained M68000 core through function pointers in
a small host C loop. It does not implement RNG or instruction semantics.
Unicorn separately checks ordered external accesses and declared rereads.
Candidate RNG instructions execute in the new resident C/ABI bundle. Math calls execute the separately source-assembled, byte-identical runtime at its original fixed addresses; they are explicitly allowed, not opaque instruction fallbacks.
"""
import argparse
import copy
import ctypes as c
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/'scripts'))
import check_biwn_rng as fixtures
from check_biwn_scheduler import Native
from check_biwn_native_button_digit import SP, STOP
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.m68k_const import UC_CPU_M68K_M68000, UC_M68K_REG_SR, UC_M68K_REG_A7, UC_M68K_REG_PC

BASE = 0x15edc0
ENTRIES = {
    0x1a6e0:'biwn_native_rng_init', 0x1a6f8:'biwn_native_rng_current',
    0x1a77c:'biwn_native_rng_indexed', 0x1a7f4:'biwn_native_rng_fill',
    0x1a87a:'biwn_native_rng_select', 0x1a8c6:'biwn_native_rng_seed',
    0x1a8e2:'biwn_native_rng_get', 0x1a8f8:'biwn_native_rng_set',
}
ORACLE = r'''
#include <stdint.h>
#include <string.h>
typedef int(*execute_fn)(int);
typedef unsigned(*get_fn)(void*,int);
struct stats {uint32_t status,pc;uint64_t steps,cycles;uint8_t coverage[0x23e];};
int run_cpu(execute_fn execute,get_fn get,uint32_t stop,uint32_t sp,
            uint32_t base,uint32_t end,int reference,uint32_t limit,struct stats*out){
 memset(out,0,sizeof(*out));
 for(uint32_t i=0;i<limit;i++){
  uint32_t pc=get(0,16);out->pc=pc;
  if(pc==stop&&get(0,15)==sp+4)return 0;
  int allowed=reference?((pc>=0x1a6e0&&pc<0x1a91e)||(pc>=0xe540&&pc<0xe61c)):((pc>=base&&pc<end)||(pc>=0xe540&&pc<0xe61c));
  if(!allowed){out->status=1;return 1;}
  if(reference&&pc>=0x1a6e0&&pc<0x1a91e)out->coverage[pc-0x1a6e0]=1;
  int cycles=execute(1);if(cycles<=0){out->status=3;return 3;}
  out->cycles+=(unsigned)cycles;out->steps++;
 }
 out->status=2;return 2;
}
'''


class Stats(c.Structure):
    _fields_ = [('status',c.c_uint32),('pc',c.c_uint32),('steps',c.c_uint64),
                ('cycles',c.c_uint64),('coverage',c.c_uint8*0x23e)]


def save(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n')


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def make_vectors(limit=None):
    rows = [copy.deepcopy(row) for row in fixtures.cases() if row['entry'] in ENTRIES]
    counters = {entry:0 for entry in ENTRIES}
    selected = []
    for row in rows:
        ordinal = counters[row['entry']]; counters[row['entry']] += 1
        if limit and ordinal >= limit:
            continue
        row['sr'] = (ordinal%32) | (0x2000 if (ordinal//32)%2 else 0)
        selected.append(row)
    return selected


def initial_image(image, case):
    result = bytearray(image)
    for address,width,value in case['initial']:
        result[address:address+width] = value.to_bytes(width,'big')
    args = b''.join(value.to_bytes(width,'big') for value,width in zip(
        case['params'], fixtures.ENTRY_WIDTHS.get(case['entry'],[])))
    result[SP:SP+4+len(args)] = STOP.to_bytes(4,'big')+args
    return result


def native_run(native, oracle, image, entry, case, code_length, reference):
    native.device.seed(bytes(image),0)
    lib = native.lib
    lib.m68k_pulse_reset(); lib.m68k_set_irq(0)
    supervisor = bool(case['sr']&0x2000)
    lib.m68k_set_reg(17,0x2000); lib.m68k_set_reg(15,SP if supervisor else 0x1ff000)
    lib.m68k_set_reg(17,0); lib.m68k_set_reg(15,0x1fe000 if supervisor else SP)
    lib.m68k_set_reg(17,case['sr'])
    registers = list(case['incoming'])[:15]+[SP]
    for index,value in enumerate(registers):
        lib.m68k_set_reg(index,value)
    lib.m68k_set_reg(16,entry)
    stats = Stats()
    status = oracle.run_cpu(c.cast(lib.m68k_execute,c.c_void_p),
        c.cast(lib.m68k_get_reg,c.c_void_p), STOP,SP,BASE,BASE+code_length,
        reference,5_000_000,c.byref(stats))
    cpu = dict(registers=[lib.m68k_get_reg(None,index)for index in range(16)],
               pc=lib.m68k_get_reg(None,16),sr=lib.m68k_get_reg(None,17))
    cpu['usp'] = native.prefix[16] if cpu['sr']&0x2000 else cpu['registers'][15]
    cpu['ssp'] = cpu['registers'][15] if cpu['sr']&0x2000 else native.prefix[17]
    assert status==0,dict(status=status,pc=hex(stats.pc),steps=stats.steps,cpu=cpu)
    return cpu,native.device.ram(),stats


def trace_run(image, entry, case, code_length, reference):
    engine = Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
    engine.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    engine.mem_map(0,0x200000); engine.mem_write(0,bytes(image))
    for reg,value in zip(fixtures.world.REGS,case['incoming']):
        engine.reg_write(reg,value)
    engine.reg_write(UC_M68K_REG_SR,case['sr']); engine.reg_write(UC_M68K_REG_A7,SP)
    queues={(row['address'],row['width']):list(row['values'])for row in case.get('read_queues',[])}
    trace=[]; steps=0
    def code(emu,address,width,_):
        nonlocal steps
        assert ((0x1a6e0<=address<0x1a91e or 0xe540<=address<0xe61c)if reference else (BASE<=address<BASE+code_length or 0xe540<=address<0xe61c)),hex(address)
        steps+=1
    def ignored(address,width):
        return SP-0x4000<=address and address+width<=SP+16 or BASE<=address and address+width<=BASE+code_length
    def read(emu,access,address,width,value,_):
        if ignored(address,width):return
        queue=queues.get((address,width))
        if queue:
            emu.mem_write(address,queue.pop(0).to_bytes(width,'big'))
        trace.append(['r',address,width,int.from_bytes(emu.mem_read(address,width),'big')])
    def write(emu,access,address,width,value,_):
        if ignored(address,width):return
        trace.append(['w',address,width,value&((1<<(width*8))-1)])
    engine.hook_add(UC_HOOK_CODE,code)
    engine.hook_add(UC_HOOK_MEM_READ,read)
    engine.hook_add(UC_HOOK_MEM_WRITE,write)
    engine.emu_start(entry,STOP,count=5_000_000,timeout=20_000_000)
    assert engine.reg_read(UC_M68K_REG_PC)==STOP
    return trace,bytes(engine.mem_read(0,0x200000)),steps


def normalized(ram, reference, length):
    result=bytearray(ram)
    result[BASE:BASE+length]=reference[BASE:BASE+length]
    result[SP-0x4000:SP]=reference[SP-0x4000:SP]
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--limit',type=int)
    parser.add_argument('--phase',choices=['cpu','trace','both'],default='both')
    args=parser.parse_args()
    out=ROOT/'verification/native-heap-bundle-rng'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True); print(out,flush=True)
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),candidate=str(args.source.resolve()),
               candidate_sha256=sha(args.source),limit=args.limit,phase=args.phase,whole_game_complete=False,
               source_accepted=False,zero_divisor_behavior_verified=False,native_Chat=False)
    def checkpoint():
        save(out/'protocol.json',state);save(ROOT/'verification/native-heap-bundle-rng-active.json',state)
    checkpoint()
    try:
        native_source=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
        command=['make','-f','Makefile.heap-bundle','heap-bundle','BUILD='+str(out/'build'),'RNG_SOURCE='+str(args.source.resolve())]
        built=subprocess.run(command,cwd=native_source,capture_output=True,text=True)
        (out/'make.log').write_text(built.stdout+built.stderr)
        assert built.returncode==0,built.stderr
        elf=out/'build/native-heap-bundle.elf'; binary=out/'build/native-heap-bundle.bin'; payload=binary.read_bytes()
        prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-')
        symbols={}
        for line in subprocess.check_output([prefix+'nm','--defined-only',str(elf)],text=True).splitlines():
            words=line.split()
            if len(words)==3:symbols[words[2]]=int(words[0],16)
        save(out/'symbols.json',symbols)
        (out/'disassembly.txt').write_text(subprocess.check_output([prefix+'objdump','-dr',str(elf)],text=True))
        image=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes()
        runtime=out/'build/runtime-original.bin';runtime_bytes=runtime.read_bytes();assert runtime_bytes==image[0xe540:0xe61c]
        candidate=bytearray(image);candidate[0xe540:0xe61c]=runtime_bytes;candidate[BASE:BASE+len(payload)]=payload
        vectors=make_vectors(args.limit);save(out/'fixtures.json',vectors)
        state.update(status='testing',compiled_binary=str(binary),compiled_binary_sha256=sha(binary),binary_bytes=len(payload),symbols=symbols)
        checkpoint()
        rows=[];coverage=set()
        if args.phase in ['cpu','both']:
            host_source=out/'native-oracle.c';host_source.write_text(ORACLE)
            library=out/'libnative-oracle.dylib'
            built=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(host_source),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
            (out/'oracle-compile.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
            oracle=c.CDLL(str(library));oracle.run_cpu.argtypes=[c.c_void_p,c.c_void_p,c.c_uint32,c.c_uint32,c.c_uint32,c.c_uint32,c.c_int,c.c_uint32,c.POINTER(Stats)];oracle.run_cpu.restype=c.c_int
            native=Native();native.device.lib.lab_device_observe(type(native.device.observer)())
            try:
                for index,case in enumerate(vectors):
                    left=initial_image(image,case);right=initial_image(candidate,case)
                    expected,old_ram,old_stats=native_run(native,oracle,left,case['entry'],case,len(payload),True)
                    actual,new_ram,new_stats=native_run(native,oracle,right,symbols[ENTRIES[case['entry']]],case,len(payload),False)
                    assert new_ram[BASE:BASE+len(payload)]==payload,'Candidate modified its resident code/data'
                    differences=[]
                    if normalized(new_ram,old_ram,len(payload))!=old_ram:
                        differences=[hex(i)for i,(a,b)in enumerate(zip(normalized(new_ram,old_ram,len(payload)),old_ram))if a!=b][:32]
                    if actual!=expected or differences:
                        mismatch=dict(case=case,index=index,expected=expected,actual=actual,RAM_differences=differences)
                        save(out/'mismatch.json',mismatch);raise AssertionError(str(out/'mismatch.json'))
                    coverage.update(0x1a6e0+i for i,v in enumerate(old_stats.coverage)if v)
                    rows.append(dict(index=index,entry=hex(case['entry']),SR=case['sr'],CPU=actual,original_steps=old_stats.steps,compiled_steps=new_stats.steps,original_cycles=old_stats.cycles,compiled_cycles=new_stats.cycles,full_CPU_and_nonprivate_RAM_match=True,dynamic_read_queues_applied=False))
                    if index%32==0:
                        state.update(completed_cpu_cases=len(rows));checkpoint();print('CPU',len(rows),'/',len(vectors),flush=True)
            finally:native.close()
            save(out/'CPU-results.json',rows)
            if not args.limit:
                import binary_tools
                decoded,_=binary_tools.m68k_instructions(image[0x1a6e0:0x1a91e],0x1a6e0)
                assert {row['address']for row in decoded}<=coverage
        trace_rows=[]
        if args.phase in ['trace','both']:
            # Include every declared mutable-read fixture, all init/fill/seed
            # fixtures, and regular edges for each other entry.
            selected=[(i,row)for i,row in enumerate(vectors)if row.get('read_queues')or row['entry']in [0x1a6e0,0x1a7f4,0x1a8c6]or i%16==0]
            for index,case in selected:
                old_trace,old_ram,old_steps=trace_run(initial_image(image,case),case['entry'],case,len(payload),True)
                new_trace,new_ram,new_steps=trace_run(initial_image(candidate,case),symbols[ENTRIES[case['entry']]],case,len(payload),False)
                assert new_ram[BASE:BASE+len(payload)]==payload,'Trace candidate modified its resident code/data'
                if old_trace!=new_trace or normalized(new_ram,old_ram,len(payload))!=old_ram:
                    save(out/'trace-mismatch.json',dict(case=case,index=index,original_trace=old_trace,compiled_trace=new_trace))
                    raise AssertionError(str(out/'trace-mismatch.json'))
                trace_rows.append(dict(index=index,entry=hex(case['entry']),accesses=len(old_trace),trace=old_trace,original_steps=old_steps,compiled_steps=new_steps,ordered_nonprivate_accesses_and_RAM_match=True))
                state['completed_trace_cases']=len(trace_rows);checkpoint()
                if len(trace_rows)%16==0:print('trace',len(trace_rows),'/',len(selected),flush=True)
            save(out/'trace-results.json',trace_rows)
        state.update(status='terminal_native_rng_preflight_pass'if args.limit else'terminal_native_rng_nonzero_divisor_components_pass',
            cpu_cases=len(rows),trace_cases=len(trace_rows),original_instruction_locations=len(coverage),
            source_accepted=False,fixed_runtime_binary=str(runtime),fixed_runtime_binary_sha256=sha(runtime),fixed_runtime_bytes_match_original=True,public_runtime_entry_jump_overhead=0,source_sha256={str(p):sha(p)for p in [args.source,
                *[native_source/name for name in ['controller-native.c','controller-lean-shim.S','controller-bundle.ld','Makefile.controller-lean-bundle','rng-native.h','rng-shims.S','rng-fast-math.S','runtime-original.S','runtime-original.ld','fast-rng.ld','Makefile','Makefile.movable','Makefile.math','Makefile.bundle','Makefile.optimized','Makefile.native','Makefile.fast-rng','startup-finalize.S','button-digit-movable-shim.S']],
                native_source.parent/'biwn_inventory_select.c',native_source.parent/'biwn_inventory_select.h',Path(__file__)]},
            execution_dependencies_sha256={str(p):sha(p)for p in [ROOT/'tools/m68k-elf/m68000-soft/libgcc.a',ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib']},
            limits='Component comparison only. Native fullCPU/RAM uses fixed input RAM; separate Unicorn checks inject declared changing reads and compare ordered accesses. Private stacks and newly linked code bytes excluded from RAM identity. Same-address byte-identical math runtime is allowed on candidate. No game clock/IRQ/RNG-zero-divisor/physical console or whole-game proof. Source remains unpromoted pending coordinator review.')
        checkpoint();save(ROOT/'verification/native-heap-bundle-rng-current.json',state);print(state['status'],len(rows),len(trace_rows),len(payload),flush=True)
    except BaseException as error:
        state.update(status='terminal_failed',error=repr(error));checkpoint();raise


if __name__=='__main__':main()
