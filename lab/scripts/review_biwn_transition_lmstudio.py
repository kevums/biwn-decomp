"""Two fresh local contexts review the captured transition, with full logs."""
import fcntl
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import lab

def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    trace=json.loads((session/'emulator-runtime/gpu-transition-current.json').read_text())
    source=Path(trace['directory'])
    import csv
    with (source/'gpu-register-banks.csv').open() as f:banks=list(csv.DictReader(f))
    with (source/'events.csv').open() as f:events=[r for r in csv.DictReader(f) if int(r['type']) in (3,4,12)]
    handler=json.loads((source/'GPUhandler-decode.json').read_text())
    evidence={'trace_report':trace,'gpu_register_banks':banks,'watched_writes_and_go_stop':events,
              'handler_decode':{**handler,'instructions':[i for i in handler['instructions'] if i['address']<0xf03156]},
              'source_interpretation':'Pinned GPUHandleIRQs selects bank0, decrements r31 by4, stores interrupted PC-2 at r31 aligned down, then vectors to F03000+16*interrupt. This describes emulator source, not proven hardware behavior.',
              'scope':'No complete GPU instruction trace. Last1024GPU-PC histories inframe438 and439 contain odd PCs C1..D9, even though final438sample isF03010. Watches do not cover GPU local stores. All900frameCPU/GPU/DSPPCs equal prior run; no guest state or core changes.'}
    task='''In under180words, propose the most discriminating next diagnostic for the assisted BIOS boot failure.
State observed facts separately from a hypothesis. CPU writes G_PC=F03200 and GO=1, so do not blame a missing start write.
The stopped GPU bank0 r31 is zero at frame437; the BIOS-installed handler saves registers on r31 and loads its return from that stack.
Consider one explicitly experimental in-memory initialization of bank0 r31 to an unused GPU-RAM stack top before startup.
Do not call this a hardware fix, original-game bug or proven root cause. Specify an untouched baseline, exact changed state,
frame-address comparisons, visual/audio checks and what a positive/negative result would and would not establish.
You have not run that experiment. Do not suggest rewriting the ROM or broad core changes.'''
    out=ROOT/'runs'/f'{lab.stamp()}-game-transition-review';out.mkdir()
    (out/'protocol.json').write_text(json.dumps({'source':str(source),'task':task,'evidence':evidence,
        'local_model':lab.CONFIG['models']['advertising'],'roles':['analyst','reviewer'],'fresh_contexts':True,
        'same_weights_correlated_errors':True,'native_chat_history':False},indent=2)+'\n')
    results=[]
    with (ROOT/'runs/.inference.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        for role in ['analyst','reviewer']:
            system=lab.COMMON+'\nYour role: '+lab.ROLES['game'][role]
            user=json.dumps({'user_task':task,'source_evidence':evidence,'other_agent_drafts':results},ensure_ascii=False)
            result=lab.generate('advertising',system,user,640)
            result.update(role=role,word_count=len(result['text'].split()))
            (out/f'{role}.json').write_text(json.dumps(result,indent=2)+'\n')
            with (out/'prompts-and-responses.txt').open('a') as f:f.write(role.upper()+'\nREQUEST:\n'+json.dumps(result['request'],ensure_ascii=False,indent=2)+'\nRESPONSE:\n'+result['text']+'\n\n')
            results.append({'role':role,'text':result['text'],'quality_flags':result['quality_flags']})
            print(role,result['seconds'],'seconds',flush=True)
    status={'directory':str(out),'status':'completed_requires_coordinator_review','roles':results}
    (out/'status.json').write_text(json.dumps(status,indent=2)+'\n')
    (ROOT/'verification/biwn-transition-local-review.json').write_text(json.dumps(status,indent=2)+'\n')
    print(out,flush=True)
if __name__=='__main__':main()
