"""Consolidate actual moved-package results without rerunning passed work."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):
 with Path(p).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def main():
 now=datetime.now(timezone.utc);stamp=now.strftime('%Y%m%dT%H%M%S.%fZ');out=V/'portable-sdk-workbench-review'/stamp;out.mkdir(parents=True);p=Path(read(V/'portable-sdk-workbench-current.json')['package'])
 initial=read(V/'portable-assistant-launchers-current.json');third=read(V/'portable-advertising-launcher-current.json');training=read(V/'portable-training-update-current.json');integrity=read(V/'portable-sdk-model-integrity-current.json');native=read(V/'portable-native-build-current.json');secondary=read(p/'portable-secondary-test-current.json');boundaries=read(p/'portable-boundaries-current.json')
 assert initial['both_actual_launcher_predictions_returned']and initial['daily_default_restored']and third['daily_default_restored']and training['completed_updates']==1 and training['daily_default_restored']
 assert integrity['package']==str(p)and integrity['dependency_files_verified']==10009 and integrity['weight_shards_verified']==10 and native['package']==str(p)and native['binary_bytes']==1588
 main_dir=next(d for d in sorted((p/'test-results').glob('servers-*'),reverse=True)if(d/'calls.json').exists()and d.name.startswith('servers-20261019T1225'))
 main_calls=read(main_dir/'calls.json');assert len(main_calls)==8 and all(not x['isError']for x in main_calls)
 assert len({x['name']for x in main_calls})==7 and len(secondary['calls'])==3
 assert len(boundaries['controls'])==5 and all(x['rejected']for x in boundaries['controls'])and boundaries['copied_certificate_restored_and_rechecked']
 sources=[('game',read(Path(initial['directory'])/'game-result.json')),('advertising-reviewer',read(Path(initial['directory'])/'advertising-result.json')),('advertising-research',read(Path(third['directory'])/'result.json'))]
 rows=[];archive=ROOT/'runs/portable-inference-archive'/stamp;archive.mkdir(parents=True)
 for label,state in sources:
  source=Path(state['directory']);dest=archive/label;shutil.copytree(source,dest);response=read(dest/'response.json');audit=read(p/('path-audit-'+str(state['pid'])+'.json'));assert not audit['denied']and state['SDK_module'].startswith(str(p/'runtime/.venv'))
  model=state['model_key'];assert response['model_info']['modelKey']==model and response['load_config']['contextLength']==32768
  raw=read(dest/'protocol.json');view=dict(raw,directory=str(dest),original_external_directory=str(source),raw_as_run_protocol=str(dest/'protocol.json'));save(V/('portable-'+label+'-inference-current.json'),view)
  rows.append(dict(role=label,directory=str(dest),external_directory=str(source),model_key=model,seconds=state['seconds'],words=state['words'],raw_response=response['content'],audit=str(p/('path-audit-'+str(state['pid'])+'.json')),original_access_denials=0,SDK=state['SDK_module'],quality_review='Scoped current-game answer accepted'if label=='game'else'Partial: caught manipulation/causality errors but omitted measurement timing'if label=='advertising-reviewer'else'Partial: disclosure manipulation and post-ad timing correct; omits randomized between-participant beneficiary framing'))
 bindings=read(p/'portable-model-bindings.json');registration=read(p/'model-registration-receipt.json')
 for label,binding in bindings['models'].items():
  link=Path.home()/'.lmstudio/models/local'/('portable-ailab-'+bindings['portable_package_id']+('-daily'if label=='daily_base'else'-reviewer'))
  assert link.is_symlink()and link.resolve()==(p/binding['relative_weights']).resolve()
 save(out/'actual-model-outputs-reviewed.json',rows)
 correction='Study 2A randomized beneficiary framing between participants (consumer, company, or other) and varied three disclosure formats within participants, with ad order randomized (PDF p. 9). AI aversion was measured after the ads and follow-up items using four reverse-coded seven-point items (PDF pp. 9, 20); it was neither randomized nor established as a pretreatment baseline, so its association with attitudes does not establish that aversion causes them.'
 save(out/'coordinator-corrected-advertising-answer.json',dict(text=correction,source='Schreiner supplied PDF pages9 and20, actual copied MCP evidence',source_sha256='7da27946e1061ed9ab195c9a14c0be28f648d2e719fafff7236dd48b93248f71',coordinator_edited=True,unchanged_local_output=False,heldout=False))
 # Keep earlier source lists intact before adding the three actual SDK transcripts.
 indexlist=ROOT/'config/current-model-work-sources.json';shutil.copy2(indexlist,out/'previous-model-work-source-list.json');current=read(indexlist)
 additions=[['portable-game-inference-current.json','Moved package: actual copied SDK Game Assistant, scoped rebuild answer'],['portable-advertising-research-inference-current.json','Moved package: actual normal Advertising launcher; between-participant manipulation omitted'],['portable-advertising-reviewer-inference-current.json','Moved package: actual trained Reviewer launcher; timing correction omitted']]
 assert not any(row[0]in{x[0]for x in current}for row in additions)
 save(indexlist,additions+current)
 subprocess.run([str(ROOT/'.venv/bin/python3.12'),str(ROOT/'scripts/show_current_model_work_v4.py'),'--no-open'],check=True,capture_output=True,text=True)
 index=read(V/'current-model-work-index-v4-current.json');assert index['saved_prompt_or_transcript_records']==71
 profile=dict(status='planned_future_hardware_acceptance_recipe_not_activated',target=dict(description='User-planned Mac Studio',memory_GiB=256),starting_profile=dict(context_length=32768,workers=1,model_key='local/advertising-qwen38',roles='Sequential fresh contexts; base Researcher/Educator plus optional experimental step8 Reviewer'),candidate_after_baseline=dict(context_length=32768,workers=2),next_context_candidate=dict(context_length=65536,workers=1),acceptance=['Run all three portable assistant launchers and inspect original source support, not only response speed.','Verify copied model hashes and reproduce the checked1588byte navigation build.','Repeat the copied reviewed-data training test; never mix its experimental adapter into daily models.','Increase one capacity setting at a time; measure model load, first-token latency, token rate, memory pressure and failures on actual target.','Broader game reconstruction, hardware behavior and model quality require separate evidence.'],current_machine_proves_future_capacity=False)
 save(out/'studio256-acceptance-profile.json',profile);(p/'profiles').mkdir(exist_ok=True);save(p/'profiles/studio256-acceptance-profile.json',profile)
 guide=f'''LOCAL AI LAB — MOVED PACKAGE TEST

Package: {p}

Keep LM Studio installed and its local server running on 127.0.0.1:1234.
After moving this folder, double-click Restore Local AI Lab.command once.
Then double-click one of these launchers and type a task:
  Run Game Assistant.command
  Run Advertising Assistant.command
  Load Advertising Reviewer.command (experimental trained step8)
Each launcher selects its copied model at32Kcontext/one worker. Initial model
loading takes extra time. Questions and responses appear in Terminal, with exact
transcripts saved under runs. This test does not demonstrate native LM Studio
Chat streaming. The installed native Chat/provider workflow still needs review.
The setup registers only its own named model resources in the host LM Studio.

All three launchers returned real answers after this folder was moved. The test
controller restored the ordinary daily27Bmodel after the tests. Game answer:
{rows[0]['seconds']:.2f}s; Advertising base:{rows[2]['seconds']:.2f}s;
trained Reviewer:{rows[1]['seconds']:.2f}s. These are generation times for three
short questions, excluding model load; they are not a throughput benchmark.

The copied SDK/dependencies(10,009files),39modelresources/10shards(46.80GB),four
MCPservers and ten tested tool kinds work in the declared scopes. The copied
68000toolchain rebuilt the checked1,588byte navigation group byte-identically.
One actual copied-pipeline training update completed on a225token padded batch
from the existing reviewed dataset; its adapter is unpromoted and not selected.
This is not a full training rerun, a worst-case memory test or a quality gain.

Advertising limitations remain:the trained Reviewer omitted the measurement
timing correction;the base answer omitted the randomized beneficiary framing.
The coordinator-checked correction is in the detailed review. Always inspect
the source sections. Previous and current prompts/responses are retained here:
{index['report']}

The workbench subfolder contains advanced/historical launchers and development
files; all41legacy launchers and every tool behavior are not verified. System
macOS and the installed LM Studio host service remain external dependencies.
No off-machine/future256GBperformance proof is claimed. The planned acceptance
profile is under profiles/studio256-acceptance-profile.json.

BIWN remains a partial readable-source reconstruction. The30,036byte integrated
experiment has prior gameplay evidence; this turn adds no new game behavior.
The visible keyboard preview stays on its existing version:click it,holdC+Up
to run;Ppauses/resumes. Full same-console source rebuild remains unfinished.

Detailed reviewed evidence: {out/'review.txt'}
'''
 (out/'quick-start.txt').write_text(guide);(p/'READ ME FIRST.txt').write_text(guide);(ROOT/'reports/Portable Setup Test.txt').write_text(guide)
 alias=ROOT/'Portable Setup Test'
 if alias.is_symlink():assert alias.resolve()==p
 else:assert not alias.exists();alias.symlink_to(p,target_is_directory=True)
 report=f'''PORTABLE SDK/CLI/TRAINING WORKBENCH REVIEW\n{now.isoformat()}\n\nMoved physically:{p}\nThree actual launchers, three raw predictions; copied SDKclient and model-weight links verified.\n'''
 for row in rows:report+='\n'+row['role']+': '+row['quality_review']+'\n'+row['raw_response']+'\n'
 report+='\nCoordinator correction (not unchanged local output):\n'+correction+'\n\nAll8mainMCPcalls/7kinds passed after move;run later failed on missing secondary-task payload.1,057file evidence closure copied raw;3secondaryget/statuscalls then pass. No fresh CPU rerun or lowering inferred from certificate reuse.\nFive boundary negatives reject;v6testharness accidentally rebased its originfixture before opening it,so v7uses rawJSONDecoder originfixture. First v6failure is retained and not counted as a guard failure/pass.\nCopied training:one real update,225paddedtokens,2layers/rank8;three validation batches. Uses existingdata/base,not a fresh quality experiment. Adapter remains unpromoted.\nPostmove dependency/model hashes and1588byte sourcebuild pass. Samehost/systemlibs/LMStudioexternal. NativeChat,current easyuse and remaining legacy launchers not fully proven. Full BIWN decompilation/sameconsolebuild and futurehardware capacity remain incomplete.\n'
 (out/'review.txt').write_text(report)
 state=dict(status='terminal_moved_portable_SDK_three_launchers_training_update_scoped_pass_quality_partial',directory=str(out),package=str(p),actual_predictions=3,actual_training_updates=1,training_padded_tokens=225,SDK_dependency_files_verified=10009,model_resources_verified=39,weight_shards_verified=10,main_MCP_calls=8,main_tool_kinds=7,secondary_read_calls=3,total_tool_kinds=10,boundary_controls=5,native_binary_bytes=1588,native_binary_sha256=native['binary_sha256'],quality_gain_claim=False,trained_Reviewer_timing_omission=True,base_beneficiary_omission=True,native_Chat_verified=False,full_portable_workflow_complete=False,whole_game_complete=False,physical_console_verified=False,future_hardware_verified=False,review=str(out/'review.txt'),guide=str(ROOT/'reports/Portable Setup Test.txt'),model_work_index=index['report'],saved_prompt_or_transcript_records=71,readme=str(p/'READ ME FIRST.txt'),source_records=dict(initial=initial,third=third,training=training,integrity=integrity,native=native,secondary=secondary,boundaries=boundaries),scope=__doc__)
 save(out/'protocol.json',state);save(V/'portable-sdk-workbench-reviewed-current.json',state);print(json.dumps({k:state[k]for k in ['status','directory','actual_predictions','actual_training_updates']}))
if __name__=='__main__':main()
