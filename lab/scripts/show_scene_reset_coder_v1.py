"""Show the latest saved local code task; never invoke a model or training."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 for name in ['local-scene-reset-flags-v3-current.json','local-scene-reset-flags-v2-current.json']:
  pointer=ROOT/'verification'/name
  if pointer.is_file():break
 else:print('No scene-reset coding run is saved yet. Use menu4 or BIWN Code Test.command.');return
 state=json.loads(pointer.read_text());folder=Path(state['directory'])
 print('BIWN LOCAL CODE TEST\n'+state['status']+'\n'+str(folder)+'\n')
 print('Complete reset1102A task with supplied CPU/bus/flag primitives. This development task is separate from the game image and training quality.\n')
 transcript=folder/'prompts-and-responses.txt'
 if transcript.is_file():print(transcript.read_text())
 else:
  for role in ['Author','Repair']:
   prompt=folder/role/'prompt.json';partial=folder/role/'response.partial.txt'
   if prompt.exists():print(role+' exact prompt\n'+prompt.read_text())
   if partial.exists():print(role+' partial response\n'+partial.read_text())
 for row in state.get('rounds',[]):print(row['role']+': '+('768 CPU/RAM/order cases passed'if row['verified']else'rejected by checker')+'; '+str(row['seconds'])+' seconds')
if __name__=='__main__':main()
