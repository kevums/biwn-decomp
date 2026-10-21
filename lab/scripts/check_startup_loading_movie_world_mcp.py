"""Fresh MCP live startup chain/capture scope and matching plane PNG."""
import asyncio,json,hashlib,base64
from datetime import datetime,timezone
from check_audio_native_mcp import ROOT,RUNTIME,unpack
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
    async with stdio_client(StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools.py')],cwd=str(RUNTIME)))as(r,w):
        async with ClientSession(r,w)as client:
            await client.initialize();tools=(await client.list_tools()).tools;assert len(tools)==6
            results={k:unpack(await client.call_tool('project_evidence',{'topic':k}))for k in ['render_startup','rng','status','world_input_rendering','movie_video']}
            picture=await client.call_tool('render_animation_preview',{'preview':'checked_post_dialogue_plane','frame':1});png=next(c for c in picture.content if c.type=='image');image_metadata=picture.structuredContent or json.loads(next(c.text for c in picture.content if c.type=='text').split('\n\n',1)[1])
    cp=json.loads((ROOT/'verification/startup-loading-movie-world-checkpoint.json').read_text())
    assert all(result['current_checkpoint']==cp for result in results.values())
    assert not cp['earlier_startup_capture_supplied']and not cp['ready_merchant_capture_supplied']and not cp['source_DF60_RTS_completion_adapter']and cp['source_startup_to_loading_movie_world_connected']
    assert cp['verified_profiles']==2 and cp['source_startup_scheduler_handoffs']==26 and cp['source_startup_disc_requests']==12 and cp['source_loading_requests']==6 and cp['total_asset_disc_requests']==18
    assert cp['video_frames']==187 and cp['audio_samples_enqueued']==125 and cp['source_world_iterations']==12 and cp['source_scheduler_handoffs']==60 and not cp['source_boot_verified']
    assert hashlib.sha256(base64.b64decode(png.data)).hexdigest()==image_metadata['png_sha256']==cp['geometry_plane_preview']['PNG_sha256']
    assert (ROOT/'chat_tools.py').read_bytes()==(RUNTIME/'chat_tools.py').read_bytes()
    report=dict(status='fresh_MCP_live_startup_loading_movie_world_scope_and_plane_match',recorded_at=datetime.now(timezone.utc).isoformat(),tools=[x.name for x in tools],evidence=results,preview=image_metadata,installed_tools_sha256=hashlib.sha256((RUNTIME/'chat_tools.py').read_bytes()).hexdigest(),native_Chat_verified=False)
    (ROOT/'verification/startup-loading-movie-world-MCP-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],tools=len(tools),startup_capture=False)))
if __name__=='__main__':asyncio.run(main())
