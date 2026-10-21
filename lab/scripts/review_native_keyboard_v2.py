"""Seal the separate test app's headless/runtime/observer evidence."""
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
RT=Path.home()/'.lmstudio/local-ai-lab/native-preview-v2';V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 out=V/'native-keyboard-review-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 manifest=read(RT/'manifest.json')
 for relative,h in manifest['files'].items():assert sha(RT/relative)==h,relative
 workspace=ROOT/'runs/native-keyboard-v2-20261020T071247.801328Z';runtime=RT/'runs/native-keyboard-v2-20261020T071525.641929Z';a=read(workspace/'protocol.json');b=read(runtime/'protocol.json')
 for result in [a,b]:
  assert result['status']=='terminal_native_keyboard_frontend_stopped_pending_review'and result['headless']and result['frames']==400 and not result['keyboard_window_verified']
  assert result['native_scan_entries']==result['native_scan_returns']==1 and result['native_input_entries']==result['native_input_returns']==result['native_coordinate_entries']==result['native_coordinate_returns']==2
  assert result['original_face_entries']==result['original_face_returns']==2 and result['original_Deck_body_steps']==[0,0,0]and result['invalid_task_identities']==0
  assert result['all_GPU_Deck_guards_pass']and result['immutable_native_code_unchanged'];assert result['GPU_entries']==result['GPU_returns']
  for p,h in result['source_sha256'].items():assert sha(p)==h,p
 assert read(workspace/'frames.json')==read(runtime/'frames.json')
 app=Path.home()/'Applications/BIWN Test Preview.app';binary=app/'Contents/MacOS/BIWNTestPreview';assert binary.exists();subprocess.run(['codesign','--verify','--deep','--strict',str(app)],check=True,capture_output=True)
 assert (Path.home()/'Desktop/BIWN Test Preview.app').resolve()==app
 assert (Path.home()/'Desktop/BIWN Native Preview.app').resolve()==Path.home()/'Applications/BIWN Native Preview.app'
 assert '13) "$LAB_ROOT/Play BIWN Test Preview.command" ;;'in(ROOT/'Open Local AI Lab v7.command').read_text()
 nonintrusion=read(V/'preview-v2-nonintrusion-current.json');assert nonintrusion['status']=='terminal_preview_observer_400frame_nonintrusion_match'
 for p,h in nonintrusion['source_sha256'].items():assert sha(p)==h,p
 bound=[Path(__file__),RT/'manifest.json',ROOT/'scripts/package_native_keyboard_v2.py',ROOT/'scripts/run_biwn_native_keyboard_v2.py',ROOT/'scripts/native_preview_observer_v2.c',ROOT/'scripts/native_preview_app_launcher_v3.c',binary,app/'Contents/Info.plist',ROOT/'Open Local AI Lab v7.command',ROOT/'Play BIWN Test Preview.command',ROOT/'BIWN Test Preview - Start Here.txt',workspace/'protocol.json',runtime/'protocol.json',workspace/'frames.json',runtime/'frames.json',V/'preview-v2-nonintrusion-current.json',V/'native-Deck-shared-reviewed-v2-current.json']
 bound.extend(RT/p for p in manifest['files']);bound.extend(Path(p)for p in nonintrusion['source_sha256'])
 proof=dict(status='terminal_three_caller_test_app_headless_and_runtime_reviewed',directory=str(out),app=str(app),Desktop_shortcut=str(Path.home()/'Desktop/BIWN Test Preview.app'),main_menu_option=13,previous_Desktop_preview_preserved=True,runtime=str(RT),workspace_and_runtime_matched_frames=400,app_binary_headless_invocation_tested=True,observer_on_off_full_CPU_banks_RAM_video_GPU_DSP_matched_frames=400,native_scan_calls=1,native_input_calls=2,native_coordinate_calls=2,original_face_calls=2,guard_checks_pass=True,immutable_code_matches=True,keyboard_window_verified=False,live_keyboard_events_verified=0,ordinary_input_is_declared_headless_fixture=True,checkpoint_restored=True,fresh_boot=False,audio_sink_opened=True,audible_game_audio_verified=False,nonzero_PCM_samples=0,new_predictions=0,new_training=False,whole_game_complete=False,physical_console_verified=False,future_hardware_verified=False,source_sha256={str(p):sha(p)for p in set(bound)},scope=__doc__+' Actual native app executable invoked the runtime Python with headless arguments. This is not an observed new GUI window or live key event. Separate new Desktop app; existing tested keyboard app and default remain available. Bundle needs the installed Python runtime and clang; not a standalone future-host acceptance.')
 save(out/'review.json',proof);save(V/'native-keyboard-reviewed-v2-current.json',proof);print(proof['status'],flush=True)
if __name__=='__main__':main()
