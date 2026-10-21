"""Audit logged, sequential resident-model roles for the drawing protocol."""
from datetime import datetime, timezone
import fcntl, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab,binary_tools
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def main():
    report=json.loads((ROOT/'verification/biwn-inventory-draw-checks.json').read_text());assert report['CPU_cases']==330
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    image=(session/'nextstage-68000-candidate.bin').read_bytes();rows,_=binary_tools.m68k_instructions(image[0x1b786-0x4000:0x1bc78-0x4000],0x1b786)
    source=ROOT/'projects/black-ice-white-noise/restoration'
    evidence={'CPU_checks':report,'original_assembly':rows,'portable_C':(source/'biwn_inventory_draw.c').read_text(),
              'scope':'Sprite E2B8 and text149AE are callbacks in both CPU fixture and portable C. Actual original formatter and its division helper execute in CPU; internal formatter scratch effects excluded from C equivalence. This is command generation, not reconstructed graphics.'}
    task=('Review the drawing protocol against original assembly. Return JSON only, under220words, with keys rows_and_index, rereads, packing_edge_case, command_order, dependencies_and_limits, next_step. Identify a concrete potentially wrong claim or missing behavior if present; do not certify full graphics or whole-game equivalence. Reviewer: inspect prior draft and add errors. Treat checks as scoped evidence, not proof beyond those fixtures. Same-model roles are correlated.')
    out=ROOT/'runs'/(lab.stamp()+'-game-inventory-draw-review');out.mkdir()
    save(out/'protocol.json',{'task':task,'evidence':evidence,'roles':['analyst','reviewer'],'model':lab.CONFIG['models']['advertising'],'native_chat_history':False,'native_UI_status':'Mac locked; localhost continuation authorized','same_weights_correlated':True})
    prior=[]
    with (ROOT/'runs/.inference.lock').open('w')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        for role in ['analyst','reviewer']:
            result=lab.generate('advertising',lab.COMMON+'\nYour role: '+lab.ROLES['game'][role],json.dumps({'task':task,'evidence':evidence,'previous_drafts':prior}),1024)
            result['word_count']=len(result['text'].split());save(out/(role+'.json'),result)
            with (out/'prompts-and-responses.txt').open('a')as stream:stream.write(role.upper()+'\nREQUEST:\n'+json.dumps(result['request'],ensure_ascii=False,indent=2)+'\nRESPONSE:\n'+result['text']+'\n\n')
            prior.append({'role':role,'text':result['text'],'word_count':result['word_count']});print(role,result['seconds'],result['word_count'],flush=True)
    result={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'completed_pending_coordinator_review','directory':str(out),'roles':prior}
    save(out/'status.json',result);save(ROOT/'verification/biwn-inventory-draw-local-review.json',result);print(out,flush=True)

if __name__=='__main__':main()
