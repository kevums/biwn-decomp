"""Correct a source-path metadata inheritance error without changing test claims."""
import copy,json,shutil
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
 v=ROOT/'verification';p=v/'current-biwn-latest-publication-current.json';old=json.loads(p.read_text());assert old['facts']['experimental_build']['resident_bytes']==21080
 gatep=Path(old['facts']['component_proof']);gate=json.loads(gatep.read_text());source=Path(gate['source']);assert source.name=='actor-initialize-reference.c'and sha(source)==gate['source_sha256'][str(source)]
 out=v/'current-biwn-latest-publication'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);shutil.copy2(p,out/'previous-publication.json');new=copy.deepcopy(old);new['directory']=str(out);new['recorded_at']=datetime.now(timezone.utc).isoformat();new['facts']['component_verification']['source']=str(source);new['metadata_correction']='component_verification.source previously inherited dispatcher path from build; final134DCgate identifies actor-initialize-reference.c. Test counts/binaries/results unchanged.'
 new['dependencies_sha256'][str(Path(__file__).resolve())]=sha(Path(__file__));new['dependencies_sha256'][str(gatep)]=sha(gatep);new['dependencies_sha256'][str(source)]=sha(source)
 save(out/'publication.json',new);save(p,new);print(json.dumps(dict(resident_bytes=21080,corrected_source=source.name,binary_changed=False)))
if __name__=='__main__':main()
