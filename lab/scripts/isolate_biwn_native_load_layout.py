"""Disc-delivered loader-entry toggle; identical layout/startup and fixed pad.
No in-game guest edits, forced continuations or checkpoint restores.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,os,shutil,subprocess,argparse
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
from extract_biwn_stage import swap16

def classify(out,state,fixed):
 fd=Path(fixed['directory'])
 assert sha(state['disc'])==state['disc_sha256']
 assert sha(state['fixed_pair_proof'])==state['fixed_pair_proof_sha256']
 report=json.loads((out/'control/report.json').read_text());obs=json.loads((out/'control/gameplay-observation.json').read_text());assert report['executed_frames']==29783 and not(obs['errors']or obs['copy_errors']or obs['repair_code_errors'])
 assert obs['native_C_loader_calls']==0 and obs['old_loader_body_steps']>0 and obs['loader_entries']>0
 assert obs['native_C_acquire_calls']==obs['acquire_entries']>0
 assert obs['native_C_allocate_calls']>0 and obs['native_C_resource_release_calls']==obs['resource_release_entries']
 left=json.loads((fd/'native26_fixed/report.json').read_text())['frames'];right=json.loads((fd/'native28_fixed/report.json').read_text())['frames'];rows=report['frames'];assert len(rows)==len(left)==len(right)==29783
 assert all(x['fixed_buttons']==y['fixed_buttons']==z['fixed_buttons']for x,y,z in zip(left,right,rows));assert all(x['input_pressed_mask']==y['input_pressed_mask']and x['input_seen_mask']==y['input_seen_mask']for x,y in zip(right,rows))
 fields=['raw_player_X','raw_player_Z','scene_word','player_mode_word','floor_word','video_sha256','cumulative_nonzero_audio_samples','GPU','DSP']
 compare=lambda a,c:{k:dict(different_frames=sum(x[k]!=y[k]for x,y in zip(a,c)),first_different_frame=next((x['frame']for x,y in zip(a,c)if x[k]!=y[k]),None))for k in fields}
 comparisons=dict(control_vs_native26=compare(rows,left),control_vs_native28=compare(rows,right));state.update(status='terminal_same_layout_loader_toggle_fixed_control_classified',observation=obs,comparisons=comparisons,frames=29783,report_sha256=sha(out/'control/report.json'),control_PCM_equal_native26=sha(out/'control/frontend-PCM.s16le')==sha(fd/'native26_fixed/frontend-PCM.s16le'),control_PCM_equal_native28=sha(out/'control/frontend-PCM.s16le')==sha(fd/'native28_fixed/frontend-PCM.s16le'),final_fields={k:rows[-1][k]for k in ['raw_player_X','raw_player_Z','player_mode_word','floor_word','scene_word']},scope='Only the8byte loaderentryredirect is restored before fresh HLE boot. Same native28payload,7680heapreserve,startup,otherhelpers and29783frame buttons; actualcallbacks checked. Compiledacquire remainsenabled. Differences measure the loaderimplementation and its executioncost together; they do not distinguish algorithmicerrors from timing/IRQ interactions or prove arbitraryinput/physical equivalence.')
 save(out/'protocol.json',state);save(ROOT/'verification/native-load-layout-control-active.json',state);save(ROOT/'verification/native-load-layout-control-current.json',state);print(state['status'],json.dumps(comparisons),flush=True)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--analyze-existing',type=Path);args=parser.parse_args()
 if args.analyze_existing:
  out=args.analyze_existing.resolve();state=json.loads((out/'protocol.json').read_text());fixed=json.loads(Path(state['fixed_pair_proof']).read_text())
  state['analysis_correction']='Reanalyzed existing saved compact control output without rerunning emulation.'
  state['original_driver_snapshot']=str(out/'driver-as-run.py');state['analysis_driver_sha256']=sha(__file__);state['native_child_exit_code']=0
  classify(out,state,fixed);return
 bp=ROOT/'verification/native-load-disc-build-current.json';b=json.loads(bp.read_text());fixedp=ROOT/'verification/native-load-fixed-route-current.json';fixed=json.loads(fixedp.read_text());assert fixed['status']=='terminal_equal_duration_fixed_pad_pair_pending_analysis';fd=Path(fixed['directory']);assert sha(b['derived_disc'])==b['derived_disc_sha256']
 out=ROOT/'verification/native-load-layout-control'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 patch=next(x for x in json.loads(Path(b['patch_manifest']).read_text())['patches']if int(x['address'],16)==0x1b044);original=bytes.fromhex(patch['original']);replacement=bytes.fromhex(patch['replacement']);assert len(original)==len(replacement)==8
 session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'nextstage-mapping.json').read_text());offset=mapping['payload_raw_cdi_offset']+0x1b044-0x4000
 disc=out/'BIWN-23-native28-layout-original-loader-control.cdi';shutil.copyfile(b['derived_disc'],disc)
 with disc.open('r+b')as f:f.seek(offset);assert f.read(8)==swap16(replacement);f.seek(offset);f.write(swap16(original));f.flush();os.fsync(f.fileno())
 changes=[];pos=0
 with Path(b['derived_disc']).open('rb')as a,disc.open('rb')as c:
  while True:
   left=a.read(1048576);right=c.read(1048576);assert len(left)==len(right)
   if not left:break
   if left!=right:
    for i,(x,y)in enumerate(zip(left,right)):
     if x!=y:assert offset<=pos+i<offset+8;changes.append(pos+i)
   pos+=len(left)
 assert changes and pos==disc.stat().st_size
 source=fd/'fresh-fixed-free-route.py';assert sha(source)==fixed['source_sha256'][str(source)]
 baseline=json.loads((ROOT/'verification/native-resource-disc-build-current.json').read_text());new_predicate='disc==Path('+repr(b['derived_disc'])+')';control_predicate='disc!=Path('+repr(baseline['derived_disc'])+')';text=source.read_text();assert text.count(new_predicate)==2;text=text.replace(new_predicate,control_predicate)
 probe=out/'fresh-layout-control.py';probe.write_text(text);compile(text,str(probe),'exec')
 oldcmd=next(x['command']for x in fixed['commands']if x['lane']=='native28_fixed');cmd=list(oldcmd);cmd[2]=str(probe);cmd[cmd.index('--disc')+1]=str(disc);cmd[cmd.index('--output')+1]=str(out/'control')
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),build_proof=str(bp),build_proof_sha256=sha(bp),fixed_pair_proof=str(fixedp),fixed_pair_proof_sha256=sha(fixedp),disc=str(disc),disc_sha256=sha(disc),parent_disc_sha256=b['derived_disc_sha256'],disc_change_scope='Only8byte loader redirect restored to original entry bytes; same native28linkedpayload7680reserve/startupcopy and allotherredirects.',declared_toggle_CDI_offset=offset,actual_changed_CDI_bytes=len(changes),command=cmd,source_sha256={str(p):sha(p)for p in [Path(__file__),source,probe,Path(b['patch_manifest'])]},host_guest_RAM_writes=0,checkpoint_restores=0,host_CPU_seeds=0,whole_game_complete=False)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-load-layout-control-active.json',state)
 mark()
 try:
  with(out/'control.log').open('w')as log:
   child=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT);state.update(status='running_same_layout_original_loader_fixed_control',child_pid=child.pid);mark();print('PID',child.pid,flush=True);code=child.wait()
  assert code==0,code
  state['native_child_exit_code']=code;mark();classify(out,state,fixed)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
