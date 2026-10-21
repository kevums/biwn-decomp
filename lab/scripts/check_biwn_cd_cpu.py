"""Full CPU/CD wrapper checks against native CPU and independent Unicorn."""
import argparse, ctypes as c, hashlib, json, os, random, subprocess
from datetime import datetime, timezone
from pathlib import Path
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_scheduler as scheduler
import check_biwn_actor_lifecycle_runtime as lifecycle
import check_biwn_world_cpu as world_cpu
import check_biwn_input_dispatch as dispatch
import generate_biwn_cd_cpu as gen
from check_biwn_68000_slices import make_toc

ROOT=gen.ROOT; CPU=scheduler.CPU; SP=0x1ff000; STOP=0x1ffe00
REGS=[UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7]
BIOS={0x303c,0x3042}; RETURNS={0xd1ea,0xd204}
world=world_cpu.prior
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def make_cpu(case):
    s=CPU();s.registers[:]=case['registers'];s.pc=case['entry'];s.sr=case['SR'];s.usp=case['usp'];s.ssp=case['ssp'];return s

class Runtime:
    def __init__(self,library,rows):
        self.native_oracle=scheduler.Native();self.device=self.native_oracle.device;self.core=self.native_oracle.lib;self.prefix=self.native_oracle.prefix;self.lib=c.CDLL(str(library));self.rows={r['address']:r for r in rows}
        self.fn=self.lib.biwn_cd_cpu_body;self.call=self.lib.biwn_cd_cpu_call
        for f in [self.fn,self.call]:f.argtypes=[c.POINTER(world.Bus),c.POINTER(CPU),dispatch.W8,world_cpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];f.restype=c.c_int
    def reset(self,ram,case,mode):self.device.seed(ram,mode);self.case=case;self.calls=[];self.trace=[];self.errors=[]
    def cpu(self):
        s=CPU();s.registers[:]=[self.core.m68k_get_reg(None,i)for i in range(16)];s.pc=self.core.m68k_get_reg(None,16);s.sr=self.core.m68k_get_reg(None,17);s.usp=self.prefix[16]if s.sr&0x2000 else s.registers[15];s.ssp=s.registers[15]if s.sr&0x2000 else self.prefix[17];return s
    def read(self,a,w):
        assert 0<=a<=0x200000-w,(hex(a),w)
        v=int.from_bytes(c.string_at(self.device.pointer+a,w),'big');self.trace.append(['r',a,w,v]);return v
    def write(self,a,w,v):
        assert 0<=a<=0x200000-w,(hex(a),w)
        self.trace.append(['w',a,w,v]);self.device.direct(a,w,v)
    def scripted(self,s,target):
        row={'target':target,'incoming':scheduler.cpu_dict(s),'actual_body':False}
        # A declared ABI adversary, not an emulation of firmware or a transfer.
        seed=(target+self.case['id']*1234567)&0xffffffff
        for r in [0,1,8,9,10]:s.registers[r]=(seed*(r+1)+0xaabbccdd)&0xffffffff
        s.sr=(s.sr&0xffe0)|(seed&31);row['return']=scheduler.cpu_dict(s);self.calls.append(row)
    def native(self,ram,case,coverage):
        self.reset(ram,case,0);lifecycle.seed_cpu(self,make_cpu(case));steps=[];stack=[]
        for a in BIOS:self.device.direct(a,2,0x4e75)
        try:
            for _ in range(10000):
                pc=self.core.m68k_get_reg(None,16)
                if pc==STOP:break
                if pc in BIOS:
                    s=self.cpu();self.scripted(s,pc)
                    for r in [0,1,8,9,10]:self.core.m68k_set_reg(r,s.registers[r])
                    self.core.m68k_set_reg(17,s.sr)
                else:
                    assert pc in self.rows,hex(pc);steps.append(pc);coverage.add(pc)
                    if pc==0xd1e0 and self.core.m68k_get_reg(None,15)!=SP:
                        row={'target':pc,'incoming':scheduler.cpu_dict(self.cpu()),'actual_body':True};self.calls.append(row);stack.append(row)
                    if pc in RETURNS and stack:stack.pop()['return']=scheduler.cpu_dict(self.cpu())
                self.core.m68k_execute(1)
            else:raise AssertionError('native CD wrapper did not return')
        finally:
            for a in BIOS:self.device.direct(a,2,int.from_bytes(ram[a:a+2],'big'))
        assert not stack
        return self.device.ram(),self.cpu(),{'steps':steps,'calls':self.calls}
    def unicorn(self,ram,case,coverage):
        self.reset(ram,case,0);engine=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);engine.ctl_set_cpu_model(UC_CPU_M68K_M68000);engine.mem_map(0,0x200000);engine.mem_write(0,ram)
        for a in BIOS:engine.mem_write(a,b'\x4e\x75')
        # Bank setup is explicit; the snapshot records both banks separately.
        engine.reg_write(UC_M68K_REG_SR,case['SR'])
        for reg,v in zip(REGS,case['registers']):engine.reg_write(reg,v)
        def code(cpu,pc,w,_):
            if pc in BIOS:
                s=make_cpu(case);s.registers[:]=[cpu.reg_read(r)for r in REGS];s.pc=pc
                self.scripted(s,pc)
                for r in [0,1,8,9,10]:cpu.reg_write(REGS[r],s.registers[r])
                cpu.reg_write(UC_M68K_REG_SR,s.sr)
            else:assert pc in self.rows,hex(pc);coverage.add(pc)
        def read(cpu,access,a,w,v,_):cpu.mem_write(a,self.read(a,w).to_bytes(w,'big'))
        def write(cpu,access,a,w,v,_):self.write(a,w,v&((1<<(8*w))-1))
        hook=engine.hook_add(UC_HOOK_CODE,code);engine.hook_add(UC_HOOK_MEM_READ,read);engine.hook_add(UC_HOOK_MEM_WRITE,write);engine.emu_start(case['entry'],STOP,count=10000,timeout=3000000)
        s=make_cpu(case);s.registers[:]=[engine.reg_read(r)for r in REGS];s.pc=engine.reg_read(UC_M68K_REG_PC);assert s.pc==STOP
        if case['SR']&0x2000:s.ssp=s.registers[15]
        else:s.usp=s.registers[15]
        output=self.device.ram();trace=list(self.trace);engine.hook_del(hook);engine.mem_write(STOP,b'\x40\xc7');engine.emu_start(STOP,STOP+2,count=1);s.sr=engine.reg_read(UC_M68K_REG_D7)&65535
        return output,s,{'trace':trace}
    def translated(self,ram,case,missing=None,null_bus=False,null_cpu=False,null_service=False,budget=10000,fail=None,bad_pc=False):
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
        types=[world.R8,world.R16,world.R32,world.W16,world.W32,dispatch.W8]
        callbacks=[types[0](reader(1)),types[1](reader(2)),types[2](reader(4)),types[3](writer(2)),types[4](writer(4)),types[5](writer(1))]
        if missing is not None:callbacks[missing]=types[missing]()
        bus=world.Bus(*callbacks[:5],world.CALL(),None,0)
        def service(_,passed,state,target):
            if fail==('helper',target):return 1
            try:
                if target==0xd1e0:
                    row={'target':target,'incoming':scheduler.cpu_dict(state.contents),'actual_body':True};self.calls.append(row);status=self.fn(passed,state,callbacks[5],callback,None,budget,0);row['return']=scheduler.cpu_dict(state.contents);return status
                assert target in BIOS,hex(target);self.scripted(state.contents,target);return 0
            except Exception as e:self.errors.append(repr(e));return 1
        callback=world_cpu.SERVICE()if null_service else world_cpu.SERVICE(service);state=make_cpu(case)
        if bad_pc:state.pc=0
        before=bytes(state);status=self.call(None if null_bus else c.byref(bus),None if null_cpu else c.byref(state),callbacks[5],callback,None,budget,0)
        return self.device.ram(),state,{'status':status,'trace':list(self.trace),'calls':self.calls,'errors':self.errors,'CPU_unchanged':before==bytes(state)}
    def close(self):self.native_oracle.close()

def cases(session):
    rng=random.Random(0xd206c0de);toc=bytes(make_toc(json.loads((session/'cdi-layout.json').read_text())));rows=[]
    for entry,count in [(0xd1e0,512),(0xd206,512),(0xd2f0,128),(0xd306,128)]:
        for i in range(count):
            regs=[rng.getrandbits(32)for _ in range(15)]+[SP];params=[];fixture_toc=bytearray(toc)
            if entry==0xd1e0:
                d=[1,2,3,75,2352,65535][i%6]if i<128 else rng.randrange(1,65536)
                n=[0,1,65535,65536,d*65535,min(0xffffffff,d*65536),0xffffffff][(i//6)%7]if i<128 else rng.getrandbits(32)
                regs[0]=(regs[0]&0xffff0000)|d;regs[1]=n
            elif entry==0xd206:
                params=[i%5, [0,1,2351,2352,2353,74*2352,75*2352,4500*2352,641054064,0xffffffff][(i//5)%10]if i<256 else rng.getrandbits(32)]
                if i>=128:
                    for a in [17,18,19]:fixture_toc[a]=rng.randrange(256)
            elif entry==0xd2f0:params=[rng.getrandbits(32)for _ in range(3)]
            sup=i%2;rows.append({'id':len(rows),'entry':entry,'params':params,'registers':regs,'SR':(0x2000 if sup else 0)|((i%8)<<8)|rng.randrange(32),'usp':0x170000 if sup else SP,'ssp':SP if sup else 0x1d0000,'toc_hex':fixture_toc.hex()})
    return rows
def fixture(snapshot,case):
    ram=bytearray(snapshot);toc=bytes.fromhex(case['toc_hex']);ram[0x2c00:0x2c00+len(toc)]=toc
    for i,v in enumerate([STOP]+case['params']):ram[SP+4*i:SP+4*i+4]=v.to_bytes(4,'big')
    return bytes(ram)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opt=ap.parse_args();out=ROOT/'verification/biwn-cd-cpu'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libcd-cpu.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_cd_cpu.c'),'-o',str(library)]
    result=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'cd-wrapper-fullCPU-generation.json').read_text());snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=cases(session)
    if opt.limit:vectors=sum([[v for v in vectors if v['entry']==e][:opt.limit]for e in gen.RANGES],[])
    runtime=Runtime(library,mapping['instructions_decoded']);coverage=set();rows=[]
    try:
        for i,case in enumerate(vectors):
            save(out/'status.json',{'status':'running','case':i});ram=fixture(snapshot,case);left,expected,old=runtime.native(ram,case,coverage);seen,observer,unicorn=runtime.unicorn(ram,case,coverage);right,actual,new=runtime.translated(ram,case)
            if new['status']or bytes(expected)!=bytes(actual)or bytes(observer)!=bytes(actual)or left!=right or seen!=right or unicorn['trace']!=new['trace']or old['calls']!=new['calls']:
                save(out/'mismatch.json',{'case':case,'CPU_original':scheduler.cpu_dict(expected),'CPU_Unicorn':scheduler.cpu_dict(observer),'CPU_C':scheduler.cpu_dict(actual),'RAM_differences':[hex(j)for j,(a,b)in enumerate(zip(left,right))if a!=b][:20],'Unicorn_RAM_differences':[hex(j)for j,(a,b)in enumerate(zip(seen,right))if a!=b][:20],'original':old,'Unicorn':unicorn,'rebuilt':new});raise AssertionError(str(out/'mismatch.json'))
            rows.append({'parameters':case,'CPU':scheduler.cpu_dict(actual),'original':old,'rebuilt':new,'full_CPU_RAM_privateframes_orderedbus_match':True})
        save(out/'fixtures.json',rows)
        if opt.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'cases':len(rows),'directory':str(out)}));return
        missing=[r for r in mapping['instructions_decoded']if r['address']not in coverage];save(out/'coverage.json',{'instructions':mapping['instructions_decoded'],'uncovered':missing});assert not missing,[hex(r['address'])for r in missing]
        guards=[];case=vectors[0];ram=fixture(snapshot,case)
        for kwargs in [{'missing':i}for i in range(6)]+[{'null_bus':True},{'null_cpu':True},{'null_service':True},{'budget':0}]:
            _,_,r=runtime.translated(ram,case,**kwargs);assert r['status']==1 and r['CPU_unchanged']and not r['trace'];guards.append(kwargs)
        for kwargs,status in [({'bad_pc':True},7),({'budget':1},4)]:
            _,_,r=runtime.translated(ram,case,**kwargs);assert r['status']==status and r['CPU_unchanged'];guards.append(kwargs)
        zero={**case,'registers':[case['registers'][0]&0xffff0000]+case['registers'][1:]};_,_,r=runtime.translated(fixture(snapshot,zero),zero);assert r['status']==8 and r['CPU_unchanged'];guards.append({'zero_divisor':'host_status8_not_original_exception'})
        for fail in [('read',1),('read',2),('read',4),('write',4)]:
            row=next(r for r in rows if any(t[0]==('r'if fail[0]=='read'else'w')and t[2]==fail[1]for t in r['rebuilt']['trace']));case=row['parameters'];_,_,r=runtime.translated(fixture(snapshot,case),case,fail=fail);assert r['status']in [2,3]and r['CPU_unchanged'];guards.append({'failure':fail})
        case=next(v for v in vectors if v['entry']==0xd2f0);_,_,r=runtime.translated(fixture(snapshot,case),case,fail=('helper',0x303c));assert r['status']==3 and r['CPU_unchanged'];guards.append({'BIOS_provider_failure':0x303c})
        report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'CD_game_wrappers_fullCPU_dual_oracles_match','directory':str(out),'CPU_cases':len(rows),'CPU_instruction_coverage':[len(coverage),mapping['instructions']],'host_guards':len(guards),'source_sha256':mapping['source_sha256'],'stage_sha256':mapping['stage_sha256'],'generator_sha256':mapping['generator_sha256'],'matched':['All registers/PC/SR/USP/SSP, complete2MBRAM/privateframes, ordered bus and nested helper incoming/return states. User/supervisor calls; actual nonzero-divisor fallback and TOC/MSF code.'], 'limits':['BIOS303C/3042 are explicit deterministic ABI-adversary scripts; no actual transfer in these standalone fixtures. DIVU-overflow N/Z undefined internally and overwritten before return. Zero-divisor host guard does not reproduce CPU exception. No loading task switching, timing, physical-drive or full-game claim.'],'compiler':command}
        save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-cd-cpu-checks.json',report);print(json.dumps(report))
    except Exception as e:save(out/'status.json',{'status':'terminal_failed','error':repr(e)});raise
    finally:runtime.close()
if __name__=='__main__':main()
