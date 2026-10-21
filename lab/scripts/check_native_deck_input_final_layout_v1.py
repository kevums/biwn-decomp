"""Repeat both component matrices at the byte-identical new disc addresses."""
import json
from pathlib import Path
import check_native_deck_input_v1 as inputs
import check_native_deck_coordinate_v2 as coordinates

ROOT=inputs.ROOT;V=ROOT/'verification'
def main():
 build=json.loads((V/'native-Deck-input-disc-build-current.json').read_text());component=Path(build['component']).read_bytes();reviews={}
 for name,matrix,address,expected_file,wanted in [
  ('input',inputs,build['input_code_address'],Path(build['directory'])/'input-build/native-input.bin',2048),
  ('coordinate',coordinates,build['deck_code_address'],Path(build['directory'])/'deck-build/native-deck.bin',576)]:
  matrix.CODE=address;matrix.ARENA=build['deck_arena_address'];save=matrix.save
  target=V/('native-Deck-input-final-'+name+'-current.json')
  old_pointer=V/('native-deck-input-v1-current.json' if name=='input' else 'native-deck-coordinate-v2-current.json')
  def record(path,data):return save(target if Path(path)==old_pointer else path,data)
  matrix.save=record
  try:matrix.main()
  finally:matrix.save=save
  proof=json.loads(target.read_text());actual=Path(proof['payload']).read_bytes();assert proof['completed']==wanted
  assert actual==expected_file.read_bytes()
  offset=address-build['resident_address'];assert component[offset:offset+len(actual)]==actual
  proof.update(status='terminal_final_input_disc_'+name+'_CPU_matrix_pass',deployed_module_byte_identity=True,actual_code_address=address,actual_arena_address=matrix.ARENA,source_sha256={**proof['source_sha256'],str(Path(__file__)):inputs.sha(Path(__file__).read_bytes())})
  save(target,proof);save(Path(proof['directory'])/'final-layout-review.json',proof);reviews[name]=str(target)
 inputs.save(V/'native-Deck-input-final-layout-current.json',dict(status='terminal_both_final_input_disc_modules_CPU_matrices_pass',completed=2624,proofs=reviews,new_training=False,whole_game_complete=False))

if __name__=='__main__':main()
