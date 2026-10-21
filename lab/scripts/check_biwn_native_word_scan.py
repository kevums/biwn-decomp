"""Current native CPU checks assembled fragment, continuation and edge behavior.
Not an equivalence claim between the buggy original and the repaired scan.
"""
from datetime import datetime,timezone
from pathlib import Path
import json,random
from check_biwn_native_button_digit import ROOT,sha,save
from check_biwn_scheduler import Native
BASE=0x1c0000;END=0x1c8000
STOPS={0x1b118:'marker_run_within_payload_bound',0x1b122:'scan_exhausted',0x1b08a:'retry_marker_run_past_payload_bound'}

def run(n,image,case,sr,regs):
    n.device.seed(bytes(image),0);l=n.lib;l.m68k_pulse_reset();l.m68k_set_irq(0)
    l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,0x1e0000);l.m68k_set_reg(17,0);l.m68k_set_reg(15,0x180000);l.m68k_set_reg(17,sr)
    for i,v in enumerate(regs):l.m68k_set_reg(i,v)
    l.m68k_set_reg(2,0x12345678);l.m68k_set_reg(10,BASE+case['start']);l.m68k_set_reg(16,0x1b0ee);pcs=[];reads=[];cycles=0
    for _ in range(1000):
        pc=l.m68k_get_reg(None,16)
        if pc in STOPS:break
        assert 0x1b0ee<=pc<0x1b118,hex(pc)
        pcs.append(pc)
        if image[pc:pc+2]==bytes.fromhex('b49a'):reads.append(l.m68k_get_reg(None,10))
        cycles+=l.m68k_execute(1)
    else:raise AssertionError('Bounded fixture did not reach scan/run continuation')
    cpu=dict(regs=[l.m68k_get_reg(None,i)for i in range(16)],PC=pc,SR=l.m68k_get_reg(None,17));cpu['usp']=n.prefix[16]if sr&0x2000 else cpu['regs'][15];cpu['ssp']=cpu['regs'][15]if sr&0x2000 else n.prefix[17]
    assert n.device.ram()==bytes(image),'Scan/continuation modifiedRAM before declared stop'
    return dict(CPU=cpu,classification=STOPS[pc],cycles=cycles,PCs=pcs,CMP_long_read_addresses=reads,input_window_overread_addresses=[a for a in reads if a<BASE or a+4>END])

def main():
    bp=ROOT/'verification/native-word-scan-build-current.json';build=json.loads(bp.read_text());assert build['status']=='terminal_source_assembled_marker_CDIs_pending_native_checks'
    payload=Path(build['binary']).read_bytes();assert sha(build['binary'])==build['binary_sha256'] and payload.hex()==build['repaired_fragment']
    out=ROOT/'verification/native-word-scan'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    atlas=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();original=bytes.fromhex(build['original_fragment']);legacy=bytes.fromhex(json.loads(Path(build['legacy_overlay']).read_text())['patches'][0]['replacement']);assert payload==legacy
    cases=[dict(name='phase0',start=0x7fa0,marker=0x7fa0,count=16,expect='marker_run_within_payload_bound'),dict(name='phase2',start=0x7fa0,marker=0x7fa2,count=16,expect='marker_run_within_payload_bound'),dict(name='phase4',start=0x7fa0,marker=0x7fa4,count=16,expect='marker_run_within_payload_bound'),dict(name='phase6',start=0x7fa0,marker=0x7fa6,count=16,expect='marker_run_within_payload_bound'),dict(name='exact_end',start=0x7fc0,marker=0x7fc0,count=16,expect='marker_run_within_payload_bound'),dict(name='run_past_end',start=0x7fc0,marker=0x7fc2,count=16,expect='retry_marker_run_past_payload_bound'),dict(name='no_marker',start=0x7ff0,marker=None,count=0,expect='scan_exhausted'),dict(name='partial_run',start=0x7fd0,marker=0x7fd0,count=4,expect='scan_exhausted')]
    rng=random.Random(0x1b0ee);rows=[];coverage=set();n=Native()
    try:
        for case in cases:
            for mode in [0,0x2000]:
                for ccr in range(32):
                    image=bytearray(atlas);image[BASE:END+0x100]=bytes.fromhex('5a')*(END+0x100-BASE)
                    if case['marker']is not None:
                        a=BASE+case['marker'];image[a:a+case['count']*4]=bytes.fromhex('12345678')*case['count']
                    regs=[rng.getrandbits(32)for _ in range(15)]+[0x1e0000 if mode else 0x180000]
                    image[0x1b0ee:0x1b100]=payload;actual=run(n,image,case,mode|ccr,regs)
                    image[0x1b0ee:0x1b100]=legacy;expected=run(n,image,case,mode|ccr,regs);assert actual==expected
                    assert actual['classification']==case['expect'],(case,actual)
                    if actual['classification']=='marker_run_within_payload_bound':assert actual['CPU']['regs'][10]==BASE+case['marker']+64 and actual['CPU']['regs'][10]<=END
                    coverage.update(actual['PCs']);rows.append(dict(case=case['name'],incoming_SR=mode|ccr,**actual))
        comparisons=[]
        for case in [cases[0],cases[1]]:
            image=bytearray(atlas);image[BASE:END+0x100]=b'Z'*(END+0x100-BASE);a=BASE+case['marker'];image[a:a+64]=bytes.fromhex('12345678')*16;regs=[0]*15+[0x1e0000]
            image[0x1b0ee:0x1b100]=original;buggy=run(n,image,case,0x201f,regs);image[0x1b0ee:0x1b100]=payload;fixed=run(n,image,case,0x201f,regs)
            comparisons.append(dict(case=case['name'],original=buggy['classification'],repaired=fixed['classification']))
        assert comparisons[0]['original']==comparisons[0]['repaired']=='marker_run_within_payload_bound'
        assert comparisons[1]['original']=='scan_exhausted' and comparisons[1]['repaired']=='marker_run_within_payload_bound'
    finally:n.close()
    save(out/'cases.json',rows);save(out/'original_vs_repaired.json',comparisons)
    overread_cases=sorted({x['case']for x in rows if x['input_window_overread_addresses']})
    assert 'no_marker'in overread_cases and 'run_past_end'in overread_cases
    result=dict(status='terminal_source_assembled_scan_and_payload_continuations_pass_with_known_read_limit',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),build_proof=str(bp),build_proof_sha256=sha(bp),native_cases=len(rows),original_vs_repaired= comparisons,original_instruction_locations_covered=len(coverage),all32CCR_and_both_stack_modes=True,fullCPU_RAM_cycle_match_to_legacy_repair=True,source_binary_equals_legacy_repair=True,accepted_marker_payload_pointer_bounded=True,overread_fixture_cases=overread_cases,known_limitation='Candidate long read occurs before bound check; no-marker/partial-run fixtures read at1C7FFE across the32Kinputwindowend. A16long marker run past theend is rejected before payload acceptance, but its reads still occur. This reproduces the existing repair; it is not a generally bounds-safe parser.',source_sha256={str(Path(__file__)):sha(__file__),build['canonical_source']:build['canonical_source_sha256'],build['linker']:build['linker_sha256']},execution_dependencies_sha256={str(p):sha(p)for p in [ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib']},scope='512native instruction/continuation fixtures; assembled source and exact legacy repairedbytes have identical fullCPU/RAM/returnedcycles at declared stops. Two original-vs-repair cases demonstrate intended2bytephase recovery. No full-loader/IRQ/physicalconsole or whole-game equivalence proof.')
    save(out/'report.json',result);save(ROOT/'verification/native-word-scan-current.json',result);print(result['status'],len(rows),'overread cases',overread_cases,flush=True)
if __name__=='__main__':main()
