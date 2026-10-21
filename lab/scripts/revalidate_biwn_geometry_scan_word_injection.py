"""Recheck the identical linked scanner after correcting WORD trace injection."""
import hashlib,json,shutil,os
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_native_geometry_scan_v2 as gate
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
    v=ROOT/'verification';bp=v/'native-geometry-scan-disc-build-current.json';build=read(bp);gp=v/'native-geometry-scan-v2-current.json';proof=read(gp)
    assert proof['status']=='terminal_native_geometry_scan_v2_CPU_RAM_ordered_pass' and proof['source_accepted']
    assert proof['native_cases']==1377 and proof['changing_coordinate_cases']==768
    assert sha(build['derived_disc'])==build['derived_disc_sha256'] and sha(build['derived_stage'])==build['derived_stage_sha256']
    assert proof['source_sha256']==sha(ROOT/'projects/black-ice-white-noise/restoration/native-m68k/geometry-scan-kernel.c')
    for p,h in proof['dependencies_sha256'].items():assert sha(p)==h,p
    now=datetime.now(timezone.utc);out=v/'native-geometry-scan-word-correction'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    (out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes());shutil.copy2(bp,out/'build-before-correction.json');shutil.copy2(gp,out/'corrected-component.json')
    payload=Path(build['component']).read_bytes();gate.BASE=build['geometry_scan_start'];length=build['geometry_scan_end']-gate.BASE;code=payload[gate.BASE-build['resident_address']:gate.BASE-build['resident_address']+length]
    standalone=Path(proof['binary']).read_bytes();normalized=bytearray(code)
    for row in build['relocations']:
        at=row['offset'];assert int.from_bytes(code[at:at+4],'big')==row['after'] and int.from_bytes(standalone[at:at+4],'big')==row['before'];normalized[at:at+4]=standalone[at:at+4]
    assert bytes(normalized)==standalone and len(code)==428
    common=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());common[build['resident_address']:build['resident_address']+len(payload)]=payload;candidate=bytearray(common);candidate[gate.ENTRY:gate.ENTRY+8]=b'\x4e\xf9'+gate.BASE.to_bytes(4,'big')+b'\x4e\x71'
    state=dict(status='running_linked_scanner_width_correct_revalidation',pid=os.getpid(),directory=str(out),derived_disc_sha256=build['derived_disc_sha256'],disc_bytes_changed=False,stable_completed=0,changing_completed=0,new_training=False,default_promoted=False)
    def mark():save(out/'protocol.json',state);save(v/'native-geometry-scan-word-correction-active.json',state)
    mark();n=gate.Native();rows=[];coverage=set()
    try:
        for kind,cases in [('stable',gate.vectors()),('changing',gate.changing_vectors())]:
            for index,case in enumerate(cases):
                x=gate.trace(common,case,length,True);y=gate.trace(candidate,case,length,False)
                assert x[1]==y[1] and gate.normalize(y[0],x[0],length)==x[0],('corrected final ordered',kind,index)
                a=gate.native(n,common,case,length,True,x[2]);b=gate.native(n,candidate,case,length,False,y[2])
                assert a[1]==b[1] and gate.normalize(b[0],a[0],length)==a[0],('corrected final CPU/RAM',kind,index)
                assert gate.normalize(a[0],x[0],length)==x[0] and gate.normalize(b[0],y[0],length)==y[0],('native/trace public RAM agreement',kind,index)
                if kind=='stable':assert b[1][:18]==gate.expected(case)
                coverage.update(a[2]);rows.append(dict(kind=kind,index=index,CPU=b[1],ordered_accesses=len(x[1]),source_changes=x[2],compiled_changes=y[2]));state[kind+'_completed']=index+1
                if index%256==0:mark();print(kind,index+1,'/',len(cases),flush=True)
        save(out/'results.json',rows);assert len(coverage)==69
        deps={str(p):sha(p)for p in [out/'runner-as-run.py',out/'build-before-correction.json',out/'corrected-component.json',Path(gate.__file__),Path(proof['binary']),Path(build['component']),Path(build['linked_component']),Path(build['derived_disc']),Path(build['derived_stage']),out/'results.json']}
        deps.update(proof['dependencies_sha256'])
        state.update(status='terminal_linked_scanner_word_injection_corrected_pass',stable_cases=1377,changing_cases=768,original_instruction_coverage=[69,69],native_tracer_public_RAM_cross_check=True,dependencies_sha256=deps,old_ordered_WORD_verdict_superseded=True,scope='Exact same428byte final-linked scanner and CDI; no source or game byte changes. Corrected trace injection writes exactly the declared2or4bytes. Native CPU/public RAM agrees with corrected traces on both sides for1377stable+768changing cases, plus full register/bank/ordered-access equality original versus compiled. Previous96startup and fresh native gameplay evidence remains byte-identical, not rerun by this receipt. Old fullCPU/RAM native replay was width-correct; old WORD ordered-event values were inconsistent and are superseded. No full-game/cycle/physical proof.');mark();save(v/'native-geometry-scan-word-correction-current.json',state)
        corrected=dict(build,component_gate=str(out/'corrected-component.json'),component_gate_sha256=sha(out/'corrected-component.json'),verification_correction=str(out/'protocol.json'),verification_correction_sha256=sha(out/'protocol.json'),verification_directory=str(out),prior_build=str(out/'build-before-correction.json'),prior_build_sha256=sha(out/'build-before-correction.json'),verification_note='Same exact disc/component/stage bytes; corrected standalone/final-address ordered WORD injection and native/tracer publicRAM cross-checks. Prior96startup/live evidence retained by exact hashes, not newly executed.')
        save(out/'corrected-build.json',corrected);save(v/'native-geometry-scan-corrected-build-current.json',corrected);print(state['status'],flush=True)
    except BaseException as error:state.update(status='terminal_linked_scanner_word_correction_failed',error=repr(error));mark();raise
    finally:n.close()
if __name__=='__main__':main()
