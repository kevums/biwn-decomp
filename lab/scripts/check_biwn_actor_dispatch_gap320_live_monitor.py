"""Qualify live dispatcher ABI oracle on both complete native fixture lanes."""
import ctypes as c,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_native_actor_dispatch_gap320 as e
ROOT=e.ROOT
class CPU(c.Structure):_fields_=[('r',c.c_uint32*16),('pc',c.c_uint32),('usp',c.c_uint32),('ssp',c.c_uint32),('sr',c.c_uint16)]
def main():
    bp=ROOT/'verification/native-actor-dispatch-gap320-disc-build-current.json';build=e.g.read(bp);proof=e.g.read(build['component_gate']);assert proof['cases']==856
    out=ROOT/'verification/native-actor-dispatch-gap320-monitor'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    payload=Path(proof['binary']).read_bytes();symbols=proof['symbols'];e.BASE=proof['code_address'];parent=e.g.read(build['parent_build']);e.PARENT_RANGE=(parent['resident_address'],parent['resident_address']+parent['linked_component_bytes'])
    snapshot=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());snapshot[0x4000:0x100000]=Path(parent['derived_stage']).read_bytes();snapshot[parent['resident_address']:parent['resident_address']+parent['component_bytes']]=Path(parent['component']).read_bytes();snapshot=bytes(snapshot)
    returns={}
    for name,target in [('actor',0x134dc),('sprite',0x137e0)]:
        opcode=b'\x4e\xb9'+target.to_bytes(4,'big');assert payload.count(opcode)==1;returns[name]=e.BASE+payload.index(opcode)+6
    source=ROOT/'scripts/native_actor_dispatch_gap320_observer.inc.c';text=source.read_text()
    replacements={'__AD_ENTRY__':build['actor_dispatch_entry'],'__AD_START__':build['actor_dispatch_start'],'__AD_END__':build['actor_dispatch_end'],'__AD_RETURN__':build['actor_dispatch_return'],'__AD_ACTOR_CHILD_RETURN__':returns['actor'],'__AD_SPRITE_CHILD_RETURN__':returns['sprite']}
    for key,value in replacements.items():assert key in text;text=text.replace(key,str(value)+'u')
    header='''#include <stdint.h>
#include <string.h>
struct cpu {uint32_t r[16],pc,usp,ssp;uint16_t sr;};
static const unsigned char *ram;static unsigned errors;static void(*read_cpu)(struct cpu*);
#define BIWN_ACTOR_DISPATCH_TASK() (0x1ff000u-0x404u)
static uint32_t rd16(uint32_t a){if(a>0x1ffffe){errors++;return 0;}return ((uint32_t)ram[a]<<8)|ram[a+1];}
static uint32_t rd32(uint32_t a){if(a>0x1ffffc){errors++;return 0;}return(rd16(a)<<16)|rd16(a+2);}
static void emit(uint32_t pc){(void)pc;}
'''
    footer='''
void begin(const void*m,void*reader){ram=m;read_cpu=(void(*)(struct cpu*))reader;memset(ad_calls,0,sizeof(ad_calls));ad_slots=ad_pending=errors=0;ad_entries=ad_native_entries=ad_returns=ad_old_steps=ad_native_steps=ad_errors=ad_child_entries=ad_child_returns=ad_actor=ad_sprite=ad_full=ad_stack_observations=ad_stack_outside=0;ad_max_depth=ad_max_child_depth=0;ad_context_collisions=0;ad_min_context_clearance=ad_min_headroom=0xffffffffu;}
void step(uint32_t pc){watch_actor_dispatch(pc);}
unsigned collisions(void){return(unsigned)ad_context_collisions;}
unsigned check(void){return (unsigned)ad_context_collisions+errors+(unsigned)ad_errors+(unsigned)ad_stack_outside+ad_pending+(ad_entries!=1)+(ad_returns!=1);}
'''
    cpp=out/'monitor.c';cpp.write_text(header+text+footer);library=out/'monitor.dylib';p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(cpp),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'build.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    monitor=c.CDLL(str(library));monitor.begin.argtypes=[c.c_void_p,c.c_void_p];monitor.step.argtypes=[c.c_uint32];monitor.check.restype=c.c_uint32;monitor.collisions.restype=c.c_uint32
    n=e.Native();override=None;negative=None;injected=False
    def cpu_state():
        cpu=CPU();cpu.r[:]=[n.lib.m68k_get_reg(None,i)for i in range(16)];cpu.pc=n.lib.m68k_get_reg(None,16);cpu.sr=n.lib.m68k_get_reg(None,17);cpu.usp=n.prefix[16]if cpu.sr&0x2000 else cpu.r[15];cpu.ssp=cpu.r[15]if cpu.sr&0x2000 else n.prefix[17];return cpu
    def reader(target):
        cpu=override or cpu_state();c.memmove(target,c.byref(cpu),c.sizeof(cpu))
    callback=c.CFUNCTYPE(None,c.POINTER(CPU))(reader);old_seed=n.device.seed;old_execute=n.lib.m68k_execute
    def seed(*args):
        old_seed(*args);monitor.begin(n.device.pointer,c.cast(callback,c.c_void_p))
    def step(cycles):
        nonlocal override,injected
        pc=n.lib.m68k_get_reg(None,16)
        if negative and not injected and ((negative=='return_D0'and pc==build['actor_dispatch_return'])or(negative=='child_X'and pc in [0x134dc,0x137e0])or(negative=='context_overlap'and pc in [0x134e0,0x137e4])):
            override=cpu_state()
            if negative=='return_D0':override.r[0]^=1
            elif negative=='child_X':override.sr^=16
            else:
                override.r[15]=e.SP-265
                if override.sr&0x2000:override.ssp=override.r[15]
                else:override.usp=override.r[15]
            injected=True
        watch=pc in [0x13ae0,0x134dc,0x137e0,0x13b3a,0x13b50,0x13b58,build['actor_dispatch_return'],returns['actor'],returns['sprite']]
        before=n.device.ram()if watch else None
        monitor.step(pc);override=None
        if watch:assert n.device.ram()==before,'Live oracle wrote RAM'
        return old_execute(cycles)
    n.device.seed=seed;n.lib.m68k_execute=step
    rows=e.vectors();checks=[];negatives=[];state=dict(status='qualifying_actor_dispatch_live_oracle',directory=str(out),planned=len(rows)*2,completed=0)
    def mark():e.g.save(out/'protocol.json',state);e.g.save(ROOT/'verification/native-actor-dispatch-gap320-monitor-active.json',state)
    mark()
    try:
        for i,case in enumerate(rows):
            for compiled in [False,True]:
                expected=e.execute(snapshot,case,payload,symbols,compiled);e.replay(n,snapshot,case,payload,symbols,compiled,expected);error=monitor.check()
                assert error==0,('Monitor fixture',i,compiled,error)
                checks.append(dict(index=i,compiled=compiled,passed=True));state['completed']=len(checks)
            if i==0:
                for negative in ['return_D0','child_X','context_overlap']:
                    injected=False;expected=e.execute(snapshot,case,payload,symbols,True);e.replay(n,snapshot,case,payload,symbols,True,expected);assert injected and monitor.check()>0,negative
                    
                    if negative=='context_overlap':assert monitor.collisions()==monitor.check()==1,'Collision-only negative must hit the exact context guard'
                    negatives.append(dict(defect=negative,rejected=True));negative=None
            if i%64==0:mark();print('Dispatcher oracle',i+1,'/',len(rows),flush=True)
        paths=[Path(__file__),source,cpp,library,bp,Path(build['component_gate']),Path(e.__file__),ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib']
        state.update(status='terminal_actor_dispatch_live_oracle_fixtures_pass',original_cases=len(rows),compiled_cases=len(rows),negative_controls=negatives,capture_return_addresses=returns,source_sha256={str(p):e.g.sha(p)for p in paths},scope=__doc__,limitations='Stable entry flags/pool prediction; actual original children/leaf scripts in fixtures. Live children must execute real helpers separately. Read-only RAM guards at watched boundaries; fixture task-ID macro changes context association only. Private-gap actual external-helper stack depth is not established by fixture scripts.')
        e.g.save(out/'results.json',checks);mark();e.g.save(ROOT/'verification/native-actor-dispatch-gap320-monitor-current.json',state);print(state['status'],len(rows),flush=True)
    except BaseException as error:state.update(status='terminal_actor_dispatch_live_oracle_failed',error=repr(error),completed=len(checks));mark();raise
    finally:n.lib.m68k_execute=old_execute;n.close()

if __name__=='__main__':main()
