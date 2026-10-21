"""Fresh native15/native19 route comparison; retained CPU and read-only counts."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,subprocess
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def main():
    bp=ROOT/'verification/native-scheduler-disc-build-current.json';build=json.loads(bp.read_text());ep=ROOT/'verification/native-scheduler-disc-entry-current.json';entry=json.loads(ep.read_text())
    assert entry['status']=='terminal_native_entry_heap_and_component_pass'and entry['build_proof_sha256']==sha(bp)
    for p,d in build['source_sha256'].items():assert sha(p)==d,p
    previous_path=ROOT/'verification/native-task-create-route-current.json';previous=json.loads(previous_path.read_text());pd=Path(previous['directory']);template=pd/'fresh-task-route.py';observer_template=pd/'task-observer.c'
    for p in [template,observer_template]:assert sha(p)==previous['source_sha256'][str(p)]
    baseline_path=ROOT/'verification/native-task-create-disc-build-current.json';baseline=json.loads(baseline_path.read_text());old_disc=Path(baseline['derived_disc']);new_disc=Path(build['derived_disc'])
    assert sha(old_disc)==baseline['derived_disc_sha256']and sha(new_disc)==build['derived_disc_sha256']
    out=ROOT/'verification/native-scheduler-route'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    host=observer_template.read_text();needle='static uint32_t heap_base;';assert host.count(needle)==1
    host=host.replace(needle,needle+'\nstatic unsigned scheduler_native;\nstatic uint64_t scheduler_dispatch_entries,scheduler_remove_entries,scheduler_yield_entries,scheduler_remove_traps,old_scheduler_steps,old_remove_steps,native_dispatch_calls,native_remove_calls,native_C_select_calls,native_scheduler_RTEs;')
    needle='task_native=((unsigned)selected&4u)!=0;';assert host.count(needle)==1;host=host.replace(needle,needle+'scheduler_native=((unsigned)selected&8u)!=0;')
    old_task=baseline['symbols']['biwn_native_task_create'];new_task=build['symbols']['biwn_native_task_create']
    needle=f'if(task_native&&pc=={old_task})';assert host.count(needle)==1;host=host.replace(needle,f'if(task_native&&pc==(scheduler_native?{new_task}:{old_task}))')
    needle='    steps++;';assert host.count(needle)==1
    host=host.replace(needle,needle+f'''
    if(pc==0xde08)scheduler_dispatch_entries++;
    if(pc==0xdeb6)scheduler_remove_entries++;
    if(pc==0xdf60)scheduler_yield_entries++;
    if(pc==0xdf7a)scheduler_remove_traps++;
    if(pc>0xde08&&pc<0xde5c)old_scheduler_steps++;
    if(pc>0xdeb6&&pc<0xdee2)old_remove_steps++;
    if(scheduler_native){{
        if(pc=={build['symbols']['biwn_native_scheduler_dispatch']})native_dispatch_calls++;
        if(pc=={build['symbols']['biwn_native_scheduler_remove']})native_remove_calls++;
        if(pc=={build['symbols']['biwn_native_scheduler_select']})native_C_select_calls++;
        if(pc=={build['symbols']['biwn_native_scheduler_rte']})native_scheduler_RTEs++;
    }}
''')
    needle='    if(events&&fclose(events))errors++;';assert host.count(needle)==1;host=host.replace(needle,'    if(candidate&&memcmp(ram+0x15edc0,payload,payload_size))copy_errors++;\n'+needle)
    needle='    array(file,"rng_entries",rng_entries,8);';assert host.count(needle)==1
    host=host.replace(needle,'    fprintf(file,",\\"scheduler_native\\":%u,\\"scheduler_dispatch_entries\\":%llu,\\"scheduler_remove_entries\\":%llu,\\"scheduler_yield_entries\\":%llu,\\"scheduler_remove_traps\\":%llu,\\"old_scheduler_steps\\":%llu,\\"old_remove_steps\\":%llu,\\"native_dispatch_calls\\":%llu,\\"native_remove_calls\\":%llu,\\"native_C_select_calls\\":%llu,\\"native_scheduler_RTEs\\":%llu",scheduler_native,(unsigned long long)scheduler_dispatch_entries,(unsigned long long)scheduler_remove_entries,(unsigned long long)scheduler_yield_entries,(unsigned long long)scheduler_remove_traps,(unsigned long long)old_scheduler_steps,(unsigned long long)old_remove_steps,(unsigned long long)native_dispatch_calls,(unsigned long long)native_remove_calls,(unsigned long long)native_C_select_calls,(unsigned long long)native_scheduler_RTEs);\n'+needle)
    source=out/'scheduler-observer.c';source.write_text(host);library=out/'libscheduler-observer.dylib';p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    lines=template.read_text().splitlines(keepends=True);changed=[]
    for i,line in enumerate(lines):
        if line.startswith('        observer=c.CDLL('):lines[i]='        observer=c.CDLL('+repr(str(library))+')\n';changed.append('observer_library')
        elif line.startswith('        observer_payload=c.create_string_buffer('):lines[i]='        observer_payload=c.create_string_buffer(Path('+repr(build['component'])+' if disc==Path('+repr(str(new_disc))+') else '+repr(baseline['component'])+').read_bytes())\n';changed.append('read_only_payload_signature')
        elif line.startswith('            (7 if disc==Path('):lines[i]='            (15 if disc==Path('+repr(str(new_disc))+') else 7),observer_payload,len(observer_payload.raw)-1,\n';changed.append('read_only_observer_flags')
    assert len(changed)==3
    probe=out/'fresh-scheduler-route.py';probe.write_text(''.join(lines));subprocess.run([str(ROOT/'.venv/bin/python'),'-m','py_compile',str(probe)],check=True)
    core=ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source/virtualjaguar_libretro.dylib';route=ROOT/'verification/normal-route-312-plan.json';post=ROOT/'verification/native-word-scan-clearance-long-route/20261018T053248.873269Z/merchant-corridor.json'
    for p in [core,route,post]:assert sha(p)==previous['source_sha256'][str(p)]
    lanes=dict(native15_repaired=str(old_disc),native19_repaired=str(new_disc));state=dict(status='prepared',directory=str(out),pid=os.getpid(),lanes=lanes,commands=[],build_proof=str(bp),build_proof_sha256=sha(bp),entry_proof=str(ep),entry_proof_sha256=sha(ep),prior_route_proof=str(previous_path),prior_route_proof_sha256=sha(previous_path),template_changes=changed,maximum_frames=35000,host_guest_RAM_writes=0,checkpoint_restores=0,host_CPU_seeds=0,source_execution_ownership=False,whole_game_complete=False,source_sha256={str(p):sha(p)for p in [Path(__file__),template,observer_template,source,library,probe,core,route,post]},input_policy=previous['input_policy'])
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-scheduler-route-active.json',state)
    mark();children=[]
    try:
        for lane,disc in lanes.items():
            command=[str(ROOT/'.venv/bin/python'),'-u',str(probe),'--boot','hle','--frames','35000','--core',str(core),'--disc',disc,'--navigate-waypoints',str(route),'--stop-after-scene-change','26000','--post-scene-navigate-actor','2','--post-scene-navigation-offset','1101','--post-scene-waypoints',str(post),'--capture-audio','--no-publish','--output',str(out/lane)]
            log=(out/(lane+'.log')).open('w');child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);children.append((lane,child,log));state['commands'].append(dict(lane=lane,pid=child.pid,command=command))
        state['status']='running_fresh_native15_native19_scheduler_routes';mark();print('PIDs',[p.pid for _,p,_ in children],flush=True)
        codes={}
        for lane,child,log in children:codes[lane]=child.wait();log.close()
        state['exit_codes']=codes;assert not any(codes.values()),codes;results={}
        for lane,_,_ in children:
            report=json.loads((out/lane/'report.json').read_text());rows=report['frames'];last=rows[-1];obs=json.loads((out/lane/'gameplay-observation.json').read_text())
            assert not(obs['errors']or obs['copy_errors']or obs['repair_code_errors']);assert obs['repair_code_checks']>0
            assert obs['old_rng_steps']==obs['old_keypad_steps']==obs['old_controller_steps']==obs['old_task_steps']==0
            if lane=='native19_repaired':assert obs['old_scheduler_steps']==obs['old_remove_steps']==0 and obs['native_C_select_calls']>0
            else:assert obs['old_scheduler_steps']>0 and obs['native_C_select_calls']==0
            returned=[x for x in rows if(x.get('navigation')or{}).get('return_started')]
            results[lane]=dict(executed_frames=report['executed_frames'],first_scene_change=report['scene_change_frame'],merchant_reached=any(x['player_mode_word']==2 and x['floor_word']==2 and x['scene_word']==314 and abs(x['raw_player_X']-12832)<=16 and abs(x['raw_player_Z']-42385)<=16 for x in rows),nonzero_audio_samples=report['audio']['nonzero_samples'],return_floor_values=sorted({x['floor_word']for x in returned}),outdoor_after_return=any(x['player_mode_word']==1 for x in returned),completed_outdoor_hold=last['player_mode_word']==1 and(last.get('navigation')or{}).get('outdoor_hold',0)>=120,final_fields={k:last[k]for k in ['raw_player_X','raw_player_Z','player_mode_word','floor_word','scene_word']},last_navigation=last.get('navigation'),observation=obs,report_sha256=sha(out/lane/'report.json'))
        state.update(status='terminal_fresh_native15_native19_scheduler_routes_classified',results=results,finished_at=datetime.now(timezone.utc).isoformat());mark();save(ROOT/'verification/native-scheduler-route-current.json',state);print(json.dumps({k:{a:b for a,b in v.items()if a not in ['observation','last_navigation']}for k,v in results.items()},indent=2),flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
