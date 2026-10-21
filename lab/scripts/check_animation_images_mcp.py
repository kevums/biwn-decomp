"""Fresh installed animation image/evidence transport plus existing inventory regression."""
import asyncio,base64,hashlib,json,struct
from datetime import datetime,timezone
from pathlib import Path
from check_audio_native_mcp import ROOT,RUNTIME,unpack
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
 proof=json.loads((ROOT/'verification/biwn-animation-frames-checks.json').read_text());frames=Path(proof['directory'])/'frames'
 params=StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools.py')],cwd=str(RUNTIME));rows=[];guards=[]
 async with stdio_client(params)as(reader,writer):
  async with ClientSession(reader,writer)as client:
   await client.initialize();names=[t.name for t in(await client.list_tools()).tools];assert len(names)==6 and'render_animation_preview'in names
   evidence={topic:unpack(await client.call_tool('project_evidence',{'topic':topic}))for topic in ['status','animation_images','animation','task_runtime']}
   assert all(e['isolated_cpu_and_portable_C_checks']['portable_C_component_count']==53 for e in evidence.values())
   assert evidence['status']['isolated_cpu_and_portable_C_checks']['processor_components']=={'CPU':51,'GPU':2}
   assert evidence['animation_images']['CPU_animation_images']['CPU_cases']==321
   assert evidence['animation_images']['sequential_animation_sprite_pipeline']['frame_cases']==144
   assert evidence['animation_images']['sequential_animation_sprite_pipeline']['producer_consumer_sequence_steps']==16
   assert not evidence['task_runtime']['current_connected_pipeline']['animation_queue_consumer_linked']
   assert evidence['animation']['animation_link_status']['queue_consumer_linked_in_sequential_sprite_pipeline']
   for arguments,frame in [({},1),({'frame':12},12),({'frame':72},72)]:
    result=await client.call_tool('render_animation_preview',arguments);assert not result.isError
    d=result.structuredContent;images=[b for b in result.content if b.type=='image'];assert len(images)==1;png=base64.b64decode(images[0].data)
    reference=json.loads((frames/f'{frame-1:02d}'/'frame.json').read_text())
    assert hashlib.sha256(png).hexdigest()==d['png_sha256'] and png.startswith(b'\x89PNG\r\n\x1a\n')
    assert list(struct.unpack('>II',png[16:24]))==d['preview_dimensions']
    assert d['frame_position']==frame and d['native_frame_index']==frame-1
    assert d['raw_sha256']==reference['raw_sha256']and d['header_hex']==reference['header_hex']and d['dimensions']==reference['dimensions']
    assert d['consumer_full_D0']==reference['full_D0']and not d['whole_game_rebuilt']
    assert not d['original_CPU_instructions_executed_during_render']and not d['original_GPU_instructions_executed_during_render']
    assert d['device_statistics']['C_sprite_decodes']==1 and d['device_statistics']['game_frames_executed']==0
    rows.append({'arguments':arguments,'metadata':d,'original_comparison_matches':True,'PNG_image_block_received':True})
   cache=RUNTIME/'runs/animation-previews';before={p.name for p in cache.iterdir()}
   for frame in [0,73,-1,True,'5',1.5,None]:
    result=await client.call_tool('render_animation_preview',{'frame':frame});assert result.isError;guards.append({'frame':frame,'rejected':True})
   assert before=={p.name for p in cache.iterdir()}
   result=await client.call_tool('render_inventory_preview',{});assert not result.isError
   inventory=result.structuredContent;assert inventory['raw_frame_sha256']=='2234cbb2e4c1fe8b97e2193d10f25846dc0a81b9dd18d7ba4dcc8791ee166e62'
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'fresh_installed_animation_images_and_guards_passed','tools':names,'evidence':evidence,'renders':rows,'invalid_inputs':guards,'invalid_requests_created_no_cache_entries':True,'inventory_regression_passed':True,'native_Chat_display_verified':False,'scope':'Installed MCP/native reconstructed C execution and image transport; not native Chat visual adoption or model vision.'}
 (ROOT/'verification/animation-images-MCP-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'tools':len(names),'renders':len(rows),'guards':len(guards),'components':53,'inventory_regression_passed':True}))
if __name__=='__main__':asyncio.run(main())
