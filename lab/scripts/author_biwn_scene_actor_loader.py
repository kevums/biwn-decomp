"""Local roles recover the complete 20AA0 body from frozen disassembly."""
import fcntl
import hashlib
import json
import re
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import lab
from run_local_portal_author_test import ensure_game_model

def main():
    ensure_game_model()
    source=ROOT/'projects/black-ice-white-noise/restoration'
    inventory=json.loads((ROOT/'verification/main-CPU-route-coverage-current.json').read_text())
    listing=Path(inventory['static_manifest']).parent/'listing.asm'
    text=listing.read_text()
    assert hashlib.sha256(text.encode()).hexdigest()==inventory['static_listing_sha256']
    assembly='\n'.join(line for line in text.splitlines() if re.match(r'^[0-9a-fA-F]{8}:',line)
                      and 0x20aa0<=int(line[:8],16)<0x20b2a)
    contract='''Recover the COMPLETE 68000 scene actor-loading function20AA0 from
the supplied original disassembly as readable C99. Use #include "biwn_scene_loading.h".
Implement its declared biwn_scene_loading signature, supporting ONLY entry0x20AA0;
return BAD_ARGUMENT for other entries. Unused argument0/1/2 need explicit void casts.
Preserve full D0 through word operations, ext.l and logical helper callbacks.
All externally visible bus reads/writes, their widths/order and rereads must match.
Helpers: 13AE0 receives five logical args: type(word zero-extended), X(long),
Y(word zero-extended), Z(long), extra(word zero-extended); callback receives pointer
to incoming D0 and writes returned D0. Signed16 coordinate extensions use unsigned
bit math, never implementation-defined casts. Signed16 loop comparisons are real.
Do not cache mutable global count or mode reads across original accesses.
Require nonnull bus/out_D0 and read16/read32/write16/write32/call upfront, even
callbacks unused in this entry. Do not require read8. No side effects on bad args.
Return BUS_ERROR on failed bus callbacks, DEPENDENCY_ERROR on failed helper.
Work budget: consume one unit before each outer iteration AND each positive inner
iteration; exhausted budget returns WORK_LIMIT. Host errors leave out_D0 unchanged
but retain prior bus/helper effects. Success writes full final D0 and returns OK.
No IO, allocation, assembly, direct guest pointers or library calls. Static pure
integer helpers allowed. No other exported functions. Do not claim tests ran.
Return JSON only: source(string), limitations(string).'''
    out=ROOT/'runs'/(lab.stamp()+'-local-scene-actor-loader');out.mkdir()
    evidence=dict(contract=contract,assembly=assembly,
                  headers={n:(source/n).read_text()for n in ['biwn_scene_loading.h','biwn_world_update.h']})
    (out/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    protocol=dict(status='authoring',directory=str(out),roles=['local Code Author','local Source Reviewer'],
                  same_weights_correlated=True,new_training=False,native_Chat_verified=False,
                  original_disassembly_SHA256=hashlib.sha256(assembly.encode()).hexdigest())
    (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');print(out,flush=True)
    drafts=[]
    with (ROOT/'runs/.inference.lock').open('w')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        for role in ['author','reviewer']:
            system=lab.COMMON+'\n'+('Recover the supplied complete function as readable C.'if role=='author'else
                    'Audit the draft line by line against original assembly and every host contract. Correct any issue and return complete C source.')
            result=lab.generate('game',system,json.dumps(dict(evidence=evidence,prior=drafts)),2400)
            (out/(role+'.json')).write_text(json.dumps(result,indent=2)+'\n')
            with (out/'prompts-and-responses.txt').open('a')as f:
                f.write(role.upper()+'\nREQUEST\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE\n'+result['text']+'\n\n')
            drafts.append(dict(role=role,text=result['text'],seconds=result['seconds'],quality_flags=result['quality_flags']))
            print(role,result['seconds'],result['quality_flags'],flush=True)
    proposed=lab.parse_object(drafts[-1]['text']);(out/'biwn_local_scene_actor_loader.c').write_text(proposed['source']+'\n')
    protocol.update(status='proposed_source_pending_checks',drafts=drafts)
    (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    (ROOT/'verification/local-scene-actor-author-current.json').write_text(json.dumps(protocol,indent=2)+'\n')

if __name__=='__main__':main()
