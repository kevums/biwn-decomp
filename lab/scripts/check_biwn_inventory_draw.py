"""Original whole CPU drawing routine vs C command protocol with modeled graphics.

Original money formatter executes. Sprite/text callees alone are RTS fixtures;
their arguments and optional RAM/MMIO effects are compared, not their pixels.
"""
import ctypes as c
from datetime import datetime,timezone
import hashlib,json,os,random,subprocess,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import unicorn
import extract_biwn_stage as stage
sys.path.insert(0,str(stage.ROOT));import binary_tools
SP,STOP=0x1ff000,0x1ffe00
REGS=[UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6]
class Text(c.Structure):_fields_=[('x',c.c_uint16),('y',c.c_uint16),('text_address',c.c_uint32),('target',c.c_uint32),('target_flags',c.c_uint32),('font',c.c_uint32),('color',c.c_uint16),('mode',c.c_uint16),('local_text',c.c_char_p)]
R8=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint8));R16=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint16));R32=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint32))
W32=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint32);SPRITE=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint32,c.c_uint32);TEXT=c.CFUNCTYPE(c.c_int,c.c_void_p,c.POINTER(Text))
class Bus(c.Structure):_fields_=[('read8',R8),('read16',R16),('read32',R32),('write32',W32),('sprite',SPRITE),('text',TEXT),('context',c.c_void_p)]


class Memory:
    def __init__(self,image,case):
        self.ram=bytearray(0x200000);self.ram[0x4000:0x4000+len(image)]=image;self.mmio=bytearray(0x1000);self.case=case
        self.ram[0xe2b8:0xe2ba]=b'\x4e\x75';self.ram[0x149ae:0x149b0]=b'\x4e\x75'
        self.trace=[];self.errors=[];self.effects=[];self.calls=0;self.text_calls=0;self.sprite_calls=0;self.start_reads=0;self.header_reads={};self.fail_read=None;self.fail_write=None;self.fail_text=None;self.fail_sprite=False
        self.put(0x49d1e,4,case['money']);self.put(0x49d54,2,case['start']);self.put(0x49d56,2,case['selected'])
        ids={'empty':[0]*10,'real':[65,36,41,70,0,0,0,0,0,0],'full':[65,36,41,70,65,36,41,70,65,36]}[case['layout']]
        for i,value in enumerate(ids):self.put(0x49d2c+i*2,2,value)
        if 'synthetic_mapping' in case:
            item,mapped=case['synthetic_mapping'];signed_item=item if item<0x8000 else item-0x10000;signed_mapped=mapped if mapped<0x80 else mapped-0x100
            for i in range(10):self.put(0x49d2c+i*2,2,item)
            self.put(0x42000+signed_item,1,mapped);self.put(0x6e6ac+signed_mapped*4,4,0x100)
            for field in [10,14,18]:self.put(0x46a60+signed_mapped*22+field,4,0x1b709+field)
        if case.get('invalid_start'):
            for address in range(0x49d1a,0x49d2c,2):self.put(address,2,0)
        self.headers={0x6e6a0+self.peek(0x6e6ac+i*4,4)for i in [0,4,38,44]}
        if 'dimensions'in case:
            for address in self.headers:self.put(address,1,case['dimensions'][0]);self.put(address+1,1,case['dimensions'][1])
    def region(self,address,width):
        if 0<=address and address+width<=len(self.ram):return self.ram,address
        if 0xf02000<=address and address+width<=0xf03000:return self.mmio,address-0xf02000
        raise ValueError('outside modeled memory: '+hex(address))
    def peek(self,address,width):
        data,offset=self.region(address,width);return int.from_bytes(data[offset:offset+width],'big')
    def put(self,address,width,value):
        data,offset=self.region(address,width);data[offset:offset+width]=(value&((1<<(width*8))-1)).to_bytes(width,'big')
    def read(self,address,width):
        if self.fail_read==(address,width):raise RuntimeError('injected bus read failure')
        if self.case.get('profile')=='read-varying':
            if address==0x49d54 and width==2:
                self.put(address,width,(self.case['start']+self.start_reads*3)%10);self.start_reads+=1
            if width==1 and (address in self.headers or address-1 in self.headers):
                n=self.header_reads.get(address,0);self.header_reads[address]=n+1;self.put(address,1,(126+n*31)&255)
        value=self.peek(address,width);self.trace.append(('r',address,width,value));return value
    def write(self,address,value):
        if self.fail_write==address:raise RuntimeError('injected bus write failure')
        assert 0xf02200<=address<=0xf0226c and address%4==0
        self.put(address,4,value);self.trace.append(('w',address,4,value))
    def dependency_effects(self):
        self.effects=[]
        if self.case.get('profile')=='callback-mutate':
            for address,width,value in [(0x49d54,2,(self.peek(0x49d54,2)+3)%10),(0x49d56,2,(self.peek(0x49d56,2)+1)%10),(0xf02214,4,0xA5000000+self.calls)]:
                self.put(address,width,value);self.effects.append((address,width,value));self.trace.append(('dependency_write',address,width,value))
    def sprite(self,base,index,dest):
        if self.fail_sprite:raise RuntimeError('injected sprite failure')
        self.calls+=1;self.sprite_calls+=1;self.trace.append(('sprite',base,index,dest));self.dependency_effects()
    def text(self,args):
        if self.fail_text==self.text_calls:raise RuntimeError('injected text failure')
        self.calls+=1;self.text_calls+=1;self.trace.append(('text',*args));self.dependency_effects()


def original(image,case,incoming):
    memory=Memory(image,case);cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    cpu.mem_map(0,0x200000);cpu.mem_map(0xf02000,0x1000);cpu.mem_write(0,bytes(memory.ram));cpu.mem_write(SP,STOP.to_bytes(4,'big'))
    for reg,value in zip(REGS,incoming):cpu.reg_write(reg,value)
    cpu.reg_write(UC_M68K_REG_A7,SP);in_formatter=False;steps=[];format_calls=[];text_clobbers=[];formatter_scratch_writes=[]
    def code(engine,address,size,_):
        nonlocal in_formatter
        if address==0x1b45a:
            in_formatter=True;s=engine.reg_read(UC_M68K_REG_A7)
            args=[int.from_bytes(engine.mem_read(s+i,4),'big')for i in [4,8,12]]
            assert args[:2]==[SP-24,0x1b780];format_calls.append(args)
        if address==0x1b838:in_formatter=False
        assert 0x1b786<=address<0x1bc78 or 0x1b160<=address<0x1b478 or (in_formatter and 0xe61c<=address<0xe68c) or address in [0xe2b8,0x149ae],hex(address)
        steps.append(address)
        if address==0xe2b8:
            s=engine.reg_read(UC_M68K_REG_A7);args=[int.from_bytes(engine.mem_read(s+i,4),'big')for i in [4,8,12]];memory.sprite(*args)
        elif address==0x149ae:
            s=engine.reg_read(UC_M68K_REG_A7)
            def get(offset,width):return int.from_bytes(engine.mem_read(s+offset,width),'big')
            pointer=get(8,4);local=None
            if pointer==SP-24:
                local=bytes(engine.mem_read(pointer,24)).split(b'\0',1)[0].decode('ascii');pointer=0
            args=[get(4,2),get(6,2),pointer,get(12,4),get(16,4),get(20,4),get(24,2),get(26,2),local]
            memory.text(args)
            if case.get('clobber',True):
                values=[0xa5a50000+memory.calls,0xdead0000+memory.calls,0x123400+memory.calls*4,0x567800+memory.calls*4]
                for reg,value in zip([UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_A0,UC_M68K_REG_A1],values):engine.reg_write(reg,value)
                text_clobbers.append(values)
        if address in [0xe2b8,0x149ae]:
            for destination,width,value in memory.effects:engine.mem_write(destination,value.to_bytes(width,'big'))
    def read(engine,access,address,size,value,_):
        if in_formatter or SP-0x1000<=address<SP+8:return
        engine.mem_write(address,memory.read(address,size).to_bytes(size,'big'))
    def write(engine,access,address,size,value,_):
        if SP-0x1000<=address<SP+8:return
        if in_formatter:
            assert size==1 and 0x15b7a0<=address<0x15b7aa,(hex(address),size)
            memory.put(address,size,value);formatter_scratch_writes.append((address,size,value));return
        assert not in_formatter and size==4,(hex(address),size)
        memory.write(address,value&0xffffffff)
    cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write)
    cpu.emu_start(0x1b786,STOP,count=50000,timeout=2_000_000)
    assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
    for i,reg in enumerate(REGS):
        if i not in [0,1,8,9]:assert cpu.reg_read(reg)==incoming[i],(i,hex(cpu.reg_read(reg)),hex(incoming[i]))
    assert bytes(cpu.mem_read(0,SP-0x1000))==bytes(memory.ram[:SP-0x1000])
    assert bytes(cpu.mem_read(SP+8,0x200000-SP-8))==bytes(memory.ram[SP+8:])
    assert bytes(cpu.mem_read(0xf02000,0x1000))==bytes(memory.mmio)
    assert len(format_calls)==1 and format_calls[0][2]==case['money']
    return memory,{'instructions':len(steps),'original_formatter_calls':format_calls,'formatter_internal_scratch_writes_excluded_from_C_protocol':formatter_scratch_writes,'callee_saved_registers_unchanged':True,'private_stack_return_checked':True,'text_callback_caller_saved_clobbers':text_clobbers}


def translated(fn,memory,missing=None):
    def reader(width):
        def callback(_,address,value):
            try:value[0]=memory.read(address,width);return 0
            except Exception as error:memory.errors.append(repr(error));return 1
        return callback
    def writer(_,address,value):
        try:memory.write(address,value);return 0
        except Exception as error:memory.errors.append(repr(error));return 1
    def sprite(_,base,index,dest):
        try:memory.sprite(base,index,dest);return 0
        except Exception as error:memory.errors.append(repr(error));return 1
    def text(_,pointer):
        obj=pointer.contents;args=[obj.x,obj.y,obj.text_address,obj.target,obj.target_flags,obj.font,obj.color,obj.mode,obj.local_text.decode()if obj.local_text is not None else None]
        try:memory.text(args);return 0
        except Exception as error:memory.errors.append(repr(error));return 1
    types=[R8,R16,R32,W32,SPRITE,TEXT];callbacks=[R8(reader(1)),R16(reader(2)),R32(reader(4)),W32(writer),SPRITE(sprite),TEXT(text)]
    if missing is not None:callbacks[missing]=types[missing]()
    bus=Bus(*callbacks,None);return fn(c.byref(bus))


def main():
    root=stage.ROOT;session=Path(json.loads((root/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes()
    assert stage.digest(image)==stage.STAGE_SHA and image[0x1b780-0x4000:0x1b786-0x4000]==b'$%ld\0\0'
    out=root/'verification/biwn-inventory-draw'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=root/'projects/black-ice-white-noise/restoration';library=out/'libbiwn_inventory_draw.dylib';compiler=['clang','-dynamiclib','-std=c11','-Wall','-Wextra','-Werror','-O2',str(source/'biwn_inventory_draw.c'),'-o',str(library)]
    subprocess.run(compiler,check=True,capture_output=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    lib=c.CDLL(str(library));fn=lib.biwn_inventory_draw;fn.argtypes=[c.POINTER(Bus)];fn.restype=c.c_int
    rng=random.Random(0x1b786);money=[0,200,0xffffffff,0x80000000,0x7fffffff,123456789,0xffed2979];cases=[]
    for start in range(10):
        for selected in range(10):
            for layout in ['empty','real','full']:cases.append({'start':start,'selected':selected,'layout':layout,'money':money[len(cases)%len(money)],'profile':'static','clobber':bool(len(cases)%2)})
    for dimensions in [(1,1),(94,31),(95,32),(255,255),(0,0),(200,65)]:
        cases.append({'start':0,'selected':0,'layout':'full','money':200,'profile':'static','dimensions':dimensions})
    for profile in ['callback-mutate','read-varying']:
        for start in [0,4,9]:
            for layout in ['real','full']:cases.append({'start':start,'selected':9,'layout':layout,'money':0x80000000,'profile':profile})
    for start in [0xffff,0xfffc,0x8000,0x7fff]:
        for selected in [0,0xffff]:cases.append({'start':start,'selected':selected,'layout':'empty','money':0,'profile':'static','invalid_start':True})
    for item,mapped in [(0xffff,0xff),(0x8000,0x80),(0x7fff,0x7f),(0x1234,0xfe)]:
        cases.append({'start':9,'selected':0,'layout':'full','money':200,'profile':'static','synthetic_mapping':[item,mapped]})
    rows=[]
    for index,case in enumerate(cases):
        (out/'status.json').write_text(json.dumps({'status':'running','case':index,'parameters':case})+'\n')
        incoming=[rng.getrandbits(32)for _ in REGS];a,observed=original(image,case,incoming);b=Memory(image,case);result=translated(fn,b)
        equal_ram=a.ram[:0x15b7a0]==b.ram[:0x15b7a0] and a.ram[0x15b7aa:]==b.ram[0x15b7aa:]
        if result!=0 or a.trace!=b.trace or not equal_ram or a.mmio!=b.mmio:
            save={'case':case,'status':result,'CPU_trace':a.trace,'C_trace':b.trace,'errors':b.errors};(out/'mismatch.json').write_text(json.dumps(save,indent=2)+'\n');raise AssertionError('CPU/Cprotocol mismatch: '+str(out/'mismatch.json'))
        commands=sum(e[0]=='w'and e[1]==0xf02238 for e in a.trace)
        rows.append({'case':case,'CPU':observed,'trace':a.trace,'sprite_calls':a.sprite_calls,'text_calls':a.text_calls,'command_writes':commands,'money_text':next(e[-1]for e in a.trace if e[0]=='text'),
                     'final_MMIO_sha256':hashlib.sha256(a.mmio).hexdigest()})
    guards=[];assert fn(None)==1;guards.append({'case':'null_bus','status':1})
    base={'start':0,'selected':0,'layout':'real','money':200,'profile':'static'}
    for missing in range(6):
        m=Memory(image,base);result=translated(fn,m,missing);assert result==1 and not m.trace;guards.append({'case':'missing_callback','index':missing,'status':result})
    for name,r,w,t,s in [('money_read',(0x49d1e,4),None,None,False),('start_read',(0x49d54,2),None,None,False),('initial_write',None,0xf02200,None,False),('money_text',None,None,0,False),('sprite',None,None,None,True),('item_text',None,None,1,False)]:
        m=Memory(image,base);m.fail_read=r;m.fail_write=w;m.fail_text=t;m.fail_sprite=s;result=translated(fn,m);expected=3 if t is not None or s else 2
        assert result==expected,(name,result);guards.append({'case':name,'status':result,'prior_trace':m.trace,'errors':m.errors})
    (out/'fixtures.json').write_text(json.dumps(rows,indent=2)+'\n');(out/'guards.json').write_text(json.dumps(guards,indent=2)+'\n')
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'whole_CPU_inventory_drawing_protocol_matches_portable_C','directory':str(out),'stage_sha256':stage.STAGE_SHA,
            'original_interval':'[0x1b786,0x1bc78)','original_bytes_sha256':hashlib.sha256(image[0x1b786-0x4000:0x1bc78-0x4000]).hexdigest(),
            'portable_components':1,'CPU_cases':len(rows),'host_guard_cases':len(guards),'CPU_model':'Unicorn'+unicorn.__version__+' M68000',
            'matched':['All routine-level RAM read addresses/widths/values, externalword write addresses/values/order, and sprite/text call arguments.','Five circularrows, signed16index wrap/remainder, empty/occupied slots and signedmappedframe IDs.','Original moneyformatter executes; specific$%ldCoutput matches signed32moneycases includingINT32MIN.','PrivateCPUstack return and callee-savedD2-D7/A2-A6preservation, including textstubs clobbering caller-saved registers.','Callback-inducedstate/MMIO changes and per-read varyingdimensions retain source rereads; Sign-extended negative X contaminates OR-packed coordinates as in the original.'],
            'synthetic_mapping_cases':4,
            'excluded':['Actual149AEglyph rendering andE2B8GPUprocessing replaced with declared fixturecallbacks; no actual pixels/device completion or hardware validation.','Genericprintf behavior or mutatedformatliteral; translation uses the preserved$%ldconstant. Formatter-internal reads/private stack writes excluded from rendererbus trace. Original formatter scratch writes within [0x15b7a0,0x15b7aa) are recorded separately and excluded from cross-C RAM equivalence.','Caller-savedD0/D1/A0/A1return ABI and fullCCR not reconstructed. Invalidcallback handling is addedhost behavior; partialeffects remain.','Only declared scripted schedules; no whole-game equivalence, complete1B786graphics implementation or portedgame build. Synthetic signed-ID/mapping table edits occur only in private test fixtures.'],
            'compiler':compiler,'source_sha256':{n:binary_tools.sha(source/n)for n in ['biwn_inventory_draw.c','biwn_inventory_draw.h']}}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(out/'status.json').write_text(json.dumps({'status':'terminal','exit_code':0})+'\n');(root/'verification/biwn-inventory-draw-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)


if __name__=='__main__':main()
