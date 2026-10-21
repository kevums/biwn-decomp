"""Publish exact route diagnosis, local-agent limits and current MCP explanation."""
import hashlib,json,shutil,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from reference_mcp_bridge import ReferenceBridge


def sha(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(path):return json.loads(Path(path).read_text())
def save(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n')


def main():
    now=datetime.now(timezone.utc);out=ROOT/'verification/native-format-exit-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    analysis_path=ROOT/'verification/native-format-exit-analysis-current.json';analysis=read(analysis_path)
    assert analysis['status']=='terminal_original_type5_encounter_explains_long_route_delay_with_limits'
    state_path=ROOT/'verification/current-biwn-status-reader-current.json';state=read(state_path)
    assert state['status']=='terminal_local_current_status_pending_review' and not state['answer_review_flags']
    assert len(state['calls'])==1 and len(state['answer'].split())<150
    with ReferenceBridge()as bridge:
        data=bridge.call('project_evidence',{'topic':'status'});assert data==state['calls'][0]['result'];metadata=bridge.metadata
    diagnosis=data['route_delay_diagnosis'];assert diagnosis['optimized_media_call']['elapsed_frames']==4813
    assert diagnosis['native_sampled_distance_minima']=={'base':269,'optimized':244}
    assert not diagnosis['earlier_approach_divergence_cause_isolated']
    old_status=ROOT/'verification/current-biwn-status-publication-current.json'
    parent_status=read(old_status);old_changes=[]
    for path,digest in parent_status['dependencies_sha256'].items():
        if sha(path)!=digest:old_changes.append(path)
    allowed={str(ROOT/'native_format_evidence.py'),str(Path.home()/'.lmstudio/local-ai-lab/native_format_evidence.py'),str(state_path)}
    assert set(old_changes)==allowed,old_changes
    # Prior workflow snapshots still identify exactly what ran. Its mutable
    # module/current-reader pointers intentionally advance in this revision.
    prior_note=dict(parent=str(old_status),sha256=sha(old_status),intentional_live_pointer_changes=old_changes,
                    reason='Add the bound native encounter diagnosis and record one new current local Reader run. No CPU/game source input changed.',
                    earlier_source_snapshots_preserved=True)
    save(out/'previous-workflow-revision.json',prior_note)
    pair=read(ROOT/'verification/native-format-exit-diagnostic-current.json');route=read(pair['parent']);old=Path(route['directory'])
    rows={lane:read(old/lane/'report.json')['frames']for lane in ['base','optimized']}
    first={}
    for field in ['raw_player_X','raw_player_Z','player_mode_word','floor_word','scene_word','video_sha256']:
        first[field]=next((dict(frame=a['frame'],base=a[field],optimized=b[field])for a,b in zip(rows['base'],rows['optimized'])if a[field]!=b[field]),None)
    for field in ['buttons','heading','desired_heading','heading_error']:
        first['navigation_'+field]=next((dict(frame=a['frame'],base=(a.get('navigation')or{}).get(field),optimized=(b.get('navigation')or{}).get(field))
            for a,b in zip(rows['base'],rows['optimized'])if(a.get('navigation')or{}).get(field)!=(b.get('navigation')or{}).get(field)),None)
    assert first['raw_player_X']['frame']==first['raw_player_Z']['frame']==9920
    assert first['navigation_buttons']['frame']==10051
    save(out/'earliest-recorded-divergences.json',first)
    state.update(coordinator_review_pending=False,coordinator_review='accepted_grounded_explanation_of_bound_native_trace',
                 review_scope='Full raw answer checked against exact MCP result. Grounded development explanation; not successful autonomous instruction analysis, independent review or new weight training.')
    save(Path(state['directory'])/'protocol.json',state);save(state_path,state)
    report=ROOT/'reports/native-format-exit-and-local-agent-review.txt'
    prediction=read(ROOT/'verification/native-format-exit-local-prediction-current.json')
    report.write_text(
        'BIWN EXIT DIAGNOSIS AND LOCAL AGENT OUTPUT TEST\n'+now.isoformat()+'\n\n'
        'VERIFIED RESULT\n'
        'A proximity-triggered original type5 NPC/media interaction accounts for most of the optimized route delay. '
        'The optimized native task reaches squared distance244; the original gate skips only values greater than255. '
        'Base sampled distances stay at269or above in the observed approach. '
        'The optimized actor calls1C9E8withargument10atframe24158 and returns to131C8at28971:4813frames. '
        'The player position is held for4817frames including the short pre-call interval. '
        'The call contains three media-active sequences and additional captured audio. '
        'Base has no corresponding call during this exit. This is different executed game content, so24975versus29791route frames is not a clean execution-speed comparison.\n\n'
        'The read-only observer reruns reproduce every recorded playerX/Z,mode,floor,scene,video hash,cumulative audio-count frame and navigation/button decision. '
        'Original actor/media instruction bytes match captured RAM. No waypoint/tolerance,code,NPCstate,guestRAM or CPU-register change was applied. '
        'Original engine/GPU/DSP/firmware/device providers remain; this is an experimental mixed original/new disc, not a standalone source-built game or physical-console proof.\n\n'
        'NEXT FIDELITY BOUNDARY\n'
        'Position first differs atframe9920, before the adaptive controllers first choose different buttons at10051. '
        'Video first differs at210. Floor and scene words remain equal through the paired duration. '
        'The earlier common-input position/timing divergence is still unisolated. The NPC trace explains the later encounter; it does not prove why the earlier divergence occurred.\n\n'
        'WHO DID WHAT\n'
        'Codex coordinator: derived a read-only observer, ran and compared both fresh routes, checked original control flow/task stack, rejected unsupported model instruction claims, updated installed status retrieval and reviewed the final explanation. '
        'The first analysis assertion incorrectly demanded fullD5zero; rawD5=0x40000,while the originalTST.Wtests only its zero low word. Corrected analysis only; original trace and game unchanged; failure preserved.\n'
        'Local Analyst: one actual dailyQwen3_5 27B6bit generation,22424inputtokens,57.08seconds,without the new diagnostic result. '
        'Broad media/NPC hypothesis supported; exact source analysis rejected for wrong PC roles,missing255gate,incorrect interval arithmetic and non-disconfirming claims. '
        'Initial over-context preparation did not invoke inference; columnar encoding kept all120declared approach rows per lane.\n'
        'Local Reader: same daily weights,one actual configuredMCP status call,'+str(round(state['seconds'],2))+'seconds,'+str(len(state['answer'].split()))+'words. '
        'Uses coordinator-verified bound facts to explain the finding. Raw final answer accepted unchanged for this grounded question. '
        'Reader success does not validate the earlier Analyst output. No independent Reviewer,new training or weight/default promotion.\n\n'
        'RAW LOCAL READER ANSWER\n'+state['answer']+'\n\n'
        'WATCH / RUN\n'
        'Desktop → Local AI Lab → Ask BIWN Candidate Status.command now includes the bound encounter diagnosis. '
        'This launcher uses localSDKinference. In an LM Studio game chat with local-ai-lab enabled, request project_evidence(topic=status). '
        'A fresh native Chat-window response was not verified in this continuation.\n'
        'Analyst exact prompts/response: '+prediction['directory']+'/prompts-and-responses.txt\n'
        'Reader exact prompts/response: '+state['directory']+'/prompts-and-responses.txt\n'
        'Native trace analysis: '+analysis['report']+'\n\n'
        'The full goal remains active: remaining recovery/linking/platform fidelity,physical console/audio validation, reliable game-authoring and advertising research/education training, and future256GBhardware testing.\n')
    head=('CURRENT EXIT / LOCAL INFERENCE FINDING — '+now.isoformat()+'\n\n'
          'The extra route frames include an original type5 NPC/media interaction. Native distance244crosses the255gate; '
          'one call lasts4813frames. The base route avoids that encounter, so route duration is not a clean speed comparison. '
          'Exact-source Analyst output rejected; grounded local Reader explanation accepted in'+str(round(state['seconds'],2))+'seconds. '
          'Ask BIWN Candidate Status.command now retrieves this diagnosis. No new weights/default preview changes or fresh nativeChatgeneration.\n'
          'Report: '+str(report)+'\n\nEARLIER RECORDS\n\n')
    for name in ['CURRENT LOCAL INFERENCE.txt','CURRENT DECOMPILATION.txt']:
        path=ROOT/name;path.write_text(head+path.read_text())
    watch=ROOT/'WATCH LOCAL AGENTS.txt';watch.write_text('LATEST EXIT DIAGNOSIS / OUTPUT TEST\n'+str(report)+'\n'
         'The local Analyst proposed the broad encounter but failed precise instruction analysis. A separate grounded Reader uses the verified native trace via the updated status tool. '
         'Both use the same weights; they are not independent validators. Exact role prompts/responses are linked in the report.\n\n'+watch.read_text())
    dependencies={};snapshots={}
    def bind(path,snapshot=False):
        path=Path(path).resolve();dependencies[str(path)]=sha(path)
        if snapshot:
            target=out/'snapshots'/(hashlib.sha256(str(path).encode()).hexdigest()[:16]+'-'+path.name);target.parent.mkdir(exist_ok=True);shutil.copyfile(path,target);snapshots[str(path)]=str(target)
    for path,digest in analysis['dependencies_sha256'].items():assert sha(path)==digest,path;bind(path)
    old_build=ROOT/'verification/native-optimized-format-publication-current.json'
    for path,digest in read(old_build)['dependencies_sha256'].items():assert sha(path)==digest,path;bind(path)
    bind(old_build,True);bind(analysis_path,True);bind(pair['parent'],True)
    for name in ['scripts/publish_format_exit_diagnosis.py','scripts/analyze_format_exit_local.py','native_format_evidence.py','chat_tools.py',
                 'scripts/ask_biwn_current_status.py','Ask BIWN Candidate Status.command','CURRENT LOCAL INFERENCE.txt','CURRENT DECOMPILATION.txt',
                 'WATCH LOCAL AGENTS.txt','verification/native-format-exit-diagnostic-current.json','verification/native-format-exit-local-prediction-current.json',
                 'verification/current-biwn-status-reader-current.json']:
        bind(ROOT/name,True)
    installed=Path.home()/'.lmstudio/local-ai-lab'
    for name in ['native_format_evidence.py','chat_tools.py']:
        assert sha(ROOT/name)==sha(installed/name);bind(installed/name,True)
    bind(Path.home()/'.lmstudio/mcp.json',True)
    for path in Path(state['directory']).rglob('*'):
        if path.is_file():bind(path,True)
    failed=ROOT/'verification/native-format-exit-analysis/20261018T164839.698026Z'
    for path in failed.iterdir():
        if path.is_file():bind(path,True)
    for name in ['previous-workflow-revision.json','earliest-recorded-divergences.json']:bind(out/name,True)
    bind(report,True)
    proof=dict(status='terminal_native_NPC_delay_diagnosis_and_grounded_local_Reader_published',recorded_at=now.isoformat(),directory=str(out),report=str(report),
               native_trace_analysis=str(analysis_path),fresh_MCP_metadata=metadata,latest_status_contains_exact_diagnosis=True,
               local_Analyst_accepted_as_precise_source_analysis=False,local_Reader_raw_final_accepted_unchanged=True,
               local_LLM_calls=2,context_preparation_failures_before_inference=1,coordinator_analysis_width_assertion_corrected=True,
               Reader_seconds=state['seconds'],Reader_words=len(state['answer'].split()),earliest_recorded_divergences=first,
               earlier_approach_divergence_cause_isolated=False,new_training=False,default_promoted=False,native_Chat_verified=False,
               whole_game_complete=False,goal_complete=False,dependencies_sha256=dependencies,snapshots=snapshots)
    save(out/'report.json',proof);save(ROOT/'verification/native-format-exit-publication-current.json',proof)
    ledger=ROOT/'verification/goal-continuation-current.json';goal=read(ledger);save(out/'goal-before.json',goal)
    goal.update(status='active_native_NPC_encounter_traced_local_reader_verified_full_goal_incomplete',recorded_at=now.isoformat(),
                previous_goal_turn_classification='progress',current_goal_turn_classification='progress',
                current_goal_turn_progress='Fresh read-only trace identifies threshold-triggered original type5 media interaction and exactly repeats prior routes. Local Analyst precise source analysis rejected; configuredMCP/localReader now explain verified diagnosis.',
                current_goal_turn_evidence=str(ROOT/'verification/native-format-exit-publication-current.json'),
                latest_exit_delay_diagnosis=str(analysis_path),latest_local_inference=state['directory'],
                latest_finite_jobs_running=False,latest_finite_job_status='Both fresh diagnostic routes and both local model calls terminal; no restart.',
                new_training=False,native_Chat_this_continuation=False,whole_game_complete=False,goal_complete=False,
                next_actions=['Investigate first same-input position difference atframe9920 before adaptive button divergence10051; original media encounter already traced.',
                              'Improve native source/runtime recovery and efficient compilation while preserving scoped CPU/RAM/access contracts.',
                              'Use the Analyst instruction-role failures as development feedback, with separate held-out validation before training promotion.',
                              'Continue advertising research/education reliability and training; future256GBhardware and physical console/audio remain unverified.'])
    save(ledger,goal)
    with(ROOT/'runs/agent-work-audit.jsonl').open('a')as stream:
        stream.write(json.dumps(dict(time=now.isoformat(),action='native_exit_diagnosis_and_local_agent_review',
             coordinator='readonly native trace and source/ABI review, installed status update, local-output review',
             local_roles=['Analyst','Reader'],local_LLM_calls=2,Analyst_precise_analysis_accepted=False,Reader_grounded_explanation_accepted=True,
             same_daily_weights=True,independent_review=False,training_updates=0,native_Chat_verified=False,
             proof=str(ROOT/'verification/native-format-exit-publication-current.json')))+'\n')
    print(json.dumps({k:proof[k]for k in ['status','report','local_LLM_calls','Reader_seconds','Reader_words','goal_complete']}))


if __name__=='__main__':main()
