"""Ordinary local request chooses a frame; installed MCP returns PNG and checked caption."""
import asyncio,base64,fcntl,hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import chat_tools,lab,lmstudio
RUNTIME=Path.home()/'.lmstudio/local-ai-lab'
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
 preset=ROOT/'presets/Game Assistant.preset.json';system=next(f['value']for f in json.loads(preset.read_text())['operation']['fields']if f['key']=='llm.prediction.systemPrompt')
 out=ROOT/'verification/easy-animation-preview'/lab.stamp();out.mkdir(parents=True)
 d={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'running','model':'advertising-scholar','system':system,'user':'Show animation frame 5 from Black Ice White Noise.','preset_sha256':lab.sha(preset),'tool_source_sha256':lab.sha(ROOT/'chat_tools.py'),'interface':'localhost SDK model tool selection; fresh installed MCP execution. Adapter forwards metadata only; native MCP includes PNG. No native Chat display or model vision claim.','config':{'temperature':0.2,'maxTokens':256},'max_prediction_rounds':2,'max_parallel_tool_calls':1,'events':[],'MCP_calls':[]};save(out/'protocol.json',d);print(out,flush=True)
 async def invoke(frame):
  params=StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools.py')],cwd=str(RUNTIME))
  async with stdio_client(params)as(reader,writer):
   async with ClientSession(reader,writer)as client:
    await client.initialize();result=await client.call_tool('render_animation_preview',{'frame':frame})
  assert not result.isError;metadata=result.structuredContent;images=[b for b in result.content if b.type=='image'];assert len(images)==1
  png=base64.b64decode(images[0].data);assert hashlib.sha256(png).hexdigest()==metadata['png_sha256'];(out/'MCP-animation-frame.png').write_bytes(png)
  d['MCP_calls'].append({'arguments':{'frame':frame},'metadata':metadata,'PNG_image_block_received':True,'SDK_model_received_image_pixels':False});save(out/'protocol.json',d);return metadata
 def render_animation_preview(frame:int=1)->dict:
  """Show a reconstructed Black Ice White Noise sprite frame. frame is a position1..72, default1. Bounded installed MCP uses C queue consumption, CPU mailbox protocol and sprite decoding with one frozen captured resource. Returns verified_caption and metadata; installed MCP also provides PNG. No full viewport/game, physical hardware or original CPU/GPU execution. Copy verified_caption exactly after rendering."""
  return asyncio.run(invoke(frame))
 with(ROOT/'runs/.inference.lock').open('w')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['contextLength']==32768
  chat=lmstudio.Chat(system);chat.add_user_message(d['user'])
  def message(value):d['events'].append(value.to_dict());save(out/'protocol.json',d)
  result=lmstudio.llm('advertising-scholar').act(chat,[chat_tools.verify_68000_fixture,chat_tools.render_inventory_preview,render_animation_preview,chat_tools.project_evidence,chat_tools.inspect_boot,chat_tools.search_references],max_prediction_rounds=2,max_parallel_tool_calls=1,config=lmstudio.LlmPredictionConfig.from_dict(d['config']),on_message=message)
  assert len(d['MCP_calls'])==1 and d['MCP_calls'][0]['metadata']['frame_position']==5
  calls=[b['toolCallRequest']for e in d['events']if e['role']=='assistant'for b in e['content']if b['type']=='toolCallRequest'];assert len(calls)==1 and calls[0]['name']=='render_animation_preview'and calls[0]['arguments']=={'frame':5}
  texts=[b['text'].strip()for e in d['events']if e['role']=='assistant'for b in e['content']if b['type']=='text'and b['text'].strip()];assert texts[-1]==d['MCP_calls'][0]['metadata']['verified_caption']
  d.update(status='ordinary_frame_request_tool_and_caption_passed',rounds=result.rounds,SDK_reported_seconds=result.total_time_seconds,completed_at=datetime.now(timezone.utc).isoformat());save(out/'protocol.json',d)
 (out/'prompts-and-responses.txt').write_text('SYSTEM:\n'+system+'\n\nUSER:\n'+d['user']+'\n\nMESSAGES:\n'+json.dumps(d['events'],ensure_ascii=False,indent=2)+'\n')
 save(ROOT/'verification/easy-animation-preview-current.json',{'directory':str(out),'status':d['status'],'seconds':result.total_time_seconds});print(json.dumps({'status':d['status'],'seconds':result.total_time_seconds,'frame':5,'answer':texts[-1]}),flush=True)
if __name__=='__main__':main()
