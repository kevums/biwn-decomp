"""Original E19E/E202 CPU protocols: rereads/order/D0 and host guards."""
import ctypes as c
from datetime import datetime,timezone
import itertools
import json
import os
from pathlib import Path
import random
import subprocess
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_gpu_commands as prior
ROOT=prior.stage.ROOT;SP=prior.SP;STOP=prior.STOP;Bus=prior.Bus
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')


class Script:
    def __init__(self,command,pre,ack,post,count):
        self.command=command;self.queues=dict(pre=pre,ack=ack,post=post);self.indices=dict(pre=0,ack=0,post=0);self.phase='pre';self.count=count;self.trace=[];self.reads=0;self.writes=0;self.fail_read=None;self.fail_write=None
    def read(self,address):
        self.reads+=1
        if self.reads==self.fail_read:raise RuntimeError('injected read failure')
        if address==0x49b88:assert self.command==0x52e0;value=self.count
        else:
            assert address==(0xf03204 if self.phase=='ack'else 0xf03200),(hex(address),self.phase)
            i=self.indices[self.phase];value=self.queues[self.phase][i];self.indices[self.phase]+=1
            if self.phase=='ack'and value!=self.command:self.phase='post'
        self.trace.append(['r',address,value]);return value
    def write(self,address,value):
        self.writes+=1
        if self.writes==self.fail_write:raise RuntimeError('injected write failure')
        self.trace.append(['w',address,value])
        if address==0xf03204:assert value==self.command;self.phase='ack'
    def complete(self):return all(self.indices[k]==len(v)for k,v in self.queues.items())


def original(snapshot,entry,script,incoming):
    cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_map(0xf03000,0x1000);cpu.mem_write(0,snapshot)
    regs=[UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6]
    for r,v in zip(regs,incoming):cpu.reg_write(r,v)
    cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP);cpu.mem_write(SP,STOP.to_bytes(4,'big'));sites=set()
    def code(e,address,size,_):assert 0xe19e<=address<0xe220 or 0xe098<=address<0xe0a6;sites.add(address)
    def read(e,access,address,width,value,_):
        if address==0x49b88 or 0xf03000<=address<0xf04000:
            assert width==4;e.mem_write(address,script.read(address).to_bytes(4,'big'))
    def write(e,access,address,width,value,_):
        if address==0x10a684 or 0xf03000<=address<0xf04000:assert width==4;script.write(address,value&0xffffffff)
        else:assert SP-8<=address<=SP and width==4,(hex(address),width)
    cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(entry,STOP,count=2048,timeout=2000000)
    assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
    assert all(cpu.reg_read(r)==v for i,(r,v)in enumerate(zip(regs,incoming))if entry==0xe202 or i!=0)
    return cpu.reg_read(UC_M68K_REG_D0),sites


def translated(fn,script,budget=128,missing=None,null_out=False):
    errors=[];context=0xc0ffee
    def read(ctx,address,out):
        try:assert ctx==context;out[0]=script.read(address);return 0
        except Exception as error:errors.append(repr(error));return 1
    def write(ctx,address,value):
        try:assert ctx==context;script.write(address,value);return 0
        except Exception as error:errors.append(repr(error));return 1
    reader=prior.READ(read);writer=prior.WRITE(write)
    bus=Bus(prior.READ()if missing=='read'else reader,prior.WRITE()if missing=='write'else writer,context,budget)
    out=c.c_uint32(0xa55aa55a)
    status=fn(c.byref(bus),None if null_out else c.byref(out))if script.command==0x52e0 else fn(c.byref(bus))
    return status,out.value,bus.read_budget,errors


def main():
    out=ROOT/'verification/gpu-render-commands'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libgpu-render-commands.dylib';names=['biwn_gpu_commands.c','biwn_gpu_render_commands.c']
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(source/n)for n in names],'-o',str(library)]
    built=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
    lib=c.CDLL(str(library));projection=lib.biwn_gpu_submit_52e0;projection.argtypes=[c.POINTER(Bus),c.POINTER(c.c_uint32)];projection.restype=c.c_int;draw=lib.biwn_gpu_submit_57a0;draw.argtypes=[c.POINTER(Bus)];draw.restype=c.c_int
    snapshot=(ROOT/'runs/zero-warm-whole-merchant-reference/final-RAM.bin').read_bytes();rng=random.Random(0xe19ee202);rows=[];coverage=set()
    for entry,cmd,fn in[(0xe19e,0x52e0,projection),(0xe202,0x57a0,draw)]:
        for pre,ack,post,ack_value in itertools.product(range(4),range(4),range(4)if cmd==0x52e0 else[0],[0,0xffffffff,0x80000000,cmd^1]):
            vectors=([0xffffffff]*pre+[0],[cmd]*ack+[ack_value],[1]*post+[0]if cmd==0x52e0 else[],rng.getrandbits(32));incoming=[rng.getrandbits(32)for _ in range(15)]
            a=Script(cmd,*vectors);expected,sites=original(snapshot,entry,a,incoming);b=Script(cmd,*vectors);status,value,remaining,errors=translated(fn,b)
            assert not status and not errors and a.complete()and b.complete()and a.trace==b.trace and (value==expected if cmd==0x52e0 else expected==incoming[0]),(status,errors,a.trace,b.trace)
            assert remaining==128-sum(e[0]=='r'for e in b.trace)
            coverage|=sites;rows.append(dict(entry=hex(entry),pre_busy_reads=pre,pending_ack_reads=ack,post_busy_reads=post,ack_value=hex(ack_value),full_D0=expected,trace=a.trace))
    guards=[]
    for cmd,fn in[(0x52e0,projection),(0x57a0,draw)]:
        vectors=([1,0],[cmd,0xffffffff],[1,0]if cmd==0x52e0 else[],0xfedcba98)
        complete=Script(cmd,*vectors);assert translated(fn,complete)[0]==0
        for budget in range(sum(e[0]=='r'for e in complete.trace)):
            script=Script(cmd,*vectors);status,value,remaining,errors=translated(fn,script,budget=budget)
            assert status==2 and remaining==0 and value==0xa55aa55a and not errors
            assert script.trace==complete.trace[:len(script.trace)];guards.append(dict(command=hex(cmd),budget=budget,status=status))
        for kind in['read','write']:
            n=sum(event[0]==kind[0]for event in complete.trace)
            for ordinal in range(1,n+1):
                script=Script(cmd,*vectors);setattr(script,'fail_'+kind,ordinal);status,value,remaining,errors=translated(fn,script)
                assert status==3 and value==0xa55aa55a and len(errors)==1 and script.trace==complete.trace[:len(script.trace)]
                guards.append(dict(command=hex(cmd),failure=kind,ordinal=ordinal,status=status))
        for missing in['read','write']:
            script=Script(cmd,*vectors);status,value,remaining,errors=translated(fn,script,missing=missing);assert status==1 and not script.trace and value==0xa55aa55a;guards.append(dict(command=hex(cmd),missing=missing))
    assert projection(None,None)==draw(None)==1
    script=Script(0x52e0,[0],[0],[],0);assert translated(projection,script,null_out=True)[0]==1 and not script.trace
    save(out/'cases.json',rows);save(out/'guards.json',guards)
    report=dict(status='original_E19E_E202_public_protocol_and_full_D0_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(rows),guards=len(guards)+3,original_instruction_addresses=len(coverage),source_sha256={n:prior.hashlib.sha256((source/n).read_bytes()).hexdigest()for n in names},scope='Original M68000 instructions in Unicorn with scripted asynchronous prebusy/ack/postbusy reads and distinct callback context. Every publicread/writeorder/value and fullD0 compare. Exhausted readbudget, each read/writefailure and badarguments retain prefixeffects/untouched52E0output. E202endsatackwithoutpostidle. No actualGPUexecution/fullABI/CCR/timing/wholegame proof.')
    save(out/'report.json',report);save(ROOT/'verification/gpu-render-commands-current.json',report);print(json.dumps(report),flush=True)


if __name__=='__main__':main()
