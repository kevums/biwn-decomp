"""FullCPU E0F2/E148 plus real E098 wait, native/Unicorn/C; declared mailbox inputs."""
import ctypes as c,hashlib,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_render_queue_cpu as queue
ROOT=queue.ROOT;CPU=queue.CPU;save=queue.save;read=queue.read;SP=queue.SP;STOP=queue.STOP
queue.ENTRIES={0xe098};queue.RETURNS={0xe0a4};queue.SCRIPTS=set()
class Runtime(queue.Runtime):
    def __init__(self,library,rows):
        super().__init__(library,rows);self.wait_fn=self.fn;self.project_fn=self.lib.biwn_gpu_interior_submit_cpu_body;self.call=self.lib.biwn_gpu_interior_submit_cpu_call
        for fn in [self.project_fn,self.call]:fn.argtypes=self.wait_fn.argtypes;fn.restype=c.c_int
        def body(bus,state,*args):return(self.wait_fn if state is not None and c.cast(state,c.POINTER(CPU)).contents.pc==0xe098 else self.project_fn)(bus,state,*args)
        self.fn=body
    def write(self,a,w,v):
        if a==0xf03204:
            assert w==4;self.trace.append(['w',a,w,v]);self.core.GPUWriteLong(a,v,0);return
        return super().write(a,w,v)
    def native(self,ram,case,coverage):
        self.reset(ram,case,0);queue.lifecycle.seed_cpu(self,queue.make_cpu(case));steps=[];stack=[];pending=None
        for _ in range(10000):
            pc=self.core.m68k_get_reg(None,16)
            if pc==STOP or(case['body']and pc==case['outer_RTS']):break
            assert pc in self.rows,hex(pc)
            if pending==pc:
                row=dict(target=pc,actual_body=True,incoming=queue.cd.scheduler.cpu_dict(self.cpu()));self.calls.append(row);stack.append(row);pending=None
            if pc==0xe0a4 and stack:stack.pop()['return']=queue.cd.scheduler.cpu_dict(self.cpu())
            if pc in [0xe0f2,0xe140,0xe148,0xe196]:pending=0xe098
            if pc==0xe098:self.inject(0xf03200,4)
            if pc in [0xe134,0xe18a]:self.inject(0xf03204,4)
            coverage.add(pc);steps.append(pc);self.core.m68k_execute(1)
        else:raise AssertionError('Interior submission CPU did not stop')
        assert not stack
        return self.device.ram(),self.cpu(),dict(steps=steps,calls=self.calls,device=self.stats())
def cases():
    rng=random.Random(0xe0f224);result=[]
    for entry,header,outer in [(0xe0f2,0x6ae0,0xe146),(0xe148,0x6da0,0xe19c)]:
        for number in range(128):
            supervisor=number%2;registers=[rng.getrandbits(32)for _ in range(15)]+[SP]
            result.append(dict(id=len(result),entry=entry,header=header,registers=registers,SR=(0x2000 if supervisor else 0)|((number%8)<<8)|rng.randrange(32),usp=0x170000 if supervisor else SP,ssp=SP if supervisor else 0x1d0000,body=number%3==1,render=False,outer_RTS=outer,scene_pointer=rng.getrandbits(32),sector=[0,1,40,70,0x7fffffff,0x80000000,0xffffffff,rng.getrandbits(32)][number%8],read_queues=[dict(address=0xf03200,width=4,values=[1]*(number%4)+[0,1,0]),dict(address=0xf03204,width=4,values=[header]*(number%3)+[0xffffffff])]))
    return result
def fixture(snapshot,case):
    memory=bytearray(snapshot);memory[SP:SP+4]=STOP.to_bytes(4,'big');memory[0x49c18:0x49c1c]=case['scene_pointer'].to_bytes(4,'big');memory[0x49c1c:0x49c20]=case['sector'].to_bytes(4,'big');return bytes(memory)
def main():
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'gpu-interior-submit-fullCPU-generation.json');snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();wait_rows,_=queue.cd.gen.base.binary_tools.m68k_instructions(snapshot[0xe098:0xe0a6],0xe098);all_rows=mapping['instructions_decoded']+wait_rows
    out=ROOT/'verification/biwn-gpu-interior-submit-cpu'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libinterior-submit-cpu.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_gpu_interior_submit_cpu.c'),str(source/'biwn_render_queue_cpu.c'),'-o',str(library)];compiler=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(compiler.stdout+compiler.stderr);assert compiler.returncode==0,compiler.stderr
    runtime=Runtime(library,all_rows);rows=[];coverage=set()
    try:
        for case in cases():
            save(out/'status.json',dict(status='running',case=case['id']));ram=fixture(snapshot,case);left,expected,native=runtime.native(ram,case,coverage);observed,observer,independent=runtime.unicorn(ram,case,coverage);right,actual,rebuilt=runtime.translated(ram,case)
            if rebuilt['status']or bytes(expected)!=bytes(actual)or bytes(observer)!=bytes(actual)or left!=right or observed!=right or independent['trace']!=rebuilt['trace']or native['calls']!=rebuilt['calls']:
                save(out/'mismatch.json',dict(case=case,CPU_native=queue.cd.scheduler.cpu_dict(expected),CPU_Unicorn=queue.cd.scheduler.cpu_dict(observer),CPU_C=queue.cd.scheduler.cpu_dict(actual),native=native,Unicorn=independent,rebuilt=rebuilt,RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(left,right))if a!=b][:40]));raise AssertionError(str(out/'mismatch.json'))
            rows.append(dict(case=case,CPU=queue.cd.scheduler.cpu_dict(actual),original=native,rebuilt=rebuilt,fullCPU_mainRAM_privateframes_bus_helpers_match=True))
        missing=sorted({row['address']for row in all_rows}-coverage);assert not missing,list(map(hex,missing));guards=[];case=cases()[0];ram=fixture(snapshot,case)
        for options in [{'missing':i}for i in range(6)]+[dict(null_bus=True),dict(null_cpu=True),dict(null_service=True),dict(budget=0),dict(stop_flag=2)]:
            _,_,result=runtime.translated(ram,case,**options);assert result['status']==1 and result['CPU_unchanged']and not result['trace'];guards.append(options)
        for options,statuses in [(dict(bad_pc=True),[7]),(dict(budget=1),[3]),(dict(fail=('read',4)),[2,3]),(dict(fail=('write',4)),[2]),(dict(fail=('helper',0xe098)),[3])]:
            _,_,result=runtime.translated(ram,case,**options);assert result['status']in statuses and result['CPU_unchanged'],(options,statuses,result);guards.append(options)
        interior={**case,'entry':0xe0f8};_,_,result=runtime.translated(ram,interior,budget=1);assert result['status']==4 and result['CPU_unchanged'];guards.append(dict(interior_outer_budget=1))
        corrupt={**case,'read_queues':case['read_queues']+[dict(address=SP-4,width=4,values=[0])]};_,_,result=runtime.translated(ram,corrupt);assert result['status']==5 and result['CPU_unchanged'];guards.append(dict(corrupt_private_return=True))
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='E0F2_E148_submission_real_E098_native_Unicorn_C_fullCPU_RAM_bus_match',directory=str(out),CPU_cases=len(rows),source_instruction_coverage=[len(mapping['instructions_decoded']),22],wait_instruction_coverage=[len(wait_rows),len(wait_rows)],host_guards=len(guards),source_sha256=mapping['source_sha256'],generator_sha256=mapping['generator_sha256'],render_queue_C_sha256=hashlib.sha256((source/'biwn_render_queue_cpu.c').read_bytes()).hexdigest(),compiler=command,live_renderer_linked=False,original_GPU_instructions_executed=False,new_published_components=0,matched=['NativeCPU and independentUnicorn match fullD/A,SR,USP/SSP,whole2MBRAM,privateJSR/RTSframes,orderedCPUbus and both actualE098wait incoming/return states. Bothstackbanks,body/fullcall and supplied busy/ack transitions.'],limits=['StandaloneCPU protocol proof. GPU6AE0/6DA0execution is separately checked, not called here; mailbox busy/ack transitions are declared device inputs, not asyncdispatcher/hardwaretiming.','No fullrenderer link/draw/viewport/audio/boot/fullgame proof. Hosterror semantics leaveinputCPUunchanged and preservepriorRAMstores.'])
        save(out/'fixtures.json',rows);save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/biwn-gpu-interior-submit-cpu-checks.json',report);print(json.dumps(report))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:runtime.close()
if __name__=='__main__':main()
