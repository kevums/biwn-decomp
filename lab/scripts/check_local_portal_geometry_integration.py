"""Isolate local helper in the portable portal function and compare originals."""
import ctypes as c
import hashlib
import json
import os
import subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_geometry as geometry
ROOT=Path(__file__).resolve().parents[1]


def main():
    proof=json.loads((ROOT/'verification/local-portal-key-checks-current.json').read_text())
    assert proof['status']=='local_portal_value_helper_original_CPU_match'
    helper=Path(proof['source']);assert hashlib.sha256(helper.read_bytes()).hexdigest()==proof['source_sha256']
    source=ROOT/'projects/black-ice-white-noise/restoration'
    out=Path(proof['directory'])/'portable-integration';out.mkdir()
    original=(source/'biwn_geometry.c').read_text()
    target='key=asr_word6(key);result=(result&0xffff0000u)|key;\n    if(match!=(key&15u))RETURN_D0(result&0xffff0000u);'
    assert original.count(target)==1
    replacement='''{
        int matches;
        /* Delta already follows the original bus-read order above. The local
         * value helper handles word shift/sign-extension and key matching. */
        if(direction<4u)matches=biwn_local_portal_key(0,key,0,0,0,0,0,byte,&key);
        else{key=asr_word6(key);matches=match==(key&15u);}
        result=(result&0xffff0000u)|key;
        if(!matches)RETURN_D0(result&0xffff0000u);
    }'''
    combined=helper.read_text()+'\n'+original.replace(target,replacement)
    path=out/'biwn_geometry_with_local_portal.c';path.write_text(combined)
    library=out/'libgeometry-local-portal.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(source),str(path),'-o',str(library)]
    build=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'compiler.log').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
    functions=geometry.bind(c.CDLL(str(library)))
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
    fixtures=[case for case in geometry.cases(snapshot)if case['entry']==0x10430]
    rows=[];coverage=set()
    for case in fixtures:
        a=geometry.boundary.Script(snapshot,case);b=geometry.boundary.Script(snapshot,case)
        expected,steps=geometry.original(a,case,coverage)
        status,actual=geometry.translated(functions,b,case)
        assert status==0 and actual==expected,(case,status,actual,expected)
        assert a.trace==b.trace and a.memory==b.memory,case
        rows.append(dict(parameters=case,full_D0=actual,original_instructions=steps,bus_trace=b.trace))
    guards=[]
    for missing in range(5):
        script=geometry.boundary.Script(snapshot,fixtures[0]);status,value=geometry.translated(functions,script,fixtures[0],missing=missing)
        assert status==1 and value==0xa5a55a5a and not script.trace
        guards.append(dict(missing_callback=missing,status=status))
    (out/'cases.json').write_text(json.dumps(rows,indent=2)+'\n')
    report=dict(status='portable_portal_with_unedited_local_helper_original_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(rows),guards=guards,original_instruction_addresses_exercised=len(coverage),helper=str(helper),helper_sha256=proof['source_sha256'],helper_body_edited=False,combined_source=str(path),combined_source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),original_source_sha256=hashlib.sha256((source/'biwn_geometry.c').read_bytes()).hexdigest(),compiler=command,full_route_runtime_promoted=False,new_training=False,same_weights_correlated=True,coordinator_contribution='Cloned existing portable geometry implementation; delegated shifted-key/match value step to the unedited local helper. Original sources and current replay candidates unchanged.',scope='Complete original10430portal entry versus portableC: fullD0, ordered external bus access and externally visibleRAM on finite synthetic fixtures, including invalid directions and byte sign extension. OriginalCPU uses UnicornM68000; helper separately passed pinned nativeCPU2432cases. FullCCR/private stack/timing/aliasing/gameplay excluded.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/local-portal-geometry-integration-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(rows),flush=True)


if __name__=='__main__':main()
