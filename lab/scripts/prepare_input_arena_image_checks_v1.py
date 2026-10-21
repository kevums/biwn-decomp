"""Isolate actual v39 checks from frozen v34/v37 evidence and pinned CPU maps."""
from datetime import datetime,timezone
from pathlib import Path
import prepare_record_stride_image_checks_v1 as prior
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha


def main():
    scripts=ROOT/'scripts'
    old_names={name.replace('record_strides','record_loop_image')for name in set(prior.MODULES.values())|{'check_native_record_strides_final_v1'}}
    mapping={name:name.replace('record_loop_image','input_arena_image')for name in old_names}
    bp=V/'native-input-arena-disc-build-v1-current.json';b=read(bp)
    assert b['profile']=='native-input-resource-arena-v39-experimental'and b['shared_Deck_code_bytes']==54134
    out=V/'input-arena-image-check-preparation-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    created=[]
    for old,new in sorted(mapping.items()):
        source=scripts/(old+'.py');text=source.read_text()
        for a,z in sorted(mapping.items(),key=lambda row:-len(row[0])):text=text.replace(a,z)
        text=text.replace('record-loop-image','input-arena-image').replace('native-input-arena-image-disc-build-v1-current.json','native-input-arena-disc-build-v1-current.json')
        text=text.replace('deck-shared-v37-record-loop-advance-v2','deck-shared-v34-record-strides-v1').replace('54060','54134').replace('terminal_v37_','terminal_v39_').replace('five-build','shared-build')
        text=text.replace('coordinator-record-loop-advance-v2','geometry-records-strides-v1').replace('geometry-input-arena-image-host-v1-current.json','geometry-record-strides-host-v1-current.json')
        assert 'input-arena-image-fullCPU-generation'not in text
        if old=='check_native_record_loop_image_final_v1':
            a=text.index("    t=(ROOT/'scripts/check_native_deck_shared_startup_heap_v4.py')")
            z=text.index("    t=(ROOT/'scripts/check_native_deck_shared_capacity_v4.py')",a)
            text=text[:a]+'''    # Reuse the already terminal actual-v39 dual-core wide startup/heap
    # proof; the legacy word-copy startup fixture is inapplicable here.
    t="from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha\\nfrom pathlib import Path\\np=V/'native-input-arena-image-startup-heap-v1-current.json';g=read(p)\\nassert g['native_startup_cases']==g['Unicorn_startup_cases']==6 and g['heap_initialize_cases']==192\\nfor f,h in g['source_sha256'].items():assert sha(f)==h,f\\ng=dict(g,reused_terminal_exact_v39_startup=True,source_sha256={**g['source_sha256'],str(p):sha(p),str(Path(__file__)):sha(__file__)})\\nsave(V/'native-Deck-input-arena-image-startup-heap-v1-current.json',g)\\nprint('Reused terminal exact-v39 wide startup/heap proof')\\n"
    (out/'startup.py').write_text(t);scripts['startup.py']=out/'startup.py'
'''+text[z:]
            text=text.replace("except BaseException as e:state.update(status='terminal_deeper_candidate_final_gate_failed',error=repr(e));mark();raise", "except subprocess.TimeoutExpired as e:state.update(status='observation_timeout_children_may_be_live',error=repr(e));mark();raise\n    except BaseException as e:state.update(status='terminal_deeper_candidate_final_gate_failed',error=repr(e));mark();raise")
        if old=='check_record_loop_image_final_copied_rebuild_v1':
            text='''"""Bind prior exact-v39 copied shared-piece rebuild to this final bridge payload."""
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
from publish_geometry_records_progress_v1 import clone
def main():
 gp=V/'scene17-input-arena-image-final-bridge-v1-current.json';g=read(gp)
 cp=V/'input-arena-image-copied-rebuild-v1-current.json';c=read(cp)
 for proof in [g,c]:
  for p,h in proof['source_sha256'].items():assert sha(p)==h,p
 piece=next(p for p in c['pieces']if p['piece']=='shared');assert piece['bytes']==54134 and piece['identical']
 assert Path(piece['copied_binary']).read_bytes()==Path(g['payload']).read_bytes()
 out=V/'input-arena-image-final-copied-rebuild-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 blob=out/'checked-copied-shared.bin';clone(Path(piece['copied_binary']),blob)
 state=dict(status='terminal_copied_shared_final_bridge_bytes_match_prior_exact_v39_rebuild',directory=str(out),payload=str(blob),bytes=54134,same_as_selected_prototype_module=True,reused_terminal_new_piece_proof=True,new_compilation=False,new_predictions=0,new_training=False,final_disc_integrated=True,final_disc_gameplay_verified=False,source_sha256={str(p):sha(p)for p in [Path(__file__),gp,cp,blob]})
 save(out/'protocol.json',state);save(V/'input-arena-image-final-copied-rebuild-v1-current.json',state);print(state['status'])
if __name__=='__main__':main()
'''
        compile(text,str(scripts/(new+'.py')),'exec');target=scripts/(new+'.py');assert not target.exists(),target;target.write_text(text);created.extend([source,target])
    proof=dict(status='terminal_isolated_v39_image_checks_prepared',directory=str(out),build=str(bp),modules=mapping,pinned_maps_unchanged=True,prior_startup_and_copied_proofs_reused=True,new_predictions=0,optimizer_updates=0,source_sha256={str(p):sha(p)for p in [Path(__file__),bp,*created]})
    save(out/'protocol.json',proof);save(V/'input-arena-image-check-preparation-v1-current.json',proof);print('Prepared',len(mapping),'isolated v39 modules.',flush=True)


if __name__=='__main__':main()
