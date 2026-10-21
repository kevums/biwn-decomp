"""Additional checks from recorded native game runs; no execution replay."""
import json,hashlib,shutil
from pathlib import Path
from check_biwn_native_button_digit import ROOT,save,sha
pfile=ROOT/'verification/native-button-game-current.json';p=json.loads(pfile.read_text());out=Path(p['directory']);assert p['status']=='terminal_native_component_game_experiment'
r=json.loads((out/'reference/report.json').read_text());c=json.loads((out/'candidate/report.json').read_text());assert len(r['frames'])==len(c['frames'])==1500
video=all(a['video']==b['video']for a,b in zip(r['frames'],c['frames']));assert video
frame_cpu=sum(a['CPU']==b['CPU']for a,b in zip(r['frames'],c['frames']))
a=(out/'reference/final-RAM.bin').read_bytes();b=(out/'candidate/final-RAM.bin').read_bytes();diff=[i for i,(x,y)in enumerate(zip(a,b))if x!=y];assert len(diff)==17 and all(0x1b718<=i<0x1b72a for i in diff)
base=ROOT/'runs/natural-coordinate-confirm-20261017T142910.851410Z/reference';base_equal={name:sha(out/'candidate'/name)==sha(base/name)for name in ['final-video.bin','frontend-PCM.s16le']};assert all(base_equal.values())
boundaries=json.loads((out/'call-boundaries.json').read_text());return_PCs=sorted({row['return_PC']for row in boundaries})
assert len(return_PCs)==2
p.update(actual_distinct_caller_sites=len(return_PCs),caller_return_PCs=[hex(x)for x in return_PCs],all_frame_video_hashes_match=True,matched_video_frames=1500,identical_frame_end_CPU_count=frame_cpu,final_RAM_different_bytes=len(diff),final_RAM_differences_only_declared_entry_patch=True,final_RAM_difference_addresses=[hex(i)for i in diff],direct_prior_unallocated_baseline_artifacts_equal=base_equal,PCM_nonzero_samples=c['audio'].get('nonzero_samples'),audible_playback_proved=False,source_checkpoint_inherited_repair_bytes=18)
paths=[Path(__file__),ROOT/'scripts/check_biwn_native_button_game.py',ROOT/'scripts/check_biwn_native_button_movable.py',Path(r['core']),Path(r['frame_controller_script']),out/'reference-overlay.json',out/'candidate-overlay.json',out/'reference/report.json',out/'candidate/report.json',out/'call-boundaries.json',out/'frame-comparison.json',out/'reference/CPU-before-instructions.bin',out/'candidate/CPU-before-instructions.bin',out/'reference/final-RAM.bin',out/'candidate/final-RAM.bin']
p['artifacts_sha256']={str(path):sha(path)for path in paths};save(out/'protocol.json',p);save(pfile,p);save(ROOT/'verification/native-button-game-active.json',p)
print(json.dumps({k:p[k]for k in ['matched_video_frames','identical_frame_end_CPU_count','final_RAM_different_bytes','PCM_nonzero_samples','direct_prior_unallocated_baseline_artifacts_equal']}))
