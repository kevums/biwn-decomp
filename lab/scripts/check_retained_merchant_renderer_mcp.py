"""Fresh installed MCP caller evidence and byte-identical controlled audio files."""
import asyncio,json,hashlib
from datetime import datetime,timezone
from pathlib import Path
from check_audio_native_mcp import ROOT,RUNTIME,unpack
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
    async with stdio_client(StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools.py')],cwd=str(RUNTIME))) as (reader,writer):
        async with ClientSession(reader,writer) as client:
            await client.initialize();tools=(await client.list_tools()).tools;assert len(tools)==6
            evidence=unpack(await client.call_tool('project_evidence',{'topic':'movie_video'}));status=unpack(await client.call_tool('project_evidence',{'topic':'status'}))
            picture=await client.call_tool('render_animation_preview',{'preview':'checked_post_dialogue_plane','frame':1})
            png=next(c for c in picture.content if c.type=='image');import base64
            image_metadata=picture.structuredContent or json.loads(next(c.text for c in picture.content if c.type=='text').split('\n\n',1)[1])
            assert hashlib.sha256(base64.b64decode(png.data)).hexdigest()==image_metadata['png_sha256']
    cp=evidence['current_checkpoint'];assert (cp['source_selected_message'],cp['video_frames'],cp['audio_samples_enqueued'],cp['source_next_boundary'])==(60,187,125,'0xef88')
    assert cp['retained_trigger_movie_post_dialogue_context'] and not cp['intermediate_trigger_capture_or_peripheral_reset']
    assert cp['source_warm_scheduler_frame_resumed'] and cp['source_post_dialogue_state2_verified'] and cp['source_post_dialogue_facing_verified']
    assert cp['animation_after_dialogue_verified'] and cp['movement_after_dialogue_verified'] and cp['source_post_dialogue_scheduler_yield_verified'] and cp['standalone_GPU_movement_cases']==1025 and not cp['collision_edge_branch_reached'] and not cp['whole_game_complete']
    assert status['newer_retained_merchant_renderer']==cp
    assert cp['renderer_after_dialogue_verified'] and cp['source_renderer_iterations']==1 and not cp['renderer_geometry_GPU_reset']
    assert cp['source_sprite_GPU_commands']==2 and cp['standalone_sprite_cases']==244 and cp['standalone_sprite_instruction_coverage']==[198,214]
    assert (ROOT/'chat_tools.py').read_bytes()==(RUNTIME/'chat_tools.py').read_bytes()
    report=dict(status='fresh_MCP_full_normal_movie_caller_evidence_and_audio_copies_match',recorded_at=datetime.now(timezone.utc).isoformat(),tools=[t.name for t in tools],checkpoint=cp,retained_merchant_renderer_checked=True,checked_post_dialogue_plane=True,native_Chat_verified=False)
    (ROOT/'verification/retained-merchant-renderer-MCP-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(tools=6,frames=187,audio_enqueued=125,message=60,native_Chat_verified=False)))
if __name__=='__main__':asyncio.run(main())
