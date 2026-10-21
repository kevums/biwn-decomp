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
        print(f"Record builder: {records['native_record_returns']:,} native returns; copy {records['native_record_copy_returns']:,}, matrix {records['native_record_matrix_returns']}. Fresh matrix-path coverage remains open.",flush=True)
        print(f"Component: host {records['host_cases']} + {records['host_guards']} guards; native {records['native_body_cases']}; whole scene with inherited providers {records['whole_scene_actual_inherited_provider_cases']}. Module {records['module_bytes']:,} bytes.",flush=True)
        print(f"Identical-input prefix: {records['current_fixed_input_video_comparison']['count']} differing video frames of 1,000. This is a timing measurement, not full-game fidelity.",flush=True)
        print('New record source is coordinator-authored; prior linked hybrid attribution remains. Local full-function Author/Repair attempts are separate and unpromoted; no new weight updates.',flush=True)
    compact=p.get('local_geometry_records_compact_progress')
    if compact:print(f"Compact local Author: {compact['seconds']} seconds; output truncated; no redundant Repair, compile or installation.",flush=True)

    prototype=p.get('native_geometry_record_stride_progress')
    if prototype:
        print(f"\nNewer source prototype: {prototype['module_bytes']:,} bytes; saves {prototype['CPU_cycles_saved_each_fixture']:,} CPU cycles in each of eight fixtures. Not yet a disc image.",flush=True)
        print(f"Prototype checks: host {prototype['host_cases']} + {prototype['host_guards']} guards, native {prototype['native_body_cases']}, connected scene {prototype['prototype_scene_cases']}; copied SDK byte-identical.",flush=True)
        print('Prototype details: '+prototype['report'],flush=True)

    print('\nPlay: Desktop BIWN Test Preview.app; click the window and press P. Arrows move; C+Up or Shift+Up sends run input. LM Studio is not needed for the game window.',flush=True)
    print('The checkpoint preview is unchanged. Whole-game source rebuilding, same-console completion, copied-weight Native Chat usability and broader fidelity remain open.',flush=True)
    if not args.brief:print('\nDetails:',c['report'],'\nNext:',c['next_action'],flush=True)

if __name__=='__main__':main()
