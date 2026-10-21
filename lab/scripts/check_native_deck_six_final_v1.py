"""Finite final-address gates for both modules, startup and heap.

Generated isolated checkers retain their exact as-run sources. No prototype
pointer, accepted five-caller disc, or desktop app is overwritten.
"""
import json,os,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def sha(p):
    with Path(p).open('rb')as f:return __import__('hashlib').file_digest(f,'sha256').hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')


def main():
    bp=V/'native-Deck-six-disc-build-v1-current.json';b=read(bp)
    for p,h in b['source_sha256'].items():assert sha(p)==h,p
    out=V/'native-Deck-six-final-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    save(out/'build-as-tested.json',b)
    state=dict(status='preparing',pid=os.getpid(),directory=str(out),build=str(bp),build_sha256=sha(bp),whole_game_complete=False,new_training=False,results={})
    def mark():save(out/'protocol.json',state);save(V/'native-Deck-six-final-v1-current.json',state)
    mark()
    text=(ROOT/'scripts/check_native_deck_outer_v1.py').read_text()
    old='CODE=0x180000;ARENA=0x130000;DECK=0x160000;'
    new='CODE='+hex(b['outer_code_address'])+';ARENA='+hex(b['outer_arena_address'])+';DECK='+hex(b['deck_arena_address'])+';'
    assert text.count(old)==1;text=text.replace(old,new).replace('native-Deck-outer-v1','native-Deck-outer-final-v1')
    anchor="payload=(build/'native-outer.bin').read_bytes();syms="
    assert text.count(anchor)==1
    verification="payload=(build/'native-outer.bin').read_bytes(); resident=Path("+repr(b['component'])+").read_bytes(); assert payload==resident[CODE-"+str(b['resident_address'])+":CODE-"+str(b['resident_address'])+"+len(payload)],'Outer deployed bytes differ';syms="
    text=text.replace(anchor,verification);(out/'native_outer_final_checker.py').write_text(text)
    scripts={'outer':out/'native_outer_final_checker.py'}
    for kind in ['fallback','waits','connected']:
        text=(ROOT/f'scripts/check_native_deck_outer_{kind}_v1.py').read_text().replace('import check_native_deck_outer_v1 as outer','import native_outer_final_checker as outer')
        text=text.replace('native-Deck-outer-v1-current.json','native-Deck-outer-final-v1-current.json').replace('native-Deck-outer-'+kind+'-v1','native-Deck-outer-'+kind+'-final-v1')
        if kind=='connected':
            text=text.replace('SHARED_CODE=0x190000','SHARED_CODE='+hex(b['shared_Deck_code_address']))
            anchor="assert len(spayload)==sg['code_bytes']"
            assert text.count(anchor)==1
            more=anchor+"; resident=Path("+repr(b['component'])+").read_bytes(); assert spayload==resident[SHARED_CODE-"+str(b['resident_address'])+":SHARED_CODE-"+str(b['resident_address'])+"+len(spayload)],'Five-caller deployed bytes differ'"
            text=text.replace(anchor,more)
        p=out/(kind+'.py');p.write_text(text);scripts[kind]=p
    text=(ROOT/'scripts/check_native_deck_shared_final_v4.py').read_text().replace('native-Deck-shared-disc-build-v4-current.json','native-Deck-six-disc-build-v1-current.json').replace('native-deck-shared-final-v4-current.json','native-deck-shared-six-final-v1-current.json').replace("'shared-build/native-shared.bin'","'five-build/native-shared.bin'")
    p=out/'five.py';p.write_text(text);scripts['five']=p
    text=(ROOT/'scripts/check_native_deck_shared_startup_heap_v4.py').read_text().replace('native-Deck-shared-disc-build-v4-current.json','native-Deck-six-disc-build-v1-current.json').replace("assert b['component_cases']==5248 and b['nested_cases']>=128 and b['deck_arena_bytes']==103424","assert b['deck_arena_bytes']==103424 and b['outer_arena_bytes']==58176")
    text=text.replace('native-Deck-shared-startup-heap-v4','native-Deck-six-startup-heap-v1')
    text=text.replace("b['deck_arena_bytes']//2)+32*101+512","b['deck_arena_bytes']//2+b['outer_arena_bytes']//2)+48*101+512")
    p=out/'startup.py';p.write_text(text);scripts['startup']=p
    text=(ROOT/'scripts/check_native_deck_shared_capacity_v4.py').read_text().replace('native-Deck-shared-disc-build-v4-current.json','native-Deck-six-disc-build-v1-current.json').replace('native-Deck-shared-capacity-v4','native-Deck-six-capacity-v1')
    p=out/'capacity.py';p.write_text(text);scripts['capacity']=p
    try:
        for kind in ['outer','five','fallback','waits','connected','startup','capacity']:
            state.update(status='checking',current_gate=kind);mark()
            with(out/(kind+'.log')).open('w')as log:
                child=subprocess.Popen([str(ROOT/'.venv/bin/python3.12'),str(scripts[kind])],stdout=log,stderr=subprocess.STDOUT,cwd='/',env={**os.environ,'PYTHONPATH':str(out)+os.pathsep+str(ROOT/'scripts')})
                state['child_pid']=child.pid;mark();code=child.wait(timeout=600)
            state['child_pid']=None;state['results'][kind]=dict(exit_code=code,log=str(out/(kind+'.log')));mark()
            assert code==0,(out/(kind+'.log')).read_text()[-6000:]
            print(kind,'passed',flush=True)
        proofs=[V/p for p in ['native-Deck-outer-final-v1-current.json','native-deck-shared-six-final-v1-current.json','native-Deck-outer-fallback-final-v1-current.json','native-Deck-outer-waits-final-v1-current.json','native-Deck-outer-connected-final-v1-current.json','native-Deck-six-startup-heap-v1-current.json','native-Deck-six-capacity-v1-current.json']]
        state.update(status='terminal_six_caller_final_addresses_startup_and_heap_gates_pass',initial_heap_bytes=b['initial_heap_bytes'],
                     source_sha256={str(p):sha(p)for p in [Path(__file__),bp,*scripts.values(),*proofs]},
                     scope=__doc__+' Prototype and final modules are compiled from the same source and independently compared to originalCPU. Exact module bytes match the candidate image. Startup verifies all arena and pointer initialization bytes. This does not run fresh gameplay or a real yielding helper.')
        mark();print(state['status'],flush=True)
    except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise


if __name__=='__main__':main()
