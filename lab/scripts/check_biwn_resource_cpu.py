"""Resource/heap/copy fullCPU, native+Unicorn; adapters explicitly scoped."""
import argparse,ctypes as c,hashlib,json,os,random,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_resources as resources
import check_biwn_memory as memory
import check_biwn_transition_cleanup as cleanup
import check_biwn_input_dispatch_cpu as prior
import generate_biwn_resource_cpu as gen
ROOT=prior.ROOT;CPU=prior.CPU;SP=prior.SP;STOP=prior.STOP;save=prior.save;world=prior.oracle.live.world
ENTRIES=set(gen.RANGES)|{0xe3ee};RETURNS={0x1b042,0x1b000,0x15578,0x1545a,0x152a0,0x1b152,0xe4a8};WIDTHS={**resources.WIDTHS,0x1b002:[2],0x1af04:[2],0x15200:[],0xe3ee:[4]*3}
def make_cpu(case):
    cpu=CPU();cpu.registers[:]=case['registers'];cpu.pc=case['entry'];cpu.sr=case['SR'];cpu.usp=case['usp'];cpu.ssp=case['ssp'];return cpu
class Runtime(prior.oracle.Runtime):
    def __init__(self,library,rows):
        super().__init__(library);self.rows={r['address']:r for r in rows};self.fn=self.lib.biwn_resource_cpu_body;self.call=self.lib.biwn_resource_cpu_call
        for fn in [self.fn,self.call]:fn.argtypes=[c.POINTER(world.Bus),c.POINTER(CPU),memory.W8,prior.oracle.world_cpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];fn.restype=c.c_int
        self.ea=prior.Runtime.ea.__get__(self,Runtime)
    def cpu(self):
        state=CPU();state.registers[:]=[self.core.m68k_get_reg(None,i)for i in range(16)];state.pc=self.core.m68k_get_reg(None,16);state.sr=self.core.m68k_get_reg(None,17);state.usp=self.prefix[16]if state.sr&0x2000 else state.registers[15];state.ssp=state.registers[15]if state.sr&0x2000 else self.prefix[17];return state
    def reset(self,ram,case,mode):
        super().reset(ram,case,mode);self.case=case;self.calls=[];self.script_count=0
        self.script=(resources.Script if case['family']=='resource'else memory.Script if case['family']in ['memory','copy']else cleanup.Script)(ram,case)
    def actual(self,target):
        if target not in ENTRIES:return False
        if self.case['family']=='resource':return target==0xe3e0 and self.case['entry']==0x1b044
        return True
    def args(self,state,target):
        offset=4;args=[]
        for width in WIDTHS.get(target,[]):args.append(int.from_bytes(c.string_at(self.device.pointer+state.registers[15]+offset,width),'big'));offset+=width
        return args
    def scripted(self,state,target):
        args=self.args(state,target);row={'target':target,'args':args,'actual_body':False,'incoming':prior.cpu_dict(state)};self.calls.append(row)
        self.script.memory[:]=self.device.ram();self.script.changed=[];self.script.bulk=[];value=self.script.call(target,args)
        for a,w,v in self.script.changed:self.device.direct(a,w,v)
        for a,payload in self.script.bulk:c.memmove(self.device.pointer+a,payload,len(payload))
        self.script_count+=1;seed=(target+self.script_count*1234567)&0xffffffff;state.registers[0]=value
        for r in [1,8,9]:state.registers[r]=(seed*r+0xaabbccdd)&0xffffffff
        state.sr=(state.sr&0xffe0)|(seed&31);row['return']=prior.cpu_dict(state)
    def read(self,a,w):
        if self.case['entry']==0x1b044 and a==0xbd848 and w==4:self.device.direct(a,w,self.script.read(a,w))
        return super().read(a,w)
    def native_inputs(self,pc):
        if self.case['entry']==0x1b044 and pc in [0x1b0c4,0x1b0da]:self.device.direct(0xbd848,4,self.script.read(0xbd848,4))
        if not any(self.queues.values()):return
        row=self.rows[pc];op,_,tail=row['assembly'].partition(' ');kind=op.split('.')[0];parts=gen.base.split(tail);width={'b':1,'w':2,'l':4}.get(op[-1],4)
        reads=parts[:1]if kind in ['move','movea','tst','suba','adda']else parts[1:2]if kind in ['cmpi','btst']else parts if kind in ['add','addq','addi','sub','subq','andi','and','or','cmp','cmpa']else[]
        regs=[self.core.m68k_get_reg(None,i)for i in range(16)]
        for text in reads:
            a=self.ea(text,regs);queue=self.queues.get((a,width))
            if queue:self.device.direct(a,width,queue.pop(0))
    def native(self,ram,case,coverage):
        self.reset(ram,case,0);prior.oracle.lifecycle.seed_cpu(self,make_cpu(case));external=[a for a in resources.WIDTHS if a!=case['entry']and not self.actual(a)];stack=[];steps=[]
        for a in external:self.device.direct(a,2,0x4e75)
        try:
            for _ in range(300000):
                pc=self.core.m68k_get_reg(None,16)
                if pc==STOP:break
                if pc in external:
                    state=self.cpu();self.scripted(state,pc)
                    for r in [0,1,8,9]:self.core.m68k_set_reg(r,state.registers[r])
                    self.core.m68k_set_reg(17,state.sr)
                else:
                    assert pc in self.rows,hex(pc);self.native_inputs(pc);steps.append(pc);coverage.add(pc)
                    if pc in ENTRIES and self.core.m68k_get_reg(None,15)!=SP:
                        state=self.cpu();row={'target':pc,'args':self.args(state,pc),'actual_body':True,'incoming':prior.cpu_dict(state)};self.calls.append(row);stack.append(row)
                    if pc in RETURNS and stack:stack.pop()['return']=prior.cpu_dict(self.cpu())
                self.core.m68k_execute(1)
            else:raise AssertionError('Native resource CPU did not return')
        finally:
            for a in external:self.device.direct(a,2,int.from_bytes(ram[a:a+2],'big'))
        assert not stack
        return self.device.ram(),self.cpu(),{'steps':steps,'calls':self.calls,'device':self.device.stats()}
    def unicorn(self,ram,case,coverage):
        self.reset(ram,case,0);engine=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);engine.ctl_set_cpu_model(UC_CPU_M68K_M68000);engine.mem_map(0,0x200000);engine.mem_map(0xf02000,0x2000);engine.mem_write(0,ram)
        external=[a for a in resources.WIDTHS if a!=case['entry']and not self.actual(a)]
        for a in external:engine.mem_write(a,b'\x4e\x75')
        for reg,v in zip(world.REGS,case['registers']):engine.reg_write(reg,v)
        engine.reg_write(UC_M68K_REG_SR,case['SR']);engine.reg_write(UC_M68K_REG_A7,SP)
        def code(cpu,pc,w,_):
            if pc in external:
                state=make_cpu(case);state.registers[:]=[cpu.reg_read(r)for r in world.REGS]+[cpu.reg_read(UC_M68K_REG_A7)];state.pc=pc
                self.scripted(state,pc)
                for reg in [0,1,8,9]:cpu.reg_write(world.REGS[reg],state.registers[reg])
                cpu.reg_write(UC_M68K_REG_SR,state.sr)
                for a,width,v in self.script.changed:cpu.mem_write(a,v.to_bytes(width,'big'))
                for a,payload in self.script.bulk:cpu.mem_write(a,payload)
            else:assert pc in self.rows,hex(pc);coverage.add(pc)
        def read(cpu,access,a,w,v,_):cpu.mem_write(a,self.read(a,w).to_bytes(w,'big'))
        def write(cpu,access,a,w,v,_):self.write(a,w,v&((1<<(w*8))-1))
        hook=engine.hook_add(UC_HOOK_CODE,code);engine.hook_add(UC_HOOK_MEM_READ,read);engine.hook_add(UC_HOOK_MEM_WRITE,write);engine.emu_start(case['entry'],STOP,count=300000,timeout=3000000)
        state=make_cpu(case);state.registers[:]=[engine.reg_read(r)for r in world.REGS]+[engine.reg_read(UC_M68K_REG_A7)];state.pc=engine.reg_read(UC_M68K_REG_PC);assert state.pc==STOP
        if case['SR']&0x2000:state.ssp=state.registers[15]
        else:state.usp=state.registers[15]
        ram=self.device.ram();trace=list(self.trace);engine.hook_del(hook);engine.mem_write(STOP,b'\x40\xc7');engine.emu_start(STOP,STOP+2,count=1);state.sr=engine.reg_read(UC_M68K_REG_D7)&65535
        return ram,state,{'trace':trace}
    def translated(self,ram,case,missing=None,null_bus=False,null_cpu=False,null_service=False,budget=300000,fail=None,bad_pc=False):
        self.reset(ram,case,1)
        def reader(w):
            def cb(_,a,v):
                if fail==('read',w):return 1
                try:v[0]=self.read(a,w);return 0
                except Exception as error:self.errors.append(repr(error));return 1
            return cb
        def writer(w):
            def cb(_,a,v):
                if fail==('write',w):return 1
                try:self.write(a,w,v);return 0
                except Exception as error:self.errors.append(repr(error));return 1
            return cb
        types=[world.R8,world.R16,world.R32,world.W16,world.W32,memory.W8];callbacks=[types[0](reader(1)),types[1](reader(2)),types[2](reader(4)),types[3](writer(2)),types[4](writer(4)),types[5](writer(1))]
        if missing is not None:callbacks[missing]=types[missing]()
        bus=world.Bus(*callbacks[:5],world.CALL(),None,0)
        def service(_,passed,state,target):
            if fail==('helper',target):return 1
            try:
                if self.actual(target):
                    row={'target':target,'args':self.args(state.contents,target),'actual_body':True,'incoming':prior.cpu_dict(state.contents)};self.calls.append(row);status=self.fn(passed,state,callbacks[5],callback,None,budget,0);row['return']=prior.cpu_dict(state.contents);return status
                self.scripted(state.contents,target);return 0
            except Exception as error:self.errors.append(repr(error));return 1
        callback=prior.oracle.world_cpu.SERVICE()if null_service else prior.oracle.world_cpu.SERVICE(service);state=make_cpu(case)
        if bad_pc:state.pc=0
        before=bytes(state);status=self.call(None if null_bus else c.byref(bus),None if null_cpu else c.byref(state),callbacks[5],callback,None,budget,0)
        return self.device.ram(),state,{'status':status,'calls':self.calls,'trace':list(self.trace),'errors':self.errors,'CPU_unchanged':before==bytes(state),'device':self.device.stats()}

def cases(snapshot):
    groups=[]
    for family,vectors in [('resource',[x for x in resources.cases()if x['entry']in [0x1af04,0x1b002,0x1b044]]),('memory',[x for x in memory.cases()if x['entry']in [0x152a2,0x15200]]),('free',[x for x in cleanup.cases(snapshot)if x['entry']==0x1545c])]:
        for case in vectors:case={**case,'family':family};groups.append(case)
    rng=random.Random(0xe3e0c0de)
    for i in range(256):
        entry=0xe3e0 if i%2 else 0xe3ee;count=[0,1,2,7,127,128,129,255,256,65536,65538][i%11];src=0x80000+i%8;dst=0xc0000+(i//8)%8
        groups.append({'entry':entry,'params':[src,dst,count],'incoming':[rng.getrandbits(32)for _ in range(15)],'initial':[],'payload_pattern':'source[j]=(17*j+3)&255 for j in0..count+7','read_queues':[],'family':'copy','default_helper_return':0,'helper_D0':0})
    result=[]
    for i,case in enumerate(groups):
        widths=[2]if case['entry']in [0x1af04,0x1b002]else[4]*len(case['params']);initial=case['initial']+[[SP,4,STOP]];offset=4
        for width,value in zip(widths,case['params']):initial.append([SP+offset,width,value]);offset+=width
        supervisor=i%2;result.append({**case,'initial':initial,'registers':case['incoming']+[SP],'SR':(0x2000 if supervisor else 0)|((i%8)<<8)|rng.randrange(32),'usp':0x170000 if supervisor else SP,'ssp':SP if supervisor else 0x1d0000})
    return result
def fixture(snapshot,case):
    ram=bytearray(cleanup.Script(snapshot,case).memory)
    if case['family']=='copy':
        src,_,count=case['params'];ram[src:src+count+8]=bytes((17*j+3)&255 for j in range(count+8))
    return bytes(ram)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opt=ap.parse_args();out=ROOT/'verification/biwn-resource-cpu'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libresource-cpu.dylib';names=prior.oracle.NAMES+['biwn_resource_cpu.c'];command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(source/n)for n in names]+['-o',str(library)]
    run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'resource-fullCPU-generation.json').read_text());snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=cases(snapshot)
    if opt.limit:vectors=sum([[x for x in vectors if x['entry']==entry][:opt.limit]for entry in sorted(ENTRIES)],[])
    runtime=Runtime(library,mapping['instructions_decoded']);coverage=set();rows=[]
    try:
        for i,case in enumerate(vectors):
            save(out/'status.json',{'status':'running','case':i,'entry':hex(case['entry'])});ram=fixture(snapshot,case)
            left,expected,old=runtime.native(ram,case,coverage);observed,observer,seen=runtime.unicorn(ram,case,coverage);right,actual,new=runtime.translated(ram,case)
            if new['status']or bytes(expected)!=bytes(actual)or bytes(observer)!=bytes(actual)or left!=right or observed!=right or seen['trace']!=new['trace']or old['calls']!=new['calls']:
                save(out/'mismatch.json',{'case':i,'parameters':case,'CPU_original':prior.cpu_dict(expected),'CPU_Unicorn':prior.cpu_dict(observer),'CPU_C':prior.cpu_dict(actual),'RAM_differences':[hex(j)for j,(a,b)in enumerate(zip(left,right))if a!=b][:100],'Unicorn_RAM_differences':[hex(j)for j,(a,b)in enumerate(zip(observed,right))if a!=b][:100],'original':old,'observer':seen,'rebuilt':new});raise AssertionError(str(out/'mismatch.json'))
            rows.append({'case':i,'parameters':case,'CPU':prior.cpu_dict(actual),'original':old,'rebuilt':new,'allCPU_privateframes_completeRAM_orderedbus_nestedhelper_states_match':True})
        save(out/'fixtures.json',rows)
        if opt.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'cases':len(rows),'directory':str(out)}));return
        missing=[r for r in mapping['instructions_decoded']if r['address']not in coverage];save(out/'decode.json',{'instructions':mapping['instructions_decoded'],'uncovered':missing});assert not missing,[hex(r['address'])for r in missing]
        guards=[];case=vectors[0];ram=fixture(snapshot,case)
        for kwargs in [{'missing':i}for i in range(6)]+[{'null_bus':True},{'null_cpu':True},{'null_service':True},{'budget':0}]:
            _,_,result=runtime.translated(ram,case,**kwargs);assert result['status']==1 and result['CPU_unchanged']and not result['trace'];guards.append(kwargs)
        for kwargs,status in [({'bad_pc':True},7),({'budget':1},4)]:
            _,_,result=runtime.translated(ram,case,**kwargs);assert result['status']==status and result['CPU_unchanged'];guards.append(kwargs)
        for fail in [('read',1),('read',2),('read',4),('write',1),('write',2),('write',4)]:
            row=next(r for r in rows if any(t[0]==('r'if fail[0]=='read'else'w')and t[2]==fail[1]for t in r['rebuilt']['trace']));case=row['parameters'];ram=fixture(snapshot,case);_,_,result=runtime.translated(ram,case,fail=fail);assert result['status']in [2,3]and result['CPU_unchanged'];guards.append({'failure':fail})
        report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'resource_memory_copy_static_fullCPU_dual_oracles_match','directory':str(out),'CPU_cases':len(rows),'CPU_instruction_coverage':[506,506],'host_guards':len(guards),'new_components':0,'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in ['biwn_resource_cpu.c','biwn_resource_cpu.h']},'stage_sha256':mapping['stage_sha256'],'generator_sha256':mapping['generator_sha256'],
                'matched':['NativeCPU and independent Unicorn orderedbus match allregisters/PC/SR/USP/SSP, private save/argument/JSR/RTSframes, complete2MBRAM and nested helper fullstates for sevenresource/heap/copy functions. Supervisor/user paths included.',
                           'Allocator calls actualcompactor and actualCPUcopy, with pinned synchronous emulatedblitter; loader also calls actualcopy. Acquire/release standalone fixtures explicitly script their allocator/free/loader/synchronization boundaries.'],
                'limits':['Synthetic finite heap/cache/streamfixtures and controlled rereads/adapters. Acquire/release logical boundaries scripted here; realweapon resource lifetimes/world linkage remain incomplete. LoaderBIOS/progress/yields/synchronization are scripts, not real loading contextswitches.',
                          'Static C recompilation, no runtime instructiondecode or originalCPU/GPUcalls onCside. Copy huge/negative counts are not claimed as completed; separate older prefix evidence retains its limits. No physicalhardware/fullgame/real-time/concurrency proof.'],'compiler':command}
        save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-resource-cpu-checks.json',report);print(json.dumps(report))
    except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
    finally:runtime.close()
if __name__=='__main__':main()
