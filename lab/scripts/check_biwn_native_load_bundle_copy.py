"""Native target copy ABI+real blitter; independent ordered-access emulation.

The second engine maps MMIO as ordinary storage and proves ordered access only.
Original public save slots at entrySP-12..entrySP are NOT masked as private.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,os,random,subprocess,sys
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_scheduler as sched
from check_biwn_native_button_digit import ROOT,sha,save
BASE=0x180000;SP=0x1e0000;STOP=0x1f0000
ENTRIES={0xe3e0:'biwn_native_copy_source_first',0xe3ee:'biwn_native_copy_destination_first'}
REGS=[UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7]
def private(a,w):return SP-0x2000<=a and a+w<=SP-12
def normalize(ram,reference,length):
    b=bytearray(ram);b[BASE:BASE+length]=reference[BASE:BASE+length]
    for a in ENTRIES:b[a:a+6]=reference[a:a+6]
    b[SP-0x2000:SP-12]=reference[SP-0x2000:SP-12];return b
def native(n,image,case,length,original):
    n.device.seed(image,1)
    for a in range(0xf02200,0xf022a0,4):
        if a!=0xf02238:n.device.write(a,0)
    l=n.lib;l.m68k_pulse_reset();l.m68k_set_irq(0)
    l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,SP if case['sr']&0x2000 else 0x1fc000)
    l.m68k_set_reg(17,0);l.m68k_set_reg(15,0x1fd000 if case['sr']&0x2000 else SP);l.m68k_set_reg(17,case['sr'])
    for i,v in enumerate(case['incoming']+[SP]):l.m68k_set_reg(i,v)
    l.m68k_set_reg(16,case['entry']);steps=[];cycles=0
    for _ in range(100000):
        pc=l.m68k_get_reg(None,16)
        if pc==STOP:break
        assert (0xe3e0<=pc<0xe4aa)if original else(BASE<=pc<BASE+length or pc in ENTRIES),hex(pc)
        steps.append(pc);cycles+=l.m68k_execute(1)
    else:raise AssertionError('Native copy did not return')
    cpu=dict(registers=[l.m68k_get_reg(None,i)for i in range(16)],PC=l.m68k_get_reg(None,16),SR=l.m68k_get_reg(None,17));cpu['usp']=n.prefix[16]if cpu['SR']&0x2000 else cpu['registers'][15];cpu['ssp']=cpu['registers'][15]if cpu['SR']&0x2000 else n.prefix[17]
    hardware=[n.device.read(a,4)for a in [0xf02200,0xf02204,0xf0220c,0xf02224,0xf02228,0xf02230,0xf0223c]]
    return n.device.ram(),cpu,steps,cycles,hardware
def trace(image,case,length,original,prefix_units=None):
    u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_map(0xf02000,0x1000);u.mem_write(0,image)
    u.reg_write(UC_M68K_REG_SR,case['sr'])
    for reg,v in zip(REGS,case['incoming']+[SP]):u.reg_write(reg,v)
    events=[];units=0
    def code(e,a,w,_):assert (0xe3e0<=a<0xe4aa)if original else(BASE<=a<BASE+length or a in ENTRIES),hex(a)
    def read(e,t,a,w,v,_):
        if not private(a,w):events.append(['r',a,w,int.from_bytes(e.mem_read(a,w),'big')])
    def write(e,t,a,w,v,_):
        nonlocal units
        if not private(a,w):events.append(['w',a,w,v&((1<<(w*8))-1)])
        if prefix_units and ((w==1 and case['destination']<=a<case['destination']+128)or a==0xf02238):
            units+=1
            if units==prefix_units:e.emu_stop()
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write)
    u.emu_start(case['entry'],STOP,count=100000,timeout=3000000)
    if prefix_units:assert units==prefix_units
    else:assert u.reg_read(UC_M68K_REG_PC)==STOP
    return events,bytes(u.mem_read(0,0x200000)),[u.reg_read(reg)for reg in REGS]
def vectors():
    rng=random.Random(0xe3e0e3ee);rows=[]
    def add(entry,count,source,destination,kind,sr=None):
        incoming=[rng.getrandbits(32)for _ in range(15)];incoming[2]=[0,1,0x80000000,0xffffffff,rng.getrandbits(32)][len(rows)%5]
        rows.append(dict(entry=entry,count=count,source=source,destination=destination,kind=kind,incoming=incoming,sr=(0x2000|rng.randrange(32))if sr is None else sr))
    for e in ENTRIES:
        for count in range(128):
            for delta in [-1,0,1,200]:add(e,count,0x100080,0x100080+delta,'small_forward_overlap')
        for count in [128,129,65535,65536,65537,131071,131072,131073]:
            for so in range(8):
                for do in range(8):add(e,count,0x100000+so,0x130000+do,'large_all_phrase_offsets')
        for count in [128,129,65537]:
            for so in range(8):
                for delta in [-16,-8,-2,-1,0,1,2,8,16]:add(e,count,0x100080+so,0x100080+so+delta,'large_overlap_actual_blitter')
        for mode in [0,0x2000]:
            for ccr in range(32):
                for count in [0,1,127,128,129,65537]:add(e,count,0x100001+(ccr%8),0x130000+((ccr*3)%8),'all_CCR_and_stack_banks',mode|ccr|((ccr%8)<<8))
        for count in [128,129,65537]:
            add(e,count,SP-12,0x130000,'source_in_original_public_save_slots')
            add(e,count,0x100000,SP+16,'destination_after_public_arguments')
    return rows
def prepare(image,case):
    b=bytearray(image);params=[case['source'],case['destination'],case['count']]if case['entry']==0xe3e0 else[case['destination'],case['source'],case['count']]
    for i,v in enumerate([STOP]+params):b[SP+i*4:SP+i*4+4]=v.to_bytes(4,'big')
    # Distinct untouched words expose unwanted small/zero stack writes.
    b[SP-12:SP]=bytes.fromhex('102030405060708090a0b0c0');return bytes(b)
def main():
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int);p.add_argument('--source',type=Path);p.add_argument('--phase',choices=['native','trace','both'],default='both');p.add_argument('--bundle',action='store_true');args=p.parse_args()
    global BASE
    if args.bundle:BASE=0x15edc0
    ap=ROOT/'verification/local-native-copy-current.json';author=json.loads(ap.read_text());source=args.source or Path(author['source']);assert args.source or sha(source)==author['source_sha256']
    name='native-load-bundle-copy'if args.bundle else'native-copy';stem='native-load-bundle'if args.bundle else'native-copy'
    out=ROOT/'verification'/name/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='prepared',directory=str(out),pid=os.getpid(),source=str(source),source_sha256=sha(source),limit=args.limit,phase=args.phase,source_accepted=False,game_frames=0,whole_game_complete=False)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification'/(name+'-active.json'),state)
    mark()
    try:
        native_dir=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';build=out/'build';run=subprocess.run(['make','-f','Makefile.load-bundle'if args.bundle else'Makefile.copy','load-bundle'if args.bundle else'copy','BUILD='+str(build),'COPY_SOURCE='+str(source)],cwd=native_dir,capture_output=True,text=True);(out/'make.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
        prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');binary=build/(stem+'.bin');payload=binary.read_bytes();symbols={}
        assert sha(binary)=='418ae7d7f9c3a72da6231e694caaf1936ed55c85db3a1ba8e8420d07bb7aee85', "Wrong relocated bundle bytes"
        for line in subprocess.check_output([prefix+'nm','--defined-only',str(build/(stem+'.elf'))],text=True).splitlines():
            t=line.split()
            if len(t)==3:symbols[t[2]]=int(t[0],16)
        save(out/'symbols.json',symbols);(out/'disassembly.txt').write_text(subprocess.check_output([prefix+'objdump','-dr',str(build/(stem+'.elf'))],text=True))
        image=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes())
        session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
        stage_path=session/'nextstage-68000-candidate.bin'
        from extract_biwn_stage import STAGE_SHA
        assert sha(stage_path)==STAGE_SHA
        assert image[0xe3e0:0xe4aa]==stage_path.read_bytes()[0xe3e0-0x4000:0xe4aa-0x4000]
        image[0x100000:0x151000]=random.Random(0xe4aa).randbytes(0x51000)
        candidate=bytearray(image);candidate[BASE:BASE+len(payload)]=payload
        for address,key in ENTRIES.items():candidate[address:address+6]=b'\x4e\xf9'+symbols[key].to_bytes(4,'big')
        cases=vectors()
        if args.limit:cases=[next(c for c in cases if c['entry']==e and c['count']==count)for e in ENTRIES for count in [0,1,127,128,129,65536,65537]][:args.limit]
        save(out/'fixtures.json',cases);rows=[];traces=[];coverage=set();prefixes=[]
        if args.phase in ['native','both']:
            n=sched.Native();state['status']='native_CPU_RAM_actual_blitter';mark()
            try:
                for i,case in enumerate(cases):
                    a=native(n,prepare(image,case),case,len(payload),True);b=native(n,prepare(candidate,case),case,len(payload),False)
                    if a[1]!=b[1] or normalize(b[0],a[0],len(payload))!=a[0] or a[4]!=b[4]:
                        save(out/'mismatch.json',dict(case=i,parameters=case,original_CPU=a[1],compiled_CPU=b[1],original_hardware=a[4],compiled_hardware=b[4],RAM_differences=[hex(j)for j,(x,y)in enumerate(zip(a[0],normalize(b[0],a[0],len(payload))))if x!=y][:32]));raise AssertionError(str(out/'mismatch.json'))
                    assert b[0][BASE:BASE+len(payload)]==payload;coverage.update(a[2]);rows.append(dict(case=i,entry=hex(case['entry']),count=case['count'],CPU=b[1],original_cycles=a[3],compiled_cycles=b[3],hardware=b[4],RAM_and_full_CPU_and_hardware_match=True))
                    if i%128==0:state['native_completed']=len(rows);mark();print('Native',len(rows),'/',len(cases),flush=True)
            finally:n.close()
            save(out/'native-results.json',rows)
        if args.phase in ['trace','both']:
            state['status']='ordered_access_MMIO_as_plain_storage';mark()
            for i,case in enumerate(cases):
                a=trace(prepare(image,case),case,len(payload),True);b=trace(prepare(candidate,case),case,len(payload),False)
                if a[0]!=b[0]or a[2]!=b[2]or normalize(b[1],a[1],len(payload))!=a[1]:
                    save(out/'trace-mismatch.json',dict(case=i,parameters=case,original=a[0],compiled=b[0],original_regs=a[2],compiled_regs=b[2]));raise AssertionError(str(out/'trace-mismatch.json'))
                traces.append(dict(case=i,events=a[0],registers=b[2]));
                if i%128==0:state['trace_completed']=len(traces);mark();print('Trace',len(traces),'/',len(cases),flush=True)
            save(out/'trace-results.json',traces)
            if not args.limit:
                for e in ENTRIES:
                    for count in [0x7fffffff,0x80000000,0x8000007f,0x80000080,0x8000ffff,0xffffffff]:
                        case={**cases[0],'entry':e,'count':count,'source':0x100001,'destination':0x100002,'kind':'raw_subtraction_N_prefix'}
                        left=trace(prepare(image,case),case,len(payload),True,3)[0];right=trace(prepare(candidate,case),case,len(payload),False,3)[0];assert left==right,(e,count,left,right)
                        prefixes.append(dict(entry=e,count=count,units=3,unit='byte'if(count-128)&0x80000000 else'command',events=left,full_return_claimed=False))
                save(out/'raw-count-prefixes.json',prefixes)
        state.update(status='terminal_native_copy_preflight_pass'if args.limit else'terminal_native_copy_CPU_RAM_blitter_and_ordered_access_pass',native_cases=len(rows),trace_cases=len(traces),compiled_binary=str(binary),compiled_binary_sha256=sha(binary),binary_bytes=len(payload),symbols=symbols,original_instruction_locations=len(coverage),original_instruction_coverage=sorted(coverage),source_accepted=not args.limit and args.phase=='both',source_sha256={str(q):sha(q)for q in [source,Path(__file__),native_dir/'copy-native.h',native_dir/'copy-shims.S',native_dir/'copy.ld',native_dir/'Makefile.copy',native_dir/'Makefile']},execution_dependencies_sha256={str(q):sha(q)for q in [ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib',ROOT/'render-assets/biwn-inventory-baseline.bin']},scope='Native full D/A/PC/SR/USP/SSP, public2MBRAM including original12byte save slots and seven actual-emulated-blitter registers. Separate ordered original argument/data/MMIO/stack accesses under Unicorn with MMIO as ordinary storage, not hardware effects or CCR oracle. Private8KBworkingstack below the original save slots, new code and redirected entry bytes excluded. No IRQ/concurrency/busfault/physical/fullgame timing/general arbitrary stack/code aliases proof.')
        state['raw_count_prefix_cases']=len(prefixes)
        state['original_stage_proof']={'path':str(stage_path),'sha256':sha(stage_path),'copy_bytes_match_baseline':True}
        if args.bundle:state['source_sha256'].update({str(q):sha(q)for pattern in ['Makefile*','*.ld','*.S','*.c','*.h']for q in native_dir.glob(pattern)})
        mark();save(ROOT/'verification'/(name+'-current.json'),state);print(state['status'],len(rows),len(traces),len(payload),flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
