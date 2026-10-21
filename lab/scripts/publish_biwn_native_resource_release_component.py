"""Freeze resource-release component evidence; no new CDI/game promotion."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
 ap=ROOT/'verification/local-native-resource-release-current.json';a=json.loads(ap.read_text());proofs=[ROOT/'verification/native-resource-release-current.json',ROOT/'verification/native-resource-release-bundle-current.json'];gates=[json.loads(p.read_text())for p in proofs];assert a['coordinator_supplied_complete_algorithm']and a['raw_model_C_unchanged']
 native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';assert sha(native/'resource-release-native.c')==a['source_sha256']==sha(a['source'])
 for g in gates:
  assert g['source_accepted']and g['native_cases']==g['trace_cases']==768 and g['free_C_entry_hits']==9024
  for field in ['source_sha256','execution_dependencies_sha256']:
   for p,d in g[field].items():assert sha(p)==d,p
 assert gates[0]['binary_bytes']==240 and gates[1]['binary_bytes']==5986
 now=datetime.now(timezone.utc);out=ROOT/'verification/native-resource-release-component-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);deps={};snapshots={}
 def pin(p,snapshot=False):
  p=Path(p).resolve();assert p.is_relative_to(ROOT);relative=str(p.relative_to(ROOT));digest=sha(p)
  if snapshot:
   dest=out/(hashlib.sha256(relative.encode()).hexdigest()[:12]+'-'+p.name)
   if not dest.exists():shutil.copy2(p,dest)
   assert sha(dest)==digest;deps[str(dest.relative_to(ROOT))]=digest;snapshots[relative]=str(dest.relative_to(ROOT))
  else:deps[relative]=digest
 for p in [ap,*proofs,Path(__file__)]:pin(p,True)
 for g in gates:
  for field in ['source_sha256','execution_dependencies_sha256']:
   for p in g[field]:pin(p,True)
  directory=Path(g['directory'])
  for p in directory.glob('*.json'):pin(p)
  pin(directory/'disassembly.txt');pin(g['compiled_binary'])
 history=[a,a['previous'],a['previous']['previous']]
 for attempt in history:
  for p in Path(attempt['directory']).iterdir():
   if p.is_file():pin(p,True)
 initial=history[-1];reviewer=initial['roles'][1];author=initial['roles'][0]
 facts=dict(original_entry='0x1B002',original_bytes=66,new_C_bodies=1,source_accepted_scope='Only unchanged fully guided C under stated component gates.',native_CPU_cases_per_profile=768,ordered_access_cases_per_profile=768,standalone_bytes=240,linked_bundle_bytes=5986,reserved_bytes=6144,padding_if_reserved=158,free_C_entry_hits_per_profile=9024,raw_C_unchanged=True,canonical_C=str(native/'resource-release-native.c'),coordinator_supplied_complete_algorithm=True,coordinator_scope='Original disassembly, ABI/native prologue/capture/header/build/link/tests, complete final algorithm. No manual edit to accepted model C.',attempts=[dict(role='Local Author',seconds=author['seconds'],outcome='Rejected first native case:wrong argument offset and missingD0/CCR commits.'),dict(role='Same-weight Reviewer',seconds=reviewer['seconds'],outcome='Output budget ended mid-review with no usable final verdict; incorrect16bitMULS explanation. Not independent validation.'),dict(role='Targeted Repair Author',seconds=history[1]['reported_seconds'],outcome='Rejected first native case:incorrectcarry1; inspected stale nested-callD0 and forbidden frame write.'),dict(role='Fully guided Author',seconds=a['reported_seconds'],outcome='Accepted raw C unchanged after both768native/768ordered profiles.')],scope=gates[1]['scope'],new_training=False,independent_model_validation=False,native_Chat=False,new_disc_built=False,game_integration_verified=False,other_relinked_bundle_components_reverified=False,fixed_input_native25_failure_not_resolved=True)
 manifest=dict(status='published_native_resource_release_component_only',recorded_at=now.isoformat(),directory=str(out),facts=facts,dependencies_sha256=deps,source_snapshots=snapshots,whole_game_complete=False)
 save(out/'publication.json',manifest);save(ROOT/'verification/native-resource-release-component-publication-current.json',manifest);print(json.dumps({'status':manifest['status'],'directory':str(out),'dependencies':len(deps),'standalone_bytes':240,'linked_bytes':5986}),flush=True)
if __name__=='__main__':main()
