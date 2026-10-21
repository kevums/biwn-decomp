"""Offline polling-work evidence from completed native queues and original listing.
No model, game or matrix rerun. Instruction counts are not physical-console cycles.
"""
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

def main():
 gp=V/'scene17-wait-final-bridge-v1-current.json';g=read(gp)
 for p,h in g['source_sha256'].items():assert sha(p)==h,p
 rows=read(Path(g['directory'])/'cases.json');a,b=rows[-2:];assert [a['long_completion_polls'],b['long_completion_polls']]==[512,1024]
 assert a['helper_returns']==b['helper_returns']==7 and a['original_case_id']==b['original_case_id']==257
 delta=b['native_instructions']-a['native_instructions'];poll_delta=b['long_completion_polls']-a['long_completion_polls'];assert delta==14336 and poll_delta==512
 session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mp=session/'scene-draw-fullCPU-generation.json';m=read(mp);original=[row for row in m['instructions_decoded']if row['address']in [0x17e5c,0x17e62,0x17ed6,0x17edc]];assert [row['assembly']for row in original]==['tst.l $10a684.l','bne.b $17e5c','tst.l $10a684.l','bne.b $17ed6']
 out=V/'scene17-wait-polling-analysis-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 proof=dict(status='terminal_offline_scene_polling_work_and_preinput_difference_evidence',directory=str(out),native_busy_reads=[512,1024],native_instruction_counts=[a['native_instructions'],b['native_instructions']],native_incremental_instructions_per_extra_busy_read=28,original_decoded_polling_loop_instructions=2,original_loop=original,comparison_isolated_cycle_benchmark=False,frame_difference_causality_proven=False,whole_game_speed_ratio_proven=False,new_game_runs=0,new_predictions=0,new_training=False,next_target='SpecializethephysicalnativeGPUcompletionlooptooriginalTST.L/BNEtimingwhilekeepingunboundedhardwarewait,fullfinallogicalCPUflagsandbusreads.StrictlyinstrumentactualTSTsitesforcontrolledqueues;do notsilentlybypassqueued-readtests.Keepgenericportablehostguardsseparate.Thenmeasureandfixed-input/freshcomparebeforeadoption.',scope=__doc__+'TwoexistingnativecasesdifferinqueuesizebutalsoCCR0vs1/task/stackaddress;bothtakeordinarysamezero/nonzeroCCRlogic,andonly512extraqueueiterationschangeexecutedloopwork. Treat28asanobservedcomponentinstructiondelta,notanisolatedhardwarecyclebenchmarkor14xgameslowdown. Firstfreshvideodiff549precedesheld-inputdiff600;laterfeedbackinputconflatescause. No originalCPU code or game state changed.')
 save(out/'facts.json',proof);proof['source_sha256']={str(p):sha(p)for p in [Path(__file__),gp,Path(g['directory'])/'cases.json',mp,out/'facts.json']};save(V/'scene17-wait-polling-analysis-v1-current.json',proof);print(proof['status'],proof['native_incremental_instructions_per_extra_busy_read'])
if __name__=='__main__':main()
