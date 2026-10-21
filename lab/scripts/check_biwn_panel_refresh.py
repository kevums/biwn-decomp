"""Panel command order vs original instructions and native blitter framebuffer."""
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

ROOT=controls.ROOT;world=controls.world;SP=controls.SP;STOP=controls.STOP
WIDTHS=[2,2,4,4,4,4,2,2]
sha=lambda raw:hashlib.sha256(raw).hexdigest()
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')


class Script(controls.dispatch.boundary.Script):
    def __init__(self,snapshot,case):self.MMIO={};self.calls=0;super().__init__(snapshot,case)
    def put(self,a,w,v):
        if a>=0x200000:
            assert 0xf02000<=a<0xf03000;self.MMIO[(a,w)]=v;self.changed.append((a,w,v));return
        return super().put(a,w,v)
    def read(self,a,w):
        if a>=0x200000:
            assert 0xf02000<=a<0xf03000
            if self.fail_read==(a,w):raise RuntimeError('injected read failure')
            v=self.MMIO.get((a,w),0);self.trace.append(['r',a,w,v]);return v
        return super().read(a,w)
    def call(self,address,args):
        if self.fail_call==address:raise RuntimeError('injected text failure')
        assert address==0x149ae and len(args)==8;self.trace.append(['call',address,args]);n=self.calls;self.calls+=1
        self.put(0x93000+n*4,4,0x12340000+n)
        return self.case['helper_returns'][min(n,len(self.case['helper_returns'])-1)]


def original(script,case,coverage):
    cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    cpu.mem_map(0,0x200000);cpu.mem_map(0xf02000,0x1000);cpu.mem_write(0,bytes(script.memory));cpu.mem_write(SP,STOP.to_bytes(4,'big')+case['id'].to_bytes(2,'big'));cpu.mem_write(0x149ae,b'\x4e\x75')
    for reg,value in zip(world.REGS,case['incoming']):cpu.reg_write(reg,value)
    cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP)
    def code(e,a,width,_):
        if a==0x149ae:
            offset=4;args=[];stack=e.reg_read(UC_M68K_REG_A7)
            for w in WIDTHS:args.append(int.from_bytes(e.mem_read(stack+offset,w),'big'));offset+=w
            script.changed=[];value=script.call(a,args)
            for target,w,v in script.changed:e.mem_write(target,v.to_bytes(w,'big'))
            e.reg_write(UC_M68K_REG_D0,value);return
        assert 0x12620<=a<0x12896,hex(a);coverage.add(a)
    def read(e,t,a,w,v,_):
        if SP-0x1000<=a<SP+8:return
        e.mem_write(a,script.read(a,w).to_bytes(w,'big'))
    def write(e,t,a,w,v,_):
        if SP-0x1000<=a<SP+8:return
        script.write(a,w,v&((1<<(w*8))-1))
    cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(0x12620,STOP,count=10000,timeout=1000000)
    assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
    assert all(cpu.reg_read(reg)==case['incoming'][i]for i,reg in enumerate(world.REGS)if i not in[0,1,8,9])
    return cpu.reg_read(UC_M68K_REG_D0)


def translated(fn,script,case,budget=1024,missing=None):
    def reader(w):
        def cb(_,a,v):
            try:v[0]=script.read(a,w);return 0
            except Exception as error:script.errors.append(str(error));return 1
        return cb
    def writer(_,a,v):
        try:script.write(a,4,v);return 0
        except Exception as error:script.errors.append(str(error));return 1
    def call(_,a,args,n,result):
        try:result[0]=script.call(a,list(args[:n]));return 0
        except Exception as error:script.errors.append(str(error));return 1
    callbacks=[world.R8(reader(1)),world.R16(reader(2)),world.R32(reader(4)),world.W32(writer),world.CALL(call)]
    if missing is not None:callbacks[missing]=type(callbacks[missing])()
    bus=world.Bus(*callbacks[:3],world.W16(),callbacks[3],callbacks[4],None,0);out=c.c_uint32(0xa5a55a5a)
    status=fn(c.byref(bus),case['id'],budget,c.byref(out));return status,out.value


def fixtures():
    rng=random.Random(0x12620);rows=[]
    for id in[0,4,0xffff]:
        for border in[0,1,2,4]:
            for geometry in[(20,10,40,20),(0,0,1,1),(0x7fff,0x8000,0x8000,0xffff),(0xffff,0xffff,0xffff,0x8000)]:
                for segments in[1,2]:
                    record=(0x410be+(id if id<32768 else id-65536)*14)&0xffffffff;x,y,width,height=geometry
                    initial=[[record+i*2,2,v]for i,v in enumerate([x,y,width,height,border])]+[[record+10,4,0x90000],[0xbd830,4,0x100000]]
                    data=b'\x01\x02AB\0\x03\x04C\0\0'if segments==2 else b'\x01\x02AB\0\0'
                    initial += [[0x90000+i,1,v]for i,v in enumerate(data)]
                    rows.append(dict(id=id,border=border,geometry=geometry,segments=segments,initial=initial,incoming=[rng.getrandbits(32)for _ in world.REGS],helper_returns=[rng.getrandbits(32),rng.getrandbits(32)]))
    return rows


def native_blitter(runtime,fn,snapshot,case):
    def seed():
        script=Script(snapshot,case);ram=bytearray(script.memory);ram[0x149ae:0x149b0]=b'\x4e\x75';ram[SP:SP+6]=STOP.to_bytes(4,'big')+case['id'].to_bytes(2,'big')
        runtime.device.seed(bytes(ram),0);return script,bytes(ram)
    script,before=seed();cpu=controls.media.CPU();cpu.registers[:15]=case['incoming'];cpu.registers[15]=SP;cpu.pc=0x12620;cpu.sr=0x2000;cpu.ssp=SP;cpu.usp=0x180000;runtime.seed_cpu(cpu);steps=0
    while runtime.cpu().pc!=STOP and steps<10000:
        state=runtime.cpu()
        if state.pc==0x149ae:
            args=[];offset=4
            for w in WIDTHS:args.append(getattr(runtime.core,'m68k_read_memory_'+str(w*8))(state.registers[15]+offset));offset+=w
            script.changed=[];value=script.call(0x149ae,args)
            for a,w,v in script.changed:runtime.device.direct(a,w,v)
            runtime.core.m68k_set_reg(0,value)
        runtime.core.m68k_execute(1);steps+=1
    state=runtime.cpu();assert state.pc==STOP and state.registers[15]==SP+4
    expected=runtime.device.ram();expected_D0=state.registers[0];expected_calls=list(script.trace)
    script,_=seed();errors=[]
    def reader(w):
        def cb(_,a,v):v[0]=getattr(runtime.core,'m68k_read_memory_'+str(w*8))(a);return 0
        return cb
    def writer(_,a,v):runtime.core.m68k_write_memory_32(a,v);return 0
    def call(_,a,args,n,result):
        try:
            script.changed=[];result[0]=script.call(a,list(args[:n]))
            for target,w,v in script.changed:runtime.device.direct(target,w,v)
            return 0
        except Exception as error:errors.append(str(error));return 1
    callbacks=[world.R8(reader(1)),world.R16(reader(2)),world.R32(reader(4)),world.W32(writer),world.CALL(call)]
    bus=world.Bus(*callbacks[:3],world.W16(),callbacks[3],callbacks[4],None,0);out=c.c_uint32();status=fn(c.byref(bus),case['id'],1024,c.byref(out));actual=runtime.device.ram()
    matches=actual[:SP-0x1000]==expected[:SP-0x1000]and actual[SP+8:]==expected[SP+8:]
    assert status==0 and not errors and out.value==expected_D0 and matches and script.trace==expected_calls,dict(status=status,errors=errors,D0=out.value,expected_D0=expected_D0,RAM_match=matches)
    region=slice(0x100000,0x100000+224*240*2);changed=sum(a!=b for a,b in zip(before[region],actual[region]))
    assert changed>0
    return dict(id=case['id'],border=case['border'],segments=case['segments'],native_instructions=steps,changed_framebuffer_bytes=changed,framebuffer_sha256=sha(actual[region]),public_RAM_sha256=sha(actual[:SP-0x1000]+actual[SP+8:]))


def main():
    out=ROOT/'verification/panel-refresh'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    restore=ROOT/'projects/black-ice-white-noise/restoration';p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(restore/'biwn_panel_refresh.c'),'-o',str(out/'libpanel.dylib')],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(p.stdout+p.stderr);assert not p.returncode,p.stderr
    fn=c.CDLL(str(out/'libpanel.dylib')).biwn_panel_refresh;fn.argtypes=[c.POINTER(world.Bus),c.c_uint16,c.c_uint32,c.POINTER(c.c_uint32)];fn.restype=c.c_int
    snapshot=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();coverage=set();results=[]
    for i,case in enumerate(fixtures()):
        left=Script(snapshot,case);right=Script(snapshot,case);expected=original(left,case,coverage);status,value=translated(fn,right,case)
        if status or value!=expected or left.trace!=right.trace or left.memory!=right.memory or left.MMIO!=right.MMIO:
            save(out/'mismatch.json',dict(case=i,parameters=case,status=status,expected=expected,actual=value,original_trace=left.trace,C_trace=right.trace,errors=right.errors));raise AssertionError(str(out/'mismatch.json'))
        results.append(dict(case=i,trace_sha256=sha(json.dumps(left.trace).encode())))
    decoded,_=world.select.binary_tools.m68k_instructions(snapshot[0x12620:0x12896],0x12620);assert all(x['address']in coverage for x in decoded)
    case=fixtures()[0];guards=[]
    for missing in range(5):
        script=Script(snapshot,case);status,value=translated(fn,script,case,missing=missing);assert status==1 and value==0xa5a55a5a and not script.trace;guards.append(dict(missing_callback=missing))
    script=Script(snapshot,case);status,value=translated(fn,script,case,budget=0);assert status==1 and value==0xa5a55a5a and not script.trace;guards.append(dict(zero_budget=True))
    baseline=Script(snapshot,case);original(baseline,case,set())
    for field,event in [('fail_read',['r',0xbd830,4]),('fail_write',['w',0xf02238,4]),('fail_call',['call',0x149ae])]:
        script=Script(snapshot,case);setattr(script,field,event[1]if field=='fail_call'else tuple(event[1:]));status,value=translated(fn,script,case)
        index=next(i for i,row in enumerate(baseline.trace)if row[:len(event)]==event);assert status==(3 if field=='fail_call'else 2)and value==0xa5a55a5a and script.trace==baseline.trace[:index];guards.append(dict(failure=event,prior_effects_retained=True,output_untouched=True))
    case=next(row for row in fixtures()if row['border']==4);script=Script(snapshot,case);status,value=translated(fn,script,case,budget=1);assert status==4 and value==0xa5a55a5a and len(script.trace)>20;guards.append(dict(work_limit=True,original_completion_claimed=False))
    core=Path(json.loads((ROOT/'verification/DSP-music-context-experimental-candidate.json').read_text())['core_path']);oracle=controls.media.scheduler.Native(diagnostic_core=core);runtime=controls.media.Runtime.__new__(controls.media.Runtime);runtime.oracle,runtime.device,runtime.core=oracle,oracle.device,oracle.lib
    for w in[8,16,32]:reader=getattr(runtime.core,'m68k_read_memory_'+str(w));reader.argtypes=[c.c_uint32];reader.restype=c.c_uint32
    runtime.core.m68k_write_memory_32.argtypes=[c.c_uint32,c.c_uint32];runtime.core.m68k_write_memory_32.restype=None
    try:native=[native_blitter(runtime,fn,snapshot,case)for case in fixtures()if case['id']==4 and tuple(case['geometry'])==(20,10,40,20)]
    finally:oracle.close()
    save(out/'results.json',results);save(out/'native-blitter.json',native);save(out/'guards.json',guards)
    report=dict(status='panel_refresh_original_commands_and_native_blitter_match',directory=str(out),cases=len(results),instruction_address_coverage=[len(coverage),len(decoded)],native_blitter_cases=len(native),guards=len(guards),source_sha256={name:sha((restore/name).read_bytes())for name in ['biwn_panel_refresh.c','biwn_panel_refresh.h']},verifier_sha256=sha(Path(__file__).read_bytes()),remaining_scripted_helpers=['0x149ae'],new_training=False,default_runtime_promoted=False,scope='Complete12620..12896 fullD0, signed index, word wrapping, ordered RAM/MMIO/text calls versus original CPU. Native original and C both drive actual pinned emulator blitter for eight valid border/text configurations; public RAM/framebuffer and text call arguments match. Text149AE is scripted identically, so glyph rasterization, whole UI/scene/frame timing, CPU ABI and natural gameplay remain excluded. Raw large geometry matrix checks command semantics without blitter effects; physical hardware not tested.')
    save(out/'report.json',report);save(ROOT/'verification/panel-refresh-current.json',report);print(json.dumps(report),flush=True)


if __name__=='__main__':main()
