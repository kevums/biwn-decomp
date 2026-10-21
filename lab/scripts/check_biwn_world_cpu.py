"""Full1A188 CPU/private-frame caller versus native CPU and Unicorn ordered bus."""
import argparse,ctypes as c,hashlib,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_world_update as prior
import check_biwn_scheduler as scheduler
import emulated_pad_input as pad
ROOT=prior.ROOT;CPU=scheduler.CPU;SP=prior.SP;STOP=prior.STOP
TARGETS=[0xe4c0,0x191f4,0x1b786,0xe220,0x19f2c,0x19fda,0xf0fa,0xeb04,0x20820]
save=scheduler.save
SERVICE=c.CFUNCTYPE(c.c_int,c.c_void_p,c.POINTER(prior.Bus),c.POINTER(CPU),c.c_uint32)
def arguments(memory,cpu,target):
    if target==0xf0fa:return [cpu.registers[2]&65535,cpu.registers[3]&65535]
    widths={0xe220:[4]*5,0x19f2c:[2]*3,0x19fda:[4,2],0xeb04:[4]}.get(target,[])
    offset=4;args=[]
    for width in widths:args.append(int.from_bytes(memory[cpu.registers[15]+offset:cpu.registers[15]+offset+width],'big'));offset+=width
    return args
class Script(prior.Script):
    def __init__(self,snapshot,case):
        super().__init__(snapshot,case);self.services=[];self.index=0;self.input_read_index=0
    def read(self,a,w):
        if getattr(self,'real_poll',False)and a==0xf14000:
            assert w==4;value=self.pad.read_for_C();self.trace.append(['r',a,w,value]);return value
        if a==0x49bac and w==4 and 'input_reads'in self.case:
            values=self.case['input_reads'];self.put(a,w,values[min(self.input_read_index,len(values)-1)]);self.input_read_index+=1
        return super().read(a,w)
    def write(self,a,w,v):
        if getattr(self,'real_poll',False)and a==0xf14000:
            if self.fail_write:raise RuntimeError('injected write failure')
            assert w==2;self.pad.write_for_C(v);self.trace.append(['w',a,w,v]);return
        return super().write(a,w,v)
    def enable_poll(self,device,core,poll_fn):
        self.real_poll=True;self.poll_fn=poll_fn;self.pad=pad.Backend(core,device);self.pad.start(self.case)
    def begin_poll(self):
        self.pad.begin_poll();self.put(0x778cc,4,(self.case['clock']+self.pad.polls-1)&0xffffffff)
    def service(self,state,target,record=True,bus=None):
        if record:self.services.append({'target':target,'CPU':scheduler.cpu_dict(state)})
        if getattr(self,'real_poll',False)and target==0xe4c0:
            self.trace.append(['call',target,[]]);self.begin_poll();assert self.poll_fn(bus,c.byref(state))==0;return
        args=arguments(self.memory,state,target);self.changed=[];result=self.call(target,args)
        rng=random.Random(self.case['clobber_seed']+self.index*98765+target);self.index+=1
        state.registers[0]=result
        for reg in [1,8,9]:state.registers[reg]=rng.getrandbits(32)
        state.sr=(self.case['SR']&0xffe0)|rng.randrange(32)

def cpu_for(case):
    cpu=CPU();cpu.registers[:]=case['registers'];cpu.pc=0x1a188;cpu.sr=case['SR'];cpu.usp=case['usp'];cpu.ssp=case['ssp'];return cpu

class Native(scheduler.Native):
    def state(self):
        cpu=CPU();cpu.registers[:]=[self.lib.m68k_get_reg(None,i)for i in range(16)];cpu.pc=self.lib.m68k_get_reg(None,16);cpu.sr=self.lib.m68k_get_reg(None,17)
        cpu.usp=self.prefix[16]if cpu.sr&0x2000 else cpu.registers[15];cpu.ssp=cpu.registers[15]if cpu.sr&0x2000 else self.prefix[17];return cpu
    def original(self,script,case,coverage):
        self.device.seed(bytes(script.memory),0)
        real_poll=getattr(self,'real_poll',False)
        if real_poll:self.pad=pad.Backend(self.lib,self.device);self.pad.start(case)
        for target in TARGETS:
            if not(real_poll and target==0xe4c0):self.device.direct(target,2,0x4e75)
        self.lib.m68k_pulse_reset();self.lib.m68k_set_irq(0)
        self.lib.m68k_set_reg(17,0x2000);self.lib.m68k_set_reg(15,case['ssp']);self.lib.m68k_set_reg(17,0);self.lib.m68k_set_reg(15,case['usp']);self.lib.m68k_set_reg(17,case['SR'])
        for i,v in enumerate(case['registers']):self.lib.m68k_set_reg(i,v)
        self.lib.m68k_set_reg(16,0x1a188);steps=[]
        for _ in range(10000):
            pc=self.lib.m68k_get_reg(None,16)
            if pc==STOP:break
            if pc==0xe4c0 and real_poll:
                script.services.append({'target':pc,'CPU':scheduler.cpu_dict(self.state())});self.pad.begin_poll();coverage.add(pc)
            elif pc in TARGETS:
                state=self.state();script.memory[:]=self.device.ram();script.service(state,pc)
                for a,w,v in script.changed:self.device.direct(a,w,v)
                for reg in [0,1,8,9]:self.lib.m68k_set_reg(reg,state.registers[reg])
                self.lib.m68k_set_reg(17,state.sr)
            else:
                assert 0x1a188<=pc<0x1a544 or 0x1b718<=pc<0x1b780 or(real_poll and 0xe4c0<=pc<0xe53c),hex(pc)
                if pc in [0x1a340,0x1a3d6]and'mode_reads'in case:
                    value=script.read(0x49c60,2);self.device.direct(0x49c60,2,value)
                if pc in [0x1a1f6,0x1a224]and'input_reads'in case:
                    value=script.read(0x49bac,4);self.device.direct(0x49bac,4,value)
                coverage.add(pc)
            steps.append(pc);self.lib.m68k_execute(1)
        else:raise AssertionError('Native world caller did not return')
        for target in TARGETS:self.device.direct(target,2,int.from_bytes(script.case['source'][target:target+2],'big'))
        return self.device.ram(),self.state(),steps

def unicorn_original(script,case,coverage):
    real_poll=getattr(script,'real_poll',False)
    engine=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);engine.ctl_set_cpu_model(UC_CPU_M68K_M68000);engine.mem_map(0,0x200000);engine.mem_write(0,bytes(script.memory))
    if real_poll:engine.mem_map(0xf14000,0x1000)
    for reg,v in zip(prior.select.REGS,case['registers']):engine.reg_write(reg,v)
    engine.reg_write(UC_M68K_REG_SR,case['SR']);engine.reg_write(UC_M68K_REG_A7,SP)
    for target in TARGETS:
        if not(real_poll and target==0xe4c0):engine.mem_write(target,b'\x4e\x75')
    def code(cpu,pc,size,_):
        if pc==0xe4c0 and real_poll:
            script.trace.append(['call',pc,[]]);script.begin_poll();coverage.add(pc)
        elif pc in TARGETS:
            state=CPU();state.registers[:]=[cpu.reg_read(r)for r in prior.select.REGS]+[cpu.reg_read(UC_M68K_REG_A7)];state.pc=pc;state.sr=case['SR']
            # Do not read UnicornSR here: that can commit stale deferred flags.
            # Native CPU separately checks complete incoming helper SR/state.
            script.service(state,pc,record=False)
            for a,w,v in script.changed:cpu.mem_write(a,v.to_bytes(w,'big'))
            for i in [0,1,8,9]:cpu.reg_write(prior.select.REGS[i],state.registers[i])
            cpu.reg_write(UC_M68K_REG_SR,state.sr)
        else:
            assert 0x1a188<=pc<0x1a544 or 0x1b718<=pc<0x1b780 or(real_poll and 0xe4c0<=pc<0xe53c),hex(pc);coverage.add(pc)
    def read(cpu,access,a,w,v,_):cpu.mem_write(a,script.read(a,w).to_bytes(w,'big'))
    def write(cpu,access,a,w,v,_):script.write(a,w,v&((1<<(8*w))-1))
    hook=engine.hook_add(UC_HOOK_CODE,code);engine.hook_add(UC_HOOK_MEM_READ,read);engine.hook_add(UC_HOOK_MEM_WRITE,write)
    engine.emu_start(0x1a188,STOP,count=10000,timeout=1000000);assert engine.reg_read(UC_M68K_REG_PC)==STOP
    actual=bytearray(engine.mem_read(0,0x200000))
    for target in TARGETS:actual[target:target+2]=case['source'][target:target+2]
    assert actual==script.memory
    engine.hook_del(hook);engine.mem_write(STOP,b'\x40\xc7');engine.emu_start(STOP,STOP+2,count=1)
    return engine.reg_read(UC_M68K_REG_D7)&65535

def bind(lib):
    fn=lib.biwn_world_cpu_call;fn.argtypes=[c.POINTER(prior.Bus),c.POINTER(CPU),SERVICE,c.c_void_p,c.c_uint32];fn.restype=c.c_int;return fn
def translated(fn,script,case,missing=None,null_bus=False,null_cpu=False,null_service=False,pc=0x1a188,budget=64,bad_return=False):
    errors=[]
    def reader(width):
        def callback(_,a,v):
            try:v[0]=script.read(a,width);return 0
            except Exception as error:errors.append(repr(error));return 1
        return callback
    def writer(width):
        def callback(_,a,v):
            try:script.write(a,width,v);return 0
            except Exception as error:errors.append(repr(error));return 1
        return callback
    def service(_,bus,state,target):
        try:
            script.service(state.contents,target,bus=bus)
            if bad_return:state.contents.registers[15]+=4
            return 0
        except Exception as error:errors.append(repr(error));return 1
    kinds=[prior.R8,prior.R16,prior.R32,prior.W16,prior.W32];callbacks=[prior.R8(reader(1)),prior.R16(reader(2)),prior.R32(reader(4)),prior.W16(writer(2)),prior.W32(writer(4))]
    if missing is not None:callbacks[missing]=kinds[missing]()
    bus=prior.Bus(*callbacks,prior.CALL(),None,0);cb=SERVICE(service);cpu=cpu_for(case);cpu.pc=pc
    status=fn(None if null_bus else c.byref(bus),None if null_cpu else c.byref(cpu),SERVICE()if null_service else cb,None,budget)
    return status,cpu,errors

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);options=ap.parse_args();out=ROOT/'verification/biwn-world-cpu'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libworld-cpu.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_world_cpu.c'),'-o',str(library)]
    result=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=[];rng=random.Random(0x1a188f00d)
    for i,case in enumerate(prior.cases()):
        item=dict(case);item['initial']=case['initial']+[[SP,4,STOP]];item['registers']=[rng.getrandbits(32)for _ in range(15)]+[SP];item['SR']=(0x2000 if i%2 else 0)|((i%8)<<8)|rng.randrange(32);item['usp']=0x170000 if i%2 else SP;item['ssp']=SP if i%2 else 0x1d0000;item['clobber_seed']=rng.getrandbits(32);item['source']=snapshot;vectors.append(item)
    for bit in [19,18,17,7,6,5,4,3,2,1]:
        item=dict(vectors[1]);item['poll_inputs']=[1<<bit];vectors.append(item)
    item=dict(vectors[1]);item['poll_inputs']=[0x10];item['input_reads']=[0x10,0];vectors.append(item)
    if options.limit:vectors=vectors[:options.limit]
    functions=bind(c.CDLL(str(library)));rows=[];coverage=set();native=Native()
    try:
        for i,case in enumerate(vectors):
            save(out/'status.json',{'status':'running','case':i});a=Script(snapshot,case);b=Script(snapshot,case);u=Script(snapshot,case)
            ram,expected,steps=native.original(a,case,coverage);status,actual,errors=translated(functions,b,case);sr=unicorn_original(u,case,coverage)
            if status or bytes(expected)!=bytes(actual)or ram!=b.memory or u.memory!=b.memory or u.trace!=b.trace or a.services!=b.services or sr!=actual.sr:
                parameters={k:v for k,v in case.items()if k!='source'}
                save(out/'mismatch.json',{'case':i,'parameters':parameters,'status':status,'errors':errors,'CPU_original':scheduler.cpu_dict(expected),'CPU_C':scheduler.cpu_dict(actual),'Unicorn_SR':sr,'steps':[hex(a)for a in steps],'services_original':a.services,'services_C':b.services,'trace_original':u.trace,'trace_C':b.trace,'RAM_differences':[hex(j)for j,(x,y)in enumerate(zip(ram,b.memory))if x!=y][:100]});raise AssertionError(str(out/'mismatch.json'))
            rows.append({'case':i,'parameters':{k:v for k,v in case.items()if k!='source'},'CPU':scheduler.cpu_dict(actual),'services':b.services,'trace':b.trace,'steps':[hex(a)for a in steps],'full_CPU_private_RAM_ordered_bus_match':True})
    except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
    finally:native.close()
    save(out/'fixtures.json',rows)
    if options.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'directory':str(out),'cases':len(rows)}));return
    guards=[];case=vectors[1]
    for kwargs in [{'missing':i}for i in range(5)]+[{'null_bus':True},{'null_cpu':True},{'null_service':True},{'pc':0},{'budget':0}]:
        script=Script(snapshot,case);status,cpu,errors=translated(functions,script,case,**kwargs);expected=cpu_for(case);expected.pc=kwargs.get('pc',0x1a188);assert status==1 and bytes(cpu)==bytes(expected)and not script.trace;guards.append(kwargs)
    for kind in ['fail_read','fail_write']:
        script=Script(snapshot,case);setattr(script,kind,True);status,cpu,_=translated(functions,script,case);assert status==2 and bytes(cpu)==bytes(cpu_for(case));guards.append({'failure':kind,'status':status})
    for target in TARGETS:
        row=next(r for r in rows if any(s['target']==target for s in r['services']));case=vectors[row['case']];script=Script(snapshot,case);script.fail_call=target;status,cpu,_=translated(functions,script,case);assert status==3 and bytes(cpu)==bytes(cpu_for(case));guards.append({'service_failure':hex(target)})
    case=dict(vectors[1]);case['poll_inputs']=[0x10000000,0];script=Script(snapshot,case);status,cpu,_=translated(functions,script,case,budget=3);assert status==4 and script.polls==3 and bytes(cpu)==bytes(cpu_for(case));guards.append({'pause_poll_limit':3})
    script=Script(snapshot,vectors[1]);status,cpu,_=translated(functions,script,vectors[1],bad_return=True);assert status==5 and bytes(cpu)==bytes(cpu_for(vectors[1]));guards.append({'bad_helper_return':True})
    save(out/'guards.json',guards);decoded=[]
    for a,b in [(0x1a188,0x1a544),(0x1b718,0x1b780)]:part,_=prior.select.binary_tools.m68k_instructions(snapshot[a:b],a);decoded+=part
    missing=[r for r in decoded if r['address']not in coverage];save(out/'decode.json',{'instructions':decoded,'uncovered':missing});assert not missing
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'world_caller_full_CPU_private_frames_and_flags_match_original','directory':str(out),'CPU_cases':len(rows),'CPU_instruction_coverage':[len(decoded),len(decoded)],'world_caller_instructions':239,'digit_helper_instructions':len(decoded)-239,'host_guards':len(guards),'new_components':0,
            'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in ['biwn_world_cpu.c','biwn_world_cpu.h']},'helper_targets_scripted':[hex(a)for a in TARGETS],'helper_incoming_full_CPU_flags_compared':True,
            'matched':['Original native CPU and C compare all16registers/PC/SR/USP/SSP and complete2MBRAM including caller local/save/JSR/argument frames. Original Unicorn independently matches ordered data/stack/bus accesses and materialized final SR.',
                       'Complete1A188caller and original1B718digit helper, pause loops, raw32bit clock difference/signed upper30clamp, word/long positions/fractions, all boundary directions, lowword failures/selective rollback/camera sign/change, volatile helper effects and full incoming helper state.'],
            'limits':['Nine helper bodies are explicit synthetic scripts in this caller-interface proof. Their actual bodies, hardware input, real GPU and world/actor task integration are separate work.',
                      'Bounded SRAM/private-stack fixtures and SRbits0x271f, no external interrupts/tracing/cycle timing/arbitrary code-stack aliases. Host argument/bus/service/poll/return failures retain RAM effects and unchanged callerCPU; not original exceptions.'],
            'core_sha256':scheduler.cleanup.world.select.binary_tools.sha(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'),'compiler':command}
    save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-world-cpu-checks.json',report);print(json.dumps(report))

if __name__=='__main__':main()
