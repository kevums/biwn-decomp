"""Record native UI observations using LM Studio's own exported transcript."""
import hashlib,json,re,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
save=lambda p,v:p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    source=json.loads((ROOT/'verification/firmware-relocation-review.json').read_text())
    out=Path(source['directory']);export=out/'native-chat-export.md'
    text=export.read_text();parts=re.split(r'^### (System|User|Assistant|Tool)\n',text,flags=re.M)
    messages=[dict(role=r,content=b.strip())for r,b in zip(parts[1::2],parts[2::2])]
    assert [m['role']for m in messages]==['System','User','Assistant','Tool','Assistant','User','Assistant']
    tool_request=json.loads(re.search(r'```json\n(.*?)\n```',messages[2]['content'],re.S).group(1))
    assert tool_request['name']=='project_evidence' and tool_request['parameters']=={'topic':'boot_loader'}
    result=json.loads(re.search(r'```\n(.*?)\n```',messages[3]['content'],re.S).group(1))
    evidence=json.loads(result[0]['text'])
    assert evidence['current_checkpoint']['natural_CPU_jump_to4000']
    assert not evidence['full_BIOS_firmware_boot_verified'] and not evidence['playable_rebuilt_game']
    answers=[messages[i]['content']for i in [4,6]]
    assert len(answers[0].split())<=140 and len(answers[1].split())<=110
    assert 'not standalone' in answers[1] and '4E75 RTS' in answers[1]
    now=datetime.now(timezone.utc).isoformat()
    record=dict(status='native_Chat_two_visible_role_responses_and_evidence_call_verified',recorded_at=now,directory=str(out),chat_title='BIWN — Local Roles and Firmware Checkpoint',interface='LM Studio native Chat, operated only via cua_repl; native app Markdown export',native_Chat_verified=True,native_Chat_verification_scope='Observed model selection, Game Assistant preset, local-ai-lab evidence call with visible arguments/result, two completed role-formatted responses, and native export. No arbitrary file editing/game execution by Chat.',model='advertising-scholar',model_context=32768,model_parallel=1,thinking_off_observed=True,preset='Game Assistant',integration='local-ai-lab',messages=messages,answer_words=[len(x.split())for x in answers],tool_request=tool_request,export_path=str(export),export_sha256=sha(export),followup_UI_generation_info=dict(tokens=168,tokens_per_second=22.97,displayed_seconds_value=0.64,displayed_seconds_meaning_not_assumed=True,stop_reason='EOS Token Found'),coordinator_review=dict(first_response='core scope accepted; installs/TOC wording describes aggregate checked chain, with its host-prelude limit retained by Reviewer',second_response='core standalone relocation/source patch/coldRAM/remaining boot scope accepted; coordinator facts supplied in prompt',roles_are_one_model=True,independent_agents=False,broad_reliability_proved=False),historical_tool_native_Chat_flag='false in the saved source checkpoint; this later native UI test does not alter that historical source artifact',new_weight_training=False,model_defaults_changed=False,whole_game_complete=False)
    save(out/'native-chat-review.json',record);save(ROOT/'verification/firmware-native-chat-review.json',record)
    (out/'who-prompts-and-responses.txt').write_text((out/'who-prompts-and-responses.txt').read_text()+'\nNATIVE CHAT\nExact app export including system, user prompts, tool request/result and both local responses:\n'+str(export)+'\nReview:\n'+str(out/'native-chat-review.json')+'\n')
    for name in ['START HERE.txt','CURRENT LOCAL INFERENCE.txt']:
        shutil.copy2(ROOT/name,out/('prior-'+name))
    ad=json.loads((ROOT/'verification/advertising-analysis-v2-review.json').read_text())
    ad_path=ROOT/'verification/advertising-analysis-v2-review/20261015T010126.787930Z'
    (ROOT/'START HERE.txt').write_text(f'''LOCAL AI — START HERE
Updated {now}

1. LM Studio Chat is ready with advertising-scholar, Game Assistant and local-ai-lab enabled.
2. Open “BIWN — Local Roles and Firmware Checkpoint” to see the prompts, evidence call and Analyst/Restorer/Reviewer responses.
3. Ask your next question in ordinary language. After a restart, double-click Game Model.command or Advertising Model.command, select the loaded model, then choose the matching assistant preset.
Example: Where are we with Black Ice White Noise, and can I play it yet?
Picture: Show the current interior drawing.
Advertising: Compare measured involvement in Olsen’s survey with a hypothetical randomized advertising experiment.

CURRENT GAME RESULT
The game’s own loader reads the large stage from disc and continues directly into startup. Two original/C profiles match stage/assets/movie transport,187movieframes and12worldcycles. A separate49instruction ROM bootstrap reconstruction now matches12clean original/C zeroRAM fixtures and naturally jumps to relocated firmware code. Connecting the remaining firmware/authentication/DSP loading is unfinished; the game is not playable yet.

LOCAL INFERENCE TEST
Native Chat completed the visible evidence lookup and two role-formatted answers (84 and88words). One local model plays these roles; they are not independent verification. The second answer’s UI showed22.97tokens/sec,168tokens and EOS completion. This is one bounded test, not broad reliability or a256GB benchmark.

ADVERTISING
The everyday model is loaded. Analysis Pilot v2 is trained and loadable but experimental: research/rubric/tool-call failures prevent promotion. Coordinator-corrected lesson:
{ad_path/'coordinator-corrected-lesson.txt'}

EXACT PROMPTS / RESPONSES / TOOL RESULT
{export}
SOURCE AND LOCAL REVIEW
{out/'review.json'}
{out/'native-chat-review.json'}
ADVERTISING AUDIT
{ad_path/'review.json'}
''')
    (ROOT/'CURRENT LOCAL INFERENCE.txt').write_text(f'''CURRENT LOCAL INFERENCE
Updated {now}

Everyday model: local/advertising-qwen38,27B/6bit,advertising-scholar,32,768context,oneworker,60minuteTTL. Daily weights/presets/defaults unchanged. Separate experimental Advertising Analysis Pilot v2 remains trained/loadable/unpromoted.

NATIVE CHAT
Visible Chat: BIWN — Local Roles and Firmware Checkpoint.
Game Assistant preset, thinking off, local-ai-lab integration enabled. One project_evidence call with boot_loader argument/result and two completed responses:84words on current game scope,88words on the new standalone firmware proof. Second response:168tokens,22.97tokens/sec,EOS; UI0.64s field is recorded without assuming total runtime.
Exact app export includes system prompt,user prompts,tool request/result and responses:
{export}
{out/'native-chat-review.json'}
Analyst/Restorer/Reviewer are roles of the same model, not independent agents. This verifies the observed Chat/evidence interaction only. Chat does not perform arbitrary source edits or full-game execution. Native advertising/rendering/broad reliability and future256GB performance are not established by this test.

SOURCE WORK
Coordinator reconstructed actual ROM802000 bootstrap to its naturalRAM500D6 jump.12clean original/C zeroRAM fixtures/all49instructions,fullCPU/bothstackbanks/privateRAM/hardware and clean shutdown. Separate from unchanged connected game180000->4000/startup/movie/world proof. Preceding authenticated firmware/DSP header-load/game dispatch and global clocks remain incomplete.
Both initial SDK source-role drafts were rejected:4E75 miscalled NOP and resource loop confused with50000 maincode copy. Native follow-up correctly retained the coordinator's source correction. Reused facts/questions and supplied corrections are not an independent generalization benchmark.
Repeated-byteRAM comparisons matched but process shutdown crashed; preserved failed runs are not clean passes. Cause unresolved. Clean fixture domain is zero-filled RAM.
{out/'review.json'}

ADVERTISING
Analysis Pilot v2:36examples(30/3/3),sixsource-checkednewtargets,32steps/rank8/last2layers. Testloss1.82244->1.33735; package1.33565 within0.01tolerance. Native32kload and text inference verified. Sampling/significance/grammar/rubric/tool-format failures prevent promotion; daily base remains active.
{ad_path/'coordinator-corrected-lesson.txt'}
{ad_path/'who-prompts-and-responses.txt'}
{ad_path/'review.json'}
''')
    for name in ['START HERE.txt','CURRENT LOCAL INFERENCE.txt']:
        target=out/('current-'+name);shutil.copy2(ROOT/name,target)
    source.update(native_chat_review=str(out/'native-chat-review.json'),native_Chat_verified=True,native_Chat_scope=record['native_Chat_verification_scope'],whole_game_complete=False)
    source['manifest'].append(dict(source=str(export),snapshot=str(export),sha256=sha(export)))
    save(out/'review.json',source);save(ROOT/'verification/firmware-relocation-review.json',source)
    npath=ROOT/'verification/NEXT SOURCE AND INFERENCE WORK.json';n=json.loads(npath.read_text());n.update(native_chat_audit=str(out/'native-chat-review.json'),native_Chat_verified=True,native_Chat_scope=record['native_Chat_verification_scope']);save(npath,n)
    assert len((ROOT/'START HERE.txt').read_text().splitlines())<45
    assert sha(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib')=='c2990c86f54473b55a68ee2493c50b6e584e4ac81a46bfb7e593611133e8e856'
    assert sha(ROOT/'render-assets/jaguarcd_bios.bin')=='646a0687a01dc6c1fffff508ca25c14b78d30bdfcfa958d4c3e20f6bf78e4f1b'
    assert all(sha(Path(item['snapshot']))==item['sha256']for item in source['manifest'])
    print(json.dumps(dict(status=record['status'],answer_words=record['answer_words'],native_export=str(export),whole_game_complete=False)))

if __name__=='__main__':main()
