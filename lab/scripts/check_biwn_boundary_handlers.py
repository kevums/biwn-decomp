"""Original CPU boundary handlers vs high-level C with nested helper scripts."""
import argparse,ctypes as c,hashlib,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_world_update as world
ROOT=world.ROOT;SP=world.SP;STOP=world.STOP;REGS=world.REGS
HELPERS=[0x1039c,0x10430,0x102c4,0x1028e,0x10652,0x20e8c,0x20f0c,0xdf60,0x1aa40,0x20f78]
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')

class Script:
    def __init__(self,snapshot,case):
        self.memory=bytearray(snapshot);self.case=case;self.trace=[];self.changed=[];self.errors=[];self.read_counts={}
        self.fail_read=None;self.fail_write=None;self.fail_call=None
        for a,w,v in case['initial']:self.put(a,w,v)
        self.changed=[]
    def put(self,a,w,v):
        assert 0<=a<=0x200000-w
        v&=(1<<(8*w))-1;self.memory[a:a+w]=v.to_bytes(w,'big');self.changed.append((a,w,v))
    def read(self,a,w):
        if self.fail_read==(a,w):raise RuntimeError('injected read failure')
        assert 0<=a<=0x200000-w
        for entry in self.case.get('read_queues',[]):
            if entry['address']==a and entry['width']==w:
                key=(a,w);n=self.read_counts.get(key,0);values=entry['values'];self.put(a,w,values[min(n,len(values)-1)]);self.read_counts[key]=n+1
        v=int.from_bytes(self.memory[a:a+w],'big');self.trace.append(['r',a,w,v]);return v
    def write(self,a,w,v):
        if self.fail_write==(a,w):raise RuntimeError('injected write failure')
        self.put(a,w,v);self.trace.append(['w',a,w,v])
    def call(self,a,args):
        if self.fail_call==a:raise RuntimeError('injected dependency failure')
        assert a in HELPERS;self.trace.append(['call',a,args])
        for target,address,width,value in self.case.get('helper_effects',[]):
            if target==a:self.put(address,width,value)
        return self.case.get('helper_returns',{}).get(str(a),self.case['default_helper_return'])&0xffffffff

def make_cpu(script,entry,params,incoming):
    cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(script.memory))
    args=(b''.join(v.to_bytes(2,'big')for v in params)if entry==0x19f2c else params[0].to_bytes(4,'big')+params[1].to_bytes(2,'big'))
    cpu.mem_write(SP,STOP.to_bytes(4,'big')+args)
    for reg,value in zip(REGS,incoming):cpu.reg_write(reg,value)
    cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP)
    return cpu,args

def original(script,case,coverage):
    entry=case['entry'];cpu,args=make_cpu(script,entry,case['params'],case['incoming']);steps=[]
    for target in HELPERS:cpu.mem_write(target,b'\x4e\x75')
    def code(engine,a,w,_):
        if a in HELPERS:
            stack=engine.reg_read(UC_M68K_REG_A7)
            def arg(offset,width):return int.from_bytes(engine.mem_read(stack+offset,width),'big')
            if a in [0x1039c,0x10652]:values=[arg(4,4),arg(8,2)]
            elif a==0x10430:values=[arg(4,4),arg(8,2),arg(10,2)]
            elif a in [0x102c4,0x1028e]:values=[arg(4,4)]
            elif a in [0x1aa40,0x20f78]:values=[arg(4,2)]
            else:values=[]
            script.changed=[];result=script.call(a,values)
            for address,width,value in script.changed:engine.mem_write(address,value.to_bytes(width,'big'))
            engine.reg_write(UC_M68K_REG_D0,result);return
        assert 0x19f2c<=a<0x1a0f8,hex(a);steps.append(a);coverage.add(a)
    def read(engine,access,a,w,v,_):
        if SP-0x1000<=a<SP+16:return
        engine.mem_write(a,script.read(a,w).to_bytes(w,'big'))
    def write(engine,access,a,w,v,_):
        if SP-0x1000<=a<SP+16:return
        script.write(a,w,v&((1<<(8*w))-1))
    cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(entry,STOP,count=4096,timeout=500000)
    assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
    for i,reg in enumerate(REGS):
        if i not in [0,1,8,9]:assert cpu.reg_read(reg)==case['incoming'][i]
    assert bytes(cpu.mem_read(SP+4,len(args)))==args
    actual=bytearray(cpu.mem_read(0,0x200000))
    for target in HELPERS:actual[target:target+2]=script.memory[target:target+2]
    assert actual[:SP-0x1000]==script.memory[:SP-0x1000] and actual[SP+16:]==script.memory[SP+16:]
    return cpu.reg_read(UC_M68K_REG_D0),len(steps)

def translated(functions,script,case,missing=None,limit=64):
    def reader(width):
        def callback(_,a,v):
            try:v[0]=script.read(a,width);return 0
            except Exception as error:script.errors.append(str(error));return 1
        return callback
    def write(_,a,v):
        try:script.write(a,2,v);return 0
        except Exception as error:script.errors.append(str(error));return 1
    def call(_,a,args,count,result):
        try:result[0]=script.call(a,list(args[:count]));return 0
        except Exception as error:script.errors.append(str(error));return 1
    types=[world.R16,world.R32,world.W16,world.CALL];callbacks=[world.R16(reader(2)),world.R32(reader(4)),world.W16(write),world.CALL(call)]
    if missing is not None:callbacks[missing]=types[missing]()
    bus=world.Bus(world.R8(),callbacks[0],callbacks[1],callbacks[2],world.W32(),callbacks[3],None,1);out=c.c_uint32(0xa5a55a5a)
    if case['entry']==0x19f2c:status=functions[0x19f2c](c.byref(bus),*case['params'],case['incoming'][0],c.byref(out))
    else:status=functions[0x19fda](c.byref(bus),*case['params'],case['incoming'][0],case['incoming'][1],limit,c.byref(out))
    return status,out.value

def make_cases(snapshot):
    rng=random.Random(0x19f2c);cases=[];returns=[0,1,0xffff,0x12340000,0xabcd0001]
    def incoming():return [rng.getrandbits(32)for _ in REGS]
    for kind in range(16):
        for low in [0,1,0x7ff,0xffe,0xfff,rng.randrange(4096)]:
            for result in returns:
                cases.append({'kind':'edge_class','entry':0x19f2c,'params':[(kind<<12)|low,rng.randrange(65536),rng.randrange(65536)],'incoming':incoming(),'initial':[[0x49c60,2,0xa55a],[0x49c8c,2,rng.randrange(65536)]],'default_helper_return':result})
    for delta in [0,1,5,0xffff,0xfffb,0x7fff,0x8000]:
        for old in [0,1,0xffff,0x7fff,0x8000,0xfffe,rng.randrange(65536)]:
            for result in returns:
                for mutation in [False,True]:
                    cases.append({'kind':'relative_neighbor_reread','entry':0x19f2c,'params':[0xffff,0,delta],'incoming':incoming(),'initial':[[0x49c8c,2,old]],'default_helper_return':result,'helper_effects':[[0x102c4,0x49c8c,2,0x1337]]if mutation else[]})
    object=0x81000;node=0x80000
    layouts=['no_index','zero_flags','target','transition_pass','transition_fail','transition_level','late_match','terminator_miss','matching_negative_flags','target_reread','index_reread','cross64k']
    for direction in [0,1,2,3,4,0xffff,0x8000,0x7fff]:
        for layout in layouts:
            for index in [0,1,0xfffe,0x7fff,0x8000]:
                inc=incoming();initial=[[0x49c18,4,node],[0x49c60,2,2],[0x49c62,2,1 if layout=='transition_level' else 0],[object+6,2,rng.randrange(65536)],[object+8,2,rng.randrange(65536)],[object+0x16,2,0xffff if layout=='no_index' else index]]
                for address in [0x49c52,0x49c7e,0x49c58,0x49c86,0x49c82,0x49c8a]:initial.append([address,2,rng.choice([0,1,0x7fff,0x8000,0xffff,rng.randrange(65536)])])
                case={'kind':layout,'entry':0x19fda,'params':[object,direction],'incoming':inc,'initial':initial,'default_helper_return':rng.choice(returns)}
                # Derive the key by executing the unchanged original prefix,
                # rather than reproducing the C key formula in the fixtures.
                prefix=Script(snapshot,case);cpu,_=make_cpu(prefix,0x19fda,case['params'],inc);cpu.emu_start(0x19fda,0x1a05a,count=64,timeout=500000);assert cpu.reg_read(UC_M68K_REG_PC)==0x1a05a;key=cpu.reg_read(UC_M68K_REG_D1)&0xffff
                actual_index=0xfffe if layout=='index_reread' else index
                signed_index=actual_index if actual_index<0x8000 else actual_index-65536
                base=0x9fffc if layout=='cross64k' else 0x90000
                pointer=base+signed_index*6
                case['initial'].append([node+8,4,base])
                flags=0 if layout in ['zero_flags','cross64k'] else 0x9000 if layout=='matching_negative_flags' else 0x7000
                target=0xffff if layout.startswith('transition') else 0x1234
                offset=12 if layout=='late_match' else 6 if layout=='cross64k' else 0
                if offset:
                    for j in range(offset//6):case['initial'] += [[pointer+j*6,2,key^1],[pointer+j*6+2,2,0],[pointer+j*6+4,2,0]]
                case['initial'] += [[pointer+offset,2,key^1 if layout=='terminator_miss' else key],[pointer+offset+2,2,0x8000 if layout=='terminator_miss' else flags],[pointer+offset+4,2,target]]
                if layout=='transition_pass':case['helper_returns']={str(0x1028e):0x12340001}
                if layout=='transition_fail':case['helper_returns']={str(0x1028e):0x12340000}
                if layout=='target_reread':case['read_queues']=[{'address':pointer+4,'width':2,'values':[9,0xffff]}]
                if layout=='index_reread':case['read_queues']=[{'address':object+0x16,'width':2,'values':[1,0xfffe]}]
                case['original_prefix_key']=key;cases.append(case)
    return cases

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);options=parser.parse_args()
    s=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(s/'nextstage-68000-candidate.bin').read_bytes();assert world.select.stage.digest(image)==world.select.stage.STAGE_SHA
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();assert snapshot[0x19f2c:0x1a0f8]==image[0x19f2c-0x4000:0x1a0f8-0x4000]
    out=ROOT/'verification/biwn-boundary-handlers'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libboundary-handlers.dylib'
    compiler=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_boundary_handlers.c'),'-o',str(library)];result=subprocess.run(compiler,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});assert result.returncode==0,result.stderr
    lib=c.CDLL(str(library));one=lib.biwn_boundary_type1;one.argtypes=[c.POINTER(world.Bus),c.c_uint16,c.c_uint16,c.c_uint16,c.c_uint32,c.POINTER(c.c_uint32)];one.restype=c.c_int;two=lib.biwn_boundary_type2;two.argtypes=[c.POINTER(world.Bus),c.c_uint32,c.c_uint16,c.c_uint32,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];two.restype=c.c_int;functions={0x19f2c:one,0x19fda:two}
    cases=make_cases(snapshot)
    if options.limit:cases=cases[:options.limit]
    coverage=set();rows=[]
    for i,case in enumerate(cases):
        save(out/'status.json',{'status':'running','case':i,'entry':hex(case['entry'])});a=Script(snapshot,case);b=Script(snapshot,case);d0,steps=original(a,case,coverage);status,actual=translated(functions,b,case)
        if status or d0!=actual or a.trace!=b.trace or a.memory!=b.memory:
            save(out/'mismatch.json',{'case':i,'parameters':case,'original_D0':d0,'C_D0':actual,'C_status':status,'C_errors':b.errors,'original_trace':a.trace,'C_trace':b.trace,'RAM_differences':[[j,a.memory[j],b.memory[j]]for j in range(len(a.memory))if a.memory[j]!=b.memory[j]][:100]});raise AssertionError(str(out/'mismatch.json'))
        rows.append({'case':i,'parameters':case,'original_CPU_instructions':steps,'full_D0':d0,'trace':b.trace,'whole_external_RAM_and_trace_match':True})
    save(out/'fixtures.json',rows)
    if options.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'preflight_cases':len(rows),'directory':str(out)}),flush=True);return
    guards=[]
    for entry,fn in functions.items():
        case=next(x['parameters']for x in rows if x['parameters']['entry']==entry)
        null_args=[None,*case['params'],case['incoming'][0]]+([case['incoming'][1],64]if entry==0x19fda else[])+[c.byref(c.c_uint32())];assert fn(*null_args)==1;guards.append({'null_bus_entry':hex(entry),'status':1})
        for missing in ([0,2,3]if entry==0x19f2c else[0,1,2,3]):
            script=Script(snapshot,case);status,d0=translated(functions,script,case,missing=missing);assert status==1 and d0==0xa5a55a5a and not script.trace;guards.append({'missing_callback_entry':hex(entry),'index':missing,'status':1})
    for target in HELPERS:
        case=next(x['parameters']for x in rows if any(t[0]=='call'and t[1]==target for t in x['trace']));script=Script(snapshot,case);script.fail_call=target;status,d0=translated(functions,script,case);assert status==4 and d0==0xa5a55a5a;guards.append({'helper_failure':hex(target),'status':4,'partial_trace':script.trace})
    case=next(x['parameters']for x in rows if x['parameters']['entry']==0x19fda and x['parameters']['kind']=='late_match');script=Script(snapshot,case);status,d0=translated(functions,script,case,limit=1);assert status==2 and d0==0xa5a55a5a;guards.append({'scan_limit':1,'status':2,'partial_trace':script.trace})
    script=Script(snapshot,case);status,d0=translated(functions,script,case,limit=0);assert status==1 and not script.trace;guards.append({'zero_scan_limit':True,'status':1})
    script=Script(snapshot,case);script.fail_read=(0x49c18,4);status,d0=translated(functions,script,case);assert status==3 and d0==0xa5a55a5a;guards.append({'failed_read':'49c18long','status':3})
    case=next(x['parameters']for x in rows if x['parameters']['entry']==0x19f2c and x['parameters']['params'][0]==0xffff);script=Script(snapshot,case);script.fail_write=(0x49c8c,2);status,d0=translated(functions,script,case);assert status==3 and d0==0xa5a55a5a;guards.append({'failed_write':'49c8cword','status':3})
    save(out/'guards.json',guards);decoded,decoder=world.select.binary_tools.m68k_instructions(image[0x19f2c-0x4000:0x1a0f8-0x4000],0x19f2c);missing=[row for row in decoded if row['address']not in coverage];save(out/'original-decode.json',{'instructions':decoded,'decoder':decoder,'uncovered':missing});assert not missing
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'two_original_CPU_boundary_handlers_match_C','directory':str(out),'CPU_cases':len(rows),'type1_cases':sum(row['parameters']['entry']==0x19f2c for row in rows),'type2_cases':sum(row['parameters']['entry']==0x19fda for row in rows),'host_guards':len(guards),'covered_CPU_instructions':len(decoded),'CPU_instruction_count':len(decoded),'original_interval':'[0x19f2c,0x1a0f8)','original_bytes':460,'portable_components':2,
            'source_sha256':{name:world.select.binary_tools.sha(source/name)for name in ['biwn_boundary_handlers.c','biwn_boundary_handlers.h']},'compiler':compiler,
            'matched':['Both complete originalCPU functions and fullD0 vsC; privateRTSstack/argument preservation and callee-saved registers.','Every externalRAM read/write width,address,value/order and nestedhelper target/args/order; whole externally visibleRAM.','Edge class masks, tentatively changed neighborword and posthelper reread/subtract, signed16coordinate differences/ASR6, signedtable index*6, sixbyte records, negative mismatch terminators and matching negative flags.','Index/target rereads can change values; CLR.W keepsupperD0; original prefix computesfixture keys independently of C.'],
            'remaining_dependencies':[hex(x)for x in HELPERS],
            'limits':['Nested geometry/transition helper functions remain identical scriptedRTSboundaries, not original helper execution or complete collision geometry.','No GPU/scene/main-loop/hardware scheduling proof; private stack and fullCCR/caller-savedABI excluded.','Finite mainRAM tables and scripted rereads, not arbitrary asynchronous changes; added hostscanlimits/callback errors preserve partial effects.']}
    save(out/'report.json',report);save(ROOT/'verification/biwn-boundary-handlers-checks.json',report);save(out/'status.json',{'status':'terminal','exit_code':0});print(json.dumps(report),flush=True)

if __name__=='__main__':main()
