"""Record exact local roles and native checkpoint evidence for review."""
import json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
now=datetime.now(timezone.utc).isoformat();out=ROOT/'verification/TOC-semantic-audit'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
proof=json.loads((ROOT/'verification/BIWN-TOC-local-C-current.json').read_text());match=json.loads((ROOT/'verification/BIWN-TOC-origin-match-current.json').read_text());roles=json.loads((ROOT/'verification/TOC-origin-local-review-current.json').read_text());model=Path(proof['candidate_source']).parent.parent
files=[ROOT/'verification/BIWN-TOC-local-C-current.json',ROOT/'verification/BIWN-TOC-checksum-trace-current.json',ROOT/'verification/BIWN-TOC-compression-current.json',ROOT/'verification/TOC-coordinate-origin-hypotheses.json',ROOT/'verification/BIWN-TOC-origin-match-current.json',ROOT/'verification/TOC-origin-local-review-current.json',ROOT/'verification/TOC-semantic-MCP-check.json',model/'request-and-response.json',model/'candidate.c',model/'coordinator-rejection.json',model/'repair-1/request-and-response.json',model/'repair-1/candidate.c',ROOT/'scripts/check_biwn_TOC_local_C.py',ROOT/'scripts/check_biwn_TOC_origin_match.py',ROOT/'scripts/check_biwn_TOC_compression.py',ROOT/'scripts/trace_biwn_TOC_checksum.py',ROOT/'chat_tools.py',ROOT/'projects/black-ice-white-noise/restoration/biwn_firmware_TOC_checksum.c',ROOT/'projects/black-ice-white-noise/restoration/biwn_firmware_TOC_checksum.h']
manifest=[]
for i,p in enumerate(files):
 target=out/f'{i:02d}-{p.name}';shutil.copy2(p,target);manifest.append(dict(source=str(p),snapshot=str(target),sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
transcript='WHO DOES WHAT\nCoordinator derives/checks firmware semantics, instruments original core, compiles and compares results, builds separate diagnostic providers. Local Restorer authors C and repair; accepted repair body is unchanged. Local Researcher/Reviewer provide sequential textual reviews using same27Bweights, not independent validation. No new weight training or promotion.\n\n'
for p in [model/'prompts-and-responses.txt',model/'repair-1/prompts-and-responses.txt',Path(roles['directory'])/'prompts-and-responses.txt']:
 transcript+='EXACT PROMPTS/RESPONSES FROM '+str(p)+'\n'+p.read_text()+'\n\n'
transcript+='COORDINATOR REVIEW OF LOCAL ROLES\n'+json.dumps(roles['coordinator_review'],indent=2)+'\n'
(out/'who-prompts-and-responses.txt').write_text(transcript)
report=dict(status='semantic_function_accepted_origin_hypothesis_verified_live_diagnostic_in_progress',recorded_at=now,directory=str(out),local_C=proof,origin_match=match,local_role_review=roles['coordinator_review'],manifest=manifest,exact_prompts_and_responses=str(out/'who-prompts-and-responses.txt'),local_instruction_case_bodies_unchanged=171,separate_model_semantic_firmware_functions=1,game_components_unchanged=139,new_weight_training=False,normal_boot_verified=False,native_Chat_verified=False,whole_goal_complete=False)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/TOC-semantic-audit-current.json').write_text(json.dumps(report,indent=2)+'\n')
feedback=dict(used_in_weight_training=False,initial_C_rejected=True,repair_C_accepted=True,proof=str(Path(proof['directory'])/'report.json'),local_review_failures=roles['coordinator_review'],exact_audit=str(out/'who-prompts-and-responses.txt'));(ROOT/'training/feedback/TOC-semantic-origin-20261015.jsonl').write_text(json.dumps(feedback)+'\n')
print(out)
