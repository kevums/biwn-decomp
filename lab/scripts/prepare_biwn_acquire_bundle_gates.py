"""Checked target/link-namespace adaptation of existing native26 validators."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 proof=ROOT/'verification/native-acquire-bundle-preflight-current.json';a=json.loads(proof.read_text());assert sha(a['binary'])==a['binary_sha256'];rows=[]
 for kind in ['controller','rng','tasks','scheduler','heap','copy','free','initialize']:
  old=ROOT/'scripts'/('check_biwn_native_resource_bundle_'+kind+'.py');new=ROOT/'scripts'/('check_biwn_native_acquire_bundle_'+kind+'.py');s=old.read_text();t=s.replace('resource-bundle','acquire-bundle')
  pattern=r'(?m)^( +)[^\n]*payload\s*=\s*binary\.read_bytes\(\)[^\n]*$';matches=list(re.finditer(pattern,t));assert len(matches)==1,(kind,len(matches));m=matches[0]
  t=t[:m.end()]+'\n'+m.group(1)+'assert sha(binary)=='+repr(a['binary_sha256'])+', "Wrong relocated bundle bytes"'+t[m.end():]
  compile(t,str(new),'exec');new.write_text(t)
  rows.append(dict(kind=kind,original=str(old),original_sha256=sha(old),adapted=str(new),adapted_sha256=sha(new),changes='Only literal resource-bundle→acquire-bundle names/link target plus exact compiled SHA assertion; fixtures/normalization/loop/assertions retained.'))
 record=dict(status='prepared_eight_relocated_component_gates',recorded_at=datetime.now(timezone.utc).isoformat(),bundle_proof=str(proof),bundle_proof_sha256=sha(proof),target_binary_sha256=a['binary_sha256'],gates=rows,new_game_image=False)
 (ROOT/'verification/native-acquire-gates-preparation-current.json').write_text(json.dumps(record,indent=2)+'\n');print('Prepared8componentgates',a['binary_sha256'])
if __name__=='__main__':main()
