"""Audit actual geometry records, failed scope answers, and original GPU probe."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
from record_disc_camera_animation_checkpoint import samples
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(p,value):p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def main():
    now=datetime.now(timezone.utc).isoformat();checkpoint=read(ROOT/'verification/geometry-records-checkpoint.json');linked=read(ROOT/'verification/biwn-disc-world-geometry-records-checks.json');cpu=read(ROOT/'verification/biwn-geometry-records-cpu-checks.json');source=ROOT/'projects/black-ice-white-noise/restoration'
    for proof in [cpu,linked]:
        assert read(Path(proof['directory'])/'status.json')['status']=='terminal_pass'
        for name,expected in proof['source_sha256'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==expected
    mcp=read(ROOT/'verification/geometry-records-MCP-check.json');assert mcp['topics']['movement_matrix']['movement_matrix_scope']['whole_scene_E220_submissions']==3488
    labels=['easy-geometry-records','easy-geometry-records-compact','easy-geometry-records-scoped','easy-geometry-records-linked'];protocols=[];reviewed=[]
    for label in labels:
        path=Path(read(ROOT/'verification'/(label+'-current.json'))['directory'])/'protocol.json';protocol=read(path);assert protocol['status']=='completed_pending_coordinator_review';protocols.append((label,path,protocol));reviewed.append(samples(protocol))
    assert [len(s)for s in reviewed]==[2,2,2,1]
    assert len({s[0]['prompt']for s in reviewed})==1 and len({s[1]['prompt']for s in reviewed[:3]})==1
    reviewed[0][0].update(verdict='bounded_branch_scope_correct_but_two_overlapping_reports_and_slow')
    reviewed[0][1].update(verdict='bounded_rejection_of_fullgame_correct_but_verbose_historical_detail')
    reviewed[1][0].update(verdict='rejected_live_integration_scope_overstatement',reason='Says matrix path is proven only separately and not in the integrated21-context world. World/actor E220/GPU4320 already executes3488times; zero is only nested170A0branch.')
    reviewed[1][1].update(verdict='rejected_global_zero_E220_claim',reason='Explicitly says live21-context scene makes0E220submissions. Measured whole-scene entrycount3488 contradicts it; builder branch alone has0.')
    reviewed[2][0].update(verdict='rejected_linked_versus_exercised_conflation',reason='Correct3488whole-scene/0buildercounts, but describes render-path matrix integration as notyetdone. Actual provider is compiled and linked; fixture does not reach its branch.')
    reviewed[2][1].update(verdict='bounded_same_model_role_scope_correct',reason='Correct3488whole-scene/0nestedbranch and rejection of viewport/fullgame.92words/one evidence call; same-model roles not independent verification.')
    reviewed[3][0].update(verdict='bounded_ordinary_scope_correct_after_explicit_linked_and_exercised_fields',reason='Correct realbuilder1008/copies3024/4records, linkedbutunreachedE220branch0,whole-scene3488world1440actor2048,sevenlower/fivereachedscripts and fullviewport/game limits.132words/twooverlappingtoolcalls; inference ease remains imperfect.')
    gpu=read(ROOT/'verification/biwn-gpu-geometry-original-probes.json');assert gpu['cases']==4 and gpu['observed_instruction_addresses']==434 and not gpu['C_geometry_reconstructed']and read(Path(gpu['directory'])/'status.json')['status']=='terminal_pass'
    models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['status']=='idle'and models[0]['queued']==0
    audit=ROOT/'verification/geometry-records-review'/Path(linked['directory']).name;audit.mkdir(parents=True,exist_ok=True)
    for label,path,_ in protocols:shutil.copy2(path,audit/(label+'.json'))
    shutil.copy2(ROOT/'verification/geometry-records-MCP-check.json',audit/'installed-MCP.json')
    gpu_snapshot=Path(gpu['directory'])/'observer-snapshot';gpu_snapshot.mkdir(exist_ok=True)
    files=[ROOT/'scripts/biwn_geometry_probe_bridge.c',ROOT/'scripts/biwn_movement_device_bridge.c',ROOT/'scripts/biwn_inventory_device_bridge.c',ROOT/'scripts/probe_biwn_gpu_geometry.py',ROOT/'tools/libbiwn-geometry-probe.dylib']
    for p in files:shutil.copy2(p,gpu_snapshot/p.name)
    save(gpu_snapshot/'manifest.json',dict(recorded_at=now,sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in files}))
    save(audit/'original-GPU4D80-probe.json',gpu)
    who=('Codex authored170A0fullCPUrecord builder, nested E220/E098fullCPU interface, tests and live renderer integration. Actual accepted E3E0copy, originalGPU4320 and reconstructedCmatrix execute in standalone tests; independent Unicorn and original nativeCPU validate scoped source effects. Codex also authored a separate originalGPU4D80observer using the pinned core; it is not a C geometry transform. The local27Bbase answered seven SDK samples with same-model Analyst/Reviewer roles where requested. No subagents or local-model-authored source code, new training, prompt/default/weight/model change. General movement_matrix retrieval was reduced to bounded current evidence and explicit branch/global and linked/exercised fields. Native UI observation timed out after120.6seconds; no new native prompt/response/provider adoption or unlock request.')
    corrections=['512standalone cases/all166instructions/19guards,5782copies/2569matrixsubmissions and16livecases passed. First dense Unicorn observer stopped at10000instructionceiling while native/Calready matched; raised only private observer ceiling100000and asserted endpoints. NoCbehaviorrepair.',
                 'Live170A0runs1008times,3024actualcopies/4records each. ItsE220branch is compiled and linked but unreached0times. Entire same scene executes3488E220submissions:1440matchedworld and2048actor by difference. Zero nested branch is not zero whole-scene GPUmath.',
                 'Seven lower render scripts configured/five reached1008each:181F8,E0A6,E19E,E202,185B2. E0F2/E148 unreached. Scene caller/clear/rotation/queue stillactual,6144fullCPUhandoffs/160sprite decodes/32disc payloads/3080416bytes retained. Main-scene sync,15blockedcontexts,fullgeometry/viewport/scanout/audio/boot/fullgame/hardware remain incomplete.',
                 'Original two answers were factually bounded but slow/verbose. Compact evidence trials produced a globalzero/integration error and were rejected. Paired whole-scene/builder counts fixed the role answer, but ordinary reply still confused linkedwithreached; explicit linked/exercised fields fixed the unchanged ordinary question. All failed trials retained, no reliability generalization.',
                 'Movement_matrix tool now carries about23KB instead of41KB in these SDK envelopes. Reported question times and response lengths differ; cache,toolcount/outputlength prevent causal/general speed claims. Finalordinary132words/twocalls31.14s; boundedrole92words/onecall18.09s. No claim of effortless general local inference.',
                 'OriginalGPU4D80only:1360byteoverlay from4D88,434observed code addresses (424direct/10derivedmandatorydelays),fourcapturedscene probes returnF031BE. GPUregisterseeds/mailboxes are supplied, not original dispatcher/asyncCPUexecution. Rawreadtrace values may beplaceholders. C transform/fullviewport not implemented; next code reference is now concrete.',
                 '113selectedcomponents=111CPU+2GPU. Only170A0is new; existingE220/E098/copy not recounted. This is not a completion percentage.']
    review=dict(recorded_at=now,status='geometry_record_CPU_and_live_checks_passed_corrected_bounded_local_scope_game_incomplete',who_did_what=who,samples_by_stage={label:rows for label,rows in zip(labels,reviewed)},corrections=corrections,
                native_new_response_verified=False,native_UI_observation='Sky request timed out after120.6154seconds; current lock state not established by this attempt',native_current_provider_adoption_verified=False,
                original_GPU4D80_probe=gpu,model_idle=True,new_training=False,default_promoted=False,general_retrieval_compaction=True,system_prompt_changed=False,general_model_reliability_proved=False,directory=str(audit))
    save(audit/'review.json',review);save(ROOT/'verification/geometry-records-review.json',review)
    transcript='GEOMETRY RECORDS / LOCAL INFERENCE AUDIT\n\nWHO DID WHAT\n'+who+'\n\nCORRECTIONS / LIMITS\n'+'\n'.join(corrections)
    for label,_,protocol in protocols:transcript+='\n\nEXACT SYSTEM / USER / TOOLS / RESPONSES — '+label+'\n'+json.dumps(protocol,ensure_ascii=False,indent=2)
    transcript+='\n\nCOORDINATOR REVIEW\n'+json.dumps(review,ensure_ascii=False,indent=2)+'\n\nNEXT\n'+checkpoint['next_work']+'\nFullgoalactive andincomplete.\n';(audit/'prompts-and-responses.txt').write_text(transcript)
    checkpoint.pop('live_matrix_submissions',None)
    checkpoint.update(recorded_at=now,status=review['status'],live_geometry_builder_matrix_submissions=0,whole_scene_matrix_submissions=3488,geometry_builder_matrix_provider_linked=True,geometry_builder_matrix_branch_executed=False,
                      model_idle=True,known_compute_jobs='terminal',native_new_response_verified=False,native_UI_observation=review['native_UI_observation'],new_training=False,default_promoted=False,
                      bounded_correct_role_answer_words=92,bounded_correct_ordinary_answer_words=132,ordinary_two_overlapping_tools_remain=True,general_model_reliability_proved=False,review=str(ROOT/'verification/geometry-records-review.json'),transcript=str(audit/'prompts-and-responses.txt'),original_GPU4D80_probe=str(ROOT/'verification/biwn-gpu-geometry-original-probes.json'))
    checkpoint['evidence']+=['verification/geometry-records-MCP-check.json','verification/geometry-records-review.json','verification/biwn-gpu-geometry-original-probes.json',str((audit/'prompts-and-responses.txt').relative_to(ROOT))]
    save(ROOT/'verification/geometry-records-checkpoint.json',checkpoint)
    for name in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']:
        p=ROOT/'verification'/name;v=read(p);v.update(geometry_records_checkpoint=checkpoint,geometry_records_review=review)
        if name=='current-runtime-state.json':v.update(recorded_at=now,models=models,local_inference_jobs='Terminal: seven SDK samples reviewed; three intermediate scope answers rejected, corrected role/ordinary bounded answers retained. Modelidle. NativeUItimeout unresolved.',latest_API_ease_review=str(ROOT/'verification/geometry-records-review.json'))
        save(p,v)
    note='\nGEOMETRY RECORDS / INFERENCE REVIEW — '+now+'\n\n'+who+'\n\n'+'\n'.join(corrections)+'\n\nEXACT PROMPTS / RESPONSES\n'+str(audit/'prompts-and-responses.txt')+'\n\nNEXT\n'+checkpoint['next_work']+'\nFullgoalactive andincomplete.\n'
    for name in ['CURRENT DECOMPILATION.txt','POST REVIEW.txt','projects/black-ice-white-noise/restoration/READ ME.txt']:
        with(ROOT/name).open('a')as f:f.write(note)
    p=ROOT/'START HERE.txt';text=p.read_text();a=text.index('LOCAL INFERENCE RESULT\n');b=text.index('TRY ADVERTISING ASSISTANT\n',a)
    p.write_text(text[:a]+'LOCAL INFERENCE RESULT\nExisting native Game Assistant — Live Queue Checkpoint retains prior image/roles/scene-caller exchanges. Latest native access timedout; new geometry-record questions used localSDK and logs below. Three intermediate replies misread branch/global or linked/reached scope and were rejected. Final132word ordinary reply and92word same-model role reply are boundedcorrect, around31s/18s. Ordinary answer stillfetches twooverlapping reports; general reliability/ease not proved. Everydaybaseidle; no newtraining/prompt/default/weights.\n\nTry: Does the renderer build real records, and does its matrix branch actually run?\n\nExact exchanges and review:\n'+str(audit/'prompts-and-responses.txt')+'\n\n'+text[b:])
    print(json.dumps(dict(status=review['status'],components=113,live_record_builder_calls=1008,whole_scene_matrix_calls=3488,nested_builder_matrix_calls=0,original_GPU4D80_probes=4,model_idle=True,audit=str(audit))))
if __name__=='__main__':main()
