"""Show the source-checked current build without starting a model or game."""
import argparse,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from native_deck_source_context_v13 import snapshot
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--brief',action='store_true');args=ap.parse_args();f=snapshot();n=f['native_experimental_disc']
    print('CURRENT BIWN BUILD\nSix recovered Deck callers are native in the fresh-reviewed experimental disc and installed checkpoint GUI.\n'
          f"Fresh candidate/control: {n['frames']:,} frames each; control restores only the outer task. Forty video frames differ; final video matches.\n"
          'Desktop: BIWN Test Preview.app, then P. Run input: C+Up or Shift+Up. LM Studio is not required for the game window.\n'
          'The whole game cannot yet be rebuilt from recovered source. Deck appearance, timing/audio/physical fidelity and broad training quality remain open.\n',flush=True)
    plane=f.get('plane_layout_recovery')
    if plane and plane.get('new_fresh_gameplay_verified')and 'geometry_faces_recovery'not in f:
        print(f"Latest separate four-helper disc: final-address/nesting checks pass; fresh candidate/control {plane['candidate_frames']:,} frames each, with 18 geometry calls per lane. {plane['differing_video_frames']} video frames differ; final video matches. Timing/gameplay fidelity remains open. Installed preview unchanged.\n",flush=True)
    elif plane and 'geometry_faces_recovery'not in f:
        print('New 110D4 source:1,408CPU/RAM cases pass. Four-helper native prototype passes256geometry,4,992retained and1,280fallback cases. Final/fresh-disc qualification pending.\n',flush=True)
    elif 'native_deeper_helper_candidate'in f:
        c=f['native_deeper_helper_candidate']
        if c.get('fresh_candidate_gameplay_verified'):
            print(f"Separate deeper candidate:3internal compiled helpers;256alias/128connected cases pass. Fresh candidate/control:{c['candidate_frames']:,}/{c['control_frames']:,}frames. {c['differing_video_frames']}video frames differ;final video matches. Preview unchanged.\n",flush=True)
        else:print('Separate three-helper candidate:final component checks pass;nesting/fresh checks pending.\n',flush=True)
    faces=f.get('latest_native_candidate')or f.get('native_alu_optimization')or f.get('geometry_faces_recovery')
    if faces:
        stage=(f"Fresh candidate/control: {faces['candidate_frames']:,}/{faces['control_frames']:,} frames. {faces['differing_video_frames']} video frames differ; final video equal: {faces['final_video_equal']}. Runtime guards pass. Fidelity is unapproved."if faces.get('fresh_route_completed')else'Final-address/startup/heap and 256 alias checks pass; combined integration and fresh gameplay remain pending.'if faces.get('final_address_gates_verified')else'Separate candidate disc built; final-address, nesting and fresh qualification pending.')
        print(f"Geometry source: 640 face-builder host cases and 256 connected cases pass. The five-helper native prototype passes 256 geometry, 4,992 retained-caller and 1,280 fallback cases; peak C stack {faces['maximum_observed_C_stack_bytes']}/176 bytes. {stage} Preview unchanged.\n",flush=True)
    debug=f.get('debug_overlay_recovery')
    if debug:
        print('New 10734 debug caller: 256 full-CPU cases, 172 host-error cases and a separate 256-case real formatter/text/blitter chain pass. All 141 caller instructions covered; four source defects rejected. Target object is compile-only; native integration remains pending.\n',flush=True)
    if f.get('game_geometry_training_review'):
        followup='The separate filename-clarified diagnostic also finished at 0/4 each.'if f['game_geometry_training_review'].get('clarified_diagnostic_complete')else'Filename ambiguity recorded; a separate clarified diagnostic is underway.'
        print('Game-model pilot: 64 updates complete; selected adapter and base each passed 0/4 original code tests. '+followup+' No model promotion. Open Game Model Training Progress.command for current status.\n',flush=True)
    elif plane:print('Game-model pilot:experimental and unpromoted. Open Game Model Training Progress.command on the Desktop for current worker/update/evaluation status.\n',flush=True)
    if not args.brief:print('Disc:',n['disc'],'\nNext:',f['next_source_work'],flush=True)
if __name__=='__main__':main()
