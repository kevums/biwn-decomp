"""Verify source-table resource payloads against preserved raw track and captures."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import extract_biwn_stage as stage
ROOT=stage.ROOT
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);layout=json.loads((session/'cdi-layout.json').read_text());track=next(t for t in layout['tracks']if t['track']==3);raw=(session/'raw-tracks/track-03-raw.bin').read_bytes();assert len(raw)==track['raw_bytes'] and sha(raw)=='e72ce60059eb9de926c5ebf1782b8bfd3202fd2e9ed084c10363ee6aa0575cc0'
 with(ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi').open('rb')as f:f.seek(track['raw_file_offset']);assert f.read(track['raw_bytes'])==raw
 data=stage.swap16(raw);ram=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();assert sha(ram)=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3';get=lambda a:int.from_bytes(ram[a:a+4],'big');rows=[]
 for index in range((0x4674c-0x464d0)//12):
  offset,tag,size=[get(0x464d0+index*12+k)for k in[0,4,8]]
  if not offset:continue
  needle=tag.to_bytes(4,'big')*16;marker=data.find(needle);assert marker>=0 and data.find(needle,marker+1)<0 and marker-offset==610 and offset%2352==64
  payload=data[marker+64:marker+64+size];assert len(payload)==size
  rows.append({'resource_id':index,'offset_field':offset,'tag':tag,'tag_ascii':tag.to_bytes(4,'big').decode('ascii'),'bytes':size,'marker_track_offset':marker,'payload_track_offset':marker+64,'payload_sha256':sha(payload),'marker_minus_source_offset':610})
 assert len(rows)==50
 model=next(r for r in rows if r['resource_id']==0);payload=data[model['payload_track_offset']:model['payload_track_offset']+model['bytes']];assert payload==ram[0x1a87a0:0x1a87a0+model['bytes']]
 marker=data.find(b'RTXT'*16);assert marker>=0 and data.find(b'RTXT'*16,marker+1)<0 and marker-0xe3adc0==610;texture=data[marker+64:marker+64+0x1e000];assert texture==ram[0x1134a0:0x1134a0+0x1e000]
 captured=ram[0x1c0000:0x1c8000];captured_offset=data.find(captured);assert captured_offset>=0 and data.find(captured,captured_offset+1)<0;phase=captured_offset%2352;assert phase==674
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'50_model_resources_and_RTXT_disc_provenance_verified','source_CDI_sha256':stage.IMAGE_SHA,'source_raw_track_sha256':sha(raw),'normalized_track_sha256':sha(data),'raw_track_path':str(session/'raw-tracks/track-03-raw.bin'),'track':track,'source_table_interval':'[0x464d0,0x4674c)','source_slots':53,'active_model_resources':50,'resources':rows,'player_model':{**model,'captured_RAM_address':hex(0x1a87a0),'full_payload_matches_capture':True},'textures':{'offset_field':0xe3adc0,'tag':0x52545854,'bytes':0x1e000,'marker_track_offset':marker,'payload_track_offset':marker+64,'payload_sha256':sha(texture),'captured_RAM_address':hex(0x1134a0),'full_payload_matches_capture':True},'captured_CD_buffer_witness':{'RAM_interval':'[0x1c0000,0x1c8000)','bytes':32768,'unique_normalized_track_offset':captured_offset,'sha256':sha(captured),'within_sector_phase':phase},'backend_mapping_scope':'Image-specific normalized track3 data. An empirical674-byte stream phase is supported by an exact32768byte original-capture witness and all50resource marker positions. This is not physical BIOS/CD seek timing or a universal Jaguar CD driver.','no_original_CPU_or_GPU_executed':True}
 p=ROOT/'verification/biwn-disc-resources.json';p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'active_models':50,'model_bytes':model['bytes'],'model_capture_equal':True,'textures_capture_equal':True,'CD_buffer_witness_bytes':32768,'stream_phase':phase}))
if __name__=='__main__':main()
