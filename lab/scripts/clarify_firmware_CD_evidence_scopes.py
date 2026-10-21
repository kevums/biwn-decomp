"""Label earlier ROM-view1 DSP proof separately from current view5 diagnostic."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];RUNTIME=Path.home()/'.lmstudio/local-ai-lab'
save=lambda p,v:p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')

def main():
    pointer=ROOT/'verification/firmware-CD-diagnostic-review.json';review=json.loads(pointer.read_text());out=Path(review['directory']);compact=review['evidence']
    save(out/'compact-evidence-before-scope-clarification.json',compact)
    keys=['firmware_DSP_instructions','firmware_DSP_instruction_coverage','firmware_DSP_checkpoints','firmware_DSP_success_word','firmware_DSP_C','original_DSP_instructions_on_C_path','initial_DSP_boundary_hostloaded','DSP_equivalence_bytes','DSP_pipeline_tail_excluded_bytes']
    earlier={key:compact.pop(key)for key in keys if key in compact}
    compact['historical_unchanged_ROM_view1_DSP_proof']=dict(scope='Earlier, separate, original ROM-view1 success path. These counts/outcome DO NOT describe the current ROM-view5 diagnostic.',**earlier)
    responsibilities=compact['processor_responsibilities'];responsibilities.pop('C_DSP',None)
    responsibilities['historical_C_DSP_ROM_view1']='Earlier unchanged-ROM input1:462 reached instructions/10,460,888 executions; source result03D0DEAD. These numbers must not be applied to diagnostic input5.'
    compact['DSP_proof_scope_comparison']=[dict(scope='CURRENT_DIAGNOSTIC_ROM_VIEW5',C_observed_source_instructions=447,C_executed_instructions=10460873,source_result='0x12345678',result_meaning='Source ROM-check failure routes CPU to CD initialization; not authentication success.',hardware_ROM_view_verified=False),dict(scope='HISTORICAL_UNCHANGED_ROM_VIEW1',C_observed_source_instructions=462,C_executed_instructions=10460888,source_result='0x03d0dead',result_meaning='Earlier original-ROM success path leading to the BIOS loop; separate comparison.')]
    compact['current_DSP_numbers_answer']='For the latest diagnostic use447 reached source instructions and10,460,873 executions, result12345678. The older462/10,460,888/03D0DEAD numbers belong only to unchanged-ROM view1. The secondDSP140,371-instruction TOC run is original DSP execution, not C.'
    review['evidence']=compact;review['native_Chat_first_answer_review']=dict(status='scope_numbers_conflated',current_scope_expected=[447,10460873,'0x12345678'],response_used=[462,10460888,'0x12345678'],other_limits_correct=True,source='native-chat-before-scope-clarification.md',action='Preserve response, separate historical/current evidence labels and retest in the same native Chat; no weight training.')
    save(out/'compact-evidence.json',compact);save(out/'review.json',review);save(pointer,review)
    for base in [ROOT,RUNTIME]:
        session=Path(json.loads((base/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);p=session/'emulator-runtime/summary.json';data=json.loads(p.read_text());data['firmware_bootstrap_DSP_progress']=compact;save(p,data)
    print('Updated scope labels in root and installed evidence; historical proof and Chat responses preserved.')

if __name__=='__main__':main()
