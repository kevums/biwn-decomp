"""Preserve two actual local development attempts and distinguish static rejection from tests."""
from datetime import datetime, timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha,atomic

def main():
    out=V/'local-scene-gpu-family-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    roles=[]; dependencies={str(Path(__file__)):sha(__file__)}; transcripts=[]
    for version,role in [(1,'Author'),(2,'Repair')]:
        pointer=V/f'local-gpu-command-family-v{version}-current.json'
        protocol=read(pointer);folder=Path(protocol['directory']);attempt=folder/role
        assert protocol['new_predictions']==1 and protocol['model_source_installed'] is False
        inference=read(attempt/'inference.json');response=(attempt/'response.txt').read_text()
        assert response==inference['text']
        row=dict(role=role,source_directory=str(folder),seconds=inference['seconds'],
                 model=protocol['model_identifier'],status=protocol['status'],
                 begin_occurrences=response.count('SCENE_GPU_BEGIN('),end_occurrences=response.count('SCENE_GPU_END('),
                 complete_outer_code_fence=response.rstrip().endswith('```'),compiled=False,
                 semantic_verifier_executed=False,accepted=False,unedited_raw_response=True)
        assert row['begin_occurrences']>1 and row['end_occurrences']>1
        row['manual_findings']=[
            'Multiple lexical begin/end markers violate the explicit one-occurrence constraint.',
            'Acknowledgement-loop conditions test the carry mask0x1; BEQ requires the zero mask0x4.',
            'Final E098 calls pass the JSR instruction address instead of its post-JSR return address.',
            'Projection ADD ignores the arithmetic return value, leaving D0 and the next mailbox pointer unchanged.'
        ]
        if role=='Author':
            assert not row['complete_outer_code_fence']
            row['manual_findings'].insert(0,'Output ends mid-function near its2600token cap. The raw signature is correct; the coarse parser could not extract an incomplete fence.')
        else: assert row['complete_outer_code_fence']
        roles.append(row)
        transcripts.append(f'\n{role} — actual local development inference; rejected, no training or source adoption\n'+(folder/'prompts-and-responses.txt').read_text())
        for p in [pointer,*folder.rglob('*')]:
            if p.is_file(): dependencies[str(p)]=sha(p)
    limitations=[
        'Same copied27B model ran both roles; Repair is feedback continuation, not independent review.',
        'Repair feedback used ambiguous bit-number shorthand for carry and zero. Future prompts should use explicit masks0x1 and0x4.',
        'The primitive description did not explicitly state that deck_alu returns the arithmetic result for assignment. Clarify this before treating the ADD error as an independent capability result.',
        'Static issues were inspected after source rejection. No compiled semantic counterexample exists for these responses.',
        'The selected and verified source is coordinator-authored, not model-authored. These development attempts are not held-out evaluations or useful training gains.'
    ]
    state=dict(status='terminal_two_local_gpu_family_attempts_rejected_and_preserved',directory=str(out),roles=roles,
               actual_predictions=2,new_predictions=0,recovered_completed_predictions=2,new_training=False,
               optimizer_updates=0,model_source_installed=False,native_Chat_verified=False,
               selected_source_authorship='Coordinator',prompt_and_interpretation_limits=limitations,
               whole_game_complete=False)
    save(out/'facts.json',state)
    (out/'prompts-and-responses.txt').write_text('BIWN GPU CPU command family — exact local prompts and raw outputs\n\n'+ '\n'.join(limitations)+'\n'+''.join(transcripts))
    dependencies.update({str(p):sha(p)for p in out.rglob('*')if p.is_file()})
    state['dependencies_sha256']=dependencies
    atomic(V/'local-scene-gpu-family-reviewed-v1-current.json',state)
    print(state['status'],out,flush=True)

if __name__=='__main__':main()
