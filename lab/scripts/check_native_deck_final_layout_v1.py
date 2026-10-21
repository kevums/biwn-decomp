"""Repeat native component matrix using byte-identical final-image module/layout."""
import json,sys
from pathlib import Path
import check_native_deck_coordinate_v2 as matrix
ROOT=matrix.ROOT;V=ROOT/'verification'
def main():
 build=json.loads((V/'native-Deck-coordinate-disc-build-current.json').read_text());matrix.CODE=build['deck_code_address'];matrix.ARENA=build['deck_arena_address'];save=matrix.save
 def record(path,data):
  if Path(path)==V/'native-deck-coordinate-v2-current.json':path=V/'native-deck-final-layout-current.json'
  return save(path,data)
 matrix.save=record;matrix.main()
 pointer=V/'native-deck-final-layout-current.json';state=json.loads(pointer.read_text());actual=Path(state['payload']);deployed=Path(build['directory'])/'deck-build/native-deck.bin'
 assert actual.read_bytes()==deployed.read_bytes()and len(actual.read_bytes())==build['deck_code_bytes']
 component=Path(build['component']).read_bytes();offset=matrix.CODE-build['resident_address'];assert component[offset:offset+len(actual.read_bytes())]==actual.read_bytes()
 state.update(status='terminal_final_image_native_coordinate_576_CPU_match',deployed_module_byte_identity=True,actual_code_address=matrix.CODE,actual_arena_address=matrix.ARENA,source_sha256={**state['source_sha256'],str(Path(__file__)):matrix.sha(Path(__file__).read_bytes())},SP_modulo_field_is_not_C_stack_measurement=True,native_disc_changed=False)
 save(Path(state['directory'])/'final-layout-review.json',state);save(pointer,state);print(state['status'],flush=True)
if __name__=='__main__':main()
