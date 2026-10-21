"""Attack effect against original M68000, with controlled and real RNG paths."""
import argparse
import ctypes as c
import hashlib
import json
import os
from pathlib import Path
import random
import re
import subprocess
from datetime import datetime, timezone
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_boundary_handlers as boundary
import check_biwn_rng as rng_check
import check_biwn_media_setup_cpu as media

ROOT=boundary.ROOT
world=boundary.world
SP,STOP=boundary.SP,boundary.STOP
ENTRY,END=0x18df2,0x18e92
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n')


class Script(boundary.Script):
    def call(self,address,args):
        if self.fail_call==address:raise RuntimeError('Injected dependency failure')
        assert address==0x1a77c and args==[100]
        self.trace.append(['call',address,args])
        return self.case['random_return']


def original(script,case,coverage):
    cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
    cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(script.memory))
    cpu.mem_write(SP,STOP.to_bytes(4,'big'))
    for reg,value in zip(world.REGS,case['incoming']):cpu.reg_write(reg,value)
    cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP)
    linked=case['linked_rng']
    if not linked:cpu.mem_write(0x1a77c,b'\x4e\x75')
    steps=[]
    def code(e,address,width,_):
        if address==0x1a77c and not linked:
            stack=e.reg_read(UC_M68K_REG_A7)
            value=script.call(address,[int.from_bytes(e.mem_read(stack+4,2),'big')])
            e.reg_write(UC_M68K_REG_D0,value)
            return
        assert ENTRY<=address<END or (linked and (0x1a77c<=address<0x1a7f4 or 0xe540<=address<0xe61c)),hex(address)
        if linked and address in {0x1a77c,0xe60a,0xe588,0xe540}:
            stack=e.reg_read(UC_M68K_REG_A7)
            returned=int.from_bytes(e.mem_read(stack,4),'big')
            if not(address==0xe588 and returned==0xe616):
                widths=[2]if address==0x1a77c else[4,4]
                values=[];offset=4
                for w in widths:
                    values.append(int.from_bytes(e.mem_read(stack+offset,w),'big'));offset+=w
                script.trace.append(['call',address,values])
        steps.append(address);coverage.add(address)
    def read(e,access,address,width,value,_):
        if SP-0x1000<=address<SP+4:return
        e.mem_write(address,script.read(address,width).to_bytes(width,'big'))
    def write(e,access,address,width,value,_):
        if SP-0x1000<=address<SP+4:return
        script.write(address,width,value&((1<<(width*8))-1))
    cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write)
    cpu.emu_start(ENTRY,STOP,count=20000,timeout=2000000)
    assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
    for index,reg in enumerate(world.REGS):
        if index not in[0,1,8,9]:assert cpu.reg_read(reg)==case['incoming'][index]
    memory=bytearray(cpu.mem_read(0,0x200000))
    if not linked:memory[0x1a77c:0x1a77e]=script.memory[0x1a77c:0x1a77e]
    assert memory[:SP-0x1000]==script.memory[:SP-0x1000]and memory[SP+4:]==script.memory[SP+4:]
    return cpu.reg_read(UC_M68K_REG_D0),len(steps)


def bind(source,out):
    restore=ROOT/'projects/black-ice-white-noise/restoration'
    for directive in re.findall(r'(?m)^\s*#([^\n]+)',source.read_text()):
        match=re.fullmatch(r'\s*include\s*[<"]([^>"\n]+)[>"]\s*',directive)
        assert match and match[1]in['biwn_attack_effect.h','biwn_world_update.h','stdint.h'],directive
    base=['clang','-std=c99','-I',str(restore)]
    syntax=subprocess.run(base+['-fsyntax-only','-Xclang','-ast-dump=json',str(source)],capture_output=True,text=True)
    (out/'syntax.log').write_text(syntax.stderr);assert not syntax.returncode,syntax.stderr
    tree=json.loads(syntax.stdout)
    functions=[n for n in tree['inner']if n['kind']=='FunctionDecl'and any(x['kind']=='CompoundStmt'for x in n.get('inner',[]))]
    names={n['name']for n in functions};assert 'biwn_attack_effect'in names
    assert all(n['name']=='biwn_attack_effect'or n.get('storageClass')=='static'for n in functions)
    assert not any(n['kind']in['VarDecl','FileScopeAsmDecl']for n in tree['inner'])
    portability=[]
    def inspect(node):
        assert node['kind']not in['GCCAsmStmt','MSAsmStmt']
        assert node.get('castKind')not in['IntegralToPointer','PointerToIntegral','BitCast']
        if node['kind']in['BinaryOperator','CompoundAssignOperator']and node.get('opcode')in['>>','>>=']:
            left_type=node['inner'][0]['type']
            if 'unsigned'not in left_type.get('desugaredQualType',left_type['qualType']):
                portability.append('Portable C99 requires explicit unsigned arithmetic shift/sign fill, not implementation-defined signed right shift.')
        if node['kind']=='CallExpr':
            target=node['inner'][0]
            while target['kind']in['ImplicitCastExpr','ParenExpr']:target=target['inner'][0]
            assert(target['kind']=='MemberExpr'and target['name']in['read16','read32','write16','call'])or(target['kind']=='DeclRefExpr'and target['referencedDecl']['name']in names)
        for child in node.get('inner',[]):inspect(child)
    for node in functions:inspect(node)
    save(out/'portability.json',portability)
    library=out/'libattack.dylib'
    command=base+['-dynamiclib','-O2','-Wall','-Wextra','-Werror',str(source)]+[str(restore/name)for name in['biwn_rng.c','biwn_signed_division.c','biwn_camera.c']]+['-o',str(library)]
    built=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'compiler.log').write_text(built.stdout+built.stderr);assert not built.returncode,built.stderr
    lib=c.CDLL(str(library));fn=lib.biwn_attack_effect;fn.argtypes=[c.POINTER(world.Bus),c.POINTER(c.c_uint32)];fn.restype=c.c_int
    return fn,rng_check.bind(lib),command


def translated(fn,bindings,script,case,missing=None,null_bus=False,null_out=False):
    functions,division,multiply=bindings
    def reader(width):
        def cb(_,address,result):
            try:result[0]=script.read(address,width);return 0
            except Exception as exc:script.errors.append(str(exc));return 1
        return cb
    def writer(width):
        def cb(_,address,value):
            try:script.write(address,width,value);return 0
            except Exception as exc:script.errors.append(str(exc));return 1
        return cb
    def call(_,address,args,count,result):
        try:
            values=list(args[:count])
            if script.fail_call==address:raise RuntimeError('Injected dependency failure')
            if not case['linked_rng']:
                result[0]=script.call(address,values);return 0
            script.trace.append(['call',address,values])
            if address==0x1a77c:
                assert values==[100];return functions[address](c.byref(bus),values[0],result)
            if address==0xe60a:return functions[address](*values,result)
            if address==0xe588:
                remainder=c.c_uint32();return division(*values,result,c.byref(remainder))
            if address==0xe540:result[0]=multiply(*values);return 0
            raise AssertionError(hex(address))
        except Exception as exc:script.errors.append(str(exc));return 1
    callbacks=[world.R8(),world.R16(reader(2)),world.R32(reader(4)),world.W16(writer(2)),world.W32(writer(4)),world.CALL(call)]
    if missing is not None:callbacks[missing]=type(callbacks[missing])()
    bus=world.Bus(*callbacks,None,0);value=c.c_uint32(0xa55aa55a)
    status=fn(None if null_bus else c.byref(bus),None if null_out else c.byref(value))
    return status,value.value


def fixtures():
    generator=random.Random(ENTRY);rows=[]
    words=[0,1,199,200,0x3fff,0x4000,0x7fff,0x8000,0xffff]
    for i in range(384):
        aligned=0 if i%17==0 else 1;in_range=0 if i%19==0 else 1
        cooldown=[0,1,300,0x7fff,0x8000,0xffff][i%6]
        score=words[(i//6)%len(words)];radius=words[(i//9)%len(words)]
        target=[-1,0,1,39][i%4];weapon=[-32768,-1,0,1,5,32767][i%6]
        x=[0xbf*64-1,0xbf*64,0xbf*64+63,0xc0*64,0xffffffff,0x80000000][i%6]
        z=[0x22f*64-1,0x22f*64,0x22f*64+63,0x230*64,0xffffffff,0x7fffffff][(i//6)%6]
        initial=[[0x49d5e,2,aligned],[0x49d5c,2,in_range],[0x49d62,2,cooldown],
                 [0x49d66,2,radius],[0x49d12,2,score],[0x49d60,2,target&65535],
                 [0x49d5a,2,weapon&65535],[0x461b4+weapon*2,2,words[i%len(words)]],
                 [0x49e34+target*206,2,generator.randrange(65536)],
                 [0x49c50,4,x],[0x49c56,4,z],[0x43d98,2,0xa55a]]
        rows.append(dict(kind='controlled_rng',linked_rng=False,random_return=[0,199,200,1023,0xffffffff,0xabcdef00][(i//5)%6],incoming=[generator.getrandbits(32)for _ in world.REGS],initial=initial))
    # Direct boundary pairs cover equality/one-below, negative threshold, and word wrap.
    seed=next(row for row in rows if row['initial'][0][2]and row['initial'][1][2]and row['initial'][2][2]==0)
    for score,radius,random_value in[(0,0,199),(0,0,200),(0,0,1023),(0x7fff,0,0),(0xff38,0,0),(0xffff,0,198),(0,0x8000,199),(0x7fff,0xffff,0)]:
        row=json.loads(json.dumps(seed));row['kind']='threshold_boundary';row['random_return']=random_value
        row['initial'] += [[0x49d12,2,score],[0x49d66,2,radius],[0x49d60,2,0],[0x49d5a,2,0],[0x461b4,2,7],[0x49e34,2,3],[0x49c50,4,0xbf*64],[0x49c56,4,0x22f*64]];rows.append(row)
    for index,seed_value in enumerate([0,1,2,44487,44488,0x7ffffffe,0x7fffffff,0x80000000,0xffffffff]*2):
        row=json.loads(json.dumps(seed));row.update(kind='real_indexed_rng',linked_rng=True)
        row['initial'] += [[0x49d12,2,[0,1000,0x7fff][index%3]],[0x49d66,2,100],
                           [0x49d60,2,index%40],[0x49d5a,2,index%6],
                           [0x461b4+(index%6)*2,2,7],[0x49e34+(index%40)*206,2,100],
                           [0x462e8,4,44488],[0x462ec,4,3399],[0x113082+400,4,seed_value]]
        rows.append(row)
    return rows


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True);parser.add_argument('--no-publish',action='store_true');args=parser.parse_args()
    out=ROOT/'verification/attack-effect'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    fn,bindings,compiler=bind(args.source,out)
    snapshot=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes()
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    image=(session/'nextstage-68000-candidate.bin').read_bytes()
    assert world.select.stage.digest(image)==world.select.stage.STAGE_SHA
    assert snapshot[ENTRY:END]==image[ENTRY-0x4000:END-0x4000]
    vectors=fixtures();coverage=set();results=[]
    for index,case in enumerate(vectors):
        left=Script(snapshot,case);right=Script(snapshot,case);expected,steps=original(left,case,coverage);status,actual=translated(fn,bindings,right,case)
        if status or right.errors or actual!=expected or left.trace!=right.trace or left.memory!=right.memory:
            save(out/'mismatch.json',dict(case=index,parameters=case,status=status,expected=expected,actual=actual,errors=right.errors,original_trace=left.trace,C_trace=right.trace));raise AssertionError(out/'mismatch.json')
        results.append(dict(case=index,kind=case['kind'],D0=actual,instructions=steps,trace_sha256=sha(json.dumps(left.trace).encode()),RAM_sha256=sha(left.memory),damage_word_writes=sum(t[0]=='w'and t[1]!=0x49d62 and t[1]!=0x43d98 and t[2]==2 for t in left.trace)))
    decoded,_=world.select.binary_tools.m68k_instructions(snapshot[ENTRY:END],ENTRY)
    assert all(row['address']in coverage for row in decoded),[hex(row['address'])for row in decoded if row['address']not in coverage]
    guards=[]
    for options in[dict(null_bus=True),dict(null_out=True)]+[dict(missing=i)for i in[1,2,3,5]]:
        script=Script(snapshot,vectors[0]);status,value=translated(fn,bindings,script,vectors[0],**options);assert status==1 and value==0xa55aa55a and not script.trace;guards.append(options)
    selected=next(case for case in vectors if not case['linked_rng']and case['kind']=='threshold_boundary'and case['random_return']==199)
    baseline=Script(snapshot,selected);original(baseline,selected,set())
    for index,event in enumerate(baseline.trace):
        if event[0]not in['r','w','call']:continue
        script=Script(snapshot,selected)
        if event[0]=='call':script.fail_call=event[1];wanted=3
        else:setattr(script,'fail_read'if event[0]=='r'else'fail_write',(event[1],event[2]));wanted=2
        status,value=translated(fn,bindings,script,selected);assert status==wanted and value==0xa55aa55a
        assert script.trace==baseline.trace[:index],dict(event=index,trace=script.trace,expected=baseline.trace[:index])
        guards.append(dict(failed_event=event[:3],status=status,prior_effects_retained=True))
    core=Path(json.loads((ROOT/'verification/DSP-music-context-experimental-candidate.json').read_text())['core_path'])
    oracle=media.scheduler.Native(diagnostic_core=core);runtime=media.Runtime.__new__(media.Runtime);runtime.oracle,runtime.device,runtime.core=oracle,oracle.device,oracle.lib;native=[]
    try:
        for case in[case for case in vectors if case['linked_rng']]:
            expected=Script(snapshot,case);status,value=translated(fn,bindings,expected,case);initial=Script(snapshot,case);initial.memory[SP:SP+4]=STOP.to_bytes(4,'big')
            cpu=media.CPU();cpu.registers[:15]=case['incoming'];cpu.registers[15]=SP;cpu.pc=ENTRY;cpu.sr=0x2000;cpu.usp=0x180000;cpu.ssp=SP
            runtime.device.seed(bytes(initial.memory),0);runtime.seed_cpu(cpu);steps=0
            while runtime.cpu().pc!=STOP and steps<20000:runtime.core.m68k_execute(1);steps+=1
            actual=runtime.cpu();memory=runtime.device.ram()
            assert not status and not expected.errors and actual.pc==STOP and actual.registers[15]==SP+4 and actual.registers[0]==value
            assert memory[:SP-0x1000]==expected.memory[:SP-0x1000]and memory[SP+4:]==expected.memory[SP+4:]
            native.append(dict(seed=next(v for a,w,v in reversed(case['initial'])if a==0x113082+400),D0=value,instructions=steps))
    finally:oracle.close()
    assert not json.loads((out/'portability.json').read_text()), 'Implementation-defined signed right shift rejected; see portability.json'
    save(out/'fixtures.json',vectors);save(out/'case-results.json',results);save(out/'guards.json',guards);save(out/'native.json',native)
    report=dict(status='attack_effect_original_and_native_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),source=str(args.source.resolve()),source_sha256=sha(args.source.read_bytes()),cases=len(vectors),instruction_coverage=[len(decoded),len(decoded)],native_cases=len(native),guard_cases=len(guards),linked_real_RNG_cases=sum(case['linked_rng']for case in vectors),compiler=compiler,core=str(core),core_sha256=sha(core.read_bytes()),scope='Full18DF2..18E92 ordered external bus effects, fullD0 and2MBRAM against original UnicornM68000; real indexedRNG/division/multiply linked on18cases and pinned-native finalD0/RAM. Private stack/CCR/caller-saved registers, physicaltiming and natural gameplay hits excluded. No gameplay patch/default promotion or new training.')
    save(out/'report.json',report)
    if not args.no_publish:save(ROOT/'verification/attack-effect-current.json',report)
    print(json.dumps(report),flush=True)


if __name__=='__main__':main()
