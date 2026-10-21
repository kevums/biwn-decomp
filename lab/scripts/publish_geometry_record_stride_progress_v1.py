"""Publish qualified stride prototype separately from gameplay-tested v33 disc."""
import shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone

def main():
 out=V/'geometry-record-stride-progress-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 deps={str(Path(__file__)):sha(__file__)};proofs={}
 for name in ['geometry-records-native-strides-v1','scene17-geometry-records-strides-bridge-v1','geometry-records-strides-copied-rebuild-v1','geometry-records-native-cost-v1','geometry-records-native-stride-cost-v1']:
  path=V/(name+'-current.json');g=read(path);assert g['status'].startswith('terminal_') and 'failed'not in g['status'],name
  for p,h in g['source_sha256'].items():assert sha(p)==h,p
  deps.update(g['source_sha256']);deps[str(path)]=sha(path);save(out/(name+'.json'),g);proofs[name]=g
 hostp=V/'geometry-records-stride-host-v1/report.json';host=read(hostp);assert host['completed']==512 and host['host_guards']==19
 for name,h in host['source_sha256'].items():
  p=Path(name);p=p if p.is_absolute()else ROOT/p;assert sha(p)==h,p;deps[str(p)]=h
 for name in ['report.json','fixtures.json','guards.json','coverage.json','protocol.json']:
  p=hostp.parent/name;deps[str(p)]=sha(p)
 native=proofs['geometry-records-native-strides-v1'];scene=proofs['scene17-geometry-records-strides-bridge-v1'];copied=proofs['geometry-records-strides-copied-rebuild-v1']
 assert native['completed']==512 and scene['completed']==772 and native['payload_sha256']==scene['payload_sha256']==copied['sha256']
 assert native['maximum_C_stack_bytes']==120 and scene['maximum_C_stack_bytes']==168 and native['payload_bytes']==54134
 old=proofs['geometry-records-native-cost-v1']['cases'];new=proofs['geometry-records-native-stride-cost-v1']['cases'];rows=[]
 for a,b in zip(old,new):
  assert a['case']==b['case'] and a['original_CPU_cycles']==b['original_CPU_cycles'] and a['native_CPU_cycles']-b['native_CPU_cycles']==8080
  rows.append(dict(case=a['case'],original_CPU_cycles=a['original_CPU_cycles'],v33_CPU_cycles=a['native_CPU_cycles'],stride_CPU_cycles=b['native_CPU_cycles'],cycles_saved=8080,percent_saved=100*8080/a['native_CPU_cycles']))
 assert len(rows)==8
 wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
 for p,h in w['dependencies_sha256'].items():assert sha(p)==h,p
 packet=read(w['packet']);save(out/'before-wrapper.json',w);save(out/'before-packet.json',packet)
 report=ROOT/'reports/BIWN Record Stride Optimization Prototype.txt'
 action='Integrate the verified v34stride prototype into a relocated candidate disc,then qualify its exact addresses,fallbacks/aliases,read-only observers and fresh route before any preview promotion. Exercise E220through ordinary controls;current v33fresh record-matrix count is zero. Continue remaining CPU/GPU/DSP/HLE source recovery,source-only same-console rebuild,video/audio/IRQ fidelity,useful untouched-task training and copied-weight LM Studio Chat usability.'
 facts=dict(status='terminal_readable_record_stride_prototype_host_native_scene_and_copied_SDK_pass_unintegrated',directory=str(out),report=str(report),profile='deck-shared-v34-record-strides-v1',artifact_type='source_component_prototype_not_disc_image',new_disc_built=False,disc_integrated=False,candidate_disc=None,fresh_gameplay_verified=False,installed_preview_changed=False,authored_source=str(ROOT/'projects/black-ice-white-noise/restoration/experimental/geometry-records-strides-v1/coordinator-reference.inc'),authorship='Coordinator target adaptation of readable170A0. No model source adopted.',new_unique_original_functions=0,new_internal_readable_helper_integrations=0,host_cases=512,host_guards=19,native_body_cases=512,prototype_scene_cases=772,module_bytes=54134,previous_module_bytes=54214,module_bytes_saved=80,body_C_stack_bytes=120,connected_C_stack_bytes=168,C_stack_reserved=208,C_stack_margin=40,CPU_cost_fixtures=rows,CPU_cycles_saved_each_fixture=8080,CPU_cost_percent_saved_range=[min(r['percent_saved']for r in rows),max(r['percent_saved']for r in rows)],target_CPU_cycle_measurement=True,game_frame_speed_measured=False,copied_prototype_module_byte_identical=True,original_instructions_newly_recovered=0,remaining_original_scene_service_entry_points=['0xe3e0','0xe220'],component_provider_scope='Pinned original E3E0/E220/E098 CPU providers and synchronous originalGPU4320;other sceneGPU commands use controlled mailboxes. This does not inherit v33actual-provider/final-image/fresh proof.',native_IRQ_verified=False,native_alias_fallback_qualification_complete=False,new_training=False,optimizer_updates=0,model_source_installed=False,native_Chat_verified=False,whole_game_complete=False,next_action=action)
 packet['previous_latest_source_development_before_record_strides']=packet['latest_source_development'];packet['native_geometry_record_stride_progress']=packet['latest_source_development']=facts
 assert 'pending_native_candidate'not in packet
 for key in ['latest_native_candidate','native_geometry_records_progress','native_scene_draw_progress','native_outer_compact_progress','native_scene_dispatch_headroom_progress']:packet[key]['next_action']=action
 packet['checked_current_summary']+=' Newer v34source/component prototype replaces two loop index calculations with MULS.W;saves8080CPUcycles in eight fixtures and80modulebytes;host512+19guards,native512,scene772,copiedSDKpass. No v34disc or fresh gameplay yet.'
 packet['checked_answer']=packet['checked_current_summary'];packet['recorded_at']=datetime.now(timezone.utc).isoformat()
 report.write_text('BIWN — record stride optimization prototype\n\n'
  'Two40-record loops now calculate signed206/30byte strides with actual68000 MULS.W. It replaces only temporary index arithmetic and dead MOVE flags;logical X/upperSR,full registers,bus/helper/guest-stack effects are preserved at the qualified boundaries. New code is coordinator-authored,zero new unique original functions.\n\n'
  'Eight measured CPU fixtures each save8080cycles relative to v33,about4–15percent of record-body CPU cost. Module54,134bytes versus54,214,80bytes smaller. CPUcycles are sums returned by m68k_execute(1),including declared copy/matrix/wait CPUproviders;GPUtime is excluded. The reference stops before original outerRTS and native includes its C ABIreturn. Relative v33/v34measurements use the same boundaries. This is not measured game-frame speed or hardware timing.\n\n'
  'Host512cases+19error guards pass,including5782actualcopy and2569matrix submissions. Actual68000body512cases pass full logical CPU,banks,nonprivateRAM,helper boundaries and scoped ordered public bus;nativeCLRdummyreads included. Continuous trace remains armed. Connectedscene772cases pass with declared original copy/matrix providers and synchronousGPU4320fixture. BodyCstack120bytes;scene168/208. Copied source+SDKrebuild is byte-identical54,134bytes.\n\n'
  'This is an unintegrated source/component prototype. There is no new CDI,exact final relocation/nesting/observer or fresh-route proof for v34. Latest gameplay-tested disc remains v33:25020/24965frames,5668native scene returns,4666record bodies,8381copy returns,ZERO record-matrix calls;8764video differences,finalvideo/selectedfields agree,silentaudio. Sampled active-outer heap14256bytes,not globalminimum. The Desktopcheckpoint preview is unchanged.\n\n'
  'Local model:full-function v1Author/Repair and compactv2Author all truncated;three actual predictions,no compiled body or new optimizer updates. A bounded22instruction prologue Author/Repair worker is separate;it respects the shared model lease and has not supplied adopted code.\n\n'+action+'\n')
 for name in ['show_native_status_v6.py','portable_biwn_entry_v14.py']:
  p=ROOT/'scripts'/name;deps[str(p)]=sha(p);clone(p,P/'workbench/scripts'/name)
 target=P/'workbench/portable_biwn.py';shutil.copy2(target,out/'previous-portable-entry.py');shutil.copy2(ROOT/'scripts/portable_biwn_entry_v14.py',target)
 save(out/'cost-comparison.json',rows);save(out/'facts.json',facts);save(out/'current-status-packet.json',packet);shutil.copy2(report,out/report.name);shutil.copy2(__file__,out/'publisher-source.py')
 deps.update({str(p):sha(p)for p in out.rglob('*')if p.is_file()});deps[str(report)]=sha(report)
 for p,h in deps.items():assert Path(p).is_relative_to(ROOT)and sha(p)==h,p
 pub=V/'geometry-record-stride-progress-v1-current.json';atomic(pub,dict(status=facts['status'],directory=str(out),report=str(report),facts=str(out/'facts.json'),dependencies_sha256=deps,new_training=False,whole_objective_complete=False))
 w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps,str(pub):sha(pub)});atomic(wp,w)
 for p in deps:clone(Path(p),P/'workbench'/Path(p).relative_to(ROOT))
 clone(pub,P/'workbench/verification'/pub.name);clone(wp,P/'workbench/verification'/wp.name)
 for root in [ROOT,P/'workbench']:(root/'CURRENT DECOMPILATION.txt').write_text(report.read_text());(root/'WATCH LOCAL AGENTS.txt').write_text(report.read_text())
 for label,command in [('Root',[str(ROOT/'.venv/bin/python3.12'),str(ROOT/'scripts/show_native_status_v6.py'),'--brief']),('copied',[str(P/'runtime/python/bin/python3.12'),str(target),'status'])]:
  q=subprocess.run(command,cwd='/',capture_output=True,text=True,timeout=180);(out/(label+'-status.txt')).write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
  assert all(x in q.stdout for x in ['25,020/24,965','8,764','54,134','8,080','Not yet a disc image','320.05'])
 print(facts['status'],report,flush=True)
if __name__=='__main__':main()
