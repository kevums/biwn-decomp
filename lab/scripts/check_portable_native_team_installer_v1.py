"""Shadow route ownership/backup/collision controls for the portable Chat installer."""
import hashlib,importlib.util,json,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 setup=read(V/'portable-native-team-v1-current.json');p=Path(setup['package']);out=Path(setup['directory'])/'installer-checks';out.mkdir();target=p/'install_visible_biwn_team.py';shutil.copy2(ROOT/'scripts/portable_native_team_installer_v1.py',target)
 spec=importlib.util.spec_from_file_location('portable_native_installer',target);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);shadow=out/'home';shadow.mkdir();plan=m.install(shadow,write=False);assert not(shadow/'biwn-portable-runtimes').exists()
 first=m.install(shadow,write=True);route=Path(first['route']);prior=route.read_bytes();payload=read(route);payload['workspace']='/previous/package/workbench';save(route,payload);old=route.read_bytes();updated=m.install(shadow,write=True);assert(Path(updated['backup'])/'previous-route.json').read_bytes()==old and read(route)['workspace']==str(p/'workbench')
 payload=read(route);payload['portable_package_id']='unrelated';save(route,payload);prior=route.read_bytes()
 try:m.install(shadow,write=True)
 except ValueError as error:route_error=str(error)
 else:raise AssertionError('Foreign route replaced')
 assert route.read_bytes()==prior;save(route,{**payload,'portable_package_id':setup['package_id']})
 plugin=Path(plan['destination']);plugin.mkdir(parents=True)
 try:m.install(shadow,write=True)
 except ValueError as error:plugin_error=str(error)
 else:raise AssertionError('Foreign plugin replaced')
 assert not(plugin/'portable-ownership.json').exists()
 launcher=p/'Install Visible BIWN Team.command';launcher.write_text('#!/bin/zsh\nset -eu\nBIWN_PACKAGE=${0:A:h}\nunset PYTHONPATH PYTHONHOME VIRTUAL_ENV\n"$BIWN_PACKAGE/runtime/python/bin/python3.12" "$BIWN_PACKAGE/repair_copied_runtime_v8.py"\n"$BIWN_PACKAGE/runtime/python/bin/python3.12" "$BIWN_PACKAGE/install_visible_biwn_team.py" --install\n');launcher.chmod(0o755);subprocess.run(['zsh','-n',str(launcher)],check=True)
 result=dict(status='terminal_portable_native_installer_shadow_ownership_and_backups_pass',directory=str(out),package=str(p),dryrun_no_mutation=True,owned_route_move_update_and_backup=True,foreign_route_rejected=True,foreign_plugin_rejected=True,live_plugin_installed=False,new_predictions=0,new_training=False,source_sha256={str(path):sha(path)for path in [Path(__file__),ROOT/'scripts/portable_native_team_installer_v1.py',target,launcher]});save(out/'review.json',result);save(V/'portable-native-installer-v1-current.json',result);print(result['status'])
if __name__=='__main__':main()
