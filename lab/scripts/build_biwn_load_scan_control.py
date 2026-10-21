"""Restore only the loader redirect in a copy of the scan-kernel candidate."""
from pathlib import Path
from datetime import datetime,timezone
import json,shutil,os
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
from extract_biwn_stage import swap16

def main():
 bp=ROOT/'verification/native-load-scan-disc-build-current.json';b=json.loads(bp.read_text());assert sha(b['derived_disc'])==b['derived_disc_sha256'];out=ROOT/'verification/native-load-scan-control-disc'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 patch=next(x for x in json.loads(Path(b['patch_manifest']).read_text())['patches']if int(x['address'],16)==0x1b044);original=bytes.fromhex(patch['original']);replacement=bytes.fromhex(patch['replacement']);assert len(original)==len(replacement)==8
 session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'nextstage-mapping.json').read_text());offset=mapping['payload_raw_cdi_offset']+0x1b044-0x4000;disc=out/'BIWN-23-native28scan-original-loader-control.cdi';shutil.copyfile(b['derived_disc'],disc)
 with disc.open('r+b')as f:f.seek(offset);assert f.read(8)==swap16(replacement);f.seek(offset);f.write(swap16(original));f.flush();os.fsync(f.fileno())
 changed=[];pos=0
 with Path(b['derived_disc']).open('rb')as a,disc.open('rb')as c:
  while True:
   left=a.read(1048576);right=c.read(1048576);assert len(left)==len(right)
   if not left:break
   if left!=right:
    for i,(x,y)in enumerate(zip(left,right)):
     if x!=y:assert offset<=pos+i<offset+8;changed.append(pos+i)
   pos+=len(left)
 state=dict(status='terminal_scan_payload_original_loader_control_disc_built',directory=str(out),build_proof=str(bp),build_proof_sha256=sha(bp),disc=str(disc),disc_sha256=sha(disc),parent_disc_sha256=b['derived_disc_sha256'],changed_bytes=len(changed),allowed_offset=offset,whole_game_complete=False,scope='Only8byteentryrestored; same7680payload/startup/heap/othercode andexistingword-scanrepair retained.',source_sha256={str(Path(__file__)):sha(__file__)})
 save(out/'protocol.json',state);save(ROOT/'verification/native-load-scan-control-disc-current.json',state);print(state['status'],len(changed),flush=True)
if __name__=='__main__':main()
