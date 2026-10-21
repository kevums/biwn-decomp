"""Original 10520/105DA versus one native typed C kernel, full public state/order."""
import argparse
import json
import os
import random
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import check_biwn_native_doorway as engine

ROOT = Path(__file__).resolve().parents[1]
ND = ROOT / 'projects/black-ice-white-noise/restoration/native-m68k'
BASE = 0x180000  # Dense 32768*24 fixture at A0000 ends at 160000.
SP, STOP = 0x1e0000, 0x1f0000
RANGES = {0: (0x10520, 0x105da), 1: (0x105da, 0x10652)}
sha, save = engine.sha, engine.save


def vectors():
    rng = random.Random(0x10520105da)
    rows = []
    patterns = [(0,'none'),(0x8001,'none'),(0xffff,'none'),(1,'highest'),
                (3,'highest'),(3,'lowest'),(3,'multiple'),(3,'none'),
                (1,'x_equal'),(1,'z_equal'),(1,'signed_wrap'),
                (2,'carry_retained'),(2,'carry_reset'),(1,'word_shift')]
    for kind in [0, 1]:
        for mode in [0, 0x2000]:
            for flags in range(32):
                for j, (count, pattern) in enumerate(patterns):
                    rows.append(dict(kind=kind, count=count, pattern=pattern,
                                     object=0x80000 + 2*(j%3), origin=[0x80000020,0xffffffc0],
                                     delta=[0,0], incoming=[rng.getrandbits(32) for _ in range(15)],
                                     sr=mode|flags))
        for tag in [0x80000000,0xff000000]:
            for alias in [None,0,2,20,30,42,44,48,52]:
                rows.append(dict(kind=kind,count=1,pattern='highest',object=0x80000|tag,
                                 origin=[0x80000020,0xffffffc0],delta=[0,0],header_tag=tag,
                                 record_tag=tag,record_alias=alias,
                                 incoming=[rng.getrandbits(32) for _ in range(15)],sr=0x201f))
        for j in range(64):
            rows.append(dict(kind=kind,count=rng.randrange(1,7),pattern='random',object=0x80000,
                             origin=[rng.getrandbits(32),rng.getrandbits(32)],
                             delta=[rng.getrandbits(32),rng.getrandbits(32)],
                             random_records=[[rng.randrange(65536) for _ in range(4)] for _ in range(6)],
                             incoming=[rng.getrandbits(32) for _ in range(15)],sr=(j%2)*0x2000|(j%32)))
        rows.append(dict(kind=kind,count=0x8000,pattern='long_none',object=0x80000,
                         origin=[0,0],delta=[0,0],incoming=[0x87654321]*15,sr=0x201f,
                         instruction_limit=3000000))
    return rows


def seed(image, c):
    b = bytearray(image)
    obj = c['object'] & 0xffffff
    header = 0x90000 | c.get('header_tag',0)
    records = (0xa0000 if c.get('record_alias') is None else obj+c['record_alias']) | c.get('record_tag',0)
    def put(a,w,v):
        a &= 0xffffff
        assert a+w <= len(b)
        b[a:a+w] = (v & ((1 << (8*w))-1)).to_bytes(w,'big')
    put(0x49c18,4,header)
    put(header,2,c['count']);put(header+4,4,records)
    put(obj+(4 if c['kind']==0 else 2),4,c['origin'][0]+c['delta'][0])
    put(obj+(10 if c['kind']==0 else 8),4,c['origin'][1]+c['delta'][1])
    put(obj+30 if c['kind']==0 else 0x49c6a,4,c['origin'][0])
    put(obj+38 if c['kind']==0 else 0x49c72,4,c['origin'][1])
    if not ((c['count']-1)&0x8000):
        row=bytearray(24)
        for off,v in [(2,16),(4,0),(6,16),(8,16)]:row[off:off+2]=v.to_bytes(2,'big')
        a=records&0xffffff;b[a:a+24*c['count']]=bytes(row)*c['count']
        for i in range(min(c['count'],8)):
            pattern=c['pattern'];values=[16,0,16,16]
            if pattern in ['highest','word_shift'] and i==c['count']-1:values=[0,0,16,16]
            if pattern in ['lowest','multiple'] and (i==0 or pattern=='multiple'):values=[0,0,16,16]
            if pattern=='x_equal':values=[0xffff,0,1,16]
            if pattern=='z_equal':values=[0,0xffff,16,1]
            if pattern=='signed_wrap':values=[0xffff,0xffff,2,2]
            if pattern=='carry_retained':values=[16,0,16,16] if i==0 else [0xffff,0,1,16]
            if pattern=='carry_reset':values=[0,0,0,16] if i==0 else [0xffff,0,1,16]
            if pattern=='word_shift':values=[0,0,16,0x400]
            if pattern=='random':values=c['random_records'][i]
            for off,v in zip([2,4,6,8],values):put(records+24*i+off,2,v)
    if c.get('secondary'):
        for i in range(2):
            for off,v in zip([2,4,6,8],[0,0,16,16]):put(0xb0000+24*i+off,2,v)
    put(SP,4,STOP);put(SP+4,4,c['object'])
    assert len(b)==0x200000
    return bytes(b)


def changing_vectors():
    rows=[]
    for kind in [0,1]:
        for mode in [0,0x2000]:
            for flags in range(32):
                for tag in [0,0xff000000]:
                    for variation in range(4 if kind==0 else 2):
                        c=dict(kind=kind,count=1,pattern='highest',object=0x80000|tag,
                               origin=[0,0],delta=[0,0],incoming=[0x80000000]*15,sr=mode|flags,
                               header_tag=tag,record_tag=tag)
                        record=0xa0000|tag
                        if variation==0:
                            c['read_queues']=[(record+2,2,[0,0,1] if kind==0 else [0,0xffff])]
                        elif variation==1:
                            c.update(count=2,pattern='lowest',secondary=True)
                            c['read_queues']=[(0x90004|tag,4,[record,0xb0000|tag])]
                        elif variation==2:c['read_queues']=[(record+8,2,[16,0x400])]
                        else:c['read_queues']=[((c['object']+38)&0xffffffff,4,[0,0xffffffff])]
                        rows.append(c)
    return rows


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--limit',type=int);parser.add_argument('--no-publish',action='store_true')
    args=parser.parse_args();source=args.source.resolve()
    out=ROOT/'verification/native-interior-select'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='building',pid=os.getpid(),directory=str(out),source=str(source),source_sha256=sha(source),
               source_accepted=False,game_frames=0,new_training=False,default_promoted=False,whole_game_complete=False)
    def mark():
        save(out/'protocol.json',state);save(ROOT/'verification/native-interior-select-active.json',state)
    mark();n=None
    try:
        paths=[Path(__file__),Path(engine.__file__),source,ND/'interior-select-native.h',
               ND/'interior-select-shim.S',ND/'Makefile.interior-select']
        snap=out/'source-snapshot';snap.mkdir()
        for p in paths:shutil.copy2(p,snap/p.name)
        command=['make','-f',str(ND/'Makefile.interior-select'),'interior-select','BUILD='+str(out/'build'),
                 'INTERIOR_SOURCE='+str(source),'ADDRESS='+hex(BASE)]
        result=subprocess.run(command,capture_output=True,text=True)
        (out/'build.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
        binary=out/'build/interior-select.bin';payload=binary.read_bytes()
        assert len(payload)<0x10000
        prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-')
        nm=subprocess.check_output([prefix+'nm','-n',str(out/'build/interior-select.elf')],text=True)
        symbols={p[2]:int(p[0],16)for line in nm.splitlines()if len(p:=line.split())==3}
        baseline=ROOT/'render-assets/biwn-inventory-baseline.bin'
        assert sha(baseline)=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3'
        image=baseline.read_bytes();candidate=bytearray(image);candidate[BASE:BASE+len(payload)]=payload
        for kind,name in [(0,'biwn_native_interior_actor_select'),(1,'biwn_native_interior_sprite_select')]:
            entry=RANGES[kind][0];candidate[entry:entry+8]=b'\x4e\xf9'+symbols[name].to_bytes(4,'big')+b'\x4e\x71'
        engine.BASE=BASE;engine.SP=SP;engine.STOP=STOP;engine.seed=seed
        # The two redirections are part of the test installation, not public-state differences.
        def normalize(ram,reference,length):
            b=bytearray(ram)
            for lo,hi in [(BASE,BASE+length),(SP-8192,SP)]+[(a,a+8)for a,_ in RANGES.values()]:
                b[lo:hi]=reference[lo:hi]
            return bytes(b)
        cases=vectors();cases=cases[:args.limit]if args.limit else cases
        dynamic=changing_vectors() if not args.limit else []
        save(out/'fixtures.json',cases);save(out/'changing-fixtures.json',dynamic)
        n=engine.Native();rows=[];changing=[];coverage={0:set(),1:set()};minimum=SP
        state.update(status='checking_native_CPU_RAM_ordered',planned=len(cases),planned_changing=len(dynamic));mark()
        for stable,group,output in [(True,cases,rows),(False,dynamic,changing)]:
            for index,c in enumerate(group):
                engine.ENTRY,engine.END=RANGES[c['kind']]
                x=engine.trace(image,c,len(payload),True);y=engine.trace(candidate,c,len(payload),False)
                if x[1]!=y[1] or normalize(y[0],x[0],len(payload))!=x[0]:
                    save(out/'ordered-mismatch.json',dict(stable=stable,case=index,parameters=c,original=x[1],candidate=y[1]))
                    raise AssertionError(('ordered accesses/public RAM',stable,index))
                left=engine.native(n,image,c,len(payload),True,x[2]);right=engine.native(n,candidate,c,len(payload),False,y[2])
                normalized=normalize(right[0],left[0],len(payload))
                if left[1]!=right[1] or normalized!=left[0]:
                    save(out/'mismatch.json',dict(stable=stable,case=index,parameters=c,original_CPU=left[1],compiled_CPU=right[1],
                                                RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(left[0],normalized))if a!=b][:30]))
                    raise AssertionError(('full CPU/public RAM',stable,index))
                assert normalize(left[0],x[0],len(payload))==x[0],('original native/tracer RAM',stable,index)
                assert normalize(right[0],y[0],len(payload))==y[0],('compiled native/tracer RAM',stable,index)
                assert right[0][BASE:BASE+len(payload)]==payload
                coverage[c['kind']].update(left[2]);minimum=min(minimum,right[5])
                output.append(dict(case=index,kind=c['kind'],CPU=right[1],ordered_events=len(x[1]),
                                   original_steps=left[3],compiled_steps=right[3],original_cycles=left[4],compiled_cycles=right[4]))
                if index%256==0:
                    state.update(stable_completed=len(rows),changing_completed=len(changing));mark()
                    print('Stable'if stable else'Changing',index+1,'/',len(group),flush=True)
        locations={}
        for kind,(start,end)in RANGES.items():
            assembly=subprocess.check_output([prefix+'objdump','-D','-b','binary','-m','m68k:68000',
                                               '--start-address='+hex(start),'--stop-address='+hex(end),str(baseline)],text=True)
            (out/f'original-{start:x}.asm').write_text(assembly)
            pcs={int(line.split(':',1)[0].strip(),16)for line in assembly.splitlines()
                 if ':'in line and len(line.split('\t'))>=3 and line.split('\t')[2].strip()}
            locations[str(kind)]=[len(pcs&coverage[kind]),len(pcs)]
            if not args.limit:assert pcs<=coverage[kind],('uncovered',kind,sorted(pcs-coverage[kind]))
        save(out/'results.json',rows);save(out/'changing-results.json',changing)
        state.update(status='terminal_native_interior_select_preflight_pass'if args.limit else'terminal_native_interior_select_CPU_RAM_ordered_pass',
                     source_accepted=not args.limit,stable_cases=len(rows),changing_cases=len(changing),
                     original_instruction_coverage=locations,binary=str(binary),binary_sha256=sha(binary),
                     binary_bytes=len(payload),symbols=symbols,max_private_stack_bytes=SP-minimum,
                     dependencies_sha256={str(p):sha(p)for p in paths},
                     scope='Complete original10520/105DA native ABI and logical ordered public accesses. Full retained-native CPU D/A/PC/SR/USP/SSP plus public2MBRAM; width-correct changing reads and native/tracer publicRAM agreement. Private8KBstack, two entry patches and isolated code180000 excluded. Dense32768*24 fixture ends160000 and cannot overwritecode. Bounded fixtures, no arbitraryfault/IRQ/cycle equivalence, final-link/disc/gameplay/physical/full-game proof. Not a new logical-function recovery or model-training gain.')
        mark()
        if not args.no_publish and not args.limit:save(ROOT/'verification/native-interior-select-current.json',state)
        print(json.dumps({k:state[k]for k in ['status','stable_cases','changing_cases','binary_bytes','original_instruction_coverage']}))
    except BaseException as error:
        state.update(status='terminal_failed',error=repr(error));mark();raise
    finally:
        if n:n.close()


if __name__=='__main__':main()
