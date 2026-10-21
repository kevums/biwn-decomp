"""Same larger layout with only core/variadic redirects restored, raw disc."""
import json,os,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
from extract_biwn_stage import swap16
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def main():
 bp=ROOT/'verification/native-core-format-disc-build-current.json';build=json.loads(bp.read_text());rp=ROOT/'verification/native-core-format-long-route-current.json';route=json.loads(rp.read_text());parent=Path(route['directory']);out=ROOT/'verification/native-core-raw-layout-control'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);disc=out/'same-layout-original-core-raw-control.cdi';shutil.copyfile(build['derived_disc'],disc)
 session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);offset=json.loads((session/'nextstage-mapping.json').read_text())['payload_raw_cdi_offset'];rows=json.loads(Path(build['patch_manifest']).read_text())['patches'];intervals=[]
 with disc.open('r+b')as stream:
  for pc in [0x1b29c,0x1b45a]:
   row=next(x for x in rows if int(x['address'],16)==pc);old=bytes.fromhex(row['original']);new=bytes.fromhex(row['replacement']);at=offset+pc-0x4000;stream.seek(at);assert stream.read(len(new))==swap16(new);stream.seek(at);stream.write(swap16(old));intervals.append((at,at+len(old)))
  stream.flush();os.fsync(stream.fileno())
 changed=0;pos=0
 with disc.open('rb')as a,Path(build['derived_disc']).open('rb')as b:
  while True:
   left=a.read(1048576);right=b.read(1048576);assert len(left)==len(right)
   if not left:break
   for i,(x,y)in enumerate(zip(left,right)):
    if x!=y:assert any(lo<=pos+i<hi for lo,hi in intervals);changed+=1
   pos+=len(left)
 assert 0<changed<=12
 src=(parent/'fresh-route.py').read_text();line=next(x for x in src.splitlines()if x.startswith('        observer_payload=c.create_string_buffer('));src=src.replace(line,'        observer_payload=c.create_string_buffer(Path('+repr(build['component'])+').read_bytes())');probe=out/'probe.py';compile(src,str(probe),'exec');probe.write_text(src)
 command=list(next(row['command']for row in route['commands']if row['lane']=='core'));command[2]=str(probe);command[command.index('--frames')+1]='9000';command[command.index('--disc')+1]=str(disc);command[command.index('--output')+1]=str(out/'control')
 state=dict(status='running_same_layout_raw_core_control',pid=os.getpid(),directory=str(out),command=command,disc=str(disc),disc_sha256=sha(disc),core_build=str(bp),core_build_sha256=sha(bp),actual_changed_CDI_bytes=changed,declared_changed_bytes=12,change_scope='Only original core/variadic6byte entries restored. Same15408payload,16384reservation,heap162DC0,24KBstaging,othercompiledhelpers. No selector repairs,guestRAMwrites orcheckpoint restores.',source_sha256={str(p):sha(p)for p in [Path(__file__),rp,probe]})
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-core-raw-layout-control-active.json',state)
 mark();print(out,flush=True)
 with(out/'control.log').open('w')as log:
  child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;mark();code=child.wait()
 state.update(status='terminal_same_layout_raw_core_control_classified'if not code else'terminal_failed',exit_code=code)
 if not code:
  report=json.loads((out/'control/report.json').read_text());obs=json.loads((out/'control/gameplay-observation.json').read_text());last=report['frames'][-1];state.update(executed_frames=report['executed_frames'],first_scene_change=report['scene_change_frame'],final_fields={k:last[k]for k in ['raw_player_X','raw_player_Z','scene_word','player_mode_word','floor_word','CPU']},observation=obs,report_sha256=sha(out/'control/report.json'))
 mark()
 if not code:save(ROOT/'verification/native-core-raw-layout-control-current.json',state)
 print(json.dumps({k:state.get(k)for k in ['status','first_scene_change','final_fields']}),flush=True);assert not code
if __name__=='__main__':main()
