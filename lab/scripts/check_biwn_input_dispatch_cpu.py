"""All816dispatcher instructions/fullCPU versus native and ordered Unicorn.

The19helper bodies are explicit scripted boundaries in this standalone proof.
Their full incoming/return states and source-created private frames compare.
"""
import argparse,ctypes as c,hashlib,json,os,random,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_input_dispatch as prior
import check_biwn_camera_cpu as oracle
import generate_biwn_input_dispatch_cpu as generator
ROOT=prior.ROOT;CPU=oracle.CPU;SP=prior.SP;STOP=prior.STOP;save=oracle.save
def cpu_dict(cpu):return oracle.live.prior.scheduler.cpu_dict(cpu)
class Runtime(oracle.Runtime):
    def __init__(self,library,rows):
        super().__init__(library);self.rows={r['address']:r for r in rows};self.instruction_limit=200000;self.callbacks=[]
        self.fn=self.lib.biwn_input_dispatch_cpu_call;self.fn.argtypes=[c.POINTER(oracle.live.world.Bus),c.POINTER(CPU),prior.W8,oracle.world_cpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];self.fn.restype=c.c_int
        self.body=self.lib.biwn_input_dispatch_cpu_body;self.body.argtypes=self.fn.argtypes;self.body.restype=c.c_int
    def reset(self,ram,case,mode):
        super().reset(ram,case,mode);self.script=prior.Script(ram,case);self.calls=[];self.script_count=0
    def scripted(self,state,target):
        sp=state.registers[15];offset=4;args=[]
        for width in prior.WIDTHS.get(target,[]):args.append(int.from_bytes(c.string_at(self.device.pointer+sp+offset,width),'big'));offset+=width
        incoming=cpu_dict(state);self.script.changed=[];result=self.script.call(target,args)
        for a,w,v in self.script.changed:self.device.direct(a,w,v)
        self.script_count+=1;seed=(target+self.script_count*1234567)&0xffffffff;state.registers[0]=result
        for r in [1,8,9]:state.registers[r]=(seed*r+0xaabbccdd)&0xffffffff
        state.sr=(state.sr&0xffe0)|(seed&31);self.calls.append({'target':target,'args':args,'incoming':incoming,'return':cpu_dict(state)})
    def ea(self,text,registers):
        if re.fullmatch(r'\$[0-9a-f]+\.[wl]',text):return generator.number(text[:-2])
        m=re.fullmatch(r'(\$[0-9a-f]+)?\((a[0-7]|pc)(?:, ([da][0-7])\.([wl]))?\)',text)
        if not m:return None
        prefix,base,index,width=m.groups();value=generator.number(prefix)if base=='pc'else registers[generator.register(base)]+(generator.number(prefix)if prefix else 0)
        if index:
            v=registers[generator.register(index)]
            if width=='w':v=v&65535;v=v if v<32768 else v-65536
            value+=v
        return value&0xffffffff
    def apply_native_queues(self,pc):
        if not any(self.queues.values()):return
        row=self.rows[pc];op,_,tail=row['assembly'].partition(' ');base=op.split('.')[0];parts=generator.split(tail);width={'b':1,'w':2,'l':4}.get(op[-1],4)
        reads=parts[:1]if base in ['move','movea','tst']else parts[1:2]if base in ['cmpi','btst']else parts if base in ['add','addq','addi','sub','andi']else[]
        registers=[self.core.m68k_get_reg(None,i)for i in range(16)]
        for text in reads:
            a=self.ea(text,registers);queue=self.queues.get((a,width))
            if queue:self.device.direct(a,width,queue.pop(0))
    def native(self,ram,case,coverage):
        self.reset(ram,case,0);oracle.lifecycle.seed_cpu(self,oracle.make_cpu(case));steps=[]
        for target in prior.HELPERS:self.device.direct(target,2,0x4e75)
        try:
            for _ in range(self.instruction_limit):
                pc=self.core.m68k_get_reg(None,16)
                if pc==STOP:break
                if pc in prior.HELPERS:
                    state=self.cpu();self.scripted(state,pc)
                    for reg in [0,1,8,9]:self.core.m68k_set_reg(reg,state.registers[reg])
                    self.core.m68k_set_reg(17,state.sr)
                else:assert pc in self.rows,hex(pc);self.apply_native_queues(pc);steps.append(pc);coverage.add(pc)
                self.core.m68k_execute(1)
            else:raise AssertionError('Native dispatcher did not return')
        finally:
            for target in prior.HELPERS:self.device.direct(target,2,int.from_bytes(ram[target:target+2],'big'))
        return self.device.ram(),self.cpu(),{'steps':steps,'calls':self.calls}
    def unicorn(self,ram,case,coverage):
        self.reset(ram,case,0);engine=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);engine.ctl_set_cpu_model(UC_CPU_M68K_M68000);engine.mem_map(0,0x200000);engine.mem_write(0,ram)
        for target in prior.HELPERS:engine.mem_write(target,b'\x4e\x75')
        for reg,v in zip(oracle.live.world.REGS,case['registers']):engine.reg_write(reg,v)
        engine.reg_write(UC_M68K_REG_SR,case['SR']);engine.reg_write(UC_M68K_REG_A7,SP)
        def code(cpu,pc,w,_):
            if pc in prior.HELPERS:
                state=oracle.make_cpu(case);state.registers[:]=[cpu.reg_read(r)for r in oracle.live.world.REGS]+[cpu.reg_read(UC_M68K_REG_A7)];state.usp=state.registers[15];state.pc=pc
                # Do not read Unicorn's deferred SR before a materialization
                # instruction. Script replaces allCCRbits; upperSRis invariant.
                state.sr=case['SR'];self.scripted(state,pc)
                for reg in [0,1,8,9]:cpu.reg_write(oracle.live.world.REGS[reg],state.registers[reg])
                cpu.reg_write(UC_M68K_REG_SR,state.sr)
                for a,width,value in self.script.changed:cpu.mem_write(a,value.to_bytes(width,'big'))
            else:assert pc in self.rows,hex(pc);coverage.add(pc)
        def read(cpu,access,a,w,v,_):cpu.mem_write(a,self.read(a,w).to_bytes(w,'big'))
        def write(cpu,access,a,w,v,_):self.write(a,w,v&((1<<(w*8))-1))
        hook=engine.hook_add(UC_HOOK_CODE,code);engine.hook_add(UC_HOOK_MEM_READ,read);engine.hook_add(UC_HOOK_MEM_WRITE,write);engine.emu_start(0x191f4,STOP,count=self.instruction_limit,timeout=3000000)
        state=oracle.make_cpu(case);state.registers[:]=[engine.reg_read(r)for r in oracle.live.world.REGS]+[engine.reg_read(UC_M68K_REG_A7)];state.pc=engine.reg_read(UC_M68K_REG_PC);state.usp=state.registers[15];assert state.pc==STOP
        output=self.device.ram();trace=list(self.trace);engine.hook_del(hook);engine.mem_write(STOP,b'\x40\xc7');engine.emu_start(STOP,STOP+2,count=1);state.sr=engine.reg_read(UC_M68K_REG_D7)&65535
        return output,state,{'trace':trace}
    def translated(self,ram,case,missing=None,null_bus=False,null_cpu=False,null_service=False,budget=200000,fail=None,bad_pc=False,supervisor=False,stop_on_yield=0):
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
        types=[oracle.live.world.R8,oracle.live.world.R16,oracle.live.world.R32,oracle.live.world.W16,oracle.live.world.W32,prior.W8];callbacks=[types[0](reader(1)),types[1](reader(2)),types[2](reader(4)),types[3](writer(2)),types[4](writer(4)),types[5](writer(1))]
        if missing is not None:callbacks[missing]=types[missing]()
        bus=oracle.live.world.Bus(*callbacks[:5],oracle.live.world.CALL(),None,0)
        def service(_,bus,state,target):
            if fail==('helper',target):return 1
            try:self.scripted(state.contents,target);return 0
            except Exception as error:self.errors.append(repr(error));return 1
        callback=oracle.world_cpu.SERVICE()if null_service else oracle.world_cpu.SERVICE(service);state=oracle.make_cpu(case)
        if bad_pc:state.pc=0
        if supervisor:state.sr|=0x2000
        before=bytes(state);status=self.fn(None if null_bus else c.byref(bus),None if null_cpu else c.byref(state),callbacks[5],callback,None,budget,stop_on_yield)
        return self.device.ram(),state,{'status':status,'trace':self.trace,'calls':self.calls,'errors':self.errors,'CPU_unchanged':bytes(state)==before}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opt=ap.parse_args();out=ROOT/'verification/biwn-input-dispatch-cpu'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libinput-dispatch-cpu.dylib';names=oracle.NAMES+['biwn_input_dispatch_cpu.c'];command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(source/n)for n in names]+['-o',str(library)]
    run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'input-dispatch-fullCPU-workmap.json').read_text());snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rng=random.Random(0x191f4c0de)
    vectors=[{**case,'entry':0x191f4,'initial':case['initial']+[[SP,4,STOP]],'registers':case['incoming']+[SP],'SR':rng.randrange(32)|((i%8)<<8)}for i,case in enumerate(prior.cases(snapshot))]
    if opt.limit:vectors=sum([[x for x in vectors if x['state']==state][:opt.limit]for state in range(13)],[])+vectors[-4:]
    runtime=Runtime(library,mapping['instructions']);rows=[];coverage=set()
    try:
        for i,case in enumerate(vectors):
            save(out/'status.json',{'status':'running','case':i});ram=bytes(prior.Script(snapshot,case).memory)
            left,expected,old=runtime.native(ram,case,coverage);observed,observer,seen=runtime.unicorn(ram,case,coverage);right,actual,new=runtime.translated(ram,case)
            if new['status']or bytes(expected)!=bytes(actual)or bytes(observer)!=bytes(actual)or left!=right or observed!=right or seen['trace']!=new['trace']or old['calls']!=new['calls']:
                save(out/'mismatch.json',{'case':i,'parameters':case,'CPU_original':cpu_dict(expected),'CPU_Unicorn':cpu_dict(observer),'CPU_C':cpu_dict(actual),'RAM_differences':[hex(j)for j,(a,b)in enumerate(zip(left,right))if a!=b][:100],'Unicorn_RAM_differences':[hex(j)for j,(a,b)in enumerate(zip(observed,right))if a!=b][:100],'original':old,'observer':seen,'rebuilt':new});raise AssertionError(str(out/'mismatch.json'))
            rows.append({'case':i,'parameters':case,'CPU':cpu_dict(actual),'original':old,'rebuilt':new,'allCPU_completeRAM_privateframes_orderedbus_helperincoming_and_return_match':True})
        save(out/'fixtures.json',rows)
        if opt.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'cases':len(rows),'directory':str(out)}));return
        missing=[r for r in mapping['instructions']if r['address']not in coverage];save(out/'decode.json',{'instructions':mapping['instructions'],'uncovered':missing});assert not missing
        guards=[];case=vectors[0];ram=bytes(prior.Script(snapshot,case).memory)
        for kwargs in [{'missing':i}for i in range(6)]+[{'null_bus':True},{'null_cpu':True},{'null_service':True},{'supervisor':True},{'budget':0}]:
            _,_,result=runtime.translated(ram,case,**kwargs);assert result['status']==1 and result['CPU_unchanged']and not result['trace'];guards.append(kwargs)
        for kwargs,expected_status in [({'bad_pc':True},7),({'budget':1},4)]:
            _,_,result=runtime.translated(ram,case,**kwargs);assert result['status']==expected_status and result['CPU_unchanged'];guards.append(kwargs)
        for fail in [('read',1),('read',2),('read',4),('write',1),('write',2),('write',4)]+[('helper',a)for a in prior.HELPERS]:
            row=next(r for r in rows if (fail[0]=='helper'and any(x['target']==fail[1]for x in r['original']['calls']))or(fail[0]in ['read','write']and any(t[0]==('r'if fail[0]=='read'else'w')and t[2]==fail[1]for t in r['rebuilt']['trace'])))
            case=row['parameters'];ram=bytes(prior.Script(snapshot,case).memory);_,_,result=runtime.translated(ram,case,fail=fail);assert result['status']in [2,3]and result['CPU_unchanged'];guards.append({'failure':fail})
        report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'static_dispatcher_fullCPU_privateframes_scripted_helpers_match_original','directory':str(out),'CPU_cases':len(rows),'CPU_instruction_coverage':[816,816],'host_guards':len(guards),'new_components':0,'configured_helper_scripts':[hex(a)for a in prior.HELPERS],
                'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in ['biwn_input_dispatch_cpu.c','biwn_input_dispatch_cpu.h']},'generator_sha256':hashlib.sha256((ROOT/'scripts/generate_biwn_input_dispatch_cpu.py').read_bytes()).hexdigest(),'stage_sha256':mapping['stage_sha256'],
                'matched':['All816sourceinstructions/13states compare against nativeCPU and Unicorn orderedbus: fullCPU/SR/USP/SSP, whole2MBRAM/privateframes, complete helperincoming/return states.',
                           'Source-specific static C blocks, no runtime instructiondecode/originalCPUcalls. Existing readable logicalC remains. Equipment/idle/motion/turn/reread paths, scriptedhelpercallerclobbers and source-owned argument/JSR/return frames.'],
                'limits':['All19nestedhelpers are explicit scripts in this standalone proof; no actual scheduling at the twoDF60calls. Suspensioninterface, worldintegration, real nested bodies and fullgame remain unverified.',
                          'Usermode only, finite fixtures/controlledeffects/rereads. Hosterrors leaveCPUunchanged with priorRAM effects. Static recompilation is not recovered originalsource or a whole-game decompile.'], 'compiler':command}
        save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-input-dispatch-cpu-checks.json',report);print(json.dumps(report))
    except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
    finally:runtime.close()
if __name__=='__main__':main()
