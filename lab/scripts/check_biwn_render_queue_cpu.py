"""Render/queue fullCPU with actual spriteGPU/Cdecoder and independent CPU oracle."""
import argparse,ctypes as c,hashlib,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_cd_cpu as cd
import check_biwn_actor_lifecycle_runtime as lifecycle
import animation_renderer as renderer
ROOT=cd.ROOT;CPU=cd.CPU;world=cd.world;SP=0x1ff000;STOP=0x1ffe00
ENTRIES={0xea20,0xea28,0xe2b8,0xe098};RETURNS={0xea26,0xeac2,0xe2f2,0xe0a4};SCRIPTS={0x17e0e,0x181f8}
save=cd.save;read=lambda p:json.loads(p.read_text())
def make_cpu(case):
    s=CPU();s.registers[:]=case['registers'];s.pc=case['entry'];s.sr=case['SR'];s.usp=case['usp'];s.ssp=case['ssp'];return s
class Runtime(cd.Runtime):
    def __init__(self,library,rows):
        self.native_oracle=cd.scheduler.Native();self.device=self.native_oracle.device;self.core=self.native_oracle.lib;self.prefix=self.native_oracle.prefix;self.lib=c.CDLL(str(library));self.rows={r['address']:r for r in rows}
        self.core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];self.core.GPUReadLong.restype=c.c_uint32;self.core.GPUWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32]
        self.fn=self.lib.biwn_render_queue_cpu_body;self.call=self.lib.biwn_render_queue_cpu_call
        for f in [self.fn,self.call]:f.argtypes=[c.POINTER(world.Bus),c.POINTER(CPU),cd.dispatch.W8,cd.world_cpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];f.restype=c.c_int
    def reset(self,ram,case,mode):
        super().reset(ram,case,mode);self.queues={(q['address'],q['width']):list(q['values'])for q in case['read_queues']}
    def inject(self,a,w):
        queue=self.queues.get((a,w))
        if queue:
            v=queue.pop(0)
            if a<0x200000:self.device.direct(a,w,v)
            else:assert w==4;self.core.GPUWriteLong(a,v,0)
    def read(self,a,w):
        self.inject(a,w);v=self.device.read(a,w);self.trace.append(['r',a,w,v]);return v
    def write(self,a,w,v):
        self.trace.append(['w',a,w,v])
        if w==1:self.device.direct(a,w,v)
        elif w==2:self.device.write16(a,v)
        else:self.device.write(a,v)
    def stats(self):
        v=self.device.stats();v['original_GPUExec1_calls']=v['GPUExec1_calls'];return v
    def scripted(self,s,target):
        row={'target':target,'actual_body':False,'incoming':cd.scheduler.cpu_dict(s)};seed=(target+self.case['id']*1234567)&0xffffffff
        for r in [0,1,8,9]:s.registers[r]=(seed*(r+1)+0xaabbccdd)&0xffffffff
        s.sr=(s.sr&0xffe0)|(seed&31);row['return']=cd.scheduler.cpu_dict(s);self.calls.append(row)
    def native(self,ram,case,coverage):
        self.reset(ram,case,0);lifecycle.seed_cpu(self,make_cpu(case));steps=[];stack=[];pending=None
        for target in SCRIPTS:self.device.direct(target,2,0x4e75)
        try:
            for _ in range(10000):
                pc=self.core.m68k_get_reg(None,16)
                if pc==STOP or(case['render']and pc==0xdf60)or(case['body']and pc==case['outer_RTS']):break
                if pc in SCRIPTS:
                    state=self.cpu();self.scripted(state,pc)
                    for r in [0,1,8,9]:self.core.m68k_set_reg(r,state.registers[r])
                    self.core.m68k_set_reg(17,state.sr);pending=None
                else:
                    assert pc in self.rows,hex(pc)
                    if pending==pc:
                        row={'target':pc,'actual_body':True,'incoming':cd.scheduler.cpu_dict(self.cpu())};self.calls.append(row);stack.append(row);pending=None
                    if pc in RETURNS and stack:stack.pop()['return']=cd.scheduler.cpu_dict(self.cpu())
                    source=self.rows[pc]
                    if source['assembly'].startswith('jsr '):
                        target=int(source['assembly'].split('$')[1].split('.')[0],16);pending=target if target in ENTRIES else None
                    if pc==0xe098:self.inject(0xf03200,4)
                    if pc==0xe2e0:self.inject(0xf03204,4)
                    if pc in [0xea2e,0xeab0]:self.inject(0x112940,2)
                    if pc in [0x17dc2,0x17dd4,0x17de0,0x17dec]:self.inject(0x778cc,4)
                    steps.append(pc);coverage.add(pc)
                self.core.m68k_execute(1)
                if pc==0xe2d6:self.device.write(0xf03204,0x4b00)
            else:raise AssertionError('native render/queue did not stop')
        finally:
            for target in SCRIPTS:self.device.direct(target,2,int.from_bytes(ram[target:target+2],'big'))
        assert not stack,stack
        return self.device.ram(),self.cpu(),{'steps':steps,'calls':self.calls,'device':self.stats()}
    def unicorn(self,ram,case,coverage):
        self.reset(ram,case,0);e=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);e.ctl_set_cpu_model(UC_CPU_M68K_M68000);e.mem_map(0,0x200000);e.mem_map(0xf02000,0x2000);e.mem_write(0,ram)
        for target in SCRIPTS:e.mem_write(target,b'\x4e\x75')
        e.reg_write(UC_M68K_REG_SR,case['SR'])
        for r,v in zip(cd.REGS,case['registers']):e.reg_write(r,v)
        def code(cpu,pc,w,_):
            if(case['render']and pc==0xdf60)or(case['body']and pc==case['outer_RTS']):cpu.emu_stop();return
            if pc in SCRIPTS:
                s=make_cpu(case);s.registers[:]=[cpu.reg_read(r)for r in cd.REGS];s.pc=pc;self.scripted(s,pc)
                for r in [0,1,8,9]:cpu.reg_write(cd.REGS[r],s.registers[r])
                cpu.reg_write(UC_M68K_REG_SR,s.sr)
            else:assert pc in self.rows,hex(pc);coverage.add(pc)
        def reader(cpu,access,a,w,v,_):cpu.mem_write(a,self.read(a,w).to_bytes(w,'big'))
        def writer(cpu,access,a,w,v,_):self.write(a,w,v&((1<<(8*w))-1))
        hook=e.hook_add(UC_HOOK_CODE,code);e.hook_add(UC_HOOK_MEM_READ,reader);e.hook_add(UC_HOOK_MEM_WRITE,writer);e.emu_start(case['entry'],STOP,count=10000,timeout=30000000)
        s=make_cpu(case);s.registers[:]=[e.reg_read(r)for r in cd.REGS];s.pc=e.reg_read(UC_M68K_REG_PC)
        if case['SR']&0x2000:s.ssp=s.registers[15]
        else:s.usp=s.registers[15]
        output=self.device.ram();trace=list(self.trace);e.hook_del(hook);e.mem_write(STOP,b'\x40\xc7');e.emu_start(STOP,STOP+2,count=1);s.sr=e.reg_read(UC_M68K_REG_D7)&65535
        return output,s,{'trace':trace,'device':self.stats()}
    def translated(self,ram,case,missing=None,null_bus=False,null_cpu=False,null_service=False,budget=10000,fail=None,bad_pc=False,stop_flag=None):
        self.reset(ram,case,1)
        def reader(w):
            def cb(_,a,v):
                if fail==('read',w):return 1
                try:v[0]=self.read(a,w);return 0
                except Exception as e:self.errors.append(repr(e));return 1
            return cb
        def writer(w):
            def cb(_,a,v):
                if fail==('write',w):return 1
                try:self.write(a,w,v);return 0
                except Exception as e:self.errors.append(repr(e));return 1
            return cb
        types=[world.R8,world.R16,world.R32,world.W16,world.W32,cd.dispatch.W8];callbacks=[types[0](reader(1)),types[1](reader(2)),types[2](reader(4)),types[3](writer(2)),types[4](writer(4)),types[5](writer(1))]
        if missing is not None:callbacks[missing]=types[missing]()
        bus=world.Bus(*callbacks[:5],world.CALL(),None,0)
        def service(_,passed,state,target):
            if fail==('helper',target):return 1
            try:
                if target in ENTRIES:
                    row={'target':target,'actual_body':True,'incoming':cd.scheduler.cpu_dict(state.contents)};self.calls.append(row);status=self.fn(passed,state,callbacks[5],callback,None,budget,0);row['return']=cd.scheduler.cpu_dict(state.contents);return status
                assert target in SCRIPTS,hex(target);self.scripted(state.contents,target);return 0
            except Exception as e:self.errors.append(repr(e));return 1
        callback=cd.world_cpu.SERVICE()if null_service else cd.world_cpu.SERVICE(service);s=make_cpu(case)
        if bad_pc:s.pc=0
        before=bytes(s);f=self.fn if case['body']or case['render']else self.call;status=f(None if null_bus else c.byref(bus),None if null_cpu else c.byref(s),callbacks[5],callback,None,budget,int(case['render'])if stop_flag is None else stop_flag)
        return self.device.ram(),s,{'status':status,'CPU_unchanged':before==bytes(s),'calls':self.calls,'trace':list(self.trace),'errors':self.errors,'device':self.stats()}
def cases(snapshot):
    rng=random.Random(0xea2878);vectors=[]
    def add(entry,index=0,flip=False,kind='normal',initial_count=None,read_queues=None):
        ram,info=renderer.frame_ram(snapshot,index,flip);params=[];body=len(vectors)%3==1;render=entry in [0x17dc2,0x17dce]
        if entry==0xe2b8:
            handle=int.from_bytes(ram[0x49ca4:0x49ca8],'big');params=[int.from_bytes(ram[handle:handle+4],'big'),index,info['output']+16]
        regs=[rng.getrandbits(32)for _ in range(15)]+[SP];sup=len(vectors)%2;sr=(0x2000 if sup else 0)|((len(vectors)%8)<<8)|rng.randrange(32)
        if render:
            body=False;regs[2]=[0,1,0x7fffffff,0xffffffff][len(vectors)%4]
        vectors.append({'id':len(vectors),'entry':entry,'index':index,'flip':flip,'kind':kind,'body':body,'render':render,'params':params,'registers':regs,'SR':sr,'usp':0x170000 if sup else SP,'ssp':SP if sup else 0x1d0000,'outer_RTS':{0xea20:0xea26,0xea28:0xeac2,0xe2b8:0xe2f2,0xe098:0xe0a4}.get(entry,0),'initial_count':initial_count,'read_queues':read_queues or[]})
    for i in range(72):
        for flip in [False,True]:add(0xea28,i,flip)
    for i in range(32):add(0xea20,i,initial_count=[0,1,0x7fff,0xffff][i%4])
    for i in range(72):add(0xe2b8,i,read_queues=[{'address':0xf03200,'width':4,'values':[1,0,0]},{'address':0xf03204,'width':4,'values':[0x4b00,0xffffffff]}]if i%3==0 else[])
    for i in range(32):add(0xe098,i,read_queues=[{'address':0xf03200,'width':4,'values':[1,1,0]}])
    for i in range(64):add(0x17dce,i%72,flip=bool(i%2),read_queues=[{'address':0x778cc,'width':4,'values':[0,0x7fffffff,0xffffffff,1]if i%2 else[0xffffffff,0,7,0]}])
    for i in range(8):add(0x17dc2,i)
    for i in range(8):add(0xea28,i,kind='multiple',initial_count=3)
    for i in range(8):add(0xea28,i,kind='multiple',initial_count=1,read_queues=[{'address':0x112940,'width':2,'values':[1,2,2]}])
    for count in [0,0xffff]:add(0xea28,0,initial_count=count)
    return vectors
def fixture(snapshot,case):
    raw,info=renderer.frame_ram(snapshot,case['index'],case['flip']);ram=bytearray(raw)
    for i,v in enumerate([STOP]+case['params']):ram[SP+i*4:SP+i*4+4]=v.to_bytes(4,'big')
    if case['kind']=='multiple':
        for j in range(1,3):
            a=0x1126c0+16*j;ram[a:a+16]=ram[0x1126c0:0x1126d0];ram[a+4:a+8]=((case['index']+j)%72).to_bytes(4,'big');ram[a+12:a+16]=(j%2).to_bytes(4,'big')
    if case['initial_count']is not None:ram[0x112940:0x112942]=case['initial_count'].to_bytes(2,'big')
    return bytes(ram)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opt=ap.parse_args();out=ROOT/'verification/biwn-render-queue-cpu'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'librender-queue-cpu.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_render_queue_cpu.c'),'-o',str(library)]
    run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'render-queue-fullCPU-generation.json');manifest,snapshot=renderer.assets();vectors=cases(snapshot)
    if opt.limit:vectors=sum([[v for v in vectors if v['entry']==entry][:opt.limit]for entry in [0xea20,0xea28,0xe2b8,0xe098,0x17dc2,0x17dce]],[])
    runtime=Runtime(library,mapping['instructions_decoded']);rows=[];coverage=set()
    try:
        for i,case in enumerate(vectors):
            save(out/'status.json',{'status':'running','case':i});ram=fixture(snapshot,case);left,expected,old=runtime.native(ram,case,coverage);observed,observer,seen=runtime.unicorn(ram,case,coverage);right,actual,new=runtime.translated(ram,case)
            if new['status']!=(6 if case['render']else 0)or bytes(expected)!=bytes(actual)or bytes(observer)!=bytes(actual)or left!=right or observed!=right or seen['trace']!=new['trace']or old['calls']!=new['calls']:
                save(out/'mismatch.json',{'case':case,'CPU_original':cd.scheduler.cpu_dict(expected),'CPU_Unicorn':cd.scheduler.cpu_dict(observer),'CPU_C':cd.scheduler.cpu_dict(actual),'RAM_differences':[hex(j)for j,(a,b)in enumerate(zip(left,right))if a!=b][:30],'Unicorn_RAM_differences':[hex(j)for j,(a,b)in enumerate(zip(observed,right))if a!=b][:30],'original':old,'Unicorn':seen,'rebuilt':new});raise AssertionError(str(out/'mismatch.json'))
            assert not new['device']['original_GPUExec1_calls']and not new['device']['original_GPU_sprite_decodes']and not new['device']['game_frames_executed']and not new['device']['device_error']
            assert old['device']['original_GPU_sprite_decodes']==new['device']['C_sprite_decodes']
            rows.append({'case':case,'CPU':cd.scheduler.cpu_dict(actual),'original':old,'rebuilt':new,'fullCPU_fullRAM_privateframes_orderedbus_helpers_match':True})
        save(out/'fixtures.json',rows)
        if opt.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'cases':len(rows),'directory':str(out)}));return
        missing=[r for r in mapping['instructions_decoded']if r['address']not in coverage];save(out/'coverage.json',{'instructions':mapping['instructions_decoded'],'uncovered':missing});assert not missing,[hex(r['address'])for r in missing]
        guards=[];case=vectors[0];ram=fixture(snapshot,case)
        for kwargs in [{'missing':i}for i in range(6)]+[{'null_bus':True},{'null_cpu':True},{'null_service':True},{'budget':0},{'stop_flag':2}]:
            _,_,r=runtime.translated(ram,case,**kwargs);assert r['status']==1 and r['CPU_unchanged']and not r['trace'];guards.append(kwargs)
        for kwargs,status in [({'bad_pc':True},7),({'budget':1},4)]:
            _,_,r=runtime.translated(ram,case,**kwargs);assert r['status']==status and r['CPU_unchanged'];guards.append(kwargs)
        for fail in [('read',1),('read',2),('read',4),('write',1),('write',2),('write',4)]:
            probe=next(r['case']for r in rows if any(t[0]==('r'if fail[0]=='read'else'w')and t[2]==fail[1]for t in r['rebuilt']['trace']));_,_,r=runtime.translated(fixture(snapshot,probe),probe,fail=fail);assert r['status']in [2,3]and r['CPU_unchanged'];guards.append({'failure':fail})
        case=next(v for v in vectors if v['entry']==0x17dce);_,_,r=runtime.translated(fixture(snapshot,case),case,fail=('helper',0xea28));assert r['status']==3 and r['CPU_unchanged'];guards.append({'helper_failure':0xea28})
        report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'render_queue_fullCPU_dual_CPU_originalGPU_and_Cdecoder_match','directory':str(out),'CPU_cases':len(rows),'source_instruction_coverage':[78,78],'host_guards':len(guards),'actual_C_sprite_decodes':sum(r['rebuilt']['device']['C_sprite_decodes']for r in rows),'renderer_suspend_cases':sum(r['case']['render']for r in rows),'source_sha256':mapping['source_sha256'],'stage_sha256':mapping['stage_sha256'],'generator_sha256':mapping['generator_sha256'],'device_bridge_sha256':hashlib.sha256((ROOT/'tools/libbiwn-movement-device.dylib').read_bytes()).hexdigest(),'matched':['NativeCPU and independent Unicorn match fullCPU/SR/USP/SSP,whole2MBRAM,private MOVEM/JSR/RTSframes,orderedCPUbus and allnestedhelper incoming/return states. Source16instruction renderloop suspends/resumes at realDF60boundary, with wrapped clock fields.','Actual originalGPU4B00 decoding versus reconstructedCdecoder for72capturedspriteframes,flips,multiple/dynamicqueues and mailbox busy rereads. Reconstructed side runs no originalCPU/GPU or gameframes.'], 'limits':['Standalone supplied queues and captured72frameassets, not live world/render task linkage. Scene draw17E0E andoverlay181F8 are two explicit ABI-adversary scripts in rendercaller cases. No full3Ddraw/viewport/audio/fullgame claim.','Synchronous GPU mailbox completion with some declared external read changes; supplied clock values, no hardwaretiming/concurrency/physical validation. Hostbus/budget/helper failures retain priorRAM and unchanged inputCPU.'],'compiler':command}
        save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-render-queue-cpu-checks.json',report);print(json.dumps(report))
    except Exception as e:save(out/'status.json',{'status':'terminal_failed','error':repr(e)});raise
    finally:runtime.close()
if __name__=='__main__':main()
