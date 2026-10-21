"""Full targeting caller and actual math against native and ordered Unicorn CPU."""
import argparse,ctypes as c,hashlib,json,os,random,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_targeting as prior
import check_biwn_camera_cpu as oracle
ROOT=oracle.ROOT;CPU=oracle.CPU;SP=oracle.SP;STOP=oracle.STOP;save=oracle.save
RANGES=[(0x20820,0x20a9c),(0xe540,0xe60a),(0x13440,0x134dc)]
NAMES=oracle.NAMES+['biwn_targeting_cpu.c']
class Runtime(oracle.Runtime):
    def __init__(self,library):
        super().__init__(library);self.ranges=RANGES;self.instruction_limit=200000
        self.native_rereads={pc:(0x49d68,2)for pc in [0x20974,0x2097c,0x20984,0x20996,0x2099e,0x209a8,0x209fc,0x20a2a]}
        self.native_rereads.update({pc:(0x49d6a,2)for pc in [0x209b8,0x209c0,0x209c8,0x209da,0x209e2,0x209ec,0x20a04,0x20a38]})
        fn=self.lib.biwn_targeting_cpu_call;fn.argtypes=[c.POINTER(oracle.live.world.Bus),c.POINTER(CPU),oracle.world_cpu.SERVICE,c.c_void_p];fn.restype=c.c_int
        self.fn=lambda bus,state,unused_write8,service,context:fn(bus,state,service,context)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opt=ap.parse_args();out=ROOT/'verification/biwn-targeting-cpu'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libtargeting-cpu.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(source/n)for n in NAMES]+['-o',str(library)]
    run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rng=random.Random(0x20820c0de);session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();assert prior.world.select.stage.digest(image)==prior.world.select.stage.STAGE_SHA
    for a,b in RANGES:assert snapshot[a:b]==image[a-0x4000:b-0x4000]
    vectors=[{**case,'initial':case['initial']+[[SP,4,STOP]],'registers':case['incoming']+[SP],'SR':rng.randrange(32)|((i%8)<<8)}for i,case in enumerate(prior.cases(snapshot))]
    if opt.limit:vectors=vectors[:opt.limit]+vectors[-2:]
    runtime=Runtime(library);rows=[];coverage=set()
    try:
        for i,case in enumerate(vectors):
            save(out/'status.json',{'status':'running','case':i});ram=bytes(prior.camera.Script(snapshot,case).memory)
            left,expected,old=runtime.native(ram,case,coverage);observed,observer,observed_info=runtime.unicorn(ram,case,coverage);right,actual,new=runtime.translated(ram,case)
            if new['status']or bytes(expected)!=bytes(actual)or bytes(observer)!=bytes(actual)or left!=right or observed!=right or observed_info['trace']!=new['trace']:
                save(out/'mismatch.json',{'case':i,'parameters':case,'CPU_original':oracle.live.prior.scheduler.cpu_dict(expected),'CPU_Unicorn':oracle.live.prior.scheduler.cpu_dict(observer),'CPU_C':oracle.live.prior.scheduler.cpu_dict(actual),'RAM_differences':[hex(j)for j,(x,y)in enumerate(zip(left,right))if x!=y][:100],'Unicorn_RAM_differences':[hex(j)for j,(x,y)in enumerate(zip(observed,right))if x!=y][:100],'original':old,'observer':observed_info,'rebuilt':new});raise AssertionError(str(out/'mismatch.json'))
            assert not new['device']['original_GPUExec1_calls']and not new['device']['game_frames_executed']
            rows.append({'case':i,'parameters':case,'CPU':oracle.live.prior.scheduler.cpu_dict(actual),'original':old,'rebuilt':new,'allCPU_privateframes_completeRAM_orderedbus_match':True})
        save(out/'fixtures.json',rows)
        if opt.limit:save(out/'status.json',{'status':'terminal_preflight','cases':len(rows)});print(json.dumps({'directory':str(out),'cases':len(rows)}));return
        decoded,_=prior.world.select.binary_tools.m68k_instructions(snapshot[0x20820:0x20a9c],0x20820);missing=[r for r in decoded if r['address']not in coverage];save(out/'decode.json',{'instructions':decoded,'uncovered':missing});assert not missing,[hex(r['address'])for r in missing]
        guards=[];case=vectors[0];ram=bytes(prior.camera.Script(snapshot,case).memory)
        for kwargs in [{'missing':i}for i in range(5)]+[{'null_bus':True},{'null_cpu':True},{'null_service':True},{'bad_pc':True},{'supervisor':True}]:
            _,_,result=runtime.translated(ram,case,**kwargs);assert result['status']==1 and result['CPU_unchanged']and not result['trace'];guards.append(kwargs)
        for fail in [('read',1),('read',2),('read',4),('write',2),('write',4),('helper',0x13440),('helper',0xe540),('helper',0xe588)]:
            # E588 also occurs inside direction13440. Failure injection here
            # targets the caller's service callback, so choose its own JSR.
            helper_pc=0x20950 if fail==('helper',0xe588)else fail[1]
            case=next(r['parameters']for r in rows if (fail[0]=='helper'and helper_pc in r['original']['steps'])or(fail[0]in ['read','write']and any(t[0]==('r'if fail[0]=='read'else'w')and t[2]==fail[1]for t in r['rebuilt']['trace'])))
            ram=bytes(prior.camera.Script(snapshot,case).memory);_,_,result=runtime.translated(ram,case,fail=fail);assert result['status']in [2,3]and result['CPU_unchanged'];guards.append({'failure':fail,'status':result['status']})
        report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'targeting_fullCPU_privateframes_actual_math_match_original','directory':str(out),'CPU_cases':len(rows),'CPU_instruction_coverage':[len(decoded),len(decoded)],'host_guards':len(guards),'new_components':0,'helper_scripts':[],
                'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in NAMES+[n.replace('.c','.h')for n in NAMES]},
                'matched':['Original native CPU and independent Unicorn observer match reconstructed fullCPU: allregisters/PC/SR/USP/SSP, complete2MBRAM, eight localbytes/elevenregistersave/privateJSRframes and ordered accesses.',
                           'Actual direction/multiply/division;40records, wrapped scores and first ties, rawindices/depth/range, partialD0, signedlowdistance radius, both cursor approach branches and changing rereads.'],
                'limits':['Usermode only; finite syntheticcandidate/matrixfixtures and controlledrereads, not real-scene target acquisition or visible crosshair. No original exceptions/timing/concurrency.',
                          'Already counted20820 gainsfullCPUinterface; no newcomponent. Hosterrors leaveCPUunchanged and retain earlierRAMeffects. Worldintegration/render/fullgame/hardware remain unfinished.'],
                'core_sha256':hashlib.sha256((ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib').read_bytes()).hexdigest(),'stage_sha256':prior.world.select.stage.STAGE_SHA,'compiler':command}
        save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-targeting-cpu-checks.json',report);print(json.dumps(report))
    except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
    finally:runtime.close()
if __name__=='__main__':main()
