"""Complete10430 native doorway contract; full CPU/RAM and width-correct ordered reads."""
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
BASE,ENTRY,END,SP,STOP=0x148000,0x10430,0x10520,0x1e0000,0x1f0000
ND=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
def signed16(x):return x if x<0x8000 else x-0x10000

def vectors():
    import random
    rng=random.Random(ENTRY);rows=[]
    patterns=[(0,0,4,'match'),(0xffff,0xfffe,4,'match'),(0x7fff,0x8000,4,'match'),(0x8000,0x8000,4,'match'),(0,0xffff,4,'match'),(0,1,4,'sentinel'),(0xffff,1,4,'sentinel')]
    patterns += [(0,1,d,k)for d in range(4)for k in ['match','mismatch','negative_byte']]
    patterns += [(0,1,d,k)for d,k in [(4,'match'),(0xffff,'match'),(0x8000,'match'),(4,'mismatch')]]
    patterns += [(0xffff,1,4,'match'),(0x8000,0x7fff,4,'match'),(0x7ffe,0x7fff,4,'match')]
    def make(index,count,direction,kind,j,sr,**extra):
        incoming=[rng.getrandbits(32)for _ in range(15)];delta=[0,0x7fff,0x8000,0xffff,32,64,0xffc0][j%7];nibble=(delta>>6)&15
        incoming[1]=(incoming[1]&0xffff0000)|delta;incoming[3]=(incoming[3]&0xffff0000)|(nibble if kind=='match'else(nibble+1)&15)
        return dict(index=index,count=count,direction=direction,kind=kind,sector=[0,1,0xffff,0x8000,0x7fff][j%5],object=0x80000+2*(j%3)|extra.get('object_tag',0),header_tag=extra.get('header_tag',0),record_tag=extra.get('record_tag',0),delta=delta,key_byte=nibble if kind=='match'else 0x80 if kind=='negative_byte'else(nibble+1)&15,target=0xffff if kind=='sentinel'else 312,bounds=[[0xffff,0x8000,0x7fff,0,1,0x400][(j+k)%6]for k in range(4)],incoming=incoming,sr=sr,**{k:v for k,v in extra.items()if k not in ['object_tag','header_tag','record_tag']})
    for mode in [0,0x2000]:
        for flags in range(32):
            for j,(index,count,direction,kind)in enumerate(patterns):rows.append(make(index,count,direction,kind,j,mode|flags))
            for j,(index,count,direction,kind,head,record,obj)in enumerate([(0,1,0,'match',0x80000000,0xff000000,0x80000000),(0xffff,1,4,'sentinel',0xff000000,0x80000000,0xff000000),(0,0,4,'match',0x80000000,0,0),(0x8000,0x7fff,0xffff,'match',0,0xff000000,0)]):rows.append(make(index,count,direction,kind,j,mode|flags,header_tag=head,record_tag=record,object_tag=obj))
    for j in range(96):
        c=make(rng.randrange(65536),rng.randrange(65536),rng.choice([0,1,2,3,4,0xffff,0x8000]),rng.choice(['match','mismatch','negative_byte','sentinel']),j,rng.choice([0,0x2000])|rng.randrange(32));rows.append(c)
    for delta in [-16,-8,0,4,8,12,16,24,32]:
        c=make(0,1,4,'match',0,0x201f,record_delta=delta);c['incoming'][1]&=0xffff0000;c['incoming'][3]&=0xffff0000;c['delta']=0;rows.append(c)
    return rows

def seed(image,c):
    b=bytearray(image);obj=c['object']&0xffffff;header=0x90000;record=(c['object']+c['record_delta'])&0xffffffff if 'record_delta'in c else 0xb0000|c.get('record_tag',0)
    def put(a,w,v):a&=0xffffff;b[a:a+w]=(v&((1<<(8*w))-1)).to_bytes(w,'big')
    put(obj+64,2,c['sector']);put(0x49bb4+4*signed16(c['sector']),4,header|c.get('header_tag',0));put(header+2,2,c['count']);put(header+12,4,(record-28*signed16(c['index']))&0xffffffff)
    for at in [6,12,74,78,82,86]:put(obj+at,2,0)
    if c['direction']<4:
        left,right=[(6,78),(74,6),(82,12),(12,86)][c['direction']];put(obj+left,2,c['delta']);put(obj+right,2,0)
    for at in [11,13,15,17]:put(record+at,1,c['key_byte'])
    for at,value in zip([18,20,22,24],c['bounds']):put(record+at,2,value)
    put(record+26,2,c['target'])
    b[SP:SP+12]=STOP.to_bytes(4,'big')+c['object'].to_bytes(4,'big')+c['index'].to_bytes(2,'big')+c['direction'].to_bytes(2,'big');return bytes(b)

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
    mem=bytearray(seed(bytes(0x200000),c))
    def r(a,w):a&=0xffffff;return int.from_bytes(mem[a:a+w],'big')
    def put(a,w,v):a&=0xffffff;mem[a:a+w]=(v&((1<<(8*w))-1)).to_bytes(w,'big')
    obj=c['object'];sector=r(obj+64,2);offset=(signed16(sector)*4)&0xffffffff;header=r(0x49bb4+offset,4);count=r(header+2,2)
    regs=c['incoming']+[SP+4,STOP,c['sr']&0xffe0];regs[9]=obj;regs[8]=header;regs[0]=offset&0xffff0000
    if signed16(c['index'])>=signed16(count):regs[17]|=4|(16 if sector&0x8000 else 0);return regs
    product=(signed16(c['index'])*28)&0xffffffff;base=r(header+12,4);address=(base+product)&0xffffffff;regs[8]=address;regs[0]=address&0xffff0000
    if r(address+26,2)==0xffff:regs[17]|=4|(16 if base+product>0xffffffff else 0);return regs
    key=regs[1]&0xffff;compare=regs[3]&0xffff
    if c['direction']<4:
        left,right=[(6,78),(74,6),(82,12),(12,86)][c['direction']];key=(r(obj+left,2)-r(obj+right,2))&0xffff;compare=r(address+11+2*c['direction'],1);compare=compare if compare<128 else compare-256
    nibble=(key>>6)&15;regs[1]=(regs[1]&0xffff0000)|nibble
    if compare!=nibble:regs[17]|=4|(16 if key&32 else 0);return regs
    put(obj+22,2,0);put(obj+24,2,r(address+26,2));put(obj+30,4,signed16(r(address+18,2))*64);put(obj+38,4,signed16(r(address+20,2))*64);put(obj+26,4,signed16(r(address+22,2))*64+r(obj+30,4))
    depth=(signed16(r(address+24,2))*64)&0xffffffff;base_z=r(obj+38,4);total=base_z+depth;put(obj+34,4,total);regs[0]=1;regs[17]|=16 if total>0xffffffff else 0;return regs

def changing_vectors():
    rows=[]
    for mode in [0,0x2000]:
        for flags in range(32):
            for tagged in [False,True]:
                for kind in range(6):
                    obj=0x80000|(0x80000000 if tagged else 0);record=0xb0000|(0xff000000 if tagged else 0)
                    c=dict(index=0,count=1,direction=4,kind='changing',sector=0,object=obj,header_tag=0xff000000 if tagged else 0,record_tag=record&0xff000000,delta=0,key_byte=0,target=312,bounds=[1,2,3,4],incoming=[0x80000000]*15,sr=mode|flags)
                    if kind==0:c['read_queues']=[(record+26,2,[312,41])]
                    elif kind==1:c['read_queues']=[(obj+30,4,[0xffffffff])]
                    elif kind==2:c['read_queues']=[(obj+38,4,[0xffffffff])]
                    elif kind==3:c.update(direction=0,delta=7*64,key_byte=0,read_queues=[(record+11,1,[7])])
                    elif kind==4:c.update(direction=2,delta=0,key_byte=3,read_queues=[(obj+82,2,[3*64])])
                    else:c['read_queues']=[(record+24,2,[0xffff])]
                    rows.append(c)
    return rows

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path);p.add_argument('--limit',type=int);p.add_argument('--no-publish',action='store_true');a=p.parse_args();source=a.source.resolve()
    out=ROOT/'verification/native-doorway'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='building',pid=os.getpid(),directory=str(out),source=str(source),source_sha256=sha(source),source_accepted=False,game_frames=0,new_training=False,default_promoted=False,whole_game_complete=False)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-doorway-active.json',state)
    mark();n=None
    try:
        paths=[Path(__file__),Path(fixtures.__file__),source,ND/'doorway-shim.S',ND/'Makefile.doorway',ND/'doorway-native.h'];snap=out/'source-snapshot';snap.mkdir()
        for path in paths:shutil.copy2(path,snap/path.name)
        result=subprocess.run(['make','-f',str(ND/'Makefile.doorway'),'doorway','BUILD='+str(out/'build'),'DOOR_SOURCE='+str(source)],capture_output=True,text=True);(out/'build.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
        binary=out/'build/doorway.bin';payload=binary.read_bytes();baseline=ROOT/'render-assets/biwn-inventory-baseline.bin';assert sha(baseline)=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3';image=baseline.read_bytes();candidate=bytearray(image);candidate[BASE:BASE+len(payload)]=payload;candidate[ENTRY:ENTRY+8]=b'\x4e\xf9'+BASE.to_bytes(4,'big')+b'\x4e\x71';cases=vectors();cases=cases[:a.limit] if a.limit else cases;save(out/'fixtures.json',cases)
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
        state.update(status='terminal_native_geometry_select_preflight_pass' if a.limit else 'terminal_native_doorway_v2_CPU_RAM_ordered_pass',source_accepted=not a.limit,native_cases=len(rows),changing_coordinate_cases=len(dynamic),ordered_cases=len(rows)+len(dynamic),original_instruction_coverage=[len(locations&coverage),len(locations)],binary=str(binary),binary_sha256=sha(binary),binary_bytes=len(payload),max_private_stack_bytes=SP-minimum,dependencies_sha256={str(p):sha(p) for p in paths},scope='Complete original10430..1051E doorway function. Full nativeD/A/PC/SR/USP/SSP/public2MBRAM plus logical ordered accesses, width-correct1/2/4byte changing-read injection and independent native/tracer publicRAM agreement. Signed index/count, record sentinel andcarry, directions0..3and invalid directions, byte sign extension, fullD0/partialD1/A0/A1/CCR, tagged pointers and nine actor/record aliases. Original register saves/private8KBscratch/code/entry excluded. Coordinator fullABI/layout/reference; earlier local portable body has narrower provenance. No arbitraryfault/IRQ/timing/final-link/disc/gameplay/whole-game proof.');mark()
        if not a.no_publish and not a.limit:save(ROOT/'verification/native-doorway-current.json',state)
        print(state['status'],len(rows),len(dynamic),len(payload),state['original_instruction_coverage'],flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
    finally:
        if n:n.close()
if __name__=='__main__':main()
