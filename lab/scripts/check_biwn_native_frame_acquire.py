"""Complete 1AC68 native C candidate: CPU, public frame, loader ABI, bus, DIVS."""
import argparse, copy, json, os, random, re, shutil, subprocess
from datetime import datetime, timezone
from pathlib import Path
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_local_frame_resource_acquire as fixture
from check_biwn_scheduler import Native
from check_biwn_native_resource_release import REGS
from check_biwn_native_button_digit import ROOT, sha, save

ENTRY, END, BASE = 0x1ac68, 0x1ae56, 0x148000
SP, STOP, SCRATCH = fixture.SP, fixture.STOP, fixture.SCRATCH
SSP, HANDLER, PROVIDER, CONFIG = 0x1ed000, 0x1f1000, 0x144000, 0x142200
LOADER = fixture.LOADER
ND = ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
PROVIDER_SOURCE = '''.text
.globl fixture_frame_loader
fixture_frame_loader:
movea.l 12(%sp),%a0
move.l 0x142214,(%a0)
move.w 0x142218,0x15b532
move.l 0x142200,%d0
move.l 0x142204,%d1
movea.l 0x142208,%a0
movea.l 0x14220c,%a1
move.w 0x142210,%ccr
rts
'''

def cpu(n):
    r=[n.lib.m68k_get_reg(None,i) for i in range(18)]
    return r+[n.prefix[16] if r[17]&0x2000 else r[15],r[15] if r[17]&0x2000 else n.prefix[17]]

def vectors():
    image, cases = fixture.fixtures(); rng=random.Random(0x1ac682026)
    for i,c in enumerate(cases):
        c.update(sr=(0x2000 if i%2 else 0)|(i%32),clobbers=[rng.getrandbits(32) for _ in range(3)],loader_ccr=i%32)
    # Every CCR and both stack modes on hit, empty, eviction and failure.
    selected=[next(c for c in cases if c['mode_word']==3 and c['count_word']==2 and c['reserved_word']<16 and c['pattern']==p and c['adjusted_word']<32768) for p in range(4)]
    for mode in [0,0x2000]:
        for flags in range(32):
            for c in selected:
                d=copy.deepcopy(c);d.update(sr=mode|flags,loader_ccr=flags);cases.append(d)
    # Wrapping references in an existing hit (including sign/unsigned edges).
    for value in [0,1,0x7fff,0x8000,0xffff]:
        c=copy.deepcopy(selected[0]);a=0x15b4a2+c['reserved_word']*4;c['initial'] += [[a,2,value],[a+4,2,value]];cases.append(c)
    zeros=[]
    for mode in [0,0x2000]:
        for flags in range(32):
            for pattern,queue in [(3,[40,40,40]),(1,[40,0]),(2,[40,40,0])]:
                c=copy.deepcopy(selected[pattern]);c.update(count_word=0,reserved_word=40,sr=mode|flags,loader_ccr=flags)
                c['initial'] += [[0x464a6,2,0],[0x15b532,2,40]]
                c['read_queues']=[dict(address=0x15b532,width=2,values=queue)]
                c['zero_fixture']=True;zeros.append(c)
    return image,cases,zeros

def seed(image,case):
    b=bytearray(image)
    for a,w,v in case['initial']:b[a:a+w]=v.to_bytes(w,'big')
    b[SP:SP+6]=STOP.to_bytes(4,'big')+case['id_word'].to_bytes(2,'big')
    b[20:24]=HANDLER.to_bytes(4,'big');b[HANDLER:HANDLER+2]=b'\x4e\x73'
    scratch=next(v for a,w,v in case['loader_effects'] if a==SCRATCH)
    reserved=next(v for a,w,v in case['loader_effects'] if a==0x15b532)
    data=[case['loader_return'],*case['clobbers']]
    for i,v in enumerate(data):b[CONFIG+i*4:CONFIG+i*4+4]=v.to_bytes(4,'big')
    b[CONFIG+16:CONFIG+18]=case['loader_ccr'].to_bytes(2,'big')
    b[CONFIG+20:CONFIG+24]=scratch.to_bytes(4,'big');b[CONFIG+24:CONFIG+26]=reserved.to_bytes(2,'big')
    return bytes(b)

def private(a,w):return SP-8192<=a and a+w<=SP-44
def allowed(pc,length,plen,original):
    return (ENTRY<=pc<END if original else pc==ENTRY or BASE<=pc<BASE+length) or pc==LOADER or PROVIDER<=pc<PROVIDER+plen

def normalize(ram,reference,length,zero=False):
    b=bytearray(ram)
    regions=[(BASE,BASE+length),(ENTRY,ENTRY+8),(SP-8192,SP-44)]
    if zero:regions.append((SSP-64,SSP))
    for lo,hi in regions:b[lo:hi]=reference[lo:hi]
    return bytes(b)

def trace(image,case,length,plen,original):
    u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,seed(image,case));u.reg_write(UC_M68K_REG_SR,case['sr'])
    for r,v in zip(REGS,case['incoming']+[SP]):u.reg_write(r,v)
    events=[];changes=[];queues={(q['address'],q['width']):list(q['values']) for q in case.get('read_queues',[])};current=ENTRY;minimum=SP
    def ignored(a,w):
        nonlocal minimum
        if private(a,w):minimum=min(minimum,a);return True
        return BASE<=a and a+w<=BASE+length
    def code(e,pc,w,_):
        nonlocal current
        assert allowed(pc,length,plen,original),('Trace escaped',hex(pc));current=pc
        if pc==LOADER:
            sp=e.reg_read(UC_M68K_REG_A7);args=[int.from_bytes(e.mem_read(sp+4+4*i,4),'big') for i in range(5)]
            events.append(['loader',sp,args,[e.reg_read(r) for r in REGS[:15]]])
    def read(e,t,a,w,v,_):
        if ignored(a,w):return
        q=queues.get((a,w))
        if q:
            value=q.pop(0);e.mem_write(a,value.to_bytes(w,'big'));changes.append([current,a,w,value])
        events.append(['r',a,w,int.from_bytes(e.mem_read(a,w),'big')])
    def write(e,t,a,w,v,_):
        if not ignored(a,w):events.append(['w',a,w,v&((1<<(8*w))-1)])
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write)
    u.emu_start(ENTRY,STOP,count=500000,timeout=10000000);assert u.reg_read(UC_M68K_REG_PC)==STOP,dict(PC=hex(u.reg_read(UC_M68K_REG_PC)),SP=hex(u.reg_read(UC_M68K_REG_A7)),events=events[-8:])
    return bytes(u.mem_read(0,0x200000)),events,changes,minimum

def run(n,image,case,length,plen,original,changes=None):
    n.device.seed(seed(image,case),0);l=n.lib;l.m68k_pulse_reset();l.m68k_set_irq(0)
    l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,SSP);l.m68k_set_reg(17,0);l.m68k_set_reg(15,0x1ec000);l.m68k_set_reg(17,case['sr'])
    for i,v in enumerate(case['incoming']+[SP]):l.m68k_set_reg(i,v)
    l.m68k_set_reg(16,ENTRY);coverage=set();calls=[];faults=[];minimum=SP;cycles=0
    pending=list(changes or []);queues={q['address']:list(q['values']) for q in case.get('read_queues',[])}
    for step in range(500000):
        pc=l.m68k_get_reg(None,16)
        if pc==STOP:break
        if pc!=HANDLER:minimum=min(minimum,l.m68k_get_reg(None,15))
        if pc==HANDLER:
            st=l.m68k_get_reg(None,15);ram=n.device.ram()
            faults.append(dict(cpu=cpu(n),frame_SR=int.from_bytes(ram[st:st+2],'big'),frame_PC=int.from_bytes(ram[st+2:st+6],'big'),source_site=None if original else int.from_bytes(ram[SP-556+72:SP-556+76],'big')))
        else:
            assert allowed(pc,length,plen,original),('Native escaped',hex(pc))
            coverage.add(pc)
            if pending and pc==pending[0][0]:
                _,a,w,v=pending.pop(0);n.device.direct(a,w,v)
            elif changes is None and pc in ([0x1acc2,0x1ad12,0x1adb0] if original else case.get('_compiled_zero_read_pcs',[])):
                q=queues.get(0x15b532)
                if q:n.device.direct(0x15b532,2,q.pop(0))
            if pc==LOADER:
                ram=n.device.ram();st=l.m68k_get_reg(None,15)
                calls.append(dict(cpu=cpu(n),args=[int.from_bytes(ram[st+4+i*4:st+8+i*4],'big') for i in range(5)],return_PC=int.from_bytes(ram[st:st+4],'big')))
        cycles+=l.m68k_execute(1)
    else:raise AssertionError(('Instruction budget',hex(pc),original))
    assert not pending,('Unreached read changes',pending)
    result=cpu(n);assert result[15]==SP+4
    return dict(cpu=result,calls=calls,faults=faults,ram=n.device.ram(),coverage=coverage,steps=step,cycles=cycles,minimum=minimum)

def compare(out,index,case,a,b,length,symbols):
    def fail(kind,detail):
        save(out/'mismatch.json',dict(kind=kind,index=index,case=case,detail=detail));raise AssertionError(kind)
    if a['cpu']!=b['cpu']:fail('Full native CPU mismatch',dict(original=a['cpu'],candidate=b['cpu']))
    if len(a['calls'])!=len(b['calls']):fail('Loader count mismatch',dict(original=a['calls'],candidate=b['calls']))
    for x,y in zip(a['calls'],b['calls']):
        x=x.copy();y=y.copy();oldpc=x.pop('return_PC');newpc=y.pop('return_PC')
        if x!=y or oldpc not in [0x1ad7a,0x1ae16] or newpc!=symbols['biwn_frame_acquire_after_load']:fail('Loader ABI mismatch',dict(original=x,candidate=y,old_return=oldpc,new_return=newpc))
    if len(a['faults'])!=len(b['faults']):fail('Fault count mismatch',dict(original=a['faults'],candidate=b['faults']))
    for x,y in zip(a['faults'],b['faults']):
        x=x.copy();y=y.copy();oldpc=x.pop('frame_PC');newpc=y.pop('frame_PC');x.pop('source_site');site=y.pop('source_site');offset=oldpc-site
        if x!=y or site not in [0x1ad0c,0x1ad4e,0x1adea] or offset not in [0,2] or newpc!=symbols['biwn_frame_acquire_divs_instruction']+offset:fail('Fault CPU/frame mismatch',dict(original=x,candidate=y,original_saved_PC=oldpc,native_saved_PC=newpc,site=site))
    ram=normalize(b['ram'],a['ram'],length,bool(a['faults']))
    if ram!=a['ram']:fail('Full public RAM mismatch',[dict(address=hex(i),original=x,candidate=y) for i,(x,y) in enumerate(zip(a['ram'],ram)) if x!=y][:40])

def main():
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int);p.add_argument('--zero-only',action='store_true');args=p.parse_args()
    out=ROOT/'verification/native-frame-acquire'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),source_accepted=False,game_frames=0,new_training=False,local_model_authored=False,goal_complete=False)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-frame-acquire-active.json',state)
    mark();n=None
    try:
        snapshot=out/'source-snapshot';snapshot.mkdir();paths=[Path(__file__),Path(fixture.__file__),*[ND/name for name in ['frame-acquire-native.c','frame-acquire-native.h','frame-acquire-shim.S','Makefile.frame-acquire']]]
        for path in paths:shutil.copy2(path,snapshot/path.name)
        commands=[['make','-f',str(ND/'Makefile.frame-acquire'),'frame-acquire','BUILD='+str(out/'build')]]
        provider=out/'fixture-loader.S';provider.write_text(PROVIDER_SOURCE);prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-')
        commands += [[prefix+'as','-m68000','-o',str(out/'fixture-loader.o'),str(provider)],[prefix+'ld','-Ttext='+hex(PROVIDER),'-e','fixture_frame_loader','-o',str(out/'fixture-loader.elf'),str(out/'fixture-loader.o')],[prefix+'objcopy','-O','binary',str(out/'fixture-loader.elf'),str(out/'fixture-loader.bin')]]
        with (out/'build.log').open('w') as log:
            for command in commands:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT);assert r.returncode==0,command
        binary=out/'build/frame-acquire.bin';payload=binary.read_bytes();helper=(out/'fixture-loader.bin').read_bytes();symbols={}
        for line in subprocess.check_output([prefix+'nm','--defined-only',str(out/'build/frame-acquire.elf')],text=True).splitlines():
            s=line.split()
            if len(s)==3:symbols[s[2]]=int(s[0],16)
        save(out/'symbols.json',symbols);(out/'compiled.asm').write_text(subprocess.check_output([prefix+'objdump','-dr',str(out/'build/frame-acquire.elf')],text=True))
        image,cases,zeros=vectors();assert len(image)==0x200000
        baseline=ROOT/'render-assets/biwn-inventory-baseline.bin'
        assert sha(baseline)=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3'
        assert image[ENTRY:END]==baseline.read_bytes()[ENTRY:END],'Original routine differs from independently pinned baseline'
        state['original_image_sha256']=sha(ROOT/'verification/zero-warm-startup-instruction-atlas.bin')
        original=bytearray(image);original[PROVIDER:PROVIDER+len(helper)]=helper;original[LOADER:LOADER+6]=b'\x4e\xf9'+PROVIDER.to_bytes(4,'big')
        candidate=bytearray(original);candidate[BASE:BASE+len(payload)]=payload;candidate[ENTRY:ENTRY+8]=b'\x4e\xf9'+BASE.to_bytes(4,'big')+b'\x4e\x71'
        if args.zero_only:cases=[]
        if args.limit:cases=cases[:args.limit];zeros=zeros[:args.limit]
        save(out/'fixtures.json',dict(normal=cases,zeros=zeros));state.update(status='running_native_and_ordered',binary_bytes=len(payload),binary=str(binary),binary_sha256=sha(binary),planned_normal=len(cases),planned_zero=len(zeros));mark()
        n=Native();coverage=set();rows=[];zero_rows=[];minimum=SP
        for index,case in enumerate(cases):
            x=trace(original,case,len(payload),len(helper),True);y=trace(candidate,case,len(payload),len(helper),False)
            if x[1]!=y[1]:save(out/'ordered-mismatch.json',dict(index=index,case=case,original=x[1],candidate=y[1]));raise AssertionError('Ordered public access/loader mismatch')
            assert normalize(y[0],x[0],len(payload))==x[0],'Ordered public final RAM mismatch'
            a=run(n,original,case,len(payload),len(helper),True,x[2]);b=run(n,candidate,case,len(payload),len(helper),False,y[2]);compare(out,index,case,a,b,len(payload),symbols);assert not a['faults'] and not b['faults']
            coverage.update(a['coverage']);minimum=min(minimum,b['minimum'],y[3]);rows.append(dict(case=index,CPU=b['cpu'],loader_calls=len(b['calls']),public_events=len(x[1]),original_steps=a['steps'],native_steps=b['steps'],original_cycles=a['cycles'],native_cycles=b['cycles'],read_changes_original=x[2],read_changes_native=y[2]))
            if index%64==0:state.update(completed_normal=len(rows));mark();print('Frame acquisition',len(rows),'/',len(cases),flush=True)
        state.update(status='running_zero_fault_resumption',completed_normal=len(rows));mark();save(out/'normal-results.json',rows)
        # For compiled zero fixtures discover reserved-index MOVEs from disassembly,
        # rather than emulate or suppress divide exceptions in a host callback.
        asm=(out/'compiled.asm').read_text();read_pcs=[int(m.group(1),16) for m in re.finditer(r'^\s*([0-9a-f]+):[^\n]*\bmovew (?:0x)?15b532\b',asm,re.M)]
        assert len(read_pcs)==3,read_pcs
        # Compiler layout need not follow execution order: each phase is identified
        # by a dedicated read PC; queues pop when any such instruction executes.
        for index,case in enumerate(zeros):
            a=run(n,original,case,len(payload),len(helper),True)
            changes=[]
            # Probe the *actual* compiled CPU and inject only the declared global
            # changes before a reserved-index read. No exception interception.
            b=run_zero(n,candidate,case,len(payload),len(helper),read_pcs)
            compare(out,index,case,a,b,len(payload),symbols);assert len(a['faults']) in [1,2]
            coverage.update(a['coverage']);minimum=min(minimum,b['minimum']);zero_rows.append(dict(case=index,SR=case['sr'],pattern=case['pattern'],faults=a['faults'],compiled_faults=b['faults'],CPU=b['cpu'],loader_calls=len(b['calls'])))
            if index%32==0:state.update(completed_zero=len(zero_rows));mark();print('DIVS zero/RTE',len(zero_rows),'/',len(zeros),flush=True)
        save(out/'zero-results.json',zero_rows)
        evidence=json.loads((ROOT/'verification/frame-resource-acquire-evidence-current.json').read_text());assembly=json.loads((Path(evidence['directory'])/'evidence.json').read_text())['assembly'];expected={int(a,16) for a in re.findall(r'^([0-9a-fA-F]+):',assembly,re.M)}
        save(out/'original-coverage.json',sorted(coverage));full=not args.limit and not args.zero_only
        if full:assert len(expected)==173 and expected<=coverage,sorted(expected-coverage)
        state.update(status='terminal_native_frame_acquire_CPU_RAM_loader_ordered_DIVS_pass' if full else 'terminal_native_frame_acquire_preflight_pass',completed_normal=len(rows),completed_zero=len(zero_rows),source_accepted=full,original_instruction_coverage=[len(expected&coverage),len(expected)],minimum_stack_address=hex(minimum),maximum_stack_bytes=SP-minimum,dependencies_sha256={str(path):sha(path) for path in paths},scope='Complete 173-instruction original control flow, two stack modes/all CCR on selected paths, stable and declared changing reserved-index reads; full D/A/PC/SR/USP/SSP and 2MB RAM including all 44 public LINK/MOVEM/scratch bytes. Separate ordered nonzero public bus and loader ABI captures. Loader is an actual guest fixture with caller-saved clobbers/scratch/index effects, not the production loader. Zero DIVS executes natively with inert RTE and declared source/relocated saved PC mapping. C-private 8KB stack excluded below public saves, loader arguments/registers checked separately; alternate exception stack excluded only after frame/CPU comparison. No arbitrary alias/handler/IRQ/timing/gameplay/console/whole-game proof; coordinator C adaptation, no local-model authorship or new training.');mark()
        if full:save(ROOT/'verification/native-frame-acquire-current.json',state)
        print(state['status'],len(rows),len(zero_rows),state['original_instruction_coverage'],flush=True)
    except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise
    finally:
        if n:n.close()

def run_zero(n,image,case,length,plen,read_pcs):
    # Reuse the same native loop, supplying every static read address to its
    # explicit zero-fixture injection branch through a temporary case field.
    return run(n,image,dict(case,_compiled_zero_read_pcs=read_pcs),length,plen,False)

if __name__=='__main__':main()
