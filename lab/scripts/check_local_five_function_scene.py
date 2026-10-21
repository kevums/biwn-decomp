"""Original caller+animation+slot clear against the linked local C bodies."""
import ctypes as c,hashlib,itertools,json,os,random,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_local_global_animation_tick as animation
import check_local_slot_clear as slot
SLOT_FN=None
PREPARE_FN=None
FACE_FN=None
ROOT=animation.ROOT;SP=animation.SP;STOP=animation.STOP
HELPERS=[0x1142e,0x10734]
class Script(animation.boundary.Script):
    def call(self,target,args,incoming):
        self.trace.append(['call',target,args,incoming]);self.changed=[]
        if self.fail_call==target:raise RuntimeError('Injected helper failure')
        for address,width,value in self.case['helper_effects'].get(str(target),[]):self.put(address,width,value)
        return self.case['helper_returns'][str(target)]
def original(script,case,coverage):
    cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,bytes(script.memory));cpu.mem_write(SP,STOP.to_bytes(4,'big'))
    for reg,value in zip(animation.boundary.REGS,case['incoming']):cpu.reg_write(reg,value)
    cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP)
    for target in HELPERS:cpu.mem_write(target,b'\x4e\x75')
    steps=[]
    def code(engine,address,width,_):
        if address in HELPERS:
            stack=engine.reg_read(UC_M68K_REG_A7);args=[int.from_bytes(engine.mem_read(stack+off,2),'big')for off in [4,6]]if address==0x10968 else[]
            result=script.call(address,args,engine.reg_read(UC_M68K_REG_D0))
            for a,w,v in script.changed:engine.mem_write(a,v.to_bytes(w,'big'))
            engine.reg_write(UC_M68K_REG_D0,result);return
        if address in [0x10ba4,0x10968,0x11384,0x110d4]:
            args=[int.from_bytes(engine.mem_read(engine.reg_read(UC_M68K_REG_A7)+off,2),'big')for off in [4,6]]if address==0x10968 else[]
            if address==0x110d4:
                sp=engine.reg_read(UC_M68K_REG_A7);args=[int.from_bytes(engine.mem_read(sp+offset,width),'big')for offset,width in [(4,4),(8,4),(12,2)]]
            script.trace.append(['call',address,args,engine.reg_read(UC_M68K_REG_D0)])
        assert 0x11ad4<=address<=0x11b4a or 0x10ba4<=address<=0x10c16 or 0x10968<=address<=0x1098e or 0x110d4<=address<=0x1142c,hex(address)
        coverage.add(address);steps.append(address)
    def read(engine,t,a,w,v,_):
        if SP-40<=a<SP+4 or 0x11104<=a<0x11110:return
        engine.mem_write(a,script.read(a,w).to_bytes(w,'big'))
    def write(engine,t,a,w,v,_):
        if SP-40<=a<SP+4:return
        script.write(a,w,v&((1<<(8*w))-1))
    cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(0x11ad4,STOP,count=4000,timeout=1000000)
    assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
    memory=bytearray(cpu.mem_read(0,0x200000))
    for target in HELPERS:memory[target:target+2]=script.memory[target:target+2]
    assert memory[:SP-40]==script.memory[:SP-40]and memory[SP+4:]==script.memory[SP+4:]
    return cpu.reg_read(UC_M68K_REG_D0),steps
def translated(fn,tick,script,case,missing=None):
    w=animation.boundary.world;errors=[];tick_calls=[]
    def read(width):
        def f(_,a,out):
            try:out[0]=script.read(a,width);return 0
            except Exception as error:errors.append(repr(error));return 1
        return f
    def write(width):
        def f(_,a,value):
            try:script.write(a,width,value);return 0
            except Exception as error:errors.append(repr(error));return 1
        return f
    def call(_,target,args,count,out):
        try:
            if target==0x10968:
                assert count==2;script.trace.append(['call',target,list(args[:count]),out[0]])
                def byte_write(_,address,value):
                    try:script.write(address,1,value);return 0
                    except Exception as error:errors.append(repr(error));return 1
                callback=slot.W8(byte_write);slot_bus=slot.Bus(callback,None);result=c.c_uint32(out[0]);status=SLOT_FN(c.byref(slot_bus),args[0],args[1],c.byref(result))
                if not status:out[0]=result.value
                return status
            if target in [0x11384,0x110d4]:
                assert count==(0 if target==0x11384 else 3);script.trace.append(['call',target,list(args[:count]),out[0]]);value=c.c_uint32(out[0])
                status=PREPARE_FN(c.byref(bus),out[0],c.byref(value))if target==0x11384 else FACE_FN(c.byref(bus),args[0],args[1],args[2],c.byref(value))
                if not status:out[0]=value.value
                return status
            if target==0x10ba4:
                assert count==0;script.trace.append(['call',target,[],out[0]]);value=c.c_uint32(out[0]);status=tick(c.byref(bus),out[0],c.byref(value));tick_calls.append(status)
                if not status:out[0]=value.value
                return status
            assert target in HELPERS and count==(2 if target==0x10968 else 0)
            out[0]=script.call(target,list(args[:count]),out[0]);return 0
        except Exception as error:errors.append(repr(error));return 1
    callbacks=[w.R8(),w.R16(read(2)),w.R32(read(4)),w.W16(write(2)),w.W32(write(4)),w.CALL(call)]
    if missing is not None:callbacks[missing]=type(callbacks[missing])()
    bus=w.Bus(*callbacks,None,0);value=c.c_uint32(0xa55aa55a);status=fn(c.byref(bus),case['incoming'][0],c.byref(value));return status,value.value,errors,tick_calls
def main():
    global SLOT_FN,PREPARE_FN,FACE_FN
    proposal=json.loads((ROOT/'verification/local-global-scene-author-current.json').read_text());author_out=Path(proposal['directory']);source=author_out/'biwn_global_scene_prepare.c';out=author_out/'with-five-real-functions';out.mkdir(exist_ok=True);restoration=ROOT/'projects/black-ice-white-noise/restoration';component=json.loads((ROOT/'verification/local-global-animation-component-current.json').read_text());tick_source=Path(component['source']);assert hashlib.sha256(tick_source.read_bytes()).hexdigest()==component['source_sha256']
    slot_proof=json.loads((ROOT/'verification/local-slot-clear-checks-current.json').read_text());slot_source=Path(slot_proof['source']);assert hashlib.sha256(slot_source.read_bytes()).hexdigest()==slot_proof['source_sha256']
    prepare_proof=json.loads((ROOT/'verification/local-scene-slot-prepare-checks-current.json').read_text());prepare_source=Path(prepare_proof['source']);face_proof=json.loads((ROOT/'verification/local-face-coordinates-checks-current.json').read_text());face_source=Path(face_proof['source'])
    for proof,file in [(prepare_proof,prepare_source),(face_proof,face_source)]:assert hashlib.sha256(file.read_bytes()).hexdigest()==proof['source_sha256']
    inspection=subprocess.run(['clang','-std=c99','-I',str(restoration),'-fsyntax-only','-Xclang','-ast-dump=json',str(source)],capture_output=True,text=True);(out/'syntax.log').write_text(inspection.stderr);assert inspection.returncode==0,inspection.stderr
    tree=json.loads(inspection.stdout);functions=[n for n in tree['inner']if n['kind']=='FunctionDecl'and any(x['kind']=='CompoundStmt'for x in n.get('inner',[]))];names={n['name']for n in functions};assert 'biwn_global_scene_prepare'in names and all(n['name']=='biwn_global_scene_prepare'or n.get('storageClass')=='static'for n in functions)
    assert not any(n['kind']in ['VarDecl','FileScopeAsmDecl']for n in tree['inner'])
    def check(n):
        assert n['kind']not in ['GCCAsmStmt','MSAsmStmt'];assert n.get('castKind')not in ['IntegralToPointer','PointerToIntegral']
        if n.get('castKind')=='BitCast':
            node=n['inner'][0]
            while node['kind']=='ParenExpr':node=node['inner'][0]
            assert node.get('castKind')=='NullToPointer'
        if n['kind']=='CallExpr':
            node=n['inner'][0]
            while node['kind']in ['ImplicitCastExpr','ParenExpr']:node=node['inner'][0]
            assert(node['kind']=='MemberExpr'and node['name']in ['read16','read32','write16','write32','call'])or(node['kind']=='DeclRefExpr'and node['referencedDecl']['name']in names)
        for child in n.get('inner',[]):check(child)
    for f in functions:check(f)
    library=out/'libglobal-scene-prepare.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(restoration),str(source),str(tick_source),str(slot_source),str(prepare_source),str(face_source),'-o',str(library)];build=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
    lib=c.CDLL(str(library));fn=lib.biwn_global_scene_prepare;tick=lib.biwn_global_animation_tick
    for f in [fn,tick]:f.argtypes=[c.POINTER(animation.boundary.world.Bus),c.c_uint32,c.POINTER(c.c_uint32)];f.restype=c.c_int
    SLOT_FN=lib.biwn_slot_clear;SLOT_FN.argtypes=[c.POINTER(slot.Bus),c.c_uint16,c.c_uint16,c.POINTER(c.c_uint32)];SLOT_FN.restype=c.c_int
    PREPARE_FN=lib.biwn_scene_slot_prepare;PREPARE_FN.argtypes=[c.POINTER(animation.boundary.world.Bus),c.c_uint32,c.POINTER(c.c_uint32)];PREPARE_FN.restype=c.c_int
    FACE_FN=lib.biwn_face_coordinates;FACE_FN.argtypes=[c.POINTER(animation.boundary.world.Bus),c.c_uint32,c.c_uint32,c.c_uint16,c.POINTER(c.c_uint32)];FACE_FN.restype=c.c_int
    snapshot=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();rng=random.Random(0x11ad4);cases=[]
    for i,coordinates in enumerate(itertools.product([0xffffffdf,0xffffffe0,0,32,96,160,224,0xffffffff],repeat=3)):
        initial=[[address,4,value]for address,value in zip([0x40100,0x400f8,0x400fc],coordinates)]
        initial += [[0x3d7a2+n*2,2,(n+i)%8]for n in range(64)]
        initial += [[0x400e6,4,0x80000],[0x80090,2,i&65535],[0x403d4,2,[0,1,2,0x7fff,0x8000,0xffff][i%6]],[0x403d0,2,[0,1,0x7fff,0x8000,0xffff][i%5]],[0x403d2,2,[0,2,0x7fff,0x8000,0xffff][(i//5)%5]],[0x403da,2,[0,1,0x8000,0xffff][(i//25)%4]],[0x23f88,4,0x12345678],[0x23f8c,4,0x98765432]]
        index=[4,17,31][i%3];initial+=[[0x80000,2,index]]+[[0x400c4+(index<<5)+n*2,2,(i*991+n*313)&65535]for n in range(16)]
        effects={}
        # Real slot helper runs instead of the former scripted coordinate mutation.
        if i%13==0:effects[str(0x1142e)]=[[0x23f7c,4,0xbad00bad]]
        cases.append(dict(initial=initial,incoming=[rng.getrandbits(32)for _ in animation.boundary.REGS],helper_effects=effects,helper_returns={str(target):(0xa5a50000+i+target)&0xffffffff for target in HELPERS}))
    # Helper mutations deliberately alter some input cells. Add the complete
    # unmodified4x4x4 grid as a separate fixture family to cover every index.
    for coordinates in itertools.product([0xffffffe0,32,96,160],repeat=3):
        case=json.loads(json.dumps(cases[0]));case['helper_effects']={}
        for row,value in zip(case['initial'][:3],coordinates):row[2]=value
        cases.append(case)
    coverage=set();rows=[];table_addresses=set()
    for i,case in enumerate(cases):
        a=Script(snapshot,case);b=Script(snapshot,case);value,steps=original(a,case,coverage);status,actual,errors,ticks=translated(fn,tick,b,case)
        if status or value!=actual or a.trace!=b.trace or a.memory!=b.memory or ticks!=[0]:
            (out/'mismatch.json').write_text(json.dumps(dict(case=case,status=status,expected=value,actual=actual,original_trace=a.trace,C_trace=b.trace,errors=errors,tick_statuses=ticks),indent=2)+'\n');raise AssertionError(out/'mismatch.json')
        table_addresses.update(e[1]for e in b.trace if e[0]=='r'and 0x3d7a2<=e[1]<0x3d822)
        rows.append(dict(case=i,full_D0=value,steps=steps,trace=b.trace,parameters=case))
    guards=[]
    for missing in [1,2,3,4,5]:
        script=Script(snapshot,cases[0]);status,value,errors,ticks=translated(fn,tick,script,cases[0],missing=missing);assert status==1 and value==0xa55aa55a and not script.trace;guards.append(dict(missing=missing))
    for target in HELPERS:
        script=Script(snapshot,cases[0]);script.fail_call=target;status,value,errors,ticks=translated(fn,tick,script,cases[0]);assert status==3 and value==0xa55aa55a;guards.append(dict(dependency_failure=hex(target)))
    expected={int(pc,16)for name in [author_out/'evidence.json',Path(component['prompts_and_responses']).parent/'evidence.json',Path(slot_proof['directory'])/'evidence.json',Path(prepare_proof['directory'])/'evidence.json',Path(face_proof['directory'])/'evidence.json']for pc in re.findall(r'^([0-9a-fA-F]{8}):',json.loads(name.read_text())['assembly'],re.M)}
    (out/'coverage-review.json').write_text(json.dumps(dict(expected=len(expected),covered=len(coverage),uncovered=[hex(p)for p in sorted(expected-coverage)],unexpected=[hex(p)for p in sorted(coverage-expected)],grid_cells=len(table_addresses)),indent=2)+'\n')
    assert coverage==expected and len(table_addresses)==64,(len(coverage),len(expected),len(table_addresses))
    (out/'fixtures.json').write_text(json.dumps(rows,indent=2)+'\n')
    report=dict(status='local_five_function_scene_integration_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(rows),combined_instruction_address_coverage=[len(coverage),len(expected)],grid_cells=len(table_addresses),source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),tick_source=str(tick_source),tick_source_sha256=component['source_sha256'],coordinator_C_body_edits=False,coordinate_local_model_repair=True,prepare_local_model_repair=True,prepare_host_include_added=prepare_proof.get('host_include_added',False),prepare_source=str(prepare_source),prepare_source_sha256=prepare_proof['source_sha256'],face_source=str(face_source),face_source_sha256=face_proof['source_sha256'],slot_source=str(slot_source),slot_source_sha256=slot_proof['source_sha256'],remaining_scripted_helpers=[hex(t)for t in HELPERS],host_header_fix='Added standardstddef.h for NULL; original generated C body unchanged. Initial compiler log retained.',host_guards=guards,roles=[dict(role=d['role'],seconds=d['seconds'])for d in proposal['drafts']],full_route_runtime_promoted=False,new_training=False,native_Chat_verified=False,scope='Complete11AD4caller,10BA4animation,10968slotclear,11384slotsetup and110D4coordinates together versus originalUnicornM68000 across576synthetic fixtures and64gridcells. FullD0,logical data/helper accesses and external2MBRAM match. Helpers1142E/10734 remain scripted; nativebusdummyreads,code/tablefetch,CCR,otherregisters,private stack,timing,naturalgameplay and fullroute promotion excluded.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/local-five-function-scene-integration-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],report['cases'],report['combined_instruction_address_coverage'],report['grid_cells'])
if __name__=='__main__':main()
