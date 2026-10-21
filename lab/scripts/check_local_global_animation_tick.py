"""Unedited local C versus the complete original 10BA4 game routine."""
import ctypes as c
import hashlib
import itertools
import json
import os
import random
import re
import subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_boundary_handlers as boundary
ROOT=Path(__file__).resolve().parents[1]
SP=0x1ff000;STOP=0x190000
def oracle(script,case,coverage):
    cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(script.memory));cpu.mem_write(SP,STOP.to_bytes(4,'big'))
    for reg,value in zip(boundary.REGS,case['incoming']):cpu.reg_write(reg,value)
    cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP);steps=[]
    def code(e,a,w,_):assert 0x10ba4<=a<=0x10c16,hex(a);steps.append(a);coverage.add(a)
    def read(e,t,a,w,v,_):
        if a==SP and w==4:return
        e.mem_write(a,script.read(a,w).to_bytes(w,'big'))
    def write(e,t,a,w,v,_):script.write(a,w,v&((1<<(8*w))-1))
    cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(0x10ba4,STOP,count=100,timeout=1000000)
    assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
    memory=bytes(cpu.mem_read(0,0x200000));assert memory[:SP]==script.memory[:SP]and memory[SP+4:]==script.memory[SP+4:]
    return cpu.reg_read(UC_M68K_REG_D0),steps
def translated(fn,script,case,missing=None,null_bus=False,null_out=False):
    errors=[]
    def read(width):
        def f(_,address,out):
            try:out[0]=script.read(address,width);return 0
            except Exception as error:errors.append(repr(error));return 1
        return f
    def write(width):
        def f(_,address,value):
            try:script.write(address,width,value);return 0
            except Exception as error:errors.append(repr(error));return 1
        return f
    w=boundary.world
    callbacks=[w.R8(),w.R16(read(2)),w.R32(read(4)),w.W16(write(2)),w.W32(write(4)),w.CALL()]
    if missing is not None:callbacks[missing]=type(callbacks[missing])()
    bus=w.Bus(*callbacks,None,0);out=c.c_uint32(0xa55aa55a)
    status=fn(None if null_bus else c.byref(bus),case['incoming'][0],None if null_out else c.byref(out));return status,out.value,errors
def main():
    protocol=json.loads((ROOT/'verification/local-global-animation-author-current.json').read_text());out=Path(protocol['directory']);source=out/'biwn_global_animation_tick.c';restoration=ROOT/'projects/black-ice-white-noise/restoration'
    inspection=subprocess.run(['clang','-std=c99','-I',str(restoration),'-fsyntax-only','-Xclang','-ast-dump=json',str(source)],capture_output=True,text=True);assert inspection.returncode==0,inspection.stderr
    tree=json.loads(inspection.stdout);functions=[n for n in tree['inner']if n['kind']=='FunctionDecl'and any(x['kind']=='CompoundStmt'for x in n.get('inner',[]))];names={n['name']for n in functions}
    assert 'biwn_global_animation_tick'in names and all(n['name']=='biwn_global_animation_tick'or n.get('storageClass')=='static'for n in functions);assert not any(n['kind']in ['VarDecl','FileScopeAsmDecl']for n in tree['inner'])
    def check(n):
        assert n['kind']not in ['GCCAsmStmt','MSAsmStmt'];assert n.get('castKind')not in ['IntegralToPointer','PointerToIntegral','BitCast']
        if n['kind']=='CallExpr':
            target=n['inner'][0]
            while target['kind']in ['ImplicitCastExpr','ParenExpr']:target=target['inner'][0]
            assert (target['kind']=='MemberExpr'and target['name']in ['read16','read32','write16','write32'])or(target['kind']=='DeclRefExpr'and target['referencedDecl']['name']in names)
        for child in n.get('inner',[]):check(child)
    for f in functions:check(f)
    library=out/'libglobal-animation-tick.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(restoration),str(source),'-o',str(library)];result=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
    fn=c.CDLL(str(library)).biwn_global_animation_tick;fn.argtypes=[c.POINTER(boundary.world.Bus),c.c_uint32,c.POINTER(c.c_uint32)];fn.restype=c.c_int
    snapshot=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();rng=random.Random(0x10ba4);cases=[]
    for timer,phase,limit,offset in itertools.product([0,1,2,0x7fff,0x8000,0xffff],[0,1,2,0x7fff,0x8000,0xffff],[0,2,0x7fff,0x8000,0xffff],[0,1,0x8000,0xffff]):
        initial=[[0x403d4,2,timer],[0x403d0,2,phase],[0x403d2,2,limit],[0x403da,2,offset],[0x400e6,4,0x80000],[0x80090,2,0x9234],[0x23f88,4,0x13579bdf],[0x23f8c,4,0xfedcba98]]
        cases.append(dict(initial=initial,incoming=[rng.getrandbits(32)for _ in boundary.REGS]))
    for queues in [
        [dict(address=0x403d4,width=2,values=[3,9])],
        [dict(address=0x403d0,width=2,values=[0,1,2,0x8001])],
        [dict(address=0x403d0,width=2,values=[0x7fff,0x8000,0xffff,1])]]:
        case=json.loads(json.dumps(cases[0]));case['read_queues']=queues;cases.append(case)
    coverage=set();rows=[]
    for ordinal,case in enumerate(cases):
        a=boundary.Script(snapshot,case);b=boundary.Script(snapshot,case);value,steps=oracle(a,case,coverage);status,actual,errors=translated(fn,b,case)
        if status or value!=actual or a.trace!=b.trace or a.memory!=b.memory:
            (out/'mismatch.json').write_text(json.dumps(dict(case=case,status=status,expected=value,actual=actual,original_trace=a.trace,C_trace=b.trace,errors=errors),indent=2)+'\n');raise AssertionError(out/'mismatch.json')
        rows.append(dict(case=ordinal,full_D0=value,steps=steps,trace=b.trace,parameters=case))
    guards=[]
    for missing in [1,2,3,4]:
        script=boundary.Script(snapshot,cases[0]);status,value,errors=translated(fn,script,cases[0],missing=missing);assert status==1 and value==0xa55aa55a and not script.trace;guards.append(dict(missing=missing))
    for kwargs in [dict(null_bus=True),dict(null_out=True)]:
        script=boundary.Script(snapshot,cases[0]);status,value,errors=translated(fn,script,cases[0],**kwargs);assert status==1 and value==0xa55aa55a and not script.trace;guards.append(kwargs)
    seen=set()
    for event_index,event in enumerate(rows[0]['trace']):
        kind,address,width,value=event;key=(kind,address,width)
        if key in seen:continue
        seen.add(key);script=boundary.Script(snapshot,cases[0])
        if kind=='r':script.fail_read=(address,width)
        else:script.fail_write=(address,width)
        status,value,errors=translated(fn,script,cases[0]);assert status==2 and value==0xa55aa55a and script.trace==rows[0]['trace'][:event_index]
        expected=boundary.Script(snapshot,cases[0])
        for event in rows[0]['trace'][:event_index]:
            if event[0]=='w':expected.put(event[1],event[2],event[3])
        assert script.memory==expected.memory;guards.append(dict(bus_failure=list(key),prior_effects_retained=True))
    evidence=json.loads((out/'evidence.json').read_text());expected_PC={int(s,16)for s in re.findall(r'^([0-9a-fA-F]{8}):',evidence['assembly'],re.M)};assert coverage==expected_PC
    (out/'fixtures.json').write_text(json.dumps(rows,indent=2)+'\n')
    report=dict(status='unedited_local_global_animation_tick_original_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(rows),original_instruction_address_coverage=[len(coverage),len(expected_PC)],source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),instruction_atlas_sha256=hashlib.sha256(snapshot).hexdigest(),source_body_edited=False,host_guards=guards,roles=[dict(role=x['role'],seconds=x['seconds'])for x in protocol['drafts']],new_training=False,native_Chat_verified=False,full_route_runtime_promoted=False,scope='Complete10BA4..10C16 body versus originalM68000, signed countdown/phase/limit/offset edges and volatile rereads; fullD0,externalRAM and ordered bus reads/writes. CCR,otherCPUregisters,private stack/timing,natural gameplay integration and graphics semantic identity excluded.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/local-global-animation-checks-current.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
