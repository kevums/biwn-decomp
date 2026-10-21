"""Create a new self-contained Python/SDK/CLI/toolchain package from the cold copy.
Preserve the preceding package/live installation. Uses APFS clones, copied exact
installed dependencies and frozen current evidence; no download or new training.
"""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def main():
 source=Path(read(V/'cold-runtime-model-reviewed-current.json')['package']);stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out=V/'portable-sdk-workbench'/stamp;out.mkdir(parents=True);target=Path.home()/'Documents/Local AI Lab Restore Tests'/(stamp+'-sdk');assert not target.exists()
 state=dict(status='cloning_portable_sdk_workbench',pid=os.getpid(),directory=str(out),source_package=str(source),package=str(target),live_configuration_changed=False,new_training=False,completed=0)
 def mark():save(out/'protocol.json',state);save(V/'portable-sdk-workbench-active.json',state)
 mark();subprocess.run(['/bin/cp','-cR',str(source),str(target)],check=True,capture_output=True);records=[]
 def copy_file(src,dst):
  src,dst=Path(src),Path(dst);dst.parent.mkdir(parents=True,exist_ok=True);subprocess.run(['/bin/cp','-c',str(src),str(dst)],check=True,capture_output=True);records.append(dict(source=str(src),target_relative=str(dst.relative_to(target)),bytes=src.stat().st_size,sha256=sha(src)));assert sha(dst)==records[-1]['sha256']
 def overlay(src,dst):
  src,dst=Path(src),Path(dst);assert src.name==dst.name;dst.parent.mkdir(parents=True,exist_ok=True);subprocess.run(['/bin/cp','-cR',str(src),str(dst.parent)],check=True,capture_output=True)
 runtime=target/'runtime';workbench=target/'workbench';site=runtime/'.venv/lib/python3.12/site-packages';backup=target/'backups/site-packages-before-sdk';backup.parent.mkdir(exist_ok=True);site.rename(backup);overlay(ROOT/'.venv/lib/python3.12/site-packages',site)
 state['status']='copying_current_CLI_and_source_evidence';mark()
 for p in ROOT.iterdir():
  if p.is_file()and(p.suffix in ['.py','.command']or p.name in ['lab','config.json']):copy_file(p,workbench/p.name)
 for directory in ['scripts','presets','model-definitions','config','corpus','indexes']:overlay(ROOT/directory,workbench/directory)
 overlay(ROOT/'projects/black-ice-white-noise/restoration',workbench/'projects/black-ice-white-noise/restoration');overlay(ROOT/'tools/m68k-elf',workbench/'tools/m68k-elf')
 for p in ROOT.glob('*.py'):copy_file(p,runtime/p.name)
 copy_file(ROOT/'config.json',runtime/'config.json');overlay(ROOT/'corpus',runtime/'corpus');overlay(ROOT/'indexes',runtime/'indexes')
 publication=read(V/'current-biwn-latest-publication-current.json')
 for i,(p,h)in enumerate(publication['dependencies_sha256'].items()):
  p=Path(p);assert p.is_relative_to(ROOT)and sha(p)==h,str(p);copy_file(p,workbench/p.relative_to(ROOT))
  if i%128==0:state['completed']=i+1;mark()
 copy_file(V/'current-biwn-latest-publication-current.json',workbench/'verification/current-biwn-latest-publication-current.json')
 copy_file(ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi',workbench/'projects/black-ice-white-noise/originals/BIWN#23.cdi')
 copy_file(Path.home()/'.lmstudio/bin/lms',target/'lmstudio-home/bin/lms')
 adapter=(source/'runtime/portable_runtime_paths_v3.py').read_text();old="local = any(within(filename, root) for root in roots)";assert old in adapter;adapter=adapter.replace(old,"local = any(within(filename, root) for root in roots) and not any(within(filename, str(runtime / name)) for name in ['.venv', 'python'])");(runtime/'portable_runtime_paths_v4.py').write_text(adapter)
 (runtime/'sitecustomize.py').write_text('import portable_runtime_paths_v4\nportable_runtime_paths_v4.install()\n')
 (site/'sitecustomize.py').write_text("import sys\nfrom pathlib import Path\nsys.path.insert(0,str(Path(__file__).resolve().parents[4]))\nimport portable_runtime_paths_v4\nportable_runtime_paths_v4.install()\n")
 (runtime/'portable_chat_tools_v4.py').write_text("import portable_runtime_paths_v4\nportable_runtime_paths_v4.install()\nimport chat_tools_current_v10 as entry\nentry.legacy.mcp.run(transport='stdio')\n")
 repair=(ROOT/'scripts/repair_copied_runtime.py').read_text().replace('portable_chat_tools_v3.py','portable_chat_tools_v4.py')
 needle="    config_path.write_text(json.dumps(config,indent=2)+'\\n')";assert needle in repair
 extra="""    for name,script in [('biwn-instruction-workbench','native_fact_chat_tools.py'),('biwn-string-workbench','native_string_chat_tools.py'),('biwn-compiler-workbench','native_ccr_chat_tools.py')]:
        config['mcpServers'][name]=dict(command=str(python),args=[str(root/'workbench/scripts'/script)],env={'PYTHONPATH':str(runtime)})
"""
 repair=repair.replace(needle,extra+needle);(target/'repair_copied_runtime.py').write_text(repair)
 index_repair=(ROOT/'scripts/repair_copied_indexes.py').read_text().replace("sorted((root/'runtime/indexes').glob('*.sqlite'))","sorted([*(root/'runtime/indexes').glob('*.sqlite'),*(root/'workbench/indexes').glob('*.sqlite')])").replace("backup=root/('index-before-path-repair-'+path.name)","backup=root/('index-before-path-repair-'+path.parent.parent.name+'-'+path.name)")
 (target/'repair_copied_indexes.py').write_text(index_repair)
 launcher=target/'Restore Local AI Lab.command';launcher.write_text('#!/bin/zsh\nset -eu\nlab_restore_dir=${0:A:h}\nunset PYTHONPATH PYTHONHOME VIRTUAL_ENV\n"$lab_restore_dir/runtime/python/bin/python3.12" "$lab_restore_dir/repair_copied_runtime.py"\nexec "$lab_restore_dir/runtime/python/bin/python3.12" "$lab_restore_dir/repair_copied_indexes.py"\n');launcher.chmod(0o755)
 env={k:v for k,v in os.environ.items()if k not in ['PYTHONPATH','PYTHONHOME','VIRTUAL_ENV']};run=subprocess.run([str(launcher)],capture_output=True,text=True,env=env,timeout=120);(out/'repair.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
 save(out/'overlaid-files.json',records)
 state.update(status='terminal_portable_SDK_workbench_prepared_pending_execution',completed=len(records),overlaid_files=len(records),current_game_resident_bytes=30036,copied_SDK_and_training_dependencies=True,copied_scripts=True,copied_m68k_toolchain=True,registered_MCP_servers=4,live_configuration_changed=False,source_sha256={str(p):sha(p)for p in [Path(__file__),out/'overlaid-files.json',out/'repair.log',runtime/'portable_runtime_paths_v4.py',runtime/'sitecustomize.py',site/'sitecustomize.py',runtime/'portable_chat_tools_v4.py',target/'repair_copied_runtime.py',target/'repair_copied_indexes.py',target/'path-repair-receipt.json',target/'index-repair-receipt.json']},scope=__doc__);mark();save(V/'portable-sdk-workbench-current.json',state);print(json.dumps({k:state[k]for k in ['status','package','overlaid_files','registered_MCP_servers']}))
if __name__=='__main__':main()
