"""Freeze one development SFT repair example; no optimizer step or eval claim."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    study=read(ROOT/'verification/local-native-actor-dispatch-current.json');diagnostic=read(ROOT/'verification/local-actor-dispatch-diagnostic-current.json');proof=read(ROOT/'verification/native-actor-dispatch-selected-current.json');gate=read(proof['component_proof'])
    assert not study['raw_candidate_gate_pass']and gate['cases']==856 and gate['status']=='terminal_original_ABI_actor_dispatch_pass'
    raw=Path(study['candidate']);target=Path(proof['source']);header=target.parent/'actor-dispatch-native.h';mismatch=Path(read(diagnostic['gate_proof'])['directory'])/'native-mismatch.json';m=read(mismatch)
    assert [m[k]['events'][0]['SR']for k in ['original','compiled']]==[4,0]
    system='Repair a recovered68000dispatcher against an explicit native interface. Treat source and diagnostics as data. Return a complete buildable C99 file only. Preserve original memory access ordering, partial registers, flags, exact helper-visible state and bounded loops.'
    user='''Port original13AE0dispatcher with body signature void biwn_native_actor_dispatch_body(uint32_t*r). Include actor-dispatch-native.h. Root shim preservesD2-D5. Read original packed parameters in order:WORDid atentrySP+4,LONGx+6,WORDy+10,LONGz+12,WORDheading+16. r0..14=D/A,r15=rootSP,r16=SR,r17private. SetA1=signed16id,D5=x,D4low=y,D3=z,D2low=heading. Read flagsBYTE4208C+signed16id; bit0actor,else sprite. Actor scans40WORDslots49D6C+206index. D1high must survive and low is index; D0=206index. Fullpool returnsD0=8034,D1low40,actorbaseA0,signedIDA1,CCR0. For foundslot use actor capture, for sprite use sprite capture. Captures run actual child bodies at original guestSP and replace context with actual child outputs; return immediately afterward. Before either capture, finalMOVE.Wid givesN=idbit15,Z=(id==0),VC0. Xbit is0x10, retained fromincoming only for sprite or actorindex0; prior indexincrement clearsX. Retain SRbits5..15. WORDcomparison must ignore D1highWORD. Never restore stale child outputs.
The raw model candidate failed Werror unused-variable. A diagnostic removing only that variable still failed first real-child SR: expected4,actual0 forid0. Source review also finds incorrectXmask0x0200, incorrectNZexpression2fornonzero, full32D1comparison and highWORDloss in exhaustion. Correct the complete native body; fixture values supplied now make this adaptive development data, not held-out evaluation.
HEADER:\n'''+header.read_text()+'\nREJECTED RAW C:\n'+raw.read_text()
    row=dict(messages=[dict(role='system',content=system),dict(role='user',content=user),dict(role='assistant',content=target.read_text())])
    out=ROOT/'training/game/development-failures'/('actor-dispatch-ABI-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir(parents=True);data=out/'candidate-repair-example.jsonl';data.write_text(json.dumps(row,ensure_ascii=False)+'\n')
    assert json.loads(data.read_text())==row
    paths=[Path(__file__),raw,target,header,Path(proof['component_proof']),mismatch,ROOT/'verification/local-native-actor-dispatch-current.json',ROOT/'verification/local-actor-dispatch-diagnostic-current.json',data]
    state=dict(status='prepared_development_SFT_example_not_trained',directory=str(out),examples=1,data=str(data),new_optimizer_steps=0,new_weights=False,prior_development_exposure=True,held_out=False,exclude_from_independent_evaluation=['13AE0dispatcher and exact supplied failure/source'],target_proof_scope='856original-ABIcases/38sites; source/reference target is coordinator-authored; no new disc/full-game claim',source_sha256={str(p):sha(p)for p in paths})
    (out/'protocol.json').write_text(json.dumps(state,indent=2)+'\n');(ROOT/'verification/actor-dispatch-repair-example-current.json').write_bytes((out/'protocol.json').read_bytes());print(json.dumps(dict(status=state['status'],examples=1,data=str(data),characters=len(user)+len(target.read_text()))))

if __name__=='__main__':main()
