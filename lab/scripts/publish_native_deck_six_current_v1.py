"""Bind the fresh six-caller review and actual keyboard sessions to current UI evidence."""
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; V=ROOT/'verification'
RT=Path.home()/'.lmstudio/local-ai-lab/native-preview-v4'
def read(p):return json.loads(Path(p).read_text())
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')

def main():
    out=V/'native-Deck-six-current-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    reviewed=V/'native-Deck-six-reviewed-v1-current.json';r=read(reviewed)
    assert r['status']=='terminal_fresh_six_native_Deck_callers_observed_reviewed'
    for p,h in r['source_sha256'].items():assert sha(p)==h,p
    bp=Path(r['build']);b=read(bp);assert sha(bp)==r['build_sha256']and sha(r['disc'])==r['disc_sha256']
    replay=V/'preview-v4-nonintrusion-current.json';n=read(replay)
    assert n['status']=='terminal_six_caller_preview_2400frame_observer_nonintrusion_match'
    for p,h in n['source_sha256'].items():assert sha(p)==h,p
    # The first session verifies the modifier fix. The second holds game digit1
    # long enough to be sampled, reaches all six native callers, then exits Deck.
    sessions=[]
    for tag,stamp in [('run_alias','20261020T152215.574884Z'),('Deck_calls','20261020T152250.497735Z')]:
        folder=RT/'runs'/('native-keyboard-v4-'+stamp);p=folder/'protocol.json';s=read(p)
        assert s['status']=='terminal_native_keyboard_frontend_stopped_pending_review'and not s['headless']
        assert s['all_GPU_Deck_guards_pass']and s['immutable_native_code_unchanged']and s['invalid_task_identities']==0
        assert s['native_entries']==s['native_returns']and not any(s['original_Deck_body_steps'].values())
        for path,h in s['source_sha256'].items():assert sha(path)==h,path
        rows=read(folder/'frames.json');chord=sum(x['pressed_buttons']==[1,4]for x in rows)
        assert chord>0 and any(x['kind']=='down'and x['key']=='up'and x['shift']and x['pad']==[1,4]for x in s['frontend_key_events'])
        if tag=='Deck_calls':assert all(x>0 for x in s['native_returns'].values())
        shutil.copyfile(p,out/(tag+'-protocol.json'))
        sessions.append(dict(role=tag,protocol=str(p),protocol_sha256=sha(p),frames=s['frames'],keyboard_events=s['keyboard_events'],
                             native_returns=s['native_returns'],run_chord_frames=chord,all_guards_pass=True))
    gui=dict(status='terminal_six_caller_GUI_and_Shift_run_mapping_reviewed',app=str(Path.home()/'Applications/BIWN Test Preview.app'),runtime=str(RT),
             actual_GUI_observed=True,frames=sessions[1]['frames'],keyboard_events=sessions[1]['keyboard_events'],native_returns=sessions[1]['native_returns'],
             sessions=sessions,launch_movement_pause_close_verified=True,Shift_Up_sends_C_Up_verified=True,run_speed_ratio_measured=False,
             Deck_expected_visual_transition_verified=False,revision23_visual_fidelity_verified=False,audible_game_audio_verified=False,
             headless_nonintrusion_frames=2400,whole_game_complete=False,new_training=False,
             scope='Actual CUA launch, input, pause, screenshots and close. Shift modifier mapping recorded ordinary C+Up. All six callers returned in the held-digit session; street view remained visible, so expected Deck appearance is unverified. No speed benchmark, audio or physical-console fidelity claim.',
             source_sha256={str(p):sha(p)for p in [Path(__file__),replay,RT/'scripts/run_biwn_native_keyboard_v4.py',*[Path(x['protocol'])for x in sessions]]})
    save(out/'GUI-review.json',gui);save(V/'native-keyboard-live-v4-reviewed-current.json',gui)
    old_install=V/'native-preview-v4-install-current.json';shutil.copyfile(old_install,out/'previous-install-receipt.json');install=read(old_install)
    assert sha(Path(install['app'])/'Contents/MacOS/BIWNTestPreview')==install['launcher_sha256']
    inventory={str(p.relative_to(RT)):sha(p)for p in RT.rglob('*')if p.is_file()and not {'runs','__pycache__'}&set(p.relative_to(RT).parts)and p.name not in ['manifest.json','native-keyboard-v4-current.json']}
    save(out/'runtime-files.json',inventory)
    install.update(status='terminal_six_caller_Test_Preview_installed_GUI_and_run_mapping_reviewed',directory=str(out),proof=str(replay),proof_sha256=sha(replay),
                   runtime_inventory=str(out/'runtime-files.json'),runtime_inventory_sha256=sha(out/'runtime-files.json'),actual_GUI_observed=True,
                   GUI_review=str(out/'GUI-review.json'),GUI_review_sha256=sha(out/'GUI-review.json'))
    save(out/'install-receipt.json',install);save(old_install,install)
    counts=dict(r['native_five_returns']['candidate'],outer=r['outer_observations']['candidate']['native_returns'])
    control=dict(r['native_five_returns']['control'],outer=0)
    text=('Six recovered Deck callers now execute natively in the reviewed experimental disc and installed Python preview. '
          'Fresh candidate and same-layout original-outer control each ran 25,007 frames. The inner five stay native in both; '
          'the candidate outer returned once versus one original-outer control return. Forty video frames differ despite equal final video; '
          'cycle identity is unverified. The checkpoint GUI passed movement, pause, close and Shift+Up to C+Up mapping; all six callers returned in its 415-frame held-digit session. '
          'Expected Deck appearance remains unverified. The six callers are one subsystem; full-game source rebuilding, arbitrary suspension/reentry/IRQ, timing, visual, audio and physical fidelity remain incomplete. '
          'The retained 13-frame restoration changes original 16-frame behavior. Outer integration is coordinator work; no new model-authored algorithm or training update.')
    report=ROOT/'reports/Six Native Deck Callers and Preview Review.txt'
    report.write_text('BIWN — SIX NATIVE DECK CALLERS AND PYTHON PREVIEW\n\n'+text+'\n\n'
        'Native fresh returns: '+json.dumps(counts)+'. Geometry calls five original helpers 18 times each in both lanes. '
        'The native outer makes 19 iteration boundaries,55 wait slices and222 protected-frame checks. Its lowest observed C-stack offset is204 against lower bound144:60 bytes observed margin. '
        'Scheduler boundary visits do not establish arbitrary interrupt or reentry safety. Minimum sampled free heap while outer active is17,968 bytes, not a global route minimum.\n\n'
        'Native code72,204 bytes; total reservation260,160; initial heap137,728. All three arena fences and immutable code pass. '
        'The separate2,400-frame observed/unobserved replay matches full CPU,RAM,video,GPU,DSP and final serialized state in its finite scope.\n\n'
        'GUI run-alias session:367 frames,77 C+Up frames. Held-digit Deck session:415 frames,58 C+Up frames; all six native callers return. '
        'A short digit press selected nothing; hold1 about one second, release, then holdD. Native execution is observed but the expected Deck visual transition is not confirmed.\n\n'
        'Fresh source review: '+str(reviewed)+'\nGUI review: '+str(out/'GUI-review.json')+'\nDisc: '+r['disc']+'\nSHA-256: '+r['disc_sha256']+'\n')
    build=dict(derived_disc=r['disc'],derived_disc_sha256=r['disc_sha256'],resident_bytes=r['native_code_bytes'],reserved_bytes=r['total_reservation_bytes'],
               initial_heap_bytes=r['initial_heap_bytes'],authorship='Coordinator outer native wrapper/capture/layout, recovered algorithm unchanged. Retained five caller bodies preserve their earlier local/coordinator provenance.')
    packet=dict(project='Black Ice/White Noise revision23',schema_version=3,status='terminal_native_six_Deck_status_published',milestone='six native Deck callers reviewed',
        checked_current_summary=text,checked_answer=text,report=str(report),experimental_build=build,facts=dict(experimental_build=build),
        installed_recovered_Deck_entries=r['installed_recovered_Deck_entries'],remaining_hosted_only_Deck_entries=[],
        gameplay_comparison=dict(candidate_frames=r['candidate_frames'],control_frames=r['control_frames'],ordinary_native_returns=counts,same_layout_control_returns=control,
            same_layout_control_original_outer_returns=r['outer_observations']['control']['original_returns'],control_restores_only_outer=True,control_declared_redirect_bytes=12,
            outer_observations=r['outer_observations'],geometry_observations=r['geometry_observations'],differing_video_frames=r['differing_video_frames'],final_video_equal=r['final_video_equal'],timing_cycle_identity_verified=False),
        current_processors='Retained reference emulator CPU/GPU/DSP/HLE executing mixed original and compiled game code.',processor_tests=[],older_source_CPU_GPU_DSP_tests_apply_to_this_disc=False,
        local_C_authorship=build['authorship'],preview_native_Deck_callers=6,latest_image_GUI_verified=True,restoration_changes_original_behavior=True,original_frames_per_group=16,restored_frames_per_group=13,
        whole_game_complete=False,physical_console_verified=False,standalone_runtime_verified=False,new_training=False,default_promoted=True,native_Chat_verified=False,goal_complete=False,
        this_lookup_executes_game_tests=False,this_lookup_invokes_model_or_training=False,GUI_review=str(out/'GUI-review.json'),GUI_checkpoint_restored=True,GUI_fresh_boot=False,
        GUI_frames=gui['frames'],GUI_native_returns=gui['native_returns'],GUI_Deck_expected_visual_transition_verified=False,GUI_audio_verified=False,GUI_Shift_Up_sends_C_Up_verified=True,
        headless_observer_nonintrusion_frames=2400,remaining=['Full readable game source build','Arbitrary suspension/reentry/IRQ','Timing, visual, audio and physical-console fidelity','Broad accepted game and Advertising training','Expected Deck appearance and run-speed benchmark'])
    save(out/'current-status.json',packet);shutil.copyfile(reviewed,out/'fresh-review.json');shutil.copyfile(bp,out/'build.json');shutil.copyfile(replay,out/'replay.json')
    pointer=V/'native-Deck-current-status-v1-current.json';shutil.copyfile(pointer,out/'previous-status-publication.json')
    state=dict(status='terminal_reviewed_six_caller_status_published',directory=str(out),packet=str(out/'current-status.json'),report=str(report),source_review=str(out/'fresh-review.json'),
               dependencies_sha256={str(p):sha(p)for p in [out/'current-status.json',out/'GUI-review.json',out/'fresh-review.json',out/'build.json',out/'replay.json',out/'runtime-files.json',report,Path(r['disc'])]},new_game_execution=False,new_prediction=False,new_training=False,whole_goal_complete=False)
    save(out/'publication.json',state);save(pointer,state)
    guide=ROOT/'BIWN Test Preview - Start Here.txt';shutil.copyfile(guide,out/'previous-Start-Here.txt')
    command=str(Path.home()/'.lmstudio/local-ai-lab/.venv/bin/python3.12')+' '+str(RT/'scripts/run_biwn_native_keyboard_v4.py')+' --play-audio'
    guide.write_text('BIWN TEST PREVIEW — START HERE\n\nDouble-click BIWN Test Preview.app on the Desktop, click inside the window and press P. LM Studio is not required.\n\n'
        'Arrows: move/turn. Hold C+Up or Shift+Up: run input. Z: attack/read. P: pause/resume. Esc: close.\n'
        'Hold1 about one second, release, then holdD: select/activate Deck. D sends B+C. Hold0: Deck exit. Some short key taps can be missed at low emulation speed.\n\n'
        +text+'\n\nDirect Python:\n'+command+'\n\nReview: '+str(report)+'\n')
    for name in ['BIWN Latest Work.txt','BIWN Latest Result.txt']:
        p=ROOT/name
        if p.exists():shutil.copyfile(p,out/('previous-'+name))
        p.write_text(text+'\n\nReview: '+str(report)+'\n')
    goal_path=V/'goal-continuation-current.json';shutil.copyfile(goal_path,out/'previous-goal.json');g=read(goal_path)
    g.update(status='active_six_caller_fresh_and_GUI_reviewed_full_game_incomplete',recorded_at=datetime.now(timezone.utc).isoformat(),
             previous_goal_turn_classification='Progress: fresh six-caller pair reviewed; staged preview and diagnosed Shift modifier event handling. Last user-answer turn verified launch paths without changing game state.',
             current_turn_classification='Progress: recovered terminal2400frame comparison; actual367/415frame GUI sessions verify run mapping and six native returns; published current six-caller evidence and launch guide.',
             publication=str(pointer),review=str(report),current_GUI_native_callers=6,current_disc_native_Deck_callers=6,latest_fresh_reviewed_disc_native_Deck_callers=6,
             current_native_Deck_installed=r['installed_recovered_Deck_entries'],current_Deck_hosted_only=[],candidate_fresh_gameplay_verified=True,
             current_turn_actual_local_predictions=0,current_turn_optimizer_updates=0,current_turn_predictions=0,ongoing_finite_workers=[],full_objective_complete=False,blocked=False)
    g['remaining_requirements']['game']='Six-caller subsystem fresh/control and checkpoint GUI reviewed; deeper original helpers, full-game source rebuilding, arbitrary suspension/reentry/IRQ and fidelity remain incomplete.'
    g['remaining_requirements']['local_frontend']='Six-caller GUI, run alias and current source publication reviewed. Expected Deck appearance, run-speed ratio, broad model reliability and audio/visual fidelity remain incomplete.'
    g['next_actions']=['Update and test current local-model Chat and one-click status routes against six-caller evidence.','Recover deeper original helper implementations and resolve active-route timing/video differences; preserve all existing native callers.','Improve Advertising source-faithful research/teaching output and complete portable migration; retain rejectedV12adapter.']
    save(goal_path,g)
    print(json.dumps(dict(directory=str(out),GUI=gui['native_returns'],report=str(report)),indent=2))

if __name__=='__main__':main()
