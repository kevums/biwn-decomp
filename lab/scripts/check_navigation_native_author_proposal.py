"""Compile the unchanged local Author proposal, then compare original execution.
Only a single outer Markdown fence is removed; no semantic repair is allowed.
A first counterexample rejects adoption; it is not a full candidate matrix pass.
"""
import json, subprocess
from pathlib import Path
from datetime import datetime, timezone
import native_actor_navigation_engine_v2 as e
ROOT=e.ROOT; V=ROOT/'verification'; ND=e.ND

def main():
    proposal=json.loads((V/'navigation-native-Author-current.json').read_text())
    assert proposal['new_predictions']==1 and not proposal['gold_C_supplied']
    raw=Path(proposal['candidate']); original=raw.read_text(); text=original.strip()
    out=V/'navigation-native-Author-machine-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'); out.mkdir(parents=True)
    fenced=text.startswith('```c\n') and text.endswith('\n```')
    if fenced:text=text[5:-4]
    cleaned=out/'candidate-fence-removed.c'; cleaned.write_text(text+'\n')
    reference=ND/'actor-navigation-reference-v2.c'
    wrapper=out/'dispatch.c'
    wrapper.write_text('#define biwn_native_actor_navigation_body coordinator_navigation_body\n#include '+json.dumps(str(reference))+'\n#undef biwn_native_actor_navigation_body\n#include '+json.dumps(str(cleaned))+'\nvoid biwn_native_actor_navigation_body(uint32_t *r){if(r[17]==0x13f12u){biwn_native_actor_nav_left(r);return;}coordinator_navigation_body(r);}\n')
    state=dict(status='checking_local_navigation_Author',directory=str(out),raw_candidate=str(raw),formatting_only_fence_removed=fenced,semantic_repairs=0,adopted=False,new_predictions=0,proposal_predictions=1,independent_model_reviewer=False,compiler_pass=False,completed=0)
    def save():e.g.save(out/'protocol.json',state);e.g.save(V/'navigation-native-Author-machine-reviewed-current.json',state)
    run=subprocess.run(['make','-f',str(ND/'Makefile.actor-navigation'),'actor-navigation','BUILD='+str(out/'build'),'NAV_SOURCE='+str(wrapper)],capture_output=True,text=True);(out/'build.log').write_text(run.stdout+run.stderr)
    state['compiler_pass']=run.returncode==0
    inputs=[Path(__file__),raw,cleaned,wrapper,reference,ND/'actor-navigation-native.h',ND/'actor-navigation-shim.S',ND/'actor-navigation.ld',ND/'Makefile.actor-navigation',Path(e.__file__),Path(e.g.__file__),Path(e.g.navigation.__file__),ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'render-assets/biwn-inventory-baseline.bin',out/'build.log']
    native=None
    try:
        assert run.returncode==0,'Strict native compiler rejected proposal'
        binary=out/'build/actor-navigation.bin';elf=out/'build/actor-navigation.elf';payload=binary.read_bytes();inputs += [binary,elf]
        nm=subprocess.check_output([str(ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'-n',str(elf)],text=True);(out/'symbols.txt').write_text(nm);symbols={x[2]:int(x[0],16)for line in nm.splitlines()if len(x:=line.split())==3}
        rows=[c for c in e.vectors()if c['entry']==0x13f12];e.g.save(out/'fixtures.json',rows);state['planned']=len(rows);state['binary_bytes']=len(payload)
        snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();native=e.Native()
        for index,case in enumerate(rows):
            witness=dict(index=index,case=case)
            a=e.execute(snapshot,case,payload,symbols,False);an=e.replay(native,snapshot,case,payload,symbols,False,a)
            witness.update(original_trace=a['trace'],original_registers=a['registers'],original_native=an,original_native_replayed=True)
            try:b=e.execute(snapshot,case,payload,symbols,True)
            except Exception as error:
                witness.update(candidate_execution_error=repr(error));e.g.save(out/'counterexample.json',witness);inputs.append(out/'counterexample.json');raise AssertionError('Unchanged proposal failed guest execution on original-valid fixture')from error
            differences=[key for key in ['ram','registers','trace']if a[key]!=b[key]]
            if differences:
                witness.update(differences=differences,candidate_trace=b['trace'],candidate_registers=b['registers']);e.g.save(out/'counterexample.json',witness);inputs.append(out/'counterexample.json');raise AssertionError('Original/public-access counterexample rejects proposal')
            bn=e.replay(native,snapshot,case,payload,symbols,True,b)
            assert an==bn,'Native fullCPU/SR/banks counterexample'
            state['completed']=index+1
        state.update(status='terminal_local_navigation_Author_matrix_pass_pending_adoption')
    except Exception as error:state.update(status='terminal_local_navigation_Author_rejected',error=repr(error))
    finally:
        if native:native.close()
        state['source_sha256']={str(p):e.g.sha(p)for p in inputs};assert raw.read_text()==original
        state['scope']=__doc__;save();print(json.dumps({k:state[k]for k in ['status','compiler_pass','completed','adopted','directory']}))

if __name__=='__main__':main()
