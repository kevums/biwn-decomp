"""Publish 1142E recovery and five-helper native prototype with exact proof scopes."""
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    names=['deck-geometry-faces-v1-current.json','geometry-faces-fault-controls-v1-current.json',
           'deck-geometry-connected-faces-v3-current.json','native-Deck-faces-v1-current.json',
           'native-deck-retained-faces-v1-current.json','shared-Deck-fallback-faces-v1-current.json']
    proofs={n:read(V/n)for n in names}
    assert proofs[names[0]]['completed']==640
    assert len(proofs[names[1]]['negative_controls'])==4 and all(x['rejected']for x in proofs[names[1]]['negative_controls'])
    assert proofs[names[2]]['completed']==256
    native=proofs[names[3]];assert native['status']=='terminal_native_geometry_five_deeper_helpers_match'and native['completed']==256
    assert proofs[names[4]]['completed']==4992 and proofs[names[5]]['completed']==1280
    for p in proofs.values():
        for name,digest in p.get('source_sha256',{}).items():assert sha(name)==digest,name
    assert sha(native['payload'])==native['payload_sha256']==proofs[names[4]]['payload_sha256']
    prepared=read(V/'geometry-faces-reviewed-v1-prepared-current.json');out=Path(prepared['directory'])
    assert not(out/'publication.json').exists()
    for name,p in proofs.items():save(out/name,p)
    facts=dict(status='terminal_geometry_faces_host_and_native_prototype_reviewed',recovered_entry='0x1142E',
        recovered_extent='0x1142E..0x11762; stops at 0x11760 RTS',authorship='Codex coordinator structured C; not accepted local-model output',
        host_CPU_RAM_cases=640,host_instruction_locations=188,host_error_cases=330,host_GPU_fixture_calls=2073,
        deliberate_source_defects_rejected=4,connected_six_body_cases=256,
        standalone_object_text_bytes=6676,standalone_object_executed=False,
        native_geometry_cases=256,native_retained_cases=4992,native_fallback_cases=1280,
        native_module_bytes=native['code_bytes'],native_module_sha256=native['payload_sha256'],native_module=native['payload'],
        native_internal_helpers=['0x10968','0x10BA4','0x11384','0x110D4','0x1142E'],
        maximum_observed_C_stack_bytes=native['maximum_C_stack_bytes'],C_stack_partition_bytes=176,
        observed_C_stack_margin_bytes=176-native['maximum_C_stack_bytes'],private_arena_added=False,
        native_disc_qualified=False,new_fresh_gameplay_verified=False,installed_preview_changed=False,whole_game_complete=False,
        experimental_game_model_adopted=False,
        remaining_geometry_helper='0x10734 debug overlay; MMIO/blitter and formatted-text dependencies need device-aware recovery',
        scope='The complete face builder and geometry plus five helpers match finite original68000 CPU/RAM/ordered-entry checks. Native prototype executes compiled algorithms on68000. E26C GPU effects and10734debug overlay remain declared fixtures in these matrices. No final-address disc integration,nesting/fresh gameplay,asynchronous IRQ,timing,physical console or full-game rebuild claim.',
        next_action='Integrate the fifth internal helper into a separate final-address disc; retain all six public callers and qualify startup,capacity,outer waits,nesting and fresh original-geometry controls before preview promotion. Recover10734with device-aware effects;resolve existing fidelity differences.')
    candidate=read(V/'native-Deck-faces-disc-build-v1-current.json');save(out/'candidate-build.json',candidate)
    facts.update(separate_candidate_disc_built=True,candidate_disc=candidate['derived_disc'],candidate_disc_sha256=candidate['derived_disc_sha256'],candidate_initial_heap_bytes=candidate['initial_heap_bytes'],candidate_final_gates='native-Deck-faces-final-v1-current.json')
    report=ROOT/'reports/Five Geometry Helpers Source and Native Prototype Review.txt';facts['report']=str(report)
    report.write_text('BIWN — 1142E FACE BUILDER RECOVERY AND FIVE-HELPER NATIVE PROTOTYPE\n\n'
        'The complete 1142E..11762 face-record builder is recovered as structured coordinator C. It stops at original11760RTS; the wrapper consumes that return. This is coordinator-authored source, not a successful output from the local model pilot.\n\n'
        'Host comparison passes640CPU/RAM/ordered-GPU-entry cases, covering all188instruction locations,330host-error cases and2,073GPU fixture calls. Four compiled defects are rejected:logical signed averaging,stale post-GPU record counter,wrong X changes on address ADDQ,and wrong argument cleanup. Geometry plus the five recovered helpers passes256connected cases against all six original bodies.\n\n'
        'The monolithic standalone source compiles to a6,676byte M68000object with no undefined symbols. That object is compile-only. A separate linked native prototype stages the same algorithm around GPU calls and stages parent arithmetic before nested services. Its full256geometry cases execute the compiled code on68000, with fullCPU/banks,nonarenaRAM and ordered entry comparisons. The unchanged four retained callers pass4,992cases;invalid-task and busy fallback pass1,280cases with entireRAM/CPU equality.\n\n'
        'Early integration attempts failed the linker short-call range and the existing stack fences. Their failures are retained. The final prototype uses absolute body calls and direct native stack writes consistent with its existing volatile bus profile;large arithmetic C frames end before nested captures. No private arena was added. Maximum measured geometry C-stack use:'+str(native['maximum_C_stack_bytes'])+'of176bytes;observed remaining headroom:'+str(176-native['maximum_C_stack_bytes'])+'bytes. This is finite measured headroom,not an arbitrary interrupt/reentry guarantee.\n\n'
        'The new native module is '+str(native['code_bytes'])+'bytes. It has five internal compiled helpers inside geometry;their global original entries remain unpatched. A separate experimental disc has been built with the module;its final-address,startup and heap/capacity checks are running. It has not been promoted to the playable preview. New nesting and fresh-gameplay qualification remain required. Its first build receipt used the earlier four-helper filename;the new receipt is now separate,and the earlier receipt was restored byte-exact against its recorded SHA. The exact builder as run and receipt repair are archived;no disc rebuild was needed for the name correction. The installed BIWN Test Preview remains the previously reviewed six-caller build.\n\n'
        'E26C GPU and10734debug-overlay effects remain fixtures in these component comparisons. GPU device timing,debug blitter/MMIO and formatted text,arbitrary suspension/IRQ,audio/physical fidelity and full-game source rebuilding are incomplete. The earlier four-helper disc retains94differing video frames versus its control despite equal final video.\n\n'
        'Next:'+facts['next_action']+'\n')
    save(out/'facts.json',facts)
    paths=[Path(__file__),out/'facts.json',report,*[out/n for n in names],out/'geometry-faces.o',out/'geometry-faces.su',out/'compiler.log',out/'compile-command.json',out/'size.txt',out/'undefined-symbols.txt',out/'candidate-build.json']
    publication=dict(status=facts['status'],directory=str(out),facts=str(out/'facts.json'),report=str(report),
        dependencies_sha256={str(p):sha(p)for p in paths},whole_objective_complete=False,new_predictions=0,new_training=False)
    save(out/'publication.json',publication);save(V/'geometry-faces-recovery-reviewed-v1-current.json',publication)
    print(out,flush=True)
if __name__=='__main__':main()
