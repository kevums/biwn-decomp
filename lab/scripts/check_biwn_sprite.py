"""OriginalE2B8 CPU mailbox wrapper versus C, with scripted GPU replies."""
import ctypes as c
from datetime import datetime,timezone
import hashlib,itertools,json,os,random,subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_gpu_commands as prior
ROOT=prior.stage.ROOT;SP=prior.SP;STOP=prior.STOP
REGS=[UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6]

def original(image,script,args,incoming):
    cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_map(0xf03000,0x1000);cpu.mem_write(0x4000,image)
    cpu.mem_write(SP,STOP.to_bytes(4,'big')+b''.join(x.to_bytes(4,'big')for x in args));cpu.reg_write(UC_M68K_REG_A7,SP)
    for reg,value in zip(REGS,incoming):cpu.reg_write(reg,value)
    steps=[];stack=[]
    def code(engine,address,size,_):
        assert 0xe098<=address<0xe0a6 or 0xe2b8<=address<0xe2f4,hex(address)
        steps.append(address)
    def read(engine,access,address,size,value,_):
        if 0xf03000<=address<0xf04000:assert size==4;engine.mem_write(address,script.read(address).to_bytes(4,'big'))
    def write(engine,access,address,size,value,_):
        if 0xf03000<=address<0xf04000:assert size==4;script.write(address,value&0xffffffff)
        else:assert address==SP-4 and size==4;stack.append((address,value))
    cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write)
    cpu.emu_start(0xe2b8,STOP,count=512,timeout=1_000_000)
    assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
    assert stack==[(SP-4,0xe2be),(SP-4,0xe2f2)]
    for reg,value in zip(REGS,incoming):assert cpu.reg_read(reg)==value
    for address,value in script.memory.items():assert int.from_bytes(cpu.mem_read(address,4),'big')==value
    return {'instructions':len(steps),'all_D0_D7_A0_A6_preserved':True,'RTS_private_stack_checked':True}

def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();assert prior.stage.digest(image)==prior.stage.STAGE_SHA
    out=ROOT/'verification/biwn-sprite'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libbiwn_sprite.dylib';command=['clang','-dynamiclib','-std=c11','-Wall','-Wextra','-Werror','-O2',str(source/'biwn_gpu_commands.c'),'-o',str(library)];subprocess.run(command,check=True,capture_output=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    lib=c.CDLL(str(library));fn=lib.biwn_gpu_submit_4b00;fn.argtypes=[c.POINTER(prior.Bus),c.c_uint32,c.c_uint32,c.c_uint32];fn.restype=c.c_int
    rng=random.Random(0xe2b8);rows=[]
    for pre_n,ack_n,post_n,ack in itertools.product(range(4),range(4),range(4),[0,0xffffffff,0x80000000,0x4b01]):
        args=[rng.getrandbits(32)for _ in range(3)];pre=[rng.getrandbits(32)or 1 for _ in range(pre_n)]+[0];pending=[0x4b00]*ack_n+[ack];post=[rng.getrandbits(32)or 1 for _ in range(post_n)]+[0]
        a=prior.Script(0x4b00,pre,pending,post,[]);CPU=original(image,a,args,[rng.getrandbits(32)for _ in REGS]);b=prior.Script(0x4b00,pre,pending,post,[])
        status,budget=prior.translated(lambda bus:fn(bus,*args),b);assert status==0 and not b.errors and a.complete()and b.complete()and a.trace==b.trace and a.memory==b.memory
        assert [(a,v)for kind,a,v in b.trace if kind=='w']==[(0xf0320c,args[0]),(0xf03210,args[1]),(0xf03214,args[2]),(0xf03204,0x4b00)]
        rows.append({'args':args,'CPU':CPU,'trace':a.trace,'remaining_budget':budget})
    guards=[];assert fn(None,0,0,0)==1;guards.append({'case':'null_bus','status':1})
    for name,budget,fail_read,fail_write in [('missing_read',128,None,None),('missing_write',128,None,None),('zero_budget',0,None,None),('ack_budget',1,None,None),('post_budget',2,None,None),('initial_read_failure',128,0xf03200,None),('ack_failure',128,0xf03204,None),('post_failure',128,0xf03200,None)]+[('write_failure_'+hex(a),128,None,a)for a in [0xf0320c,0xf03210,0xf03214,0xf03204]]:
        script=prior.Script(0x4b00,[0],[0],[0],[]);script.fail_read=fail_read;script.fail_write=fail_write
        if name=='post_failure':script.fail_read_phase='post'
        result,remaining=prior.translated(lambda bus:fn(bus,0x6e6a0,0xffffffff,0x10a688),script,budget,missing_read=name=='missing_read',missing_write=name=='missing_write')
        expected=1 if name.startswith('missing')else 2 if 'budget'in name else 3;assert result==expected,(name,result)
        guards.append({'case':name,'status':result,'trace':script.trace,'remaining_budget':remaining,'errors':script.errors})
    (out/'fixtures.json').write_text(json.dumps(rows,indent=2)+'\n');(out/'guards.json').write_text(json.dumps(guards,indent=2)+'\n')
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'whole_sprite_CPU_mailbox_protocol_matches_portable_C','directory':str(out),'stage_sha256':prior.stage.STAGE_SHA,'portable_components':1,'CPU_cases':len(rows),'host_guard_cases':len(guards),'original_interval':'[0xe2b8,0xe2f4)','original_bytes_sha256':hashlib.sha256(image[0xe2b8-0x4000:0xe2f4-0x4000]).hexdigest(),'matched':['All scripted read/write addresses,values,order.','All15D/A registers preserved and originalprivate-stackRTSreturn.','Initial and final idle waits, acknowledgement !=4B00includingnonzero unequalvalues.'],
            'excluded':['Actual GPU4B00work/spritepixels,device timing,races outside scripted schedules,hardware and whole-game equivalence.','Original condition codes. Hoststatus/readbudgets/callbackerrors are addedbehavior, partialeffects remain.'],
            'source_sha256':{n:prior.binary_tools.sha(source/n)for n in ['biwn_gpu_commands.c','biwn_gpu_commands.h']},'compiler':command}
    n,row=next((i,z)for i,z in enumerate(rows)if any(t[0]=='r'and t[1]==0xf03204 and t[2]==0xffffffff for t in z['trace']));assert row['trace'][-1]==('r',0xf03200,0)
    report['checked_examples']={'nonzero_unequal_ack':{'ack_value':'0xffffffff','published_command':'0x00004b00','CPU_returned':True,'final_idle_read':'0x00000000','rule':'Poll while acknowledgement equals4B00; continue when unequal, then wait foridle0.','source_fixture':str(out/'fixtures.json'),'row_index':n,'trace':row['trace']}}
    for p in [out/'report.json',ROOT/'verification/biwn-sprite-checks.json']:p.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)

if __name__=='__main__':main()
