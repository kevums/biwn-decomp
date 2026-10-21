"""Complete original elevator-input body vs local readable C, explicit helpers."""
import argparse
import ctypes as c
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_game_controls as controls

ROOT=controls.ROOT;SP=controls.SP;STOP=controls.STOP;world=controls.world
HELPERS={0x20f0c:[],0x20f78:[2]}
sha=lambda raw:hashlib.sha256(raw).hexdigest()
save=lambda path,value:path.write_text(json.dumps(value,indent=2)+'\n')


class Script(controls.dispatch.boundary.Script):
    def call(self,address,args):
        if self.fail_call==address:raise RuntimeError('injected dependency error')
        assert address in HELPERS
        self.trace.append(['call',address,args])
        for target,a,w,v in self.case.get('helper_effects',[]):
            if target==address:self.put(a,w,v)
        return self.case['helper_returns'][str(address)]


def original(script,case,coverage):
    cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(script.memory));cpu.mem_write(SP,STOP.to_bytes(4,'big'))
    for reg,value in zip(world.REGS,case['incoming']):cpu.reg_write(reg,value)
    cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP)
    for address in HELPERS:cpu.mem_write(address,b'\x4e\x75')
    def code(e,address,width,_):
        if address in HELPERS:
            offset=4;args=[];stack=e.reg_read(UC_M68K_REG_A7)
            for size in HELPERS[address]:args.append(int.from_bytes(e.mem_read(stack+offset,size),'big'));offset+=size
            script.changed=[];value=script.call(address,args)
            for a,w,v in script.changed:e.mem_write(a,v.to_bytes(w,'big'))
            e.reg_write(UC_M68K_REG_D0,value);return
        assert 0x1a0f8<=address<0x1a188,hex(address);coverage.add(address)
    def read(e,access,address,width,value,_):
        if SP-0x1000<=address<SP+8:return
        e.mem_write(address,script.read(address,width).to_bytes(width,'big'))
    def write(e,access,address,width,value,_):
        if SP-0x1000<=address<SP+8:return
        script.write(address,width,value&((1<<(width*8))-1))
    cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write)
    cpu.emu_start(0x1a0f8,STOP,count=2000,timeout=1000000)
    assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
    assert all(cpu.reg_read(reg)==case['incoming'][i]for i,reg in enumerate(world.REGS)if i not in[0,1,8,9])
    memory=bytearray(cpu.mem_read(0,0x200000))
    for address in HELPERS:memory[address:address+2]=script.memory[address:address+2]
    assert memory[:SP-0x1000]==script.memory[:SP-0x1000]and memory[SP+8:]==script.memory[SP+8:]
    return cpu.reg_read(UC_M68K_REG_D0)


def translated(fn,script,case,missing=None):
    def reader(width):
        def cb(_,a,v):
            try:v[0]=script.read(a,width);return 0
            except Exception as error:script.errors.append(str(error));return 1
        return cb
    def writer(_,a,v):
        try:script.write(a,2,v);return 0
        except Exception as error:script.errors.append(str(error));return 1
    def call(_,a,args,n,result):
        try:result[0]=script.call(a,list(args[:n]));return 0
        except Exception as error:script.errors.append(str(error));return 1
    callbacks=[world.R8(reader(1)),world.R16(reader(2)),world.R32(reader(4)),world.W16(writer),world.CALL(call)]
    if missing is not None:callbacks[missing]=type(callbacks[missing])()
    bus=world.Bus(*callbacks[:4],world.W32(),callbacks[4],None,0);output=c.c_uint32(0xa5a55a5a)
    status=fn(c.byref(bus),case['incoming'][0],c.byref(output));return status,output.value


def fixtures():
    rng=random.Random(0x1a0f8);rows=[]
    for mode in[0,1,2,3,0xffff]:
        for sign in[0,1,0x7fff,0x8000,0xffff]:
            for held in[0,0x10,0x20,0x30,0xff]:
                for permissions in[0,0x8000,0x40,0x4000,0x8040,0xffff]:
                    initial=[[0x49c60,2,mode],[0x49c78,4,0x90100],[0x90100,2,sign],
                             [0x49ba5,1,held],[0x49c18,4,0x90200],[0x9020c,2,permissions],
                             [0x49c62,2,rng.choice([0,1,0x7fff,0x8000,0xffff])],[0x49c64,2,rng.choice([0,1,0x7fff,0x8000,0xffff])]]
                    effects=[[0x20f0c,0x49c62,2,rng.choice([0,0x7fff,0x8000,0xffff])],[0x20f0c,0x49c64,2,rng.choice([0,0x7fff,0x8000,0xffff])],[0x20f78,0x90220,4,rng.getrandbits(32)]]
                    rows.append(dict(mode=mode,sign=sign,held=held,permissions=permissions,initial=initial,helper_effects=effects,helper_returns={str(a):rng.getrandbits(32)for a in HELPERS},incoming=[rng.getrandbits(32)for _ in world.REGS]))
    return rows


def native(runtime,snapshot,case,expected,expected_memory):
    script=Script(snapshot,case);memory=bytearray(script.memory)
    for address in HELPERS:memory[address:address+2]=b'\x4e\x75'
    memory[SP:SP+4]=STOP.to_bytes(4,'big');cpu=controls.media.CPU();cpu.registers[:15]=case['incoming'];cpu.registers[15]=SP;cpu.pc=0x1a0f8;cpu.sr=0x2000;cpu.ssp=SP;cpu.usp=0x180000
    runtime.device.seed(bytes(memory),0);runtime.seed_cpu(cpu);steps=0
    while runtime.cpu().pc!=STOP and steps<2000:
        cpu=runtime.cpu();address=cpu.pc
        if address in HELPERS:
            args=[];offset=4;stack=cpu.registers[15]
            for width in HELPERS[address]:args.append(getattr(runtime.core,'m68k_read_memory_'+str(width*8))(stack+offset));offset+=width
            script.changed=[];value=script.call(address,args)
            for a,w,v in script.changed:runtime.device.direct(a,w,v)
            runtime.core.m68k_set_reg(0,value)
        runtime.core.m68k_execute(1);steps+=1
    cpu=runtime.cpu();memory=bytearray(runtime.device.ram())
    for address in HELPERS:memory[address:address+2]=expected_memory[address:address+2]
    assert cpu.pc==STOP and cpu.registers[0]==expected and cpu.registers[15]==SP+4
    assert memory[:SP-0x1000]==expected_memory[:SP-0x1000]and memory[SP+8:]==expected_memory[SP+8:]
    return dict(mode=case['mode'],held=case['held'],permissions=case['permissions'],D0=expected,instructions=steps)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--candidate',type=Path,required=True);args=parser.parse_args()
    out=ROOT/'verification/elevator-input'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    source=args.candidate.resolve();restore=ROOT/'projects/black-ice-white-noise/restoration'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(restore),str(source),'-o',str(out/'libelevator.dylib')]
    built=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(built.stdout+built.stderr)
    if built.returncode:save(out/'report.json',dict(status='candidate_compile_rejected',candidate=str(source)));raise SystemExit(1)
    fn=c.CDLL(str(out/'libelevator.dylib')).biwn_elevator_input;fn.argtypes=[c.POINTER(world.Bus),c.c_uint32,c.POINTER(c.c_uint32)];fn.restype=c.c_int
    snapshot=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();coverage=set();results=[];natives=[];seen=set()
    for i,case in enumerate(fixtures()):
        left=Script(snapshot,case);right=Script(snapshot,case);expected=original(left,case,coverage);status,value=translated(fn,right,case)
        if status or expected!=value or left.trace!=right.trace or left.memory!=right.memory:
            save(out/'mismatch.json',dict(case=i,parameters=case,status=status,expected=expected,actual=value,original_trace=left.trace,C_trace=right.trace,errors=right.errors));save(out/'report.json',dict(status='candidate_rejected',candidate=str(source),matched_cases=len(results)));raise SystemExit(1)
        results.append(dict(case=i,D0=value,trace_sha256=sha(json.dumps(left.trace).encode()),RAM_sha256=sha(left.memory)))
        tag=(case['mode'],bool(case['sign']&0x8000),case['held'],case['permissions'])
        if case['mode']==2 and tag not in seen:seen.add(tag);natives.append((case,value,bytes(right.memory)))
    decoded,_=world.select.binary_tools.m68k_instructions(snapshot[0x1a0f8:0x1a188],0x1a0f8);assert all(x['address']in coverage for x in decoded)
    guards=[];case=next(x for x in fixtures()if x['mode']==2 and x['sign']==0xffff and x['held']==0x10 and x['permissions']==0x8000)
    output=c.c_uint32(0xa5a55a5a);assert fn(None,0,c.byref(output))==1 and output.value==0xa5a55a5a
    empty=world.Bus();assert fn(c.byref(empty),0,None)==1
    guards.extend([dict(null_bus=True),dict(null_output=True)])
    for missing in range(5):
        script=Script(snapshot,case);status,value=translated(fn,script,case,missing);assert status==1 and value==0xa5a55a5a and not script.trace;guards.append(dict(missing_callback=missing))
    baseline=Script(snapshot,case);original(baseline,case,set())
    for field,event in [('fail_read',['r',0x49c60,2]),('fail_write',['w',0x49c62,2]),('fail_call',['call',0x20f0c]),('fail_call',['call',0x20f78])]:
        script=Script(snapshot,case);setattr(script,field,tuple(event[1:])if field!='fail_call'else event[1]);status,value=translated(fn,script,case)
        index=next(i for i,row in enumerate(baseline.trace)if row[:len(event)]==event)
        assert status==(3 if field=='fail_call'else 2)and value==0xa5a55a5a and script.trace==baseline.trace[:index];guards.append(dict(failure=event,prior_effects_retained=True,output_untouched=True))
    core=Path(json.loads((ROOT/'verification/DSP-music-context-experimental-candidate.json').read_text())['core_path']);oracle=controls.media.scheduler.Native(diagnostic_core=core);runtime=controls.media.Runtime.__new__(controls.media.Runtime);runtime.oracle,runtime.device,runtime.core=oracle,oracle.device,oracle.lib
    for width in[16,32]:reader=getattr(runtime.core,'m68k_read_memory_'+str(width));reader.argtypes=[c.c_uint32];reader.restype=c.c_uint32
    try:native_results=[native(runtime,snapshot,*row)for row in natives]
    finally:oracle.close()
    save(out/'results.json',results);save(out/'native.json',native_results);save(out/'guards.json',guards)
    report=dict(status='complete_elevator_input_original_C_and_native_match',directory=str(out),candidate=str(source),source_sha256=sha(source.read_bytes()),header_sha256=sha((restore/'biwn_elevator_input.h').read_bytes()),cases=len(results),instruction_address_coverage=[len(coverage),len(decoded)],native_cases=len(native_results),guards=len(guards),nested_helpers=[hex(a)for a in HELPERS],default_runtime_promoted=False,new_training=False,scope='Complete34instruction source1A0F8..1A188. FullD0, ordered public bus read/write/calls and full2MBRAM excluding private stack match original. Modes, signed entrance gate, asymmetric up-word/down-byte permissions, button priority, wrapping counters after helper effects and partialD0 writes. Scene exit20F0C/setup20F78 are scripted on both original/native and C sides. Other registers/CCR, asynchronous timing and natural gameplay integration excluded.',verifier_sha256=sha(Path(__file__).read_bytes()),core_sha256=sha(core.read_bytes()))
    save(out/'report.json',report);save(ROOT/'verification/elevator-input-current.json',report);print(json.dumps(report),flush=True)


if __name__=='__main__':main()
