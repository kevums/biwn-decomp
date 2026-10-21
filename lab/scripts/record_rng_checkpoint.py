"""Record the nine RNG routines, startup integration and native Chat audit."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def selected(message):return message['versions'][message['currentlySelected']]
def chat_rows(document):
 rows=[]
 for m in document['messages']:
  v=selected(m)
  if v['role']=='user':rows.append({'question':''.join(b['text']for b in v['content']if b['type']=='text'),'answer':'','tool_calls':[],'tool_results':[],'generation_statistics':[]})
  elif v['role']=='assistant'and rows:
   for step in v.get('steps',[]):
    if 'genInfo'in step:rows[-1]['generation_statistics'].append(step['genInfo']['stats'])
    for b in step.get('content',[]):
     if b['type']=='text':rows[-1]['answer']+=b['text']
     elif b['type']=='toolCallRequest':rows[-1]['tool_calls'].append({k:b[k]for k in ['name','parameters']})
     elif b['type']=='toolCallResult':rows[-1]['tool_results'].append({'name':b['name'],'content':json.loads(b['content'])})
 return rows

def main():
 now=datetime.now(timezone.utc).isoformat();rng=read(ROOT/'verification/biwn-rng-checks.json');linked=read(ROOT/'verification/biwn-render-rng-runtime-checks.json');mcp=read(ROOT/'verification/rng-MCP-check.json')
 assert rng['CPU_cases']==2194 and rng['CPU_instruction_coverage']==[187,187]and rng['host_guards']==42
 assert linked['cases']==144 and linked['RNG_fill_iterations']==36720 and linked['RNG_initializations']==144 and linked['render_task_caller_instruction_coverage']==[98,98]
 assert linked['created_task_calls']==2304 and linked['public_context_header_bytes_compared']==38 and linked['saved_context_CCR_bits_compared']
 assert len(linked['startup_scripted_targets'])==5 and len(linked['render_scripted_targets'])==6
 for proof in [rng,linked]:
  out=Path(proof['directory']);assert read(out/'status.json')['status']=='terminal_pass'
  for n,sha in proof['source_sha256'].items():assert hashlib.sha256((ROOT/'projects/black-ice-white-noise/restoration'/n).read_bytes()).hexdigest()==sha
  for n,sha in read(out/'harness-snapshot/manifest.json').items():assert hashlib.sha256((out/'harness-snapshot'/n).read_bytes()).hexdigest()==sha
 assert mcp['status']=='fresh_installed_RNG_and_render_startup_evidence_passed'and len(mcp['tools'])==6
 # These files are read-only snapshots of interactions performed through CUA.
 native_path=Path.home()/'.lmstudio/conversations/1791902526993.conversation.json';native=read(native_path);old_path=Path.home()/'.lmstudio/conversations/1791860011452.conversation.json';old=read(old_path)
 prompt=(ROOT/'presets/Game Assistant.system.txt').read_text().strip();fields=native['perChatPredictionConfig']['fields'];assert next(f['value']for f in fields if f['key']=='llm.prediction.systemPrompt')==prompt
 rows=chat_rows(native);assert len(rows)==3
 assert rows[0]['tool_calls']==[{'name':'project_evidence','parameters':{'topic':'status'}}]
 assert rows[0]['answer'].startswith('No,')and all(x in rows[0]['answer']for x in ['70','4 of 21','17 unported','3 bodies','18 contexts','incomplete'])
 assert rows[1]['tool_calls']==[{'name':'project_evidence','parameters':{'topic':'rng'}}]
 assert rows[1]['answer'].startswith('No,')and '0xabcd1234'in rows[1]['answer']and'0xffff'in rows[1]['answer']
 assert rows[2]['tool_calls']==[{'name':'render_inventory_preview','parameters':{}}]
 metadata=next(json.loads(b['text'][b['text'].index('{'):])for r in rows[2]['tool_results']for b in r['content']if b['type']=='text')
 assert rows[2]['answer'].split('\n\n')[-1]==metadata['verified_caption'] and metadata['raw_frame_sha256']=='2234cbb2e4c1fe8b97e2193d10f25846dc0a81b9dd18d7ba4dcc8791ee166e62'
 assert any(b['type']=='image'for r in rows[2]['tool_results']for b in r['content'])
 assert all(stats['stopReason']=='eosFound' for row in rows for stats in row['generation_statistics'])
 for row,limit in zip(rows,[60,45,100]):assert len(row['answer'].split())<=limit
 oldrow=chat_rows(old)[-1];assert oldrow['question']==rows[0]['question']and not oldrow['tool_calls']
 out=ROOT/'verification/native-rng-chat'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 shutil.copy2(native_path,out/native_path.name);shutil.copy2(old_path,out/'earlier-Quick-Start.conversation.json');shutil.copy2(ROOT/'presets/Game Assistant.system.txt',out/'system-prompt.txt');shutil.copy2(metadata['image_path'],out/'native-inventory-panel.png');assert hashlib.sha256((out/'native-inventory-panel.png').read_bytes()).hexdigest()==metadata['png_sha256']
 # Do not duplicate base64 image data in the readable audit.
 readable=[]
 for row in rows:
  readable.append({**row,'tool_results':[{'name':r['name'],'content':[b if b['type']!='image'else {'type':'image','mimeType':b.get('mimeType'),'base64_omitted':True}for b in r['content']]}for r in row['tool_results']]})
 review={'recorded_at':now,'status':'native_status_RNG_and_inventory_caption_passed','directory':str(out),'conversation':str(native_path),'native_chat_name':native['name'],'system_prompt_characters':len(prompt),'questions':readable,'earlier_history_failure':{'conversation':str(old_path),'question':oldrow['question'],'answer':oldrow['answer'],'reason':'Used historical chat evidence without a fresh tool call; not accepted as current-progress retrieval.'},'native_inventory_UI_image_visually_confirmed':True,'scoped_inventory_tool_permission':'Always allow render_inventory_preview enabled through native UI; other tool permissions unchanged.','audit_parser_repair':'Inventory result is caption plus JSON and a local-image Markdown block; validator initially expected bare JSON/caption. Parser corrected to the observed native format; no model/tool correction required.','limits':'Three native Chat samples only; not general reliability or response-time benchmark. Generation statistics are recorded per prediction and are not end-to-end wall time. Image tool block, saved PNG hash and CUA screenshot confirm native UI visibility.'}
 save(out/'review.json',review);save(ROOT/'verification/native-rng-chat-review.json',review)
 (out/'prompts-and-responses.txt').write_text('NATIVE LM STUDIO CHAT — '+native['name']+'\n\nSYSTEM\n'+prompt+'\n\n'+'\n\n'.join('USER\n'+r['question']+'\nTOOL CALLS\n'+json.dumps(r['tool_calls'],indent=2)+'\nLOCAL MODEL RESPONSE\n'+r['answer'] for r in rows)+'\n\nEARLIER HISTORY ANSWER — REJECTED AS CURRENT RETRIEVAL\n'+oldrow['answer']+'\n')
 model=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(model)==1 and model[0]['identifier']=='advertising-scholar'and model[0]['status']=='idle'
 game=('70 checked C components: 68 CPU and two GPU. Nine RNG routines now match original CPU execution in 2,194 cases, all 187 source instructions and 42 host error checks. Real RNG initialization is connected to the render startup test: 144 native CPU/GPU versus C cases, 36,720 state-fill iterations, 2,304 task creations, 432 handoffs, 144 sprite decodes, 259 display-list calls and 108 text calls. All 98 render-caller instructions, full startup CPU and all 38 public context bytes including saved CCR compare. Final A0/A1, private stacks and ten formatter scratch bytes are excluded.\n\n'
 'Five supplied contexts plus 16 real creations form 21 contexts. Eighteen are deliberately blocked, so only render and two idle bodies execute in this test. Four unique captured task callers are implemented across separate world/render proofs; 17 callers remain unported. Five startup services and six render services remain scripted; the separate world runtime retains 15 nested scripted services. World/render linkage, live actor/asset lifecycles, other task bodies, full 3D drawing, scanout, scenes, main loop and audio remain unfinished. No complete rebuilt game frames or physical-hardware validation. Counts do not imply a completion percentage.')
 roles=('Local 30B coder ran Author, Reviewer and one guided correction in fresh sequential API contexts at per-run temperature 0.2. Author and Reviewer each exhausted 4,096-token budgets and returned byte-identical incomplete drafts. The correction exhausted 8,192 tokens and repeated arithmetic blocks before truncation. All three were rejected before CPU execution: zero CPU cases for the model drafts. The accepted C was authored by the Codex coordinator and independently compared with original execution. These are the same model weights in different roles, not independent agents. No weight training, model promotion or persistent coding-temperature change; the configured coding default remains 0.7.')
 frontend=('Native LM Studio Chat is accessible. A clean chat with the current Game Assistant preset correctly fetched current status and RNG evidence, then called inventory preview and returned its exact checked caption. The earlier Quick Start history answered status without fresh evidence and remains recorded as a failed current-retrieval check. Three clean-chat samples pass; this does not establish general reliability or end-to-end speed. Game Assistant prompt is '+str(len(prompt))+' characters. The everyday 27B base remains loaded, thinking off, 32K context, one worker. Advertising Source Pilot v1 remains trained and loadable but experimental; everyday base remains the default. API role transcripts and native Chat history are separate artifacts.')
 pending=('Continue remaining startup services, connect compatible live world/render/asset lifecycles, reconstruct the remaining 17 task callers and 15 nested world services, expand 3D drawing/scanout/main loop/scenes/audio, and keep validating easy native Chat use. Future 256GB hardware remains unbenchmarked. Full goal active and incomplete.')
 evidence=['verification/biwn-rng-checks.json','verification/rng-checked-examples.json','verification/biwn-render-rng-runtime-checks.json','verification/rng-MCP-check.json','verification/native-rng-chat-review.json',str((out/'prompts-and-responses.txt').relative_to(ROOT)),'runs/20261013T141456.512897Z-local-rng-author-reviewer/prompts-and-responses.txt','runs/20261013T141456.512897Z-local-rng-author-reviewer/one-guided-correction/prompts-and-responses.txt']
 for name in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']:
  p=ROOT/'verification'/name;d=read(p)
  if name=='setup-status.json':d.update(updated_at_utc=now,game_work=game,frontend=frontend,pending=pending)
  elif name=='current-runtime-state.json':d.update(recorded_at=now,model_state_refreshed_at=now,models=model,decomp_progress=game,visible_chat=frontend,MCP_updated_evidence=frontend,local_inference_jobs='All terminal: three local coding drafts rejected before CPU execution; three fresh native Chat samples passed; older-history status retrieval rejected. Model idle.',emulator_jobs='RNG 2194-case proof and 144-case startup integration terminal/pass. No complete rebuilt game frames.',latest_API_ease_review=str(ROOT/'verification/native-rng-chat-review.json'))
  elif name=='everyday-inference.json':d.update(updated_at=now,model_state_refreshed_at=now,model=model,frontend=frontend,latest_native_Chat_review=str(ROOT/'verification/native-rng-chat-review.json'))
  else:
   d.update(recorded_at_utc=now,previous_goal_turn_classification='61 components; full render caller/task creation checked; shortened prompt and repaired current status.',this_goal_turn_classification='70 components; RNG standalone and startup integration passed; local coding drafts rejected; native Chat status/RNG/inventory tests passed after fresh-chat repair.',next_safe_work=pending)
   for item in d['requirements']:
    if 'decompilation test'in item['requirement']:item['state']=game;item['evidence']=list(dict.fromkeys(item['evidence']+evidence))
    elif 'Configure LM frontend'in item['requirement']:item['state']=frontend;item['evidence']=list(dict.fromkeys(item['evidence']+evidence[3:]))
   d['post_review_evidence'].update({Path(e).name:str(ROOT/e)for e in evidence})
  save(p,d)
 config=read(ROOT/'config.json');config['chat_frontend']['game']['status']=game+'\n\n'+frontend;save(ROOT/'config.json',config)
 intake=read(ROOT/'corpus/game/project-intake.json');intake.update(latest_checked_at=now,latest_checked_status=game,latest_rng_check=str(ROOT/'verification/biwn-rng-checks.json'));save(ROOT/'corpus/game/project-intake.json',intake)
 (ROOT/'CURRENT DECOMPILATION.txt').write_text('BLACK ICE WHITE NOISE — CURRENT RECONSTRUCTION\n\n'+game+'\n\nWHO DID WHAT\n'+roles+'\n\nEASY LOCAL INFERENCE\n'+frontend+'\n\nEVIDENCE\n'+'\n'.join(str(ROOT/e)for e in evidence)+'\n\nNEXT WORK\n'+pending+'\n')
 p=ROOT/'START HERE.txt';s=p.read_text();a=s.index('LATEST GAME RESULT\n');b=s.index('TRY ADVERTISING ASSISTANT\n',a);s=s[:a]+'LATEST GAME RESULT\n'+game+'\n\nLOCAL INFERENCE RESULT\n'+frontend+'\n\n'+s[b:];p.write_text(s)
 notes='\nRNG / STARTUP INTEGRATION / NATIVE CHAT — '+now+'\n\n'+game+'\n\nWHO DID WHAT\n'+roles+'\n\n'+frontend+'\n\nThe selector tests the old unsigned word, then always writes the raw new word. Old 00ff/new ffff/incoming abcd1234 returns full abcd1234; old 0100 returns 000000ff with writes 0001 then ffff. Seed/fill returns 000003fc. Signed remainder uses existing checked division; zero divisor is a host error, not original exception emulation. Mutable constants, signed raw selectors and state/selector aliasing are covered in the finite RAM fixtures.\n\nIntegration preflight initially logged an unrelated formatter E540 helper on the original side after the matching startup. The harness was corrected to log RNG math call boundaries only when called from RNG source. No C translation correction was needed; the failed preflight is retained. Full 144-case comparisons then pass.\n\nEVIDENCE\n'+'\n'.join(str(ROOT/e)for e in evidence)+'\n\n'+pending+'\n'
 for name in ['POST REVIEW.txt','projects/black-ice-white-noise/restoration/READ ME.txt']:
  with(ROOT/name).open('a')as f:f.write(notes)
 checkpoint={'recorded_at':now,'components':70,'CPU_components':68,'GPU_components':2,'RNG_CPU_cases':2194,'RNG_instruction_coverage':[187,187],'RNG_host_guards':42,'startup_cases':144,'RNG_initializations':144,'RNG_fill_iterations':36720,'created_tasks':2304,'unique_implemented_callers':4,'unported_callers':17,'executed_bodies_in_fixture':3,'blocked_contexts':18,'startup_services_scripted':5,'render_services_scripted':6,'world_nested_services_scripted':15,'world_render_linked':False,'complete_rebuilt_game_frames':0,'native_Chat_questions_passed':3,'earlier_history_status_retrieval_rejected':1,'model_coding_drafts_rejected':3,'model_draft_CPU_cases':0,'accepted_C_author':'Codex coordinator','known_compute_jobs':'terminal','model_idle':True,'new_weight_training':False,'model_defaults_unchanged':True,'full_goal_status':'active incomplete','evidence':evidence,'backup':read(ROOT/'verification/rng-checkpoint-backup.json')['directory'],'next_work':pending}
 save(ROOT/'verification/rng-checkpoint.json',checkpoint)
 subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts/install_chat_runtime.py')],check=True)
 print(json.dumps({'components':70,'native_chat_samples':3,'goal':'active incomplete','audit':str(out)}))
if __name__=='__main__':main()
