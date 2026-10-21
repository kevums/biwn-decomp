"""Native free ABI/RAM plus ordered bus and declared changing-read replay.

Unicorn supplies per-engine changing-read plans, not the condition-code oracle.
Native execution applies only those declared values before matching reads;
no host cleanup/coalescing implementation executes on the candidate side.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,os,random,subprocess
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_transition_cleanup as old
import check_biwn_scheduler as sched
from check_biwn_native_button_digit import ROOT,sha,save
BASE=0x140000;ENTRY=0x1545c;END=0x1557a;PATCH_BYTES=8;SP=0x1e0000;STOP=0x1f0000
REGS=[UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7]
def private(a,w):return SP-0x2000<=a and a+w<=SP-8
def normalize(ram,reference,length):
    b=bytearray(ram);b[BASE:BASE+length]=reference[BASE:BASE+length];b[ENTRY:ENTRY+PATCH_BYTES]=reference[ENTRY:ENTRY+PATCH_BYTES];b[SP-0x2000:SP-8]=reference[SP-0x2000:SP-8];return b
def seed(image,case):
    script=old.Script(image,case);script.put(SP,4,STOP);script.put(SP+4,4,case['params'][0]);return bytes(script.memory)
def trace(image,case,length,original):
    script=old.Script(image,case);script.memory[:]=seed(image,case)
    u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,bytes(script.memory));u.reg_write(UC_M68K_REG_SR,case['sr'])
    for reg,value in zip(REGS,case['incoming']+[SP]):u.reg_write(reg,value)
    steps=[];plan=[]
    def code(e,a,w,_):
        assert (ENTRY<=a<END)if original else(BASE<=a<BASE+length or a==ENTRY),hex(a)
        steps.append(a)
    def read(e,t,a,w,v,_):
        if not private(a,w):
            value=script.read(a,w);e.mem_write(a,value.to_bytes(w,'big'))
            if any(q['address']==a and q['width']==w for q in case.get('read_queues',[])):
                record=dict(step=len(steps)-1,PC=steps[-1],address=a,width=w,value=value)
                assert not any(p['step']==record['step']and(p['address'],p['width'])==(a,w)for p in plan),'Two distinct values for the same operand within one native instruction require a different bus replay mechanism.'
                plan.append(record)
    def write(e,t,a,w,v,_):
        if not private(a,w):script.write(a,w,v&((1<<(w*8))-1))
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(ENTRY,STOP,count=50000,timeout=3000000)
    assert u.reg_read(UC_M68K_REG_PC)==STOP and u.reg_read(UC_M68K_REG_A7)==SP+4
    ram=bytes(u.mem_read(0,0x200000));assert normalize(ram,bytes(script.memory),length)==script.memory
    return dict(events=script.trace,registers=[u.reg_read(reg)for reg in REGS],plan=plan,steps=steps),ram
def native(n,image,case,length,original,plan=None):
    n.device.seed(seed(image,case),0);l=n.lib;l.m68k_pulse_reset();l.m68k_set_irq(0)
    l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,SP if case['sr']&0x2000 else 0x1fc000);l.m68k_set_reg(17,0);l.m68k_set_reg(15,0x1fd000 if case['sr']&0x2000 else SP);l.m68k_set_reg(17,case['sr'])
    for i,v in enumerate(case['incoming']+[SP]):l.m68k_set_reg(i,v)
    l.m68k_set_reg(16,ENTRY);steps=[];cycles=0;plan=plan or[];j=0
    for step in range(50000):
        pc=l.m68k_get_reg(None,16)
        if pc==STOP:break
        assert (ENTRY<=pc<END)if original else(BASE<=pc<BASE+length or pc==ENTRY),hex(pc)
        while j<len(plan)and plan[j]['step']==step:
            event=plan[j];assert event['PC']==pc,(step,event,hex(pc));n.device.direct(event['address'],event['width'],event['value']);j+=1
        steps.append(pc);cycles+=l.m68k_execute(1)
    else:raise AssertionError('Native free did not return')
    assert j==len(plan) and l.m68k_get_reg(None,15)==SP+4
    cpu=dict(registers=[l.m68k_get_reg(None,i)for i in range(16)],PC=l.m68k_get_reg(None,16),SR=l.m68k_get_reg(None,17));cpu['usp']=n.prefix[16]if cpu['SR']&0x2000 else cpu['registers'][15];cpu['ssp']=cpu['registers'][15]if cpu['SR']&0x2000 else n.prefix[17]
    return n.device.ram(),cpu,steps,cycles
def vectors(image):
    rng=random.Random(0x1545c);base=[x for x in old.cases(image)if x['entry']==ENTRY]
    for x in base:
        x['initial']=[[0x110000 if a==0x160000 else a,w,v]for a,w,v in x['initial']];x['params']=[0x110000 if v==0x160000 else v for v in x['params']]
        x['read_queues']=[{**q,'address':0x110000 if q['address']==0x160000 else q['address']}for q in x.get('read_queues',[])];x['sr']=0x2000
    samples=[next(x for x in base if x['kind']==k)for k in dict.fromkeys(x['kind']for x in base)];rows=list(base)
    for sample in samples:
        for mode in [0,0x2000]:
            for ccr in range(32):rows.append({**sample,'initial':list(sample['initial']),'read_queues':[],'incoming':[rng.getrandbits(32)for _ in range(15)],'sr':mode|ccr|((ccr%8)<<8),'kind':sample['kind']+'_all_CCR'})
    for kind in ['empty','before_join_next','middle_both_next','tail_separate']:
        sample=next(x for x in samples if x['kind']==kind)
        for value in [0,1,0x7fffffff,0x80000000,0xfffffffe,0xffffffff]:
            for available in [0,1,0x7fffffff,0x80000000,0xfffffffe,0xffffffff]:
                for mode in [0,0x2000]:
                    # Change allocated size (empty/middle), merged next size
                    # (before), or previous size (tail); all dereferenced links
                    # stay mapped, including raw wrapped metadata cases.
                    address={'empty':0x170700,'before_join_next':0x170140,'middle_both_next':0x170400,'tail_separate':0x170100}[kind]
                    rows.append({**sample,'initial':list(sample['initial'])+[[address,4,value],[0x112d64,4,available]],'read_queues':[],'sr':mode|rng.randrange(32),'incoming':[rng.getrandbits(32)for _ in range(15)],'kind':kind+'_raw_add_flags'})
    sample=next(x for x in samples if x['kind']=='before_separate')
    rows.append({**sample,'initial':list(sample['initial'])+[[0x170700,4,0x40],[0x170704,4,0],[0x170708,4,0]],'read_queues':[dict(address=0x112d60,width=4,values=[0x170400,0x170700])],'kind':'head_rereads_change'})
    sample=next(x for x in samples if x['kind']=='scan_middle')
    rows.append({**sample,'initial':list(sample['initial']),'read_queues':[dict(address=0x170104,width=4,values=[0x170300,0x170500])],'kind':'next_rereads_change'})
    sample=next(x for x in samples if x['kind']=='before_join_next')
    rows.append({**sample,'initial':list(sample['initial']),'read_queues':[dict(address=0x170144,width=4,values=[0x170400,0])],'kind':'merged_next_test_reread_changes'})
    return rows
def main():
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int);p.add_argument('--source',type=Path);p.add_argument('--bundle',action='store_true');args=p.parse_args()
    global BASE
    if args.bundle:BASE=0x15edc0
    author_path=ROOT/'verification/local-native-free-current.json';author=json.loads(author_path.read_text());source=args.source or Path(author['source']);assert args.source or sha(source)==author['source_sha256']
    name='native-core-format-bundle-free'if args.bundle else'native-free';out=ROOT/'verification'/name/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),source=str(source),source_sha256=sha(source),limit=args.limit,source_accepted=False,game_frames=0,whole_game_complete=False)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification'/(name+'-active.json'),state)
    mark()
    try:
        native_dir=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';build=out/'build';stem='native-format-bundle'if args.bundle else'native-free'
        cmd=['make','-f','/Users/kevin/Documents/Codex/2026-10-10/i-now-am-using-the-following/outputs/local-ai-lab/verification/native-core-bundle/20261018T185634.729219Z/Makefile'if args.bundle else'Makefile.free','format-bundle'if args.bundle else'free','BUILD='+str(build),'FREE_SOURCE='+str(source)]
        result=subprocess.run(cmd,cwd=native_dir,capture_output=True,text=True);(out/'make.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
        prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');binary=build/(stem+'.bin');payload=binary.read_bytes();symbols={}
        assert sha(binary)=='f95dc1ea802aac6a9288bde917575a3ec61538d8fcc60ec18172281ea6565d25', "Wrong relocated bundle bytes"
        for line in subprocess.check_output([prefix+'nm','--defined-only',str(build/(stem+'.elf'))],text=True).splitlines():
            t=line.split()
            if len(t)==3:symbols[t[2]]=int(t[0],16)
        save(out/'symbols.json',symbols);(out/'disassembly.txt').write_text(subprocess.check_output([prefix+'objdump','-dr',str(build/(stem+'.elf'))],text=True))
        image=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);stage=session/'nextstage-68000-candidate.bin'
        from extract_biwn_stage import STAGE_SHA
        assert sha(stage)==STAGE_SHA and image[ENTRY:END]==stage.read_bytes()[ENTRY-0x4000:END-0x4000]
        candidate=bytearray(image);candidate[BASE:BASE+len(payload)]=payload;candidate[ENTRY:ENTRY+PATCH_BYTES]=b'\x4e\xf9'+symbols['biwn_native_free'].to_bytes(4,'big')+b'\x4e\x71'
        cases=vectors(image)
        if args.limit:
            no_handle=next(c for c in cases if c['params']==[0])
            empty_handle=next(c for c in cases if [0x110000,4,0]in c['initial'])
            cases=([no_handle,empty_handle]+[next(c for c in cases if c['kind']==kind)for kind in dict.fromkeys(c['kind']for c in cases)])[:args.limit]
        save(out/'fixtures.json',cases);native_rows=[];trace_rows=[];mutable_rows=[];coverage=set();n=sched.Native()
        try:
            for i,case in enumerate(cases):
                state['status']='native_full_CPU_RAM_stable_inputs';stable={**case,'read_queues':[]}
                a=native(n,image,stable,len(payload),True);b=native(n,candidate,stable,len(payload),False)
                if a[1]!=b[1]or normalize(b[0],a[0],len(payload))!=a[0]:
                    save(out/'mismatch.json',dict(case=i,parameters=stable,original_CPU=a[1],compiled_CPU=b[1],RAM_differences=[hex(j)for j,(x,y)in enumerate(zip(a[0],normalize(b[0],a[0],len(payload))))if x!=y][:32]));raise AssertionError(str(out/'mismatch.json'))
                assert b[0][BASE:BASE+len(payload)]==payload;coverage.update(a[2]);native_rows.append(dict(case=i,kind=case['kind'],CPU=b[1],original_cycles=a[3],compiled_cycles=b[3],full_CPU_and_RAM_match=True))
                ta,ar=trace(image,case,len(payload),True);tb,br=trace(candidate,case,len(payload),False)
                if ta['events']!=tb['events']or ta['registers']!=tb['registers']or normalize(br,ar,len(payload))!=ar:
                    save(out/'trace-mismatch.json',dict(case=i,parameters=case,original=ta,compiled=tb));raise AssertionError(str(out/'trace-mismatch.json'))
                trace_rows.append(dict(case=i,kind=case['kind'],events=ta['events']))
                if case.get('read_queues'):
                    # Both instruction plans arise from the same declared
                    # address/width/value queues and same matched public trace.
                    left=native(n,image,case,len(payload),True,ta['plan']);right=native(n,candidate,case,len(payload),False,tb['plan'])
                    assert left[1]==right[1]and normalize(right[0],left[0],len(payload))==left[0],('native changing-read mismatch',i)
                    assert normalize(left[0],ar,len(payload))==ar and normalize(right[0],br,len(payload))==br
                    coverage.update(left[2]);mutable_rows.append(dict(case=i,kind=case['kind'],CPU=right[1],original_read_plan=ta['plan'],compiled_read_plan=tb['plan'],same_declared_input_stream_full_CPU_RAM_match=True))
                if i%128==0:state.update(native_completed=len(native_rows),trace_completed=len(trace_rows),changing_read_native_completed=len(mutable_rows));mark();print('Native/trace',len(native_rows),'/',len(cases),'mutable',len(mutable_rows),flush=True)
        finally:n.close()
        save(out/'native-results.json',native_rows);save(out/'trace-results.json',trace_rows);save(out/'changing-read-native-results.json',mutable_rows)
        paths=[Path(__file__),ROOT/'scripts/check_biwn_transition_cleanup.py',ROOT/'scripts/check_biwn_scheduler.py',source,*[native_dir/x for x in ['free-native.h','free-shims.S','free.ld','Makefile.free','Makefile']]]
        if args.bundle:paths+=[q for pattern in ['Makefile*','*.ld','*.S','*.c','*.h']for q in native_dir.glob(pattern)]
        state.update(status='terminal_native_free_preflight_pass'if args.limit else'terminal_native_free_CPU_RAM_ordered_and_mutable_reads_pass',native_cases=len(native_rows),trace_cases=len(trace_rows),changing_read_native_cases=len(mutable_rows),original_instruction_coverage=sorted(coverage),compiled_binary=str(binary),compiled_binary_sha256=sha(binary),binary_bytes=len(payload),symbols=symbols,source_accepted=not args.limit,source_sha256={str(q):sha(q)for q in paths},execution_dependencies_sha256={str(q):sha(q)for q in [ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib',ROOT/'render-assets/biwn-inventory-baseline.bin',stage]},scope='Full native D/A/PC/SR/USP/SSP and public2MBRAM, including original8public stack-save bytes. Separate Unicorn ordered argument/data/stack/CLR accesses; its SR is not the flags oracle. Declared changing-read values replayed before individually matched original/compiled native instructions and compared with their equal public traces. Private8KBworkingstack below original save slots, new code/entryJMP excluded. No host free/coalescing body, IRQ/device concurrency/busfault/arbitrary malformed-list/physical/fullgame proof.')
        mark();save(ROOT/'verification'/(name+'-current.json'),state);print(state['status'],len(native_rows),len(trace_rows),len(mutable_rows),len(payload),flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
