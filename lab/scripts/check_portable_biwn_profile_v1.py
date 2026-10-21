"""Check a game-only copied MCP/preset installer against shadow destinations."""
import hashlib,importlib.util,json,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 state=read(V/'portable-biwn-current-v1-current.json');package=Path(state['package']);out=Path(state['directory'])/'profile-checks';out.mkdir();live=Path.home()/'.lmstudio/mcp.json';before=sha(live)
 source=(Path(state['baseline'])/'install_current_profile.py').read_text().replace("PRESETS=['Game Assistant.preset.json','Advertising Assistant.preset.json','Advertising Research Desk.preset.json','Advertising Source Reviewer Experimental.preset.json']", "PRESETS=['Game Assistant.preset.json']").replace('four saved presets','the game preset');installer=package/'install_biwn_profile.py';installer.write_text(source)
 launcher=package/'Install BIWN Profile in LM Studio.command';launcher.write_text('#!/bin/zsh\nset -eu\nBIWN_PACKAGE=${0:A:h}\nunset PYTHONPATH PYTHONHOME VIRTUAL_ENV\n"$BIWN_PACKAGE/runtime/python/bin/python3.12" "$BIWN_PACKAGE/repair_copied_runtime_v8.py"\n"$BIWN_PACKAGE/runtime/python/bin/python3.12" "$BIWN_PACKAGE/install_biwn_profile.py" --install\n');launcher.chmod(0o755);subprocess.run(['zsh','-n',str(launcher)],check=True)
 spec=importlib.util.spec_from_file_location('copied_biwn_profile_installer',installer);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);shadow=package/'test-results/current-biwn-profile-shadow';shadow.mkdir();save(shadow/'mcp.json',dict(mcpServers={'unrelated-test':dict(command='/usr/bin/true',args=[])}));prior=(shadow/'mcp.json').read_bytes();plan=module.install(shadow,write=False);assert(shadow/'mcp.json').read_bytes()==prior
 installed=module.install(shadow,write=True);config=read(shadow/'mcp.json');assert len(config['mcpServers'])==5 and config['mcpServers']['unrelated-test']==dict(command='/usr/bin/true',args=[])
 assert (Path(installed['backup'])/'mcp.json').read_bytes()==prior and module.PRESETS==['Game Assistant.preset.json'];assert sha(shadow/'config-presets/Game Assistant.preset.json')==sha(package/'workbench/presets/Game Assistant.preset.json')
 collision=package/'test-results/current-biwn-profile-collision';collision.mkdir();save(collision/'mcp.json',dict(mcpServers={'local-ai-lab':dict(command='/usr/bin/python3',args=['/unrelated/server.py'])}));prior=sha(collision/'mcp.json')
 try:module.install(collision,write=True)
 except ValueError as error:message=str(error)
 else:raise AssertionError('Unrelated server collision accepted')
 assert sha(collision/'mcp.json')==prior and sha(live)==before
 # Preserve exact currently installed native Chat source as an explicitly
 # unmigrated reference;its private socket transport needs a separate adapter.
 plugin=Path.home()/'.lmstudio/extensions/plugins/local/visible-local-team';archive=package/'workbench/native-chat-installed-reference';archive.mkdir()
 for name in ['index.mjs','manifest.json','package.json']:
  shutil.copy2(plugin/name,archive/name);assert sha(plugin/name)==sha(archive/name)
 save(archive/'scope.json',dict(status='exact_installed_source_reference_not_portable_plugin_install',current_workspace='~/.lmstudio/local-ai-lab',private_socket_transport_rebinding_required=True,new_plugin_installed=False,new_native_Chat_rendering_verified=False))
 save(out/'installer-plan.json',plan);save(out/'shadow-install.json',installed);save(out/'collision.json',dict(rejected=True,message=message));paths=[Path(__file__),installer,launcher,out/'installer-plan.json',out/'shadow-install.json',out/'collision.json',archive/'index.mjs',archive/'scope.json']
 result=dict(status='terminal_moved_biwn_profile_shadow_install_and_collision_checks_pass',directory=str(out),package=str(package),copied_game_presets=1,shadow_MCP_servers=5,unrelated_server_preserved=True,collision_rejected_without_mutation=True,live_MCP_unchanged=True,source_bytes_archived=True,native_Chat_transport_migrated=False,new_predictions=0,new_training=False,source_sha256={str(p):sha(p)for p in paths},scope=__doc__);save(out/'review.json',result);save(V/'portable-biwn-profile-v1-current.json',result);print(result['status'])
if __name__=='__main__':main()
