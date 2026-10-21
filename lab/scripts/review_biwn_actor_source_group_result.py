"""Publish coordinator review of finite source-porting and local inference evidence."""
import json,hashlib
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    publication=read(V/'actor-group-source-publication-current.json');component=read(publication['component_proof']);native=read(publication['native_proof']);errors=read(V/'native-actor-group-errors-current.json')
    author=read(V/'local-actor-source-group-author-current.json');repair=read(V/'local-actor-source-group-repair-current.json');diagnostic=read(V/'local-actor-first-difference-review-current.json')
    assert component['cases']==native['cases']==2596 and publication['binary_bytes']==3384 and component['max_compiled_private_depth']==248
    assert not author['raw_candidate_gate_pass']and not repair['raw_repair_gate_pass']and diagnostic['actual_predictions']==1
    assert len(errors['cases'])==5 and errors['status']=='terminal_native_actor_source_API_errors_pass'
    mismatch=Path(read(repair['gate_proof'])['directory'])/'mismatch.json';m=read(mismatch);a,b=m['original_trace'],m['compiled_trace'];first=next(i for i,(x,y)in enumerate(zip(a,b))if x!=y)
    out=V/'actor-source-group-reviewed'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    report=ROOT/'reports/actor-source-group.txt';assert not report.exists()
    report.write_text('''BIWN — FIVE-MEMBER ACTOR/SPRITE SOURCE GROUP

Result: reproducible3384byte native68000 source component. All2596coupled
original-versus-C cases pass; all2596also pass a retained-native-CPU replay.
Maximum observed private stack248bytes. The older generic bridge uses4596bytes
and512stack bytes. These are the five already-recovered algorithms13AE0,
134DC,137E0,10520,105DA; this is not five newly recovered functions.

WHAT EXECUTES
Root dispatch and internal group calls execute complete high-level C bodies.
Internal calls are no longer scripted member substitutes. Four remaining
external helpers102C4/DF6C/152A2/E2B8 are prescribed services. Tests check full
logicalD0, public2MBRAM, ordered widths/values, nested call/return args/D0,
root C callee saves/RTS/argument bytes and immutable text across469original
instruction sites. Two seeded reference-binary defects were rejected.
Native replay executes each instruction and checks the PC sequence, logicalD0,
publicRAM, real external-call arguments, callee saves and return/text contract.
Its queue/instruction schedules come from Unicorn; native bus events are not
independently observed. Five additional native tests check unknown-root status1,
direct/nested external status17 and inline dispatch status5 propagation, earlier
stores retained and root output unchanged. Those are source-API checks, not
original error-domain equivalence.

LOCAL MODEL TEST — EXACTLY FIVE ACTUAL PREDICTIONS
Local27B base model advertising-scholar,32Kcontext, one worker, temperature0.
Author and Reviewers use the same weights. Roles ran sequentially through the
LM Studio SDK. They are not independent agents or verified current Chat UI.
1 Author: complete source port from supplied original-CPU-checked high-level C,
  coordinator API, and explicit rules; no hidden fixture values. Failed compile
  with66getter-arity errors. This was not independent recovery from assembly.
2 Reviewer: identified getter mismatch, gave a vague slot-division concern.
3 One repair Author: compiled, but failed the first runtime case. FullD0 and
  final publicRAM matched; decoderE2B8received a private stack pointer as its
  third argument instead of the payload destination. Its p2array had only one
  element yet was used as a three-argument array. Full-pool loops also retained
  a known lost-index defect despite explicit feedback.
4 Reviewer: returned no issues after full source plus generic gate-failure log.
  The exact mismatch artifact was not supplied in that request. No approval.
5 Diagnostic Reviewer: exact first differing trace events were supplied. It
  identified the undersized p2array twice, with duplicate issues and inaccurate
  wording about the destination expression. Line1citations are not useful.
  This feedback-assisted diagnosis is not a held-out benchmark or code repair.

COORDINATOR CHANGES
The raw outputs remain unchanged and failed. A separate derivative retains the
index for all three40slot searches, allocates all three decoder arguments and
keeps destination in argument2, and propagates actual nonzero nested status at
all eight call sites. The first corrected derivative passed2596cases at3412bytes;
final status propagation reduced it to3384bytes and was checked again. The
published canonical source is byte-identical to that final tested derivative.
A clean Makefile rebuild produces the exact tested binary SHA. No training or
weight update occurred. No raw local candidate is claimed accepted.

BUILD / INSPECTION
Source: projects/black-ice-white-noise/restoration/native-m68k/actor-group-restored.c
Build: from that folder, make -f Makefile.actor-group-restored actor-group-restored
Provenance: verification/actor-group-source-publication-current.json
Prompts: Start Local AI → I, or Model Prompts and Responses.command.
The viewer contains exact saved transcripts; it does not stream native Chat.

INTEGRATION STILL REQUIRED
Source-owned C ABI omits original volatileD1/A0/A1/SR/private-frame ABI. Actual
external helper implementations, their stack depth and device/concurrent reads
are not established here. The current playable disc remains18888resident bytes
with1592reserve bytes free; this3384byte component is not inserted. A measured
4032byte staging-reserve expansion is only an option, not an adopted layout.
Adapters or all callers must be ported; heap/resource/task/startup/gameplay gates
must then pass. Current video/state/navigation differences and inherited scanner
media disagreement remain. Full readable game/same-console reconstruction,
current native Chat usability, Advertising reliability and complete future-machine
migration remain unfinished. No physical-console or future-hardware proof.
''')
    paths=[Path(__file__),report,V/'actor-group-source-publication-current.json',Path(publication['component_proof']),Path(publication['native_proof']),V/'native-actor-group-errors-current.json',V/'native-actor-source-group-reference-current.json',V/'native-actor-source-group-negatives-current.json',V/'actor-group-layout-options-current.json',mismatch,Path(publication['source']),Path(publication['binary'])]
    nd=Path(publication['source']).parent;paths += [nd/'Makefile.actor-group-restored',nd/'actor-group-restored.txt',nd/'actor-group-native-api.h',nd/'actor-group-source.ld']
    for state in [author,repair,diagnostic]:
        paths.append(Path(state['directory'])/'protocol.json')
        paths += list(Path(state['directory']).glob('*.json'))+list(Path(state['directory']).glob('*.txt'))+list(Path(state['directory']).glob('*.c'))
    for proof in [component,native,errors]:
        paths += [Path(p)for p in proof['source_sha256']]
        for p,h in proof['source_sha256'].items():assert sha(p)==h,(p,'Changed bound input')
    hashes={str(p.resolve()):sha(p)for p in paths}
    record=dict(status='terminal_actor_source_group_coordinator_reviewed',directory=str(out),report=str(report),component_cases=2596,native_cases=2596,native_source_API_error_cases=5,binary_bytes=3384,max_observed_private_stack=248,original_instruction_sites=len(component['original_instruction_addresses']),actual_local_predictions=5,raw_model_accepted=False,coordinator_corrected=True,new_training=False,current_native_Chat_verified=False,new_logical_functions=0,disc_integrated=False,source_sha256=hashes,first_failed_raw_repair_trace=dict(index=first,original=a[first],compiled=b[first],same_D0=True,same_final_public_RAM=True),remaining=['Original-facing ABI or all caller ports','Actual external helper implementations/stack depth','Memory layout plus heap/resource/task/startup/gameplay integration','Full readable original-console game','Current native Chat interaction','Advertising reliability and whole-workbench migration'])
    (out/'protocol.json').write_text(json.dumps(record,indent=2)+'\n');(V/'actor-source-group-reviewed-current.json').write_bytes((out/'protocol.json').read_bytes());print(json.dumps({k:record[k]for k in ['status','report','actual_local_predictions','binary_bytes','original_instruction_sites']}))

if __name__=='__main__':main()
