"""Current six-caller evidence for the local Chat team; no execution in lookup."""
from pathlib import Path
from native_deck_source_context_v9 import matches,read,sha
from native_deck_status_evidence_v1 import load
ROOT=Path(__file__).resolve().parent

def snapshot():
    p=load(ROOT)
    assert p['preview_native_Deck_callers']==6 and len(p['installed_recovered_Deck_entries'])==6
    gui=read(p['GUI_review']);g=p['gameplay_comparison'];b=p['experimental_build']
    return dict(project=p['project'],topic='deck_readable_source',authorship=p['local_C_authorship'],
        native_experimental_disc=dict(variant='native Deck six v1',disc=b['derived_disc'],disc_sha256=b['derived_disc_sha256'],
            installed_recovered_Deck_entries=p['installed_recovered_Deck_entries'],hosted_only_recovered_Deck_entries=[],
            native_code_bytes=b['resident_bytes'],total_reservation_bytes=b['reserved_bytes'],initial_heap_bytes=b['initial_heap_bytes'],
            frames=g['candidate_frames'],native_returns=g['ordinary_native_returns'],control_returns=g['same_layout_control_returns'],
            control_original_outer_returns=g['same_layout_control_original_outer_returns'],control_restores_only_outer=True,
            differing_video_frames=g['differing_video_frames'],final_video_equal=g['final_video_equal'],cycle_identity_verified=False,
            fresh_reviewed=True,default_preview_promoted=True,review=p['report']),
        fresh_outer_trial=dict(outer_native_returns=1,outer_original_control_returns=1,inner_five_native_in_both=True,
            geometry_returns_each_lane=18,five_original_geometry_helpers_each_return=18,other_four_returns_each_lane=19,
            observed_wait_slices=55,protected_frame_checks=222,observed_stack_margin_bytes=60,
            minimum_sampled_free_heap_while_outer_active=17968,global_heap_minimum_measured=False,
            arbitrary_suspension_reentry_IRQ_verified=False),
        separate_test_preview=dict(app=gui['app'],runtime=gui['runtime'],native_Deck_callers=6,checkpoint_restored=True,fresh_boot=False,
            actual_GUI_observed=True,live_GUI_frames=gui['frames'],live_native_returns=gui['native_returns'],
            Shift_Up_sends_C_Up_verified=True,run_speed_ratio_measured=False,Deck_expected_visual_transition_verified=False,
            audible_game_audio_verified=False,headless_nonintrusion_frames=2400,
            direct_python_command=str(Path.home()/'.lmstudio/local-ai-lab/.venv/bin/python3.12')+' '+str(Path(gui['runtime'])/'scripts/run_biwn_native_keyboard_v4.py')+' --play-audio',
            launch_and_controls=dict(launch='Double-click BIWN Test Preview.app on the Desktop; click the window and press P.',
                arrows='move/turn',run='Hold C+Up or Shift+Up. Shift alias verified to send ordinary C+Up; speed ratio not measured.',
                Z='attack/read',one_then_D='Hold1 about one second, release, then holdD. Sends ordinary selection and B+C; native calls observed but expected Deck appearance unverified.',
                zero='hold0 to exit Deck',P='start/pause',Esc='close',LM_Studio_required_for_game_window=False)),
        next_source_work='Recover deeper original helper implementations and resolve the active-route timing/video differences while preserving all six native callers. Full-game source rebuilding, arbitrary suspension/reentry/IRQ and fidelity remain incomplete.',
        restoration=dict(frames_per_group=13,original_frames_per_group=16,changes_original_behavior=True),
        whole_game_complete=False,same_console_whole_game_source_rebuild_verified=False,new_training=False,
        source_publication_sha256=p['proof_sha256'],
        scope='Six recovered callers form one Deck subsystem. Fresh/control trials and checkpoint GUI have separate input and frame scopes. Retained emulator/HLE/original-helper dependencies remain. Broad Advertising/game training quality and portable migration remain open.')

def compact_snapshot():return snapshot()
