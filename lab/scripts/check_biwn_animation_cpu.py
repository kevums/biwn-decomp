"""FullCPU EAC4/EB04 with actual queue, versus native CPU and ordered Unicorn bus."""
import argparse,ctypes as c,hashlib,json,os,random,subprocess
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_animation as prior
import check_biwn_scheduler as scheduler
ROOT=prior.ROOT;CPU=scheduler.CPU;SP=prior.SP;STOP=prior.STOP;save=scheduler.save
def make_cpu(case):
    cpu=CPU();cpu.registers[:]=case['registers'];cpu.pc=case['entry'];cpu.sr=case['SR'];cpu.usp=case['usp'];cpu.ssp=case['ssp'];return cpu
class Native(scheduler.Native):
    def original(self,script,case,coverage):
        self.device.seed(bytes(script.memory),0);self.lib.m68k_pulse_reset();self.lib.m68k_set_irq(0)
        self.lib.m68k_set_reg(17,0x2000);self.lib.m68k_set_reg(15,case['ssp']);self.lib.m68k_set_reg(17,0);self.lib.m68k_set_reg(15,case['usp']);self.lib.m68k_set_reg(17,case['SR'])
        for i,v in enumerate(case['registers']):self.lib.m68k_set_reg(i,v)
        self.lib.m68k_set_reg(16,case['entry']);steps=[]
        for _ in range(200000):
            pc=self.lib.m68k_get_reg(None,16)
            if pc==STOP:break
            assert any(a<=pc<b for a,b in prior.RANGES.items()),hex(pc)
            obj=self.lib.m68k_get_reg(None,10)
            address,width=({0xeac4:(0x112940,2),0xeace:(0x112940,2),0xeaf6:(0x112940,2),0xeb54:(obj+0xca,1),0xebc6:(obj+0xca,1),0xeb70:(obj+0x58,4),0xebde:(obj+0x58,4)}).get(pc,(None,None))
            for q in case.get('read_queues',[]):
                if(q['address'],q['width'])==(address,width):self.device.direct(address,width,script.read(address,width))
            steps.append(pc);coverage.add(pc);self.lib.m68k_execute(1)
        else:raise AssertionError('Original animation did not return')
        cpu=CPU();cpu.registers[:]=[self.lib.m68k_get_reg(None,i)for i in range(16)];cpu.pc=self.lib.m68k_get_reg(None,16);cpu.sr=self.lib.m68k_get_reg(None,17)
        cpu.usp=self.prefix[16]if cpu.sr&0x2000 else cpu.registers[15];cpu.ssp=cpu.registers[15]if cpu.sr&0x2000 else self.prefix[17]
        return self.device.ram(),cpu,steps
def original_bus(script,case,coverage):
    engine=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);engine.ctl_set_cpu_model(UC_CPU_M68K_M68000);engine.mem_map(0,0x200000);engine.mem_write(0,bytes(script.memory))
    for reg,v in zip(prior.world.REGS,case['registers']):engine.reg_write(reg,v)
    engine.reg_write(UC_M68K_REG_SR,case['SR']);engine.reg_write(UC_M68K_REG_A7,SP)
    def code(cpu,pc,size,_):assert any(a<=pc<b for a,b in prior.RANGES.items()),hex(pc);coverage.add(pc)
    def read(cpu,access,a,w,v,_):cpu.mem_write(a,script.read(a,w).to_bytes(w,'big'))
    def write(cpu,access,a,w,v,_):script.write(a,w,v&((1<<(8*w))-1))
    hook=engine.hook_add(UC_HOOK_CODE,code);engine.hook_add(UC_HOOK_MEM_READ,read);engine.hook_add(UC_HOOK_MEM_WRITE,write);engine.emu_start(case['entry'],STOP,count=200000,timeout=2000000)
    assert engine.reg_read(UC_M68K_REG_PC)==STOP and bytes(engine.mem_read(0,0x200000))==script.memory
    engine.hook_del(hook);engine.mem_write(STOP,b'\x40\xc7');engine.emu_start(STOP,STOP+2,count=1);return engine.reg_read(UC_M68K_REG_D7)&65535
def bind(lib,body=False):
    fn=lib.biwn_animation_cpu_body if body else lib.biwn_animation_cpu_call;fn.argtypes=[c.POINTER(prior.world.Bus),c.POINTER(CPU),c.c_uint32];fn.restype=c.c_int;return fn
def translated(fn,script,case,missing=None,null_bus=False,null_cpu=False,budget=512,pc=None):
    def reader(width):
        def cb(_,a,v):
            try:v[0]=script.read(a,width);return 0
            except Exception as error:script.errors.append(repr(error));return 1
        return cb
    def writer(width):
        def cb(_,a,v):
            try:script.write(a,width,v);return 0
            except Exception as error:script.errors.append(repr(error));return 1
        return cb
    types=[prior.world.R8,prior.world.R16,prior.world.R32,prior.world.W16,prior.world.W32];callbacks=[types[0](reader(1)),types[1](reader(2)),types[2](reader(4)),types[3](writer(2)),types[4](writer(4))]
    if missing is not None:callbacks[missing]=types[missing]()
    bus=prior.world.Bus(*callbacks,prior.world.CALL(),None,0);cpu=make_cpu(case)
    if pc is not None:cpu.pc=pc
    status=fn(None if null_bus else c.byref(bus),None if null_cpu else c.byref(cpu),budget);return status,cpu
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opt=ap.parse_args();out=ROOT/'verification/biwn-animation-cpu'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libanimation-cpu.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_animation_cpu.c'),'-o',str(library)]
    run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rng=random.Random(0xeb04c0de);vectors=[]
    for i,case in enumerate(prior.cases()):
        item=dict(case);item['initial']=case['initial']+[[SP,4,STOP]]+[[SP+4+j*4,4,v]for j,v in enumerate(case['params'])];item['registers']=case['incoming']+[SP];item['SR']=(0x2000 if i%2 else 0)|((i%8)<<8)|rng.randrange(32);item['usp']=0x170000 if i%2 else SP;item['ssp']=SP if i%2 else 0x1d0000;vectors.append(item)
    if opt.limit:vectors=[x for x in vectors if x['entry']==0xeb04][:opt.limit]+[x for x in vectors if x['entry']==0xeac4][:opt.limit]
    fn=bind(c.CDLL(str(library)));native=Native();rows=[];coverage=set()
    try:
        for i,case in enumerate(vectors):
            save(out/'status.json',{'status':'running','case':i});a=prior.Script(snapshot,case);b=prior.Script(snapshot,case);u=prior.Script(snapshot,case)
            ram,expected,steps=native.original(a,case,coverage);status,actual=translated(fn,b,case);sr=original_bus(u,case,coverage)
            if status or bytes(actual)!=bytes(expected)or ram!=b.memory or u.memory!=b.memory or u.trace!=b.trace or sr!=actual.sr:
                save(out/'mismatch.json',{'case':i,'parameters':case,'status':status,'CPU_original':scheduler.cpu_dict(expected),'CPU_C':scheduler.cpu_dict(actual),'Unicorn_SR':sr,'trace_original':u.trace,'trace_C':b.trace,'steps':[hex(p)for p in steps],'RAM_differences':[hex(j)for j,(x,y)in enumerate(zip(ram,b.memory))if x!=y][:100]});raise AssertionError(str(out/'mismatch.json'))
            rows.append({'case':i,'parameters':case,'CPU':scheduler.cpu_dict(actual),'trace':b.trace,'original_steps':[hex(p)for p in steps],'fullCPU_privateframes_completeRAM_orderedbus_match':True})
    except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
    finally:native.close()
    save(out/'fixtures.json',rows)
    if opt.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'directory':str(out),'cases':len(rows)}));return
    guards=[]
    for entry in prior.RANGES:
        case=next(x for x in vectors if x['entry']==entry)
        for kwargs in [{'missing':i}for i in([1,2,3,4]if entry==0xeac4 else range(5))]+[{'null_bus':True},{'null_cpu':True},{'pc':0}]+([{'budget':0}]if entry==0xeb04 else[]):
            script=prior.Script(snapshot,case);status,cpu=translated(fn,script,case,**kwargs);initial=make_cpu(case);initial.pc=kwargs.get('pc',entry);assert status==1 and bytes(cpu)==bytes(initial)and not script.trace;guards.append({'entry':hex(entry),**kwargs})
        for kind in ['fail_read','fail_write']:
            row=next(r for r in rows if r['parameters']['entry']==entry and any(t[0]==('r'if kind=='fail_read'else'w')for t in r['trace']));case=row['parameters'];event=next(t for t in row['trace']if t[0]==('r'if kind=='fail_read'else'w'));script=prior.Script(snapshot,case);setattr(script,kind,(event[1],event[2]));status,cpu=translated(fn,script,case);assert status==2 and bytes(cpu)==bytes(make_cpu(case));guards.append({'entry':hex(entry),'bus_failure':kind})
    case=dict(next(x for x in vectors if x['entry']==0xeb04));case['initial']=[[SP,4,STOP],[SP+4,4,prior.OBJECT],[prior.OBJECT+0x68,4,0],[prior.OBJECT+0x64,4,prior.CURRENT],[prior.OBJECT+0x62,2,0],[prior.OBJECT+0xcc,2,0],[0x4c24e,2,0],[prior.CURRENT,1,0],[prior.CURRENT+1,1,0],[prior.CURRENT+3,1,0]];case.pop('read_queues',None)
    script=prior.Script(snapshot,case);status,cpu=translated(fn,script,case,budget=2);assert status==3 and bytes(cpu)==bytes(make_cpu(case));guards.append({'nonprogressing_work_budget':2,'prior_effects_retained':True})
    save(out/'guards.json',guards);decoded=[]
    for a,b in prior.RANGES.items():part,_=prior.world.select.binary_tools.m68k_instructions(snapshot[a:b],a);decoded+=part
    missing=[r for r in decoded if r['address']not in coverage];save(out/'decode.json',{'instructions':decoded,'uncovered':missing});assert not missing
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'animation_update_and_queue_fullCPU_privateframes_match_original','directory':str(out),'CPU_cases':len(rows),'CPU_instruction_coverage':[len(decoded),len(decoded)],'host_guards':len(guards),'new_components':0,
            'entries':['0xeac4','0xeb04'],'actual_queue_body_linked':True,'nested_helper_scripts':0,
            'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in ['biwn_animation_cpu.c','biwn_animation_cpu.h']},
            'matched':['Native originalCPU and reconstructedC compare allregisters/PC/SR/USP/SSP, complete2MBRAM and all private saved-A2/JSR/argument/RTS frames. Independent Unicorn matches ordered data/stack/bus accesses and materialized SR.',
                       'Both complete functions, partial/fullD0, D1/A0/A1 sideeffects, signedqueuecounter/rereads/wrap, signedbyteframe/step/duration, wordtimer catchup, suppression/dirtyretry and realnestedqueue.'],
            'limits':['Bounded fixture scene/record layouts and controlled rereads; no queueconsumer/modeldecode/render or actor/world integration/hardware claim yet.',
                      'Host argument/bus/scan/return errors preserve priorRAM effects and unchangedCPU; boundedcatchup is not originalexception/timing/interrupt behavior.'],
            'core_sha256':scheduler.cleanup.world.select.binary_tools.sha(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'),'compiler':command}
    save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-animation-cpu-checks.json',report);print(json.dumps(report))
if __name__=='__main__':main()
