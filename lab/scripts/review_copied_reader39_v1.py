"""Review one ordinary copied-model briefing against its exact supplied snapshot."""
import shutil
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha

def main():
 pointer=P/'workbench/verification/Deck-status-live-v39-current.json';job=read(pointer);assert job['status']=='terminal_streamed_current_Reader_pending_source_review'and job['new_predictions']==1
 folder=Path(job['directory']);r=read(folder/'response.json');text=(folder/'response.txt').read_text();e=read(folder/'evidence.json');assert text==r['text'] and r['seconds']==11.92
 assert e['fixed_input_video_differences']is None and e['control_layout_changes']is None
 assert e['latest_source_development']['profile']=='deck-shared-v35-local-record-prologue-v1' and e['latest_source_artifact_kind']=='source_component_prototype'
 assert e['experimental_candidate']['candidate_frames']==25012 and e['experimental_candidate']['control_frames']==24966
 assert e['display_source']['final_native_display_returns']==4777 and e['experimental_candidate']['differing_video_frames']==8717
 assert e['measured_heap_while_outer_active']==dict(candidate=14320,control=14320)
 words=len(text.split());assert words<=150 and len(text.strip().split('\n\n'))==2
 assert all(s in text for s in ['4,777','8,717','168/208','14,320','final video agrees','preview remains unchanged','not a disc image','authored by the local model','coordinator-authored disc source','same-console source rebuild remains unproven','no new weight updates','both base and adapter passing zero of four'])
 assert 'not a disc image' in text and 'prototype'in text and 'sampled free heap while the outer task was active'in text
 out=V/'copied-Reader39-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'actual-run';shutil.copytree(folder,snap)
 rootpre=read(V/'Deck-status-live-v39-current.json');assert rootpre['status']=='terminal_current_Reader_evidence_preflight_zero_predictions'
 copiedpre=[p for p in (P/'workbench/runs').glob('Deck-status-live-v39-*/protocol.json')if read(p)['status']=='terminal_current_Reader_evidence_preflight_zero_predictions'];assert len(copiedpre)==1
 for name,source in [('Root-preflight',Path(rootpre['directory'])),('copied-preflight',copiedpre[0].parent)]:shutil.copytree(source,out/name)
 report=ROOT/'reports/BIWN Copied Local Reader39 Briefing Review.txt'
 report.write_text('BIWN — ordinary local briefing check\n\nOne actual generation through the moved package’s ordinary reader launcher used the configured copied-model identifier. Generation11.92seconds;'+str(words)+'words,two paragraphs. Timings exclude model setup/evidence retrieval and any resource queue;total click-to-completion was not instrumented. Exact request,stream and raw response are preserved.\n\n'
  'The response correctly reports v34display4777,video8717,finalvideoagreement,stack168/208 and sampledouter-activeheap14320. It identifies v35as a source/component prototype rather than a disc,distinguishes local block and coordinator disc source,preserves unchangedpreview and unproven same-console rebuild,and includes earlier base0/4adapter0/4quality failure with no new weightupdates. These supplied-snapshot factual claims and requested150wordformat pass. This is one development briefing,not heldout/general quality or weight-training gain. Earlier hybrid-code attribution remains documented in the source evidence;the reply does not claim sole authorship of every linked component.\n\n'
  'Reader39fixes nullable pending-comparison handling and explicitly includes the verified local block facts. Root and copied no-inference preflights passed on the same game/model snapshot. The ordinary launcher also preserves different/busy loaded models before setup. Native LM Studio Chat rendering of copied weights remains unverified.\n\nRAW RESPONSE\n'+text+'\n')
 facts=dict(status='terminal_copied_Reader39_current_snapshot_facts_artifact_authorship_and_format_pass',directory=str(out),report=str(report),original_run_directory=str(folder),actual_predictions=1,seconds=11.92,words=words,max_words=150,word_limit_pass=True,two_paragraphs=True,artifact_type_pass=True,code_authorship_statement_present=True,supplied_snapshot_factual_claims_approved=True,complete_requested_briefing_approved=True,provided_candidate_profile='v34',provided_source_prototype_profile='v35',ordinary_copied_launcher_verified=True,Root_evidence_preflight_verified=True,copied_evidence_preflight_verified=True,broader_quality_approved=False,held_out_benchmark=False,new_training=False,optimizer_updates=0,native_Chat_display_verified=False,model_identifier=job['model_identifier'],source_sha256={str(p):sha(p)for p in [Path(__file__),ROOT/'scripts/run_deck_status_live_v39.py',ROOT/'scripts/portable_biwn_entry_v16.py',*list(snap.rglob('*')),*list((out/'Root-preflight').rglob('*')),*list((out/'copied-preflight').rglob('*'))]if p.is_file()})
 save(out/'review.json',facts);save(V/'copied-Reader39-reviewed-v1-current.json',facts)
 for p in [*map(Path,facts['source_sha256']),out/'review.json',report,V/'copied-Reader39-reviewed-v1-current.json']:
  dest=P/'workbench'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 print(facts['status'],words,flush=True)
if __name__=='__main__':main()
