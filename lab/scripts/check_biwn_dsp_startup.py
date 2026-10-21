"""Compare four translated CPU routines against original M68000/scripted bus."""
import ctypes as c
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import unicorn
import extract_biwn_stage as stage
sys.path.insert(0, str(stage.ROOT))
import binary_tools

SP, STOP = 0x1ff000, 0x1ffe00
READ = c.CFUNCTYPE(c.c_int, c.c_void_p, c.c_uint32, c.POINTER(c.c_uint32))
WRITE = c.CFUNCTYPE(c.c_int, c.c_void_p, c.c_uint32, c.c_uint, c.c_uint32)
class Bus(c.Structure):
    _fields_ = [('read32',READ), ('write',WRITE), ('context',c.c_void_p), ('read_budget',c.c_uint32)]
class State(c.Structure):
    _fields_ = [('d1',c.c_uint32), ('a0',c.c_uint32), ('a1',c.c_uint32)]


class Script:
    def __init__(self, image, length, destination, poll):
        self.main = bytearray(0x200000)
        self.main[0x4000:0x4000+len(image)] = image
        self.main[0x7240:0x7248] = destination.to_bytes(4,'big') + length.to_bytes(4,'big')
        self.high = bytearray(0x100000)
        self.poll = list(poll); self.index = 0; self.trace = []; self.errors = []
        self.fail_read = None; self.fail_write = None
    def region(self,address):
        if 0 <= address < 0x200000: return self.main,address
        if 0xf00000 <= address < 0x1000000: return self.high,address-0xf00000
        raise ValueError('address out of fixture map')
    def read(self,address):
        if address == self.fail_read: raise RuntimeError('injected read error')
        if address == 0xf1badc:
            value = self.poll[self.index]; self.index += 1
            memory,offset = self.region(address); memory[offset:offset+4] = value.to_bytes(4,'big')
        else:
            memory,offset = self.region(address); value = int.from_bytes(memory[offset:offset+4],'big')
        self.trace.append(('r',address,4,value)); return value
    def write(self,address,width,value):
        if address == self.fail_write: raise RuntimeError('injected write error')
        assert width in (2,4)
        memory,offset = self.region(address); memory[offset:offset+width] = value.to_bytes(width,'big')
        self.trace.append(('w',address,width,value))


REGS = [UC_M68K_REG_D0, UC_M68K_REG_D1, UC_M68K_REG_D2, UC_M68K_REG_D3, UC_M68K_REG_D4, UC_M68K_REG_D5, UC_M68K_REG_D6, UC_M68K_REG_D7, UC_M68K_REG_A0, UC_M68K_REG_A1, UC_M68K_REG_A2, UC_M68K_REG_A3, UC_M68K_REG_A4, UC_M68K_REG_A5, UC_M68K_REG_A6]
def original(entry, script, incoming, instruction_budget=300000):
    cpu = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN); cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    cpu.mem_map(0,0x200000); cpu.mem_map(0xf00000,0x100000)
    cpu.mem_write(0,bytes(script.main)); cpu.mem_write(SP,STOP.to_bytes(4,'big')); cpu.reg_write(UC_M68K_REG_A7,SP)
    for reg,value in zip(REGS,incoming): cpu.reg_write(reg,value)
    steps=[]; stack=[]
    def code(engine,address,size,_):
        assert 0xe942 <= address < 0xea16,(hex(address),size)
        steps.append(address)
    def read(engine,access,address,size,value,_):
        if SP-8 <= address < SP+4: return
        assert size == 4,(hex(address),size)
        engine.mem_write(address,script.read(address).to_bytes(4,'big'))
    def write(engine,access,address,size,value,_):
        value &= (1 << (size*8))-1
        if SP-8 <= address < SP:
            assert size == 4; stack.append((address,size,value))
        else: script.write(address,size,value)
    cpu.hook_add(UC_HOOK_CODE,code); cpu.hook_add(UC_HOOK_MEM_READ,read); cpu.hook_add(UC_HOOK_MEM_WRITE,write)
    cpu.emu_start(entry,STOP,count=instruction_budget,timeout=5_000_000)
    returned = cpu.reg_read(UC_M68K_REG_PC) == STOP
    changed = {1,8,9} if entry in (0xe942,0xe96c) else set()
    for i,reg in enumerate(REGS):
        if i not in changed: assert cpu.reg_read(reg) == incoming[i]
    if returned:
        assert cpu.reg_read(UC_M68K_REG_A7) == SP+4
        expected = {0xe942:[(SP-4,4,0xe96a),(SP-8,4,0xe9ea)], 0xe96c:[(SP-4,4,0xe9ea)], 0xe9ec:[(SP-4,4,0xea06)], 0xea08:[]}[entry]
        assert stack == expected,(stack,expected)
    assert bytes(cpu.mem_read(0,SP-8)) == bytes(script.main[:SP-8])
    assert bytes(cpu.mem_read(0xf00000,0x100000)) == bytes(script.high)
    return {'returned':returned,'PC':hex(cpu.reg_read(UC_M68K_REG_PC)), 'instructions':len(steps),
            'state':[cpu.reg_read(UC_M68K_REG_D1),cpu.reg_read(UC_M68K_REG_A0),cpu.reg_read(UC_M68K_REG_A1)],'stack_writes':stack}


def translated(fn, script, incoming, entry, budget=200000, missing_read=False, missing_write=False):
    def read(_,address,out):
        try: out[0]=script.read(address); return 0
        except Exception as error: script.errors.append(repr(error)); return 1
    def write(_,address,width,value):
        try: script.write(address,width,value); return 0
        except Exception as error: script.errors.append(repr(error)); return 1
    reader,writer = READ(read),WRITE(write)
    bus = Bus(READ() if missing_read else reader,WRITE() if missing_write else writer,None,budget)
    state = State(incoming[1],incoming[8],incoming[9])
    result = fn(c.byref(bus),c.byref(state)) if entry in (0xe942,0xe96c) else fn(c.byref(bus))
    return result,bus.read_budget,[state.d1,state.a0,state.a1]


def trace_hash(trace):
    return hashlib.sha256(json.dumps(trace,separators=(',',':')).encode()).hexdigest()


def main():
    root = stage.ROOT
    session = Path(json.loads((root/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    image = (session/'nextstage-68000-candidate.bin').read_bytes(); assert stage.digest(image)==stage.STAGE_SHA
    block = image[0xe942-0x4000:0xea16-0x4000]
    instructions,decoder = binary_tools.m68k_instructions(block,0xe942)
    folder = root/'verification/biwn-dsp-startup'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'); folder.mkdir(parents=True)
    source = root/'projects/black-ice-white-noise/restoration'
    library = folder/'libbiwn_dsp_startup.dylib'
    compiler = ['clang','-dynamiclib','-std=c11','-Wall','-Wextra','-Werror','-O2',str(source/'biwn_dsp_startup.c'),'-o',str(library)]
    subprocess.run(compiler,check=True,capture_output=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    lib = c.CDLL(str(library)); funcs = {}
    for entry,name in [(0xe942,'biwn_dsp_setup'),(0xe96c,'biwn_dsp_load_start'),(0xe9ec,'biwn_dsp_signal_one'),(0xea08,'biwn_dsp_wait_mailbox')]:
        fn=getattr(lib,name); fn.restype=c.c_int; fn.argtypes=[c.POINTER(Bus),c.POINTER(State)] if entry in (0xe942,0xe96c) else [c.POINTER(Bus)]; funcs[entry]=fn
    rng=random.Random(0xe942); rows=[]
    lengths=[0,1,3,4,5,7,8,12,0x1210,0x1213,0x3fffc,0x40000,0x40004,0x80000000,0xffffffff]
    for entry in funcs:
        for length in lengths if entry in (0xe942,0xe96c) else [0x1210]:
            for busy in range(3):
                destination=0xf1b000 if length in (0x1210,0x1213) else 0x100000
                poll=[rng.choice([1,2,0xffffffff,0x80000000,0x12345678]) for _ in range(busy)]+[0]
                incoming=[rng.getrandbits(32) for _ in REGS]
                a=Script(image,length,destination,poll); observed=original(entry,a,incoming)
                assert observed['returned'] and a.index==len(poll)
                b=Script(image,length,destination,poll); status,remaining,state=translated(funcs[entry],b,incoming,entry)
                assert status==0 and not b.errors and b.index==len(poll)
                assert a.trace==b.trace and a.main==b.main and a.high==b.high
                assert observed['state']==state
                row={'entry':hex(entry),'length':hex(length),'destination':hex(destination),'poll':poll,'incoming_registers':incoming,'CPU':observed,
                     'trace_count':len(a.trace),'trace_sha256':trace_hash(a.trace),'trace_first24':a.trace[:24],'trace_last24':a.trace[-24:],'remaining_host_budget':remaining}
                if length==0x1210 and busy==0:
                    (folder/(hex(entry)+'-full-trace.json')).write_text(json.dumps(a.trace)+'\n')
                rows.append(row)
    guards=[]
    for entry,fn in funcs.items():
        assert (fn(None,None) if entry in (0xe942,0xe96c) else fn(None))==1
        guards.append({'case':'null_bus','entry':hex(entry),'status':1})
        if entry in (0xe942,0xe96c):
            dummy=Bus();assert fn(c.byref(dummy),None)==1
            guards.append({'case':'null_state','entry':hex(entry),'status':1})
    for name,entry,budget,fail_r,fail_w in [
        ('missing_read',0xea08,1,None,None),('missing_write',0xe9ec,1,None,None),
        ('zero_budget',0xea08,0,None,None),('table_budget',0xe96c,1,None,None),
        ('payload_budget',0xe96c,3,None,None),('mailbox_budget',0xe9ec,1,None,None),
        ('table_failure',0xe96c,200000,0x7244,None),('payload_failure',0xe96c,200000,0x7250,None),
        ('payload_write_failure',0xe96c,200000,None,0xf1b004),('setup_write_failure',0xe942,200000,None,0xf10002),
        ('mailbox_read_failure',0xe9ec,200000,0xf1badc,None),('control_write_failure',0xe9ec,200000,None,0xf1a114)]:
        a=Script(image,0x1210,0xf1b000,[1,0]);a.fail_read=fail_r;a.fail_write=fail_w
        result,remaining,state=translated(funcs[entry],a,[0]*15,entry,budget,name=='missing_read',name=='missing_write')
        expected=1 if name.startswith('missing') else 3 if 'failure' in name else 2
        assert result==expected,(name,result,expected)
        guards.append({'case':name,'entry':hex(entry),'status':result,'remaining_budget':remaining,'trace':a.trace,'callback_errors':a.errors})
    a=Script(image,0x1210,0xf1b000,[1]*64); observed=original(0xea08,a,[0]*15,instruction_budget=32)
    b=Script(image,0x1210,0xf1b000,[1]*64); result,_,_=translated(funcs[0xea08],b,[0]*15,0xea08,budget=16)
    assert not observed['returned'] and observed['PC']=='0xea08' and result==2 and a.trace==b.trace
    guards.append({'case':'bounded_nonclearing_mailbox','CPU':observed,'host_status':result,'reads':16,'scope':'Observation budget only; original remains in loop. Added host guard is not original timeout.'})
    (folder/'fixtures.json').write_text(json.dumps(rows,indent=2)+'\n');(folder/'guards.json').write_text(json.dumps(guards,indent=2)+'\n')
    (folder/'original-decode.json').write_text(json.dumps({'instructions':instructions,'decoder':decoder,'bytes_hex':block.hex()},indent=2)+'\n')
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'CPU_protocol_and_portable_C_match_scripted_bus', 'directory':str(folder),
            'stage_sha256':stage.STAGE_SHA,'original_interval':'[0xe942,0xea16)','original_bytes':len(block),'original_bytes_sha256':hashlib.sha256(block).hexdigest(),
            'portable_components':4,'completed_CPU_cases':len(rows),'host_guard_cases':len(guards),'CPU_model':'Unicorn'+unicorn.__version__+' M68000',
            'entry_cases':{hex(e):sum(x['entry']==hex(e) for x in rows) for e in funcs},
            'actual_payload':{'destination':'0xf1b000','length':0x1210,'longword_copies':0x1210//4,'source_start':'0x7248','source_end':'0x8458'},
            'matched':['All CPU-visible logical read/write addresses, widths, values and ordering, including source/table reads.','Full fixture RAM/MMIO memory and completed D1/A0/A1. Other D/A registers unchanged; RTS/private-stack balance.','Zero/short, nonmultiple-of-four,65536loop,16bit DBRA wrap and signed-ASR lengths. Mailbox waits for exactly zero.'],
            'excluded':['DSP execution, actual scheduling, physical16bit bus splitting, interrupts, sound quality or command-purpose validation.','CCR, full-game integration, code/source/destination overlap cases not represented by fixtures.','Host read budget/callback failure handling is additional behavior; partial writes retained; error-state registers are not CPU exception equivalence.'],
            'compiler':compiler,'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest() for n in ['biwn_dsp_startup.c','biwn_dsp_startup.h']}}
    (folder/'report.json').write_text(json.dumps(report,indent=2)+'\n');(root/'verification/biwn-dsp-startup-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)


if __name__=='__main__':main()
