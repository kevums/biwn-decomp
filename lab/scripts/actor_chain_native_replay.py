"""Native replay with explicit source-C boundaries and physical stack observation."""
from pathlib import Path


def replay(engine,native,snapshot,case,payload,symbols,compiled,expected,observer=None):
    entry=case['entry'];SP,STOP=engine.SP,engine.STOP
    memory=bytearray(snapshot);memory[engine.BASE:engine.BASE+len(payload)]=payload
    roots={0x13c9a:('biwn_native_actor_move',8),0x13b5a:('biwn_native_actor_collision_outdoor',8),0x13bb0:('biwn_native_actor_collision_indoor',6)}
    if compiled:
        for root in roots if entry==0x13c9a else [entry]:
            name,width=roots[root]
            memory[root:root+width]=b'\x4e\xf9'+symbols[name].to_bytes(4,'big')+(b'\x4e\x71'if width==8 else b'')
    memory=bytearray(engine.g.prior.Script(memory,case).memory)
    for target in engine.g.SERVICES:
        memory[target:target+2]=b'\x4e\x75'
    params=b''.join(v.to_bytes(w,'big')for v,w in zip(case['params'],engine.g.prior.WIDTHS[entry]))
    memory[SP:SP+4+len(params)]=STOP.to_bytes(4,'big')+params
    boundary=SP-918;guard_start=boundary-166;guard=bytes((i*73+19)&255 for i in range(166))
    memory[guard_start:boundary]=guard
    native.device.seed(bytes(memory),0);lib=native.lib;lib.m68k_pulse_reset();lib.m68k_set_irq(0)
    for sr,sp in [(0x2000,SP if case['sr']&0x2000 else 0x1fd000),(0,SP if not case['sr']&0x2000 else 0x1fc000)]:
        lib.m68k_set_reg(17,sr);lib.m68k_set_reg(15,sp)
    lib.m68k_set_reg(17,case['sr'])
    for i,value in enumerate(case['incoming']):
        lib.m68k_set_reg(i,value)
    lib.m68k_set_reg(15,SP);lib.m68k_set_reg(16,entry)
    events=[];minimum=SP
    def reg(i):return lib.m68k_get_reg(None,i)
    if observer:
        observer.begin(native,case,compiled,symbols,engine.BASE,payload)
    for index,step in enumerate(expected['machine']):
        pc=reg(16);assert pc==step['pc'],('NativePC',index,hex(pc),hex(step['pc']))
        minimum=min(minimum,reg(15))
        for a,w,v in step['queue_injections']:
            native.device.direct(a,w,v)
        if observer:
            observer.step(pc)
        if compiled and pc==symbols['biwn_actor_chain_collision_call']:
            ram=native.device.ram();stack=reg(15);context=int.from_bytes(ram[stack+4:stack+8],'big')
            shadow=[int.from_bytes(ram[context+4*i:context+4*i+4],'big')for i in range(20)]
            target=shadow[18];logical=shadow[15];offset=4;args=[]
            for width in engine.g.prior.WIDTHS[target]:
                args.append(int.from_bytes(ram[logical+offset:logical+offset+width],'big'));offset+=width
            events.append(dict(target=target,args=args,registers=shadow[:15],SP=logical,SR=shadow[16]&0xffff))
        if pc in(engine.g.MEMBERS-{entry})|engine.g.SERVICES:
            ram=native.device.ram();stack=reg(15);offset=4;args=[]
            for width in engine.g.prior.WIDTHS[pc]:
                args.append(int.from_bytes(ram[stack+offset:stack+offset+width],'big'));offset+=width
            events.append(dict(target=pc,args=args,registers=[reg(i)for i in range(15)],SP=stack,SR=reg(17)))
        if 'service'in step:
            service=step['service'];assert events[-1]['args']==service['args']and reg(0)==service['incoming']
            for a,w,v in service['effects']:
                native.device.direct(a,w,v)
            lib.m68k_set_reg(0,service['result'])
        lib.m68k_execute(1)
    assert reg(16)==STOP and reg(15)==SP+4
    ram=native.device.ram();assert ram[guard_start:boundary]==guard,'Task header/lower guard changed'
    assert ram[SP+4:SP+4+len(params)]==params and ram[engine.BASE:engine.BASE+len(payload)]==payload
    assert engine.normalized(ram,snapshot,len(payload))==expected['ram'],'Native/Unicorn publicRAM'
    registers=[reg(i)for i in range(16)];sr=reg(17)
    assert registers[:15]==expected['registers']
    if observer:
        observer.finish()
    return dict(registers=registers,SR=sr,USP=native.prefix[16]if sr&0x2000 else registers[15],SSP=registers[15]if sr&0x2000 else native.prefix[17],events=events),SP-minimum
