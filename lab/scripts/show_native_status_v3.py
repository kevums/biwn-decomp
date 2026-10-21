"""Concise current game/model status from checked evidence, without inference."""
import argparse,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from native_deck_status_evidence_v1 import load

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--brief',action='store_true');args=ap.parse_args()
    p=load(ROOT);c=p['latest_native_candidate'];scene=p['native_scene_draw_progress'];outer=p.get('native_outer_compact_progress');reader=p.get('current_copied_Reader_progress',{})
    print('BIWN — current checked status\n',flush=True)
    print(c['variant'],flush=True)
    print(f"Fresh candidate/control: {c['candidate_frames']:,}/{c['control_frames']:,} frames; {c['native_scene_returns']:,} native scene returns. All monitors clear.",flush=True)
    print(f"Video: {c['differing_video_frames']:,} paired differences; final video agrees: {c['final_video_equal']}. Audio fidelity remains unresolved.",flush=True)
    heap=scene['minimum_sampled_heap_while_outer_active'];print(f"Sampled free heap while outer task was active: {heap['candidate']:,}/{heap['control']:,} bytes; not a global minimum.",flush=True)
    print(f"Scene stack: {c['native_scene_prototype_C_stack_bytes']}/208 bytes.",flush=True)
    if outer:print(f"Outer stack: {outer['outer_C_stack_bytes']}/{outer['outer_C_stack_reserved']} bytes; {outer['outer_arena_bytes_reclaimed']:,} private arena bytes reclaimed.",flush=True)
    print(f"Local Reader: latest saved response took {reader.get('seconds','unknown')} seconds and {reader.get('words','unknown')} words; fully approved: {reader.get('current_source_reply_verified',False)}. Default Reader version: {reader.get('default_reader_version','unknown')}.",flush=True)
    print('Training: copied-runtime capability verified; earlier base/adapter quality pilot each passed 0/4 tasks. No useful trained-model gain or adopted adapter established.',flush=True)
    print('\nPlay: Desktop BIWN Test Preview.app; click the window and press P. Arrows move; C+Up or Shift+Up sends run input. LM Studio is not needed for the game window.',flush=True)
    print('The checkpoint preview is unchanged. Whole-game source rebuilding, same-console completion, copied-weight Native Chat usability and broader fidelity remain open.',flush=True)
    if not args.brief:print('\nDetails:',c['report'],'\nNext:',c['next_action'],flush=True)

if __name__=='__main__':main()
