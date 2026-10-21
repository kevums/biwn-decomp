"""Install a separately named package-owned BIWN Chat plugin with a managed route.
No model load,unload,prediction or training occurs. Existing plugins are preserved.
"""
import argparse,hashlib,json,os,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
PACKAGE=Path(__file__).resolve().parent

def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def install(destination=None,write=False,activate=False):
 identity=read(PACKAGE/'portable-package-id.json')['id'];name='biwn-portable-'+identity[:8]+'-team';plugin=PACKAGE/'workbench'/name;assert read(plugin/'manifest.json')['name']==name
 home=Path(destination)if destination is not None else Path.home()/'.lmstudio';route=home/'biwn-portable-runtimes'/(identity+'.json');installed=home/'extensions/plugins/local'/name
 payload=dict(portable_package_id=identity,workspace=str(PACKAGE/'workbench'),python=str(PACKAGE/'runtime/python/bin/python3.12'),package_root=str(PACKAGE),plugin_name=name)
 for value in [payload['workspace'],payload['python']]:assert Path(value).resolve().is_relative_to(PACKAGE)and Path(value).exists()
 if route.exists()and read(route).get('portable_package_id')!=identity:raise ValueError('Preserve an unrelated runtime route with this name.')
 if installed.exists():
  ownership=installed/'portable-ownership.json'
  if not ownership.is_file()or read(ownership).get('portable_package_id')!=identity:raise ValueError('Preserve an unrelated installed plugin with this name.')
 result=dict(status='portable_native_team_install_plan',plugin=name,source=str(plugin),destination=str(installed),route=str(route),package_root=str(PACKAGE),changes_live_models=False,changes_old_plugin=False,native_UI_verified=False)
 if not write:return result
 stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');backup=PACKAGE/'backups/portable-native-team'/stamp;backup.mkdir(parents=True)
 if route.exists():shutil.copy2(route,backup/'previous-route.json')
 route.parent.mkdir(parents=True,exist_ok=True);temp=route.with_suffix('.new.json');save(temp,payload);temp.chmod(0o600);os.replace(temp,route);result['backup']=str(backup)
 if activate:
  if destination is not None:raise ValueError('Vendor activation is supported only for the actual LM Studio home.')
  old=Path.home()/'.lmstudio/extensions/plugins/local/visible-local-team/index.mjs';old_hash=sha(old)if old.is_file()else None
  config=Path.home()/'.lmstudio/mcp.json';config_hash=sha(config)if config.is_file()else None
  command=[str(Path.home()/'.lmstudio/bin/lms'),'dev','--install','--yes','--no-notify'];process=subprocess.run(command,cwd=plugin,capture_output=True,text=True,timeout=120);(backup/'vendor-install.log').write_text(process.stdout+process.stderr);result['vendor_exit_code']=process.returncode
  if process.returncode!=0:save(backup/'failed-receipt.json',result);raise RuntimeError(process.stdout[-1500:]+process.stderr[-2500:])
  assert installed.is_dir()and read(installed/'manifest.json')['name']==name
  save(installed/'portable-ownership.json',dict(portable_package_id=identity,package_root=str(PACKAGE),route=str(route),plugin_name=name))
  assert old_hash is None or sha(old)==old_hash,'The original plugin changed during installation'
  assert config_hash is None or sha(config)==config_hash,'The live MCP configuration changed during installation'
  result.update(status='portable_native_team_installed_without_model_or_original_plugin_change',production_sha256=sha(installed/'.lmstudio/production.js'),native_UI_verified=False)
 else:result['status']='portable_native_team_route_shadow_written'
 save(backup/'install-receipt.json',result);save(PACKAGE/'portable-native-team-install-current.json',result);return result

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--install',action='store_true');args=ap.parse_args();print(json.dumps(install(write=args.install,activate=args.install),indent=2))
if __name__=='__main__':main()
