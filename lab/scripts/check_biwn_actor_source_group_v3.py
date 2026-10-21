"""Coupled original five-member group versus target-compiled source-owned C ABI.

Only four external helpers remain prescribed services. Internal group calls
execute complete original or C member bodies, never their former stubs.
"""
import argparse
import copy
import json
import os
import shutil
import subprocess
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import UC_CPU_M68K_M68000,UC_M68K_REG_SR,UC_M68K_REG_A7,UC_M68K_REG_PC,UC_M68K_REG_D0
import check_biwn_actor_creation as prior
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

BASE,ARGV,OUTPUT,EXTERNAL=0x1c8000,0x1d0000,0x1d0040,0x1d1000
SP,STOP=prior.SP,prior.STOP
MEMBERS=set(prior.RANGES)
SERVICES=set(prior.WIDTHS)-MEMBERS


def read(p):return json.loads(Path(p).read_text())


def cases():
    rows=copy.deepcopy(prior.cases())
    def geometry(case,count=3):
        initial=case['initial'];initial += [[0x49c18,4,0x84000],[0x84000,2,count],[0x84004,4,0x100000]]
        for i in range(3):
            initial += [[0x100000+24*i+off,2,value]for off,value in [(2,0),(4,0),(6,16),(8,16)]]
    for i,row in enumerate(rows):
        row['source_case']=i;row['sr']=(0x2000 if i%2 else 0)|(i%32)
        if row['entry'] not in [0x10520,0x105da]:geometry(row)
    for kind in ['actor','sprite','animated']:
        template=next(c for c in rows if c['entry']==(0x137e0 if kind=='animated'else 0x13ae0)
                      and c['params'][0]==(111 if kind=='animated'else 70))
        for count in [0,1,3]:
            for xcell,zcell in [(0,0),(15,15),(16,0),(0,16)]:
                row=copy.deepcopy(template);row['coupled_extra']=kind;row['sr']=0x201f
                geometry(row,count)
                initial=row['initial'];initial += [[0x49c60,2,2],[0x49c6a,4,0x80000020],[0x49c72,4,0xffffffc0]]
                for j in range(40):initial += [[0x49d6c+j*206,2,int(j!=0)],[0x4bd9c+j*30,2,int(j!=0)]]
                initial.append([0x4208c+row['params'][0],1,1 if kind=='actor'else 2 if kind=='animated'else 0])
                row['params'][1]=(0x80000020+xcell*64)&0xffffffff
                row['params'][3]=(0xffffffc0+zcell*64)&0xffffffff
                rows.append(row)
    return rows


def execute(snapshot,case,payload,symbols,compiled):
    memory=bytearray(snapshot)
    if compiled:
        memory[BASE:BASE+len(payload)]=payload;memory[EXTERNAL:EXTERNAL+2]=b'\x4e\x75'
    script=prior.Script(memory,case)
    u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    u.mem_map(0,0x200000);u.mem_write(0,bytes(script.memory))
    u.reg_write(UC_M68K_REG_SR,case['sr'])
    for reg,value in zip(prior.world.REGS,case['incoming']):u.reg_write(reg,value)
    u.reg_write(UC_M68K_REG_A7,SP)
    if compiled:
        argv=b''.join(value.to_bytes(4,'big')for value in case['params'])
        u.mem_write(ARGV,argv);u.mem_write(OUTPUT,b'\xa5\x5a\xa5\x5a')
        params=b''.join(x.to_bytes(4,'big')for x in [case['entry'],ARGV,case['incoming'][0],OUTPUT])
        entry=symbols['biwn_actor_group_invoke']
    else:
        params=b''.join(value.to_bytes(width,'big')for value,width in zip(case['params'],prior.WIDTHS[case['entry']]))
        entry=case['entry']
        for address in SERVICES:u.mem_write(address,b'\x4e\x75')
    u.mem_write(SP,STOP.to_bytes(4,'big')+params)
    counts=Counter();coverage=set();minimum=SP;pending=[];original_frames=[case['entry']];machine=[]
    def private(a,width):
        return (SP-8192<=a and a+width<=SP+64)or(BASE<=a and a+width<=BASE+len(payload))or(ARGV<=a and a+width<=OUTPUT+4)or(EXTERNAL<=a and a+width<=EXTERNAL+2)
    def word(address,width=4):return int.from_bytes(u.mem_read(address,width),'big')
    def perform_service(target,args,incoming):
        assert target in SERVICES,hex(target)
        script.changed=[];d0=script.call(target,args,incoming)
        for address,width,value in script.changed:u.mem_write(address,value.to_bytes(width,'big'))
        counts['external_'+hex(target)]+=1
        machine[-1]['service']=dict(target=target,args=args,incoming=incoming,result=d0,effects=list(script.changed))
        return d0
    def code(e,pc,width,_):
        nonlocal minimum
        counts['steps']+=1;machine.append(dict(pc=pc,queue_injections=[]));stack=e.reg_read(UC_M68K_REG_A7);minimum=min(minimum,stack)
        if compiled:
            if pending and pc==pending[-1]['return_pc'] and stack==pending[-1]['stack']+4:
                call=pending.pop();script.trace.append(['group_return',call['target'],word(call['output'])])
            if pc==symbols['biwn_actor_group_call']:
                target=word(stack+8);argv=word(stack+12);n=word(stack+16);out=word(stack+20)
                assert target in prior.WIDTHS and n==len(prior.WIDTHS[target])
                args=[word(argv+4*i)for i in range(n)]
                if target in MEMBERS:
                    script.trace.append(['group_call',target,args,word(out)])
                    counts['group_'+hex(target)]+=1
                    pending.append(dict(target=target,return_pc=word(stack),stack=stack,output=out))
            if pc==EXTERNAL:
                target,argv,n,out=[word(stack+i)for i in [4,8,12,16]]
                assert target in SERVICES and n==len(prior.WIDTHS[target])
                result=perform_service(target,[word(argv+4*i)for i in range(n)],word(out))
                u.mem_write(out,result.to_bytes(4,'big'));u.reg_write(UC_M68K_REG_D0,0)
                return
            assert BASE<=pc<BASE+len(payload),('Original opcode reached from source-owned group',hex(pc))
        else:
            if pc in SERVICES:
                args=[];offset=4
                for size in prior.WIDTHS[pc]:args.append(word(stack+offset,size));offset+=size
                u.reg_write(UC_M68K_REG_D0,perform_service(pc,args,u.reg_read(UC_M68K_REG_D0)))
                return
            assert any(lo<=pc<hi for lo,hi in prior.CODE_RANGES),hex(pc)
            coverage.add(pc)
            if pc in MEMBERS and not(pc==case['entry'] and counts['steps']==1):
                args=[];offset=4
                for size in prior.WIDTHS[pc]:args.append(word(stack+offset,size));offset+=size
                script.trace.append(['group_call',pc,args,u.reg_read(UC_M68K_REG_D0)])
                original_frames.append(pc);counts['group_'+hex(pc)]+=1
            if pc==prior.RANGES[original_frames[-1]]-2:
                target=original_frames.pop()
                if original_frames:script.trace.append(['group_return',target,u.reg_read(UC_M68K_REG_D0)])
    def memory_read(e,kind,address,width,value,_):
        if private(address,width):return
        observed=script.read(address,width)
        if any(q['address']==address and q['width']==width for q in case.get('read_queues',[])):
            machine[-1]['queue_injections'].append([address,width,observed])
        e.mem_write(address,observed.to_bytes(width,'big'))
    def memory_write(e,kind,address,width,value,_):
        if not private(address,width):script.write(address,width,value&((1<<(8*width))-1))
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,memory_read);u.hook_add(UC_HOOK_MEM_WRITE,memory_write)
    u.emu_start(entry,STOP,count=2000000,timeout=5000000)
    assert u.reg_read(UC_M68K_REG_PC)==STOP and u.reg_read(UC_M68K_REG_A7)==SP+4,hex(u.reg_read(UC_M68K_REG_PC))
    assert not pending and (compiled or not original_frames)
    assert bytes(u.mem_read(SP+4,len(params)))==params,'Root call argument bytes changed'
    assert all(u.reg_read(reg)==case['incoming'][i]for i,reg in enumerate(prior.world.REGS)if i not in [0,1,8,9]),'Callee-save ABI mismatch'
    if compiled:
        assert u.reg_read(UC_M68K_REG_D0)==0,('Source API status',u.reg_read(UC_M68K_REG_D0))
        d0=word(OUTPUT);assert bytes(u.mem_read(BASE,len(payload)))==payload,'Source text/constant pool overwritten'
    else:d0=u.reg_read(UC_M68K_REG_D0)
    ram=bytearray(u.mem_read(0,0x200000))
    if not compiled:
        for address in SERVICES:ram[address:address+2]=script.memory[address:address+2]
    for lo,hi in [(BASE,BASE+len(payload)),(ARGV,OUTPUT+4),(EXTERNAL,EXTERNAL+2),(SP-8192,SP+64)]:
        ram[lo:hi]=snapshot[lo:hi]
    model=bytearray(script.memory)
    for lo,hi in [(BASE,BASE+len(payload)),(ARGV,OUTPUT+4),(EXTERNAL,EXTERNAL+2),(SP-8192,SP+64)]:model[lo:hi]=snapshot[lo:hi]
    assert ram==model,'CPU public RAM disagrees with the observed bus model'
    return dict(D0=d0,RAM=bytes(ram),trace=script.trace,counts=dict(counts),coverage=coverage,private_depth=SP-minimum,machine=machine)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);parser.add_argument('--source',type=Path);args=parser.parse_args()
    bp=ROOT/'verification/native-actor-source-group-build-current.json';build=read(bp)
    assert build['status']=='terminal_source_owned_actor_group_linked_pending_coupling_checks'
    candidate_source=args.source.resolve()if args.source else None
    candidate_inputs=[]
    if candidate_source:
        candidate_out=ROOT/'verification/native-actor-source-candidate-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
        candidate_out.mkdir(parents=True);nd=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
        includes=re.findall(r'^\s*#\s*include\s*[<\"]([^>\"]+)[>\"]',candidate_source.read_text(),re.M)
        if any(name not in ['actor-group-native-api.h','stdint.h']for name in includes):
            failure=dict(status='terminal_actor_source_candidate_include_rejected',directory=str(candidate_out),source=str(candidate_source),source_sha256=sha(candidate_source),error='Candidate may include only the supplied native API header and stdint.h',includes=includes)
            save(candidate_out/'protocol.json',failure);save(ROOT/'verification/native-actor-source-group-checks-active.json',failure)
            raise AssertionError(failure['error'])
        command=['make','-f',str(nd/'Makefile.actor-group-candidate'),'actor-group-candidate','BUILD='+str(candidate_out),'NATIVE_SOURCE='+str(candidate_source)]
        result=subprocess.run(command,capture_output=True,text=True);(candidate_out/'build.log').write_text(result.stdout+result.stderr)
        if result.returncode:
            failure=dict(status='terminal_actor_source_candidate_compile_failed',directory=str(candidate_out),source=str(candidate_source),source_sha256=sha(candidate_source),error=result.stderr)
            save(candidate_out/'protocol.json',failure);save(ROOT/'verification/native-actor-source-group-checks-active.json',failure)
            raise AssertionError(result.stderr)
        build=dict(directory=str(candidate_out),binary=str(candidate_out/'actor-group-source.bin'),ELF=str(candidate_out/'actor-group-source.elf'))
        prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-')
        (candidate_out/'symbols.txt').write_text(subprocess.check_output([prefix+'nm','-n',build['ELF']],text=True))
        assert not subprocess.check_output([prefix+'nm','-u',build['ELF']],text=True).strip()
        candidate_inputs=[candidate_source,nd/'actor-group-native-api.h',nd/'Makefile.actor-group-candidate']
        save(candidate_out/'protocol.json',dict(status='compiled_candidate_only_no_original_body_linked',source=str(candidate_source),command=command,**build))
    payload=Path(build['binary']).read_bytes()
    if not candidate_source:assert len(payload)==4596
    assert 0<len(payload)<ARGV-BASE
    symbols={fields[2]:int(fields[0],16)for line in (Path(build['directory'])/'symbols.txt').read_text().splitlines()
             if len(fields:=line.split())==3}
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
    assert sha(ROOT/'render-assets/biwn-inventory-baseline.bin')=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3'
    out=ROOT/'verification/native-actor-source-group-checks'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True);print(out,flush=True)
    allcases=cases();vectors=allcases
    if args.limit:vectors=[row for entry in prior.RANGES for row in [x for x in allcases if x['entry']==entry][:args.limit]]
    save(out/'fixtures.json',vectors)
    sources=[Path(__file__),Path(prior.__file__),bp,Path(build['binary']),Path(build['ELF']),
             ROOT/'projects/black-ice-white-noise/restoration/biwn_actor_creation.c',
             ROOT/'projects/black-ice-white-noise/restoration/biwn_actor_creation.h',
             ROOT/'projects/black-ice-white-noise/restoration/biwn_world_update.h',
             *[ROOT/'projects/black-ice-white-noise/restoration/native-m68k'/name for name in
               ['actor-group-source.c','actor-group-source.ld','Makefile.actor-group-source']]]
    sources.extend(candidate_inputs)
    hashes={str(p):sha(p)for p in sources};state=dict(status='checking_coupled_native_actor_source_group',pid=os.getpid(),directory=str(out),
        planned=len(vectors),completed=0,candidate_source=str(candidate_source)if candidate_source else None,candidate_original_body_linked=False if candidate_source else True,source_sha256=hashes,new_training=False,new_model_predictions=0,disc_integrated=False)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-actor-source-group-checks-active.json',state)
    mark();rows=[];coverage=set();totals=Counter()
    try:
        for i,case in enumerate(vectors):
            left=execute(snapshot,case,payload,symbols,False);right=execute(snapshot,case,payload,symbols,True)
            if left['D0']!=right['D0']or left['RAM']!=right['RAM']or left['trace']!=right['trace']:
                save(out/'mismatch.json',dict(index=i,case=case,original_D0=left['D0'],compiled_D0=right['D0'],
                    original_trace=left['trace'],compiled_trace=right['trace'],RAM_differences=[hex(j)for j,(a,b)in enumerate(zip(left['RAM'],right['RAM']))if a!=b][:32]))
                raise AssertionError('Coupled source group mismatch')
            coverage.update(left['coverage']);totals.update(right['counts'])
            rows.append(dict(index=i,entry=hex(case['entry']),D0=right['D0'],public_events=len(right['trace']),
                             original_steps=left['counts']['steps'],compiled_steps=right['counts']['steps'],
                             original_private_depth=left['private_depth'],compiled_private_depth=right['private_depth']))
            if i%128==0:state['completed']=len(rows);mark();print('Coupled source group',len(rows),'/',len(vectors),flush=True)
        assert all(sha(p)==h for p,h in hashes.items()),'Source or build changed during checking'
        save(out/'results.json',rows)
        state.update(status='terminal_actor_source_group_preflight_pass'if args.limit else'terminal_coupled_target_compiled_actor_source_group_pass',
            cases=len(rows),counts=dict(totals),original_instruction_addresses=sorted(coverage),binary_bytes=len(payload),binary=build['binary'],ELF=build['ELF'],
            max_compiled_private_depth=max(x['compiled_private_depth']for x in rows),
            scope='Five-member group closes internal calls in complete original68000 bodies versus target-compiled high-level C. Full logical D0, public2MBRAM, ordered reads/writes, group call/return D0 and prescribed external-helper args/D0/effects; root C callee saves/RTS/args and immutable text checked. Four remaining helpers102C4/DF6C/152A2/E2B8 are scripted on both sides. New source-owned C ABI, not original volatile-register/SR/stack ABI. Declared code/argv/service-stub/private8KBstack exclusions. Selected validRAM fixtures and added coupled geometry cases; no arbitrary faults/aliases/helper ABI/device concurrency, disc, gameplay, physical-console or full-game proof.')
        mark()
        if not args.limit:save(ROOT/'verification/native-actor-source-group-checks-current.json',state)
        print(json.dumps({k:state[k]for k in ['status','cases','binary_bytes','max_compiled_private_depth']}))
    except BaseException as error:
        state.update(status='terminal_actor_source_group_failed',error=repr(error),completed=len(rows));mark();raise


if __name__=='__main__':main()
