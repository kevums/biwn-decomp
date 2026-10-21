"""Five complete pure-CPU geometry functions versus high-level callback C."""
import argparse,ctypes as c,hashlib,json,os,random,subprocess
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_boundary_handlers as boundary
world=boundary.world;ROOT=world.ROOT;SP=world.SP;STOP=world.STOP;REGS=world.REGS
RANGES={0x1028e:0x102c4,0x102c4:0x1039c,0x1039c:0x10430,0x10430:0x10520,0x10652:0x106c4}
NAMES={0x1028e:'biwn_geometry_outside',0x102c4:'biwn_geometry_find_tile',0x1039c:'biwn_geometry_select_tile',0x10430:'biwn_geometry_select_portal',0x10652:'biwn_geometry_select_region'}
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')

def cpu_for(script,case):
    cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(script.memory))
    args=case['params'][0].to_bytes(4,'big')+b''.join(x.to_bytes(2,'big')for x in case['params'][1:]);cpu.mem_write(SP,STOP.to_bytes(4,'big')+args)
    for reg,value in zip(REGS,case['incoming']):cpu.reg_write(reg,value)
    cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP)
    return cpu,args

def original(script,case,coverage,prefix=None):
    cpu,args=cpu_for(script,case);steps=[];entry=case['entry']
    def code(engine,a,w,_):
        if a==prefix:engine.emu_stop();return
        assert entry<=a<RANGES[entry],hex(a);coverage.add(a);steps.append(a)
    def read(engine,access,a,w,v,_):
        if SP-0x1000<=a<SP+16:return
        engine.mem_write(a,script.read(a,w).to_bytes(w,'big'))
    def write(engine,access,a,w,v,_):
        if SP-0x1000<=a<SP+16:return
        script.write(a,w,v&((1<<(8*w))-1))
    cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(entry,STOP,count=10000,timeout=500000)
    if prefix is not None:return cpu
    assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
    for i,reg in enumerate(REGS):
        if i not in [0,1,8,9]:assert cpu.reg_read(reg)==case['incoming'][i]
    assert bytes(cpu.mem_read(SP+4,len(args)))==args
    actual=bytes(cpu.mem_read(0,0x200000));assert actual[:SP-0x1000]==script.memory[:SP-0x1000]and actual[SP+16:]==script.memory[SP+16:]
    return cpu.reg_read(UC_M68K_REG_D0),len(steps)

def translated(functions,script,case,missing=None,limit=64):
    def reader(width):
        def callback(_,a,v):
            try:v[0]=script.read(a,width);return 0
            except Exception as error:script.errors.append(str(error));return 1
        return callback
    def writer(width):
        def callback(_,a,v):
            try:script.write(a,width,v);return 0
            except Exception as error:script.errors.append(str(error));return 1
        return callback
    types=[world.R8,world.R16,world.R32,world.W16,world.W32];callbacks=[types[0](reader(1)),types[1](reader(2)),types[2](reader(4)),types[3](writer(2)),types[4](writer(4))]
    if missing is not None:callbacks[missing]=types[missing]()
    bus=world.Bus(*callbacks,world.CALL(),None,0);out=c.c_uint32(0xa5a55a5a);entry=case['entry'];params=case['params']
    if entry==0x1028e:status=functions[entry](c.byref(bus),*params,case['incoming'][0],c.byref(out))
    elif entry==0x102c4:status=functions[entry](c.byref(bus),*params,limit,c.byref(out))
    elif entry==0x10430:status=functions[entry](c.byref(bus),*params,case['incoming'][1],case['incoming'][3],c.byref(out))
    elif entry==0x10652:status=functions[entry](c.byref(bus),*params,case['incoming'][0],c.byref(out))
    else:status=functions[entry](c.byref(bus),*params,c.byref(out))
    return status,out.value

def bind(lib):
    result={}
    for entry,name in NAMES.items():
        fn=getattr(lib,name);types=[c.POINTER(world.Bus),c.c_uint32]
        if entry in [0x1039c,0x10430,0x10652]:types.append(c.c_uint16)
        if entry==0x10430:types += [c.c_uint16,c.c_uint32,c.c_uint32]
        elif entry in [0x1028e,0x102c4,0x10652]:types.append(c.c_uint32)
        types.append(c.POINTER(c.c_uint32));fn.argtypes=types;fn.restype=c.c_int;result[entry]=fn
    return result

def cases(snapshot):
    rng=random.Random(0x1028e);rows=[];obj=0x80000;container=0x82000;scene=0x84000;table=0x100000
    words=[0,1,15,16,511,512,1023,1024,0x7fff,0x8000,0xffff]
    longs=[0,1,63,64,1023,1024,0xffffffff,0xffffffc0,0x7fffffff,0x80000000]
    def create(entry,kind):
        return {'entry':entry,'kind':kind,'params':[obj],'incoming':[rng.getrandbits(32)for _ in REGS],'initial':[],'default_helper_return':0}
    for x in [-101,-100,-1,0,99,100,101,-2147483648,2147483647]:
        for z in [-101,-100,0,99,100,101,-2147483648,2147483647]:
            for d0 in [0,0xabcd1234]:
                case=create(0x1028e,'signed_bounds');case['incoming'][0]=d0;case['initial']=[[obj+4,4,x],[obj+10,4,z],[obj+0x1e,4,-100],[obj+0x1a,4,100],[obj+0x26,4,-100],[obj+0x22,4,100]];rows.append(case)
    for entry in [0x1039c,0x10430,0x10652]:
        for i in range(192):
            room=rng.choice([0,1,0xffff,0x7fff,0x8000]);index=rng.choice([0,1,2,0xffff,0xfffe,0x7fff,0x8000]);count=rng.choice([0,1,2,3,0x7fff,0x8000,0xffff]);signed_room=room if room<0x8000 else room-65536;signed_index=index if index<0x8000 else index-65536
            stride={0x1039c:20,0x10430:28,0x10652:24}[entry];record=table+signed_index*stride
            case=create(entry,'record_selection');case['params'].append(index);case['initial']=[[obj+0x40,2,room],[0x49bb4+signed_room*4,4,container],[container,2,count],[container+2,2,count],[container+8,4,table],[container+12,4,table],[0x49c18,4,scene],[scene,2,count],[scene+4,4,table],[obj+4,4,rng.choice(longs)],[obj+10,4,rng.choice(longs)]]
            for offset in [0x1a,0x1e,0x22,0x26,0x48,0x4c,0x50,0x54]:case['initial'].append([obj+offset,4,rng.getrandbits(32)])
            for offset in range(0,28,2):case['initial'].append([record+offset,2,rng.choice(words)])
            if entry==0x10430:
                direction=rng.choice([0,1,2,3,4,0xffff]);case['params'].append(direction);case['initial'].append([record+26,2,0xffff if i%7==0 else 7])
                prefix=boundary.Script(snapshot,case);cpu=original(prefix,case,set(),prefix=0x104ce)
                if cpu.reg_read(UC_M68K_REG_PC)==0x104ce:
                    key=cpu.reg_read(UC_M68K_REG_D1)&0xffff;case['original_prefix_key']=key
                    if direction<4:case['initial'].append([record+[11,13,15,17][direction],1,key if i%3==0 else 0x80 if i%3==1 else(key+1)&15])
                    elif i%3==0:case['incoming'][3]=(case['incoming'][3]&0xffff0000)|key
            if i%17==0 and entry in [0x1039c,0x10652]:
                address=obj+(0x4c if entry==0x1039c else 0x34);case['read_queues']=[{'address':address,'width':4,'values':[0x12345678]}]
            rows.append(case)
    for count in [0,1,2,5,0x8000,0x8001,0xffff]:
        for layout in ['first_match','later_match','none','overflow_extent','signed_extent']:
            if count==0x8000 and layout!='first_match':continue
            for j in range(16):
                case=create(0x102c4,'scan_'+layout);room=rng.choice([0,1,0xffff]);signed_room=room if room<0x8000 else room-65536
                x=rng.choice(longs);z=rng.choice(longs);case['initial']=[[obj+0x40,2,room],[0x49bb4+signed_room*4,4,container],[container,2,count],[container+8,4,table],[obj+4,4,x],[obj+10,4,z]]
                prefix=boundary.Script(snapshot,case);cpu=original(prefix,case,set(),prefix=0x102f6);assert cpu.reg_read(UC_M68K_REG_PC)==0x102f6;xkey=cpu.reg_read(UC_M68K_REG_D3)&0xffff;zkey=cpu.reg_read(UC_M68K_REG_D2)&0xffff
                n=(count-1)&0xffff
                if n<0x8000:
                    for k in range(n+1 if n<16 else 1):
                        index=n-k;record=table+index*20;match=(layout=='first_match'and k==0)or(layout=='later_match'and k==min(n,2))
                        start_x=xkey if match else 16;extent_x=1 if match else 0
                        if layout=='overflow_extent':start_x=0x7fff;extent_x=1
                        if layout=='signed_extent':start_x=0xffff;extent_x=17
                        case['initial'] += [[record+10,2,start_x],[record+14,2,zkey if match or layout=='signed_extent'else 16],[record+16,2,extent_x],[record+18,2,1 if match or layout=='signed_extent'else 0]]
                if j%5==0:case['read_queues']=[{'address':obj+4,'width':4,'values':[x,0x12345678]},{'address':obj+10,'width':4,'values':[z,0xffffffc0]}]
                rows.append(case)
    return rows

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);options=parser.parse_args()
    s=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(s/'nextstage-68000-candidate.bin').read_bytes();assert world.select.stage.digest(image)==world.select.stage.STAGE_SHA
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
    for a,b in RANGES.items():assert snapshot[a:b]==image[a-0x4000:b-0x4000]
    out=ROOT/'verification/biwn-geometry'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libgeometry.dylib'
    compiler=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_geometry.c'),'-o',str(library)];run=subprocess.run(compiler,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});assert run.returncode==0,run.stderr
    functions=bind(c.CDLL(str(library)));fixtures=cases(snapshot)
    if options.limit:fixtures=fixtures[:options.limit]
    coverage=set();rows=[]
    for i,case in enumerate(fixtures):
        save(out/'status.json',{'status':'running','case':i,'entry':hex(case['entry'])});a=boundary.Script(snapshot,case);b=boundary.Script(snapshot,case);d0,steps=original(a,case,coverage);status,result=translated(functions,b,case)
        if status or result!=d0 or a.trace!=b.trace or a.memory!=b.memory:
            save(out/'mismatch.json',{'case':i,'parameters':case,'original_D0':d0,'C_D0':result,'C_status':status,'C_errors':b.errors,'original_trace':a.trace,'C_trace':b.trace,'RAM_differences':[[j,a.memory[j],b.memory[j]]for j in range(len(a.memory))if a.memory[j]!=b.memory[j]][:100]});raise AssertionError(str(out/'mismatch.json'))
        rows.append({'case':i,'parameters':case,'original_CPU_instructions':steps,'full_D0':d0,'trace':b.trace,'whole_external_RAM_and_trace_match':True})
    save(out/'fixtures.json',rows)
    if options.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'preflight_cases':len(rows),'directory':str(out)}),flush=True);return
    guards=[]
    for entry in functions:
        case=next(row['parameters']for row in rows if row['parameters']['entry']==entry)
        required=[2]if entry==0x1028e else[1,2,3,4]
        if entry==0x10430:required=[0]+required
        for missing in required:
            script=boundary.Script(snapshot,case);status,value=translated(functions,script,case,missing=missing);assert status==1 and value==0xa5a55a5a and not script.trace;guards.append({'entry':hex(entry),'missing_callback':missing,'status':1})
    scan=next(row['parameters']for row in rows if row['parameters']['entry']==0x102c4 and row['parameters']['kind']=='scan_later_match'and row['full_D0']==1 and len([t for t in row['trace']if t[0]=='r'and t[1]==0x82008])>1)
    script=boundary.Script(snapshot,scan);status,value=translated(functions,script,scan,limit=1);assert status==2 and value==0xa5a55a5a;guards.append({'scan_limit':1,'status':2,'partial_trace':script.trace})
    script=boundary.Script(snapshot,scan);status,value=translated(functions,script,scan,limit=0);assert status==1 and not script.trace;guards.append({'zero_scan_limit':True,'status':1})
    for entry in [0x1039c,0x10430,0x10652]:
        row=next(row for row in rows if row['parameters']['entry']==entry and row['full_D0']==1);case=row['parameters'];first_write=next(t for t in row['trace']if t[0]=='w');script=boundary.Script(snapshot,case);script.fail_write=(first_write[1],first_write[2]);status,value=translated(functions,script,case);assert status==3 and value==0xa5a55a5a;guards.append({'entry':hex(entry),'failed_write':first_write[1:3],'status':3})
    save(out/'guards.json',guards);decodes=[];missing=[]
    for a,b in RANGES.items():
        decoded,decoder=world.select.binary_tools.m68k_instructions(image[a-0x4000:b-0x4000],a);decodes.extend(decoded);missing.extend(row for row in decoded if row['address']not in coverage)
    save(out/'original-decodes.json',{'instructions':decodes,'uncovered':missing});assert not missing,[(hex(row['address']),row['assembly'])for row in missing]
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'five_original_CPU_geometry_functions_match_C','directory':str(out),'CPU_cases':len(rows),'entry_cases':{hex(a):sum(row['parameters']['entry']==a for row in rows)for a in RANGES},'host_guards':len(guards),'CPU_instruction_coverage':[len(decodes),len(decodes)],'portable_components':5,'intervals':{hex(a):hex(b)for a,b in RANGES.items()},'original_bytes':sum(b-a for a,b in RANGES.items()),'nested_helper_calls':0,'source_sha256':{name:world.select.binary_tools.sha(source/name)for name in ['biwn_geometry.c','biwn_geometry.h']},'compiler':compiler,
        'matched':['Five complete original CPU functions execute without helper stubs; fullD0, privateRTSstack/arguments and callee-saved registers.','Every external read/write width,address,value/order and whole externally visibleRAM.','Signed half-open bounds, reverse20byte tile lookup, negative accepted indexes,28byte portal/24byte region selection, signedbyte matching, word-vs-long shift6 and all declared rereads.'],
        'limits':['Finite synthetic mainRAM layouts and scripted rereads, not complete gameplay/scene/physicalhardware or arbitrary aliasing/scheduling.','FullCCR and caller-saved registers exceptD0 excluded; hostscanlimits/errors are added, with earlier stores retained and outputD0 unchanged.','Geometry functions not yet linked into the current world pipeline at this standalone checkpoint.']}
    save(out/'report.json',report);save(ROOT/'verification/biwn-geometry-checks.json',report);save(out/'status.json',{'status':'terminal','exit_code':0});print(json.dumps(report),flush=True)

if __name__=='__main__':main()
