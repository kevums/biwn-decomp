"""Complete102C4 scanner; width-correct external injection and native/trace RAM agreement."""
import argparse,json,os,shutil,subprocess,ctypes as ctypes
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE,UC_PROT_ALL
from unicorn.m68k_const import *
import check_biwn_native_frame_reference_single_lean as fixtures
from check_biwn_native_resource_release import REGS
from check_biwn_native_button_digit import ROOT,sha,save
Native=fixtures.Native
BASE,ENTRY,END,SP,STOP=0x148000,0x102c4,0x1039c,0x1e0000,0x1f0000
ND=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
def signed16(x):return x if x<0x8000 else x-0x10000

def scenario(kind,count):
    records={};match=[0,0,16,16];reject=[16,16,1,1]
    if kind=='highest':records[count-1]=match
    elif kind=='lowest':records[0]=match
    elif kind=='multiple':records[0]=match;records[count-1]=match
    elif kind=='x_upper_equal':records[0]=[0,0,0,16]
    elif kind=='x_carry':records[0]=[0xffff,0,1,16]
    elif kind=='z_upper_equal':records[0]=[0,0,16,0]
    elif kind=='z_carry':records[0]=[0,0xffff,16,1]
    elif kind=='carry_retained':records[1]=[0xffff,0,1,16];records[0]=reject
    elif kind=='carry_reset':records[1]=[0xffff,0,1,16];records[0]=[0,0,0,16]
    elif kind=='signed_wrap':records[1]=[0xffff,0x8000,2,0x8001]
    return {str(i):v for i,v in records.items()}

def vectors():
    import random
    rng=random.Random(ENTRY);rows=[]
    patterns=[(0,'none'),(0x8001,'none'),(0xffff,'none'),(1,'highest'),(3,'highest'),(3,'lowest'),(3,'multiple'),(3,'none'),(1,'x_upper_equal'),(1,'x_carry'),(1,'z_upper_equal'),(1,'z_carry'),(2,'carry_retained'),(2,'carry_reset'),(3,'signed_wrap'),(0x8000,'highest')]
    def make(count,kind,j,sr,**tags):
        xcell=0 if kind=='signed_wrap' else j%16;zcell=0 if kind=='signed_wrap' else(j*3)%16
        return dict(count=count,kind=kind,sector=[0,1,0xffff,0x8000,0x7fff][j%5],object=0x80000+2*(j%3)|tags.get('object_tag',0),header_tag=tags.get('header_tag',0),record_tag=tags.get('record_tag',0),position=[(rng.getrandbits(32)&0xfffffc3f)|(xcell<<6),(rng.getrandbits(32)&0xfffffc3f)|(zcell<<6)],records=scenario(kind,count),incoming=[rng.getrandbits(32)for _ in range(15)],sr=sr)
    for mode in [0,0x2000]:
        for flags in range(32):
            for j,(count,kind)in enumerate(patterns):rows.append(make(count,kind,j,mode|flags))
            for j,(count,kind,head,record,obj)in enumerate([(3,'lowest',0x80000000,0,0),(3,'highest',0xff000000,0x80000000,0xff000000),(0,'none',0x80000000,0xff000000,0x80000000),(2,'carry_retained',0,0xff000000,0)]):rows.append(make(count,kind,j,mode|flags,header_tag=head,record_tag=record,object_tag=obj))
    for j in range(96):
        count=rng.randrange(1,9);c=make(count,'none',j,rng.choice([0,0x2000])|rng.randrange(32));c['records']={str(i):[rng.randrange(65536)for _ in range(4)]for i in range(count)};rows.append(c)
    c=make(0x8000,'none',0,0x201f);c['instruction_limit']=2000000;c['long_complete_reverse_scan']=True;rows.append(c)
    return rows

def seed(image,c):
    b=bytearray(image);obj=c['object']&0xffffff;header=0x90000;records=0xa0000;count=c['count'];index=(count-1)&0xffff
    def put(a,w,v):a&=0xffffff;b[a:a+w]=v.to_bytes(w,'big')
    put(obj+64,2,c['sector']);put(obj+4,4,c['position'][0]);put(obj+10,4,c['position'][1]);put(0x49bb4+4*signed16(c['sector']),4,header|c.get('header_tag',0));put(header,2,count);put(header+8,4,records|c.get('record_tag',0))
    if not index&0x8000:
        row=bytearray(20)
        for offset,value in [(10,16),(14,16),(16,1),(18,1)]:row[offset:offset+2]=value.to_bytes(2,'big')
        b[records:records+20*count]=bytes(row)*count
    for key,values in c.get('records',{}).items():
        for offset,value in zip([10,14,16,18],values):put(records+20*int(key)+offset,2,value)
    for key,values in c.get('secondary_records',{}).items():
        for offset,value in zip([10,14,16,18],values):put(0xb0000+20*int(key)+offset,2,value)
    b[SP:SP+8]=STOP.to_bytes(4,'big')+c['object'].to_bytes(4,'big');return bytes(b)
def normalize(ram,reference,length):
    b=bytearray(ram)
    for lo,hi in [(BASE,BASE+length),(ENTRY,ENTRY+8),(SP-8192,SP)]:b[lo:hi]=reference[lo:hi]
    return bytes(b)
def allowed(pc,length,original):return ENTRY<=pc<END if original else pc==ENTRY or BASE<=pc<BASE+length
def trace(image,c,length,original):
    u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);backing=ctypes.create_string_buffer(seed(image,c));base_pointer=ctypes.addressof(backing)
    for alias in [0,0x80000000,0xff000000]:u.mem_map_ptr(alias,0x200000,UC_PROT_ALL,base_pointer)
    u.reg_write(UC_M68K_REG_SR,c['sr'])
    for r,v in zip(REGS,c['incoming']+[SP]):u.reg_write(r,v)
    events=[];changes=[];visits=Counter();current=ENTRY;external={a:(w,list(values)) for a,w,values in c.get('read_queues',[])}
    def internal(a,w):return SP-8192<=a and a+w<=SP or BASE<=a and a+w<=BASE+length
    def code(e,pc,w,_):
        nonlocal current
        assert allowed(pc,length,original),hex(pc);current=pc;visits[pc]+=1
    def read(e,t,a,w,v,_):
        if internal(a,w):return
        if a in external and external[a][1]:
            assert w==external[a][0];value=external[a][1].pop(0);e.mem_write(a,value.to_bytes(w,'big'));changes.append([current,visits[current],a,w,value])
        events.append(['r',a,w,int.from_bytes(e.mem_read(a,w),'big')])
    def write(e,t,a,w,v,_):
        if not internal(a,w):events.append(['w',a,w,v&((1<<(8*w))-1)])
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(ENTRY,STOP,count=c.get('instruction_limit',20000));assert u.reg_read(UC_M68K_REG_PC)==STOP
    return bytes(u.mem_read(0,0x200000)),events,changes
def native(n,image,c,length,original,changes=()):
    l=n.lib;n.device.seed(seed(image,c),0);l.m68k_pulse_reset();l.m68k_set_irq(0);supervisor=bool(c['sr']&0x2000)
    l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,SP if supervisor else 0x1ff000);l.m68k_set_reg(17,0);l.m68k_set_reg(15,0x1fe000 if supervisor else SP);l.m68k_set_reg(17,c['sr'])
    for i,v in enumerate(c['incoming']+[SP]):l.m68k_set_reg(i,v)
    l.m68k_set_reg(16,ENTRY);coverage=set();visits=Counter();pending=list(changes);minimum=SP;cycles=0
    for steps in range(c.get('instruction_limit',20000)):
        pc=l.m68k_get_reg(None,16)
        if pc==STOP:break
        assert allowed(pc,length,original),hex(pc);coverage.add(pc);visits[pc]+=1;minimum=min(minimum,l.m68k_get_reg(None,15))
        if pending and [pc,visits[pc]]==pending[0][:2]:_,_,a,w,v=pending.pop(0);n.device.direct(a&0xffffff,w,v)
        cycles+=l.m68k_execute(1)
    else:raise AssertionError('Geometry scanion instruction limit')
    assert not pending,pending;cpu=[l.m68k_get_reg(None,i) for i in range(18)];cpu.extend([n.prefix[16] if supervisor else cpu[15],cpu[15] if supervisor else n.prefix[17]]);assert cpu[15]==SP+4
    return n.device.ram(),cpu,coverage,steps,cycles,minimum
def expected(c):
    mem=seed(bytes(0x200000),c)
    def r(a,w):a&=0xffffff;return int.from_bytes(mem[a:a+w],'big')
    obj=c['object'];header=r(0x49bb4+4*signed16(r(obj+64,2)),4);position_z=r(obj+10,4);shifted=(position_z>>6)|(0xfc000000 if position_z&0x80000000 else 0);x=(r(obj+4,4)>>6)&15;z=shifted&15;count=r(header,2);index=(count-1)&0xffff;carry=count==0
    regs=c['incoming']+[SP+4,STOP,c['sr']&0xffe0];regs[0]=shifted&0xffff0000;regs[1]=(regs[1]&0xffff0000)|index;regs[8]=header
    if index&0x8000:regs[17]|=4|(16 if carry else 0);return regs
    while True:
        record=(r(header+8,4)+20*index)&0xffffffff;regs[9]=record
        if x>=signed16(r(record+10,2)):
            total=r(record+10,2)+r(record+16,2);carry=total>0xffff
            if x<signed16(total&0xffff) and z>=signed16(r(record+14,2)):
                total=r(record+14,2)+r(record+18,2);carry=total>0xffff
                if z<signed16(total&0xffff):
                    regs[0]=1;regs[1]=position_z&0xfffffc00;regs[8]=((position_z&0xfffffc00)+signed16((r(record+14,2)<<6)&0xffff)+signed16((r(record+18,2)<<6)&0xffff))&0xffffffff;regs[17]|=16 if r(record+18,2)&0x400 else 0;return regs
        index=(index-1)&0xffff
        if index==0xffff:break
    regs[0]=0;regs[1]=(regs[1]&0xffff0000)|0xffff;regs[17]|=4|(16 if carry else 0);return regs

def changing_vectors():
    rows=[]
    for mode in [0,0x2000]:
        for flags in range(32):
            for tagged in [False,True]:
                for kind in range(6):
                    obj=0x80000|(0x80000000 if tagged else 0);head=0x90000|(0xff000000 if tagged else 0);record=0xa0000|(0x80000000 if tagged else 0)
                    c=dict(count=1,kind='changing',sector=0,object=obj,header_tag=head&0xff000000,record_tag=record&0xff000000,position=[0,0],records={'0':[0,0,16,16]},incoming=[0x80000000]*15,sr=mode|flags)
                    if kind==0:c['read_queues']=[(obj+4,4,[0,0x80000001])]
                    elif kind==1:c['read_queues']=[(record+10,2,[0,0xffff,7])];c['records']['0'][2]=2
                    elif kind==2:c['read_queues']=[(record+14,2,[0,0xffff,7])];c['records']['0'][3]=2
                    elif kind==3:c['read_queues']=[(record+18,2,[16,0x400])]
                    elif kind==4:c['read_queues']=[(obj+76,4,[0x7fffffff])]
                    else:
                        c.update(count=3,records={},secondary_records={'1':[0,0,16,16]});c['read_queues']=[(head+8,4,[record,0xb0000|c['record_tag']])]
                    rows.append(c)
    return rows
def main():
    p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path);p.add_argument('--limit',type=int);p.add_argument('--no-publish',action='store_true');a=p.parse_args();source=a.source.resolve()
    out=ROOT/'verification/native-geometry-scan-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='building',pid=os.getpid(),directory=str(out),source=str(source),source_sha256=sha(source),source_accepted=False,game_frames=0,new_training=False,default_promoted=False,whole_game_complete=False)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-geometry-scan-v2-active.json',state)
    mark();n=None
    try:
        paths=[Path(__file__),Path(fixtures.__file__),source,ND/'geometry-scan-shim.S',ND/'Makefile.geometry-scan',ND/'geometry-scan-native.h'];snap=out/'source-snapshot';snap.mkdir()
        for path in paths:shutil.copy2(path,snap/path.name)
        result=subprocess.run(['make','-f',str(ND/'Makefile.geometry-scan'),'geometry-scan','BUILD='+str(out/'build'),'SCAN_SOURCE='+str(source)],capture_output=True,text=True);(out/'build.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
        binary=out/'build/geometry-scan.bin';payload=binary.read_bytes();baseline=ROOT/'render-assets/biwn-inventory-baseline.bin';assert sha(baseline)=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3';image=baseline.read_bytes();candidate=bytearray(image);candidate[BASE:BASE+len(payload)]=payload;candidate[ENTRY:ENTRY+8]=b'\x4e\xf9'+BASE.to_bytes(4,'big')+b'\x4e\x71';cases=vectors();cases=cases[:a.limit] if a.limit else cases;save(out/'fixtures.json',cases)
        n=Native();rows=[];dynamic=[];coverage=set();minimum=SP;state.update(status='checking_native_ordered',planned=len(cases));mark()
        def compare(c,index,stable):
            nonlocal minimum
            x=trace(image,c,len(payload),True);y=trace(candidate,c,len(payload),False)
            if x[1]!=y[1] or normalize(y[0],x[0],len(payload))!=x[0]:
                save(out/'ordered-mismatch.json',dict(case=index,parameters=c,original=x[1],candidate=y[1]));raise AssertionError(('Ordered reads/RAM',index))
            left=native(n,image,c,len(payload),True,x[2]);right=native(n,candidate,c,len(payload),False,y[2]);normalized=normalize(right[0],left[0],len(payload))
            if left[1]!=right[1] or normalized!=left[0]:save(out/'mismatch.json',dict(case=index,parameters=c,original_CPU=left[1],compiled_CPU=right[1],RAM_differences=[hex(i) for i,(a,b) in enumerate(zip(left[0],normalized)) if a!=b][:30]));raise AssertionError('Full CPU/RAM')
            assert normalize(left[0],x[0],len(payload))==x[0],('Native/tracer original publicRAM',index)
            assert normalize(right[0],y[0],len(payload))==y[0],('Native/tracer compiled publicRAM',index)
            if stable:assert right[1][:18]==expected(c),('Independent return contract',index)
            assert right[0][BASE:BASE+len(payload)]==payload;coverage.update(left[2]);minimum=min(minimum,right[5]);return dict(case=index,CPU=right[1],ordered_events=len(x[1]),original_steps=left[3],native_steps=right[3],original_cycles=left[4],native_cycles=right[4],source_read_updates=x[2],compiled_read_updates=y[2])
        for i,c in enumerate(cases):
            rows.append(compare(c,i,True))
            if i%256==0:state['completed']=len(rows);mark();print('Geometry scan',len(rows),'/',len(cases),flush=True)
        dynamic_cases=changing_vectors();save(out/'changing-fixtures.json',dynamic_cases)
        for c in dynamic_cases:dynamic.append(compare(c,len(dynamic),False))
        save(out/'results.json',rows);save(out/'changing-coordinate-results.json',dynamic);prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');asm=subprocess.check_output([prefix+'objdump','-D','-b','binary','-m','m68k:68000','--start-address='+hex(ENTRY),'--stop-address='+hex(END),str(baseline)],text=True);(out/'original.asm').write_text(asm);locations={int(line.split(':',1)[0].strip(),16) for line in asm.splitlines() if ':' in line and len(line.split('\t'))>=3 and line.split('\t')[2].strip()};assert locations<=coverage
        state.update(status='terminal_native_geometry_select_preflight_pass' if a.limit else 'terminal_native_geometry_scan_v2_CPU_RAM_ordered_pass',source_accepted=not a.limit,native_cases=len(rows),changing_coordinate_cases=len(dynamic),ordered_cases=len(rows)+len(dynamic),original_instruction_coverage=[len(locations&coverage),len(locations)],binary=str(binary),binary_sha256=sha(binary),binary_bytes=len(payload),max_private_stack_bytes=SP-minimum,dependencies_sha256={str(p):sha(p) for p in paths},scope='Complete original102C4..1039Ascanning selector. Full native D/A/PC/SR/USP/SSP and2MBpublicRAM plus ordered access widths/values; original register saves,private8KB scratch and code/entry excluded. All32CCR/two stack modes, reverse first-match/no-match/signed wrapping/carry retention, tagged object/header/record pointers, one complete32768entry miss and controlled changing coordinates/WORD bounds/LONG record-base/installed-bound reads. Coordinator ABI/header/known bounds helper; kernel provenance separate. No arbitraryalias/fault/IRQ/physical timing/final-link/disc/gameplay/whole-game proof.');mark()
        if not a.no_publish and not a.limit:save(ROOT/'verification/native-geometry-scan-v2-current.json',state)
        print(state['status'],len(rows),len(dynamic),len(payload),state['original_instruction_coverage'],flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
    finally:
        if n:n.close()
if __name__=='__main__':main()
