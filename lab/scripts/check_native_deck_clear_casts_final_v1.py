"""Exact candidate-address module/startup/heap gates; new nesting/freshness pending."""
import json,hashlib,os,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    bp=V/'native-Deck-clear-casts-disc-build-v1-current.json';b=read(bp)
    for p,h in b['source_sha256'].items():assert sha(p)==h,p
    out=V/'native-Deck-clear-casts-final-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    save(out/'build-as-run.json',b)
    state=dict(status='preparing',pid=os.getpid(),directory=str(out),build=str(bp),build_sha256=sha(bp),results={},whole_game_complete=False,new_training=False,fresh_gameplay_verified=False,new_outer_connected_matrix_verified=False)
    def mark():save(out/'protocol.json',state);save(V/'native-Deck-clear-casts-final-v1-current.json',state)
    mark();scripts={}
    def native_module(name,source,oldstem,newstem):
        text=(ROOT/'scripts'/source).read_text()
        anchor='CODE=0x180000;ARENA=0x160000;';assert text.count(anchor)==1
        text=text.replace(anchor,'CODE='+hex(b['shared_Deck_code_address'])+';ARENA='+hex(b['deck_arena_address'])+';').replace(oldstem,newstem)
        anchor="payload=(build/'native-shared.bin').read_bytes();syms=";assert text.count(anchor)==1
        text=text.replace(anchor,"payload=(build/'native-shared.bin').read_bytes();resident=Path("+repr(b['component'])+").read_bytes();assert payload==resident[CODE-"+str(b['resident_address'])+":CODE-"+str(b['resident_address'])+"+len(payload)],'Deployed module bytes differ';syms=")
        p=out/name;text=text.replace("private_stack_lower=832,","private_stack_lower=832,deployed_module_byte_identity=True,")
        p.write_text(text);scripts[name]=p
    native_module('geometry.py','check_native_deck_clear_casts_v1.py','native-Deck-clear-casts-v1','native-Deck-clear-casts-final-geometry-v1')
    native_module('retained.py','check_native_deck_retained_clear_casts_v1.py','native-deck-retained-clear-casts-v1','native-deck-retained-clear-casts-final-v1')
    # Importable name so the fallback checker uses exactly the final constants.
    (out/'native_retained_final_checker.py').write_bytes(scripts['retained.py'].read_bytes())
    t=(ROOT/'scripts/check_shared_deck_fallback_clear_casts_v1.py').read_text().replace('import check_native_deck_retained_clear_casts_v1 as m','import native_retained_final_checker as m')
    t=t.replace('native-deck-retained-clear-casts-v1-current.json','native-deck-retained-clear-casts-final-v1-current.json').replace('native-Deck-clear-casts-v1-current.json','native-Deck-clear-casts-final-geometry-v1-current.json').replace('shared-Deck-fallback-clear-casts-v1','shared-Deck-fallback-clear-casts-final-v1')
    (out/'fallback.py').write_text(t);scripts['fallback.py']=out/'fallback.py'
    t=(ROOT/'scripts/check_native_deck_shared_startup_heap_v4.py').read_text().replace('native-Deck-shared-disc-build-v4-current.json','native-Deck-clear-casts-disc-build-v1-current.json')
    old="assert b['component_cases']==5248 and b['nested_cases']>=128 and b['deck_arena_bytes']==103424";assert t.count(old)==1
    t=t.replace(old,"assert b['deck_arena_bytes']==103424 and b['outer_arena_bytes']==58176")
    t=t.replace("b['deck_arena_bytes']//2)+32*101+512","b['deck_arena_bytes']//2+b['outer_arena_bytes']//2)+48*101+512").replace('native-Deck-shared-startup-heap-v4','native-Deck-clear-casts-startup-heap-v1')
    (out/'startup.py').write_text(t);scripts['startup.py']=out/'startup.py'
    t=(ROOT/'scripts/check_native_deck_shared_capacity_v4.py').read_text().replace('native-Deck-shared-disc-build-v4-current.json','native-Deck-clear-casts-disc-build-v1-current.json').replace('native-Deck-shared-capacity-v4','native-Deck-clear-casts-capacity-v1')
    (out/'capacity.py').write_text(t);scripts['capacity.py']=out/'capacity.py'
    # The unchanged outer algorithm still needs its own relocated machine-code
    # checks; its previous five-body connected proof does not cover this image.
    t=(ROOT/'scripts/check_native_deck_outer_v1.py').read_text();old='CODE=0x180000;ARENA=0x130000;DECK=0x160000;';assert t.count(old)==1
    t=t.replace(old,'CODE='+hex(b['outer_code_address'])+';ARENA='+hex(b['outer_arena_address'])+';DECK='+hex(b['deck_arena_address'])+';').replace('native-Deck-outer-v1','native-Deck-outer-clear-casts-final-v1')
    anchor="payload=(build/'native-outer.bin').read_bytes();syms=";assert t.count(anchor)==1
    t=t.replace(anchor,"payload=(build/'native-outer.bin').read_bytes();resident=Path("+repr(b['component'])+").read_bytes();assert payload==resident[CODE-"+str(b['resident_address'])+":CODE-"+str(b['resident_address'])+"+len(payload)],'Outer deployed bytes differ';syms=")
    (out/'native_outer_final_checker.py').write_text(t);scripts['outer.py']=out/'native_outer_final_checker.py'
    for kind in ['fallback','waits']:
        t=(ROOT/f'scripts/check_native_deck_outer_{kind}_v1.py').read_text().replace('import check_native_deck_outer_v1 as outer','import native_outer_final_checker as outer')
        t=t.replace('native-Deck-outer-v1-current.json','native-Deck-outer-clear-casts-final-v1-current.json').replace('native-Deck-outer-'+kind+'-v1','native-Deck-outer-'+kind+'-debug-final-v1')
        (out/(kind+'-outer.py')).write_text(t);scripts[kind+'-outer.py']=out/(kind+'-outer.py')
    def launch(name):
        stream=(out/(name+'.log')).open('w');p=subprocess.Popen([str(ROOT/'.venv/bin/python3.12'),str(scripts[name])],stdout=stream,stderr=subprocess.STDOUT,cwd='/',env={**os.environ,'PYTHONPATH':str(out)+os.pathsep+str(ROOT/'scripts')})
        return p,stream
    def finish(name,pair):
        child,stream=pair;code=child.wait(timeout=900);stream.close();state['results'][name]=dict(exit_code=code,log=str(out/(name+'.log')));mark()
        assert code==0,(name,(out/(name+'.log')).read_text()[-5000:]);print(name,'passed',flush=True)
    try:
        state.update(status='checking',child_pids={});mark()
        # Independent final geometry, retained-caller and startup checks run in
        # separate emulator processes. Dependent fallback/outer checks follow.
        group={name:launch(name)for name in ['geometry.py','retained.py','startup.py']};state['child_pids']={name:pair[0].pid for name,pair in group.items()};mark()
        for name,pair in group.items():finish(name,pair)
        state['child_pids']={};mark()
        for name in ['fallback.py','capacity.py','outer.py','fallback-outer.py','waits-outer.py']:
            pair=launch(name);state['child_pids']={name:pair[0].pid};mark();finish(name,pair);state['child_pids']={};mark()
        names=['native-Deck-clear-casts-final-geometry-v1-current.json','native-deck-retained-clear-casts-final-v1-current.json','shared-Deck-fallback-clear-casts-final-v1-current.json','native-Deck-clear-casts-startup-heap-v1-current.json','native-Deck-clear-casts-capacity-v1-current.json','native-Deck-outer-clear-casts-final-v1-current.json','native-Deck-outer-fallback-clear-casts-final-v1-current.json','native-Deck-outer-waits-clear-casts-final-v1-current.json']
        proofs=[V/n for n in names]
        state.update(status='terminal_deeper_candidate_final_component_startup_heap_gates_pass',source_sha256={str(p):sha(p)for p in [Path(__file__),bp,*scripts.values(),out/'native_retained_final_checker.py',*proofs]},scope=__doc__+' Exact image bytes checked for both modules; geometry256,retained4992,fallback1280,startup6,heap192,capacity36,outer1280,fallback384,wait192pairs. New alias/nested six-caller integration,real helper suspension,resource peaks and fresh gameplay remain pending. No preview promotion.')
        mark();print(state['status'],flush=True)
    except BaseException as e:state.update(status='terminal_deeper_candidate_final_gate_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
