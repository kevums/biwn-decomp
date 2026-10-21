"""Fresh native23/native25 diagnostic routes with pad/read-only observation."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,re,subprocess
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def main():
    bp=ROOT/'verification/native-free-disc-build-current.json';build=json.loads(bp.read_text())
    ep=ROOT/'verification/native-free-disc-entry-current.json';entry=json.loads(ep.read_text());assert entry['status']=='terminal_native_entry_heap_and_component_pass'and entry['build_proof_sha256']==sha(bp)
    for p,d in build['source_sha256'].items():assert sha(p)==d,p
    pp=ROOT/'verification/native-copy-route-current.json';previous=json.loads(pp.read_text());pd=Path(previous['directory']);template=pd/'fresh-copy-route.py';observer_template=pd/'copy-observer.c'
    for p in [template,observer_template]:assert sha(p)==previous['source_sha256'][str(p)]
    baseline_path=ROOT/'verification/native-copy-disc-build-current.json';baseline=json.loads(baseline_path.read_text());old_disc=Path(baseline['derived_disc']);new_disc=Path(build['derived_disc'])
    assert sha(old_disc)==baseline['derived_disc_sha256']and sha(new_disc)==build['derived_disc_sha256']
    out=ROOT/'verification/native-free-route'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    host=observer_template.read_text();needle='static unsigned copy_native;';assert host.count(needle)==1
    host=host.replace(needle,needle+'\nstatic unsigned free_native;\nstatic uint64_t free_entries,old_free_body_steps,native_C_free_calls,initialize_entries,old_initialize_body_steps,native_initialize_calls;')
    needle='copy_native=((unsigned)selected&32u)!=0;';assert host.count(needle)==1;host=host.replace(needle,needle+'free_native=((unsigned)selected&64u)!=0;')
    replacements={
     'native_C_allocate_calls':('biwn_native_heap_allocate_body','heap_native&&'),
     'native_C_compact_calls':('biwn_native_heap_compact_body','heap_native&&'),
     'native_dispatch_calls':('biwn_native_scheduler_dispatch',''),
     'native_remove_calls':('biwn_native_scheduler_remove',''),
     'native_C_select_calls':('biwn_native_scheduler_select',''),
     'native_scheduler_RTEs':('biwn_native_scheduler_rte',''),
     'native_task_entries':('biwn_native_task_create','task_native&&'),
     'native_C_copy_entry_observations':('biwn_native_copy_body','copy_native&&')}
    for counter,(symbol,prefix)in replacements.items():
        old=baseline['symbols'][symbol];new=build['symbols'][symbol]
        pattern=r'if\([^\n;]*\)'+re.escape(counter)+r'\+\+;'
        host,count=re.subn(pattern,f'if({prefix}pc==(free_native?{new}:{old})){counter}++;',host);assert count==1,(counter,count)
    needle='    steps++;';assert host.count(needle)==1;host=host.replace(needle,needle+f'''
    if(pc==0x1545c)free_entries++;
    if(pc>0x1545c&&pc<0x1557a)old_free_body_steps++;
    if(free_native&&pc=={build['symbols']['biwn_native_free_body']})native_C_free_calls++;
    if(pc==0x1557a)initialize_entries++;
    if(pc>0x1557a&&pc<0x155c2)old_initialize_body_steps++;
    if(free_native&&pc=={build['symbols']['biwn_native_heap_initialize']})native_initialize_calls++;
''')
    needle='if(pc==0x155c0){heap_inits++;heap_base=rd32(0x112d60);}';assert host.count(needle)==1
    host=host.replace(needle,f"if(pc==(free_native?{build['symbols']['biwn_native_heap_initialize_return']}:0x155c0)){{heap_inits++;heap_base=rd32(0x112d60);}}")
    needle='    array(file,"rng_entries",rng_entries,8);';assert host.count(needle)==1
    host=host.replace(needle,'    fprintf(file,",\\"free_native\\":%u,\\"free_entries\\":%llu,\\"old_free_body_steps\\":%llu,\\"native_C_free_calls\\":%llu,\\"initialize_entries\\":%llu,\\"old_initialize_body_steps\\":%llu,\\"native_initialize_calls\\":%llu",free_native,(unsigned long long)free_entries,(unsigned long long)old_free_body_steps,(unsigned long long)native_C_free_calls,(unsigned long long)initialize_entries,(unsigned long long)old_initialize_body_steps,(unsigned long long)native_initialize_calls);\n'+needle)
    source=out/'free-observer.c';source.write_text(host);library=out/'libfree-observer.dylib'
    p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    lines=template.read_text().splitlines(keepends=True);changes=[]
    for i,line in enumerate(lines):
        if line.startswith('        observer=c.CDLL('):lines[i]='        observer=c.CDLL('+repr(str(library))+')\n';changes.append('observer_library')
        elif line.startswith('        observer_payload=c.create_string_buffer('):lines[i]='        observer_payload=c.create_string_buffer(Path('+repr(build['component'])+' if disc==Path('+repr(str(new_disc))+') else '+repr(baseline['component'])+').read_bytes())\n';changes.append('payload_signature')
        elif line.startswith('            (63 if disc==Path('):lines[i]='            (127 if disc==Path('+repr(str(new_disc))+') else 63),observer_payload,len(observer_payload.raw)-1,\n';changes.append('read_only_flags')
    assert len(changes)==3;probe=out/'fresh-free-route.py';probe.write_text(''.join(lines));subprocess.run([str(ROOT/'.venv/bin/python'),'-m','py_compile',str(probe)],check=True)
    core=ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source/virtualjaguar_libretro.dylib';route=ROOT/'verification/normal-route-312-plan.json';post=ROOT/'verification/native-word-scan-clearance-long-route/20261018T053248.873269Z/merchant-corridor.json'
    for p in [core,route,post]:assert sha(p)==previous['source_sha256'][str(p)]
    lanes=dict(native23_repaired=str(old_disc),native25_repaired=str(new_disc))
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),lanes=lanes,commands=[],build_proof=str(bp),build_proof_sha256=sha(bp),entry_proof=str(ep),entry_proof_sha256=sha(ep),prior_route_proof=str(pp),prior_route_proof_sha256=sha(pp),baseline_build_proof=str(baseline_path),baseline_build_proof_sha256=sha(baseline_path),template_changes=changes,maximum_frames=35000,host_guest_RAM_writes=0,checkpoint_restores=0,host_CPU_seeds=0,source_execution_ownership=False,whole_game_complete=False,source_sha256={str(p):sha(p)for p in [Path(__file__),template,observer_template,source,library,probe,core,route,post]},input_policy=previous['input_policy'])
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-free-route-active.json',state)
    mark();children=[]
    try:
        for lane,disc in lanes.items():
            command=[str(ROOT/'.venv/bin/python'),'-u',str(probe),'--boot','hle','--frames','35000','--core',str(core),'--disc',disc,'--navigate-waypoints',str(route),'--stop-after-scene-change','26000','--post-scene-navigate-actor','2','--post-scene-navigation-offset','1101','--post-scene-waypoints',str(post),'--capture-audio','--no-publish','--output',str(out/lane)]
            log=(out/(lane+'.log')).open('w');child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);children.append((lane,child,log));state['commands'].append(dict(lane=lane,pid=child.pid,command=command))
        state['status']='running_fresh_native23_native25_free_routes';mark();print('PIDs',[p.pid for _,p,_ in children],flush=True);codes={}
        for lane,child,log in children:codes[lane]=child.wait();log.close()
        state['exit_codes']=codes;assert not any(codes.values()),codes;results={}
        for lane,_,_ in children:
            report=json.loads((out/lane/'report.json').read_text());rows=report['frames'];last=rows[-1];obs=json.loads((out/lane/'gameplay-observation.json').read_text());assert not(obs['errors']or obs['copy_errors']or obs['repair_code_errors']);assert obs['repair_code_checks']>0
            assert obs['old_rng_steps']==obs['old_keypad_steps']==obs['old_controller_steps']==obs['old_task_steps']==obs['old_scheduler_steps']==obs['old_remove_steps']==obs['old_allocate_steps']==obs['old_compact_steps']==0
            assert obs['native_C_allocate_calls']>0 and obs['heap_base']==build['heap_start']
            assert obs['old_copy_body_steps']==0 and obs['native_C_copy_entry_observations']>0
            if lane=='native25_repaired':assert obs['old_free_body_steps']==obs['old_initialize_body_steps']==0 and obs['native_initialize_calls']>0
            else:assert obs['native_C_free_calls']==obs['native_initialize_calls']==0 and obs['old_initialize_body_steps']>0
            returned=[x for x in rows if(x.get('navigation')or{}).get('return_started')]
            results[lane]=dict(executed_frames=report['executed_frames'],first_scene_change=report['scene_change_frame'],merchant_reached=any(x['player_mode_word']==2 and x['floor_word']==2 and x['scene_word']==314 and abs(x['raw_player_X']-12832)<=16 and abs(x['raw_player_Z']-42385)<=16 for x in rows),nonzero_audio_samples=report['audio']['nonzero_samples'],return_floor_values=sorted({x['floor_word']for x in returned}),completed_outdoor_hold=last['player_mode_word']==1 and(last.get('navigation')or{}).get('outdoor_hold',0)>=120,final_fields={k:last[k]for k in ['raw_player_X','raw_player_Z','player_mode_word','floor_word','scene_word']},last_navigation=last.get('navigation'),observation=obs,report_sha256=sha(out/lane/'report.json'))
        state.update(status='terminal_fresh_native23_native25_free_routes_classified',results=results,finished_at=datetime.now(timezone.utc).isoformat());mark();save(ROOT/'verification/native-free-route-current.json',state);print(json.dumps({k:{a:b for a,b in value.items()if a not in ['observation','last_navigation']}for k,value in results.items()},indent=2),flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
