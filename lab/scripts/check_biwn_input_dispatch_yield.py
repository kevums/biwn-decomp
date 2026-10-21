"""Actual scheduler handoffs at both dispatcher yield sites; helper fixtures explicit."""
import argparse,ctypes as c,hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_input_dispatch_cpu as prior
ROOT=prior.ROOT;CPU=prior.CPU;SP=prior.SP;STOP=prior.STOP;save=prior.save
MAIN=0xc2128;IDLES=[0xc5928,0xc5528];CONTEXTS=[MAIN]+IDLES
class Runtime(prior.Runtime):
    def __init__(self,library,rows):
        super().__init__(library,rows);self.yield_fn=self.lib.biwn_scheduler_yield;self.yield_fn.argtypes=[c.POINTER(prior.oracle.live.world.Bus),c.POINTER(CPU),c.c_uint32];self.yield_fn.restype=c.c_int
        self.idle=self.lib.biwn_task_loop_step;self.idle.argtypes=[c.POINTER(prior.oracle.live.world.Bus),c.POINTER(CPU),prior.oracle.live.prior.BODY,c.c_void_p,c.c_uint32];self.idle.restype=c.c_int
    def current(self):return int.from_bytes(c.string_at(self.device.pointer+0xc0920,4),'big')
    def event(self,state):return {'context':self.current(),'CPU':prior.cpu_dict(state)}
    def native(self,ram,case):
        self.reset(ram,case,0);prior.oracle.lifecycle.seed_cpu(self,prior.oracle.make_cpu(case));steps=[];handoffs=[];yields=[]
        helpers=[a for a in prior.prior.HELPERS if a!=0xdf60]
        for target in helpers:self.device.direct(target,2,0x4e75)
        try:
            for _ in range(300000):
                pc=self.core.m68k_get_reg(None,16)
                if pc==STOP:break
                if pc in helpers:
                    state=self.cpu();self.scripted(state,pc)
                    for reg in [0,1,8,9]:self.core.m68k_set_reg(reg,state.registers[reg])
                    self.core.m68k_set_reg(17,state.sr)
                else:
                    assert pc in self.rows or any(a<=pc<b for a,b in [(0xdf60,0xdf6c),(0xde08,0xde5c),(0xf360,0xf368),(0xf880,0xf888)]),hex(pc)
                    if pc in self.rows:self.apply_native_queues(pc)
                    steps.append(pc)
                if pc==0xdf60:yields.append(self.event(self.cpu()))
                self.core.m68k_execute(1)
                if pc==0xdf6a or(pc==0xde5a and self.core.m68k_get_reg(None,16)!=0xdf66):handoffs.append(self.event(self.cpu()))
            else:raise AssertionError('Native dispatcher-yield ring did not return')
        finally:
            for target in helpers:self.device.direct(target,2,int.from_bytes(ram[target:target+2],'big'))
        return self.device.ram(),self.cpu(),{'steps':steps,'calls':self.calls,'handoffs':handoffs,'yields':yields}
    def translated(self,ram,case):
        self.reset(ram,case,1);state=prior.oracle.make_cpu(case);handoffs=[];yields=[]
        def reader(w):
            def cb(_,a,v):
                try:v[0]=self.read(a,w);return 0
                except Exception as error:self.errors.append(repr(error));return 1
            return cb
        def writer(w):
            def cb(_,a,v):
                try:self.write(a,w,v);return 0
                except Exception as error:self.errors.append(repr(error));return 1
            return cb
        world=prior.oracle.live.world;callbacks=[world.R8(reader(1)),world.R16(reader(2)),world.R32(reader(4)),world.W16(writer(2)),world.W32(writer(4)),prior.prior.W8(writer(1))];bus=world.Bus(*callbacks[:5],world.CALL(),None,0)
        def service(_,bus,cpu,target):
            try:assert target!=0xdf60;self.scripted(cpu.contents,target);return 0
            except Exception as error:self.errors.append(repr(error));return 1
        callback=prior.oracle.world_cpu.SERVICE(service)
        for _ in range(10000):
            context=self.current()
            if context==MAIN:
                status=self.fn(c.byref(bus),c.byref(state),callbacks[5],callback,None,200000,1)
                if status==0:assert state.pc==STOP;break
                assert status==6 and state.pc==0xdf60,(status,hex(state.pc),self.errors)
                yields.append(self.event(state));assert self.yield_fn(c.byref(bus),c.byref(state),64)==0;handoffs.append(self.event(state))
            else:
                assert context in IDLES;yielding=state.pc in [0xf360,0xf880]
                if yielding:
                    fake=CPU.from_buffer_copy(bytes(state));fake.registers[15]-=4;fake.usp=fake.registers[15];fake.pc=0xdf60
                    # The source JSR return write changes no flags/registers.
                    yields.append({'context':context,'CPU':prior.cpu_dict(fake)})
                assert self.idle(c.byref(bus),c.byref(state),prior.oracle.live.prior.BODY(),None,64)==0
                if yielding:handoffs.append(self.event(state))
        else:raise AssertionError('C dispatcher-yield ring did not return')
        assert not self.errors
        return self.device.ram(),state,{'calls':self.calls,'handoffs':handoffs,'yields':yields}
def fixture(snapshot,case):
    ram=bytearray(prior.prior.Script(snapshot,case).memory)
    def put(a,w,v):ram[a:a+w]=(v&((1<<(8*w))-1)).to_bytes(w,'big')
    put(0xc0920,4,MAIN);put(0x80,4,0xde08);put(0x778cc,4,0)
    for i,(ctx,entry,stack)in enumerate(zip(CONTEXTS,[0x191f4,0xf360,0xf880],[SP,IDLES[0]+0x400,IDLES[1]+0x400])):
        for off,w,v in [(0,4,CONTEXTS[(i+1)%3]),(4,4,CONTEXTS[(i-1)%3]),(8,4,entry),(12,4,stack),(16,4,entry),(20,2,0),(22,4,0),(26,4,0),(30,4,0),(34,4,0)]:put(ctx+off,w,v)
    return bytes(ram)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opt=ap.parse_args();out=ROOT/'verification/biwn-input-dispatch-yield'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    proof=json.loads((ROOT/'verification/biwn-input-dispatch-cpu-checks.json').read_text());saved=json.loads((Path(proof['directory'])/'fixtures.json').read_text());session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'input-dispatch-fullCPU-workmap.json').read_text());sites=[r['address']for r in mapping['yield_instructions']]
    chosen=[]
    for site in sites:
        chosen += [r['parameters']for r in saved if site in r['original']['steps']and not r['parameters'].get('read_queues')][:opt.limit or 16]
    source=ROOT/'projects/black-ice-white-noise/restoration';names=prior.oracle.NAMES+['biwn_input_dispatch_cpu.c','biwn_scheduler.c','biwn_task_loops.c'];library=out/'libinput-yield.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(source/n)for n in names]+['-o',str(library)]
    run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
    runtime=Runtime(library,mapping['instructions']);snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rows=[]
    try:
        for i,case in enumerate(chosen):
            save(out/'status.json',{'status':'running','case':i});ram=fixture(snapshot,case);left,expected,old=runtime.native(ram,case);right,actual,new=runtime.translated(ram,case)
            if left!=right or bytes(expected)!=bytes(actual)or any(old[k]!=new[k]for k in ['calls','handoffs','yields']):
                save(out/'mismatch.json',{'case':i,'parameters':case,'CPU_original':prior.cpu_dict(expected),'CPU_C':prior.cpu_dict(actual),'RAM_differences':[hex(j)for j,(a,b)in enumerate(zip(left,right))if a!=b][:100],'original':old,'rebuilt':new});raise AssertionError(str(out/'mismatch.json'))
            assert len(new['handoffs'])>=3 and len(new['handoffs'])%3==0
            rows.append({'case':i,'parameters':case,'CPU':prior.cpu_dict(actual),'original':old,'rebuilt':new,'allCPU_completeRAM_privateframes_liveyield_handoffs_match':True})
        save(out/'fixtures.json',rows)
        if opt.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'cases':len(rows),'directory':str(out)}));return
        assert len(rows)==len(chosen)==25 and all(any(site in r['original']['steps']for r in rows)for site in sites)
        report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'dispatcher_two_yield_sites_with_actual_scheduler_and_idles_match_original','directory':str(out),'cases':len(rows),'yield_sites':[hex(a)for a in sites],'task_handoffs':sum(len(r['rebuilt']['handoffs'])for r in rows),'dispatcher_inner_yields':sum(sum(y['context']==MAIN for y in r['rebuilt']['yields'])for r in rows),'new_components':0,'configured_helper_scripts':[hex(a)for a in prior.prior.HELPERS if a!=0xdf60],
                'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in ['biwn_input_dispatch_cpu.c','biwn_input_dispatch_cpu.h','biwn_scheduler.c','biwn_scheduler.h','biwn_task_loops.c','biwn_task_loops.h']},
                'matched':['Both sourceDF60calls suspend dispatcher with full private save/argument/JSRframes; actual original/C scheduler runs twoactualidles then restores internaldispatchercontinuation. FullCPU/SR/USP/SSP/whole2MBRAM/calls/yields/allhandoffstates match.',
                           'All816instructions have separate1890case dualCPU/orderedbus proof. This25case proof adds real suspension/task switching instead of scripted yield returns.'],
                'limits':['Synthetic three-context dispatcher/idle ring; not the disc-scene world caller stack. Eighteen other helper bodies remain scripted, including mutable animation/poll/resource effects. No actual animationconsumer, loading switch, crosshair/render/fullgame/hardware completion.',
                          'Host instruction/scan budgets, usermode entry, no external interrupts/timing/concurrency. Static C recompilation preserves low-level CPU continuation; readable logicalC retained.'], 'compiler':command}
        save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-input-dispatch-yield-checks.json',report);print(json.dumps(report))
    except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
    finally:runtime.close()
if __name__=='__main__':main()
