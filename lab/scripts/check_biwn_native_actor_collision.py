"""Original13B5A/13BB0 versus high-level native collision C/original-facing ABI.

All four geometry helpers execute in both lanes; no prescribed services. Source collision bodies never delegate original13B5A/13BB0instructions. Finite validRAM/geometry fixtures; no GPU/device/task/timing/general concurrent-input proof.
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
import native_actor_collision_fixture_env as g
from check_biwn_scheduler import Native
ROOT=g.ROOT;ND=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';BASE=0x180000;SP=g.SP;STOP=g.STOP;PARENT_RANGE=None
ENTRY,END=0x13b5a,0x13c9a

def vectors():
    return g.cases()


def normalized(ram,snapshot,length):
    b=bytearray(ram)
    for lo,hi in [(BASE,BASE+length),(0x13b5a,0x13b62),(0x13bb0,0x13bb6),(SP-8192,SP+64)]+[(a,a+2)for a in g.SERVICES]:b[lo:hi]=snapshot[lo:hi]
    return bytes(b)

def execute(snapshot,case,payload,symbols,compiled):
    ENTRY=case['entry'];END=g.END_BY_ENTRY[ENTRY]
    memory=bytearray(snapshot);memory[BASE:BASE+len(payload)]=payload
    if compiled:memory[ENTRY:ENTRY+g.PATCH_WIDTHS[ENTRY]]=b'\x4e\xf9'+symbols['biwn_native_actor_collision_outdoor'if ENTRY==0x13b5a else'biwn_native_actor_collision_indoor'].to_bytes(4,'big')+(b'\x4e\x71'if g.PATCH_WIDTHS[ENTRY]==8 else b'')
    script=g.prior.Script(memory,case);u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,bytes(script.memory))
    for a in g.SERVICES:u.mem_write(a,b'\x4e\x75')
    params=b''.join(v.to_bytes(w,'big')for v,w in zip(case['params'],g.prior.WIDTHS[ENTRY]));u.mem_write(SP,STOP.to_bytes(4,'big')+params)
    u.reg_write(UC_M68K_REG_SR,case['sr'])
    for reg,v in zip(g.prior.world.REGS,case['incoming']):u.reg_write(reg,v)
    u.reg_write(UC_M68K_REG_A7,SP);machine=[];coverage=set();minimum=SP
    def word(a,w=4):return int.from_bytes(u.mem_read(a,w),'big')
    def private(a,w):return(SP-8192<=a and a+w<=SP+64)or(BASE<=a and a+w<=BASE+len(payload))
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
        if pc in g.MEMBERS and pc!=ENTRY:
            args=[];offset=4
            for width in g.prior.WIDTHS[pc]:args.append(word(stack+offset,width));offset+=width
            script.trace.append(['child_entry',pc,args,[e.reg_read(reg)for reg in g.prior.world.REGS],stack])
        if compiled:
            assert pc==ENTRY or BASE<=pc<BASE+len(payload)or (PARENT_RANGE is not None and PARENT_RANGE[0]<=pc<PARENT_RANGE[1])or any(lo<=pc<hi for lo,hi in g.prior.CODE_RANGES if not(0x13b5a<=pc<0x13c9a)),('Original collision instruction reached',hex(pc))
        else:assert any(lo<=pc<hi for lo,hi in g.prior.CODE_RANGES)or(PARENT_RANGE is not None and PARENT_RANGE[0]<=pc<PARENT_RANGE[1]),hex(pc)
        if ENTRY<=pc<END:coverage.add(pc)
    def read(e,k,a,w,v,_):
        if private(a,w):return
        value=script.read(a,w)
        if any(q['address']==a and q['width']==w for q in case.get('read_queues',[])):machine[-1]['queue_injections'].append([a,w,value])
        e.mem_write(a,value.to_bytes(w,'big'))
    def write(e,k,a,w,v,_):
        if not private(a,w):script.write(a,w,v&((1<<(8*w))-1))
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(ENTRY,STOP,count=1000000,timeout=5000000)
    assert u.reg_read(UC_M68K_REG_PC)==STOP and u.reg_read(UC_M68K_REG_A7)==SP+4
    assert bytes(u.mem_read(SP+4,len(params)))==params
    ram=bytes(u.mem_read(0,0x200000));assert ram[BASE:BASE+len(payload)]==payload
    public=normalized(ram,snapshot,len(payload));assert public==normalized(script.memory,snapshot,len(payload))
    return dict(ram=public,registers=[u.reg_read(reg)for reg in g.prior.world.REGS],trace=script.trace,machine=machine,private_depth=SP-minimum,coverage=coverage)

def replay(native,snapshot,case,payload,symbols,compiled,expected):
    ENTRY=case['entry'];END=g.END_BY_ENTRY[ENTRY]
    memory=bytearray(snapshot);memory[BASE:BASE+len(payload)]=payload
    if compiled:memory[ENTRY:ENTRY+g.PATCH_WIDTHS[ENTRY]]=b'\x4e\xf9'+symbols['biwn_native_actor_collision_outdoor'if ENTRY==0x13b5a else'biwn_native_actor_collision_indoor'].to_bytes(4,'big')+(b'\x4e\x71'if g.PATCH_WIDTHS[ENTRY]==8 else b'')
    memory=bytearray(g.prior.Script(memory,case).memory)
    for a in g.SERVICES:memory[a:a+2]=b'\x4e\x75'
    params=b''.join(v.to_bytes(w,'big')for v,w in zip(case['params'],g.prior.WIDTHS[ENTRY]));memory[SP:SP+4+len(params)]=STOP.to_bytes(4,'big')+params
    native.device.seed(bytes(memory),0);lib=native.lib;lib.m68k_pulse_reset();lib.m68k_set_irq(0)
    for sr,sp in [(0x2000,SP if case['sr']&0x2000 else 0x1fd000),(0,SP if not case['sr']&0x2000 else 0x1fc000)]:lib.m68k_set_reg(17,sr);lib.m68k_set_reg(15,sp)
    lib.m68k_set_reg(17,case['sr'])
    for i,v in enumerate(case['incoming']):lib.m68k_set_reg(i,v)
    lib.m68k_set_reg(15,SP);lib.m68k_set_reg(16,ENTRY);events=[]
    def reg(i):return lib.m68k_get_reg(None,i)
    for index,step in enumerate(expected['machine']):
        pc=reg(16);assert pc==step['pc'],('NativePC',index,hex(pc),hex(step['pc']))
        for a,w,v in step['queue_injections']:native.device.direct(a,w,v)
        if pc in (g.MEMBERS-{ENTRY})|g.SERVICES:
            ram=native.device.ram();stack=reg(15);offset=4;args=[]
            for width in g.prior.WIDTHS[pc]:args.append(int.from_bytes(ram[stack+offset:stack+offset+width],'big'));offset+=width
            events.append(dict(target=pc,args=args,registers=[reg(i)for i in range(15)],SP=stack,SR=reg(17)))
        if 'service'in step:
            s=step['service'];assert events[-1]['args']==s['args']and reg(0)==s['incoming']
            for a,w,v in s['effects']:native.device.direct(a,w,v)
            lib.m68k_set_reg(0,s['result'])
        lib.m68k_execute(1)
    assert reg(16)==STOP and reg(15)==SP+4
    ram=native.device.ram();assert ram[SP+4:SP+4+len(params)]==params and ram[BASE:BASE+len(payload)]==payload
    assert normalized(ram,snapshot,len(payload))==expected['ram'],'Native/Unicorn publicRAM'
    sr=reg(17);regs=[reg(i)for i in range(16)];assert regs[:15]==expected['registers'],'Native/Unicorn registers'
    return dict(registers=regs,SR=sr,USP=native.prefix[16]if sr&0x2000 else regs[15],SSP=regs[15]if sr&0x2000 else native.prefix[17],events=events)

def main():
    global BASE,PARENT_RANGE
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=ND/'actor-collision-reference.c');ap.add_argument('--limit',type=int);ap.add_argument('--address',type=lambda x:int(x,0),default=BASE);ap.add_argument('--parent-build',type=Path);args=ap.parse_args();BASE=args.address
    out=ROOT/'verification/native-actor-collision-linked'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    command=['make','-f',str(ND/'Makefile.actor-collision'),'actor-collision','BUILD='+str(out/'build'),'COLLISION_SOURCE='+str(args.source.resolve()),'ADDRESS='+hex(BASE)]
    p=subprocess.run(command,capture_output=True,text=True);(out/'build.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    binary=out/'build/actor-collision.bin';elf=out/'build/actor-collision.elf';payload=binary.read_bytes();assert len(payload)<0x10000
    nm=subprocess.check_output([str(ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'-n',str(elf)],text=True);(out/'symbols.txt').write_text(nm);symbols={x[2]:int(x[0],16)for line in nm.splitlines()if len(x:=line.split())==3}
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();assert g.sha(ROOT/'render-assets/biwn-inventory-baseline.bin')=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3'
    parent_inputs=[]
    if args.parent_build:
        parent=g.read(args.parent_build);assert g.sha(parent['derived_stage'])==parent['derived_stage_sha256']
        assert BASE==(parent['resident_address']+parent['linked_component_bytes']+3)&~3
        assert BASE+len(payload)<=parent['heap_start']==parent['resident_address']+parent['component_bytes']
        image=bytearray(snapshot);image[0x4000:0x100000]=Path(parent['derived_stage']).read_bytes();image[parent['resident_address']:parent['resident_address']+parent['component_bytes']]=Path(parent['component']).read_bytes()
        assert all(image[a:a+w]==snapshot[a:a+w]for a,w in g.PATCH_WIDTHS.items())
        snapshot=bytes(image);PARENT_RANGE=(parent['resident_address'],parent['resident_address']+parent['linked_component_bytes'])
        parent_inputs=[args.parent_build.resolve(),Path(parent['derived_stage']),Path(parent['component'])]
    rows=vectors();rows=rows[:args.limit]if args.limit else rows
    inputs=[Path(__file__),Path(g.__file__),Path(g.prior.__file__),args.source.resolve(),binary,elf,*[ND/n for n in ['actor-collision-native.h','actor-collision-shim.S','actor-collision.ld','Makefile.actor-collision']],ROOT/'scripts/check_biwn_scheduler.py',ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib']
    inputs+=parent_inputs+[Path(g.base.__file__),Path(g.direction.__file__),Path(g.movement.__file__),Path(g.creation.__file__),ROOT/'projects/black-ice-white-noise/restoration/biwn_actor_collisionment.c']
    hashes={str(p):g.sha(p)for p in inputs};state=dict(status='checking_original_ABI_native_actor_collision',directory=str(out),pid=os.getpid(),planned=len(rows),completed=0,source=str(args.source.resolve()),source_sha256=hashes,binary=str(binary),ELF=str(elf),binary_bytes=len(payload),code_address=BASE,parent_build=str(args.parent_build)if args.parent_build else None,symbols=symbols,disc_integrated=False,new_predictions=0)
    def mark():g.save(out/'protocol.json',state);g.save(ROOT/'verification/native-actor-collision-linked-active.json',state)
    mark();g.save(out/'fixtures.json',rows);results=[];coverage=set();native=Native()
    try:
        for i,case in enumerate(rows):
            a=execute(snapshot,case,payload,symbols,False);b=execute(snapshot,case,payload,symbols,True)
            if any(a[k]!=b[k]for k in ['ram','registers','trace']):
                g.save(out/'mismatch.json',dict(index=i,case=case,original_trace=a['trace'],compiled_trace=b['trace'],original_regs=a['registers'],compiled_regs=b['registers']));raise AssertionError('OriginalABI actor collision comparison failed')
            an=replay(native,snapshot,case,payload,symbols,False,a);bn=replay(native,snapshot,case,payload,symbols,True,b)
            if an!=bn:g.save(out/'native-mismatch.json',dict(index=i,case=case,original=an,compiled=bn));raise AssertionError('Full native CPU/SR/bank/helper ABI mismatch')
            coverage.update(a['coverage']);results.append(dict(index=i,original_steps=len(a['machine']),compiled_steps=len(b['machine']),original_depth=a['private_depth'],compiled_depth=b['private_depth'],calls=len(an['events'])))
            if i%64==0:state['completed']=len(results);mark();print('OriginalABI actor collision',len(results),'/',len(rows),flush=True)
        assert all(g.sha(Path(p))==h for p,h in hashes.items())
        g.save(out/'results.json',results);state.update(status='terminal_original_ABI_actor_collision_preflight_pass'if args.limit else'terminal_original_ABI_actor_collision_pass',completed=len(results),cases=len(results),original_sites=sorted(coverage),per_root_cases={hex(entry):sum(c['entry']==entry for c in rows)for entry in g.PATCH_WIDTHS},max_private_depth=max(x['compiled_depth']for x in results),max_original_depth=max(x['original_depth']for x in results),scope=__doc__);mark()
        if not args.limit:g.save(ROOT/'verification/native-actor-collision-linked-current.json',state)
        print(state['status'],len(rows),'bytes',len(payload),'depth',state['max_private_depth'],flush=True)
    except BaseException as error:state.update(status='terminal_original_ABI_actor_collision_failed',error=repr(error),completed=len(results));mark();raise
    finally:native.close()

if __name__=='__main__':main()
