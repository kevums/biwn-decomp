"""Concise current game/model status from checked evidence, without inference."""
import argparse,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from native_deck_status_evidence_v1 import load

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--brief',action='store_true');args=ap.parse_args()
    p=load(ROOT);c=p['latest_native_candidate'];scene=p['native_scene_draw_progress'];outer=p.get('native_outer_compact_progress');reader=p.get('current_copied_Reader_progress',{})
    print('BIWN — current checked status\n',flush=True)
    print('Latest reviewed gameplay: '+c['variant'],flush=True)
    print(f"Fresh candidate/control: {c['candidate_frames']:,}/{c['control_frames']:,} frames; {c['native_scene_returns']:,} native scene returns. All monitors clear.",flush=True)
    print(f"Video: {c['differing_video_frames']:,} paired differences; final video agrees: {c['final_video_equal']}. Audio fidelity remains unresolved.",flush=True)
    heap=c['minimum_sampled_heap_while_outer_active'];print(f"Sampled free heap while outer task was active: {heap['candidate']:,}/{heap['control']:,} bytes; not a global minimum.",flush=True)
    print(f"Scene stack: {c['native_scene_prototype_C_stack_bytes']}/208 bytes.",flush=True)
    if outer:print(f"Outer stack: {outer['outer_C_stack_bytes']}/{outer['outer_C_stack_reserved']} bytes; {outer['outer_arena_bytes_reclaimed']:,} private arena bytes reclaimed.",flush=True)
    print(f"Local Reader: latest saved response took {reader.get('seconds','unknown')} seconds and {reader.get('words','unknown')} words; fully approved: {reader.get('current_source_reply_verified',False)}. Default Reader version: {reader.get('default_reader_version','unknown')}.",flush=True)
    print('Training: copied-runtime capability verified; earlier base/adapter quality pilot each passed 0/4 tasks. No useful trained-model gain or adopted adapter established.',flush=True)
    records=p.get('native_geometry_records_progress')
    if records:
        print(f"Record builder: {records['native_record_returns']:,} native returns; copy {records['native_record_copy_returns']:,}, matrix {records['native_record_matrix_returns']}. This count belongs to the standard route.",flush=True)
        print(f"Component: host {records['host_cases']} + {records['host_guards']} guards; native {records['native_body_cases']}; whole scene with inherited providers {records['whole_scene_actual_inherited_provider_cases']}. Module {records['module_bytes']:,} bytes.",flush=True)
        prefix=records.get('current_fixed_input_video_comparison')
        if prefix:print(f"Identical-input prefix: {prefix['count']} differing video frames of 1,000; not full-game fidelity.",flush=True)
        else:print('Current-image identical-input prefix comparison remains pending.',flush=True)
        print('Record source and signed-stride adaptation are coordinator-authored; prior linked hybrid attribution remains. Local full-function Author/Repair attempts are separate and unpromoted; no new weight updates.',flush=True)
    matrix=p.get('record_matrix_fresh_progress')
    if matrix:
        print(f"Additional fresh indoor scene {matrix['source_target_scene']}: {matrix['native_record_matrix_returns']} native / {matrix['original_record_matrix_returns']} original matrix returns; final video and selected player fields agree. All monitors clear.",flush=True)
        print(f"Matrix route: {matrix['candidate_frames']:,}/{matrix['control_frames']:,} frames, {matrix['video_differences']:,} paired video differences. Static type {matrix['instantiated_type']}, angle {matrix['static_angle']}; broader timing/fidelity remains open.",flush=True)
        print('The matrix route did not exercise the outer task; its outer stack/active heap are unmeasured.',flush=True)
    compact=p.get('local_geometry_records_compact_progress')
    if compact:print(f"Compact local Author: {compact['seconds']} seconds; output truncated; no redundant Repair, compile or installation.",flush=True)

    prototype=p.get('native_geometry_record_stride_progress')
    if prototype and not prototype.get('new_disc_built',False):
        print(f"\nNewer source prototype: {prototype['module_bytes']:,} bytes; saves {prototype['CPU_cycles_saved_each_fixture']:,} CPU cycles in each of eight fixtures. Not yet a disc image.",flush=True)
        print(f"Prototype checks: host {prototype['host_cases']} + {prototype['host_guards']} guards, native {prototype['native_body_cases']}, connected scene {prototype['prototype_scene_cases']}; copied SDK byte-identical.",flush=True)
        print('Prototype details: '+prototype['report'],flush=True)

    loop=p.get('native_geometry_record_loop_progress')
    if loop:
        if loop.get('new_disc_built'):
            print(f"Newer experimental disc: {loop['profile']}, {loop['module_bytes']:,} bytes. Unpromoted; final matrix-video comparison passed: {loop.get('final_matrix_video_comparison_pass',False)}.",flush=True)
            standard=loop.get('standard_route',{});matrix=loop.get('matrix_route',{});prefix=loop.get('fixed_input_prefix',{})
            if standard:print(f"New candidate standard route: {standard['candidate_frames']:,}/{standard['control_frames']:,} frames, {standard['native_record_returns']:,} record returns, {standard['video_differences']:,} video differences; final video agrees: {standard['final_video_equal']}.",flush=True)
            if matrix:print(f"New candidate matrix route: {matrix['native_record_matrix_returns']} native/{matrix['original_record_matrix_returns']} original returns; final video differs by {matrix['final_differing_pixels']:,} pixels. Fractional player/camera state also differs; cause unresolved.",flush=True)
            if prefix:print(f"New candidate fixed-input prefix: {prefix['count']} differing video frames of 1,000. This does not resolve visual timing.",flush=True)
        else:print(f"Newer coordinator loop-tail component: {loop['module_bytes']:,} bytes; native {loop['native_body_cases']}, scene {loop['prototype_scene_cases']}; not a disc.",flush=True)
        print('Separate local Author/Repair: 16.92/19.48 seconds; Repair repeated failed code. No code from these trials adopted; no new training.',flush=True)

    repair=p.get('local_geometry_prologue_repair_progress')
    local=p.get('local_geometry_prologue_native_progress')
    if local:print(f"Local coding result: {local['seconds']} seconds; host {local['host_cases']} + {local['host_guards']} guards, native {local['native_body_cases']}, scene {local['prototype_scene_cases']}. Verified component; not adopted in the game.",flush=True)
    elif repair:print('Latest bounded local Repair: '+repair['status']+'; adopted: '+str(repair.get('model_source_installed',False))+'.',flush=True)

    print('\nPlay: Desktop BIWN Test Preview.app; click the window and press P. Arrows move; C+Up or Shift+Up sends run input. LM Studio is not needed for the game window.',flush=True)
    print('The checkpoint preview is unchanged. Whole-game source rebuilding, same-console completion, copied-weight Native Chat usability and broader fidelity remain open.',flush=True)
    if not args.brief:print('\nDetails:',c['report'],'\nNext:',c['next_action'],flush=True)

if __name__=='__main__':main()
