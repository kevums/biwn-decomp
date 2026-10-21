"""Publish readable caller, actual local failure, linked pipeline and menu."""
import hashlib,json,os,re,shutil,sqlite3,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification';RT=Path.home()/'.lmstudio/local-ai-lab'
sys.path.insert(0,str(ROOT));from reference_mcp_bridge import ReferenceBridge
def read(p):return json.loads(Path(p).read_text())
def save(p,d):Path(p).write_text(json.dumps(d,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 selected=read(V/'Deck-coordinate-source-candidate-current.json');source=Path(selected['candidate']);assert sha(source)==selected['candidate_sha256']
 component=read(selected['receipt']);assert component['status']=='terminal_readable_Deck_coordinate_full_CPU_component_pass'and component['completed']==576 and component['instruction_coverage']==[87,87]and component['host_error_cases']==87
 for p,h in component['source_bindings'].items():assert sha(p)==h,p
 edges=read(V/'Deck-coordinate-boundaries-current.json');assert edges['cases']==128 and edges['candidate_sha256']==sha(source)
 qualification=read(V/'Deck-coordinate-checker-qualification-current.json');assert len(qualification['mutations'])==4 and all(x['rejected']for x in qualification['mutations'])
 for data in [edges,qualification]:
  for p,h in data['source_sha256'].items():assert sha(p)==h,p
 pipeline=read(V/'Deck-coordinate-pipeline-current.json');assert pipeline['status']=='terminal_readable_Deck_coordinate_source_world_loop_match'and pipeline['candidate_sha256']==sha(source)
 linked=read(pipeline['integration_proof']);assert sha(pipeline['integration_proof'])==pipeline['integration_proof_sha256']
 assert linked['readable_Deck_coordinate_calls']==17 and linked['paired_checkpoints']==31 and linked['render_iterations']==16
 assert all(pair['native']==pair['C']for pair in linked['phases'].values())
 assert linked['results'][1]['original_CPU_instructions']==linked['results'][1]['original_GPU_opcodes']==0
 assert len(linked['results'][1]['events'])==149
 for p,h in linked['source_sha256'].items():assert sha(p)==h,p
 trial=read(V/'Deck-coordinate-local-current.json');assert trial['status']=='terminal_local_Deck_coordinate_rejected_after_one_repair'and trial['actual_predictions']==2
 run=Path(trial['directory']);local=[]
 for role in ['author','repair']:
  verdict=read(run/role/'verifier.json');response=read(run/role/'response.json')
  assert not verdict['verified']and verdict['completed']==0 and verdict['actual_counterexample']['RAM_differences']
  local.append(dict(role=role,seconds=response['seconds'],model=response['request']['model'],usage=response['usage'],context_preflight=response['context_preflight'],rejected_at_case=0))
 def tokens(p):return re.sub(r'\s+','',re.sub(r'/\*[\s\S]*?\*/|//[^\n]*','',p.read_text()))
 assert tokens(run/'author/candidate.c')==tokens(run/'repair/candidate.c')
 confirmed=read(V/'deck-coordinate-raw-repair-v3-confirmation/protocol.json');assert confirmed['status']=='terminal_component_rejected'and confirmed['completed']==0
 out=V/'deck-coordinate-recovery'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 # Explicit finite artifact set. Do not recursively snapshot old publications.
 files={Path(__file__),source,Path(selected['receipt']),V/'Deck-coordinate-source-candidate-current.json',V/'Deck-coordinate-local-current.json',V/'Deck-coordinate-boundaries-current.json',V/'Deck-coordinate-checker-qualification-current.json',V/'Deck-coordinate-pipeline-current.json',Path(pipeline['integration_proof']),Path(pipeline['runner']),Path(linked['directory'])/'report.json',Path(linked['directory'])/'native-final-RAM.bin',Path(linked['directory'])/'C-final-RAM.bin'}
 for p in component['source_bindings']:files.add(Path(p))
 for d in [edges,qualification]:
  for p in d['source_sha256']:files.add(Path(p))
 for p in linked['source_sha256']:files.add(Path(p))
 for p in run.rglob('*'):
  if p.is_file()and p.suffix in ['.json','.txt','.c','.log']:files.add(p)
 for folder in [Path(selected['receipt']).parent,Path(edges['directory']),Path(qualification['directory']),Path(pipeline['directory']),V/'deck-coordinate-raw-repair-v3-confirmation',V/'deck-coordinate-positive-v3-confirmation',V/'deck-coordinate-coordinator-check-v2',V/'deck-coordinate-source-pipeline/20261019T164859.848023Z']:
  for p in folder.rglob('*'):
   if p.is_file()and p.suffix in ['.json','.txt','.c','.h','.py','.log']:files.add(p)
 for name in ['run_local_deck_coordinate_v1.py','run_local_deck_coordinate_v2.py','check_deck_coordinate_source_v1.py','check_deck_coordinate_source_v2.py','check_deck_coordinate_source_v3.py','check_deck_coordinate_pipeline_v1.py','check_deck_coordinate_pipeline_v2.py']:
  files.add(ROOT/'scripts'/name)
 for p in (ROOT/'projects/black-ice-white-noise/restoration/experimental/deck-coordinate-update').iterdir():
  if p.is_file():files.add(p)
 snapshot=out/'as-run';snapshot.mkdir();bound=[]
 for p in sorted({p.resolve()for p in files}):
  digest=sha(p);target=snapshot/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,target);assert sha(target)==digest
  bound.append(dict(source=str(p),snapshot=str(target),sha256=digest))
 save(out/'bound-files.json',bound)
 summary=dict(status='terminal_readable_Deck_coordinate_recovered_coordinator_source_local_trial_rejected',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),source=str(source),source_sha256=sha(source),original_interval=['0x11D1A','0x11E64'],original_bytes=330,original_instruction_locations=87,component_cases=576,boundary_witnesses=128,host_error_cases=87,source_mutations_rejected=4,connected_source_calls=17,render_iterations=16,paired_checkpoints=31,GPU_commands_in_connected_test=149,authorship=selected['authorship'],local_predictions=local,actual_local_predictions=2,local_repair_executable_code_unchanged=True,raw_local_source_accepted=False,new_optimizer_updates=0,native_Chat_verified=False,native_disc_changed=False,native_code_bytes_still=34784,ordinary_native_E26C_coverage_still_zero=True,natural_unpatched_gameplay_verified=False,experimental_selector_count13_overlay_retained=True,whole_game_complete=False,local_transcript=str(run/'prompts-and-responses.txt'),component_receipt=selected['receipt'],integration_proof=pipeline['integration_proof'],limits='Complete structured C caller with explicit dependencies. Component uses declaredGPUresultfixture and originalnative multiply; linkedpipeline uses existing sourceCPU/GPU math/renderer with experimentalassetpatch,capturedRAM,suppliedworldentry/two-context ring/BIOSdiscproviders. No nativeconsolebinaryintegration,untouchedgamepath,IRQ/timing/physicalhardware orwholegameproof. FailedglueV1 hostreturnreadlatching,metadatawrapper andfirstintegrationRTSboundary attempt retained. Newv2localpromptpreparedwithaddressing/stack/branchguidance,notyetinference-tested.')
 report=ROOT/'reports/Deck C-Space Coordinate Recovery.txt'
 report.write_text('DECK/C-SPACE COORDINATE SOURCE RECOVERY\n\nRecovered the complete 330-byte original caller at 11D1A..11E64 as grouped C, with no per-instruction switch. It wraps angles, submits a GPU transform, checks an unsigned squared-distance boundary and updates signed view offsets. CPU registers, flags, private stack and original helper frames are retained. Source is coordinator-authored.\n\n576 original-CPU comparisons cover all 87 instruction locations and both stack banks/all incoming CCR values. 128 additional exact-boundary/sign/wrap witnesses pass; 87 host-error cases pass. Four compiled source defects are rejected. Component E26C is an explicit GPU-result fixture; E540 executes original CPU instructions as a separate dependency.\n\nThe new body replaces the old instruction cases in an isolated source Deck/C-Space pipeline. It executes 17 times over 16 rendering iterations, exits, restores the cache and resumes the world task. All 31 native/C checkpoints match, including full CPU/RAM and checked device/logical GPU state; 149 GPU commands execute with zero original CPU/GPU on the C path. This uses the retained experimental selector/count13 patch, supplied entry/ring and BIOS/disc providers. It is not unpatched natural gameplay or physical-console proof. The current experimental disc remains at 34,784 native code bytes; this hosted C recovery has not been added to it.\n\nActual local-model test: Author 163.36 seconds; sole informed repair 194.38 seconds. Both fail case 0. After comments/whitespace are removed, their executable C is identical. The Author confuses absolute-memory operands with constants and mishandles flags, branch direction, stack reclamation and successful-return PC. No raw local source was adopted and no training update occurred. The coordinator wrote the accepted implementation separately.\n\nCoordinator issues retained: V1 host error glue overwrote a failed return-address read with a bad-return status; corrected in V2. The first pipeline adapter consumed RTS where its service caller expected a body ending at RTS; the corrected adapter retains that boundary. A V2 metadata wrapper also assumed successful source_bindings on rejection; V3 handles both statuses. These are not model failures.\n\nDesktop launcher option 10 repeats the bounded local source-output test. Its revised V2 prompt includes operand/stack/branch guidance and uses corrected glue; that revised prompt has not yet received a new inference run. Option 7 shows exact saved prompts/responses. Native LM Studio Chat display remains unverified.\n\nSource: '+str(source)+'\nExact local transcript: '+str(run/'prompts-and-responses.txt')+'\nIntegration proof: '+pipeline['integration_proof']+'\n\nFull game source, native reconstruction, GPU/DSP/service recovery, broader timing/hardware checks, reliable Advertising workflows and latest migration/future-hardware acceptance remain incomplete.\n')
 summary['report']=str(report);save(out/'review.json',summary);save(V/'Deck-coordinate-recovery-current.json',summary)
 # Add scoped evidence to both reference corpora, rebuild each entire game
 # index atomically, and verify retrieval through the actual configured MCP.
 evidence={k:summary[k]for k in ['status','recorded_at','original_interval','original_bytes','authorship','component_cases','boundary_witnesses','connected_source_calls','paired_checkpoints','GPU_commands_in_connected_test','actual_local_predictions','raw_local_source_accepted','local_repair_executable_code_unchanged','native_disc_changed','native_code_bytes_still','natural_unpatched_gameplay_verified','experimental_selector_count13_overlay_retained','whole_game_complete','limits']}
 evidence['subject']='BIWN Deck C-Space coordinate readable source recovery 11D1A';evidence['report']=str(report)
 for root in [ROOT,RT]:
  target=root/'corpus/game/project-evidence/biwn-deck-coordinate-readable.json';save(target,evidence)
  index=root/'indexes/game.sqlite'
  if index.exists():
   with sqlite3.connect(index)as before,sqlite3.connect(out/('game-index-'+('workspace'if root==ROOT else'runtime')+'-before.sqlite'))as backup:before.backup(backup)
  command=[str(root/'.venv/bin/python3.12'),'-c',"import lab;lab.ingest('game',lab.ROOT/'corpus/game')"]
  p=subprocess.run(command,cwd=root,capture_output=True,text=True);(out/('index-'+('workspace'if root==ROOT else'runtime')+'.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 with ReferenceBridge()as bridge:
  result=bridge.call('search_references',dict(domain='game',query='biwn deck coordinate readable 11D1A',max_chunks=4));save(out/'actual-MCP-search.json',result);assert any(Path(x['source']).name=='biwn-deck-coordinate-readable.json'for x in result['evidence']);save(out/'actual-MCP-connection.json',bridge.metadata)
 # A reversible new menu version; earlier launcher targets remain present.
 menu=ROOT/'Open Local AI Lab v4.command';desktop=Path.home()/'Desktop/Local AI Lab Launcher.command';previous=os.readlink(desktop);assert previous==str(ROOT/'Open Local AI Lab v3.command')
 subprocess.run(['zsh','-n',str(menu),str(ROOT/'Try Local Deck Coordinate.command')],check=True)
 p=subprocess.run(['zsh',str(menu)],input='0\n',capture_output=True,text=True);assert p.returncode==0 and '10 Local Deck/C-Space'in p.stdout
 save(out/'menu-check.json',dict(exit_code=p.returncode,output=p.stdout,previous_target=previous,new_target=str(menu)))
 desktop.unlink();desktop.symlink_to(menu)
 summary.update(desktop_launcher=str(desktop),desktop_menu=str(menu),menu_option=10,actual_MCP_reference_retrieved=True,saved_prompt_or_transcript_records=read(V/'current-model-work-index-v4-current.json')['saved_prompt_or_transcript_records'])
 goal=read(V/'goal-continuation-current.json');save(out/'previous-goal-state.json',goal)
 goal.update(status='active_readable_Deck_coordinate_caller_recovered_local_output_trial_rejected',recorded_at=summary['recorded_at'],directory=str(out),publication=str(out),previous_observation_turn_classification='no progress:read-only overall-status answer; revalidated current evidence and advanced source recovery this turn.',current_turn_classification='progress:complete330byte/87instruction caller recovered as structured coordinatorC;576fullCPU+128boundary+87hosterrorchecks,4source mutations,17connectedsource calls/31checkpoints. Actual localAuthor/repair both fail; no newweights/nativeCDI. Corrected coordinatorglue/RTSboundary independently.',full_objective_complete=False,blocked=False,ongoing_finite_workers=[],new_training=False,training_scope_this_turn='Two actual base27B predictions;zero optimizerupdates. Bothrawoutputs rejected;accepted source is coordinatorauthored.',current_turn_predictions=2,desktop_launcher_target=str(menu),saved_prompt_or_transcript_records=summary['saved_prompt_or_transcript_records'],Deck_coordinate_recovery=summary)
 goal['remaining_requirements']['game']='Full readable game/callgraph/same-console rebuild remain incomplete. New readable11D1A caller is hostedsource,not in34784byte nativeimage. Sevenofeight nativeGPUCPUroots live; E26Cstillcomponent-only in ordinary native route. Newsourcepipeline17calls retain experimentalassetpatch/suppliedentry/ring/providers. OriginalotherCPU/GPU/DSP/services remain.'
 goal['next_actions'][0]='Use recoveredDeckcoordinate caller to replace additional instruction-generatedDeck/scene functions;resolve original mode3asset/schema path before claiming naturalunpatchedE26Ccoverage.'
 goal['next_actions'][1]='Run the prepared revised localDeck prompt as a newinformed outputtrial;do not claim the original comment-onlyrepair succeeded or that coordinatorC is local-authored.'
 goal['limits']='Fullfourpartgoalactive. Newhostedreadablecaller verified in boundedcomponent/experimentalpipelinechecks;nativeCDI34784unchanged. RawlocalAuthor/repairrejected. NaturalunpatchedE26C/nativeChat/Advertisingreliability/latestmigration/futurehardware unfinished.'
 save(V/'goal-continuation-current.json',goal);save(out/'review.json',summary);save(V/'Deck-coordinate-recovery-current.json',summary)
 # Final immutable publication hashes include copies, reports and connection.
 integrity={str(p.relative_to(out)):sha(p)for p in out.rglob('*')if p.is_file()and p.name!='integrity.json'};save(out/'integrity.json',integrity)
 print(summary['status'],len(integrity),'publication files; native disc unchanged',flush=True)
if __name__=='__main__':main()
