"""Full elevator label/floor caller versus original CPU; formatter/refresh explicit."""
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

ROOT=controls.ROOT;world=controls.world;SP=controls.SP;STOP=controls.STOP;SCRATCH=SP-14
HELPERS={0x1b45a:[4,4,2],0x12620:[2]}
sha=lambda raw:hashlib.sha256(raw).hexdigest()
save=lambda path,value:path.write_text(json.dumps(value,indent=2)+'\n')


class Script(controls.dispatch.boundary.Script):
    def read(self,a,w):
        if self.fail_read==(a,w):raise RuntimeError('injected read error')
        if SP-0x1000<=a<SP+8:return int.from_bytes(self.memory[a:a+w],'big')
        return super().read(a,w)
    def write(self,a,w,v):
        if self.fail_write==(a,w):raise RuntimeError('injected write error')
        if SP-0x1000<=a<SP+8:self.put(a,w,v);return
        return super().write(a,w,v)
    def call(self,address,args):
        if self.fail_call==address:raise RuntimeError('injected dependency error')
        assert address in HELPERS;self.trace.append(['call',address,args])
        if address==0x1b45a:
            destination,fmt,word=args;assert destination==SCRATCH and fmt==0x190b8
            signed=(word&0x7fff)-(word&0x8000)
            text=self.case.get('formatted_override',str(signed)).encode()+b'\0'
            for i,byte in enumerate(text):self.put(destination+i,1,byte)
        else:
            assert args==[4];self.put(0x92300,4,0x12345678)
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
        assert 0x190bc<=address<0x191f4,hex(address);coverage.add(address)
    def read(e,access,a,w,value,_):
        if SP-0x1000<=a<SP+8:return
        e.mem_write(a,script.read(a,w).to_bytes(w,'big'))
    def write(e,access,a,w,v,_):
        if SP-0x1000<=a<SP+8:return
        script.write(a,w,v&((1<<(w*8))-1))
    cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write)
    cpu.emu_start(0x190bc,STOP,count=3000,timeout=1000000)
    assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
    assert all(cpu.reg_read(reg)==case['incoming'][i]for i,reg in enumerate(world.REGS)if i not in[0,1,8,9])
    memory=bytearray(cpu.mem_read(0,0x200000))
    for address in HELPERS:memory[address:address+2]=script.memory[address:address+2]
    assert memory[:SP-0x1000]==script.memory[:SP-0x1000]and memory[SP+8:]==script.memory[SP+8:]
    return cpu.reg_read(UC_M68K_REG_D0)


def translated(fn,script,case,budget=64,missing=None,scratch=SCRATCH,null_bus=False,null_out=False):
    def reader(width):
        def cb(_,a,v):
            try:v[0]=script.read(a,width);return 0
            except Exception as error:script.errors.append(str(error));return 1
        return cb
    def writer(_,a,v):
        try:script.write(a,1,v);return 0
        except Exception as error:script.errors.append(str(error));return 1
    def call(_,a,args,n,result):
        try:result[0]=script.call(a,list(args[:n]));return 0
        except Exception as error:script.errors.append(str(error));return 1
    callbacks=[world.R8(reader(1)),world.R16(reader(2)),world.R32(reader(4)),world.CALL(call),controls.dispatch.W8(writer)]
    if missing is not None:callbacks[missing]=type(callbacks[missing])()
    bus=world.Bus(*callbacks[:3],world.W16(),world.W32(),callbacks[3],None,0);out=c.c_uint32(0xa5a55a5a)
    status=fn(None if null_bus else c.byref(bus),callbacks[4],scratch,budget,case['incoming'][0],None if null_out else c.byref(out))
    return status,out.value


def fixtures():
    rng=random.Random(0x190bc);rows=[]
    for permissions in[0,0x40,0x4000,0x8000,0xc000,0xffff]:
        for floor in[0,1,9,99,999,9999,0x7fff,0x8000,0xff9c,0xfff6,0xffff]:
            for upper in[0,1,0x8000,0xffff]:
                rows.append(dict(permissions=permissions,floor=floor,kind='matrix',initial=[[0x49c18,4,0x91000],[0x9100c,2,permissions],[0x49c62,2,floor],[0x410ba,4,0x92000],[0x410b2,4,0x92100],[0x410b6,4,0x92200]],helper_returns={str(0x1b45a):(upper<<16)|6,str(0x12620):rng.getrandbits(32)},incoming=[rng.getrandbits(32)for _ in world.REGS]))
    for address,width,values in [(0x410ba,4,[0x92000,0x92010,0x92020,0x92030]),(0x410b2,4,[0x92100,0x92110]),(0x410b6,4,[0x92200,0x92210,0x92220,0x92230,0x92240])]:
        row=json.loads(json.dumps(rows[-1]));row['kind']='pointer_reread';row['read_queues']=[dict(address=address,width=width,values=values)];rows.append(row)
    row=json.loads(json.dumps(rows[0]));row['kind']='empty_formatter';row['formatted_override']='';rows.append(row)
    return rows


def native(runtime,snapshot,case,expected,expected_memory):
    script=Script(snapshot,case);memory=bytearray(script.memory)
    for address in HELPERS:memory[address:address+2]=b'\x4e\x75'
    memory[SP:SP+4]=STOP.to_bytes(4,'big');cpu=controls.media.CPU();cpu.registers[:15]=case['incoming'];cpu.registers[15]=SP;cpu.pc=0x190bc;cpu.sr=0x2000;cpu.ssp=SP;cpu.usp=0x180000
    runtime.device.seed(bytes(memory),0);runtime.seed_cpu(cpu);steps=0
    while runtime.cpu().pc!=STOP and steps<3000:
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
    return dict(floor=case['floor'],permissions=case['permissions'],D0=expected,instructions=steps)


def main():
    out=ROOT/'verification/elevator-display'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    restore=ROOT/'projects/black-ice-white-noise/restoration';source=restore/'biwn_elevator_display.c'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(out/'libdisplay.dylib')]
    built=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(built.stdout+built.stderr);assert not built.returncode,built.stderr
    fn=c.CDLL(str(out/'libdisplay.dylib')).biwn_elevator_display;fn.argtypes=[c.POINTER(world.Bus),controls.dispatch.W8,c.c_uint32,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];fn.restype=c.c_int
    snapshot=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();coverage=set();results=[];natives=[]
    for i,case in enumerate(fixtures()):
        left=Script(snapshot,case);right=Script(snapshot,case);expected=original(left,case,coverage);status,value=translated(fn,right,case)
        # Only the mapped private buffer/save frame is excluded from memory.
        memory_match=left.memory[:SP-0x1000]==right.memory[:SP-0x1000]and left.memory[SP+8:]==right.memory[SP+8:]
        if status or value!=expected or left.trace!=right.trace or not memory_match:
            save(out/'mismatch.json',dict(case=i,parameters=case,status=status,expected=expected,actual=value,original_trace=left.trace,C_trace=right.trace,errors=right.errors));raise AssertionError(str(out/'mismatch.json'))
        results.append(dict(case=i,D0=value,trace_sha256=sha(json.dumps(left.trace).encode())))
        if case['kind']=='matrix'and i%4==0:natives.append((case,value,bytes(right.memory)))
    decoded,_=world.select.binary_tools.m68k_instructions(snapshot[0x190bc:0x191f4],0x190bc);assert all(x['address']in coverage for x in decoded)
    guards=[];case=fixtures()[-2]
    for missing in range(5):
        script=Script(snapshot,case);status,value=translated(fn,script,case,missing=missing);assert status==1 and value==0xa5a55a5a and not script.trace;guards.append(dict(missing_callback=missing))
    for kwargs in[dict(null_bus=True),dict(null_out=True),dict(budget=0),dict(scratch=0)]:
        script=Script(snapshot,case);status,value=translated(fn,script,case,**kwargs);assert status==1 and value==0xa5a55a5a and not script.trace;guards.append(kwargs)
    case=fixtures()[0];baseline=Script(snapshot,case);original(baseline,case,set())
    for field,event in [('fail_read',['r',0x49c18,4]),('fail_write',['w',0x92000,1]),('fail_call',['call',0x1b45a]),('fail_call',['call',0x12620])]:
        script=Script(snapshot,case);setattr(script,field,event[1]if field=='fail_call'else tuple(event[1:]));status,value=translated(fn,script,case)
        index=next(i for i,row in enumerate(baseline.trace)if row[:len(event)]==event)
        assert status==(3 if field=='fail_call'else 2)and value==0xa5a55a5a and script.trace==baseline.trace[:index];guards.append(dict(failure=event,prior_effects_retained=True,output_untouched=True))
    case=next(row for row in fixtures()if row['floor']==0x8000);script=Script(snapshot,case);status,value=translated(fn,script,case,budget=1)
    assert status==4 and value==0xa5a55a5a and any(event[0]=='w'for event in script.trace);guards.append(dict(copy_limit=True,prior_effects_retained=True,output_untouched=True))
    core=Path(json.loads((ROOT/'verification/DSP-music-context-experimental-candidate.json').read_text())['core_path']);oracle=controls.media.scheduler.Native(diagnostic_core=core);runtime=controls.media.Runtime.__new__(controls.media.Runtime);runtime.oracle,runtime.device,runtime.core=oracle,oracle.device,oracle.lib
    for width in[16,32]:reader=getattr(runtime.core,'m68k_read_memory_'+str(width));reader.argtypes=[c.c_uint32];reader.restype=c.c_uint32
    try:native_rows=[native(runtime,snapshot,*row)for row in natives]
    finally:oracle.close()
    save(out/'results.json',results);save(out/'native.json',native_rows);save(out/'guards.json',guards)
    report=dict(status='elevator_display_original_C_native_match',directory=str(out),cases=len(results),instruction_address_coverage=[len(coverage),len(decoded)],native_cases=len(native_rows),guards=len(guards),source_sha256={name:sha((restore/name).read_bytes())for name in ['biwn_elevator_display.c','biwn_elevator_display.h']},verifier_sha256=sha(Path(__file__).read_bytes()),nested_scripted_helpers=[hex(a)for a in HELPERS],scratch=str(hex(SCRATCH)),new_training=False,default_runtime_promoted=False,authorship='Coordinator reconstruction from original68instructions; no local-model source generation.',scope='Complete190BC..191F4 caller, fullD0, ordered public RAM reads/writes/logical calls and public2MBRAM match original. Formatter1B45A and refresh12620 are identical explicit fixtures in original/native/C; actual formatting internals, rasterization, private mapped buffer/stack effects, CCR and other registers, natural gameplay and frame-runtime integration excluded. Covers independent UP/DOWN permissions, pointer rereads, signedfloor+one wrapping, basement B prefix, long output beyond four cleared cells, empty output and callback/budget errors.')
    save(out/'report.json',report);save(ROOT/'verification/elevator-display-current.json',report);print(json.dumps(report),flush=True)


if __name__=='__main__':main()
