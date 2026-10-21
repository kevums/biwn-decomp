"""Fresh native19/native21 diagnostic routes; normal pad/read-only observers."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,subprocess
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def main():
    bp=ROOT/'verification/native-heap-disc-build-current.json';build=json.loads(bp.read_text());ep=ROOT/'verification/native-heap-disc-entry-current.json';entry=json.loads(ep.read_text());assert entry['status']=='terminal_native_entry_heap_and_component_pass'and entry['build_proof_sha256']==sha(bp)
    for p,d in build['source_sha256'].items():assert sha(p)==d,p
    pp=ROOT/'verification/native-scheduler-route-current.json';previous=json.loads(pp.read_text());pd=Path(previous['directory']);template=pd/'fresh-scheduler-route.py';observer_template=pd/'scheduler-observer.c'
    for p in [template,observer_template]:assert sha(p)==previous['source_sha256'][str(p)]
    baseline_path=ROOT/'verification/native-scheduler-disc-build-current.json';baseline=json.loads(baseline_path.read_text());old_disc=Path(baseline['derived_disc']);new_disc=Path(build['derived_disc']);assert sha(old_disc)==baseline['derived_disc_sha256']and sha(new_disc)==build['derived_disc_sha256']
    out=ROOT/'verification/native-heap-route'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    host=observer_template.read_text();needle='static uint32_t heap_base;';assert host.count(needle)==1;host=host.replace(needle,needle+'\nstatic unsigned heap_native;\nstatic uint64_t heap_allocate_entries,heap_compact_entries,old_allocate_steps,old_compact_steps,native_C_allocate_calls,native_C_compact_calls,retained_copy_entries;')
    needle='scheduler_native=((unsigned)selected&8u)!=0;';assert host.count(needle)==1;host=host.replace(needle,needle+'heap_native=((unsigned)selected&16u)!=0;')
    assert baseline['symbols']['biwn_native_task_create']==build['symbols']['biwn_native_task_create']
    for symbol in ['biwn_native_scheduler_dispatch','biwn_native_scheduler_remove','biwn_native_scheduler_select','biwn_native_scheduler_rte']:
        old=baseline['symbols'][symbol];new=build['symbols'][symbol];needle=f'if(pc=={old})';assert host.count(needle)==1;host=host.replace(needle,f'if(pc==(heap_native?{new}:{old}))')
    needle='    steps++;';assert host.count(needle)==1;host=host.replace(needle,needle+f'''
    if(pc==0x152a2)heap_allocate_entries++;
    if(pc==0x15200)heap_compact_entries++;
    if(pc>0x152a2&&pc<0x1545c)old_allocate_steps++;
    if(pc>0x15200&&pc<0x152a2)old_compact_steps++;
    if(heap_native&&pc=={build['symbols']['biwn_native_heap_allocate_body']})native_C_allocate_calls++;
    if(heap_native&&pc=={build['symbols']['biwn_native_heap_compact_body']})native_C_compact_calls++;
    if(pc==0xe3e0)retained_copy_entries++;
''')
    needle='    array(file,"rng_entries",rng_entries,8);';assert host.count(needle)==1;host=host.replace(needle,'    fprintf(file,",\\"heap_native\\":%u,\\"heap_allocate_entries\\":%llu,\\"heap_compact_entries\\":%llu,\\"old_allocate_steps\\":%llu,\\"old_compact_steps\\":%llu,\\"native_C_allocate_calls\\":%llu,\\"native_C_compact_calls\\":%llu,\\"retained_copy_entries\\":%llu",heap_native,(unsigned long long)heap_allocate_entries,(unsigned long long)heap_compact_entries,(unsigned long long)old_allocate_steps,(unsigned long long)old_compact_steps,(unsigned long long)native_C_allocate_calls,(unsigned long long)native_C_compact_calls,(unsigned long long)retained_copy_entries);\n'+needle)
    source=out/'heap-observer.c';source.write_text(host);library=out/'libheap-observer.dylib';p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    lines=template.read_text().splitlines(keepends=True);changes=[]
    for i,line in enumerate(lines):
        if line.startswith('        observer=c.CDLL('):lines[i]='        observer=c.CDLL('+repr(str(library))+')\n';changes.append('observer_library')
        elif line.startswith('        observer_payload=c.create_string_buffer('):lines[i]='        observer_payload=c.create_string_buffer(Path('+repr(build['component'])+' if disc==Path('+repr(str(new_disc))+') else '+repr(baseline['component'])+').read_bytes())\n';changes.append('payload_signature')
        elif line.startswith('            (15 if disc==Path('):lines[i]='            (31 if disc==Path('+repr(str(new_disc))+') else 15),observer_payload,len(observer_payload.raw)-1,\n';changes.append('read_only_flags')
    assert len(changes)==3;probe=out/'fresh-heap-route.py';probe.write_text(''.join(lines));subprocess.run([str(ROOT/'.venv/bin/python'),'-m','py_compile',str(probe)],check=True)
    core=ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source/virtualjaguar_libretro.dylib';route=ROOT/'verification/normal-route-312-plan.json';post=ROOT/'verification/native-word-scan-clearance-long-route/20261018T053248.873269Z/merchant-corridor.json'
    for p in [core,route,post]:assert sha(p)==previous['source_sha256'][str(p)]
    lanes=dict(native19_repaired=str(old_disc),native21_repaired=str(new_disc));state=dict(status='prepared',pid=os.getpid(),directory=str(out),lanes=lanes,commands=[],build_proof=str(bp),build_proof_sha256=sha(bp),entry_proof=str(ep),entry_proof_sha256=sha(ep),prior_route_proof=str(pp),prior_route_proof_sha256=sha(pp),template_changes=changes,maximum_frames=35000,host_guest_RAM_writes=0,checkpoint_restores=0,host_CPU_seeds=0,source_execution_ownership=False,whole_game_complete=False,source_sha256={str(p):sha(p)for p in [Path(__file__),template,observer_template,source,library,probe,core,route,post]},input_policy=previous['input_policy'])
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-heap-route-active.json',state)
    mark();children=[]
    try:
        for lane,disc in lanes.items():
            command=[str(ROOT/'.venv/bin/python'),'-u',str(probe),'--boot','hle','--frames','35000','--core',str(core),'--disc',disc,'--navigate-waypoints',str(route),'--stop-after-scene-change','26000','--post-scene-navigate-actor','2','--post-scene-navigation-offset','1101','--post-scene-waypoints',str(post),'--capture-audio','--no-publish','--output',str(out/lane)]
            log=(out/(lane+'.log')).open('w');child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);children.append((lane,child,log));state['commands'].append(dict(lane=lane,pid=child.pid,command=command))
        state['status']='running_fresh_native19_native21_heap_routes';mark();print('PIDs',[p.pid for _,p,_ in children],flush=True);codes={}
        for lane,child,log in children:codes[lane]=child.wait();log.close()
        state['exit_codes']=codes;assert not any(codes.values()),codes;results={}
        for lane,_,_ in children:
            report=json.loads((out/lane/'report.json').read_text());rows=report['frames'];last=rows[-1];obs=json.loads((out/lane/'gameplay-observation.json').read_text());assert not(obs['errors']or obs['copy_errors']or obs['repair_code_errors']);assert obs['repair_code_checks']>0
            assert obs['old_rng_steps']==obs['old_keypad_steps']==obs['old_controller_steps']==obs['old_task_steps']==obs['old_scheduler_steps']==obs['old_remove_steps']==0
            if lane=='native21_repaired':assert obs['old_allocate_steps']==obs['old_compact_steps']==0 and obs['native_C_allocate_calls']>0 and obs['heap_base']==build['heap_start']
            else:assert obs['old_allocate_steps']>0 and obs['native_C_allocate_calls']==obs['native_C_compact_calls']==0
            returned=[x for x in rows if(x.get('navigation')or{}).get('return_started')]
            results[lane]=dict(executed_frames=report['executed_frames'],first_scene_change=report['scene_change_frame'],merchant_reached=any(x['player_mode_word']==2 and x['floor_word']==2 and x['scene_word']==314 and abs(x['raw_player_X']-12832)<=16 and abs(x['raw_player_Z']-42385)<=16 for x in rows),nonzero_audio_samples=report['audio']['nonzero_samples'],return_floor_values=sorted({x['floor_word']for x in returned}),completed_outdoor_hold=last['player_mode_word']==1 and(last.get('navigation')or{}).get('outdoor_hold',0)>=120,final_fields={k:last[k]for k in ['raw_player_X','raw_player_Z','player_mode_word','floor_word','scene_word']},last_navigation=last.get('navigation'),observation=obs,report_sha256=sha(out/lane/'report.json'))
        state.update(status='terminal_fresh_native19_native21_heap_routes_classified',results=results,finished_at=datetime.now(timezone.utc).isoformat());mark();save(ROOT/'verification/native-heap-route-current.json',state);print(json.dumps({k:{a:b for a,b in v.items()if a not in ['observation','last_navigation']}for k,v in results.items()},indent=2),flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
