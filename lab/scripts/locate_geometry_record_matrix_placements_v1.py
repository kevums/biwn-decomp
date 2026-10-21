"""Reuse immutable disc catalogues to locate static matrix-flagged placements."""
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

def main():
 out=V/'geometry-record-matrix-placement-leads-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 job=read(V/'native-geometry-records-fresh-v2-candidate-current.json');memoryp=Path(job['directory'])/'candidate/RAM-final.bin';m=memoryp.read_bytes();deps={str(Path(__file__)):sha(__file__),str(memoryp):sha(memoryp)};sets={};catalogues={}
 for family in ['indoor','outdoor']:
  p=V/(family+'-scene-catalog-current.json');g=read(p);recordp=Path(g['directory'])/'records.json';rows=read(recordp);deps[str(p)]=sha(p);deps[str(recordp)]=sha(recordp);catalogues[family]=g
  source=Path(g['resident_classification_RAM']if family=='indoor'else g['resident_flag_RAM']);assert sha(source)==g['resident_classification_RAM_sha256'if family=='indoor'else'resident_flag_RAM_sha256'];deps[str(source)]=sha(source)
  selected=[]
  for row in rows:
   groups=[dict(position=None,actors=row['actors'])]if family=='indoor'else row['segments']
   for group in groups:
    for a in group.get('actors',[]):
     t=a['actor_id'];flags=m[0x4208c+t];assert flags==a['resident_flags'],(family,row['index'],t)
     if not(flags&1)and(flags&2):selected.append(dict(record_index=row['index'],segment=group['position'],type_index=t,flags=flags,raw_placement=a))
  sets[family]=selected
 assert len(sets['indoor'])==28 and len({x['record_index']for x in sets['indoor']})==16 and sets['outdoor']==[]
 facts=dict(status='terminal_catalogued_matrix_flag_placement_leads_not_runtime_coverage',directory=str(out),indoor_placements=sets['indoor'],indoor_record_indices=sorted({x['record_index']for x in sets['indoor']}),indoor_matrix_placement_count=28,indoor_records_with_matrix_placements=16,outdoor_matrix_placement_count=0,catalogued_indoor_records=catalogues['indoor']['records'],catalogued_outdoor_blocks=catalogues['outdoor']['records'],current_final_flags_match_all_catalogued_actor_indices=True,ordinary_input_reachability_verified=False,actual_static_factory_instantiation_verified=False,fresh_record_matrix_path_verified=False,new_game_runs=0,new_predictions=0,new_training=False,source_sha256=deps,scope='Stored indoor/outdoor records and their source factory flag classification are reused without replaying game checks. A flagged data placement is not proof its factory actually instantiates a valid model or that controls can reach it. Indoor record IDs are catalogue indices;do not equate them with the fresh report scene_word without checking the loader/mode source. Candidate route312/313/314 does not supply matrix-path coverage.',next_action='Use scene loader/entrance source to map a naturally reachable doorway to one of these16indoor records;reach it through ordinary controls and require actual E220capture/return counts. Preserve the no-RAM-patch fresh contract.')
 save(out/'review.json',facts);save(V/'geometry-record-matrix-placement-leads-v1-current.json',facts);print('28flagged indoor placements in16records;zero stored outdoor matrix placements. Reachability unproven.',facts['indoor_record_indices'],flush=True)
if __name__=='__main__':main()
