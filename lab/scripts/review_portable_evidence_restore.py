"""Review an actual copied-root offline restore; do not broaden it to full migration."""
import json
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
 pp=ROOT/'verification/evidence-restore-pilot-current.json';pilot=read(pp);assert pilot['status']=='terminal_offline_evidence_restore_pilot_pass'and pilot['all_verified_reads_inside_restored_root']and not pilot['original_tree_fallback']and not pilot['full_workbench_restore_verified']
 for p,h in pilot['source_sha256'].items():assert sha(p)==h,p
 old=Path(pilot['directory']);dest=Path(pilot['destination']);files=read(old/'files.json');reads=read(old/'verified-read-paths.json');assert len(files)==pilot['files']==446 and len(reads)==pilot['evidence_files_verified']==451 and all(Path(p).is_relative_to(dest)for p in reads)and sum(x['bytes']for x in files)==pilot['logical_bytes']==3773677391
 stdout=read(old/'standalone-cli.stdout.txt');assert stdout['status']=='verified_offline_relocated_status_snapshot'and stdout['all_verified_reads_inside_restored_root']and stdout['evidence_files_verified']==451 and not stdout['live_MCP_frontend_installed']and not stdout['model_weights_copied']
 assert len(pilot['negative_controls'])==4 and all(x['rejected']for x in pilot['negative_controls']);captured=read(dest/'migration-status-as-recorded.json');assert len(captured['processor_tests'])==5 and all(x['status'].startswith('terminal_')for x in captured['processor_tests'])and captured['experimental_build']['resident_bytes']==23260 and captured['next_component_development']['latest_built_resident_bytes']==26220 and not captured['next_component_development']['gameplay_tested']
 out=ROOT/'verification/evidence-restore-pilot-reviewed'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);report=out/'review.txt';report.write_text(f'''Future workbench migration: verified offline evidence restore pilot

Copied446canonical evidence/source/BIWNasset files,3,773,677,391logical bytes, using446APFSclones into a genuinely different directory:
{dest}

Historical files/hash keys were preserved byte-for-byte. A new strict resolver maps recorded workbench paths to the copy and rejects fallback to the original tree.451artifact checks occur inside the restored root. Builder verifies source and copied hashes; loader verifies the recorded publication/dependencies/additional assets. A standalone invocation of the copied portable_biwn_status.py using the current hostPython3.12also passes. Four controls reject outside-origin paths, parent traversal, a symlink back to the original tree and altered copied evidence; corrupted testcopy restored afterwards. No native/source workbench was modified by these probes.

The snapshot records the23,260gameplay-tested disc plus26,220movement development that was still pending gameplay at capture. It is an immutable historical snapshot, not an updating status window. Five terminal processor receipts came from the actual configuredMCP; their old PIDs are not inspected after restore. All verified artifact reads are inside the copied root; Python/OS/runtime libraries are still current-host dependencies.

Included: canonical published-evidence closure, selected rootPython/command/config/requirements files, originalBIWNdisc and current tested/pendingBIWNassets, and the home-relative model transfer inventory. Excluded:47GBmodelweight transfer, complete historicalruns, all training/corpus/index/toolchain/preset dependencies, a cold-installed relocatedMCP/chat/runtime, full local inference/recompilation from the copy and an off-machine restore. The current inventory for39model resources and the previous10shard audit remain separate evidence; no new full-weight audit or quality claim. Future256GBhardware/performance remain unverified.

This is concrete artifact-path portability progress; fullworkbench/model/config/workflow migration remains unfinished. Current daily config, runtime, models and keyboard preview were not changed.
''')
 paths=[Path(__file__),pp,Path(ROOT/'portable_biwn_status.py'),report,old/'standalone-cli.stdout.txt',old/'standalone-cli.stderr.txt',old/'files.json',dest/'.portable-origin.json',dest/'migration-status-as-recorded.json',old/'verified-read-paths.json'];state=dict(status='terminal_offline_relocated_evidence_reviewed',directory=str(out),report=str(report),bundle_directory=str(dest),files=446,logical_bytes=3773677391,verified_artifact_reads=451,negative_controls=pilot['negative_controls'],standalone_copied_source_CLI_verified=True,current_host_Python_dependency=True,original_tree_fallback=False,model_weights_copied=False,live_MCP_frontend_restored=False,full_workbench_restored=False,off_machine_restore_verified=False,future_hardware_verified=False,source_sha256={str(p):sha(p)for p in paths},scope='Same-host different-root canonical evidence/assets snapshot, not full migration.');save(out/'protocol.json',state);save(ROOT/'verification/evidence-restore-pilot-reviewed-current.json',state);print(json.dumps({k:state[k]for k in ['status','files','logical_bytes','verified_artifact_reads','full_workbench_restored']}))
if __name__=='__main__':main()
