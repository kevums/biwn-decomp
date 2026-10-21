"""Fresh installed evidence and actual launcher inference for native CDI."""
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
   evidence=json.loads('\n'.join(x.text for x in result.content if x.type=='text'))
 d=evidence['native_M68000_button_digit']['fresh_native_optimized'];assert d['frames_per_lane']==24000 and d['native_rebuilt_entries']==4
 assert d['comparison_analysis']['arithmetic_entry_events']==142753
 assert d['comparison_analysis']['prior_run_real_input_replay']['calls']==138014
 assert d['comparison_analysis']['video_different_frames']==141 and d['comparison_analysis']['tracked_state_different_frames']==6
 assert d['normal_arithmetic_cases']==6552 and d['zero_exception_cases']==512
 assert d['native_reserved_bytes']==1240 and d['native_resident_bytes']==1236
 assert d['raw_guided_model_source_accepted_unchanged']and not d['coordinator_edited_model_source']
 save(out/'MCP.json',d);save(ROOT/'verification/native-optimized-disc-installed-MCP-current.json',d)
def main():
 out=ROOT/'verification/native-optimized-disc-menu'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 for name in ['chat_tools.py','assistant_chat.py']:shutil.copy2(ROOT/name,RT/name)
 asyncio.run(check(out));question='What did the local Restorer actually improve in native math? In under150words explain guidance and repair validation, distinguish the same-input emulated cost benchmark from fresh-run performance, and state remaining video/state differences, emulator dependencies and full-game limits.'
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),question=question,native_Chat=False,new_training=False)
 def checkpoint():save(out/'protocol.json',state);save(ROOT/'verification/native-optimized-disc-menu-active.json',state)
 checkpoint();print(out,flush=True);prior=set((ROOT/'runs').glob('ask-*-game'));started=time.monotonic()
 with(out/'menu.log').open('w')as log:
  child=subprocess.Popen(['/bin/zsh',str(RT/'Start Local AI.command')],stdin=subprocess.PIPE,stdout=log,stderr=subprocess.STDOUT,text=True);state.update(status='running_actual_menu',child_pid=child.pid);checkpoint();child.communicate('1\n'+question+'\n/quit\n')
 assert child.returncode==0;new=set((ROOT/'runs').glob('ask-*-game'))-prior;assert len(new)==1;run=new.pop();turn=json.loads((run/'session.json').read_text())['turns'][0]
 state.update(status='terminal_pending_coordinator_review',run=str(run),wall_seconds=time.monotonic()-started,turn=turn);checkpoint();save(ROOT/'verification/native-optimized-disc-menu-current.json',state)
 print(json.dumps(dict(status=state['status'],run=str(run),answer=turn['answer'],seconds=turn['seconds'],flags=turn['quality_flags'],rounds=turn['rounds'])),flush=True)
if __name__=='__main__':main()
