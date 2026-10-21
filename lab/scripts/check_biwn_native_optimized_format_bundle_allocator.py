"""Acquire linked to actual source-built allocator; controlled loader/scheduler.
Non-compacting allocation layouts only. No CD/game/real-scheduler proof.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,os,subprocess
import check_biwn_native_optimized_format_bundle_acquire as a
import check_biwn_memory as memory
from check_biwn_native_button_digit import ROOT,sha,save
HEAP=0x15edc0

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path);p.add_argument('--limit',type=int);args=p.parse_args()
    nd=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';source=(args.source or nd/'resource-acquire-reference.c').resolve()
    proofpath=ROOT/'verification/native-optimized-format-bundle-heap-current.json';proof=json.loads(proofpath.read_text());assert proof['source_accepted']and proof['native_cases']==3392
    hp=Path(proof['compiled_binary']);assert sha(hp)==proof['compiled_binary_sha256'];heap=hp.read_bytes()
    out=ROOT/'verification/native-optimized-format-bundle-allocator'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),source=str(source),source_sha256=sha(source),coordinator_reference=source==nd/'resource-acquire-reference.c',source_accepted=False,real_allocator_verified=False,real_loader_verified=False,real_scheduler_verified=False,whole_game_complete=False,game_frames=0,limit=args.limit)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-optimized-format-bundle-allocator-active.json',state)
    mark()
    try:
        build=out/'build';r=subprocess.run(['make','-f','/Users/kevin/Documents/Codex/2026-10-10/i-now-am-using-the-following/outputs/local-ai-lab/verification/native-format-optimization-builds/20261018T160621.790163Z/O2-lean/Makefile','format-bundle','BUILD='+str(build),'ACQUIRE_SOURCE='+str(source)],cwd=nd,capture_output=True,text=True);(out/'make.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
        rp=subprocess.run(['make','-f','Makefile.resource-acquire','BUILD='+str(build),str(build/'acquire-providers.bin')],cwd=nd,capture_output=True,text=True)
        (out/'providers-make.log').write_text(rp.stdout+rp.stderr);assert rp.returncode==0,rp.stderr
        prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');symbols={}
        for stem in ['native-format-bundle','acquire-providers']:
            for line in subprocess.check_output([prefix+'nm','--defined-only',str(build/(stem+'.elf'))],text=True).splitlines():
                t=line.split()
                if len(t)==3:symbols[t[2]]=int(t[0],16)
        save(out/'symbols.json',symbols);binary=build/'native-format-bundle.bin';payload=binary.read_bytes();providers=(build/'acquire-providers.bin').read_bytes()
        assert sha(binary)=='533c10742617e8596c0ce2dc32e7676d137a9fbbc463b29bb86e0db41fd0ca19', "Wrong linked bundle"
        baseline=ROOT/'render-assets/biwn-inventory-baseline.bin';assert sha(baseline)=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3'
        image=bytearray(baseline.read_bytes());image[a.PROVIDER:a.PROVIDER+len(providers)]=providers
        for addr,(name,_)in a.HELPERS.items():
            if name!='allocate':image[addr:addr+8]=b'\x4e\xf9'+symbols['acquire_provider_'+name].to_bytes(4,'big')+b'\x4e\x71'
        candidate=bytearray(image);candidate[a.BASE:a.BASE+len(payload)]=payload;candidate[HEAP:HEAP+len(heap)]=heap
        for addr,target in [(a.ENTRY,symbols['biwn_native_resource_acquire']),(0x152a2,proof['symbols']['biwn_native_heap_allocate'])]:candidate[addr:addr+8]=b'\x4e\xf9'+target.to_bytes(4,'big')+b'\x4e\x71'
        oldallowed=a.allowed
        def allowed(pc,length,plen,original):
            return oldallowed(pc,length,plen,original)or(0x152a2<=pc<0x1545c if original else HEAP<=pc<HEAP+len(heap))
        a.allowed=allowed
        def normalize(ram,ref):
            b=a.normalize(ram,ref,len(payload));b[HEAP:HEAP+len(heap)]=ref[HEAP:HEAP+len(heap)];b[0x152a2:0x152aa]=ref[0x152a2:0x152aa];return b
        base=[x for x in a.vectors()if x['kind']=='miss_first'and x['profile']==0];cases=[]
        for kind in [0,1,2,3,4,8]:
            for v in base:
                ident=v['id'];desc=0x464d0+(ident if ident<32768 else ident-65536)*12
                ccr=v['sr']&31;free=[0,25,49][ccr%3];init=list(v['initial'])
                init += [[0x15b534+6,2,1],[0x15b534+free*12+6,2,0],[desc+8,4,256],[0x13000e,2,3 if ccr&1 else 1]]
                init += memory.allocation_initial(kind,256,None if kind==8 else[0,127,255][ccr%3])
                cases.append({**v,'kind':'actual_allocator_'+str(kind),'allocation_layout':kind,'cache_slot':free,'initial':init})
        if args.limit:cases=[next(x for x in cases if x['allocation_layout']==k)for k in [0,1,2,3,4,8]][:args.limit]
        save(out/'fixtures.json',cases);n=a.sched.Native();rows=[];coverage=set()
        try:
            for i,c in enumerate(cases):
                left=a.native(n,image,c,len(payload),len(providers),True);right=a.native(n,candidate,c,len(payload),len(providers),False)
                norm=normalize(right[0],left[0])
                if left[1]!=right[1]or left[3]!=right[3]or norm!=left[0]:
                    save(out/'mismatch.json',dict(case=i,parameters=c,original_CPU=left[1],compiled_CPU=right[1],original_calls=left[3],compiled_calls=right[3],RAM_differences=[dict(address=hex(j),original=x,compiled=y)for j,(x,y)in enumerate(zip(left[0],norm))if x!=y][:64]));raise AssertionError(str(out/'mismatch.json'))
                ta=a.trace(image,c,len(payload),len(providers),True);tb=a.trace(candidate,c,len(payload),len(providers),False)
                if ta[1:]!=tb[1:]or normalize(tb[0],ta[0])!=ta[0]:save(out/'trace-mismatch.json',dict(case=i,original=ta[1:],compiled=tb[1:]));raise AssertionError(str(out/'trace-mismatch.json'))
                assert 0x15200 not in left[2]and 0x15200 not in right[2]
                hits=right[2].count(proof['symbols']['biwn_native_heap_allocate_body']);assert hits==1
                assert not any(0x152a2<pc<0x1545c for pc in right[2])
                assert right[0][HEAP:HEAP+len(heap)]==heap and right[0][a.BASE:a.BASE+len(payload)]==payload
                handle=right[1]['registers'][0]
                if c['allocation_layout']!=8:
                    assert 0x112960<=handle<0x112d60 and handle%4==0
                    pointer=int.from_bytes(right[0][handle:handle+4],'big');assert 0x1bf008<=pointer<0x1c0000
                else:assert handle==0
                coverage.update(left[2]);rows.append(dict(case=i,kind=c['kind'],sr=c['sr'],cache_slot=c['cache_slot'],returned_handle=handle,compiled_allocator_body_hits=hits,CPU=right[1],calls=right[3],ordered_events=len(ta[2]),full_CPU_public_RAM_and_ordered_access_match=True))
                if i%64==0:state['completed']=len(rows);mark();print('Actual allocator',len(rows),'/',len(cases),flush=True)
        finally:n.close();a.allowed=oldallowed
        save(out/'results.json',rows)
        paths=[Path(__file__),Path(a.__file__),ROOT/'scripts/check_biwn_memory.py',ROOT/'scripts/check_biwn_scheduler.py',source,proofpath,hp,baseline,*[nd/k for k in ['resource-acquire-native.h','resource-acquire-shim.S','resource-acquire-providers.S','resource-acquire.ld','Makefile.resource-acquire','Makefile']]]
        state.update(status='terminal_actual_allocator_acquire_preflight_pass'if args.limit else'terminal_actual_allocator_acquire_CPU_RAM_ordered_access_pass',real_allocator_verified=not args.limit,native_cases=len(rows),trace_cases=len(rows),compiled_allocator_body_hits=sum(x['compiled_allocator_body_hits']for x in rows),compiled_binary=str(binary),compiled_binary_sha256=sha(binary),binary_bytes=len(payload),original_instruction_coverage=sorted(coverage),artifacts_sha256={str(q):sha(q)for q in paths},scope='Original acquire+original allocator versus compiled acquire+verified source-built allocator. Head/middle split/whole allocation, handle exhaustion, 3cache positions, user/supervisor/all32CCR; fullCPU/publicRAM and separateorderedaccess match. Loader/wait/signal are controlledtarget68000providers. No compaction/copy/device, realCDloader/scheduler/concurrency, linkedresident/disc/game or physical-console proof.')
        mark();save(ROOT/'verification/native-optimized-format-bundle-allocator-current.json',state);print(state['status'],len(rows),flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
