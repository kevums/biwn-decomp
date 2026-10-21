"""Complete original CPU caller1A188 vs portable C, with declared helper scripts."""
import argparse,ctypes as c,hashlib,json,random,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_inventory_select as select
ROOT=select.stage.ROOT;SP=select.SP;STOP=select.STOP;REGS=select.REGS
R8=select.R8;R16=select.R16;R32=select.R32;W16=select.W16
W32=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint32)
CALL=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint32),c.c_uint32,c.POINTER(c.c_uint32))
class Bus(c.Structure):_fields_=[('read8',R8),('read16',R16),('read32',R32),('write16',W16),('write32',W32),('call',CALL),('context',c.c_void_p),('poll_limit',c.c_uint32)]
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')

class Script:
    def __init__(self,snapshot,case):
        self.memory=bytearray(snapshot);self.case=case;self.trace=[];self.polls=0;self.changed=[];self.errors=[]
        self.fail_read=False;self.fail_write=False;self.fail_call=None;self.mode_reads=0
        for a,w,v in case['initial']:self.put(a,w,v)
        self.changed=[]
    def put(self,a,w,v):
        self.memory[a:a+w]=(v&((1<<(w*8))-1)).to_bytes(w,'big');self.changed.append((a,w,v&((1<<(w*8))-1)))
    def get(self,a,w):return int.from_bytes(self.memory[a:a+w],'big')
    def read(self,a,w):
        if self.fail_read:raise RuntimeError('injected read failure')
        assert 0<=a<=0x200000-w
        if a==0x49c60 and 'mode_reads'in self.case:
            values=self.case['mode_reads'];self.put(a,w,values[min(self.mode_reads,len(values)-1)]);self.mode_reads+=1
        v=self.get(a,w);self.trace.append(['r',a,w,v]);return v
    def write(self,a,w,v):
        if self.fail_write:raise RuntimeError('injected write failure')
        self.put(a,w,v);self.trace.append(['w',a,w,v])
    def call(self,a,args):
        if a==self.fail_call:raise RuntimeError('injected dependency failure')
        self.trace.append(['call',a,args])
        result=0
        if a==0xe4c0:
            values=self.case['poll_inputs'];self.put(0x49bac,4,values[min(self.polls,len(values)-1)]);self.put(0x778cc,4,self.case['clock']+self.polls);self.polls+=1
        elif a==0xe220:
            assert len(args)==5 and args[:2]==[0x49ccc,0] and args[3]==0
            for address,width,value in self.case['movement_effects']:self.put(address,width,value)
        elif a in [0x19f2c,0x19fda]:
            result=self.case['collision_result']
            for address,width,value in self.case.get('collision_effects',[]):self.put(address,width,value)
        elif a==0x191f4:
            for address,width,value in self.case.get('input_effects',[]):self.put(address,width,value)
        elif a==0xf0fa:result=self.case['camera_result']if'camera_result'in self.case else self.case['terrain_result']
        elif a==0xeb04:assert args==[0x49c4c]
        else:assert a in [0x1b786,0x20820]
        return result&0xffffffff

def original(image,script,incoming,coverage,diagnostic=None):
    cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(script.memory));cpu.mem_write(SP,STOP.to_bytes(4,'big'))
    for reg,value in zip(REGS,incoming):cpu.reg_write(reg,value)
    cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP);steps=[]
    helpers=[0xe4c0,0x191f4,0x1b786,0xe220,0x19f2c,0x19fda,0xf0fa,0xeb04,0x20820]
    # Explicit helper stubs, outside the unchanged caller and digit-helper code.
    # Let the CPU execute the return instruction and balance its own stack.
    for helper in helpers:cpu.mem_write(helper,b'\x4e\x75')
    def code(engine,a,size,_):
        if diagnostic:
            with diagnostic.open('a')as stream:stream.write(hex(a)+'\n')
        if a in helpers:
            stack=engine.reg_read(UC_M68K_REG_A7)
            def read_stack(offset,width):return int.from_bytes(engine.mem_read(stack+offset,width),'big')
            if a==0xf0fa:args=[engine.reg_read(UC_M68K_REG_D2)&0xffff,engine.reg_read(UC_M68K_REG_D3)&0xffff]
            elif a==0xe220:args=[read_stack(4+i*4,4)for i in range(5)]
            elif a==0x19f2c:args=[read_stack(4+i*2,2)for i in range(3)]
            elif a==0x19fda:args=[read_stack(4,4),read_stack(8,2)]
            elif a==0xeb04:args=[read_stack(4,4)]
            else:args=[]
            script.changed=[];result=script.call(a,args)
            for address,width,value in script.changed:engine.mem_write(address,value.to_bytes(width,'big'))
            engine.reg_write(UC_M68K_REG_D0,result)
            return
        assert 0x1a188<=a<0x1a544 or 0x1b718<=a<0x1b780,hex(a)
        coverage.add(a);steps.append(a)
    def read(engine,access,a,w,v,_):
        if SP-0x1000<=a<SP+8:return
        engine.mem_write(a,script.read(a,w).to_bytes(w,'big'))
    def write(engine,access,a,w,v,_):
        if SP-0x1000<=a<SP+8:return
        script.write(a,w,v&((1<<(8*w))-1))
    cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write)
    cpu.emu_start(0x1a188,STOP,count=4096,timeout=500000)
    assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
    for i,reg in enumerate(REGS):
        if i not in [0,1,8,9]:assert cpu.reg_read(reg)==incoming[i]
    # Script memory contains all externally visible effects; private stack excluded.
    actual=bytearray(cpu.mem_read(0,0x200000))
    for helper in helpers:actual[helper:helper+2]=script.memory[helper:helper+2]
    assert actual[:SP-0x1000]==script.memory[:SP-0x1000] and actual[SP+8:]==script.memory[SP+8:]
    return len(steps)

def translated(fn,script,missing=None,poll_limit=16):
    def reader(width):
        def callback(_,address,value):
            try:value[0]=script.read(address,width);return 0
            except Exception as error:script.errors.append(repr(error));return 1
        return callback
    def writer(width):
        def callback(_,address,value):
            try:script.write(address,width,value);return 0
            except Exception as error:script.errors.append(repr(error));return 1
        return callback
    def call(_,address,args,count,result):
        try:result[0]=script.call(address,list(args[:count]));return 0
        except Exception as error:script.errors.append(repr(error));return 1
    types=[R8,R16,R32,W16,W32,CALL];callbacks=[R8(reader(1)),R16(reader(2)),R32(reader(4)),W16(writer(2)),W32(writer(4)),CALL(call)]
    if missing is not None:callbacks[missing]=types[missing]()
    bus=Bus(*callbacks,None,poll_limit)
    return fn(c.byref(bus))

def cases():
    rng=random.Random(0x1a188);result=[]
    inputs=[0,0x200,1<<4,1<<19,0xe02fe,0x80000000,0x20000080]
    values32=[0,1,0xffffffff,0x7fffffff,0x80000000,0x80000001,0x7ffffffe]
    values16=[0,1,0x3fff,0x4000,0x7fff,0x8000,0xffff]
    for i in range(1024):
        mode=[0,1,2,3,0xffff][i%5]
        initial=[]
        def put(a,w,v):initial.append([a,w,v])
        put(0x46252,4,values32[i%7]);put(0x49ba4,4,[0,0x80][i%2]);put(0x49d54,2,i%10);put(0x49d56,2,(i+3)%10)
        put(0x49c50,4,rng.choice(values32+[-101&0xffffffff,0,99,100]));put(0x49c54,2,rng.choice(values16));put(0x49c56,4,rng.choice(values32+[-101&0xffffffff,0,99,100]))
        for a in [0x49c5a,0x49c5c,0x49c5e,0x49b8c,0x49b8e,0x49b90,0x49b92,0x49b94,0x49b96]:put(a,2,rng.choice(values16))
        put(0x49c60,2,mode);put(0x49c78,4,0x81234);put(0x49c90,4,0x80000)
        for a in [0x49c7c,0x49c84,0x49c94,0x49c9c]:put(a,4,100)
        for a in [0x49c80,0x49c88,0x49c98,0x49ca0]:put(a,4,(-100)&0xffffffff)
        for a in [0x80002,0x80004,0x80006,0x80008]:put(a,2,rng.randrange(65536))
        put(0x49d16,2,rng.choice([0,1,0xffff,0x7fff]));put(0x49d18,2,0xa55a);put(0x49cc4,4,rng.getrandbits(32));put(0x49cba,1,rng.randrange(256))
        effects=[]
        for axis in range(3):effects.extend([[0x49cde+axis*2,2,rng.choice(values16)],[0x49ce6+axis*2,2,rng.choice(values16)]])
        case={'initial':initial,'clock':values32[(i//7)%7],'poll_inputs':[inputs[i%7]],'movement_effects':effects,'collision_result':[0,1,2,0xffff,0x12340000,0x12340001,0x80000000][(i//5)%7],'camera_result':values32[(i//3)%7]}
        if i%11==0:case['poll_inputs']=[0x10000000,0,0,0x10000000]
        if i%13==0:case['collision_effects']=[[0x49c50,4,rng.getrandbits(32)],[0x49c5a,2,rng.randrange(65536)],[0x49cde,2,rng.randrange(65536)]]
        if i%17==0:case['input_effects']=[[0x49c54,2,rng.randrange(65536)]]
        if i%19==0:case['mode_reads']=[3,2]
        result.append(case)
    return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);options=parser.parse_args()
    s=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(s/'nextstage-68000-candidate.bin').read_bytes();assert select.stage.digest(image)==select.stage.STAGE_SHA
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();assert snapshot[0x1a188:0x1a544]==image[0x1a188-0x4000:0x1a544-0x4000]
    out=ROOT/'verification/biwn-world-update'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libbiwn-world-update.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_world_update.c'),str(source/'biwn_inventory_select.c'),'-o',str(library)]
    compile_result=subprocess.run(command,capture_output=True,text=True);(out/'compiler.txt').write_text(compile_result.stdout+compile_result.stderr);assert compile_result.returncode==0
    lib=c.CDLL(str(library));fn=lib.biwn_world_update;fn.argtypes=[c.POINTER(Bus)];fn.restype=c.c_int
    rows=[];coverage=set();rng=random.Random(0x1a544);fixtures=cases()
    if options.limit:fixtures=fixtures[:options.limit]
    for i,case in enumerate(fixtures):
        save(out/'status.json',{'status':'running','case':i});a=Script(snapshot,case);b=Script(snapshot,case)
        steps=original(image,a,[rng.getrandbits(32)for _ in REGS],coverage,out/'instruction-diagnostic.txt' if options.limit and i==0 else None);status=translated(fn,b)
        if status or a.trace!=b.trace or a.memory!=b.memory:
            save(out/'mismatch.json',{'case':i,'parameters':case,'C_status':status,'C_errors':b.errors,'original_trace':a.trace,'C_trace':b.trace,'RAM_diff':[[j,a.memory[j],b.memory[j]]for j in range(len(a.memory))if a.memory[j]!=b.memory[j]][:200]});raise AssertionError(str(out/'mismatch.json'))
        rows.append({'case':i,'parameters':case,'instructions':steps,'trace':b.trace,'RAM_sha256':hashlib.sha256(b.memory).hexdigest(),'whole_external_RAM_and_bus_trace_match':True})
    save(out/'fixtures.json',rows)
    guards=[]
    for missing in range(6):
        script=Script(snapshot,fixtures[1]);assert translated(fn,script,missing)==1 and not script.trace
        guards.append({'missing_callback':missing,'status':1,'no_effects':True})
    assert fn(None)==1;guards.append({'null_bus':True,'status':1})
    script=Script(snapshot,fixtures[1]);assert translated(fn,script,poll_limit=0)==1 and not script.trace;guards.append({'zero_poll_limit':True,'status':1})
    case=dict(fixtures[1],poll_inputs=[0x10000000,0]);script=Script(snapshot,case);assert translated(fn,script,poll_limit=3)==4 and script.polls==3;guards.append({'bounded_pause_polls':3,'status':4})
    for failure in ['fail_read','fail_write']:
        script=Script(snapshot,fixtures[1]);setattr(script,failure,True);assert translated(fn,script)==2;guards.append({'injected':failure,'status':2,'partial_trace':script.trace})
    for target in [0xe4c0,0x191f4,0x1b786,0xe220,0x19f2c,0x19fda,0xf0fa,0xeb04,0x20820]:
        candidate=next(row for row in rows if any(e[0]=='call'and e[1]==target for e in row['trace']))
        script=Script(snapshot,candidate['parameters']);script.fail_call=target;assert translated(fn,script)==3;guards.append({'dependency_error_target':hex(target),'status':3,'partial_trace':script.trace})
    save(out/'guards.json',guards)
    decoded,decoder=select.binary_tools.m68k_instructions(image[0x1a188-0x4000:0x1a544-0x4000],0x1a188)
    save(out/'original-full-caller-decode.json',{'interval':['0x1a188','0x1a544'],'instructions':decoded,'decoder':decoder})
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'complete_CPU_world_update_caller_matches_callback_C','directory':str(out),'CPU_cases':len(rows),'host_guard_cases':len(guards),'interval':'[0x1a188,0x1a544)','original_bytes':956,'initial_SR':'0x2000 explicitly initialized before first flag-dependent instruction','helper_return_stubs':'RTS words at declared dependency targets; caller and digit helper bytes unchanged',
            'stage_sha256':select.stage.STAGE_SHA,'additional_original_components':0,'component_scope':'Broader caller subsumes previously counted selection basic block; no component-count inflation.',
            'covered_caller_instructions':len([row for row in decoded if row['address']in coverage]),'total_decoded_caller_instructions':len(decoded),'uncovered_instructions':[row for row in decoded if row['address']not in coverage],
            'source_sha256':{name:select.binary_tools.sha(source/name)for name in ['biwn_world_update.c','biwn_world_update.h']},'compiler':command,
            'camera_register_seed_adapter':{'target':'0xf0fa','logical_inputs':['D2low16=previousstatus','D3low16=boundarydecision'],'original_stack_arguments':0,'checked_against_original_registers':True},'matched':['Complete original CPU caller executes with actual original digit helper; external dependencies scripted identically at original call boundaries.','Every external read/write width,address,value/order and helper target/argument/order; whole externally visible2MB RAM; private stack excluded.','Original RTS/stack balance and callee-saved registers; signed clamp,14bit fractional carry,16/32bit position wrap,all boundary directions,collision restore/retain/camera rules and camera-return sign/change flag under fixtures.'],
            'limits':['Polling/input helper,GPU movement helper,redraw,collision helpers,camera helper,animation update andentity update remain scripted dependencies in this test.','Not original helper execution, rebuilt full scene/main loop,physical controller,hardware timing or complete game.','Private stack,caller-saved register/CCR ABI and arbitrary asynchronous schedules excluded.','Host callback errors/poll limits are added behavior; preserve earlier effects.']}
    save(out/'report.json',report);save(out/'status.json',{'status':'terminal','exit_code':0})
    if not options.limit:save(ROOT/'verification/biwn-world-update-checks.json',report)
    print(json.dumps(report),flush=True)

if __name__=='__main__':main()
