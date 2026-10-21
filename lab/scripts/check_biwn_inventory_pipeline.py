"""Connected inventory+real original CPU text/sprite helpers vs linked C."""
import ctypes as c
from datetime import datetime,timezone
import hashlib,json,os,random,subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_inventory_draw as draw
ROOT=draw.stage.ROOT;SP=draw.SP;STOP=draw.STOP;REGS=draw.REGS
class Bus(c.Structure):_fields_=[('read8',draw.R8),('read16',draw.R16),('read32',draw.R32),('write32',draw.W32),('context',c.c_void_p),('read_budget',c.c_uint32)]

class Memory(draw.Memory):
    def __init__(self,image,case):
        super().__init__(image,case)
        for address in [0xe2b8,0x149ae]:self.ram[address:address+2]=image[address-0x4000:address-0x4000+2]
        self.gpu=bytearray(0x1000);self.phase='pre';self.call=0;self.remaining=case.get('delays',[0,0,0])[0];self.pending_effects=[]
    def region(self,address,width):
        if 0xf03000<=address and address+width<=0xf04000:return self.gpu,address-0xf03000
        return super().region(address,width)
    def read(self,address,width):
        self.pending_effects=[]
        if 0xf03000<=address<0xf04000:
            if self.fail_read==(address,width):raise RuntimeError('injected GPU read failure')
            assert width==4 and address==(0xf03204 if self.phase=='ack'else 0xf03200),(hex(address),self.phase)
            if self.remaining:
                value=0x4b00 if self.phase=='ack'else 0x80000001;self.remaining-=1
            elif self.phase=='ack':
                value=self.case.get('ack',0);assert value!=0x4b00;self.phase='post';self.remaining=self.case.get('delays',[0,0,0])[2]
            else:
                value=0
                if self.phase=='post':self.phase='pre';self.remaining=self.case.get('delays',[0,0,0])[0];self.call+=1
            self.put(address,width,value);self.trace.append(('r',address,width,value))
            if address==0xf03204 and value!=0x4b00 and self.case.get('profile')=='gpu-mutate':
                for dest,size,new in [(0x49d54,2,(self.peek(0x49d54,2)+3)%10),(0x49d56,2,(self.peek(0x49d56,2)+1)%10),(0x10a688,4,0xa5000000+self.call)]:
                    self.put(dest,size,new);self.pending_effects.append((dest,size,new));self.trace.append(('device_write',dest,size,new))
            return value
        return super().read(address,width)
    def write(self,address,value):
        self.pending_effects=[]
        if 0xf03000<=address<0xf04000:
            if self.fail_write==address:raise RuntimeError('injected GPU write failure')
            assert address in [0xf0320c,0xf03210,0xf03214,0xf03204]
            self.put(address,4,value);self.trace.append(('w',address,4,value))
            if address==0xf03204:assert self.phase=='pre'and value==0x4b00;self.phase='ack';self.remaining=self.case.get('delays',[0,0,0])[1]
        else:super().write(address,value)

def original(image,case,incoming):
    memory=Memory(image,case);cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    cpu.mem_map(0,0x200000);cpu.mem_map(0xf02000,0x2000);cpu.mem_write(0,bytes(memory.ram));cpu.mem_write(SP,STOP.to_bytes(4,'big'))
    for reg,value in zip(REGS,incoming):cpu.reg_write(reg,value)
    cpu.reg_write(UC_M68K_REG_A7,SP);in_formatter=False;steps=[];scratch=[];entries={hex(a):0 for a in [0x1b786,0x149ae,0x147a6,0x14776,0xe2b8,0xe098]}
    def code(engine,address,size,_):
        nonlocal in_formatter
        if address==0x1b45a:in_formatter=True
        if address==0x1b838:in_formatter=False
        assert (0x1b786<=address<0x1bc78 or 0x14776<=address<0x14caa or 0xe098<=address<0xe0a6 or 0xe2b8<=address<0xe2f4 or 0xe540<=address<0xe588 or (in_formatter and (0x1b160<=address<0x1b478 or 0xe61c<=address<0xe68c))),hex(address)
        steps.append(address)
        if hex(address)in entries:entries[hex(address)]+=1
    def read(engine,access,address,size,value,_):
        if in_formatter or SP-0x1000<=address<SP+8:return
        if 0x14800<=address<0x14842:return
        value=memory.read(address,size);engine.mem_write(address,value.to_bytes(size,'big'))
        for dest,width,new in memory.pending_effects:engine.mem_write(dest,new.to_bytes(width,'big'))
    def write(engine,access,address,size,value,_):
        if SP-0x1000<=address<SP+8:return
        if in_formatter:
            assert size==1 and 0x15b7a0<=address<0x15b7aa;memory.put(address,size,value);scratch.append((address,size,value));return
        assert size==4,(hex(address),size);memory.write(address,value&0xffffffff)
    cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write)
    cpu.emu_start(0x1b786,STOP,count=250000,timeout=3_000_000)
    assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
    for i,reg in enumerate(REGS):
        if i not in [0,1,8,9]:assert cpu.reg_read(reg)==incoming[i]
    assert bytes(cpu.mem_read(0,SP-0x1000))==bytes(memory.ram[:SP-0x1000])and bytes(cpu.mem_read(SP+8,0x200000-SP-8))==bytes(memory.ram[SP+8:])
    assert bytes(cpu.mem_read(0xf02000,0x1000))==bytes(memory.mmio)and bytes(cpu.mem_read(0xf03000,0x1000))==bytes(memory.gpu)
    return memory,{'instructions':len(steps),'CPU_entry_calls':entries,'formatter_scratch_writes_excluded':scratch,'preserved_registers_and_RTS_stack_checked':True}

def translated(fn,memory,budget=100000,missing=None):
    def reader(width):
        def callback(_,address,out):
            try:out[0]=memory.read(address,width);return 0
            except Exception as error:memory.errors.append(repr(error));return 1
        return callback
    def write(_,address,value):
        try:memory.write(address,value);return 0
        except Exception as error:memory.errors.append(repr(error));return 1
    types=[draw.R8,draw.R16,draw.R32,draw.W32];callbacks=[draw.R8(reader(1)),draw.R16(reader(2)),draw.R32(reader(4)),draw.W32(write)]
    if missing is not None:callbacks[missing]=types[missing]()
    bus=Bus(*callbacks,None,budget);result=fn(c.byref(bus));return result,bus.read_budget

def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();assert draw.stage.digest(image)==draw.stage.STAGE_SHA
    out=ROOT/'verification/biwn-inventory-pipeline'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libbiwn_inventory_pipeline.dylib'
    names=['biwn_inventory_draw.c','biwn_text.c','biwn_gpu_commands.c','biwn_inventory_pipeline.c'];command=['clang','-dynamiclib','-std=c11','-Wall','-Wextra','-Werror','-O2',*[str(source/n)for n in names],'-o',str(library)];subprocess.run(command,check=True,capture_output=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    lib=c.CDLL(str(library));fn=lib.biwn_inventory_pipeline;fn.argtypes=[c.POINTER(Bus)];fn.restype=c.c_int
    rng=random.Random(0x1b786149ae);cases=[];money=[0,200,0xffffffff,0x80000000,0x7fffffff,123456789,0xffed2979]
    for start in range(10):
        for layout in ['empty','real','full']:
            n=len(cases);cases.append({'start':start,'selected':(start+7)%10,'layout':layout,'money':money[n%7],'profile':'static','delays':[[0,0,0],[1,2,3],[3,1,2]][n%3],'ack':[0,0xffffffff,0x80000000,0x4b01][n%4]})
    for profile in ['read-varying','gpu-mutate']:
        for start in [0,4,9]:
            for layout in ['real','full']:cases.append({'start':start,'selected':9,'layout':layout,'money':0x80000000,'profile':profile,'delays':[1,2,3],'ack':0xffffffff})
    for dimensions in [(0,0),(255,255),(95,32)]:cases.append({'start':0,'selected':0,'layout':'full','money':200,'profile':'static','dimensions':dimensions})
    # The same postframe slot states used in the retained original-game drawing review.
    for start in [0,1,9,0,1,2,3,4,5]:cases.append({'start':start,'selected':start,'layout':'real','money':200,'profile':'static','runtime_snapshot_fixture':True})
    rows=[]
    for n,case in enumerate(cases):
        (out/'status.json').write_text(json.dumps({'status':'running','case':n,'parameters':case})+'\n')
        a,observed=original(image,case,[rng.getrandbits(32)for _ in REGS]);b=Memory(image,case);status,budget=translated(fn,b)
        equal_ram=a.ram[:0x15b7a0]==b.ram[:0x15b7a0]and a.ram[0x15b7aa:]==b.ram[0x15b7aa:]
        if status!=0 or a.trace!=b.trace or not equal_ram or a.mmio!=b.mmio or a.gpu!=b.gpu:
            (out/'mismatch.json').write_text(json.dumps({'case':case,'CPU':observed,'C_status':status,'CPU_trace':a.trace,'C_trace':b.trace,'C_errors':b.errors},indent=2)+'\n');raise AssertionError(str(out/'mismatch.json'))
        rows.append({'case':case,'CPU':observed,'trace':a.trace,'C_remaining_read_budget':budget})
    guards=[];assert fn(None)==1;guards.append({'case':'null_bus','status':1})
    base={'start':0,'selected':0,'layout':'real','money':200,'profile':'static'}
    for missing in range(4):
        m=Memory(image,base);result,_=translated(fn,m,missing=missing);assert result==1 and not m.trace;guards.append({'case':'missing_callback','index':missing,'status':result})
    for name,budget,fail_read,fail_write in [('zero_budget',0,None,None),('mid_text_budget',12,None,None),('money_read',100000,(0x49d1e,4),None),('font_read',100000,(0x4c3e0,1),None),('sprite_idle_read',100000,(0xf03200,4),None),('sprite_ack_read',100000,(0xf03204,4),None),('initial_write',100000,None,0xf02200),('sprite_write',100000,None,0xf03210)]:
        m=Memory(image,base);m.fail_read=fail_read;m.fail_write=fail_write;result,budget=translated(fn,m,budget);expected=2 if 'budget'in name else 3;assert result==expected,(name,result);guards.append({'case':name,'status':result,'trace':m.trace,'remaining_budget':budget,'errors':m.errors})
    (out/'fixtures.json').write_text(json.dumps(rows,indent=2)+'\n');(out/'guards.json').write_text(json.dumps(guards,indent=2)+'\n')
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'connected_inventory_text_sprite_CPU_command_pipeline_matches_C','directory':str(out),'stage_sha256':draw.stage.STAGE_SHA,'CPU_cases':len(rows),'host_guard_cases':len(guards),'additional_original_components':0,
            'matched':['Original1B786executes original149AEtext, E2B8sprite mailbox and theirCPUhelpers without RTS stubs.','All external routine/font/string/device reads and drawing/mailbox writes match in value,address,width,order under scriptedGPUreplies.','Originalstack and callee-saved registers; externalRAM and bothMMIOwindows match, except explicitlyexcluded formatter scratch.','Initial/finalidle and nonzero unequalack schedules; partial source state/device changes and per-read dimensions retain rereads.'],
            'excluded':['Actual GPU4B00execution and drawing device/rasterization,pixels,timing,hardware and whole-game equivalence.','Privateformatter/string/stackdetails and its10scratchbytes[15B7A0,15B7AA); Cmoneystring read locally through an internalalias, not written to gameRAM.','Preserved format3jump-table constant reads excluded from Ctrace; actual inventory fonts are format2.','FullCCR/caller-savedreturnABI; hostreadlimits/callbackerrors are addedguards. This linked integration is not another originalcomponent.'],
            'compiler':command,'source_sha256':{n:draw.binary_tools.sha(source/n)for n in names+[n.replace('.c','.h')for n in names]}}
    for p in [out/'report.json',ROOT/'verification/biwn-inventory-pipeline-checks.json']:p.write_text(json.dumps(report,indent=2)+'\n')
    (out/'status.json').write_text(json.dumps({'status':'terminal','exit_code':0})+'\n');print(json.dumps(report),flush=True)

if __name__=='__main__':main()
