"""Fresh installed tool lookup of current route proof and actual handles."""
import asyncio
import json
from datetime import datetime,timezone
from check_audio_native_mcp import ROOT,RUNTIME,unpack
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
    params=StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools.py')],cwd=str(RUNTIME))
    async with stdio_client(params)as(rd,wr):
        async with ClientSession(rd,wr)as client:
            await client.initialize()
            data=unpack(await client.call_tool('project_evidence',{'topic':'frame_runtime'}))
    selected={'scene17_full_three_processors','optimized_DSP_full_route','scene532_entrance_three_processors','scene532_fixed_original_replay'}
    chosen={row['test']:row for row in data['current_route_tests']['jobs']if row['test']in selected}
    assert set(chosen)==selected
    for name in ['scene17_full_three_processors','scene532_entrance_three_processors']:
        assert chosen[name]['status']=='CPU_GPU_DSP_frame_comparison_pass'and not chosen[name]['handle_live']
    assert chosen['optimized_DSP_full_route']['status']=='fresh_DSP_comparison_pass'and not chosen['optimized_DSP_full_route']['handle_live']
    assert chosen['scene17_full_three_processors']['original_warm_frames']==0 and chosen['scene17_full_three_processors']['no_saved_checkpoint']
    assert chosen['scene532_entrance_three_processors']['original_checkpoint_frame']==19270
    result=dict(status='fresh_installed_MCP_current_scene_and_DSP_evidence_pass',recorded_at=datetime.now(timezone.utc).isoformat(),jobs=chosen,native_Chat_verified=False)
    (ROOT/'verification/scene17-full-and-scene532-installed-MCP-current.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({name:dict(status=row['status'],frames=row.get('frames'),handle_live=row['handle_live'])for name,row in chosen.items()}))
if __name__=='__main__':asyncio.run(main())
