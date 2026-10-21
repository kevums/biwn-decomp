"""Label inherited hybrid history and make the current layout fields consistent."""
import copy,hashlib,json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 pointer=V/'current-biwn-latest-publication-current.json';previous=json.loads(pointer.read_text());assert previous['facts']['experimental_build']['resident_bytes']==30834;out=V/'native-direction-layout-publication-correction'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);save(out/'previous-publication.json',previous);result=copy.deepcopy(previous);f=result['facts']
 f['previous_navigation_layout_verification']=f['layout_verification'];f['layout_verification']=dict(f['layout_verification'],reservation_bytes=31104,heap_floor='0x166740',initial_heap_bytes=366784,staging_address='0xf6800',staging_clear_bytes=31232,staging_clear_end='0xfe200',current_direction_payload_bytes=30834,current_direction_free_bytes=270)
 f['inherited_hybrid_navigation_integration']=f.pop('hybrid_integration');f['inherited_hybrid_navigation_integration']['scope']='Historical30036bytehybridaddition/sourceprovenance;latestlayoutisexperimental_build/layout_verification. This inherited code remains unchanged in the new build.'
 f['local_authorship']['new_direction_model_calls']=3;f['local_authorship']['unchanged_local_direction_candidates_adopted']=0
 result.update(directory=str(out),recorded_at=datetime.now(timezone.utc).isoformat());result['scope']+=' Currentlayoutfieldsupdated;inheritedhybrid30036bytelayoutlabeledhistorical.';result['dependencies_sha256'].update({str(p):sha(p)for p in [Path(__file__),out/'previous-publication.json']});save(out/'publication.json',result);save(pointer,result);save(out/'protocol.json',dict(status='terminal_current_direction_layout_metadata_consistent',directory=str(out)));print(out)
if __name__=='__main__':main()
