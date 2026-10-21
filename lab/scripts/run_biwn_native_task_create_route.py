"""Fresh native13/native15 repaired-disc route, ordinary pad and read-only observer.

The prior proven long-clearance policy is copied exactly. Only observer,
per-disc resident signature and the explicit CDI choices change.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,subprocess
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
    bp=ROOT/'verification/native-task-create-disc-build-current.json';build=json.loads(bp.read_text())
    ep=ROOT/'verification/native-task-create-disc-entry-current.json';entry=json.loads(ep.read_text())
    assert entry['status']=='terminal_native_entry_heap_and_component_pass' and entry['build_proof_sha256']==sha(bp)
    for p,d in build['source_sha256'].items():assert sha(p)==d,p
    prior_path=ROOT/'verification/native-word-scan-clearance-long-route-current.json';prior=json.loads(prior_path.read_text());prior_dir=Path(prior['directory'])
    template=prior_dir/'fresh-word-scan-route.py';old_observer=prior_dir/'word-scan-observer.c'
    for p in [template,old_observer]:assert sha(p)==prior['source_sha256'][str(p)]
    scan_path=ROOT/'verification/native-word-scan-build-current.json';scan=json.loads(scan_path.read_text());baseline=json.loads(Path(scan['baseline_proof']).read_text())
    old_disc=Path(scan['images']['native_repaired']['disc']);new_disc=Path(build['derived_disc'])
    assert sha(old_disc)==scan['images']['native_repaired']['sha256'] and sha(new_disc)==build['derived_disc_sha256']
    out=ROOT/'verification/native-task-create-route'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    host=old_observer.read_text();host=host.replace('static unsigned repaired,repair_code_errors;', 'static unsigned repaired,repair_code_errors,task_native;\nstatic uint64_t task_register_entries,task_stack_entries,old_task_steps,native_task_entries,task_empty_exceptions;')
    marker='repaired=((unsigned)selected&2u)!=0;';assert host.count(marker)==1;host=host.replace(marker,marker+'task_native=((unsigned)selected&4u)!=0;')
    marker='    steps++;';assert host.count(marker)==1
    host=host.replace(marker,marker+f'''
    if(pc==0xde5c)task_register_entries++;
    if(pc==0xdf6c)task_stack_entries++;
    if(pc>0xde5c&&pc<0xdeb4)old_task_steps++;
    if(task_native&&pc=={build['symbols']['biwn_native_task_create']})native_task_entries++;
    if(pc==0xdeb4)task_empty_exceptions++;
''')
    marker='    array(file,"rng_entries",rng_entries,8);';assert host.count(marker)==1
    host=host.replace(marker,'    fprintf(file,",\\"task_native\\":%u,\\"task_register_entries\\":%llu,\\"task_stack_entries\\":%llu,\\"old_task_steps\\":%llu,\\"native_task_entries\\":%llu,\\"task_empty_exceptions\\":%llu",task_native,(unsigned long long)task_register_entries,(unsigned long long)task_stack_entries,(unsigned long long)old_task_steps,(unsigned long long)native_task_entries,(unsigned long long)task_empty_exceptions);\n'+marker)
    source=out/'task-observer.c';source.write_text(host);library=out/'libtask-observer.dylib'
    p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    text=template.read_text();lines=text.splitlines(keepends=True);changes=[]
    for i,line in enumerate(lines):
        if line.startswith('        observer=c.CDLL('):lines[i]='        observer=c.CDLL('+repr(str(library))+')\n';changes.append('observer_library')
        elif line.startswith('        observer_payload=c.create_string_buffer('):lines[i]='        observer_payload=c.create_string_buffer(Path('+repr(build['component'])+' if disc==Path('+repr(str(new_disc))+') else '+repr(baseline['component'])+').read_bytes())\n';changes.append('disc_specific_read_only_payload_signature')
        elif line.startswith('            (int(disc in [Path('):lines[i]='            (7 if disc==Path('+repr(str(new_disc))+') else 3),observer_payload,len(observer_payload.raw)-1,\n';changes.append('observer_flags')
    assert len(changes)==3
    probe=out/'fresh-task-route.py';probe.write_text(''.join(lines))
    subprocess.run([str(ROOT/'.venv/bin/python'),'-m','py_compile',str(probe)],check=True)
    core=ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source/virtualjaguar_libretro.dylib'
    route=ROOT/'verification/normal-route-312-plan.json';post=prior_dir/'merchant-corridor.json'
    assert sha(route)==prior['source_sha256'][str(route)]and sha(post)==prior['source_sha256'][str(post)]
    lanes=dict(native13_repaired=str(old_disc),native15_repaired=str(new_disc))
    state=dict(status='prepared',directory=str(out),pid=os.getpid(),lanes=lanes,commands=[],build_proof=str(bp),build_proof_sha256=sha(bp),entry_proof=str(ep),entry_proof_sha256=sha(ep),prior_route_proof=str(prior_path),prior_route_proof_sha256=sha(prior_path),template_changes=changes,maximum_frames=35000,host_guest_RAM_writes=0,checkpoint_restores=0,host_CPU_seeds=0,source_execution_ownership=False,whole_game_complete=False,source_sha256={str(p):sha(p)for p in [Path(__file__),template,old_observer,source,library,probe,core,route,post]},input_policy=prior['input_policy'])
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-task-create-route-active.json',state)
    mark();children=[]
    try:
        for lane,disc in lanes.items():
            command=[str(ROOT/'.venv/bin/python'),'-u',str(probe),'--boot','hle','--frames','35000','--core',str(core),'--disc',disc,'--navigate-waypoints',str(route),'--stop-after-scene-change','26000','--post-scene-navigate-actor','2','--post-scene-navigation-offset','1101','--post-scene-waypoints',str(post),'--capture-audio','--no-publish','--output',str(out/lane)]
            log=(out/(lane+'.log')).open('w');child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);children.append((lane,child,log));state['commands'].append(dict(lane=lane,pid=child.pid,command=command))
        state['status']='running_two_fresh_native_task_routes';mark();print('PIDs',[p.pid for _,p,_ in children],flush=True)
        codes={}
        for lane,child,log in children:codes[lane]=child.wait();log.close()
        state['exit_codes']=codes;assert not any(codes.values()),codes
        results={}
        for lane,_,_ in children:
            report=json.loads((out/lane/'report.json').read_text());rows=report['frames'];last=rows[-1];obs=json.loads((out/lane/'gameplay-observation.json').read_text())
            assert not(obs['errors']or obs['copy_errors']or obs['repair_code_errors']);assert obs['repair_code_checks']>0
            assert obs['old_rng_steps']==obs['old_keypad_steps']==obs['old_controller_steps']==0
            if lane=='native15_repaired':assert obs['old_task_steps']==0 and obs['native_task_entries']>0
            else:assert obs['old_task_steps']>0 and obs['native_task_entries']==0
            returned=[x for x in rows if(x.get('navigation')or{}).get('return_started')]
            results[lane]=dict(executed_frames=report['executed_frames'],first_scene_change=report['scene_change_frame'],merchant_reached=any(x['player_mode_word']==2 and x['floor_word']==2 and x['scene_word']==314 and abs(x['raw_player_X']-12832)<=16 and abs(x['raw_player_Z']-42385)<=16 for x in rows),nonzero_audio_samples=report['audio']['nonzero_samples'],return_floor_values=sorted({x['floor_word']for x in returned}),outdoor_after_return=any(x['player_mode_word']==1 for x in returned),completed_outdoor_hold=last['player_mode_word']==1 and(last.get('navigation')or{}).get('outdoor_hold',0)>=120,final_fields={k:last[k]for k in ['raw_player_X','raw_player_Z','player_mode_word','floor_word','scene_word']},last_navigation=last.get('navigation'),observation=obs,report_sha256=sha(out/lane/'report.json'))
        state.update(status='terminal_fresh_native13_native15_routes_classified',results=results,finished_at=datetime.now(timezone.utc).isoformat());mark();save(ROOT/'verification/native-task-create-route-current.json',state);print(json.dumps({k:{a:b for a,b in v.items()if a not in ['observation','last_navigation']}for k,v in results.items()},indent=2),flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
