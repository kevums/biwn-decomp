"""Run the vendor-built installed bundle with a synthetic registration host.
Real SDK Chat/schema classes and exact production bytes are used. LM Studio
connection,model replies and UI controller are test doubles;zero predictions.
"""
import hashlib,json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 setup=read(V/'portable-native-team-v1-current.json');contracts=read(V/'portable-native-team-contracts-v1-current.json');out=Path(setup['directory'])/'production-contracts';out.mkdir();old=Path(contracts['directory']);installed=Path.home()/'.lmstudio/extensions/plugins/local'/setup['plugin_name'];production=installed/'.lmstudio/production.js'
 text=(old/'handler-check.mjs').read_text();anchor='const module=await import(pathToFileURL(process.argv[2]).href);';assert text.count(anchor)==1
 replacement=r'''
const {createRequire}=await import('node:module');const vm=await import('node:vm');const fileRequire=createRequire(process.argv[2]);const sdk=fileRequire('@lmstudio/sdk');let registered=null,schematics=null;let done;
const ready=new Promise(resolve=>{done=resolve;});class RegistrationClient{constructor(){this.plugins={getSelfRegistrationHost:()=>({setConfigSchematics(v){schematics=v;},setPredictionLoopHandler(v){registered=v;},initCompleted(){done();}})};}}
const hostRequire=(name)=>name==='@lmstudio/sdk'?{...sdk,LMStudioClient:RegistrationClient}:fileRequire(name);
const bytes=await readFile(process.argv[2],'utf8');const context=vm.createContext({require:hostRequire,console,process,Buffer,setTimeout,clearTimeout,crypto:globalThis.crypto,AbortController});new vm.Script(bytes,{filename:process.argv[2]}).runInContext(context);await Promise.race([ready,new Promise((_,reject)=>setTimeout(()=>reject(Error('Plugin registration timeout')),3000))]);if(typeof registered!=='function'||!schematics)throw Error('Production registration missing');const module={Chat:sdk.Chat,handleTeam:registered};
'''
 text=text.replace(anchor,replacement);script=out/'production-check.mjs';script.write_text(text);env={**os.environ,'HOME':str(old/'shadow-home')};node=Path.home()/'.lmstudio/.internal/utils/node';result=subprocess.run([str(node),str(script),str(production),str(out)],env=env,cwd='/',capture_output=True,text=True,timeout=60);(out/'run.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
 rows=read(out/'handler-cases.json');assert len(rows)==8 and all(row['new_real_predictions']==0 for row in rows)
 proof=dict(status='terminal_exact_vendor_production_registration_and_eight_synthetic_controls_pass',directory=str(out),installed_plugin=str(installed),production_sha256=sha(production),production_registered=True,synthetic_controls=8,new_predictions=0,new_training=False,native_Chat_rendering_verified=False,actual_model_quality_verified=False,source_sha256={str(path):sha(path)for path in [Path(__file__),production,script,out/'run.log',out/'handler-cases.json']},scope=__doc__);save(out/'review.json',proof);save(V/'portable-native-production-v1-current.json',proof);print(proof['status'])
if __name__=='__main__':main()
