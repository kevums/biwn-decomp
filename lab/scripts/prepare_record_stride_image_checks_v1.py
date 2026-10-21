"""Isolate v34 qualification scripts from immutable v33 results and pinned maps."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'scripts'
NAMES=['check_scene17_geometry_records_final_bridge_v1','check_geometry_records_whole_scene_disc_v3','check_geometry_records_disc_providers_v1','check_geometry_records_final_fallback_v1','check_geometry_records_alias_reentry_v1','check_native_deck_alias_nesting_geometry_records_v1','check_native_geometry_records_geometry_alias_v1','check_native_deck_outer_connected_geometry_records_v1','check_geometry_records_final_public_bus_v1','check_geometry_records_final_display_v1','check_geometry_records_final_copied_rebuild_v1','qualify_geometry_records_geometry_observer_v1','qualify_geometry_records_outer_observer_v1','check_shared_deck_observer_regions_geometry_records_v1','qualify_geometry_records_reset_observer_v1','qualify_geometry_records_shared_observer_v1','qualify_geometry_records_commit_observer_v1','qualify_geometry_records_clear_commit_observer_v1','qualify_geometry_records_rotation_commit_observer_v1','check_geometry_records_observer_actual_CPU_v1','check_geometry_records_geometry_observer_actual_cpu_v1','check_geometry_records_outer_observer_actual_CPU_v2','check_geometry_records_fallback_alias_observers_actual_CPU_v1','qualify_geometry_records_fresh_preflight_v1','run_native_geometry_records_route_v1','review_geometry_records_fresh_v1']
MODULES={name:name.replace('geometry_records','record_strides')for name in NAMES}
MODULES.update({p.stem:p.stem.replace('shared_deck_geometry_records_','shared_deck_record_strides_')for p in S.glob('shared_deck_geometry_records_*observer_v1.py')})
MODULES.update(geometry_records_observer_build_v1='record_strides_observer_build_v1',check_native_geometry_records_profile_v2='check_native_record_strides_profile_v1',check_native_deck_retained_geometry_records_v1='check_native_deck_retained_record_strides_v1')
def rewrite(text):
 text=text.replace('deck-shared-v33-geometry-records-v1','deck-shared-v34-record-strides-v1')
 for a,b in sorted(MODULES.items(),key=lambda x:-len(x[0])):text=text.replace(a,b)
 text=text.replace('geometry-records','record-strides').replace('54214','54134')
 # These are immutable original maps, not new proof-family filenames.
 text=text.replace('record-strides-fullCPU-generation.json','geometry-records-fullCPU-generation.json').replace('record-strides-structured-v1','geometry-records-strides-v1').replace('record-strides-strides-v1','geometry-records-strides-v1')
 text=text.replace('native-record-strides-profile-v2','native-record-strides-profile-v1')
 text=text.replace('terminal_v33','terminal_v34').replace('fresh v33 routes','fresh v34 routes')
 return text

def main():
 for old,new in MODULES.items():
  if old in ['check_native_geometry_records_profile_v2','check_native_deck_retained_geometry_records_v1']:continue
  p=S/(new+'.py');assert not p.exists(),p;text=rewrite((S/(old+'.py')).read_text())
  if old=='check_geometry_records_observer_actual_CPU_v1':text=text.replace('record-strides-observer-actual-CPU-v1','record-strides-record-observer-actual-CPU-v1')
  if old=='check_geometry_records_geometry_observer_actual_cpu_v1':text=text.replace('record-strides-observer-actual-CPU-v1','record-strides-geometry-observer-actual-CPU-v1')
  if old=='check_geometry_records_fallback_alias_observers_actual_CPU_v1':
   a=text.index(" review=read(V/'record-strides-record-observer-actual-CPU-reviewed-v2-current.json');");z=text.index('\n for gate in [g,s]:',a)
   text=text[:a]+" gp=V/'record-strides-commit-observer-qualified-v1-current.json';sp=V/'record-strides-shared-observer-qualified-v1-current.json';g=read(gp);s=read(sp)"+text[z:]
  if old=='qualify_geometry_records_fresh_preflight_v1':text=text.replace('record-strides-record-observer-actual-CPU-reviewed-v2','record-strides-record-observer-actual-CPU-v1')
  if old=='run_native_geometry_records_route_v1':text=text.replace('record-strides-record-observer-actual-CPU-reviewed-v2','record-strides-record-observer-actual-CPU-v1')
  compile(text,str(p),'exec');p.write_text(text)
 print('Prepared',len(MODULES)-2,'isolated v34 scripts;original maps and v33markers preserved.',flush=True)
if __name__=='__main__':main()
