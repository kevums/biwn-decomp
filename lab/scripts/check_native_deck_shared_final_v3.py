"""Repeat all four component matrices at deployed addresses; verify bytes."""
import json
from pathlib import Path
import check_native_deck_shared_v3 as matrix

ROOT=matrix.ROOT; V=ROOT/'verification'
def main():
 bp=V/'native-Deck-shared-disc-build-v3-current.json';build=json.loads(bp.read_text())
 for p,h in build['source_sha256'].items():assert matrix.sha(Path(p).read_bytes())==h,p
 matrix.CODE=build['shared_Deck_code_address'];matrix.ARENA=build['deck_arena_address']
 target=V/'native-deck-shared-final-v3-current.json';old=V/'native-deck-shared-v3-current.json';save=matrix.save
 def record(path,data):return save(target if Path(path)==old else path,data)
 matrix.save=record
 try:matrix.main()
 finally:matrix.save=save
 proof=json.loads(target.read_text());actual=Path(proof['payload']).read_bytes();expected=(Path(build['directory'])/'shared-build/native-shared.bin').read_bytes();resident=Path(build['component']).read_bytes();offset=matrix.CODE-build['resident_address']
 assert proof['completed']==4992 and actual==expected==resident[offset:offset+len(actual)]
 proof.update(status='terminal_four_final_disc_modules_component_CPU_match',actual_code_address=matrix.CODE,actual_arena_address=matrix.ARENA,deployed_module_byte_identity=True,source_sha256={**proof['source_sha256'],str(Path(__file__)):matrix.sha(Path(__file__).read_bytes()),str(bp):matrix.sha(bp.read_bytes())})
 save(target,proof);save(Path(proof['directory'])/'final-layout-review.json',proof)
 print(proof['status'],flush=True)

if __name__=='__main__':main()
