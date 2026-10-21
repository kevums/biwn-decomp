"""Full startup RNG CPU/private RAM against native CPU and Unicorn.

This is a standalone function test, not removal of the startup capture.
"""
import argparse,ctypes as c,hashlib,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_render_queue_cpu as queue
import generate_biwn_startup_cpu as gen
ROOT=gen.ROOT;CPU=queue.CPU;SP=queue.SP;STOP=queue.STOP;save=queue.save
ENTRIES={0x1a6e0,0x1a6f8,0x1a7f4,0x1a87a,0x1a8c6,0x1a8e2,0x1a8f8}
MATH={0xe540,0xe588,0xe60a,0x1a77c}
CALLER_PROVIDERS={0x4088,0xe03a,0x185b2,0xe2f4,0x18160,0x21242,0x18ba8,0xdfc0}
def sha(data):return hashlib.sha256(data).hexdigest()
class Runtime(queue.Runtime):
    def __init__(self,library,rows):
        super().__init__(library,rows)
        self.fn=self.lib.biwn_startup_cpu_body;self.call=self.lib.biwn_startup_cpu_call
        for fn in [self.fn,self.call]:fn.argtypes=[c.POINTER(queue.world.Bus),c.POINTER(CPU),queue.cd.dispatch.W8,queue.cd.world_cpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];fn.restype=c.c_int
        self.math=self.lib.biwn_startup_rng_math_cpu_body;self.math.argtypes=[c.POINTER(queue.world.Bus),c.POINTER(CPU)];self.math.restype=c.c_int
        self.factory=self.lib.biwn_actor_factory_cpu_body;self.factory.argtypes=self.fn.argtypes;self.factory.restype=c.c_int
    def script_provider(self,state,target):
        seed=(target+self.case['id']*1234567)&0xffffffff
        for r in [0,1,8,9]:state.registers[r]=(seed*(r+1)+0xaabbccdd)&0xffffffff
        state.sr=(state.sr&0xffe0)|(seed&31)
        self.calls.append(dict(target=hex(target),scripted_ABI_provider=True))
    def native(self,ram,case,coverage):
        self.reset(ram,case,0);queue.lifecycle.seed_cpu(self,queue.make_cpu(case));steps=0
        providers=CALLER_PROVIDERS if case.get('startup_caller')else set()
        for target in providers:self.device.direct(target,2,0x4e75)
        try:
            for _ in range(200000):
                pc=self.core.m68k_get_reg(None,16)
                if pc==STOP or(case.get('startup_caller')and pc==0x17dc2):break
                if pc in providers:
                    state=self.cpu();self.script_provider(state,pc)
                    for r in [0,1,8,9]:self.core.m68k_set_reg(r,state.registers[r])
                    self.core.m68k_set_reg(17,state.sr)
                else:assert pc in self.rows,hex(pc);coverage.add(pc);steps+=1
                self.core.m68k_execute(1)
            else:raise AssertionError(('native worklimit',hex(pc)))
        finally:
            for target in providers:self.device.direct(target,2,int.from_bytes(ram[target:target+2],'big'))
        return self.device.ram(),self.cpu(),dict(instructions=steps,providers=list(self.calls))
    def unicorn(self,ram,case,coverage):
        self.reset(ram,case,0);e=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);e.ctl_set_cpu_model(UC_CPU_M68K_M68000);e.mem_map(0,0x200000);e.mem_write(0,ram);e.reg_write(UC_M68K_REG_SR,case['SR'])
        for r,v in zip(queue.cd.REGS,case['registers']):e.reg_write(r,v)
        providers=CALLER_PROVIDERS if case.get('startup_caller')else set()
        for target in providers:e.mem_write(target,b'\x4e\x75')
        def code(cpu,pc,w,_):
            if case.get('startup_caller')and pc==0x17dc2:cpu.emu_stop();return
            if pc in providers:
                state=queue.make_cpu(case);state.registers[:]=[cpu.reg_read(r)for r in queue.cd.REGS];self.script_provider(state,pc)
                for r in [0,1,8,9]:cpu.reg_write(queue.cd.REGS[r],state.registers[r])
                cpu.reg_write(UC_M68K_REG_SR,state.sr)
            else:assert pc in self.rows,hex(pc);coverage.add(pc)
        def reader(cpu,access,a,w,v,_):cpu.mem_write(a,self.read(a,w).to_bytes(w,'big'))
        def writer(cpu,access,a,w,v,_):self.write(a,w,v&((1<<(w*8))-1))
        hooks=[e.hook_add(UC_HOOK_CODE,code),e.hook_add(UC_HOOK_MEM_READ,reader),e.hook_add(UC_HOOK_MEM_WRITE,writer)]
        e.emu_start(case['entry'],STOP,count=200000,timeout=30000000)
        s=queue.make_cpu(case);s.registers[:]=[e.reg_read(r)for r in queue.cd.REGS];s.pc=e.reg_read(UC_M68K_REG_PC);assert s.pc==(0x17dc2 if case.get('startup_caller')else STOP)
        if s.sr&0x2000:s.ssp=s.registers[15]
        else:s.usp=s.registers[15]
        for target in providers:e.mem_write(target,ram[target:target+2])
        output=self.device.ram();assert bytes(e.mem_read(0,0x200000))==output
        trace=list(self.trace)
        for h in hooks:e.hook_del(h)
        e.mem_write(STOP,b'\x40\xc7');e.emu_start(STOP,STOP+2,count=1);s.sr=e.reg_read(UC_M68K_REG_D7)&65535
        return output,s,dict(trace=trace)
    def translated(self,ram,case):
        self.reset(ram,case,1)
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
        callbacks=[queue.world.R8(reader(1)),queue.world.R16(reader(2)),queue.world.R32(reader(4)),queue.world.W16(writer(2)),queue.world.W32(writer(4)),queue.cd.dispatch.W8(writer(1))]
        bus=queue.world.Bus(*callbacks[:5],queue.world.CALL(),None,0)
        def service(_,passed,state,target):
            try:
                if target in MATH:return self.math(passed,state)
                if target==0xdf6c:return self.factory(passed,state,callbacks[5],callback,None,200000,0)
                if case.get('startup_caller')and target in CALLER_PROVIDERS:self.script_provider(state.contents,target);return 0
                assert target in ENTRIES,hex(target)
                return self.fn(passed,state,callbacks[5],callback,None,200000,0)
            except Exception as error:self.errors.append(repr(error));return 1
        callback=queue.cd.world_cpu.SERVICE(service);state=queue.make_cpu(case)
        status=self.call(c.byref(bus),c.byref(state),callbacks[5],callback,None,200000,0)
        return self.device.ram(),state,dict(status=status,trace=list(self.trace),errors=self.errors,device=self.stats())
def cases(snapshot,count):
    rng=random.Random(0x1a6e0c);result=[];edge=[0,1,2,0x7fffffff,0x80000000,0xffffffff,44488,93674]
    for entry in sorted(ENTRIES):
        for i in range(count):
            index=len(result);supervisor=index%2;regs=[rng.getrandbits(32)for _ in range(15)]+[SP];params=[]
            if entry==0x1a87a:params=[(2,[0,1,254,255,256,65535][i%6])]
            elif entry in [0x1a8c6,0x1a8f8]:params=[(4,edge[i%8])]
            ram=bytearray(snapshot)
            initial=[(SP,4,STOP),(0x462e0,4,44488),(0x462e4,4,3399),(0x462e8,4,44488),(0x462ec,4,3399),(0x462f0,4,93674),(0x462f4,4,7197),(0x113080,2,[0,1,254,255][i%4]),(0x113082,4,edge[i%8])]
            off=4
            for w,v in params:initial.append((SP+off,w,v));off+=w
            for a,w,v in initial:ram[a:a+w]=v.to_bytes(w,'big')
            case=dict(id=index,entry=entry,registers=regs,SR=(0x2000 if supervisor else 0)|((i%8)<<8)|rng.randrange(32),usp=0x170000 if supervisor else SP,ssp=SP if supervisor else 0x1d0000,read_queues=[],params=params,initial=initial)
            result.append((bytes(ram),case))
    return result
def caller_cases(snapshot,count):
    rng=random.Random(0x17c40c);result=[];contexts=[0xc0d28,0xc0928];free=[0xc1128+i*0x400 for i in range(19)]
    for i in range(count):
        supervisor=i%2;ram=bytearray(snapshot);initial=[(0xc0920,4,contexts[0]),(0xc0924,4,free[0]),(SP,4,STOP)]
        for j,obj in enumerate(contexts):initial.extend([(obj,4,contexts[1-j]),(obj+4,4,contexts[1-j]),(obj+8,4,0x17c40 if j==0 else 0xddcc)])
        initial.extend((obj,4,free[j+1]if j+1<len(free)else 0)for j,obj in enumerate(free))
        for a,w,v in initial:ram[a:a+w]=v.to_bytes(w,'big')
        case=dict(id=i,entry=0x17c40,startup_caller=True,registers=[rng.getrandbits(32)for _ in range(15)]+[SP],SR=(0x2000 if supervisor else 0)|((i%8)<<8)|rng.randrange(32),usp=0x170000 if supervisor else SP,ssp=SP if supervisor else 0x1d0000,read_queues=[],initial=initial,free_contexts=free)
        result.append((bytes(ram),case))
    return result
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--per-entry',type=int,default=8);ap.add_argument('--caller',action='store_true');opt=ap.parse_args();assert opt.per_entry>0
    category='BIWN-startup-caller-fullCPU'if opt.caller else 'BIWN-startup-RNG-fullCPU'
    out=ROOT/'verification'/category/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_startup_cpu.c','biwn_startup_rng_math_cpu.c','biwn_signed_division.c','biwn_camera.c','biwn_actor_factory_cpu.c','biwn_render_queue_cpu.c'];library=out/'libstartup-rng-cpu.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(source/n)for n in names]+['-o',str(library)]
    run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert not run.returncode,run.stderr
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'startup-fullCPU-generation.json').read_text());rows=mapping['instructions_decoded']
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();mathrows=gen.loader.base.binary_tools.m68k_instructions(snapshot[0xe540:0xe61c],0xe540)[0]+gen.loader.base.binary_tools.m68k_instructions(snapshot[0x1a77c:0x1a7f4],0x1a77c)[0]
    factoryrows=json.loads((session/'actor-factory-fullCPU-generation.json').read_text())['instructions_decoded']
    runtime=Runtime(library,rows+mathrows+factoryrows);results=[];coverage=set()
    try:
        vectors=caller_cases(snapshot,opt.per_entry)if opt.caller else cases(snapshot,opt.per_entry)
        for ram,case in vectors:
            save(out/'status.json',dict(status='running',case=case['id'],entry=hex(case['entry'])))
            left,expected,native=runtime.native(ram,case,coverage);observed,observer,independent=runtime.unicorn(ram,case,coverage);right,actual,rebuilt=runtime.translated(ram,case)
            if rebuilt['status']!=(8 if opt.caller else 0) or bytes(expected)!=bytes(actual) or bytes(observer)!=bytes(actual) or left!=right or observed!=right or independent['trace']!=rebuilt['trace']:
                (out/'native-RAM.bin').write_bytes(left);(out/'C-RAM.bin').write_bytes(right)
                save(out/'mismatch.json',dict(case=case,native_CPU=queue.cd.scheduler.cpu_dict(expected),Unicorn_CPU=queue.cd.scheduler.cpu_dict(observer),C_CPU=queue.cd.scheduler.cpu_dict(actual),native=native,Unicorn=independent,C=rebuilt,RAM_differences=[hex(j)for j,(a,b)in enumerate(zip(left,right))if a!=b][:80]));raise AssertionError(str(out/'mismatch.json'))
            assert not rebuilt['device']['GPUExec1_calls']and not rebuilt['device']['game_frames_executed']
            row=dict(case=case,CPU=queue.cd.scheduler.cpu_dict(actual),RAM_sha256=sha(right),native_instructions=native['instructions'],ordered_bus_operations=len(rebuilt['trace']),ordered_bus_sha256=sha(json.dumps(rebuilt['trace'],separators=(',',':')).encode()),full_CPU_RAM_private_frames_and_ordered_bus_match=True)
            if opt.caller:
                entries=[0x21d1a,0x1a544,0x17520,0x12ee0,0x155e0,0x14cc0,0x179c0,0x17380,0x17640,0x1a560,0x1a920,0xefa0,0xec20,0x1b480,0xf880,0xf360]
                get=lambda a,w=4:int.from_bytes(right[a:a+w],'big')
                assert get(0xc0924)==case['free_contexts'][16]
                for obj,entry in zip(case['free_contexts'],entries):assert get(obj+8)==get(obj+16)==entry and get(obj+30)==0 and get(get(obj)+4)==obj and get(get(obj+4))==obj
                row['actual_source_task_creations']=16;row['scripted_helper_providers']=sorted(map(hex,CALLER_PROVIDERS))
            results.append(row)
        selected=[r for r in rows if 0x1a6e0<=r['address']<0x1a91e];covered=[r for r in selected if r['address']in coverage]
        report=dict(status='standalone_startup_RNG_native_Unicorn_C_match',directory=str(out),recorded_at=datetime.now(timezone.utc).isoformat(),cases=len(results),source_RNG_instruction_coverage=[len(covered),len(selected)],native_CPU_instructions=sum(r['native_instructions']for r in results),full_2MB_RAM_compared_without_masks=True,all_CPU_registers_SR_USP_SSP_compared=True,ordered_bus_compared_to_independent_Unicorn=True,original_CPU_or_GPU_execution_on_C_path=False,startup_snapshot_removed=False,startup_caller_integrated=False,whole_game_complete=False,new_published_components=0,source_sha256={n:sha((source/n).read_bytes())for n in names},generator_sha256=mapping['generator_sha256'],test_script_sha256=sha(Path(__file__).read_bytes()),compiler=command,limits=['Standalone source RNG initialization/fill/get/set/select calls with supplied source RAM, parameters and stack banks. No interrupts, physical timing, arbitrary invalid stack aliases or zero-divisor exception emulation.','411 generated startup instructions are not all verified by this RNG test. Render startup, scene loading, missing helper bodies and actual scheduler connection remain pending. Existing connected loading/movie/world proof still begins with the older startup capture.'])
        if opt.caller:
            callerrows=[r for r in rows if 0x17c40<=r['address']<0x17dc2]
            report.update(status='standalone_startup_caller_native_Unicorn_C_match',source_caller_instruction_coverage=[sum(r['address']in coverage for r in callerrows),len(callerrows)],actual_source_task_creations=16*len(results),scripted_helper_providers=sorted(map(hex,CALLER_PROVIDERS)),limits=['Standalone17C40caller through17DC2, actual RNG initialization and sixteen source DF6C/DE5C task creations. All source caller instructions, both stack banks and private RAM compare. Eight other helpers are explicit register/CCR-clobbering ABI scripts; they do not perform display creation, framebuffer clear, scene loading, other task creation or device setup.','Supplied two-context ring and nineteen free records. Not source DD40 startup, real task scheduling, full resource startup, live renderer or removal of the existing startup capture.'])
        report['source_sha256'].update({n.replace('.c','.h'):sha((source/n.replace('.c','.h')).read_bytes())for n in names})
        pointer='startup-caller-fullCPU-checks.json'if opt.caller else 'startup-RNG-fullCPU-checks.json'
        save(out/'cases.json',results);save(out/'coverage.json',dict(covered=sorted(coverage),uncovered=[r for r in selected if r['address']not in coverage]));save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification'/pointer,report);print(json.dumps({k:v for k,v in report.items()if k not in ['compiler','source_sha256']}))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:runtime.close()
if __name__=='__main__':main()
