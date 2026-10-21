"""Read-only final descriptor inventory; identify an unexercised matrix branch."""
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

def main():
 p=V/'native-geometry-records-fresh-v2-candidate-current.json';j=read(p);rp=Path(j['report']);report=read(rp);memoryp=Path(j['directory'])/'candidate/RAM-final.bin';m=memoryp.read_bytes();records=read(Path(j['directory'])/'candidate/records-observation.json');assert records['matrix_entries']==records['matrix_returns']==0
 word=lambda a:int.from_bytes(m[a:a+2],'big');rows=[]
 for slot in range(40):
  a=0x4bd9c+slot*30;t=word(a)
  if t:rows.append(dict(slot=slot,address=hex(a),type_index=t,flag_address=hex(0x4208c+t),flags=m[0x4208c+t],matrix_bit_1_set=bool(m[0x4208c+t]&2),region=word(a+16),angle_byte=m[a+12]))
 assert rows==[dict(slot=0,address='0x4bd9c',type_index=70,flag_address='0x420d2',flags=0,matrix_bit_1_set=False,region=0,angle_byte=0)]
 source=ROOT/'projects/black-ice-white-noise/restoration/experimental/geometry-records-structured-v1/coordinator-reference.inc';factory=ROOT/'projects/black-ice-white-noise/restoration/biwn_static_factory_cpu.c';session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=session/'static-factory-fullCPU-generation.json';assembly=read(mapping)['instructions_decoded']
 visits=[dict(frame=f['frame'],scene=f['scene_word'])for i,f in enumerate(report['frames'])if i==0 or f['scene_word']!=report['frames'][i-1]['scene_word']]
 out=V/'geometry-records-matrix-fresh-gap-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 facts=dict(status='terminal_readonly_final_descriptor_inventory_matrix_fresh_coverage_open',directory=str(out),native_record_matrix_entries=0,native_record_matrix_returns=0,final_active_static_descriptors=rows,scene_transitions=visits,source_branch='Static descriptor first word is nonzero;mode2 also applies signed region filter. Read byte at0x4208C+type_index and testbit1. If set,the record builder callsE220at0x172BEwith return0x172C4.',candidate_table_indices_for_future_investigation=[dict(index=i,byte=m[0x4208c+i])for i in range(104,117)if m[0x4208c+i]&2],candidate_indices_prove_valid_instantiation=False,static_factory_entry='0x137e0',factory_original_instructions=len(assembly),next_action='Trace source137E0callers and scene descriptor loading to locate a naturally instantiated matrix-flagged static object. Reach it using ordinary controls,then require native matrix entries/returns and read-only observers. Do not patch object types or RAM to claim fresh coverage.',scope='Only the final RAM snapshot is inventoried. Its sole active type70has flag0,so that descriptor does not request the matrix branch. This alone does not explain every prior frame or prove candidate flag indices are valid objects. Zero matrix calls across the route comes from the qualified observer. No new game execution,hostwrites,training or model prediction.',new_game_runs=0,new_predictions=0,new_training=False,host_guest_RAM_writes=0,source_sha256={str(x):sha(x)for x in [Path(__file__),p,rp,memoryp,Path(j['directory'])/'candidate/records-observation.json',source,factory,mapping]})
 save(out/'review.json',facts);save(V/'geometry-records-matrix-fresh-gap-v1-current.json',facts);print('Final static descriptor:type70,flag0;fresh matrix coverage remains zero.',flush=True)
if __name__=='__main__':main()
