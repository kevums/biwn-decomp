"""Derive a separately named portable game plugin from the installed handler."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=Path(read(V/'portable-biwn-current-v1-current.json')['package']);identity=read(p/'portable-package-id.json')['id'];name='biwn-portable-'+identity[:8]+'-team';source=Path.home()/'.lmstudio/extensions/plugins/local/visible-local-team';target=p/'workbench'/name;assert not target.exists();subprocess.run(['/bin/cp','-cR',str(source),str(target)],check=True,capture_output=True)
 out=V/'portable-native-team-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);original=(source/'index.mjs').read_text();(out/'installed-handler-as-run.mjs').write_text(original)
 # Route registration is explicit and package-specific. A later move changes
 # this small managed route record,not source/evidence bytes or the old plugin.
 text=original.replace('import { homedir } from "node:os";', 'import { homedir } from "node:os";\nimport { readFileSync } from "node:fs";')
 old='const workspace = join(homedir(), ".lmstudio/local-ai-lab");';assert text.count(old)==1
 new='const portableRoute = JSON.parse(readFileSync(join(homedir(), ".lmstudio/biwn-portable-runtimes", '+json.dumps(identity+'.json')+'), "utf8"));\nconst workspace = portableRoute.workspace;\nconst portablePython = portableRoute.python;\nif (!isAbsolute(workspace) || !isAbsolute(portablePython)) throw new Error("Restore/install the BIWN portable Chat profile first.");'
 text=text.replace(old,new).replace('spawn(join(workspace, ".venv/bin/python3.12"),','spawn(portablePython,').replace('join(workspace, "scripts/native_evidence_bridge_v1.py")','join(workspace, "portable_native_context.py")')
 text=text.replace('}, "auto").field("showPrompts"', '}, "game").field("showPrompts"')
 (target/'index.mjs').write_text(text);(target/'src/index.ts').write_text(text)
 manifest=read(target/'manifest.json');manifest.update(name=name,revision=1);save(target/'manifest.json',manifest);pkg=read(target/'package.json');pkg.pop('type',None);pkg.update(name=name,main='index.mjs',description='Visible sequential local BIWN roles using the moved game workbench');save(target/'package.json',pkg)
 # The vendor builder regenerates this bundle on installation.
 if(target/'.lmstudio/production.js').exists():(target/'.lmstudio/production.js').rename(target/'.lmstudio/production-before-port.js')
 shutil.copy2(ROOT/'scripts/portable_native_context_v1.py',p/'workbench/portable_native_context.py');save(p/'workbench/config/native-chat-team.json',dict(source_root=str(p/'workbench'),portable_package_id=identity))
 proof=dict(status='terminal_portable_native_game_handler_derived_pending_contract_tests',directory=str(out),package=str(p),plugin=str(target),plugin_name=name,package_id=identity,source_handler=str(source/'index.mjs'),source_handler_sha256=sha(source/'index.mjs'),new_predictions=0,new_training=False,live_plugin_changed=False,native_Chat_verified=False,source_sha256={str(path):sha(path)for path in [Path(__file__),ROOT/'scripts/portable_native_context_v1.py',out/'installed-handler-as-run.mjs',target/'index.mjs',target/'manifest.json',target/'package.json',p/'workbench/portable_native_context.py',p/'workbench/config/native-chat-team.json']});save(out/'review.json',proof);save(V/'portable-native-team-v2-current.json',proof);print(proof['status'],name)
if __name__=='__main__':main()
