"""Full world CPU caller with real E4C0 and pinned joystick device rows."""
import argparse,ctypes as c,hashlib,json,os,random,subprocess
from datetime import datetime,timezone
import check_biwn_world_cpu as base
ROOT=base.ROOT;save=base.save

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);opt=parser.parse_args()
    out=ROOT/'verification/biwn-world-input-cpu'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_world_cpu.c','biwn_input_poll_cpu.c'];library=out/'libworld-input-cpu.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(source/n)for n in names]+['-o',str(library)]
    result=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
    lib=c.CDLL(str(library));fn=base.bind(lib);poll=lib.biwn_input_poll_cpu_body;poll.argtypes=[c.POINTER(base.prior.Bus),c.POINTER(base.CPU)];poll.restype=c.c_int
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rng=random.Random(0x1a188f00d);vectors=[]
    for i,case in enumerate(base.prior.cases()):
        item=dict(case);item['initial']=case['initial']+[[base.SP,4,base.STOP]];item['registers']=[rng.getrandbits(32)for _ in range(15)]+[base.SP];item['SR']=(0x2000 if i%2 else 0)|((i%8)<<8)|rng.randrange(32);item['usp']=0x170000 if i%2 else base.SP;item['ssp']=base.SP if i%2 else 0x1d0000;item['clobber_seed']=rng.getrandbits(32);item['source']=snapshot;vectors.append(item)
    for bit in [19,18,17,7,6,5,4,3,2,1]:
        item=dict(vectors[1]);item['poll_inputs']=[1<<bit];vectors.append(item)
    item=dict(vectors[1]);item['poll_inputs']=[0x10];item['input_reads']=[0x10,0];vectors.append(item)
    if opt.limit:vectors=vectors[:opt.limit]
    native=base.Native();native.real_poll=True;coverage=set();rows=[]
    try:
        for i,case in enumerate(vectors):
            save(out/'status.json',{'status':'running','case':i})
            a=base.Script(snapshot,case);ram,expected,steps=native.original(a,case,coverage)
            b=base.Script(snapshot,case);b.enable_poll(native.device,native.lib,poll);status,actual,errors=base.translated(fn,b,case)
            u=base.Script(snapshot,case);u.enable_poll(native.device,native.lib,poll);sr=base.unicorn_original(u,case,coverage)
            if status or bytes(actual)!=bytes(expected)or ram!=b.memory or u.memory!=b.memory or u.trace!=b.trace or a.services!=b.services or sr!=actual.sr:
                save(out/'mismatch.json',{'case':i,'parameters':{k:v for k,v in case.items()if k!='source'},'status':status,'errors':errors,'CPU_original':base.scheduler.cpu_dict(expected),'CPU_C':base.scheduler.cpu_dict(actual),'Unicorn_SR':sr,'services_original':a.services,'services_C':b.services,'trace_original':u.trace,'trace_C':b.trace,'RAM_differences':[hex(j)for j,(x,y)in enumerate(zip(ram,b.memory))if x!=y][:100]});raise AssertionError(str(out/'mismatch.json'))
            timestep=int.from_bytes(b.memory[0x4c24c:0x4c250],'big')
            rows.append({'case':i,'parameters':{k:v for k,v in case.items()if k!='source'},'CPU':base.scheduler.cpu_dict(actual),'services':b.services,'trace':b.trace,'steps':[hex(a)for a in steps],
                         'world_generated_timestep':timestep,'pad_samples':b.pad.samples,'raw_pad_reads':b.pad.raw_reads,'pad_selects':b.pad.selects,'fullCPU_privateRAM_bus_and_native_pad_match':True})
    except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
    finally:native.close()
    save(out/'fixtures.json',rows)
    if opt.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'directory':str(out),'cases':len(rows)}));return
    decoded=[]
    for a,b in [(0x1a188,0x1a544),(0x1b718,0x1b780),(0xe4c0,0xe53c)]:part,_=base.prior.select.binary_tools.m68k_instructions(snapshot[a:b],a);decoded+=part
    missing=[r for r in decoded if r['address']not in coverage];save(out/'decode.json',{'instructions':decoded,'uncovered':missing});assert not missing
    guards=[]
    for null_bus,null_cpu in [(True,False),(False,True)]:
        bus=base.prior.Bus();cpu=base.cpu_for(vectors[1]);cpu.pc=0xe4c0;before=bytes(cpu);status=poll(None if null_bus else c.byref(bus),None if null_cpu else c.byref(cpu));assert status==1 and bytes(cpu)==before;guards.append({'null_bus':null_bus,'null_cpu':null_cpu})
    # The complete caller's23host guards remain in its separate fullCPU proof.
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'full_world_caller_with_actual_input_poll_CPU_matches_original_and_pad_rows',
            'directory':str(out),'CPU_cases':len(rows),'CPU_instruction_coverage':[len(decoded),len(decoded)],'world_caller_instructions':239,'digit_helper_instructions':42,'input_poll_instructions':len(decoded)-281,
            'input_poll_fullCPU_linked':True,'controller_backend':'Pinned VirtualJaguar actual joystick row select/read implementation','physical_controller_validated':False,
            'external_button_and_clock_samples':True,'world_caller_generates_timestep':True,'world_actor_task_ring_linked':False,
            'input_poll_calls':sum(len(r['pad_samples'])for r in rows),'raw_pad_reads':sum(len(r['raw_pad_reads'])for r in rows),'remaining_scripted_helpers':[hex(a)for a in base.TARGETS if a!=0xe4c0],
            'negative_timestep_cases':sum(r['world_generated_timestep']&0x80000000!=0 for r in rows),'clamped_timestep30_cases':sum(r['world_generated_timestep']==30 for r in rows),
            'new_components':0,'basic_input_interface_argument_guards':len(guards),'caller_host_guard_proof':str(ROOT/'verification/biwn-world-cpu-checks.json'),
            'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in names+[n.replace('.c','.h')for n in names]},
            'matched':['FullCPU/SR/USP/SSP, complete2MBRAM/private caller and input-poll frames, helper incoming fullstate and ordered CPU/stack/device accesses compare versus original native CPU and independent Unicorn bus execution.',
                       'Actual E4C0 row writes810E/810D/810B/8107 and hardware row reads produce held/newpressed edges, preserveD0-D2 and originalflags. Actual caller pause/selection/timing logic computes shared4C24C from external clock samples and previous46252, rather than a direct timestep script.'],
            'limits':['Eight other helper bodies remain synthetic scripts in this caller-interface proof. No actual GPU output, collision/camera/animation/targeting bodies or actor/task-ring/fullgame/hardware claim.',
                      'Button states/clock samples are controlled host inputs to the pinned emulator joystick; not physical controller or timing validation. One input reread and mode reread fixtures are controlled memory changes.',
                      'Bounded privateRAM/layouts/SRbits0x271f; original interrupt/tracing/cycle/exception behavior remains outside scope.'],
            'core_sha256':base.scheduler.cleanup.world.select.binary_tools.sha(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'),'compiler':command}
    save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-world-input-cpu-checks.json',report);print(json.dumps(report))

if __name__=='__main__':main()
