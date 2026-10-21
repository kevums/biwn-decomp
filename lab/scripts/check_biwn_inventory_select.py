"""Original M68000 decoder and UI selection block versus portable callback C."""
import ctypes as c
from datetime import datetime,timezone
import hashlib,json,os,random,subprocess,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import unicorn
import extract_biwn_stage as stage
sys.path.insert(0,str(stage.ROOT));import binary_tools

SP,STOP,BASE=0x1ff000,0x1ffe00,0x49bac
REGS=[UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6]
R8=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint8))
R16=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint16))
R32=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint32))
W16=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint16)
DRAW=c.CFUNCTYPE(c.c_int,c.c_void_p)
class State(c.Structure):_fields_=[('d0',c.c_uint32),('d1',c.c_uint32),('a0',c.c_uint32)]
class Bus(c.Structure):_fields_=[('read8',R8),('read16',R16),('read32',R32),('write16',W16),('redraw',DRAW),('context',c.c_void_p)]


class Script:
    def __init__(self,initial,selected,secondary,input_reads=None,byte=None,slot_reads=None):
        self.memory=bytearray(0x1ac);self.trace=[];self.errors=[];self.inputs=list(input_reads or [initial,initial]);self.input_index=0
        self.byte=byte;self.slots=None if slot_reads is None else list(slot_reads);self.slot_index=0;self.fail_read=None;self.fail_write=None;self.fail_draw=False
        self.put(BASE,4,initial);self.put(0x49d54,2,selected);self.put(0x49d56,2,secondary)
    def put(self,address,width,value):self.memory[address-BASE:address-BASE+width]=value.to_bytes(width,'big')
    def read(self,address,width):
        if (address,width,len([e for e in self.trace if e[0]=='r']))==self.fail_read or (address,width)==self.fail_read:raise RuntimeError('injected read failure')
        assert (address,width)in [(BASE,4),(BASE+2,1),(0x49d54,2)]
        if address==BASE:
            value=self.inputs[self.input_index];self.input_index+=1;self.put(address,width,value)
        elif address==BASE+2 and self.byte is not None:self.put(address,width,self.byte)
        elif address==0x49d54 and self.slots is not None:
            self.put(address,width,self.slots[self.slot_index]);self.slot_index+=1
        value=int.from_bytes(self.memory[address-BASE:address-BASE+width],'big');self.trace.append(('r',address,width,value));return value
    def write(self,address,value):
        if address==self.fail_write:raise RuntimeError('injected write failure')
        assert address in (0x49d54,0x49d56);self.put(address,2,value);self.trace.append(('w',address,2,value))
    def draw(self):
        if self.fail_draw:raise RuntimeError('injected redraw failure')
        self.trace.append(('call',0x1b786))


def cpu_base(image,incoming):
    cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0x4000,image)
    for reg,value in zip(REGS,incoming):cpu.reg_write(reg,value)
    cpu.reg_write(UC_M68K_REG_A7,SP);return cpu


def original_digit(image,input,incoming):
    cpu=cpu_base(image,incoming);cpu.mem_write(SP,STOP.to_bytes(4,'big')+input.to_bytes(4,'big'));steps=[]
    def code(engine,address,size,_):assert 0x1b718<=address<0x1b780;steps.append(address)
    cpu.hook_add(UC_HOOK_CODE,code);cpu.emu_start(0x1b718,STOP,count=128,timeout=500000)
    assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4 and cpu.reg_read(UC_M68K_REG_D1)==input
    for i,reg in enumerate(REGS):
        if i not in (0,1):assert cpu.reg_read(reg)==incoming[i]
    assert bytes(cpu.mem_read(SP+4,4))==input.to_bytes(4,'big')
    return cpu.reg_read(UC_M68K_REG_D0),len(steps)


def original_block(image,script,incoming):
    cpu=cpu_base(image,incoming);cpu.mem_write(BASE,bytes(script.memory));cpu.mem_write(0x1b786,b'\x4e\x75');steps=[];stack=[]
    def code(engine,address,size,_):
        assert 0x1a1f0<=address<0x1a254 or 0x1b718<=address<0x1b780 or address==0x1b786,(hex(address),size)
        if address==0x1b786:script.draw()
        steps.append(address)
    def read(engine,access,address,size,value,_):
        if BASE<=address<BASE+len(script.memory):engine.mem_write(address,script.read(address,size).to_bytes(size,'big'))
        else:assert SP-8<=address<SP+4,(hex(address),size)
    def write(engine,access,address,size,value,_):
        value&=(1<<(size*8))-1
        if address in (0x49d54,0x49d56):assert size==2;script.write(address,value)
        else:assert address in (SP-4,SP-8)and size==4;stack.append((address,value))
    cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write)
    cpu.emu_start(0x1a1f0,0x1a254,count=256,timeout=500000)
    assert cpu.reg_read(UC_M68K_REG_PC)==0x1a254 and cpu.reg_read(UC_M68K_REG_A7)==SP
    for i,reg in enumerate(REGS):
        if i not in (0,1,8):assert cpu.reg_read(reg)==incoming[i]
    assert bytes(cpu.mem_read(BASE,len(script.memory)))==bytes(script.memory)
    expected=[]
    if ('call',0x1b786)in script.trace:
        if script.input_index==2:expected=[(SP-4,script.inputs[1]),(SP-8,0x1a22c)]
        expected.append((SP-4,0x1a254))
    assert stack==expected,(stack,expected)
    return [cpu.reg_read(UC_M68K_REG_D0),cpu.reg_read(UC_M68K_REG_D1),cpu.reg_read(UC_M68K_REG_A0)],len(steps)


def translated(fn,script,incoming,missing=None):
    def reader(width):
        def callback(_,address,value):
            try:value[0]=script.read(address,width);return 0
            except Exception as error:script.errors.append(repr(error));return 1
        return callback
    def writer(_,address,value):
        try:script.write(address,value);return 0
        except Exception as error:script.errors.append(repr(error));return 1
    def draw(_):
        try:script.draw();return 0
        except Exception as error:script.errors.append(repr(error));return 1
    callbacks=[R8(reader(1)),R16(reader(2)),R32(reader(4)),W16(writer),DRAW(draw)]
    types=[R8,R16,R32,W16,DRAW]
    if missing is not None:callbacks[missing]=types[missing]()
    bus=Bus(*callbacks,None);state=State(incoming[0],incoming[1],incoming[8]);result=fn(c.byref(bus),c.byref(state))
    return result,[state.d0,state.d1,state.a0]


def main():
    root=stage.ROOT;session=Path(json.loads((root/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    image=(session/'nextstage-68000-candidate.bin').read_bytes();assert stage.digest(image)==stage.STAGE_SHA
    out=root/'verification/biwn-inventory-select'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=root/'projects/black-ice-white-noise/restoration';library=out/'libbiwn_inventory_select.dylib'
    compiler=['clang','-dynamiclib','-std=c11','-Wall','-Wextra','-Werror','-O2',str(source/'biwn_inventory_select.c'),'-o',str(library)]
    subprocess.run(compiler,check=True,capture_output=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    lib=c.CDLL(str(library));digit=lib.biwn_button_digit;digit.argtypes=[c.c_uint32,c.c_uint32];digit.restype=c.c_uint32
    block=lib.biwn_inventory_select;block.argtypes=[c.POINTER(Bus),c.POINTER(State)];block.restype=c.c_int
    rng=random.Random(0x1b718);bits=[19,18,17,7,6,5,4,3,2,1];mask=sum(1<<b for b in bits);decoder_cases=[]
    for pattern in range(1024):
        input=sum(1<<b for i,b in enumerate(bits)if pattern&(1<<i))|(rng.getrandbits(32)&~mask)
        for incoming_d0 in [0,0x12345678,0xffffffff,0x80008000]:
            incoming=[rng.getrandbits(32)for _ in REGS];incoming[0]=incoming_d0
            observed,steps=original_digit(image,input,incoming);result=digit(input,incoming_d0);assert result==observed
            decoder_cases.append({'pattern':pattern,'input':hex(input),'incoming_D0':hex(incoming_d0),'final_D0':hex(result),'instructions':steps})
    fixtures=[]
    for pattern in range(2048):
        relevant=bits+[9];input=sum(1<<b for i,b in enumerate(relevant)if pattern&(1<<i))|(rng.getrandbits(32)&~0xe02fe)
        fixtures.append({'name':'all_input_combinations','input':input,'selected':rng.randrange(10),'secondary':rng.randrange(65536)})
    for selected in [*range(10),0xffff,0x7fff,0x8000]:fixtures.append({'name':'cycle_boundaries','input':0xe0200,'selected':selected,'secondary':rng.randrange(65536)})
    for _ in range(512):fixtures.append({'name':'random_full_words','input':rng.getrandbits(32),'selected':rng.randrange(65536),'secondary':rng.randrange(65536)})
    fixtures += [
      {'name':'reread_no_key','input':2,'selected':3,'secondary':4,'input_reads':[2,0],'byte':0},
      {'name':'reread_different_digit','input':1<<19,'selected':3,'secondary':4,'input_reads':[1<<19,1<<2],'byte':0},
      {'name':'cycle_byte_changes','input':2,'selected':9,'secondary':4,'byte':2},
      {'name':'cycle_to_digit_changes','input':512,'selected':3,'secondary':4,'input_reads':[512,1<<4],'byte':0},
      {'name':'cycle_compare_reread_changes','input':512,'selected':3,'secondary':4,'slot_reads':[3,9,0x1234]},
      {'name':'cycle_compare9_skips_second_read','input':512,'selected':3,'secondary':4,'slot_reads':[9,0xabcd]},
      {'name':'digit_subtract_and_copy_reread_changes','input':2,'selected':3,'secondary':4,'slot_reads':[0,0x4321]},
      {'name':'zero_digit_subtract_and_copy_reread_changes','input':16,'selected':3,'secondary':4,'slot_reads':[0xffff,0xbeef]}]
    rows=[]
    for fixture in fixtures:
        kwargs={k:fixture[k]for k in ['input_reads','byte','slot_reads']if k in fixture};incoming=[rng.getrandbits(32)for _ in REGS]
        a=Script(fixture['input'],fixture['selected'],fixture['secondary'],**kwargs);state,steps=original_block(image,a,incoming)
        b=Script(fixture['input'],fixture['selected'],fixture['secondary'],**kwargs);result,newstate=translated(block,b,incoming)
        assert result==0 and not b.errors and state==newstate and a.trace==b.trace and a.memory==b.memory,(fixture,state,newstate,a.trace,b.trace)
        rows.append({**fixture,'initial_D0_D1_A0':[incoming[0],incoming[1],incoming[8]],'final_D0_D1_A0':state,'instructions':steps,'trace':a.trace})
    guards=[];assert block(None,None)==1;guards.append({'case':'null_bus_and_state','status':1})
    dummy=Bus();assert block(c.byref(dummy),None)==1;guards.append({'case':'null_state','status':1})
    for missing in range(5):
        s=Script(2,3,4);result,_=translated(block,s,[0]*15,missing);assert result==1 and not s.trace;guards.append({'case':'missing_callback','index':missing,'status':result})
    for name,fail_r,fail_w,fail_draw in [('input_read',(BASE,4),None,False),('byte_read',(BASE+2,1),None,False),('second_input_read',(BASE,4,2),None,False),('selected_read',(0x49d54,2),None,False),('selected_write',None,0x49d54,False),('secondary_write',None,0x49d56,False),('redraw',None,None,True)]:
        s=Script(2,3,4);s.fail_read=fail_r;s.fail_write=fail_w;s.fail_draw=fail_draw;result,_=translated(block,s,[0]*15)
        assert result==(3 if fail_draw else 2),(name,result);guards.append({'case':name,'status':result,'trace':s.trace,'errors':s.errors})
    decodes=[]
    for start,end in [(0x1b718,0x1b780),(0x1a1f0,0x1a254)]:
        data=image[start-0x4000:end-0x4000];ins,decoder=binary_tools.m68k_instructions(data,start);decodes.append({'interval':[hex(start),hex(end)],'bytes':data.hex(),'sha256':hashlib.sha256(data).hexdigest(),'instructions':ins,'decoder':decoder})
    for name,value in [('decoder-fixtures.json',decoder_cases),('selection-fixtures.json',rows),('guards.json',guards),('original-decodes.json',decodes)]: (out/name).write_text(json.dumps(value,indent=2)+'\n')
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'CPU_decoder_and_selection_block_match_portable_C','directory':str(out),'stage_sha256':stage.STAGE_SHA,
            'portable_components':2,'digit_decoder_CPU_cases':len(decoder_cases),'selection_block_CPU_cases':len(rows),'host_guard_cases':len(guards),
            'CPU_model':'Unicorn'+unicorn.__version__+' M68000','digit_interval':'[0x1b718,0x1b780)','selection_interval':'[0x1a1f0,0x1a254)',
            'matched':['Every tested fullD0decoder result, including CLR.W upper16preservation; D1loadedinput, other registers and private RTSreturn/argument unchanged.','Input bit priority across all1024key-bit combinations and four incomingD0patterns; unrelated bits randomized.','Selectionblock all2048key/cycle combinations plus boundary/random/reread cases; every global read/write width,address,value and order; modeled redrawcall boundary.','CompletedD0/D1/A0 and other-register preservation; stack balanced at fallthrough1A254.'],
            'excluded':['Whole original1A188function, actual1B786drawing/register sideeffects, interrupts/devices/controller hardware mapping and complete-game integration.','FullCCR comparison; sourceoriginalno hostcallback errors. Partial writes retained on added host errors.','Finite scripted changes cover supplied rereads, not all real-world asynchronous schedules.'],
            'decoder_display_caveat':'Capstone5prints BTST.b for registerD1 tests including bit19; Ghidra prints BTST.l. NXP M68000PRM printed4-61..63 specifies register32bit/memory8bit. CPUfixtures exercise bit19/18/17 separately; bytes/boundaries unchanged.',
            'manual_reference':'https://www.nxp.com/docs/en/reference-manual/M68000PRM.pdf#page=165',
            'compiler':compiler,'source_sha256':{n:binary_tools.sha(source/n)for n in ['biwn_inventory_select.c','biwn_inventory_select.h']}}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(root/'verification/biwn-inventory-select-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)


if __name__=='__main__':main()
