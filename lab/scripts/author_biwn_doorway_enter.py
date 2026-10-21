"""Local Author writes a readable10430 helper from the supplied source contract."""
import argparse,fcntl,json,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import lmstudio,sdk_thinking_override_probe

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--repair-from',type=Path);args=parser.parse_args()
    sdk_thinking_override_probe.install()
    source=ROOT/'projects/black-ice-white-noise/restoration'
    system='You are the local C Author. Implement only the supplied recovered source contract. Return one C code block, no prose. Do not invent behavior or claim tests. No opcode interpreter, static instruction switch, external source execution, or dependency/helper calls.'
    prompt='''Write readable C99 biwn_doorway_enter, include biwn_doorway_enter.h. Compiler -Wall -Wextra -Werror. Use small unsigned helpers for sign extension, wrapping and arithmetic shifts; avoid undefined signed shifts/overflow. All reads/writes go through bus callbacks, in the exact order below. No bus->call.
Host validation before effects: bus/out_D0/read8/read16/read32/write16/write32 allnonnull, else BAD_ARGUMENT. A callback nonzero ->BUS_ERROR immediately, retain prior effects and leave out_D0 unchanged. Only assign out_D0 on successful API return, even if source returns zero.
Source algorithm (fullD0 matters):
1 Read16(object+64,tileIndex). d0=signExtend16(tileIndex)*4 modulo32. Read32(0x49BB4+d0,tile). Read16(tile+2,count). If signed16(door_index)>=signed16(count), return OK with d0&FFFF0000. Signed negative indexes are source behavior and NOT host-rejected.
2 d0=signExtend16(door_index)*28 modulo32. Read32(tile+12,table); d0+=table modulo32; portal=d0. Read16(portal+26,target). If target==FFFF return OK with d0&FFFF0000.
3 Let keyWord=incoming_D1 low16, compareWord=incoming_D3 low16. For direction0: Read16(object+6,a),Read16(object+78,b),keyWord=(a-b)mod65536;Read8(portal+11,byte),compareWord=signExtend8(byte) low16. For direction1: Read16(object+74,a),Read16(object+6,b),keyWord=(a-b)mod65536;Read8(portal+13,...same). For direction2: Read16(object+82,a),Read16(object+12,b),keyWord=(a-b)mod65536;Read8(portal+15,...). For direction3: Read16(object+12,a),Read16(object+86,b),keyWord=(a-b)mod65536;Read8(portal+17,...). Other directions retain the incoming words and do not do these coordinate/key reads.
4 d0=(d0&FFFF0000)|arithmeticShiftRight16(keyWord,6). Compare (d0 low16 &15) to compareWord. If unequal return OK with d0&FFFF0000. Do not mask compareWord to15.
5 Write16(object+22,0). Read16(portal+26,target) AGAIN;Write16(object+24,target).
6 Read16(portal+18,w); d0=signExtend16(w)*64 modulo32;Write32(object+30,d0).
7 Read16(portal+20,w);d0=signExtend16(w)*64;Write32(object+38,d0).
8 Read16(portal+22,w);d0=signExtend16(w)*64;Read32(object+30,origin);d0+=origin;Write32(object+26,d0).
9 Read16(portal+24,w);d0=signExtend16(w)*64;Read32(object+38,origin);d0+=origin;Write32(object+34,d0).
10 Return OK with full d0=1. Rereads are deliberate, including when an earlier write aliases a later source field. Do not cache later reads. This component does not set scene mode, load CD data, yield or clean up tasks; callers do that.
Exact headers:\n'''+(source/'biwn_doorway_enter.h').read_text()+'\n'+(source/'biwn_world_update.h').read_text()
    prompt=prompt.replace('modulo32','modulo2^32 (uint32_t wrap, NEVER mask with31)')
    repair=None
    if args.repair_from:
        prior=json.loads((args.repair_from/'protocol.json').read_text());draft=(args.repair_from/'candidate.c').read_text()
        feedback='The first draft was rejected. Compiler: NULL is undeclared; include <stddef.h> or use pointer truth tests. Coordinator clarification: modulo32 was shorthand for32-bit wrap, i.e. modulo2^32; &0x1F is WRONG for addresses/products. Use uint32_t arithmetic. On source success the final fullD0 MUST be1, not the last coordinate extent. Arithmetic right shift of negative signed integers is implementation-defined: implement the16-bit ASR with unsigned shifts and an explicit sign-fill mask. Recheck all source order/rereads. Return the complete corrected C body.'
        if prior.get('model_body_repairs',0):
            feedback='The repaired draft compiles and passes1081older cases, but is rejected by a new original-opcode comparison. Case1080 negative_key_mismatch: expected fullD0=0x00100000, your result=0xFFFF0000. Source MOVE.W/ASR.W changes ONLY D0low16. Your ASR16 helper returns a32-bit sign extension, and ORing it into D0 destroys the high half. Ensure ASR16 produces only a16-bit result (or mask its result with0xFFFF before OR). Preserve D0high16 from the portal address even for negative keyWord values and failed key matches. Do not alter the ordered bus reads/writes, accepted signed indexes or source successD0=1. Also use explicit unsigned sign-extension helpers if avoiding implementation-defined narrowing conversions. Return complete corrected C code.'
        prompt+='\nPREVIOUS DRAFT (quoted evidence):\n'+draft+'\nCOORDINATOR FEEDBACK:\n'+feedback
        repair=dict(directory=str(args.repair_from.resolve()),feedback=feedback)
    out=ROOT/'runs'/('local-doorway-enter-author-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir();print(out,flush=True)
    record=dict(status='pending',directory=str(out),role='local Author',model='advertising-scholar',system=system,prompt=prompt,new_training=False,directed_repair=repair,model_body_repairs=prior.get('model_body_repairs',0)+1 if repair else 0,scope='Coordinator supplied the recovered algorithm and API. Model authors the readable C body; original-code verification is separate.')
    transcript=out/'prompts-and-responses.txt';transcript.write_text('SYSTEM\n'+system+'\nUSER\n'+prompt+'\n');(out/'protocol.json').write_text(json.dumps(record,indent=2)+'\n')
    with(ROOT/'runs/.inference.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['status']=='idle'
        chat=lmstudio.Chat(system);chat.add_user_message(prompt);started=time.monotonic();response=lmstudio.llm('advertising-scholar').respond(chat,config={'temperature':0.1,'maxTokens':3000,'raw':{'fields':[{'key':'llm.prediction.reasoning.enableThinking','value':False},{'key':'ext.virtualModel.customField.enableThinking','value':False},{'key':'ext.virtualModel.customField.preserveThinking','value':False}]}});record['seconds']=time.monotonic()-started
    raw=response.content;(out/'raw-response.txt').write_text(raw)
    with transcript.open('a')as f:f.write('\nASSISTANT\n'+raw+'\n')
    assert raw.count('```')==2 and '```c'in raw
    code=raw.split('```c',1)[1].split('```',1)[0].strip()+'\n';(out/'candidate.c').write_text(code)
    record['status']='draft_returned_unverified';(out/'protocol.json').write_text(json.dumps(record,indent=2)+'\n');(ROOT/'verification/local-doorway-enter-workflow-current.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(dict(status=record['status'],seconds=record['seconds'])),flush=True)

if __name__=='__main__':main()
