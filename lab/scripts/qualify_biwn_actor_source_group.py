"""Require the source-group verifier to reject no-op and internal delegation defects."""
import json
from datetime import datetime, timezone
from pathlib import Path
import check_biwn_actor_source_group as gate
from run_biwn_native_fast_gameplay_route import ROOT, sha, save


def main():
    v=ROOT/'verification';build=json.loads((v/'native-actor-source-group-build-current.json').read_text())
    folder=Path(build['directory']);payload=Path(build['binary']).read_bytes()
    symbols={p[2]:int(p[0],16)for line in(folder/'symbols.txt').read_text().splitlines()if len(p:=line.split())==3}
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();cases=gate.cases()
    out=v/'native-actor-source-group-negatives'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True);rows=[]
    wrong=bytearray(payload);at=symbols['biwn_actor_group_invoke']-gate.BASE
    wrong[at:at+4]=bytes.fromhex('70004e75');first=out/'success-without-body.bin';first.write_bytes(wrong)
    left=gate.execute(snapshot,cases[0],payload,symbols,False)
    right=gate.execute(snapshot,cases[0],bytes(wrong),symbols,True)
    mismatch=[key for key in ['D0','RAM','trace']if left[key]!=right[key]];assert mismatch
    rows.append(dict(control='success_without_body_or_D0_output',mismatched=mismatch,rejected=True,binary=str(first),sha256=sha(first)))
    start=symbols['member']-gate.BASE;end=symbols['biwn_actor_group_call']-gate.BASE
    pattern=(0x134dc).to_bytes(4,'big');assert payload[start:end].count(pattern)==1
    at=payload.index(pattern,start,end);wrong=bytearray(payload);wrong[at:at+4]=(0x134de).to_bytes(4,'big')
    second=out/'internal-child-as-external.bin';second.write_bytes(wrong)
    case=next(c for c in cases if c['entry']==0x13ae0 and any(
        a==0x4208c+(c['params'][0]if c['params'][0]<0x8000 else c['params'][0]-65536)
        and w==1 and value&1 for a,w,value in c['initial']))
    try:gate.execute(snapshot,case,bytes(wrong),symbols,True)
    except AssertionError as error:
        tb=error.__traceback__;observed=None
        while tb:
            frame=tb.tb_frame
            if frame.f_code.co_name=='code' and frame.f_locals.get('pc')==gate.EXTERNAL:
                observed={key:frame.f_locals.get(key)for key in ['pc','target','n']}
            tb=tb.tb_next
        assert observed==dict(pc=gate.EXTERNAL,target=0x134dc,n=6),observed
        rows.append(dict(control='internal_actor_child_delegated_to_external',guard_observation=observed,
                         rejected=True,binary=str(second),sha256=sha(second)))
    else:raise AssertionError('Internal delegation escaped the verifier')
    state=dict(status='terminal_source_group_noop_and_internal_delegation_negatives_rejected',directory=str(out),controls=rows,
               reference_binary=build['binary'],reference_binary_sha256=sha(build['binary']),
               source_sha256={str(p):sha(p)for p in [Path(__file__),Path(gate.__file__)]},
               scope='Two seeded target-binary defects tested through the actual source-group executor/comparison. No reference file mutated. External-delegation rejection is checked at the exact guard PC/target/count, not its empty assertion text. Not exhaustive verifier validation.')
    save(out/'protocol.json',state);save(v/'native-actor-source-group-negatives-current.json',state)
    print(state['status'])


if __name__=='__main__':main()
