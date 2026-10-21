"""Fresh native26/native27compact routes, pad input and read-only CPU observation."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,re,subprocess
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
 bp=ROOT/'verification/native-load-scan-disc-build-current.json';build=json.loads(bp.read_text());ep=ROOT/'verification/native-load-scan-disc-entry-current.json';entry=json.loads(ep.read_text());assert entry['status']=='terminal_native_entry_heap_and_component_pass'and entry['build_proof_sha256']==sha(bp)
 for p,d in build['source_sha256'].items():assert sha(p)==d,p
 pp=ROOT/'verification/native-resource-route-current.json';previous=json.loads(pp.read_text());pd=Path(previous['directory']);template=pd/'fresh-resource-route.py';observer_template=pd/'resource-observer.c'
 for p in [template,observer_template]:assert sha(p)==previous['source_sha256'][str(p)]
 baseline_path=ROOT/'verification/native-resource-disc-build-current.json';baseline=json.loads(baseline_path.read_text());old_disc=Path(baseline['derived_disc']);new_disc=Path(build['derived_disc']);assert sha(old_disc)==baseline['derived_disc_sha256']and sha(new_disc)==build['derived_disc_sha256']
 out=ROOT/'verification/native-load-scan-route'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 host=observer_template.read_text();needle='static unsigned resource_native;';assert host.count(needle)==1
 host=host.replace(needle,needle+'\nstatic unsigned acquire_native;\nstatic uint64_t loader_entries,old_loader_body_steps,native_C_loader_calls,loader_user_observations,loader_task_stack_outside;\nstatic uint32_t loader_min_task_headroom=0xffffffffu;\nstatic uint64_t acquire_entries,old_acquire_body_steps,native_C_acquire_calls,acquire_user_observations,acquire_task_stack_outside;\nstatic uint32_t acquire_min_task_headroom=0xffffffffu;')
 needle='resource_native=((unsigned)selected&128u)!=0;';assert host.count(needle)==1;host=host.replace(needle,needle+'acquire_native=((unsigned)selected&256u)!=0;')
 counters={
 'native_C_allocate_calls':('biwn_native_heap_allocate_body','heap_native&&'),
 'native_C_compact_calls':('biwn_native_heap_compact_body','heap_native&&'),
 'native_dispatch_calls':('biwn_native_scheduler_dispatch',''),
 'native_remove_calls':('biwn_native_scheduler_remove',''),
 'native_C_select_calls':('biwn_native_scheduler_select',''),
 'native_scheduler_RTEs':('biwn_native_scheduler_rte',''),
 'native_task_entries':('biwn_native_task_create','task_native&&'),
 'native_C_copy_entry_observations':('biwn_native_copy_body','copy_native&&'),
 'native_C_free_calls':('biwn_native_free_body','free_native&&'),
 'native_initialize_calls':('biwn_native_heap_initialize','free_native&&'),
 'native_C_resource_release_calls':('biwn_native_resource_release_body','resource_native&&')}
 for counter,(symbol,prefix)in counters.items():
  old=baseline['symbols'][symbol];new=build['symbols'][symbol];pattern=r'if\([^\n;]*\)'+re.escape(counter)+r'\+\+;';host,count=re.subn(pattern,f'if({prefix}pc==(acquire_native?{new}:{old})){counter}++;',host);assert count==1,(counter,count)
 needle=f"if(pc==(resource_native?{baseline['symbols']['biwn_native_heap_initialize_return']}:{baseline['symbols']['biwn_native_heap_initialize_return']}))";assert host.count(needle)==1;host=host.replace(needle,f"if(pc==(acquire_native?{build['symbols']['biwn_native_heap_initialize_return']}:{baseline['symbols']['biwn_native_heap_initialize_return']}))")
 prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');component=Path(build['linked_component']);elf=component.with_suffix('.elf');nd=component.parent
 asmrow=next(l.split()for l in subprocess.check_output([prefix+'objdump','-h',str(nd/'resource-acquire-shim.o')],text=True).splitlines()if '.text.biwn_native_resource_acquire 'in l);bodyrow=next(l.split()for l in subprocess.check_output([prefix+'nm','-S','--defined-only',str(elf)],text=True).splitlines()if l.split()[-1]=='biwn_native_resource_acquire_body')
 owned={}
 for line in subprocess.check_output([prefix+'nm','-S','--defined-only',str(nd/'resource-acquire-native.o')],text=True).splitlines():
  t=line.split()
  if len(t)==4 and t[2].lower()=='t':owned[t[3]]=int(t[1],16)
 ranges=[(build['symbols']['biwn_native_resource_acquire'],build['symbols']['biwn_native_resource_acquire']+int(asmrow[2],16))];found=[]
 for line in subprocess.check_output([prefix+'nm','-S','--defined-only',str(elf)],text=True).splitlines():
  t=line.split()
  if len(t)==4 and t[3]in owned:
   assert int(t[1],16)==owned[t[3]];found.append(t[3]);ranges.append((int(t[0],16),int(t[0],16)+int(t[1],16)))
 assert sorted(found)==sorted(owned),found
 watch='||'.join(f'(pc>={x}u&&pc<{y}u)'for x,y in ranges)
 load_asm=next(l.split()for l in subprocess.check_output([prefix+'objdump','-h',str(nd/'resource-load-shim.o')],text=True).splitlines()if '.text.biwn_native_resource_load 'in l)
 load_owned={t[3]:int(t[1],16)for l in subprocess.check_output([prefix+'nm','-S','--defined-only',str(nd/'resource-load-native.o')],text=True).splitlines()if len(t:=l.split())==4 and t[2].lower()=='t'}
 load_ranges=[(build['symbols']['biwn_native_resource_load'],build['symbols']['biwn_native_resource_load']+int(load_asm[2],16))];load_found=[]
 for line in subprocess.check_output([prefix+'nm','-S','--defined-only',str(elf)],text=True).splitlines():
  t=line.split()
  if len(t)==4 and t[3]in load_owned:
   assert int(t[1],16)==load_owned[t[3]];load_found.append(t[3]);load_ranges.append((int(t[0],16),int(t[0],16)+int(t[1],16)))
 assert sorted(load_found)==sorted(load_owned)
 kernel=next(l.split()for l in subprocess.check_output([prefix+'objdump','-h',str(nd/'resource-load-scan.o')],text=True).splitlines()if '.text.biwn_native_resource_load_scan 'in l);kernel_start=build['symbols']['biwn_native_load_scan'];load_ranges.append((kernel_start,kernel_start+int(kernel[2],16)))
 load_watch='||'.join(f'(pc>={x}u&&pc<{y}u)'for x,y in load_ranges)

 needle='    steps++;';assert host.count(needle)==1
 host=host.replace(needle,needle+f'''
    if(pc==0x1b044)loader_entries++;
    if(pc>0x1b044&&pc<0x1b154)old_loader_body_steps++;
    if(acquire_native&&pc=={build['symbols']['biwn_native_resource_load_body']}u)native_C_loader_calls++;
    if(acquire_native&&({load_watch})){{
        struct cpu value;read_cpu(&value);
        if(!(value.sr&0x2000u)){{
            uint32_t task=rd32(0xc0920),sp=value.r[15];loader_user_observations++;
            if(!task||task>0x1ffbc0u||sp<task+38u||sp>task+0x404u)loader_task_stack_outside++;
            else if(sp-task-38u<loader_min_task_headroom)loader_min_task_headroom=sp-task-38u;
        }}
    }}
    if(pc==0x1af04)acquire_entries++;
    if(pc>0x1af04&&pc<0x1b002)old_acquire_body_steps++;
    if(acquire_native&&pc=={build['symbols']['biwn_native_resource_acquire_body']}u)native_C_acquire_calls++;
    if(acquire_native&&({watch})){{
        struct cpu value;read_cpu(&value);
        if(!(value.sr&0x2000u)){{
            uint32_t task=rd32(0xc0920),sp=value.r[15];acquire_user_observations++;
            if(!task||task>0x1ffbc0u||sp<task+38u||sp>task+0x404u)acquire_task_stack_outside++;
            else if(sp-task-38u<acquire_min_task_headroom)acquire_min_task_headroom=sp-task-38u;
        }}
    }}
''')
 needle='    array(file,"rng_entries",rng_entries,8);';assert host.count(needle)==1
 extra='    fprintf(file,",\\"acquire_native\\":%u,\\"acquire_entries\\":%llu,\\"old_acquire_body_steps\\":%llu,\\"native_C_acquire_calls\\":%llu,\\"acquire_user_observations\\":%llu,\\"acquire_task_stack_outside\\":%llu,\\"acquire_min_task_headroom\\":%u",acquire_native,(unsigned long long)acquire_entries,(unsigned long long)old_acquire_body_steps,(unsigned long long)native_C_acquire_calls,(unsigned long long)acquire_user_observations,(unsigned long long)acquire_task_stack_outside,acquire_min_task_headroom);\n'
 extra+='    fprintf(file,",\\"loader_entries\\":%llu,\\"old_loader_body_steps\\":%llu,\\"native_C_loader_calls\\":%llu,\\"loader_user_observations\\":%llu,\\"loader_task_stack_outside\\":%llu,\\"loader_min_task_headroom\\":%u",(unsigned long long)loader_entries,(unsigned long long)old_loader_body_steps,(unsigned long long)native_C_loader_calls,(unsigned long long)loader_user_observations,(unsigned long long)loader_task_stack_outside,loader_min_task_headroom);\n'
 host=host.replace(needle,extra+needle);source=out/'load-observer.c';source.write_text(host);library=out/'libload-observer.dylib'
 p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 lines=template.read_text().splitlines(keepends=True);changes=[]
 for i,line in enumerate(lines):
  if line.startswith('        observer=c.CDLL('):lines[i]='        observer=c.CDLL('+repr(str(library))+')\n';changes.append('observer_library')
  elif line.startswith('        observer_payload=c.create_string_buffer('):lines[i]='        observer_payload=c.create_string_buffer(Path('+repr(build['component'])+' if disc==Path('+repr(str(new_disc))+') else '+repr(baseline['component'])+').read_bytes())\n';changes.append('payload_signature')
  elif line.startswith('            (255 if disc==Path('):lines[i]='            (511 if disc==Path('+repr(str(new_disc))+') else 255),observer_payload,len(observer_payload.raw)-1,\n';changes.append('read_only_flags')
 assert len(changes)==3;probe=out/'fresh-load-route.py';probe.write_text(''.join(lines));compile(probe.read_text(),str(probe),'exec')
 core=ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source/virtualjaguar_libretro.dylib';route=ROOT/'verification/normal-route-312-plan.json';post=ROOT/'verification/native-word-scan-clearance-long-route/20261018T053248.873269Z/merchant-corridor.json'
 for p in [core,route,post]:assert sha(p)==previous['source_sha256'][str(p)]
 lanes=dict(native26_repaired=str(old_disc),native28scan_repaired=str(new_disc))
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),lanes=lanes,commands=[],build_proof=str(bp),build_proof_sha256=sha(bp),entry_proof=str(ep),entry_proof_sha256=sha(ep),prior_route_proof=str(pp),prior_route_proof_sha256=sha(pp),baseline_build_proof=str(baseline_path),baseline_build_proof_sha256=sha(baseline_path),template_changes=changes,maximum_frames=35000,host_guest_RAM_writes=0,checkpoint_restores=0,host_CPU_seeds=0,source_execution_ownership=False,whole_game_complete=False,source_sha256={str(p):sha(p)for p in [Path(__file__),template,observer_template,source,library,probe,core,route,post]},input_policy=previous['input_policy'],acquire_stack_observation_PC_ranges=ranges,loader_stack_observation_PC_ranges=load_ranges)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-load-scan-route-active.json',state)
 mark();children=[]
 try:
  for lane,disc in lanes.items():
   command=[str(ROOT/'.venv/bin/python'),'-u',str(probe),'--boot','hle','--frames','35000','--core',str(core),'--disc',disc,'--navigate-waypoints',str(route),'--stop-after-scene-change','26000','--post-scene-navigate-actor','2','--post-scene-navigation-offset','1101','--post-scene-waypoints',str(post),'--capture-audio','--no-publish','--output',str(out/lane)]
   log=(out/(lane+'.log')).open('w');child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);children.append((lane,child,log));state['commands'].append(dict(lane=lane,pid=child.pid,command=command))
  state['status']='running_fresh_native26_native28scan_load_routes';mark();print('PIDs',[p.pid for _,p,_ in children],flush=True);codes={}
  for lane,child,log in children:codes[lane]=child.wait();log.close()
  state['exit_codes']=codes;assert not any(codes.values()),codes;results={}
  for lane,_,_ in children:
   report=json.loads((out/lane/'report.json').read_text());rows=report['frames'];last=rows[-1];obs=json.loads((out/lane/'gameplay-observation.json').read_text());assert not(obs['errors']or obs['copy_errors']or obs['repair_code_errors']);assert obs['repair_code_checks']>0
   assert all(obs[k]==0 for k in ['old_rng_steps','old_keypad_steps','old_controller_steps','old_task_steps','old_scheduler_steps','old_remove_steps','old_allocate_steps','old_compact_steps','old_copy_body_steps','old_free_body_steps','old_initialize_body_steps','old_resource_release_body_steps'])
   expected_floor=(build if lane=='native28scan_repaired'else baseline)['heap_start'];assert obs['native_C_allocate_calls']>0 and obs['heap_base']==expected_floor
   assert obs['native_C_resource_release_calls']==obs['resource_release_entries']>0
   if lane=='native28scan_repaired':assert obs['old_acquire_body_steps']==0 and obs['native_C_acquire_calls']==obs['acquire_entries']>0 and obs['acquire_user_observations']>0 and obs['acquire_task_stack_outside']==0
   if lane=='native28scan_repaired':assert obs['native_C_loader_calls']==obs['loader_entries']>0 and obs['old_loader_body_steps']==0 and obs['loader_user_observations']>0 and obs['loader_task_stack_outside']==0
   else:assert obs['native_C_acquire_calls']==0 and obs['old_acquire_body_steps']>0 and obs['native_C_loader_calls']==0 and obs['old_loader_body_steps']>0
   returned=[x for x in rows if(x.get('navigation')or{}).get('return_started')]
   results[lane]=dict(executed_frames=report['executed_frames'],first_scene_change=report['scene_change_frame'],merchant_reached=any(x['player_mode_word']==2 and x['floor_word']==2 and x['scene_word']==314 and abs(x['raw_player_X']-12832)<=16 and abs(x['raw_player_Z']-42385)<=16 for x in rows),nonzero_audio_samples=report['audio']['nonzero_samples'],return_floor_values=sorted({x['floor_word']for x in returned}),completed_outdoor_hold=last['player_mode_word']==1 and(last.get('navigation')or{}).get('outdoor_hold',0)>=120,final_fields={k:last[k]for k in ['raw_player_X','raw_player_Z','player_mode_word','floor_word','scene_word']},last_navigation=last.get('navigation'),observation=obs,report_sha256=sha(out/lane/'report.json'))
  state.update(status='terminal_fresh_native26_native28scan_load_routes_classified',results=results,finished_at=datetime.now(timezone.utc).isoformat());mark();save(ROOT/'verification/native-load-scan-route-current.json',state);print(json.dumps({k:{a:b for a,b in v.items()if a not in ['observation','last_navigation']}for k,v in results.items()},indent=2),flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
