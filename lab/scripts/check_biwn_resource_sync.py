"""Native full wait/signal CPU checks; independent Unicorn signal bus oracle."""
import argparse,ctypes as c,hashlib,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_cd_cpu as cd
import check_biwn_actor_lifecycle_runtime as lifecycle
ROOT=cd.ROOT;CPU=cd.CPU;world=cd.world;SP=0x1f8000;SSP=0x1ff000;STOP=0x1ffe00;CTX=[0xc2128,0xc1928,0xc1528,0xc5928,0xc5528]
save=cd.save
def make_cpu(case):
    s=CPU();s.registers[:]=case['registers'];s.pc=case['entry'];s.sr=case['SR'];s.usp=case['usp'];s.ssp=case['ssp'];return s
class Runtime(cd.Runtime):
    def __init__(self,library,rows):
        self.native_oracle=cd.scheduler.Native();self.device=self.native_oracle.device;self.core=self.native_oracle.lib;self.prefix=self.native_oracle.prefix;self.lib=c.CDLL(str(library));self.rows={r['address']:r for r in rows};self.functions={}
        for n in ['biwn_resource_signal_body','biwn_resource_signal_call','biwn_resource_wait','biwn_resource_wait_dispatch']:
            f=getattr(self.lib,n);f.argtypes=[c.POINTER(world.Bus),c.POINTER(CPU),c.c_uint32];f.restype=c.c_int;self.functions[n]=f
    def native(self,ram,case,coverage):
        self.reset(ram,case,0);lifecycle.seed_cpu(self,make_cpu(case));steps=[]
        for _ in range(10000):
            pc=self.core.m68k_get_reg(None,16)
            if pc==STOP:break
            if case['body']and pc==(0xdf20 if case['entry']==0xdf04 else 0xdfa4):break
            assert pc in self.rows or 0xde08<=pc<0xde5c or 0xdf60<=pc<0xdf6c,hex(pc)
            steps.append(pc);coverage.add(pc);self.core.m68k_execute(1)
            if case['entry']==0xdef6 and pc==0xde5a:break
        else:raise AssertionError('native synchronization did not return/switch')
        return self.device.ram(),self.cpu(),{'steps':steps}
    def unicorn(self,ram,case,coverage):
        self.reset(ram,case,0);e=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);e.ctl_set_cpu_model(UC_CPU_M68K_M68000);e.mem_map(0,0x200000);e.mem_write(0,ram);e.reg_write(UC_M68K_REG_SR,case['SR'])
        for reg,v in zip(cd.REGS,case['registers']):e.reg_write(reg,v)
        outer=0xdf20 if case['entry']==0xdf04 else 0xdfa4
        def code(cpu,pc,w,_):
            if case['body']and pc==outer:cpu.emu_stop();return
            assert pc in self.rows,hex(pc);coverage.add(pc)
        def read(cpu,access,a,w,v,_):cpu.mem_write(a,self.read(a,w).to_bytes(w,'big'))
        def write(cpu,access,a,w,v,_):self.write(a,w,v&((1<<(8*w))-1))
        hook=e.hook_add(UC_HOOK_CODE,code);e.hook_add(UC_HOOK_MEM_READ,read);e.hook_add(UC_HOOK_MEM_WRITE,write);e.emu_start(case['entry'],STOP,count=10000,timeout=3000000)
        s=make_cpu(case);s.registers[:]=[e.reg_read(r)for r in cd.REGS];s.pc=e.reg_read(UC_M68K_REG_PC);assert s.pc==(outer if case['body']else STOP)
        if case['SR']&0x2000:s.ssp=s.registers[15]
        else:s.usp=s.registers[15]
        output=self.device.ram();trace=list(self.trace);e.hook_del(hook);e.mem_write(STOP,b'\x40\xc7');e.emu_start(STOP,STOP+2,count=1);s.sr=e.reg_read(UC_M68K_REG_D7)&65535
        return output,s,{'trace':trace}
    def translated(self,ram,case,missing=None,null_bus=False,null_cpu=False,budget=64,fail=None,bad_pc=False):
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
        types=[world.R8,world.R16,world.R32,world.W16,world.W32];callbacks=[types[0](reader(1)),types[1](reader(2)),types[2](reader(4)),types[3](writer(2)),types[4](writer(4))]
        if missing is not None:callbacks[missing]=types[missing]()
        bus=world.Bus(*callbacks,world.CALL(),None,0);s=make_cpu(case)
        if bad_pc:s.pc=0
        name='biwn_resource_wait'if case['entry']==0xdf8c else'biwn_resource_wait_dispatch'if case['entry']==0xdef6 else'biwn_resource_signal_body'if case['body']else'biwn_resource_signal_call';before=bytes(s)
        status=self.functions[name](None if null_bus else c.byref(bus),None if null_cpu else c.byref(s),budget)
        return self.device.ram(),s,{'status':status,'CPU_unchanged':before==bytes(s),'trace':list(self.trace),'errors':self.errors}
def cases():
    rng=random.Random(0xdf8cc0de);rows=[]
    for entry,count in [(0xdf04,256),(0xdf9c,256),(0xdf8c,128),(0xdef6,64)]:
        for i in range(count):
            signal=entry in [0xdf04,0xdf9c];n=1+i%5;mask=[0,1,2,0xffff,0xffffffff,0x80000000][i%6]
            if not signal and n==1:mask=0
            regs=[rng.getrandbits(32)for _ in range(15)]+[SP];regs[0]=mask
            sr=((i%8)<<8)|rng.randrange(32)|(0x2000 if signal and i%2 else 0);usp=0x1f1000 if sr&0x2000 else SP;ssp=SP if sr&0x2000 else SSP;initial=[[SP,4,STOP],[SP+4,4,mask],[0xc0920,4,CTX[0]],[0x90,4,0xdef6],[0x80,4,0xde08],[0x778cc,4,0]]
            for j,ctx in enumerate(CTX[:n]):
                initial += [[ctx,4,CTX[(j+1)%n]],[ctx+4,4,CTX[(j-1)%n]],[ctx+22,4,0],[ctx+26,4,rng.getrandbits(32)if signal else 0 if j in [0,n-1]else 1],[ctx+34,4,0]]
                if j:
                    target=[STOP,0xdf66,0xdf96][(i+j)%3];stack=ctx+0x300;initial += [[ctx+12,4,stack],[ctx+16,4,target],[ctx+20,2,((i+j)%8)<<8|rng.randrange(32)]]
                    if target!=STOP:
                        for k in range(11):initial.append([stack+4*k,4,rng.getrandbits(32)])
                        initial.append([stack+44,4,STOP])
            if entry==0xdef6:
                sr|=0x2000;regs[15]=SSP-6;usp=SP-44;ssp=SSP-6;initial += [[SSP-6,2,0],[SSP-4,4,0xdf96]]
            for body in ([False,True]if signal else[False]):rows.append({'entry':entry,'body':body,'registers':regs,'SR':sr,'usp':usp,'ssp':ssp,'mask':mask,'ring_contexts':n,'initial':initial})
    return rows
def fixture(snapshot,case):
    ram=bytearray(snapshot)
    for a,w,v in case['initial']:ram[a:a+w]=(v&((1<<(w*8))-1)).to_bytes(w,'big')
    return bytes(ram)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opt=ap.parse_args();out=ROOT/'verification/biwn-resource-sync'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libresource-sync.dylib';names=['biwn_resource_sync.c','biwn_scheduler.c'];command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(source/n)for n in names]+['-o',str(library)]
    run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'resource-synchronization-fullCPU-workmap.json').read_text());decoded=sum([f['instructions']for f in mapping['functions']],[]);snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=cases()
    if opt.limit:vectors=sum([[v for v in vectors if v['entry']==e][:opt.limit]for e in [0xdf04,0xdf9c,0xdf8c,0xdef6]],[])
    runtime=Runtime(library,decoded);coverage=set();rows=[]
    try:
        for i,case in enumerate(vectors):
            save(out/'status.json',{'status':'running','case':i});ram=fixture(snapshot,case);left,expected,old=runtime.native(ram,case,coverage);right,actual,new=runtime.translated(ram,case);extra={}
            if case['entry']in [0xdf04,0xdf9c]:
                seen,observer,observed=runtime.unicorn(ram,case,coverage);extra={'CPU_Unicorn':cd.scheduler.cpu_dict(observer),'Unicorn':observed,'Unicorn_RAM_matches':seen==right};assert bytes(observer)==bytes(actual)and seen==right and observed['trace']==new['trace'],extra
            if new['status']or bytes(expected)!=bytes(actual)or left!=right:
                save(out/'mismatch.json',{'case':case,'CPU_original':cd.scheduler.cpu_dict(expected),'CPU_C':cd.scheduler.cpu_dict(actual),'RAM_differences':[hex(j)for j,(a,b)in enumerate(zip(left,right))if a!=b][:30],'original':old,'rebuilt':new,**extra});raise AssertionError(str(out/'mismatch.json'))
            rows.append({'case':case,'CPU':cd.scheduler.cpu_dict(actual),'original':old,'rebuilt':new,'fullCPU_completeRAM_privateframes_match':True})
        save(out/'fixtures.json',rows)
        if opt.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'cases':len(rows),'directory':str(out)}));return
        missing=[r for r in decoded if r['address']not in coverage];save(out/'coverage.json',{'instructions':decoded,'uncovered':missing});assert not missing,[hex(r['address'])for r in missing]
        guards=[]
        for entry in [0xdf04,0xdf8c,0xdef6]:
            case=next(v for v in vectors if v['entry']==entry);ram=fixture(snapshot,case);indices=[2,4]if entry==0xdf04 else[1,2,3,4]
            for kwargs in [{'missing':i}for i in indices]+[{'null_bus':True},{'null_cpu':True},{'budget':0},{'bad_pc':True}]:
                _,_,r=runtime.translated(ram,case,**kwargs);assert r['status']in [1,4]and r['CPU_unchanged']and not r['trace'];guards.append({'entry':entry,**kwargs})
            for fail in [('read',4),('write',4)]:
                probe=next(row['case']for row in rows if row['case']['entry']==entry and any(t[0]==('r'if fail[0]=='read'else'w')and t[2]==fail[1]for t in row['rebuilt']['trace']))
                _,_,r=runtime.translated(fixture(snapshot,probe),probe,fail=fail);assert r['status']==(2 if entry==0xdf04 else 3)and r['CPU_unchanged'],(entry,fail,r);guards.append({'entry':entry,'failure':fail})
        case=next(v for v in vectors if v['entry']==0xdf8c);ram=bytearray(fixture(snapshot,case));ram[0x90:0x94]=bytes(4);_,_,r=runtime.translated(bytes(ram),case);assert r['status']==4 and r['CPU_unchanged'];guards.append({'bad_TRAP4_vector':True})
        blocked=bytearray(fixture(snapshot,case));blocked[SP+4:SP+8]=(1).to_bytes(4,'big');_,_,r=runtime.translated(bytes(blocked),case,budget=3);assert r['status']==2 and r['CPU_unchanged'];guards.append({'all_contexts_blocked':'host_scan_limit'})
        malformed=next(v for v in vectors if v['entry']==0xdf04 and v['ring_contexts']>1);ram=bytearray(fixture(snapshot,malformed));ram[CTX[1]:CTX[1]+4]=CTX[1].to_bytes(4,'big');_,_,r=runtime.translated(bytes(ram),malformed,budget=3);assert r['status']==3 and r['CPU_unchanged'];guards.append({'malformed_signal_ring':'host_scan_limit'})
        report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'resource_wait_signal_fullCPU_native_and_signal_dual_oracles_match','directory':str(out),'CPU_cases':len(rows),'signal_dual_oracle_cases':sum(r['case']['entry']in [0xdf04,0xdf9c]for r in rows),'wait_native_cases':sum(r['case']['entry']==0xdf8c for r in rows),'handler_native_cases':sum(r['case']['entry']==0xdef6 for r in rows),'source_instruction_coverage':[len(decoded),len(decoded)],'host_guards':len(guards),'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in names+[n.replace('.c','.h')for n in names]},'stage_sha256':mapping['stage_sha256'],'matched':['Native original CPU compares fullCPU/SR/USP/SSP,complete2MBRAM/private argument/save/BSR/TRAP/RTE/RTSframes across wait/signal and ring scans. Signal/body/fullcall also matches independent Unicorn orderedbus.','Wait selects fresh or warm DF66/DF96 contexts; scheduler saves waitmask/continuation and restores11registers/RTS. Signal clears requested bits in other contexts, preserving current context flags and X.'],'limits':['Controlled finite task rings/flags, not resource readiness in a running game. Wait/TRAP/RTE full execution has native oracle only; independent Unicorn comparison is signal-only. No full firmware/device timing/interrupt/physicalhardware/fullgame claim. Host scan/vector/bus guards are added behavior.'],'compiler':command}
        save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-resource-sync-checks.json',report);print(json.dumps(report))
    except Exception as e:save(out/'status.json',{'status':'terminal_failed','error':repr(e)});raise
    finally:runtime.close()
if __name__=='__main__':main()
