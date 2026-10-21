"""Check the bytes-only exit planner against prior exact plans and current room data."""
import sys,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import biwn_indoor_exit_from_ram_v1 as new
import biwn_indoor_exit_planner as old
from run_biwn_native_fast_gameplay_route import sha,save

def main():
 out=ROOT/'verification/current-room-exit-parser'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 manifest=json.loads((ROOT/'verified-previews/indoor-exit-planning-scene.json').read_text());historical=ROOT/manifest['relative_RAM'];raw=historical.read_bytes();left=old.plan(ROOT);right=new.plan(raw,manifest['scene_index']);assert left['candidates']==right['candidates'];cases=['preserved_historical_exact_source_plan'];inputs=[historical,ROOT/'biwn_indoor_exit_planner.py',ROOT/'biwn_indoor_exit_from_ram_v1.py',Path(__file__)]
 current=json.loads((ROOT/'verification/native-actor-navigation-candidate-current.json').read_text());p=Path(current['directory'])/'candidate/RAM-final.bin';raw=p.read_bytes();scene=int.from_bytes(raw[0x49c64:0x49c66],'big');plan=new.plan(raw,scene);assert plan['candidates'][0]['plan']['waypoints']==[dict(X=11296,Z=41376),dict(X=11296,Z=41312)];cases.append('current_south_exit_exact_records');inputs.append(p)
 altered=bytearray(raw);altered[0x49c62:0x49c64]=(1).to_bytes(2,'big');assert new.plan(altered,scene)['candidates']==[];cases.append('upper_floor_not_outdoor_exit')
 altered=bytearray(raw);address=int.from_bytes(raw[0x49c18:0x49c1c],'big');altered[0x49c18:0x49c1c]=(address|0x80000000).to_bytes(4,'big');assert new.plan(altered,scene)['candidates']==plan['candidates'];cases.append('tagged_pointer_equivalence')
 for label,altered in [('short_RAM',raw[:-1]),('out_of_RAM_pointer',raw[:0x49c18]+(0x200000).to_bytes(4,'big')+raw[0x49c1c:])]:
  try:new.plan(altered,scene)
  except ValueError:cases.append(label+'_rejected')
  else:raise AssertionError(label)
 assert raw==p.read_bytes();save(out/'current-plan.json',plan);state=dict(status='terminal_current_room_exit_parser_checked',directory=str(out),cases=cases,new_model_predictions=0,native_game_memory_modified=False,controller_executed=False,source_sha256={str(p):sha(p)for p in inputs},scope=__doc__+' Pure bytes input. Legacy live_game_state=false means this parser has no live handle; its caller supplies the current frame snapshot and emits ordinary controller buttons. No independent full-game/timing claim.');save(out/'protocol.json',state);save(ROOT/'verification/current-room-exit-parser-current.json',state);print(state['status'],len(cases))
if __name__=='__main__':main()
