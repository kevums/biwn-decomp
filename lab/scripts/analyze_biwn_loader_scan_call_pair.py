"""Compare captured real-game loader boundaries without changing guest state."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
 pp=ROOT/'verification/native-loader-scan-call-pair-current.json';s=json.loads(pp.read_text());assert s['exit_codes']=={'compiled':0,'original_control':0};out=Path(s['directory']);rows=[]
 def record(lane,seq,phase):
  files=list((out/lane).glob('*-loader-'+str(seq).zfill(2)+'-'+phase+'-*.json'));assert len(files)<=1;return None if not files else json.loads(files[0].read_text())
 for seq in range(16):
  left,right=record('original_control',seq,'entry'),record('compiled',seq,'entry')
  if left is None or right is None:break
  a,b=record('original_control',seq,'return'),record('compiled',seq,'return');row=dict(sequence=seq,args_equal=left['args']==right['args'],entry_frames=[left['frame'],right['frame']],entry_CPU_equal=all(left[k]==right[k]for k in ['PC','task','entry_SP','return_PC','SR','USP','SSP','registers']),both_returned=bool(a and b))
  if a and b:
   row.update(return_frames=[a['frame'],b['frame']],return_CPU_equal=all(a[k]==b[k]for k in ['PC','task','entry_SP','return_PC','SR','USP','SSP','registers']))
   if row['args_equal']and left['args'][2]:
    handle,size=left['args'][2:4];images=[];pointers=[]
    for lane in ['original_control','compiled']:
     image=next((out/lane).glob('*-loader-'+str(seq).zfill(2)+'-return-RAM.bin')).read_bytes();ptr=int.from_bytes(image[handle:handle+4],'big');pointers.append(ptr);assert 0<=ptr<=len(image)-size;images.append(image[ptr:ptr+size])
    row.update(copied_bytes=size,copied_payload_equal=images[0]==images[1],handle_pointers=pointers,payload_sha256=[hashlib.sha256(x).hexdigest()for x in images])
  rows.append(row)
 first=rows[0];assert first['entry_CPU_equal']and first['args_equal']and first['return_CPU_equal']and first['copied_payload_equal']
 image_a=next((out/'original_control').glob('*-loader-00-entry-RAM.bin')).read_bytes();image_b=next((out/'compiled').glob('*-loader-00-entry-RAM.bin')).read_bytes();diff=[i for i,(a,b)in enumerate(zip(image_a,image_b))if a!=b];assert diff and all(0x1b044<=i<0x1b04c for i in diff)
 d=dict(status='terminal_real_game_loader_first_call_boundary_and_payload_match_cost_differs',recorded_at=datetime.now(timezone.utc).isoformat(),capture_proof=str(pp),capture_proof_sha256=sha(pp),rows=rows,first_entry_RAM_only_declared_loader_redirect_diff=True,first_entry_changed_bytes=len(diff),first_call_added_emulated_frames=first['return_frames'][1]-first['return_frames'][0],source_sha256={str(Path(__file__)):sha(__file__)},scope='FreshHLEboot onmatchedlayoutCDIs,identical4000frame recordedbuttonprefix,noRAM/CPUrestore orguestwrites. Readonlyentry/returnCPU/RAMandfirsthelperboundaries captured. Firstcall exactlymatchesreturnedCPU and96350copiedbytes; framecostdifference measuredintherecords. Doesnotproveallcalls orattributefullroutefailure solelytothiscost; laterentries canreflectdifferenttiming/schedules.')
 save(out/'boundary-analysis.json',d);save(ROOT/'verification/native-loader-scan-call-pair-analysis-current.json',d);print(json.dumps(rows[:4],indent=2),flush=True)
if __name__=='__main__':main()
