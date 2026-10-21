"""Source-assembled heap init byte identity, full native ABI/RAM and bus trace."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,random,os,subprocess
import check_biwn_native_free as free
from check_biwn_native_button_digit import ROOT,sha,save
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);args=parser.parse_args()
    source=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';out=ROOT/'verification/native-fast-core-format-bundle-initialize'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),source_accepted=False,limit=args.limit,game_frames=0)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-fast-core-format-bundle-initialize-active.json',state)
    mark()
    try:
        build=out/'build';p=subprocess.run(['make','-f','/Users/kevin/Documents/Codex/2026-10-10/i-now-am-using-the-following/outputs/local-ai-lab/verification/native-fast-core-bundle/20261018T220820.261448Z/Makefile','format-bundle','BUILD='+str(build)],cwd=source,capture_output=True,text=True);(out/'make.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
        prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');binary=build/'native-format-bundle.bin';payload=binary.read_bytes();symbols={}
        assert sha(binary)=='35a80f52ff4bdede73aa8ec84abd8fa94a1e8c2bea9e3c85349318ded41a509a', "Wrong relocated bundle bytes"
        for line in subprocess.check_output([prefix+'nm','--defined-only',str(build/'native-format-bundle.elf')],text=True).splitlines():
            t=line.split()
            if len(t)==3:symbols[t[2]]=int(t[0],16)
        save(out/'symbols.json',symbols);(out/'disassembly.txt').write_text(subprocess.check_output([prefix+'objdump','-dr',str(build/'native-format-bundle.elf')],text=True))
        free.BASE=0x15edc0;free.ENTRY=0x1557a;free.END=0x155c2;free.PATCH_BYTES=10
        image=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());floor=symbols['biwn_native_heap_start']
        for address,value in [(0x1557c,floor),(0x1558c,floor),(0x15592,floor),(0x15598,floor+4),(0x1559e,floor+8)]:image[address:address+4]=value.to_bytes(4,'big')
        offset=symbols['biwn_native_heap_initialize']-free.BASE;original=bytes(image[free.ENTRY:free.END]);assert len(original)==72 and payload[offset:offset+72]==original
        candidate=bytearray(image);candidate[free.BASE:free.BASE+len(payload)]=payload;candidate[free.ENTRY:free.ENTRY+10]=b'\x4e\xf9'+symbols['biwn_native_heap_initialize'].to_bytes(4,'big')+b'\x4e\x71'*2
        rng=random.Random(0x1557a);cases=[]
        for variant in range(3):
            for mode in [0,0x2000]:
                for ccr in range(32):
                    initial=[[0x112960+i*4,4,rng.getrandbits(32)]for i in range(256)]+[[floor+i*4,4,rng.getrandbits(32)]for i in range(3)]+[[0x112d60,4,rng.getrandbits(32)],[0x112d64,4,rng.getrandbits(32)]]
                    cases.append(dict(entry=free.ENTRY,kind='initializer_all_CCR_stackbanks',params=[0],initial=initial,default_helper_return=0,incoming=[rng.getrandbits(32)for _ in range(15)],sr=mode|ccr|((variant*3)<<8)))
        if args.limit:cases=cases[:args.limit]
        save(out/'fixtures.json',cases);n=free.sched.Native();rows=[];traces=[];coverage=set()
        try:
            for i,case in enumerate(cases):
                a=free.native(n,image,case,len(payload),True);b=free.native(n,candidate,case,len(payload),False)
                assert a[1]==b[1]and free.normalize(b[0],a[0],len(payload))==a[0],('native mismatch',i)
                assert b[0][free.BASE:free.BASE+len(payload)]==payload and b[0][0x112960:0x112d60]==bytes(1024)
                assert int.from_bytes(b[0][0x112d60:0x112d64],'big')==floor
                assert int.from_bytes(b[0][floor:floor+4],'big')==0x1c0000-floor
                ta,ar=free.trace(image,case,len(payload),True);tb,br=free.trace(candidate,case,len(payload),False)
                assert ta['events']==tb['events']and ta['registers']==tb['registers']and free.normalize(br,ar,len(payload))==ar,('trace mismatch',i)
                coverage.update(a[2]);rows.append(dict(case=i,CPU=b[1],original_cycles=a[3],compiled_cycles=b[3],native_full_CPU_RAM_match=True));traces.append(dict(case=i,events=ta['events']))
                if i%64==0:state['completed']=len(rows);mark();print('Init',len(rows),'/',len(cases),flush=True)
        finally:n.close()
        save(out/'native-results.json',rows);save(out/'trace-results.json',traces)
        state.update(status='terminal_native_initializer_preflight_pass'if args.limit else'terminal_source_initializer_byte_identical_CPU_RAM_and_bus_pass',native_cases=len(rows),trace_cases=len(traces),source_accepted=not args.limit,compiled_binary=str(binary),compiled_binary_sha256=sha(binary),binary_bytes=len(payload),symbols=symbols,heap_start=floor,source_assembled_initializer_bytes=72,byte_identical_to_original_with_same_heap_floor=True,original_instruction_coverage=sorted(coverage),source_sha256={str(p):sha(p)for p in [Path(__file__),ROOT/'scripts/check_biwn_native_free.py',*[p for pattern in ['Makefile*','*.ld','*.S','*.c','*.h']for p in source.glob(pattern)]]},execution_dependencies_sha256={str(p):sha(p)for p in [ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib',ROOT/'render-assets/biwn-inventory-baseline.bin']},scope='Coordinator source-assembled72byte initializer matches original operand-relocated bytes. Full nativeCPU/flags/stackbanks/publicRAM and separate ordered argument/CLR/RTS bus checks; compiled code protected. Heap boundary relocation is shared by reference/candidate. No physical memory/device timing/interrupt/fullgame claim.')
        mark();save(ROOT/'verification/native-fast-core-format-bundle-initialize-current.json',state);print(state['status'],len(rows),len(payload),flush=True)
    except BaseException as exc:state.update(status='terminal_failed',error=repr(exc));mark();raise
if __name__=='__main__':main()
