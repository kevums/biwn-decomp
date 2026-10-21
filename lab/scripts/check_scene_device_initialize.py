"""Compare local18160 C with original ordered stores and pinned emulated devices."""
import ctypes as c,hashlib,json,os,random,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_local_global_animation_tick as animation
import check_biwn_memory_native as memory

ROOT=animation.ROOT;SP=animation.SP;STOP=animation.STOP;w=animation.boundary.world
sha=lambda b:hashlib.sha256(b).hexdigest()


class CoreMemory:
    """Use actual core MMIO handlers, including TOM registers outside the old bridge."""
    def __init__(self,runtime):
        self.runtime=runtime;self.readers={};self.writers={}
        for width in [2,4]:
            reader=getattr(runtime.core,'m68k_read_memory_'+str(width*8))
            reader.argtypes=[c.c_uint32];reader.restype=c.c_uint32
            writer=getattr(runtime.core,'m68k_write_memory_'+str(width*8))
            writer.argtypes=[c.c_uint32,c.c_uint32];writer.restype=None
            self.readers[width]=reader;self.writers[width]=writer
    def read(self,address,width):return self.readers[width](address)&((1<<(8*width))-1)
    def write(self,address,width,value):self.writers[width](address,value)


def original_stores(snapshot,incoming,coverage):
    cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    cpu.mem_map(0,0x200000);cpu.mem_map(0xf00000,0x10000)
    cpu.mem_write(0,snapshot);cpu.mem_write(SP,STOP.to_bytes(4,'big'))
    for reg,value in zip(animation.boundary.REGS,incoming):cpu.reg_write(reg,value)
    cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP)
    trace=[]
    def code(e,pc,width,_):assert 0x18160<=pc<=0x181d8;coverage.add(pc)
    def write(e,t,address,width,value,_):trace.append(['w',address,width,value&((1<<(8*width))-1)])
    cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_WRITE,write)
    cpu.emu_start(0x18160,STOP,count=100)
    assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
    return trace,cpu.reg_read(UC_M68K_REG_D0)


def translated(fn,fail=None,missing=None,nullbus=False,nullout=False,device=None):
    trace=[];errors=[]
    def write(width):
        def callback(_,address,value):
            if len(trace)==fail:return 1
            trace.append(['w',address,width,value])
            try:
                if device:device.write(address,width,value)
                return 0
            except Exception as error:errors.append(repr(error));return 1
        return callback
    callbacks=[w.R8(),w.R16(),w.R32(),w.W16(write(2)),w.W32(write(4)),w.CALL()]
    if missing is not None:callbacks[missing]=type(callbacks[missing])()
    bus=w.Bus(*callbacks,None,0);out=c.c_uint32(0xa55aa55a)
    status=fn(None if nullbus else c.byref(bus),None if nullout else c.byref(out))
    return status,out.value,trace,errors


def bind(source,out):
    restore=ROOT/'projects/black-ice-white-noise/restoration'
    syntax=subprocess.run(['clang','-std=c99','-I',str(restore),'-I',str(source.parent),
                           '-fsyntax-only','-Xclang','-ast-dump=json',str(source)],capture_output=True,text=True)
    (out/'syntax.log').write_text(syntax.stderr);assert not syntax.returncode,syntax.stderr
    tree=json.loads(syntax.stdout);functions=[n for n in tree['inner']if n['kind']=='FunctionDecl'and any(x.get('kind')=='CompoundStmt'for x in n.get('inner',[]))]
    assert len(functions)==1 and functions[0]['name']=='biwn_scene_device_initialize'
    assert not any(n['kind']in ['VarDecl','FileScopeAsmDecl']for n in tree['inner'])
    def check(node):
        assert node['kind']not in ['GCCAsmStmt','MSAsmStmt']
        assert node.get('castKind')not in ['IntegralToPointer','PointerToIntegral','BitCast']
        if node['kind']=='CallExpr':
            target=node['inner'][0]
            while target['kind']in ['ImplicitCastExpr','ParenExpr']:target=target['inner'][0]
            assert target['kind']=='MemberExpr'and target['name']in ['write16','write32']
        for child in node.get('inner',[]):check(child)
    check(functions[0])
    library=out/'libscene-device.dylib'
    build=subprocess.run(['clang','-std=c99','-dynamiclib','-O2','-Wall','-Wextra','-Werror',
                          '-I',str(restore),str(source),str(restore/'biwn_memory.c'),'-o',str(library)],
                         capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'compiler.log').write_text(build.stdout+build.stderr);assert not build.returncode,build.stderr
    fn=c.CDLL(str(library)).biwn_scene_device_initialize
    fn.argtypes=[c.POINTER(w.Bus),c.POINTER(c.c_uint32)];fn.restype=c.c_int
    return fn,library


def main():
    proposal=json.loads((ROOT/'verification/local-scene-device-initialize-author-current.json').read_text())
    source=Path(proposal['directory'])/'biwn_scene_device_initialize.c'
    out=ROOT/'verification/local-scene-device-initialize'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True);print(out,flush=True);fn,library=bind(source,out)
    snapshot=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes()
    evidence=json.loads((Path(proposal['directory'])/'evidence.json').read_text())
    expected={int(x['address'],16)for x in evidence['instructions']};coverage=set();rng=random.Random(0x18160)
    rows=[];guards=[];runtime=memory.Runtime(library);core_memory=CoreMemory(runtime)
    addresses=[(0xf02268,4),(0xf0226c,4),(0xf02200,4),(0xf02204,4),
               (0xf0220c,4),(0xf0223c,4),(0xf02238,4),(0x113060,2),
               (0xf00400,2),(0xf00402,2),(0xf00404,2),(0xf00406,2)]
    try:
        for case in range(16):
            incoming=[rng.getrandbits(32)for _ in animation.boundary.REGS]
            ram=bytearray(snapshot);ram[0xb29d0:0xb29d0+0x10000]=rng.randbytes(0x10000)
            ram[0x113060:0x113062]=rng.getrandbits(16).to_bytes(2,'big');ram[SP:SP+4]=STOP.to_bytes(4,'big')
            trace,value=original_stores(bytes(ram),incoming,coverage)
            status,actual,stores,errors=translated(fn)
            assert status==0 and value==actual==0 and stores==trace and not errors
            runtime.seed(bytes(ram));runtime.core.m68k_pulse_reset();runtime.core.m68k_set_irq(0)
            runtime.core.m68k_set_reg(17,0x2000)
            for i,v in enumerate(incoming):runtime.core.m68k_set_reg(i,v)
            runtime.core.m68k_set_reg(15,SP);runtime.core.m68k_set_reg(16,0x18160)
            steps=0;native_coverage=set()
            while runtime.core.m68k_get_reg(None,16)!=STOP and steps<100:
                pc=runtime.core.m68k_get_reg(None,16);assert pc in expected
                native_coverage.add(pc);runtime.core.m68k_execute(1);steps+=1
            assert runtime.core.m68k_get_reg(None,16)==STOP and runtime.core.m68k_get_reg(None,15)==SP+4
            assert runtime.core.m68k_get_reg(None,0)==0 and native_coverage==expected
            original_ram=runtime.device.ram();original_regs=[core_memory.read(a,width)for a,width in addresses]
            original_stats=runtime.device.stats()
            runtime.seed(bytes(ram));status,value,stores,errors=translated(fn,device=core_memory)
            assert status==0 and value==0 and not errors and runtime.device.ram()==original_ram
            assert [core_memory.read(a,width)for a,width in addresses]==original_regs
            assert runtime.device.stats()==original_stats
            rows.append(dict(case=case,source_buffer_sha256=sha(bytes(ram[0xb29d0:0xb29d0+0x10000])),
                             native_steps=steps,store_trace=stores,device_readbacks=original_regs,
                             RAM_sha256=sha(original_ram),device_stats=original_stats))
        assert coverage==expected
        trace=rows[0]['store_trace']
        for opts in [dict(missing=3),dict(missing=4),dict(nullbus=True),dict(nullout=True)]:
            status,value,stores,errors=translated(fn,**opts)
            assert status==1 and value==0xa55aa55a and not stores;guards.append(opts)
        for event in range(len(trace)):
            status,value,stores,errors=translated(fn,fail=event)
            assert status==2 and value==0xa55aa55a and stores==trace[:event]
            guards.append(dict(failed_store=event,prior_stores_retained=True))
    finally:runtime.close()
    report=dict(status='local_scene_device_initialize_original_and_pinned_device_match',
                recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),source=str(source),
                source_sha256=sha(source.read_bytes()),cases=len(rows),
                instruction_address_coverage=[len(expected),len(expected)],native_CPU_cases=len(rows),
                stores_per_case=len(rows[0]['store_trace']),host_guards=guards,
                core_path=str(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'),
                new_training=False,native_Chat_verified=False,natural_gameplay_integration_verified=False,
                scope='Complete18160..181D8 ordered RAM/MMIO stores and D0 versus bytechecked original Unicorn; '
                      '16 pinned JaguarCPU comparisons include full RAM, twelve register readbacks and device counters '
                      'using the same emulated blitter/video backend. Host pointer/callback/fault guards checked. '
                      'Other CPU registers/CCR, cycle timing, physical devices, global scheduler and natural gameplay excluded.')
    (out/'cases.json').write_text(json.dumps(rows,indent=2)+'\n');(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'verification/local-scene-device-initialize-checks-current.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'],len(rows),len(expected),'stores',report['stores_per_case'],'guards',len(guards),flush=True)


if __name__=='__main__':main()
