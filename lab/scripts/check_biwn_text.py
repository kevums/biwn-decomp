"""Original 14776/147A6/149AE CPU execution versus reconstructed text commands."""
import ctypes as c
from datetime import datetime,timezone
import hashlib,json,os,random,subprocess,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import unicorn,extract_biwn_stage as stage
sys.path.insert(0,str(stage.ROOT));import binary_tools
SP,STOP,STRING,FONT=0x1ff000,0x1ffe00,0x160000,0x60000
REGS=[UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6]
R8=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint8));R16=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint16));W32=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint32)
class Bus(c.Structure):_fields_=[('read8',R8),('read16',R16),('write32',W32),('context',c.c_void_p),('read_budget',c.c_uint32)]
class Args(c.Structure):_fields_=[('x',c.c_uint16),('y',c.c_uint16),('text',c.c_uint32),('target',c.c_uint32),('target_flags',c.c_uint32),('font',c.c_uint32),('color',c.c_uint16),('mode',c.c_uint16)]

class Memory:
    def __init__(self,image,case):
        self.ram=bytearray(0x200000);self.ram[0x4000:0x4000+len(image)]=image;self.mmio=bytearray(0x1000);self.case=case
        self.font=case.get('actual_font',FONT);self.ram[STRING:STRING+len(bytes.fromhex(case['string_hex']))]=bytes.fromhex(case['string_hex'])
        if 'actual_font'not in case:
            t,count,width,height,first,last,flags=case['header'];self.ram[FONT:FONT+8]=bytes([t,count,width,height,first,last])+flags.to_bytes(2,'big')
            if t==2:
                table=FONT+8+count*height*2
                for i in range(256):self.ram[table+i]=[0,1,7,8,9,16,17,24,31,32,33,255][i%12]
                self.table=table
            else:self.table=0
        else:self.table=self.font+8+self.ram[self.font+1]*self.ram[self.font+3]*2 if self.ram[self.font]==2 else 0
        self.trace=[];self.errors=[];self.effects=[];self.reads={};self.commands=0;self.fail_read=None;self.fail_write=None
    def region(self,address,width):
        if 0<=address and address+width<=len(self.ram):return self.ram,address
        if 0xf02000<=address and address+width<=0xf03000:return self.mmio,address-0xf02000
        raise ValueError(hex(address))
    def peek(self,address,width):
        data,offset=self.region(address,width);return int.from_bytes(data[offset:offset+width],'big')
    def put(self,address,width,value):
        data,offset=self.region(address,width);data[offset:offset+width]=(value&((1<<(8*width))-1)).to_bytes(width,'big')
    def read(self,address,width):
        if self.fail_read==(address,width):raise RuntimeError('injected read failure')
        n=self.reads.get(address,0);self.reads[address]=n+1
        if self.case.get('profile')=='varying':
            if address==self.font+2:self.put(address,1,[16,9,8,255][n%4])
            if address==self.font+3:self.put(address,1,[11,0,255,1][n%4])
            if self.table and self.table<=address<self.table+256:self.put(address,1,[0,9,255,17][n%4])
        value=self.peek(address,width);self.trace.append(('r',address,width,value));return value
    def write(self,address,value):
        if address==self.fail_write:raise RuntimeError('injected write failure')
        assert 0xf02200<=address<=0xf0226c and address%4==0
        self.put(address,4,value);self.trace.append(('w',address,4,value));self.effects=[]
        if address==0xf02238:
            self.commands+=1
            if self.case.get('profile')=='command-mutate':
                for dest,new in [(self.font+3,[11,0,255][self.commands%3]),(self.font+4,[32,64][self.commands%2]),(self.font+5,[90,127][self.commands%2])]:
                    self.put(dest,1,new);self.effects.append((dest,new));self.trace.append(('device_effect',dest,1,new))

def arguments(case,memory):return Args(case['x'],case['y'],STRING,case['target'],case['flags'],memory.font,case['color'],case['mode'])

def original(image,entry,case,incoming,alignment=None):
    memory=Memory(image,case);cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    cpu.mem_map(0,0x200000);cpu.mem_map(0xf02000,0x1000);cpu.mem_write(0,bytes(memory.ram));cpu.mem_write(SP,STOP.to_bytes(4,'big'))
    args=arguments(case,memory)
    if alignment is not None:stack=alignment[0].to_bytes(4,'big')+alignment[1].to_bytes(2,'big')+alignment[2].to_bytes(2,'big')
    else:stack=args.x.to_bytes(2,'big')+args.y.to_bytes(2,'big')+b''.join(v.to_bytes(4,'big')for v in [args.text,args.target,args.target_flags,args.font])+args.color.to_bytes(2,'big')+args.mode.to_bytes(2,'big')
    cpu.mem_write(SP+4,stack)
    for reg,value in zip(REGS,incoming):cpu.reg_write(reg,value)
    cpu.reg_write(UC_M68K_REG_A7,SP);steps=[];table_reads=[]
    def code(engine,address,size,_):
        assert 0x14776<=address<0x14caa or 0xe540<=address<0xe588,hex(address)
        steps.append(address)
    def read(engine,access,address,size,value,_):
        if SP-0x1000<=address<SP+64:return
        if 0x14800<=address<0x14842:
            assert size==2;table_reads.append((address,int.from_bytes(engine.mem_read(address,size),'big')));return
        engine.mem_write(address,memory.read(address,size).to_bytes(size,'big'))
    def write(engine,access,address,size,value,_):
        if SP-0x1000<=address<SP+64:return
        assert size==4,(hex(address),size);memory.write(address,value&0xffffffff)
        for dest,new in memory.effects:engine.mem_write(dest,bytes([new]))
    cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write)
    cpu.emu_start(entry,STOP,count=250000,timeout=3_000_000)
    assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
    excluded=[0,1]if alignment is not None else[0,1,8,9]
    for i,reg in enumerate(REGS):
        if i not in excluded:assert cpu.reg_read(reg)==incoming[i],(i,hex(cpu.reg_read(reg)),hex(incoming[i]))
    assert bytes(cpu.mem_read(0,SP-0x1000))==bytes(memory.ram[:SP-0x1000])
    assert bytes(cpu.mem_read(SP+64,0x200000-SP-64))==bytes(memory.ram[SP+64:])
    assert bytes(cpu.mem_read(0xf02000,0x1000))==bytes(memory.mmio)
    return memory,{'D0':cpu.reg_read(UC_M68K_REG_D0),'instructions':len(steps),'private_stack_return_checked':True,'preserved_registers_checked':True,'constant_jump_table_reads_excluded_from_C_trace':table_reads}

def translated(fn,memory,budget=10000,missing=None):
    def reader(width):
        def read(_,address,out):
            try:out[0]=memory.read(address,width);return 0
            except Exception as error:memory.errors.append(repr(error));return 1
        return read
    def write(_,address,value):
        try:memory.write(address,value);return 0
        except Exception as error:memory.errors.append(repr(error));return 1
    types=[R8,R16,W32];callbacks=[R8(reader(1)),R16(reader(2)),W32(write)]
    if missing is not None:callbacks[missing]=types[missing]()
    bus=Bus(*callbacks,None,budget);args=arguments(memory.case,memory);d0=c.c_uint32(0xabcdef01);status=fn(c.byref(bus),c.byref(args),c.byref(d0))
    return status,d0.value,bus.read_budget

def main():
    root=stage.ROOT;session=Path(json.loads((root/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();assert stage.digest(image)==stage.STAGE_SHA
    out=root/'verification/biwn-text'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=root/'projects/black-ice-white-noise/restoration';library=out/'libbiwn_text.dylib';compiler=['clang','-dynamiclib','-std=c11','-Wall','-Wextra','-Werror','-O2',str(source/'biwn_text.c'),'-o',str(library)];subprocess.run(compiler,check=True,capture_output=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    lib=c.CDLL(str(library));functions={0x147a6:lib.biwn_text_draw_format3,0x149ae:lib.biwn_text_draw}
    for fn in functions.values():fn.argtypes=[c.POINTER(Bus),c.POINTER(Args),c.POINTER(c.c_uint32)];fn.restype=c.c_int
    align=lib.biwn_text_alignment;align.argtypes=[c.c_uint16]*3;align.restype=c.c_uint32
    rng=random.Random(0x149ae);base={'x':16,'y':21,'target':0xb6030,'flags':0x3420,'color':2,'mode':0,'header':[1,96,9,11,32,126,0x5400],'string_hex':b'@ABCZ[\xff\0'.hex(),'profile':'static'}
    align_rows=[]
    align_cases=[(x,w,m)for x in [0,1,7,8,0x7fff,0x8000,0xffff]for w in [0,1,8,255,0x7fff,0x8000,0xffff]for m in [0,1,3,7,15,0x8000,0xffff]]+[(rng.getrandbits(32),rng.getrandbits(16),rng.getrandbits(16))for _ in range(1024)]
    for position,width,mask in align_cases:
        a,observed=original(image,0x14776,base,[rng.getrandbits(32)for _ in REGS],(position,width,mask));value=align(position&0xffff,width,mask)
        assert observed['D0']==value and not a.trace
        align_rows.append({'position':position,'width':width,'mask':mask,'D0':value,'CPU':observed})
    cases=[];strings=[b'\0',b'A\0',b'@ABCZ[\xff\0',b'\x01\x20\x7f\xff\0']
    for t in [0,1,2,3,4,255]:
        for width in [0,1,7,8,9,16,17,24,25,32,33,255]:
            for flag in range(0,64,8):
                n=len(cases);case={**base,'header':[t,[0,1,96,255][n%4],width,[0,1,11,255][(n//4)%4],32,126,[0,0x5400,0xffff,0x8000][n%4]],'flags':[0,0x3420,0x80030000,0xffffffff][n%4]&~0x38|flag,'x':[0,7,0x7fff,0xffff][n%4],'y':[0,11,0x8000,0xffff][(n//4)%4],'color':[0,2,0x7fc0,0xffff][n%4],'mode':[0,1,0x1234,0xffff][(n//4)%4],'string_hex':strings[(n//8)%4].hex()};cases.append((0x149ae,case))
    for font in [0x4c3e0,0x4cca0]:
        for text in [b'$200\0',b'$-2147483648\0',b'My First\0',b'\0']:
            for flags in [0x3420,0x3428,0x3430,0x3438]:cases.append((0x149ae,{**base,'actual_font':font,'string_hex':text.hex(),'flags':flags,'color':0x7fc0,'mode':1}))
    for t in [1,2,3]:
        for profile in ['varying','command-mutate']:
            for width in [9,24,255]:cases.append((0x149ae,{**base,'header':[t,96,width,11,32,126,0x5400],'profile':profile}))
    for flag in range(0,64,8):cases.append((0x147a6,{**base,'header':[3,96,255,255,32,126,0xffff],'flags':flag,'string_hex':b'@ABCZ[\xff\0'.hex()}))
    for t in [1,2,3]:cases.append((0x149ae,{**base,'header':[t,96,255,255,32,126,0x5400],'string_hex':(b'A'*320+b'\0').hex(),'x':0xfff0,'y':0xffff}))
    rows=[]
    for n,(entry,case)in enumerate(cases):
        (out/'status.json').write_text(json.dumps({'status':'running','case':n,'parameters':case})+'\n')
        a,observed=original(image,entry,case,[rng.getrandbits(32)for _ in REGS]);b=Memory(image,case);status,d0,budget=translated(functions[entry],b)
        if status!=0 or d0!=observed['D0']or a.trace!=b.trace or a.ram!=b.ram or a.mmio!=b.mmio:
            (out/'mismatch.json').write_text(json.dumps({'entry':hex(entry),'case':case,'CPU':observed,'C_status':status,'C_D0':d0,'CPU_trace':a.trace,'C_trace':b.trace,'C_errors':b.errors},indent=2)+'\n');raise AssertionError(str(out/'mismatch.json'))
        rows.append({'entry':hex(entry),'case':case,'CPU':observed,'trace':a.trace,'C_remaining_read_budget':budget,'commands':a.commands})
    guards=[]
    for entry,fn in functions.items():
        for what in ['null_bus','null_args','null_output']:
            m=Memory(image,base);dummy_bus=Bus();args=arguments(base,m);value=c.c_uint32(0xabcdef01)
            args_tuple=[c.byref(dummy_bus),c.byref(args),c.byref(value)];args_tuple[['null_bus','null_args','null_output'].index(what)]=None
            result=fn(*args_tuple);assert result==1 and value.value==0xabcdef01;guards.append({'entry':hex(entry),'case':what,'status':result})
        for missing in range(3):
            m=Memory(image,base);result,value,_=translated(fn,m,missing=missing);assert result==1 and not m.trace and value==0xabcdef01;guards.append({'entry':hex(entry),'case':'missing_callback','index':missing,'status':result})
        for what in ['zero_budget','late_budget','read8_failure','read16_failure','first_write_failure','command_write_failure']:
            m=Memory(image,base)
            if what=='read8_failure':m.fail_read=(FONT+(2 if entry==0x147a6 else 0),1)
            if what=='read16_failure':m.fail_read=(FONT+6,2)
            if what=='first_write_failure':m.fail_write=0xf02224 if entry==0x147a6 else 0xf02268
            if what=='command_write_failure':m.fail_write=0xf02238
            budget=0 if what=='zero_budget'else 3 if what=='late_budget'else 10000
            result,value,remaining=translated(fn,m,budget);expected=2 if 'budget'in what else 3;assert result==expected and value==0xabcdef01,(entry,what,result)
            guards.append({'entry':hex(entry),'case':what,'status':result,'trace':m.trace,'remaining_budget':remaining,'errors':m.errors})
    (out/'alignment-fixtures.json').write_text(json.dumps(align_rows,indent=2)+'\n');(out/'text-fixtures.json').write_text(json.dumps(rows,indent=2)+'\n');(out/'guards.json').write_text(json.dumps(guards,indent=2)+'\n')
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'full_text_CPU_helpers_match_portable_C_protocol','directory':str(out),'stage_sha256':stage.STAGE_SHA,'portable_components':3,'alignment_CPU_cases':len(align_rows),'text_CPU_cases':len(rows),'host_guard_cases':len(guards),'original_interval':'[0x14776,0x14caa)','original_bytes_sha256':hashlib.sha256(image[0x14776-0x4000:0x14caa-0x4000]).hexdigest(),'CPU_model':'Unicorn'+unicorn.__version__+' M68000',
            'matched':['Whole14776alignment return including arbitrary16bitwrap/masks.','Whole147A6and149AE CPU paths, format3 delegation, fullD0return, preserved registers and private stack.','Ordered font/string reads and drawing writes, color/mode expansion, fixed/variable widths, out-of-range characters and multi-column commands.','Actual game fonts, emptystrings, longstrings withpacked-coordinate carry, per-read/header changes and command-inducedfont changes.'],
            'excluded':['Device work from drawing-word writes, glyph rasterization/pixels, device timing, hardware and completegame equivalence.','Read-only original jump table[14800,14842) loads excluded fromCbus trace; preserved table implements switch constants. Mutated jump-table/code behavior unsupported.','Private stack/local implementation details, caller-savedD1/A0/A1 and fullCCR.','Hostguards/readbudget have no original counterpart; effects prior to errors retained. Cstatus is not originalD0.'],
            'compiler':compiler,'source_sha256':{name:binary_tools.sha(source/name)for name in ['biwn_text.c','biwn_text.h']}}
    n,row=next((i,z)for i,z in enumerate(rows)if z['case'].get('actual_font')==0x4c3e0 and z['case']['string_hex']=='00'and z['case']['flags']==0x3420)
    assert row['CPU']['D0']==0xb0000
    report['checked_examples']={'empty_string_height11':{'full_D0':'0x000b0000','return_type':'Numeric packed height/advance result, not a string.','source_fixture':str(out/'text-fixtures.json'),'row_index':n,'parameters':row['case'],'original_instructions':row['CPU']['instructions']}}
    for path in [out/'report.json',root/'verification/biwn-text-checks.json']:path.write_text(json.dumps(report,indent=2)+'\n')
    (out/'status.json').write_text(json.dumps({'status':'terminal','exit_code':0})+'\n');print(json.dumps(report),flush=True)

if __name__=='__main__':main()
