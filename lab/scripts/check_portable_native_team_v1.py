"""Exact ported handler with real SDK Chat objects and synthetic model replies.
Actual package source context is obtained read-only. These are software contract
checks,not model predictions,semantic approval or native UI rendering.
"""
import hashlib,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 setup=read(V/'portable-native-team-v1-current.json');package=Path(setup['package']);plugin=Path(setup['plugin']);out=Path(setup['directory'])/'contracts';out.mkdir();py=package/'runtime/.venv/bin/python';request=dict(domain='game',query='BIWN latest decomp status,local typed Repair and current portable setup progress')
 actual=subprocess.run([str(py),str(package/'workbench/scripts/native_chat_team_context.py')],input=json.dumps(request)+'\n',capture_output=True,text=True,timeout=30,cwd='/');(out/'context-stderr.txt').write_text(actual.stderr);assert actual.returncode==0,actual.stderr;context=json.loads(actual.stdout);assert context['status']=='ready'and context['topic']=='deck_readable_source'and context['evidence']['latest_native_candidate']['differing_video_frames']==62 and context['evidence']['game_portable_progress']['tools']==18 and context['evidence']['latest_local_source_generation_trial']['native_function_executed'];save(out/'actual-package-context.json',context)
 # Production helper refuses an actually held shared inference lock;this checks
 # coordination,not evidence readiness or the synthetic shadow helper below.
 busy=subprocess.run([str(package/'runtime/python/bin/python3.12'),str(package/'workbench/portable_native_context.py')],input=json.dumps(request)+'\n',capture_output=True,text=True,timeout=30,cwd='/');save(out/'actual-shared-lock-response.json',json.loads(busy.stdout));assert json.loads(busy.stdout)['status']=='busy'
 home=out/'shadow-home';workspace=out/'shadow-workbench';(home/'.lmstudio/biwn-portable-runtimes').mkdir(parents=True);(workspace/'config').mkdir(parents=True);save(workspace/'config/native-chat-team.json',dict(source_root=str(workspace)));save(workspace/'fixture-evidence.json',context)
 helper=workspace/'portable_native_context.py';helper.write_text('''import fcntl,json,os,sys\nfrom pathlib import Path\nr=Path(__file__).resolve().parent\nwith(r/'lease.lock').open('a')as lock:\n fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);(r/'last-child-pid.txt').write_text(str(os.getpid()));request=json.loads(sys.stdin.readline());q=request['query'];e=json.loads((r/'fixture-evidence.json').read_text())\n if 'helper-busy'in q:e={'status':'busy','message':'synthetic busy control'}\n if 'helper-failed'in q:e={'status':'failed','message':'synthetic failed control'}\n if 'helper-malformed'in q:print('not json',flush=True)\n else:print(json.dumps(e),flush=True)\n sys.stdin.read()\n''')
 save(home/'.lmstudio/biwn-portable-runtimes'/(setup['package_id']+'.json'),dict(workspace=str(workspace),python=str(package/'runtime/python/bin/python3.12')))
 script=out/'handler-check.mjs';script.write_text(r'''
import { readFile,writeFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
const module=await import(pathToFileURL(process.argv[2]).href);
const {Chat,handleTeam}=module;const root=process.argv[3];const modes=['normal','overflow','truncated','markup','cancel','helper-busy','helper-failed','helper-malformed'];const rows=[];
for(const mode of modes){
 let modelCalls=0,tokenSourceCalls=0;const blocks=[];const abort=new AbortController();
 const history=Chat.from([{role:'system',content:'Game restoration assistant'},{role:'user',content:'BIWN latest source and portable status. fixture-'+mode}]);
 const model={async getModelInfo(){return {identifier:'SYNTHETIC SOFTWARE CONTRACT MODEL'};},async getContextLength(){return mode==='overflow'?32:32768;},async applyPromptTemplate(chat){return JSON.stringify(chat.getMessagesArray().map(m=>({role:m.getRole(),content:m.getText()})));},async countTokens(text){return Math.ceil(text.length/4);},respond(chat,options){modelCalls++;return Promise.resolve({content:mode==='markup'?'<tool_call>synthetic</tool_call>':'SYNTHETIC CONTRACT REPLY '+modelCalls,stats:{stopReason:mode==='truncated'?'maxPredictedTokensReached':'eosFound'}});}};
 let error=null;
 try{await handleTeam({getPluginConfig(){return {get(key){return {domain:'game',showPrompts:true,roleMaxTokens:1024}[key];}};},pullHistory:async()=>history,abortSignal:abort.signal,guardAbort(){if(abort.signal.aborted)throw Error('synthetic cancellation');},tokenSource:async()=>{tokenSourceCalls++;return model;},setSenderName:async()=>{},needsNaming:async()=>false,suggestName:async()=>{},createContentBlock(options){const b={options,text:''};blocks.push(b);return {appendText(x){b.text+=x;},async pipeFrom(prediction){const result=await prediction;b.text+=result.content;if(mode==='cancel')abort.abort();return result;}};}});}catch(e){error=String(e);}
 const intro=blocks.find(b=>b.options.style.label==='Team workflow');let session=null;
 if(intro){const folder=intro.text.match(/Full prompts and responses: ([^\n]+)/)?.[1];session=JSON.parse(await readFile(folder+'/session.json','utf8'));for(let i=0;i<session.roles.length;i++){const role=session.roles[i].role;const prompt=await readFile(`${folder}/${i+1}-${role}-prompt.txt`,'utf8');if(blocks.find(b=>b.options.style.label===role+' prompt')?.text!==prompt)throw Error('Prompt block mismatch '+mode);if(session.roles[i].response){const response=await readFile(`${folder}/${i+1}-${role}-response.txt`,'utf8');if(blocks.find(b=>b.options.style.label===role)?.text!==response)throw Error('Response block mismatch '+mode);}}}
 if(mode==='normal'){if(error||modelCalls!==3||session.status!=='terminal_research_team_generation_complete_semantic_review_required')throw Error('Normal role sequence failed '+error);const replies=blocks.filter(b=>['Analyst','Restorer','Reviewer'].includes(b.options.style.label));if(JSON.stringify(replies.map(b=>b.options.includeInContext))!==JSON.stringify([false,false,true]))throw Error('Followup-context isolation failed');}
 else if(!error)throw Error('Invalid control was accepted '+mode);
 if(mode.startsWith('helper-')&&(modelCalls!==0||tokenSourceCalls!==0))throw Error('Helper failure reached model');
 if(mode==='overflow'&&modelCalls!==0)throw Error('Overflow reached model');
 if(['truncated','markup','cancel'].includes(mode)&&modelCalls!==1)throw Error('Failed output continued roles');
 rows.push({mode,modelCalls,tokenSourceCalls,error,session_status:session?.status||null,prompt_blocks_match_saved:true,new_real_predictions:0});
}
await writeFile(root+'/handler-cases.json',JSON.stringify(rows,null,2)+'\n');console.log('Exact portable handler:8synthetic software controls passed;zero real predictions');
''')
 node=Path.home()/'.lmstudio/.internal/utils/node';env={**os.environ,'HOME':str(home)};result=subprocess.run([str(node),str(script),str(plugin/'index.mjs'),str(out)],env=env,capture_output=True,text=True,timeout=60,cwd='/');(out/'handler-check.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
 # Every synthetic helper process exited and released its lease after normal,
 # rejection and cancellation paths;check the actual file lock after the run.
 import fcntl
 with(workspace/'lease.lock').open('a')as lock:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 pid=int((workspace/'last-child-pid.txt').read_text());probe=subprocess.run(['ps','-p',str(pid),'-o','pid='],capture_output=True,text=True);assert probe.returncode!=0,'Context helper is still alive'
 paths=[Path(__file__),plugin/'index.mjs',package/'workbench/portable_native_context.py',script,helper,out/'actual-package-context.json',out/'actual-shared-lock-response.json',out/'handler-cases.json',out/'handler-check.log']
 proof=dict(status='terminal_portable_native_context_and_synthetic_handler_contracts_pass',directory=str(out),package=str(package),plugin=str(plugin),actual_context_ready=True,actual_busy_lock_rejected_before_inference=True,synthetic_handler_cases=8,actual_model_predictions=0,new_training=False,actual_model_quality_verified=False,native_UI_verified=False,lease_released_after_normal_failure_and_cancel=True,source_sha256={str(path):sha(path)for path in paths},scope=__doc__);save(out/'review.json',proof);save(V/'portable-native-team-contracts-v1-current.json',proof);print(proof['status'])
if __name__=='__main__':main()
