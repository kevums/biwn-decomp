"""Require real register and ordered-read defects to be rejected by the new gate."""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from check_biwn_native_button_digit import ROOT, sha, save


def main():
    v=ROOT/'verification'
    model=json.loads((v/'local-native-interior-select-repair-current.json').read_text())
    assert model['status'].startswith('terminal_'),'Do not race the local role workflow for its gate receipt'
    out=v/'native-interior-gate-negative-controls'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    reference=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/interior-select-coordinator-reference.c'
    text=reference.read_text()
    variants=[('wrong_SKIP_X','xbit=count==0;','xbit=count==1;',1,'mismatch.json'),
              ('cached_x_read','lower=r->x; uint16_t width=r->width;',
               'uint16_t width=r->width;',4,'ordered-mismatch.json')]
    rows=[]
    for name,before,after,limit,mismatch in variants:
        assert text.count(before)==1
        source=out/(name+'.c');source.write_text(text.replace(before,after))
        command=[sys.executable,str(ROOT/'scripts/check_biwn_native_interior_select.py'),
                 '--source',str(source),'--limit',str(limit),'--no-publish']
        with(out/(name+'.log')).open('w')as log:
            result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=90)
        proof=json.loads((v/'native-interior-select-active.json').read_text())
        assert proof['source']==str(source) and result.returncode!=0 and proof['status']=='terminal_failed'
        diagnostic=Path(proof['directory'])/mismatch
        assert diagnostic.is_file(),'A compile error or unrelated failure does not qualify this negative control'
        row=dict(name=name,source=str(source),source_sha256=sha(source),exit_code=result.returncode,
                 proof=str(Path(proof['directory'])/'protocol.json'),diagnostic=str(diagnostic),
                 diagnostic_sha256=sha(diagnostic),rejected_for_expected_defect=True)
        rows.append(row);print(name,'rejected as expected',flush=True)
    state=dict(status='terminal_interior_gate_register_and_read_order_negatives_rejected',directory=str(out),
               controls=rows,source_reference=str(reference),source_reference_sha256=sha(reference),
               source_sha256={str(p):sha(p)for p in [Path(__file__),ROOT/'scripts/check_biwn_native_interior_select.py']},
               scope='Two seeded compiled defects caught by original CPU/full public state or ordered-access gate. Not exhaustive verifier correctness.')
    save(out/'protocol.json',state);save(v/'native-interior-gate-negative-controls-current.json',state)


if __name__=='__main__':main()
