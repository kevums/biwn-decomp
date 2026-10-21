"""Two explicit 1000-frame component ablations of the native CDI changes.
These controls are not playable/promoted builds. Read-only observer operates
in original mode; neither control installs a new keypad entry. No RAMpatch.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,shutil,subprocess,os
from check_biwn_native_button_digit import ROOT,sha,save
from extract_biwn_stage import swap16

def main():
 out=ROOT/'verification/native-startup-video-isolation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 cold_path=ROOT/'verification/native-disc-cold-boot-current.json';cold=json.loads(cold_path.read_text());build=json.loads(Path(cold['build_proof']).read_text());base=Path(cold['directory']);patches=json.loads(Path(build['patch_manifest']).read_text())['patches'];session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);offset=json.loads((session/'nextstage-mapping.json').read_text())['payload_raw_cdi_offset']
 assert sha(build['original_disc'])==build['original_disc_sha256'];original=Path(build['original_disc'])
 text=(base/'fresh_native_disc_probe.py').read_text();marker="int(disc!=Path("+repr(str(original))+"))";assert text.count(marker)==1;text=text.replace(marker,'0');probe=out/'control_probe.py';probe.write_text(text)
 inputs=out/'ordinary-input.json';save(inputs,dict(windows=[]));jobs=[];state=dict(status='prepared',pid=os.getpid(),directory=str(out),base_cold_proof=str(cold_path),base_cold_proof_sha256=sha(cold_path),frames=1000,controls_are_unpromoted=True,whole_game_complete=False,commands=[])
 def checkpoint():save(out/'protocol.json',state);save(ROOT/'verification/native-startup-video-isolation-active.json',state)
 checkpoint();print(out,flush=True)
 try:
  for name in ['heap-only','startup-copy-only']:
   selected=[p for p in patches if (0x15200<=int(p['address'],16)<0x15600 if name=='heap-only'else int(p['address'],16)in[0x4000,0xff000])]
   assert len(selected)==(7 if name=='heap-only'else 2)
   image=out/(name+'.cdi');shutil.copyfile(original,image)
   with image.open('r+b')as f:
    for p in selected:
     address=offset+int(p['address'],16)-0x4000;old=bytes.fromhex(p['original']);new=bytes.fromhex(p['replacement']);f.seek(address);assert f.read(len(old))==swap16(old);f.seek(address);f.write(swap16(new))
   run=[str(ROOT/'.venv/bin/python'),str(probe),'--boot','hle','--frames','1000','--core',str(ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source/virtualjaguar_libretro.dylib'),'--disc',str(image),'--frame-controller-script',str(inputs),'--no-publish','--output',str(out/name)]
   log=(out/(name+'.log')).open('w');child=subprocess.Popen(run,stdout=log,stderr=subprocess.STDOUT);jobs.append((name,child,log));state['commands'].append(dict(name=name,pid=child.pid,command=run,selected_patches=selected,image_sha256=sha(image)))
  state['status']='running_control_pair';checkpoint()
  for name,child,log in jobs:assert child.wait()==0,(name,out/(name+'.log'));log.close()
  refs={lane:json.loads((base/lane/'report.json').read_text())['frames'][:1000]for lane in ['reference','candidate']};rows=[]
  for name,_,_ in jobs:
   report=json.loads((out/name/'report.json').read_text());frames=report['frames'];obs=json.loads((out/name/'native-observation.json').read_text());assert len(frames)==1000 and not obs['errors']and not obs['copy_errors']and not obs['calls']
   equal={lane:sum(a['video_sha256']==b['video_sha256']for a,b in zip(frames,reference))for lane,reference in refs.items()}
   mismatch={lane:[a['frame']for a,b in zip(frames,reference)if a['video_sha256']!=b['video_sha256']]for lane,reference in refs.items()}
   rows.append(dict(name=name,video_equal_frames=equal,video_mismatch_frames=mismatch,observation=obs))
  save(out/'comparison.json',rows)
  state.update(status='terminal_control_pair_observed',results=rows,runtime_source_sha256={str(p):sha(p)for p in [probe,inputs,Path(__file__)]},interpretation='Classify from recorded control comparisons; no automatic claim of timing root cause.')
  checkpoint();save(ROOT/'verification/native-startup-video-isolation-current.json',state);print(json.dumps([dict(name=x['name'],equal=x['video_equal_frames'])for x in rows]),flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));checkpoint();raise
if __name__=='__main__':main()
