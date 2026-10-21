"""Fresh installed MCP + actual easy launcher native integration answer."""
import asyncio,json,shutil,subprocess,time,os
from pathlib import Path
from datetime import datetime,timezone
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from check_biwn_native_button_digit import ROOT,save
RT=Path.home()/'.lmstudio/local-ai-lab'
async def check(out):
 params=StdioServerParameters(command=str(RT/'.venv/bin/python'),args=[str(RT/'chat_tools.py')],cwd=str(RT))
 async with stdio_client(params)as(reader,writer):
  async with ClientSession(reader,writer)as client:
   await client.initialize();result=await client.call_tool('project_evidence',{'topic':'input_dispatch'});assert not result.isError
   d=json.loads('\n'.join(x.text for x in result.content if x.type=='text'))
 n=d['native_M68000_button_digit'];assert n['binary_bytes']==130 and n['cases']==5151
 assert n['native_game_frame_integration_verified']and n['coordinator_edited_model_source']and not n['raw_local_model_shim_accepted_unchanged']
 assert n['native_game_integration']['actual_game_calls']==8 and n['native_game_integration']['matched_video_frames']==1500
 assert n['movable_component']['candidate_comparisons']==10302 and not n['bootable_Jaguar_CD_image']
 save(out/'MCP.json',n);save(ROOT/'verification/native-game-installed-MCP-current.json',n)
def main():
 out=ROOT/'verification/native-game-menu'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 for name in ['chat_tools.py','assistant_chat.py']:shutil.copy2(ROOT/name,RT/name)
 for name in ['native-button-movable-current.json','native-button-game-current.json']:shutil.copy2(ROOT/'verification'/name,RT/'verification'/name)
 asyncio.run(check(out))
 question='Does the recompiled native 68000 code now run inside the game? In under130words say what actually ran, who adapted it, what matches, and what is still needed for a bootable Jaguar CD game.'
 state=dict(status='prepared',directory=str(out),question=question,pid=os.getpid(),native_Chat=False,new_training=False)
 def checkpoint():save(out/'protocol.json',state);save(ROOT/'verification/native-game-menu-active.json',state)
 checkpoint();print(out,flush=True);prior=set((ROOT/'runs').glob('ask-*-game'));started=time.monotonic()
 with(out/'menu.log').open('w')as log:
  child=subprocess.Popen(['/bin/zsh',str(RT/'Start Local AI.command')],stdin=subprocess.PIPE,stdout=log,stderr=subprocess.STDOUT,text=True);state.update(status='running_actual_menu',child_pid=child.pid);checkpoint();child.communicate('1\n'+question+'\n/quit\n')
 assert child.returncode==0;new=set((ROOT/'runs').glob('ask-*-game'))-prior;assert len(new)==1;run=new.pop();turn=json.loads((run/'session.json').read_text())['turns'][0]
 state.update(status='terminal_pending_coordinator_review',run=str(run),wall_seconds=time.monotonic()-started,turn=turn);checkpoint();save(ROOT/'verification/native-game-menu-current.json',state);print(json.dumps(dict(status=state['status'],run=str(run),answer=turn['answer'],seconds=turn['seconds'],flags=turn['quality_flags'],rounds=turn['rounds'])),flush=True)
if __name__=='__main__':main()
