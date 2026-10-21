"""Logged resident-model roles audit connected CPU pipeline and scope."""
import fcntl,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')

def main():
    evidence={name:json.loads((ROOT/'verification'/name).read_text())for name in ['biwn-text-checks.json','biwn-sprite-checks.json','biwn-inventory-pipeline-checks.json']}
    runtime=json.loads((ROOT/'verification/biwn-inventory-pipeline-runtime-review.json').read_text());evidence['original_game_write_review']={key:runtime[key]for key in ['groups_compared','drawing_and_text_word_records','nested_text_word_records','main_drawing_word_records','matched','limits']}
    evidence['original_assembly_excerpts']={'sprite':'E2B8 JSR E098; E2BE/2C6/2CE copy three stackargs toF0320C/10/14; E2D6 publish4B00; E2E0 CMP.L#4B00,F03204; E2EA BEQ E2E0; E2EC JSR E098; E2F2 RTS. E098 TST.L F03200; BNE E098; RTS.',
        'text_empty':'14B78 CLR.L D0;14B7A MOVE.B3(A3),D0;14B7E SWAP D0;14B80 CLR.W D0;14B82 save D0local2C;14B86 CLR.W D2;14B88 MOVE.B(A4)+,D2;14B8A TST.W D2;14B8C BEQ14C9C;14C9C MOVE.L local2C,D0;restore andRTS14CA8.',
        'type3':'149D4 MOVE.B(A3),D0;149D6 CMP.W#2,D0;149DA BEQ149FE;149DC CMP.W#3,D0;149E0 BNE14A22;149F0 JSR147A6;149FA BRA14CA0. No color/mode arguments forwarded to147A6.',
        'alignment':'14780 MOVE.W D0,D1;14782 NEG.W D1;14784 ADD.W10(SP),D0;14788 AND.W D2,D0;1478A AND.L#FFFF,D0; if nonzero subtract mask-(value-1) fromD1word;1479A CLR.L D0;1479C MOVE.W D1,D0;1479E BSET.L#16,D0.'}
    question='Explain what the connected inventory CPU pipeline now proves and what still prevents a rebuilt frame. Include: empty string return when font height=11, whether unequal nonzero acknowledgement is accepted, and whether glyph pixels were reconstructed. Keep under160words.'
    out=ROOT/'runs'/(lab.stamp()+'-game-pipeline-review');out.mkdir();save(out/'protocol.json',{'question':question,'evidence':evidence,'model':lab.CONFIG['models']['advertising'],'roles':['analyst','reviewer'],'interface':'localhost nativeAPI, saved for post review; not nativeChat','same_weights_correlated':True})
    previous=[]
    with (ROOT/'runs/.inference.lock').open('w')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        for role in ['analyst','reviewer']:
            task=question if role=='analyst'else('Audit the previous answer against assembly and scoped reports. Return JSON only with keys findings, corrected_empty_string_D0, acknowledgement_rule, graphics_limit, missing_evidence. Do not repeat or endorse the draft without checking each of these. Under160words.')
            result=lab.generate('advertising',lab.COMMON+'\nYour role: '+lab.ROLES['game'][role],json.dumps({'task':task,'evidence':evidence,'previous_draft':previous}),768)
            result['word_count']=len(result['text'].split());save(out/(role+'.json'),result)
            with (out/'prompts-and-responses.txt').open('a')as stream:stream.write(role.upper()+'\nREQUEST:\n'+json.dumps(result['request'],ensure_ascii=False,indent=2)+'\nRESPONSE:\n'+result['text']+'\n\n')
            previous.append({'role':role,'text':result['text'],'word_count':result['word_count']});print(role,result['seconds'],result['word_count'],flush=True)
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'completed_pending_coordinator_review','directory':str(out),'roles':previous}
    save(out/'status.json',report);save(ROOT/'verification/biwn-pipeline-local-review.json',report);print(out,flush=True)

if __name__=='__main__':main()
