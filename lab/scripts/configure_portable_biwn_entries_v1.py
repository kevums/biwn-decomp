"""Write current game-only entrypoints and a clearly unmeasured future profile."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 state=read(V/'portable-biwn-current-v1-current.json');p=Path(state['package']);out=Path(state['directory']);shutil.copy2(ROOT/'scripts/portable_biwn_entry_v1.py',p/'workbench/portable_biwn.py');source=(ROOT/'scripts/portable_model_setup_template.py').read_text();source=source.replace("[('daily_base','advertising-qwen38'),('trained_reviewer_step8','advertising-reviewer-experimental')]", "[('daily_base','advertising-qwen38')]").replace("choices=['daily_base','trained_reviewer_step8']", "choices=['daily_base']");(p/'workbench/portable_models_game.py').write_text(source)
 # Current launchers select only the game workflow;previous entrypoints are archived.
 for title,action in [('BIWN Current Status','status'),('Live Local BIWN Briefing','reader'),('BIWN Code Test','coder'),('BIWN Coder Live','coder-live'),('Game Model Training Progress','training-progress'),('Model Prompts and Responses','prompts'),('Play BIWN Preview','preview'),('Register Copied Game Model','register-model')]:
  path=p/(title+'.command');path.write_text('#!/bin/zsh\nset -eu\nBIWN_PACKAGE=${0:A:h}\nunset PYTHONPATH PYTHONHOME VIRTUAL_ENV\n"$BIWN_PACKAGE/runtime/python/bin/python3.12" -u "$BIWN_PACKAGE/workbench/portable_biwn.py" '+action+'\nif [[ -t 0 ]]; then print "Press Return to close."; read -r || true; fi\n');path.chmod(0o755);subprocess.run(['zsh','-n',str(path)],check=True)
 launcher=p/'Open BIWN Lab.command';launcher.write_text('''#!/bin/zsh
set -eu
BIWN_PACKAGE=${0:A:h}
unset PYTHONPATH PYTHONHOME VIRTUAL_ENV
print 'BIWN LOCAL LAB'
print '1  Play the installed checkpoint preview'
print '2  Read checked current status'
print '3  Ask the local Reader for a briefing'
print '4  Run local Author -> checks -> Repair'
print '5  Show saved coding prompts and responses'
print '0  Exit'
read -r 'BIWN_CHOICE?Choose [1]: '
case "${BIWN_CHOICE:-1}" in
0) exit 0 ;;
1) BIWN_ACTION=preview ;;
2) BIWN_ACTION=status ;;
3) BIWN_ACTION=reader ;;
4) BIWN_ACTION=coder ;;
5) BIWN_ACTION=coder-live ;;
*) print -u2 'Unknown choice'; exit 2 ;;
esac
"$BIWN_PACKAGE/runtime/python/bin/python3.12" -u "$BIWN_PACKAGE/workbench/portable_biwn.py" "$BIWN_ACTION"
if [[ -t 0 ]];then print 'Press Return to close.';read -r || true;fi
''');launcher.chmod(0o755);subprocess.run(['zsh','-n',str(launcher)],check=True)
 build=read(V/'native-Deck-debug-disc-build-v1-current.json')
 profile=dict(status='planned_256GB_profile_not_hardware_tested',target=dict(description='User-planned future Mac Studio',memory_GiB=256),baseline=dict(context_length=32768,workers=1,roles=['Author','compiler/emulator checks','Repair'],role_execution='Sequential local model roles;deterministic compiler/emulator checks are tools,not model agents.'),capacity_candidates=[dict(context_length=32768,workers=2),dict(context_length=65536,workers=1)],current_evidence=dict(frontend='v22',tools=18,native_module_bytes=40062,native_total_code_bytes=build['linked_component_bytes'],reservation_bytes=build['component_bytes'],candidate_fresh_frames=24965,control_fresh_frames=24964,video_differences=62,final_video_equal=True,local_function_target_CPU_cases=260,local_function_budget_cases=35,model_weights_promoted=False),acceptance=['Run Restore BIWN Setup.command after moving the folder.','Verify copied Python/SDK/model resources and currentMCP/source status.','Rebuild the current native module and compare exact bytes at its image addresses.','Exercise Author/check/Repair with saved prompts and unchanged CPU/RAM/order/error gates.','Evaluate training separately from untouched answer-quality tests;training loss alone is not quality.','Measure load time,first token,token rate,memory pressure and output quality before changing one capacity parameter at a time.'],current_machine_proves_future_capacity=False,whole_game_complete=False,physical_console_verified=False)
 save(p/'profiles/studio256-biwn-current-v1.json',profile)
 readme='''BIWN CURRENT LOCAL LAB

Run Restore BIWN Setup.command after moving this folder. Open BIWN Lab.command offers the game preview, checked status, a local Reader and the Author/check/Repair coding test. The playable preview needs no loaded model. LM Studio must be installed on the destination for model inference;the app itself is not bundled.

Current MCP v22 exposes18tools. Current experimental module contains six geometry helpers;the separately reviewed playable checkpoint preview remains unchanged. Fresh candidate/control had24,965/24,964frames,62video differences and equal finalimages. Fidelity and full-game rebuilding remain incomplete. The saved unedited local10968function passed260targetCPU/RAM/order cases and35budget cases;it is not in a disc. Existing64updatepilot remains unpromoted.

Python, SDK, source, copied models, evidence and the installed preview are package-owned. Historical entrypoints and older receipts are retained as historical data. The new game launchers do not run Advertising tasks. Source/evidence bytes retain their original paths/hashes;the runtime translates declared paths in memory and rejects origin file access. This is a same-host relocation test mechanism,not a security sandbox. Model workflows coordinate with an existing same-host inference lock before applying origin guards;they wait by returning busy rather than interrupting another job.

Register Copied Game Model.command creates a fresh package-specific resource alias in LM Studio;it does not replace the live MCP profile. Reader/code launchers load the package-owned daily model under that alias. Current profile:32Kcontext,one worker,sequential roles. The256GBprofile is planned and unmeasured. Native LM Studio Chat rendering and broader source-generation reliability remain unverified. Model prediction and training tests of this refreshed moved snapshot still require their own runtime results.
'''
 (p/'CURRENT SETUP READ ME.txt').write_text(readme)
 paths=[Path(__file__),ROOT/'scripts/portable_biwn_entry_v1.py',p/'workbench/portable_biwn.py',p/'workbench/portable_models_game.py',p/'profiles/studio256-biwn-current-v1.json',p/'CURRENT SETUP READ ME.txt',*p.glob('*.command')];result=dict(status='terminal_current_biwn_game_entries_written_pending_moved_runtime_checks',directory=str(out),package=str(p),new_predictions=0,new_training=False,live_MCP_unchanged=True,source_sha256={str(path):sha(path)for path in paths});save(out/'entries.json',result);save(V/'portable-biwn-entries-v1-current.json',result);print(result['status'])
if __name__=='__main__':main()
