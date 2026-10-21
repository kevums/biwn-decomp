"""Two real acquisition callers: loader yield, readiness wait, source wake and sharing."""
import argparse,ctypes as c,hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_disc_scene_actors as scene
import generate_biwn_resource_cpu as gen
ROOT=scene.ROOT;CPU=scene.CPU;get=scene.get;save=scene.save
CLIENTS=[0xc2128,0xc1928];DONE=[0x100200,0x100210]
RES_ENTRIES=set(gen.RANGES)|{0xe3ee};RES_RETURNS={0x1b042,0x1b000,0x15578,0x1545a,0x152a0,0x1b152,0xe4a8}
CD_ENTRIES={0xd1e0,0xd206,0xd2f0,0xd306};CD_RETURNS={0xd1ea,0xd204,0xd29e,0xd304}
def read(p):return json.loads(p.read_text())
class Runtime(scene.Runtime):
    def __init__(self,library):
        super().__init__(library);self.enable_world(8);self.enable_resource_disc();self.enable_cd_cpu();self.enable_loading_yields()
        self.wait_fn=self.lib.biwn_resource_wait;self.signal_fn=self.lib.biwn_resource_signal_body
        for fn in [self.wait_fn,self.signal_fn]:fn.argtypes=[c.POINTER(scene.live.world.Bus),c.POINTER(CPU),c.c_uint32];fn.restype=c.c_int
    def event(self,state):return {'context':self.current(),'CPU':scene.live.prior.scheduler.cpu_dict(state)}
    def setup(self,ram,mode,case):
        self.device.seed(ram,mode);self.world_reset(ram);self.case=case;self.frames={ctx:[]for ctx in CLIENTS};self.cdframes={ctx:[]for ctx in CLIENTS};self.sync_calls=[];self.readiness=[];self.returned=[];self.handoffs=[];self.yields=[]
    def begin(self,state,target):
        row=self.resource_begin(state,target);row['context']=self.current();self.frames[self.current()].append(row);return row
    def end(self,state):self.resource_end(self.frames[self.current()].pop(),state)
    def cdstart(self,state,target):
        row=self.cd_begin(state,target);row['context']=self.current();self.cdframes[self.current()].append(row);return row
    def cdend(self,state):self.cd_end(self.cdframes[self.current()].pop(),state)
    def ready(self,phase,state):
        ram=self.device.ram();slots=[0x15b534+12*j for j in range(50)if get(ram,0x15b534+12*j,2)==self.case['resource_ID']and get(ram,0x15b534+12*j+6,2)]
        assert len(slots)==1,slots;a=slots[0]
        self.readiness.append({'phase':phase,'context':self.current(),'CPU':scene.live.prior.scheduler.cpu_dict(state),'cache_entry':hex(a),'reference_count':get(ram,a+6,2),'ready_word':get(ram,a+8,2),'client_wait_masks':[get(ram,ctx+26)for ctx in CLIENTS]})
    def sync_observe(self,state,target):
        self.sync_calls.append({'target':target,**self.event(state)});self.ready('wait'if target==0xdf8c else'signal',state)
    def returned_observe(self,state):
        assert self.current()==CLIENTS[len(self.returned)]
        self.returned.append(self.event(state))
    def info(self):
        return {'resource_body_calls':self.resource_body_calls,'cd_body_calls':self.cd_body_calls,'sync_calls':self.sync_calls,'readiness':self.readiness,'returned':self.returned,'handoffs':self.handoffs,'yields':self.yields,'IO_calls':self.io_calls,'disc_requests':list(self.disc.requests),'disc_completions':list(self.disc.completions),'disc_stops':self.disc.stops,'completion_events':self.loading_completion_events,'device':self.device.stats()}
    def native(self,ram,initial,case):
        self.setup(ram,0,case);scene.lifecycle.seed_cpu(self,initial);steps=[]
        ranges=[(a,b)for a,b in gen.RANGES.items()]+[(0xd1e0,0xd2a0),(0xd2f0,0xd30a),(0xdf04,0xdf22),(0xdf8c,0xdfa6),(0xdef6,0xdf04),(0xde08,0xde5c),(0xdeb6,0xdee2),(0xdf60,0xdf6c),(0xdf7a,0xdf7c),(DONE[0],DONE[0]+6)]
        for _ in range(300000):
            pc=self.core.m68k_get_reg(None,16);state=self.cpu()
            if pc in DONE:
                self.returned_observe(state)
                if pc==DONE[1]:break
            if pc in RES_ENTRIES:self.begin(state,pc)
            if pc in RES_RETURNS:self.end(state)
            if pc in CD_ENTRIES:self.cdstart(state,pc)
            if pc in CD_RETURNS:self.cdend(state)
            if pc in [0xdf8c,0xdf9c]:self.sync_observe(state,pc)
            if pc==0xdfa4:self.ready('after_signal',state)
            if pc in [0x303c,0x3042]:
                opcode=get(self.device.ram(),pc,2);self.bios_cd_adapter(state,pc)
                if pc==0x3042:self.cdend(state)
                for reg in [0,1,8,9,10]:self.core.m68k_set_reg(reg,state.registers[reg])
                self.core.m68k_set_reg(17,state.sr);self.device.direct(pc,2,0x4e75);self.core.m68k_execute(1);self.device.direct(pc,2,opcode);steps.append(pc);continue
            assert any(a<=pc<b for a,b in ranges),hex(pc)
            if pc in [0xdf60,0xdf8c]:self.yields.append(self.event(state))
            steps.append(pc);self.core.m68k_execute(1)
            if pc in [0xdf6a,0xdf9a]or(pc==0xde5a and self.core.m68k_get_reg(None,16)not in [0xdf66,0xdf96]):self.handoff(self.cpu(),self.handoffs)
        else:raise AssertionError('native two-client resource readiness did not finish')
        info=self.info();info['steps']=steps;return self.device.ram(),self.cpu(),info
    def translated(self,ram,initial,case):
        self.setup(ram,1,case);cpu=CPU.from_buffer_copy(bytes(initial));bus=scene.live.world.Bus(self.device.r8,self.device.r16,self.device.r32,self.device.w16,self.device.w32,scene.live.world.CALL(),None,0);errors=[]
        def resource_call(passed,state,target):
            self.begin(state.contents,target);status=self.resource_body(passed,state,self.device.write8,callback,None,300000,1)
            if not status:self.end(state.contents)
            return status
        def cd_call(passed,state,target):
            self.cdstart(state.contents,target);status=self.cd_body(passed,state,self.device.write8,cd_callback,None,10000,0)
            if not status:self.cdend(state.contents)
            return status
        def cd_service(_,passed,state,target):
            try:
                if target==0xd1e0:return cd_call(passed,state,target)
                self.bios_cd_adapter(state.contents,target);return 0
            except Exception as e:errors.append(repr(e));return 1
        cd_callback=scene.world_cpu.SERVICE(cd_service)
        def resource_service(_,passed,state,target):
            try:
                if target in RES_ENTRIES:return resource_call(passed,state,target)
                if target in [0xd206,0xd2f0,0xd306]:return cd_call(passed,state,target)
                if target==0xdf9c:
                    self.sync_observe(state.contents,target);status=self.signal_fn(passed,state,64)
                    if not status:self.ready('after_signal',state.contents)
                    return status
                raise AssertionError('unexpected resource boundary '+hex(target))
            except Exception as e:errors.append(repr(e));return 1
        callback=scene.world_cpu.SERVICE(resource_service)
        for _ in range(1000):
            if cpu.pc in DONE:
                self.returned_observe(cpu)
                if cpu.pc==DONE[1]:break
                # Declared synthetic return glue is JMP DF7A (no flags/stack
                # effects). The actual removal wrapper/handler then run.
                cpu.pc=0xdf7a;assert self.remove_fn(c.byref(bus),c.byref(cpu),64)==0;self.handoff(cpu,self.handoffs);continue
            if not self.frames[self.current()]:self.begin(cpu,cpu.pc)
            status=self.resource_body(c.byref(bus),c.byref(cpu),self.device.write8,callback,None,300000,1)
            if status==6:
                assert cpu.pc in [0xdf60,0xdf8c],hex(cpu.pc);self.yields.append(self.event(cpu))
                if cpu.pc==0xdf8c:self.sync_observe(cpu,cpu.pc);status=self.wait_fn(c.byref(bus),c.byref(cpu),64)
                else:status=self.yield_fn(c.byref(bus),c.byref(cpu),64)
                assert status==0,(status,errors);self.handoff(cpu,self.handoffs);continue
            assert status==0,(status,errors,hex(cpu.pc));self.end(cpu)
            cpu.pc=get(self.device.ram(),cpu.registers[15]);cpu.registers[15]+=4;cpu.usp=cpu.registers[15]
        else:raise AssertionError('C two-client resource readiness did not finish')
        assert not errors,errors
        return self.device.ram(),cpu,self.info()
def fixture(ram,case,info):
    m=bytearray(ram)
    def put(a,w,v):m[a:a+w]=v.to_bytes(w,'big')
    put(0xc0920,4,CLIENTS[0]);put(0x80,4,0xde08);put(0x88,4,0xdeb6);put(0x90,4,0xdef6)
    m[DONE[0]:DONE[0]+6]=bytes.fromhex('4ef90000df7a')
    for i,ctx in enumerate(CLIENTS):
        sp=ctx+0x400
        for off,w,v in [(0,4,CLIENTS[1-i]),(4,4,CLIENTS[1-i]),(8,4,0x1af04),(12,4,sp),(16,4,0x1af04),(20,2,0),(22,4,0),(26,4,0),(30,4,0),(34,4,0)]:put(ctx+off,w,v)
        put(sp,4,DONE[i]);put(sp+4,2,case['resource_ID'])
    cpu=CPU();cpu.registers[:]=info['CPU']['registers'];cpu.registers[15]=CLIENTS[0]+0x400;cpu.usp=cpu.registers[15];cpu.ssp=0x1ff000;cpu.sr=case['SR'];cpu.pc=0x1af04
    return bytes(m),cpu
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--capture',type=Path,required=True);ap.add_argument('--limit',type=int);opt=ap.parse_args();capture=opt.capture.resolve();out=ROOT/'verification/biwn-resource-readiness'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=ROOT/'projects/black-ice-white-noise/restoration';previous=read(ROOT/'verification/biwn-disc-world-loading-yields-checks.json');names=[n for n in previous['source_sha256']if n.endswith('.c')]+['biwn_resource_sync.c'];library=out/'libresource-readiness.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(source/n)for n in names]+['-o',str(library)]
    run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
    vectors=[{'capture':str(path),'resource_ID':id,'SR':sr}for path in sorted(capture.glob('startup-C-*.bin'))for id in [1,2]for sr in [0,0x71f]][:opt.limit or None];runtime=Runtime(library);rows=[]
    try:
        for i,case in enumerate(vectors):
            save(out/'status.json',{'status':'running','case':i});path=Path(case['capture']);original_ram=path.read_bytes();info=read(capture/f'startup-capture-{path.stem.split("-")[-1]}.json');assert hashlib.sha256(original_ram).hexdigest()==info['C_RAM_sha256'];ram,initial=fixture(original_ram,case,info)
            assert all(not(get(ram,0x15b534+j*12,2)==case['resource_ID']and get(ram,0x15b53a+j*12,2))for j in range(50))
            left,expected,old=runtime.native(ram,initial,case);right,actual,new=runtime.translated(ram,initial,case);keys=[k for k in new if k!='device']
            if left!=right or bytes(expected)!=bytes(actual)or any(old[k]!=new[k]for k in keys):
                save(out/'mismatch.json',{'case':case,'CPU_original':scene.live.prior.scheduler.cpu_dict(expected),'CPU_C':scene.live.prior.scheduler.cpu_dict(actual),'RAM_differences':[hex(j)for j,(a,b)in enumerate(zip(left,right))if a!=b][:50],'original':old,'rebuilt':new});raise AssertionError(str(out/'mismatch.json'))
            assert len(new['disc_requests'])==len(new['disc_completions'])==len(new['completion_events'])==1 and new['disc_stops']==1
            assert [r['target']for r in new['sync_calls']]==[0xdf8c,0xdf9c]and [r['phase']for r in new['readiness']]==['wait','signal','after_signal']
            wait,signal,awake=new['readiness'];assert wait['ready_word']==0 and wait['reference_count']==2 and signal['ready_word']==1 and signal['client_wait_masks'][1]==1 and awake['client_wait_masks'][1]==0
            handles=[e['CPU']['registers'][0]for e in new['returned']];assert len(handles)==2 and handles[0]==handles[1]and handles[0]!=0 and get(right,handles[0])!=0
            payloads=[r['payload']for r in new['resource_body_calls']if 'payload'in r];assert len(payloads)==1 and payloads[0]['matches_preserved_normalized_disc_payload']
            assert not new['device']['original_GPUExec1_calls']and not new['device']['game_frames_executed']
            rows.append({'case':case,'capture_sha256':info['C_RAM_sha256'],'fixture_sha256':hashlib.sha256(ram).hexdigest(),'shared_handle':hex(handles[0]),'payload':payloads[0],'original':old,'rebuilt':new,'all_CPU_full_RAM_nestedframes_handoffs_readiness_match':True})
        save(out/'fixtures.json',rows)
        if opt.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'cases':len(rows),'directory':str(out)}));return
        assert len(rows)==16
        report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'two_actual_resource_clients_wait_load_wake_share_match_original','directory':str(out),'cases':16,'acquisition_returns':32,'actual_loading_yields':16,'actual_readiness_waits':16,'actual_source_signals':16,'actual_first_client_removals':16,'task_handoffs':sum(len(r['rebuilt']['handoffs'])for r in rows),'verified_payloads':16,'verified_payload_bytes':sum(r['payload']['bytes']for r in rows),'payloads':[r['payload']for r in rows],'resource_readiness_verified':True,'resource_body_scripts':0,'readiness_flag_scripts':0,'BIOS_adapter_targets':['0x303c','0x3042'],'completion_data':'Explicit external file bytes/progress after real first loading handoff; source code alone sets ready flags and signals waiter.','source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in names+[n.replace('.c','.h')for n in names]},'matched':['OriginalCPU compares fullCPU/SR/USP/SSP,complete2MBRAM,nestedresource/CD/save/BSR/JSR/TRAP/RTE/RTSframes,allhandoffCPUstates and cache/refcount/readiness transitions. Both clients return the same live handle; every payload independently matches preserved normalized disc bytes.','Cold IDs1/2 from actual captured resource table/cache/heap. First loader suspends; second acquires sameentry/ref2 andTRAP4waits. First resumes,sourcewritesready1,DF9C/DF04clears waitmask, first removes through actualTRAP2/DEB6, second resumesDF96→1AF56 andreturns sharedhandle.'],'limits':['Controlled two-client ring supplied in checked startupRAM, not original full-game task behavior. Caller entries/arguments/stacks and JMP-to-task-removal return glue are declared synthetic test scaffolding. The 21-context world/actor disc scene still does not execute synchronization.','Two BIOS transfer/stop adapters and explicit completion events remain; supplied supervisorstack1FF000 outside transfers. No reconstructed BIOS/physical timing/interrupt/render/queueconsumer/audio/fullgame proof. Native CPU is integrated oracle; separate signal standalone also has independent Unicorn proof. No completeownershipteardown/refrelease claim after both acquired references.'],'compiler':command}
        save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-resource-readiness-checks.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ['payloads','source_sha256','compiler']}))
    except Exception as e:save(out/'status.json',{'status':'terminal_failed','error':repr(e)});raise
    finally:runtime.close()
if __name__=='__main__':main()
