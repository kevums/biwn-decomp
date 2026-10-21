"""Accept prior exact deletion response after reviewing its combined-edit shape."""
import json,re
from pathlib import Path
from check_biwn_native_button_digit import ROOT,sha,save

def main():
    out=ROOT/'runs/local-native-controller-cleanup-20261018T045557.742237Z';state=json.loads((out/'protocol.json').read_text());response=json.loads((out/'response.json').read_text());edits=json.loads(response['text'])['edits'];parent=Path(state['parent_source']);assert sha(parent)==state['parent_source_sha256']
    source=parent.read_text();expected=re.sub(r'(?m)^static uint32_t (?:ror32|rol32)\([^\n]*\n','',source)
    for edit in edits:
        assert edit['new']=='' and source.count(edit['old'])==1
        assert len(re.findall(r'static uint32_t (?:ror32|rol32)\(',edit['old'])) in [1,2]
        source=source.replace(edit['old'],'')
    assert expected.split()==source.split(),'Only two helper definitions and adjacent blank lines may be deleted'
    candidate=out/'controller-native.c';candidate.write_text(source)
    state.update(status='terminal_model_literal_cleanup_pending_CPU_gates',candidate=str(candidate),candidate_sha256=sha(candidate),seconds=response['seconds'],edits=edits,coordinator_manually_edited_C=False,host_parser_correction='First host parser required two edits. Existing model response correctly grouped both contiguous helper deletions in one exact edit. Accepted without another generation after token-level comparison to only those deletions.',source_derivation='Local Author C plus one exact local Repairer edit deleting the two unused helper definitions; host literal matcher applied it. Coordinator supplied algorithm, ABI and cleanup diagnosis.',acceptance_script=str(Path(__file__)),acceptance_script_sha256=sha(__file__))
    (out/'prompts-and-responses.txt').write_text('SYSTEM\n'+state['system']+'\nUSER\n'+state['user']+'\nRESPONSE\n'+response['text']+'\n')
    save(out/'protocol.json',state);save(ROOT/'verification/local-native-controller-cleanup-current.json',state);print(state['status'],response['seconds'])
if __name__=='__main__':main()
