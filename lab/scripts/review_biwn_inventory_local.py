"""Actual local analysis/review of checked input-selection CPU contracts."""
from datetime import datetime,timezone
import fcntl,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab,binary_tools
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def main():
    checks=json.loads((ROOT/'verification/biwn-inventory-select-checks.json').read_text());assert checks['digit_decoder_CPU_cases']==4096 and checks['selection_block_CPU_cases']==2581
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes()
    ins=[]
    for start,end in [(0x1b718,0x1b780),(0x1a1f0,0x1a254)]:
        rows,_=binary_tools.m68k_instructions(image[start-0x4000:end-0x4000],start);ins+=rows
    source=ROOT/'projects/black-ice-white-noise/restoration'
    evidence={'checks':checks,'instructions':ins,'C_source':(source/'biwn_inventory_select.c').read_text(),
              'critical_facts':['Zero digit uses CLR.W, retaining incomingD0upper16; other digit/default MOVEQ replaces all32bits.','Digit priority is bit19→1,18→4,17→7,7→2,6→5,5→8,4→0,3→3,2→6,1→9; no key returnsFFFFFFFF.',
                                'UIblock rereads input32, byte at49BAE, and source32 on digitpath. Cycle branch compares49D54then rereads it ifnot9. Subtract/copy each reread global memory.',
                                'State words49D54/49D56 and redrawcall boundary are modeled; actual1B786rendering not implemented. The block falls through1A254 rather than returning byRTS.',
                                'Originalgame watch reads emit placeholdervalue0 with no width field in pinnedcore. Do not treat watchread0as actualread data. Runtime replay is being checked separately.']}
    task=('Return JSON only under180words with keys zero_digit_full_D0_example, key_priority, rereads, component_scope, unresolved, next_step. For incomingD0=12345678 and only bit4set, fullD0mustbe12340000. Do not infer original names/controller mapping, redrawimplementation, hardware/fullgame equivalence or wholefunctionRTS. Reviewer must identify unsupported claims in prior draft with errors key; same-model roles are not independent verification.')
    out=ROOT/'runs'/(lab.stamp()+'-game-inventory-review');out.mkdir();save(out/'protocol.json',{'task':task,'evidence':evidence,'roles':['analyst','reviewer'],'model':lab.CONFIG['models']['advertising'],'native_chat_history':False,'native_UI_status':'Maclocked; localhost continuation authorized','same_weights_correlated':True})
    previous=[]
    with (ROOT/'runs/.inference.lock').open('w')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        for role in ['analyst','reviewer']:
            result=lab.generate('advertising',lab.COMMON+'\nYour role: '+lab.ROLES['game'][role],json.dumps({'task':task,'evidence':evidence,'previous_drafts':previous}),768)
            result['word_count']=len(result['text'].split());save(out/(role+'.json'),result)
            with (out/'prompts-and-responses.txt').open('a')as stream:stream.write(role.upper()+'\nREQUEST:\n'+json.dumps(result['request'],ensure_ascii=False,indent=2)+'\nRESPONSE:\n'+result['text']+'\n\n')
            previous.append({'role':role,'text':result['text'],'word_count':result['word_count']});print(role,result['seconds'],result['word_count'],flush=True)
    local={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'completed_pending_coordinator_review','directory':str(out),'roles':previous}
    save(out/'status.json',local);save(ROOT/'verification/biwn-inventory-local-review.json',local);print(out,flush=True)


if __name__=='__main__':main()
