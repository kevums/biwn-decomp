"""Retained native 68000 replay of complete original/source-owned actor group.

Unicorn supplies instruction-order and declared read-queue injection schedules.
Native executes every algorithm instruction independently. Only the four named
external services are prescribed; native call args/D0 are checked at each call.
Public RAM and logical D0 are compared at return. This does not independently
observe native bus transactions or establish the original volatile/SR ABI.
"""
import argparse,json,os
from datetime import datetime,timezone
from pathlib import Path
from collections import Counter
import check_biwn_actor_source_group_v3 as g
from check_biwn_scheduler import Native
ROOT=g.ROOT

def replay(native,snapshot,case,payload,symbols,compiled,expected):
    memory=bytearray(snapshot)
    if compiled:
        memory[g.BASE:g.BASE+len(payload)]=payload;memory[g.EXTERNAL:g.EXTERNAL+2]=b'\x4e\x75'
    script=g.prior.Script(memory,case);memory=bytearray(script.memory)
    if compiled:
        argv=b''.join(v.to_bytes(4,'big')for v in case['params']);memory[g.ARGV:g.ARGV+len(argv)]=argv
        memory[g.OUTPUT:g.OUTPUT+4]=b'\xa5\x5a\xa5\x5a'
        params=b''.join(v.to_bytes(4,'big')for v in [case['entry'],g.ARGV,case['incoming'][0],g.OUTPUT])
        entry=symbols['biwn_actor_group_invoke']
    else:
        params=b''.join(v.to_bytes(w,'big')for v,w in zip(case['params'],g.prior.WIDTHS[case['entry']]))
        entry=case['entry']
        for address in g.SERVICES:memory[address:address+2]=b'\x4e\x75'
    memory[g.SP:g.SP+4+len(params)]=g.STOP.to_bytes(4,'big')+params
    native.device.seed(bytes(memory),0);lib=native.lib;lib.m68k_pulse_reset();lib.m68k_set_irq(0)
    for sr,sp in [(0x2000,g.SP if case['sr']&0x2000 else 0x1fd000),(0,g.SP if not case['sr']&0x2000 else 0x1fc000)]:
        lib.m68k_set_reg(17,sr);lib.m68k_set_reg(15,sp)
    lib.m68k_set_reg(17,case['sr'])
    for i,value in enumerate(case['incoming']):lib.m68k_set_reg(i,value)
    lib.m68k_set_reg(15,g.SP);lib.m68k_set_reg(16,entry)
    def reg(i):return lib.m68k_get_reg(None,i)
    totals=Counter()
    for ordinal,step in enumerate(expected['machine']):
        pc=reg(16);assert pc==step['pc'],('native instruction stream',ordinal,hex(pc),hex(step['pc']))
        injected={}
        for a,w,v in step['queue_injections']:
            assert (a,w)not in injected or injected[a,w]==v,'Multiple distinct same-instruction queue values unsupported'
            injected[a,w]=v;native.device.direct(a,w,v);totals['queue_injections']+=1
        if 'service'in step:
            service=step['service'];ram=native.device.ram();stack=reg(15)
            def word(a,w=4):return int.from_bytes(ram[a:a+w],'big')
            if compiled:
                target,argv,n,out=[word(stack+i)for i in [4,8,12,16]]
                assert target in g.SERVICES and n==len(g.prior.WIDTHS[target])
                args=[word(argv+4*i)for i in range(n)];incoming=word(out)
            else:
                target=pc;args=[];offset=4
                for w in g.prior.WIDTHS[target]:args.append(word(stack+offset,w));offset+=w
                incoming=reg(0)
            assert [target,args,incoming]==[service['target'],service['args'],service['incoming']],('native external call mismatch',ordinal)
            for a,w,v in service['effects']:native.device.direct(a,w,v)
            if compiled:native.device.direct(out,4,service['result']);lib.m68k_set_reg(0,0)
            else:lib.m68k_set_reg(0,service['result'])
            totals['external_services']+=1
        lib.m68k_execute(1);totals['instructions']+=1
    assert reg(16)==g.STOP and reg(15)==g.SP+4,('native return',hex(reg(16)),hex(reg(15)))
    assert all(reg(i)==v for i,v in enumerate(case['incoming'])if i not in [0,1,8,9]),'Native C callee saves'
    ram=bytearray(native.device.ram());assert ram[g.SP+4:g.SP+4+len(params)]==params,'Native root args'
    if compiled:
        assert reg(0)==0,'Native source API status'
        d0=int.from_bytes(ram[g.OUTPUT:g.OUTPUT+4],'big')
        assert ram[g.BASE:g.BASE+len(payload)]==payload,'Native source text changed'
    else:
        d0=reg(0)
        for address in g.SERVICES:ram[address:address+2]=script.memory[address:address+2]
    for lo,hi in [(g.BASE,g.BASE+len(payload)),(g.ARGV,g.OUTPUT+4),(g.EXTERNAL,g.EXTERNAL+2),(g.SP-8192,g.SP+64)]:ram[lo:hi]=snapshot[lo:hi]
    assert d0==expected['D0'],('Native logical D0',hex(d0),hex(expected['D0']))
    assert ram==expected['RAM'],('Native public RAM',[(hex(i),a,b)for i,(a,b)in enumerate(zip(ram,expected['RAM']))if a!=b][:20])
    return dict(totals)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--proof',type=Path,default=ROOT/'verification/native-actor-source-group-reference-current.json');ap.add_argument('--limit',type=int);args=ap.parse_args()
    proof=g.read(args.proof);assert proof['status']=='terminal_coupled_target_compiled_actor_source_group_pass'
    binary=Path(proof.get('binary')or next(p for p in proof['source_sha256']if p.endswith('/actor-group-source.bin')));elf=Path(proof.get('ELF')or next(p for p in proof['source_sha256']if p.endswith('/actor-group-source.elf')));payload=binary.read_bytes()
    symbols={x[2]:int(x[0],16)for line in (elf.parent/'symbols.txt').read_text().splitlines()if len(x:=line.split())==3}
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=g.cases()
    if args.limit:vectors=[row for entry in g.prior.RANGES for row in [x for x in vectors if x['entry']==entry][:args.limit]]
    out=ROOT/'verification/native-actor-group-replay'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    sources=[Path(__file__),Path(g.__file__),Path(g.prior.__file__),args.proof,binary,elf,ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'scripts/check_biwn_scheduler.py']
    hashes={str(p):g.sha(p)for p in sources};state=dict(status='running_native_actor_group_replay',pid=os.getpid(),directory=str(out),planned=len(vectors),completed=0,source_sha256=hashes,disc_integrated=False,new_model_predictions=0)
    def mark():g.save(out/'protocol.json',state);g.save(ROOT/'verification/native-actor-group-replay-active.json',state)
    mark();g.save(out/'fixtures.json',vectors);rows=[];totals=Counter();native=Native()
    try:
        for i,case in enumerate(vectors):
            left=g.execute(snapshot,case,payload,symbols,False);right=g.execute(snapshot,case,payload,symbols,True)
            assert all(left[k]==right[k]for k in ['D0','RAM','trace'])
            a=replay(native,snapshot,case,payload,symbols,False,left);b=replay(native,snapshot,case,payload,symbols,True,right)
            rows.append(dict(index=i,entry=hex(case['entry']),original=a,compiled=b));totals.update(b)
            if i%64==0:state['completed']=len(rows);mark();print('Native coupled group',len(rows),'/',len(vectors),flush=True)
        assert all(g.sha(Path(p))==h for p,h in hashes.items())
        g.save(out/'results.json',rows);state.update(status='terminal_native_actor_group_replay_preflight_pass'if args.limit else'terminal_native_actor_group_replay_pass',completed=len(rows),cases=len(rows),compiled_totals=dict(totals),scope=__doc__)
        mark()
        if not args.limit:g.save(ROOT/'verification/native-actor-group-replay-current.json',state)
        print(state['status'],len(rows),flush=True)
    except BaseException as error:state.update(status='terminal_native_actor_group_replay_failed',completed=len(rows),error=repr(error));mark();raise
    finally:native.close()

if __name__=='__main__':main()
