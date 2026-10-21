"""Acquire 1AF04: native ABI/public RAM and ordered access component checks.
Controlled target-CPU providers are declared fixtures, not real game I/O.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, random, subprocess
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_scheduler as sched
from check_biwn_native_button_digit import ROOT, sha, save
from check_biwn_native_resource_release import REGS
BASE, PROVIDER, ENTRY, END, SP, STOP = 0x15edc0, 0x144000, 0x1af04, 0x1b002, 0x1e0000, 0x1f0000
HELPERS = {0xdf8c: ('wait', 1), 0x152a2: ('allocate', 1), 0x1b044: ('load', 5), 0xdf9c: ('signal', 1)}

def private(a, w): return SP-8192 <= a and a+w <= SP-24

def normalize(ram, ref, length):
    b=bytearray(ram)
    for a,z in [(BASE,length),(ENTRY,8),(SP-8192,8192-24)]: b[a:a+z]=ref[a:a+z]
    return b

def seed(image, case):
    b=bytearray(image)
    b[0x130000:0x132000]=bytes(0x2000)
    for a,w,v in case['initial']: b[a:a+w]=v.to_bytes(w,'big')
    b[SP:SP+4]=STOP.to_bytes(4,'big'); b[SP+4:SP+6]=case['id'].to_bytes(2,'big')
    return bytes(b)

def allowed(pc, length, plen, original):
    return pc in HELPERS or PROVIDER<=pc<PROVIDER+plen or (ENTRY<=pc<END if original else pc==ENTRY or BASE<=pc<BASE+length)

def native(n,image,case,length,plen,original):
    n.device.seed(seed(image,case),0); l=n.lib; l.m68k_pulse_reset(); l.m68k_set_irq(0)
    l.m68k_set_reg(17,0x2000); l.m68k_set_reg(15,SP if case['sr']&0x2000 else 0x1fc000)
    l.m68k_set_reg(17,0); l.m68k_set_reg(15,0x1fd000 if case['sr']&0x2000 else SP); l.m68k_set_reg(17,case['sr'])
    for i,v in enumerate(case['incoming']+[SP]): l.m68k_set_reg(i,v)
    l.m68k_set_reg(16,ENTRY); pcs=[]; calls=[]; cycles=0
    for _ in range(100000):
        pc=l.m68k_get_reg(None,16)
        if pc==STOP: break
        assert allowed(pc,length,plen,original),hex(pc)
        if pc in HELPERS:
            name,argc=HELPERS[pc]; stack=l.m68k_get_reg(None,15)
            calls.append([name,*[n.device.read(stack+4+4*i,4)for i in range(argc)]])
        pcs.append(pc); cycles+=l.m68k_execute(1)
    else: raise AssertionError('Acquire did not return')
    cpu=dict(registers=[l.m68k_get_reg(None,i)for i in range(16)],PC=l.m68k_get_reg(None,16),SR=l.m68k_get_reg(None,17))
    cpu['usp']=n.prefix[16]if cpu['SR']&0x2000 else cpu['registers'][15]
    cpu['ssp']=cpu['registers'][15]if cpu['SR']&0x2000 else n.prefix[17]
    assert cpu['registers'][15]==SP+4
    return n.device.ram(),cpu,pcs,calls,cycles

def trace(image,case,length,plen,original):
    u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    u.mem_map(0,0x200000);u.mem_write(0,seed(image,case));u.reg_write(UC_M68K_REG_SR,case['sr'])
    for reg,v in zip(REGS,case['incoming']+[SP]):u.reg_write(reg,v)
    events=[]
    def code(e,a,w,_):
        assert allowed(a,length,plen,original),hex(a)
        if a in HELPERS:
            name,argc=HELPERS[a];stack=e.reg_read(UC_M68K_REG_A7)
            events.append([name,*[int.from_bytes(e.mem_read(stack+4+4*i,4),'big')for i in range(argc)]])
    def read(e,t,a,w,v,_):
        if not private(a,w):events.append(['read',a,w,int.from_bytes(e.mem_read(a,w),'big')])
    def write(e,t,a,w,v,_):
        if not private(a,w):events.append(['write',a,w,v&((1<<(8*w))-1)])
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write)
    u.emu_start(ENTRY,STOP,count=100000,timeout=3000000)
    assert u.reg_read(UC_M68K_REG_PC)==STOP and u.reg_read(UC_M68K_REG_A7)==SP+4
    return bytes(u.mem_read(0,0x200000)),[u.reg_read(r)for r in REGS],events

def vectors():
    rng=random.Random(0x1af04); cases=[]
    kinds=['descriptor_zero','hit_first','hit_last','hit_null','hit_overflow','hit_signed_overflow','hit_wait','hit_wait_three','duplicate','inactive_match','miss_first','miss_middle','miss_last','full','alloc_zero','load_refs_zero','load_refs_many','load_handle','load_null_handle','signal_handle','allocator_descriptor_size','allocator_descriptor_word0','allocator_descriptor_word1','wait_handle']
    for kind in kinds:
        for mode in [0,0x2000]:
            for profile in [0,1]:
                for ccr in range(32):
                    ident=[0,1,15,0x7fff,0xffff][ccr%5]
                    desc=0x464d0+(ident if ident<32768 else ident-65536)*12
                    hit=kind.startswith('hit') or kind in ['duplicate','wait_handle']
                    slot=49 if kind=='hit_last'else 0
                    free=25 if kind=='miss_middle'else 49 if kind=='miss_last'else 0
                    entry=0x15b534+(slot if hit else free)*12
                    initial=[[desc,4,0 if kind=='descriptor_zero'else 0x10203040],[desc+4,4,0x50607080],[desc+8,4,0x100]]
                    if ident==0xffff:initial.append([0x464d0+ident*12,4,0])
                    for i in range(50):
                        a=0x15b534+i*12;match=hit and(i==slot or kind=='duplicate'and i==49)
                        ref=0xffff if kind=='hit_overflow'and match else 0x7fff if kind=='hit_signed_overflow'and match else 1
                        if not hit and kind!='full'and i==free:ref=0
                        if kind=='inactive_match'and i==0:match=True;ref=0
                        ready=0 if kind in ['hit_wait','hit_wait_three','wait_handle']and match else 1
                        initial += [[a,2,ident if match else(ident+1)&65535],[a+2,4,0 if kind=='hit_null'and match else 0x110000+i*4],[a+6,2,ref],[a+8,2,ready],[a+10,2,rng.getrandbits(16)]]
                    initial += [[0x130000,4,0 if kind=='alloc_zero'else 0x115000],[0x130004,4,entry+8],[0x130008,2,3 if kind=='hit_wait_three'else 1],[0x13000c,2,0x8000 if ccr&1 else 1],[0x13000e,2,0 if kind=='load_refs_zero'else 3 if kind in ['load_refs_many','signal_handle']else 1],[0x130010,2,1],[0x130014,2,int(kind in ['load_handle','load_null_handle'])],[0x130018,4,0 if kind=='load_null_handle'else 0x119900],[0x13003c,2,ccr],[0x13003e,2,profile],[0x130040,4,0xa5a5a5a5],[0x130044,4,0x12345678],[0x130048,4,0x87654321],[0x130054,4,0xcafebabe],[0x130058,4,0xdeadbeef],[0x13005c,4,0xfedcba98]]
                    for label,offset,address,value in [('allocator_descriptor_size',0x20,desc+8,0x204),('allocator_descriptor_word0',0x20,desc,0x81828384),('allocator_descriptor_word1',0x20,desc+4,0x91929394),('wait_handle',0x28,entry+2,0x118800),('signal_handle',0x30,entry+2,0x117700)]:
                        if kind==label:initial += [[0x130000+offset,4,address],[0x130004+offset,4,value]]
                    cases.append(dict(kind=kind,id=ident,initial=initial,incoming=[rng.getrandbits(32)for _ in range(15)],sr=mode|ccr|((ccr%8)<<8),profile=profile))
    return cases

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path);p.add_argument('--limit',type=int);args=p.parse_args()
    nd=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';source=(args.source or nd/'resource-acquire-reference.c').resolve()
    reference=source==nd/'resource-acquire-reference.c'
    out=ROOT/'verification/native-load-scan-bundle-acquire'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),source=str(source),source_sha256=sha(source),coordinator_reference=reference,limit=args.limit,source_accepted=False,controlled_component_pass=False,real_dependencies_verified=False,whole_game_complete=False,game_frames=0)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-load-scan-bundle-acquire-active.json',state)
    mark()
    try:
        build=out/'build';r=subprocess.run(['make','-f','Makefile.load-scan-bundle','load-scan-bundle','BUILD='+str(build),'ACQUIRE_SOURCE='+str(source)],cwd=nd,capture_output=True,text=True)
        (out/'make.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
        rp=subprocess.run(['make','-f','Makefile.resource-acquire','BUILD='+str(build),str(build/'acquire-providers.bin')],cwd=nd,capture_output=True,text=True)
        (out/'providers-make.log').write_text(rp.stdout+rp.stderr);assert rp.returncode==0,rp.stderr
        prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');symbols={}
        for stem in ['native-load-scan-bundle','acquire-providers']:
            for line in subprocess.check_output([prefix+'nm','--defined-only',str(build/(stem+'.elf'))],text=True).splitlines():
                t=line.split()
                if len(t)==3:symbols[t[2]]=int(t[0],16)
            (out/(stem+'.asm')).write_text(subprocess.check_output([prefix+'objdump','-dr',str(build/(stem+'.elf'))],text=True))
        save(out/'symbols.json',symbols)
        binary=build/'native-load-scan-bundle.bin';payload=binary.read_bytes();providers=(build/'acquire-providers.bin').read_bytes()
        assert sha(binary)=='130639a231a37d872a52226927b30545cfef214f568377751de61897398d0c73', "Wrong linked bundle"
        baseline=ROOT/'render-assets/biwn-inventory-baseline.bin'
        assert sha(baseline)=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3'
        image=bytearray(baseline.read_bytes());image[PROVIDER:PROVIDER+len(providers)]=providers
        for addr,(name,_)in HELPERS.items():image[addr:addr+8]=b'\x4e\xf9'+symbols['acquire_provider_'+name].to_bytes(4,'big')+b'\x4e\x71'
        candidate=bytearray(image);candidate[BASE:BASE+len(payload)]=payload;candidate[ENTRY:ENTRY+8]=b'\x4e\xf9'+symbols['biwn_native_resource_acquire'].to_bytes(4,'big')+b'\x4e\x71'
        cases=vectors()
        if args.limit:cases=[next(c for c in cases if c['kind']==kind)for kind in dict.fromkeys(c['kind']for c in cases)][:args.limit]
        save(out/'fixtures.json',cases);n=sched.Native();rows=[];coverage=set()
        try:
            for i,case in enumerate(cases):
                left=native(n,image,case,len(payload),len(providers),True);right=native(n,candidate,case,len(payload),len(providers),False)
                norm=normalize(right[0],left[0],len(payload))
                if left[1]!=right[1]or left[3]!=right[3]or norm!=left[0]:
                    save(out/'mismatch.json',dict(case=i,parameters=case,original_CPU=left[1],compiled_CPU=right[1],original_calls=left[3],compiled_calls=right[3],RAM_differences=[dict(address=hex(j),original=x,compiled=y)for j,(x,y)in enumerate(zip(left[0],norm))if x!=y][:64]));raise AssertionError(str(out/'mismatch.json'))
                ta=trace(image,case,len(payload),len(providers),True);tb=trace(candidate,case,len(payload),len(providers),False)
                if ta[1:]!=tb[1:]or normalize(tb[0],ta[0],len(payload))!=ta[0]:
                    save(out/'trace-mismatch.json',dict(case=i,original=ta[1:],compiled=tb[1:]));raise AssertionError(str(out/'trace-mismatch.json'))
                assert right[0][BASE:BASE+len(payload)]==payload and right[0][PROVIDER:PROVIDER+len(providers)]==providers
                coverage.update(left[2]);rows.append(dict(case=i,kind=case['kind'],sr=case['sr'],profile=case['profile'],CPU=right[1],calls=right[3],original_cycles=left[4],compiled_cycles=right[4],ordered_events=len(ta[2]),ordered_trace_sha256=hashlib.sha256(json.dumps(ta[2]).encode()).hexdigest(),full_CPU_public_RAM_and_ordered_access_match=True))
                if i%64==0:state['completed']=len(rows);mark();print('Acquire',len(rows),'/',len(cases),flush=True)
        finally:n.close()
        save(out/'results.json',rows)
        packet_path=ROOT/'verification/native-resource-acquire-preflight-current.json'
        packet=json.loads(packet_path.read_text())
        expected={v['address']for v in packet['instructions']}
        assert hashlib.sha256(baseline.read_bytes()[ENTRY:END]).hexdigest()==packet['range_sha256']
        if not args.limit:assert expected<=coverage,sorted(hex(v)for v in expected-coverage)
        state['original_body_instruction_coverage']=[len(expected&coverage),len(expected)]
        state['execution_dependencies_sha256']={str(q):sha(q)for q in [Path(sched.__file__),ROOT/'scripts/check_biwn_native_resource_release.py',ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib',baseline,packet_path]}
        paths=[Path(__file__),source,*[nd/k for k in ['resource-acquire-native.h','resource-acquire-shim.S','resource-acquire-providers.S','resource-acquire.ld','Makefile.resource-acquire','Makefile']]]
        state.update(status='terminal_controlled_acquire_preflight_pass'if args.limit else'terminal_controlled_acquire_full_CPU_RAM_ordered_access_pass',source_accepted=False,controlled_component_pass=not args.limit,native_cases=len(rows),trace_cases=len(rows),binary_bytes=len(payload),compiled_binary=str(binary),compiled_binary_sha256=sha(binary),symbols=symbols,original_instruction_coverage=sorted(coverage),artifacts_sha256={str(q):sha(q)for q in paths},scope='Original24publicsavebytes/fullD/A/PC/SR/USP/SSP/public2MBRAM, helperarguments and orderedpublic reads/writes match. Identical controlledtarget68000providers exercise waits/clobbers/mutations/flags. Private8KBstack below24publicsavebytes, entryredirect and candidatecode excluded. No real allocator/loader/scheduler integration, concurrency/fault/livegame/physical or whole-game proof.')
        mark()
        if not args.limit:save(ROOT/'verification/native-load-scan-bundle-acquire-controlled-current.json',state)
        print(state['status'],len(rows),len(payload),flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
