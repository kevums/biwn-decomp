"""Rebind prior exact-binary gates to combined loader payload and7680heap floor."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def main():
 pre=ROOT/'verification/native-load-bundle-preflight-current.json';b=json.loads(pre.read_text());assert sha(b['binary'])==b['binary_sha256'];rows=[]
 for kind in ['controller','rng','tasks','scheduler','heap','copy','free','initialize','acquire','allocator','release','lifecycle','heap_witness','readiness']:
  old=ROOT/'scripts'/('check_biwn_native_acquire_compact_bundle_'+kind+'.py');new=ROOT/'scripts'/('check_biwn_native_load_bundle_'+kind+'.py');s=old.read_text().replace('acquire-compact-bundle','load-bundle').replace('check_biwn_native_acquire_compact_bundle','check_biwn_native_load_bundle').replace('2ca28b7c2e074375fa44c9a556f8a304911188ac1698615901722bb38d618572',b['binary_sha256']).replace('0x1605c0','0x160bc0').replace("bundle['component_bytes']==6144","bundle['component_bytes']==7680").replace('reserves6144bytes','reserves7680bytes')
  compile(s,str(new),'exec');new.write_text(s);rows.append(dict(kind=kind,original=str(old),original_sha256=sha(old),adapted=str(new),adapted_sha256=sha(new),changes='Buildtarget/namespace/pinnedSHA and7680reservedheapfloor only. Originalfixtures/comparisonassertions/privateownerPCrange derivation retained.'))
 prep=dict(status='prepared_exact_loader_bundle_checks',recorded_at=datetime.now(timezone.utc).isoformat(),bundle_proof=str(pre),bundle_proof_sha256=sha(pre),target_binary_sha256=b['binary_sha256'],gates=rows[:8],extra_checks=rows[8:]);save(ROOT/'verification/native-load-gates-preparation-current.json',prep)
 old=ROOT/'scripts/run_biwn_acquire_compact_bundle_gates.py';new=ROOT/'scripts/run_biwn_load_bundle_gates.py';s=old.read_text().replace('native-acquire-compact-gates-preparation','native-load-gates-preparation').replace('native-acquire-compact-bundle','native-load-bundle');compile(s,str(new),'exec');new.write_text(s)
 for oldname,newname in [('check_biwn_compact_keypad','check_biwn_load_keypad'),('check_biwn_compiler_byte_fill','check_biwn_load_compiler_byte_fill')]:
  s=(ROOT/'scripts'/(oldname+'.py')).read_text().replace('native-acquire-compact-preflight','native-load-bundle-preflight').replace('compact-keypad','load-keypad').replace('verification/compiler-byte-fill','verification/load-compiler-byte-fill');new=ROOT/'scripts'/(newname+'.py');compile(s,str(new),'exec');new.write_text(s)
 print('Prepared',len(rows),'existing gate adapters for',b['binary_sha256'],flush=True)
if __name__=='__main__':main()
