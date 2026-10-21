"""Camera full CPU/private frames with actual math and GPU, against two CPU oracles."""
import argparse,ctypes as c,hashlib,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_camera as prior
import check_biwn_actor_full_movement_runtime as live
import check_biwn_actor_lifecycle_runtime as lifecycle
import check_biwn_world_cpu as world_cpu
ROOT=prior.ROOT;CPU=live.CPU;SP=prior.SP;STOP=prior.STOP;save=live.save
RANGES=[(0xf0fa,0xf35e),(0xe540,0xe60a),(0x13440,0x134dc)]+live.motion.submit_cpu.RANGES
NAMES=['biwn_camera_cpu.c','biwn_rng_cpu.c','biwn_signed_division.c','biwn_camera.c','biwn_actor_direction.c','biwn_movement_submit_cpu.c']

def make_cpu(case):
    state=CPU();state.registers[:]=case['registers'];state.pc=case.get('entry',0xf0fa);state.sr=case['SR'];state.usp=SP;state.ssp=0x1d0000;return state

class Runtime:
    def __init__(self,library):
        self.device=live.Device();self.core=c.CDLL(str(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'));self.lib=c.CDLL(str(library))
        self.core.m68k_set_reg.argtypes=[c.c_int,c.c_uint32];self.core.m68k_get_reg.argtypes=[c.c_void_p,c.c_int];self.core.m68k_get_reg.restype=c.c_uint32
        self.core.m68k_execute.argtypes=[c.c_int];self.core.m68k_execute.restype=c.c_int;self.core.m68k_set_irq.argtypes=[c.c_uint32]
        self.core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];self.core.GPUReadLong.restype=c.c_uint32;self.prefix=(c.c_uint32*18).in_dll(self.core,'regs')
        self.rng=live.rng_cpu.bind(self.lib);self.direction=live.motion.direction.bind(self.lib);self.submit=live.motion.submit_cpu.bind(self.lib)
        self.fn=self.lib.biwn_camera_cpu_call;self.fn.argtypes=[c.POINTER(live.world.Bus),c.POINTER(CPU),live.actor.W8,world_cpu.SERVICE,c.c_void_p];self.fn.restype=c.c_int
        self.ranges=RANGES;self.instruction_limit=10000
        self.native_rereads={0xf25c:(0x3c842,4),0xf270:(0x3c842,4),0xf2c2:(0x49cba,1),0xf2ea:(0x49cba,1),0xf31c:(0x49cba,1)}
    def cpu(self):
        state=CPU();state.registers[:]=[self.core.m68k_get_reg(None,i)for i in range(16)];state.pc=self.core.m68k_get_reg(None,16);state.sr=self.core.m68k_get_reg(None,17);state.usp=state.registers[15];state.ssp=self.prefix[17];return state
    def reset(self,ram,case,mode):
        self.device.seed(ram,mode);self.queues={(q['address'],q['width']):list(q['values'])for q in case.get('read_queues',[])};self.trace=[];self.errors=[]
    def read(self,a,w):
        queue=self.queues.get((a,w))
        if queue:self.device.direct(a,w,queue.pop(0))
        v=self.device.read(a,w);self.trace.append(['r',a,w,v]);return v
    def write(self,a,w,v):
        self.trace.append(['w',a,w,v])
        if w==1:self.device.direct(a,w,v)
        elif w==2:self.device.write16(a,v)
        else:self.device.write(a,v)
    def native(self,ram,case,coverage):
        self.reset(ram,case,0);lifecycle.seed_cpu(self,make_cpu(case));steps=[]
        rereads=self.native_rereads
        for _ in range(self.instruction_limit):
            pc=self.core.m68k_get_reg(None,16)
            if pc==STOP:break
            assert any(a<=pc<b for a,b in self.ranges),hex(pc)
            if pc in rereads:
                a,w=rereads[pc];queue=self.queues.get((a,w))
                if queue:self.device.direct(a,w,queue.pop(0))
            steps.append(pc);coverage.add(pc);self.core.m68k_execute(1)
            if self.core.GPUReadLong(0xf03204,0)==0x4320:self.device.write(0xf03204,0x4320)
        else:raise AssertionError('Native camera did not return')
        return self.device.ram(),self.cpu(),{'steps':steps,'device':self.device.stats()}
    def unicorn(self,ram,case,coverage):
        self.reset(ram,case,0);engine=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);engine.ctl_set_cpu_model(UC_CPU_M68K_M68000);engine.mem_map(0,0x200000);engine.mem_map(0xf02000,0x2000);engine.mem_write(0,ram)
        for reg,value in zip(live.world.REGS,case['registers']):engine.reg_write(reg,value)
        engine.reg_write(UC_M68K_REG_SR,case['SR']);engine.reg_write(UC_M68K_REG_A7,SP)
        def code(cpu,a,w,_):assert any(lo<=a<hi for lo,hi in self.ranges),hex(a);coverage.add(a)
        def read(cpu,access,a,w,v,_):cpu.mem_write(a,self.read(a,w).to_bytes(w,'big'))
        def write(cpu,access,a,w,v,_):self.write(a,w,v&((1<<(w*8))-1))
        hook=engine.hook_add(UC_HOOK_CODE,code);engine.hook_add(UC_HOOK_MEM_READ,read);engine.hook_add(UC_HOOK_MEM_WRITE,write);engine.emu_start(case.get('entry',0xf0fa),STOP,count=self.instruction_limit,timeout=2000000)
        state=make_cpu(case);state.registers[:]=[engine.reg_read(r)for r in live.world.REGS]+[engine.reg_read(UC_M68K_REG_A7)];state.pc=engine.reg_read(UC_M68K_REG_PC);state.usp=state.registers[15];assert state.pc==STOP
        output=self.device.ram();trace=list(self.trace);stats=self.device.stats()
        # Materialize SR after taking snapshots. Direct SR reads can mutate deferred flags.
        engine.hook_del(hook);engine.mem_write(STOP,b'\x40\xc7');engine.emu_start(STOP,STOP+2,count=1);state.sr=engine.reg_read(UC_M68K_REG_D7)&65535
        return output,state,{'trace':trace,'device':stats}
    def translated(self,ram,case,missing=None,null_bus=False,null_cpu=False,null_service=False,fail=None,bad_pc=False,supervisor=False):
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
        types=[live.world.R8,live.world.R16,live.world.R32,live.world.W16,live.world.W32,live.actor.W8]
        callbacks=[types[0](reader(1)),types[1](reader(2)),types[2](reader(4)),types[3](writer(2)),types[4](writer(4)),types[5](writer(1))]
        if missing is not None:callbacks[missing]=types[missing]()
        bus=live.world.Bus(*callbacks[:5],live.world.CALL(),None,0)
        def service(_,bus,state,target):
            if fail==('helper',target):return 1
            try:
                if target in [0xe540,0xe588]:return self.rng(bus,state)
                if target==0x13440:return self.direction(bus,state)
                assert target==0xe220;return self.submit(bus,state,1000)
            except Exception as error:self.errors.append(repr(error));return 1
        callback=world_cpu.SERVICE()if null_service else world_cpu.SERVICE(service);state=make_cpu(case)
        if bad_pc:state.pc=0
        if supervisor:state.sr|=0x2000
        before=bytes(state);status=self.fn(None if null_bus else c.byref(bus),None if null_cpu else c.byref(state),callbacks[5],callback,None)
        return self.device.ram(),state,{'status':status,'trace':list(self.trace),'errors':self.errors,'device':self.device.stats(),'CPU_unchanged':before==bytes(state)}
    def close(self):self.device.close()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opt=ap.parse_args();out=ROOT/'verification/biwn-camera-cpu'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libcamera-cpu.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(source/n)for n in NAMES]+['-o',str(library)]
    run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rng=random.Random(0xf0fac0de);vectors=[]
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();assert prior.world.select.stage.digest(image)==prior.world.select.stage.STAGE_SHA
    for a,b in RANGES:assert snapshot[a:b]==image[a-0x4000:b-0x4000]
    for i,case in enumerate(x for x in prior.cases()if x['entry']==0xf0fa):
        case={**case,'initial':case['initial']+[[SP,4,STOP]],'registers':case['incoming']+[SP],'SR':rng.randrange(32)|((i%8)<<8)}
        # Old tests scripted mailbox-helper effects. Here all helpers execute real bodies.
        case.pop('helper_effects',None);vectors.append(case)
    if opt.limit:vectors=vectors[:opt.limit]+vectors[256:256+opt.limit]
    runtime=Runtime(library);rows=[];coverage=set()
    try:
        for i,case in enumerate(vectors):
            save(out/'status.json',{'status':'running','case':i});ram=bytes(prior.Script(snapshot,case).memory)
            left,expected,old=runtime.native(ram,case,coverage);observed,observer,observed_info=runtime.unicorn(ram,case,coverage);right,actual,new=runtime.translated(ram,case)
            if new['status']or bytes(expected)!=bytes(actual)or bytes(observer)!=bytes(actual)or left!=right or observed!=right or observed_info['trace']!=new['trace']:
                save(out/'mismatch.json',{'case':i,'parameters':case,'CPU_original':live.prior.scheduler.cpu_dict(expected),'CPU_Unicorn':live.prior.scheduler.cpu_dict(observer),'CPU_C':live.prior.scheduler.cpu_dict(actual),'RAM_differences':[hex(j)for j,(x,y)in enumerate(zip(left,right))if x!=y][:100],'Unicorn_RAM_differences':[hex(j)for j,(x,y)in enumerate(zip(observed,right))if x!=y][:100],'original':old,'observer':observed_info,'rebuilt':new});raise AssertionError(str(out/'mismatch.json'))
            assert old['device']['original_GPUExec1_calls']>0 and not new['device']['original_GPUExec1_calls']and not new['device']['game_frames_executed']
            rows.append({'case':i,'parameters':case,'CPU':live.prior.scheduler.cpu_dict(actual),'original':old,'rebuilt':new,'allCPU_privateframes_completeRAM_orderedbus_match':True})
        save(out/'fixtures.json',rows)
        if opt.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'directory':str(out),'cases':len(rows)}));return
        decoded,_=prior.world.select.binary_tools.m68k_instructions(snapshot[0xf0fa:0xf35e],0xf0fa);missing=[r for r in decoded if r['address']not in coverage];save(out/'decode.json',{'instructions':decoded,'uncovered':missing});assert not missing
        guards=[];case=vectors[0];ram=bytes(prior.Script(snapshot,case).memory)
        for kwargs in [{'missing':i}for i in range(6)]+[{'null_bus':True},{'null_cpu':True},{'null_service':True},{'bad_pc':True},{'supervisor':True}]:
            _,_,result=runtime.translated(ram,case,**kwargs);assert result['status']==1 and result['CPU_unchanged']and not result['trace'];guards.append(kwargs)
        for fail in [('read',1),('read',2),('read',4),('write',2),('write',4),('helper',0x13440),('helper',0xe220)]:
            _,_,result=runtime.translated(ram,case,fail=fail);assert result['status']in [2,3]and result['CPU_unchanged'];guards.append({'failure':fail,'status':result['status']})
        case=vectors[256];ram=bytes(prior.Script(snapshot,case).memory);_,_,result=runtime.translated(ram,case,fail=('helper',0xe540));assert result['status']==3 and result['CPU_unchanged'];guards.append({'failure':['helper',0xe540]})
        report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'camera_fullCPU_privateframes_actual_math_and_GPU_match_original','directory':str(out),'CPU_cases':len(rows),'CPU_instruction_coverage':[len(decoded),len(decoded)],'host_guards':len(guards),'new_components':0,'helper_scripts':[],
                'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in NAMES+[n.replace('.c','.h')for n in NAMES]},
                'matched':['Native original CPU/GPU and independent Unicorn observer match reconstructed CPU/math/GPU: allregisters/PC/SR/USP/SSP, complete2MBRAM/privateframes and ordered data/stack/device accesses.',
                           'Debug controls/wrap and incoming D2/D3, signed counters, both angle averaging branches, changing rereads and normal multiply/direction pipeline. Four live direction-argument bytes are reused in20byteGPUsubmitframe.'],
                'limits':['Usermode only; external fixtures/rereads and synchronousGPUcompletion model. Host errors retain priorRAM effects and unchanged inputCPU; no original exceptions/timing/interrupts.',
                          'Standalone camera proof; world integration and fullrender/scanout/mainloop/audio/game/hardware remain unfinished. Already counted F0FA gains interface; no new component.'],
                'compiler':command}
        save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-camera-cpu-checks.json',report);print(json.dumps(report))
    except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
    finally:runtime.close()

if __name__=='__main__':main()
