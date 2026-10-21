"""Original13AE0+134DC versus both native high-level C implementations together.

The candidate dispatches into the real native134DC, not an original-body substitute. Original137E0and10520children execute when called; four leaf services remain prescribed. Separate private frames coexist in the same guest task stack.
Unicorn compares ordered public bus/call observations. Retained native CPU
replays both instruction streams and independently compares full returned CPU,
SR/banks, logical child/helper entry CPU/stack, and public2MBRAM. Private C
frames, installation bytes and return-PC differences are declared exclusions.
"""
import argparse,copy,json,os,shutil,subprocess
from collections import Counter
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import UC_CPU_M68K_M68000,UC_M68K_REG_SR,UC_M68K_REG_A7,UC_M68K_REG_PC,UC_M68K_REG_D0
import check_biwn_actor_source_group_v3 as g
from check_biwn_scheduler import Native
ROOT=g.ROOT;ND=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';BASE=0x190000;SP=g.SP;STOP=g.STOP;PARENT_RANGE=None
INITBASE=0x180000;INIT_PAYLOAD=b"";INIT_SYMBOLS={}
SPRITEBASE=0x1a0000;SPRITE_PAYLOAD=b"";SPRITE_SYMBOLS={}

def vectors():
    rows=[copy.deepcopy(x)for x in g.cases()if x['entry']==0x13ae0]
    for mode in [0,0x2000]:
        for flags in range(32):
            for free in [0,1,39,40]:
                c=copy.deepcopy(rows[0]);c['params'][0]=0xffff;c['sr']=mode|flags
                c['initial'] += [[0x4208c-1,1,1]]+[[0x49d6c+i*206,2,int(i!=free)]for i in range(40)]
                rows.append(c)
            c=copy.deepcopy(rows[0]);c['params'][0]=0x8000;c['sr']=mode|flags;c['initial'].append([0x4208c-0x8000,1,0]);rows.append(c)
    return rows

def normalized(ram,snapshot,length):
    b=bytearray(ram)
    for lo,hi in [(BASE,BASE+length),(0x13ae0,0x13ae8),(0x134dc,0x134e4),(INITBASE,INITBASE+len(INIT_PAYLOAD)),(SPRITEBASE,SPRITEBASE+len(SPRITE_PAYLOAD)),(0x137e0,0x137e8),(SP-8192,SP+64)]+[(a,a+2)for a in g.SERVICES]:b[lo:hi]=snapshot[lo:hi]
    return bytes(b)

def execute(snapshot,case,payload,symbols,compiled):
    memory=bytearray(snapshot);memory[BASE:BASE+len(payload)]=payload;memory[INITBASE:INITBASE+len(INIT_PAYLOAD)]=INIT_PAYLOAD;memory[SPRITEBASE:SPRITEBASE+len(SPRITE_PAYLOAD)]=SPRITE_PAYLOAD
    if compiled:memory[0x13ae0:0x13ae8]=b'\x4e\xf9'+symbols['biwn_native_actor_dispatch'].to_bytes(4,'big')+b'\x4e\x71'
    if compiled:memory[0x134dc:0x134e4]=b'\x4e\xf9'+INIT_SYMBOLS['biwn_native_actor_initialize'].to_bytes(4,'big')+b'\x4e\x71';memory[0x137e0:0x137e8]=b'\x4e\xf9'+SPRITE_SYMBOLS['biwn_native_sprite_create'].to_bytes(4,'big')+b'\x4e\x71'
    script=g.prior.Script(memory,case);u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,bytes(script.memory))
    for a in g.SERVICES:u.mem_write(a,b'\x4e\x75')
    params=b''.join(v.to_bytes(w,'big')for v,w in zip(case['params'],g.prior.WIDTHS[0x13ae0]));u.mem_write(SP,STOP.to_bytes(4,'big')+params)
    u.reg_write(UC_M68K_REG_SR,case['sr'])
    for reg,v in zip(g.prior.world.REGS,case['incoming']):u.reg_write(reg,v)
    u.reg_write(UC_M68K_REG_A7,SP);machine=[];coverage=set();minimum=SP
    def word(a,w=4):return int.from_bytes(u.mem_read(a,w),'big')
    def private(a,w):return(SP-8192<=a and a+w<=SP+64)or(BASE<=a and a+w<=BASE+len(payload))or(INITBASE<=a and a+w<=INITBASE+len(INIT_PAYLOAD))or(SPRITEBASE<=a and a+w<=SPRITEBASE+len(SPRITE_PAYLOAD))
    def code(e,pc,w,_):
        nonlocal minimum
        stack=e.reg_read(UC_M68K_REG_A7);minimum=min(minimum,stack);step=dict(pc=pc,queue_injections=[]);machine.append(step)
        if pc in g.SERVICES:
            args=[];offset=4
            for width in g.prior.WIDTHS[pc]:args.append(word(stack+offset,width));offset+=width
            script.changed=[];incoming=e.reg_read(UC_M68K_REG_D0);result=script.call(pc,args,incoming)
            step['service']=dict(target=pc,args=args,incoming=incoming,result=result,effects=list(script.changed))
            for a,width,value in script.changed:u.mem_write(a,value.to_bytes(width,'big'))
            u.reg_write(UC_M68K_REG_D0,result);return
        if pc in g.MEMBERS and pc!=0x13ae0:
            args=[];offset=4
            for width in g.prior.WIDTHS[pc]:args.append(word(stack+offset,width));offset+=width
            script.trace.append(['child_entry',pc,args,[e.reg_read(reg)for reg in g.prior.world.REGS],stack])
        if compiled:
            assert pc in [0x13ae0,0x134dc,0x137e0] or BASE<=pc<BASE+len(payload)or INITBASE<=pc<INITBASE+len(INIT_PAYLOAD)or SPRITEBASE<=pc<SPRITEBASE+len(SPRITE_PAYLOAD)or (PARENT_RANGE is not None and PARENT_RANGE[0]<=pc<PARENT_RANGE[1])or any(lo<=pc<hi for lo,hi in g.prior.CODE_RANGES if lo!=0x13ae0 and not(0x134dc<=pc<0x13ae0)),('Original dispatcher instruction reached',hex(pc))
        else:assert any(lo<=pc<hi for lo,hi in g.prior.CODE_RANGES)or(PARENT_RANGE is not None and PARENT_RANGE[0]<=pc<PARENT_RANGE[1]),hex(pc)
        if 0x134dc<=pc<0x13b5a:coverage.add(pc)
    def read(e,k,a,w,v,_):
        if private(a,w):return
        value=script.read(a,w)
        if any(q['address']==a and q['width']==w for q in case.get('read_queues',[])):machine[-1]['queue_injections'].append([a,w,value])
        e.mem_write(a,value.to_bytes(w,'big'))
    def write(e,k,a,w,v,_):
        if not private(a,w):script.write(a,w,v&((1<<(8*w))-1))
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(0x13ae0,STOP,count=1000000,timeout=5000000)
    assert u.reg_read(UC_M68K_REG_PC)==STOP and u.reg_read(UC_M68K_REG_A7)==SP+4
    assert bytes(u.mem_read(SP+4,len(params)))==params
    ram=bytes(u.mem_read(0,0x200000));assert ram[INITBASE:INITBASE+len(INIT_PAYLOAD)]==INIT_PAYLOAD;assert ram[SPRITEBASE:SPRITEBASE+len(SPRITE_PAYLOAD)]==SPRITE_PAYLOAD;assert ram[BASE:BASE+len(payload)]==payload
    public=normalized(ram,snapshot,len(payload));assert public==normalized(script.memory,snapshot,len(payload))
    return dict(ram=public,registers=[u.reg_read(reg)for reg in g.prior.world.REGS],trace=script.trace,machine=machine,private_depth=SP-minimum,coverage=coverage)

def replay(native,snapshot,case,payload,symbols,compiled,expected):
    memory=bytearray(snapshot);memory[BASE:BASE+len(payload)]=payload;memory[INITBASE:INITBASE+len(INIT_PAYLOAD)]=INIT_PAYLOAD;memory[SPRITEBASE:SPRITEBASE+len(SPRITE_PAYLOAD)]=SPRITE_PAYLOAD
    if compiled:memory[0x13ae0:0x13ae8]=b'\x4e\xf9'+symbols['biwn_native_actor_dispatch'].to_bytes(4,'big')+b'\x4e\x71'
    if compiled:memory[0x134dc:0x134e4]=b'\x4e\xf9'+INIT_SYMBOLS['biwn_native_actor_initialize'].to_bytes(4,'big')+b'\x4e\x71';memory[0x137e0:0x137e8]=b'\x4e\xf9'+SPRITE_SYMBOLS['biwn_native_sprite_create'].to_bytes(4,'big')+b'\x4e\x71'
    memory=bytearray(g.prior.Script(memory,case).memory)
    for a in g.SERVICES:memory[a:a+2]=b'\x4e\x75'
    params=b''.join(v.to_bytes(w,'big')for v,w in zip(case['params'],g.prior.WIDTHS[0x13ae0]));memory[SP:SP+4+len(params)]=STOP.to_bytes(4,'big')+params
    native.device.seed(bytes(memory),0);lib=native.lib;lib.m68k_pulse_reset();lib.m68k_set_irq(0)
    for sr,sp in [(0x2000,SP if case['sr']&0x2000 else 0x1fd000),(0,SP if not case['sr']&0x2000 else 0x1fc000)]:lib.m68k_set_reg(17,sr);lib.m68k_set_reg(15,sp)
    lib.m68k_set_reg(17,case['sr'])
    for i,v in enumerate(case['incoming']):lib.m68k_set_reg(i,v)
    lib.m68k_set_reg(15,SP);lib.m68k_set_reg(16,0x13ae0);events=[]
    def reg(i):return lib.m68k_get_reg(None,i)
    for index,step in enumerate(expected['machine']):
        pc=reg(16);assert pc==step['pc'],('NativePC',index,hex(pc),hex(step['pc']))
        for a,w,v in step['queue_injections']:native.device.direct(a,w,v)
        if pc in (g.MEMBERS-{0x13ae0})|g.SERVICES:
            ram=native.device.ram();stack=reg(15);offset=4;args=[]
            for width in g.prior.WIDTHS[pc]:args.append(int.from_bytes(ram[stack+offset:stack+offset+width],'big'));offset+=width
            events.append(dict(target=pc,args=args,registers=[reg(i)for i in range(15)],SP=stack,SR=reg(17)))
        if 'service'in step:
            s=step['service'];assert events[-1]['args']==s['args']and reg(0)==s['incoming']
            for a,w,v in s['effects']:native.device.direct(a,w,v)
            lib.m68k_set_reg(0,s['result'])
        lib.m68k_execute(1)
    assert reg(16)==STOP and reg(15)==SP+4
    ram=native.device.ram();assert ram[INITBASE:INITBASE+len(INIT_PAYLOAD)]==INIT_PAYLOAD;assert ram[SPRITEBASE:SPRITEBASE+len(SPRITE_PAYLOAD)]==SPRITE_PAYLOAD;assert ram[SP+4:SP+4+len(params)]==params and ram[BASE:BASE+len(payload)]==payload
    assert normalized(ram,snapshot,len(payload))==expected['ram'],'Native/Unicorn publicRAM'
    sr=reg(17);regs=[reg(i)for i in range(16)];assert regs[:15]==expected['registers'],'Native/Unicorn registers'
    return dict(registers=regs,SR=sr,USP=native.prefix[16]if sr&0x2000 else regs[15],SSP=regs[15]if sr&0x2000 else native.prefix[17],events=events)
