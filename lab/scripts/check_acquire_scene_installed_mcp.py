"""Check installed evidence and fixed initializer candidate tool in a fresh MCP process."""
import asyncio, hashlib, json
from datetime import datetime, timezone
from check_audio_native_mcp import ROOT, RUNTIME, unpack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    proof_pointer=ROOT/'verification/local-scene-initial-setup-devices-checks-current.json'
    before=hashlib.sha256(proof_pointer.read_bytes()).hexdigest()
    source=(ROOT/'projects/black-ice-white-noise/restoration/biwn_scene_initial_setup.c').read_text()
    params=StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),
                                args=[str(RUNTIME/'chat_tools.py')],cwd=str(RUNTIME))
    async with stdio_client(params) as (reader,writer):
        async with ClientSession(reader,writer) as client:
            await client.initialize()
            names=[t.name for t in (await client.list_tools()).tools]
            data={topic:unpack(await client.call_tool('project_evidence',{'topic':topic}))
                  for topic in ['frame_resource_acquire','scene_select','scene_initial_setup','scene_device_initialize','frame_disc_layout']}
            candidate=unpack(await client.call_tool('verify_scene_initial_candidate',{'source':source}))
    assert data['frame_resource_acquire']['cases']==370
    assert data['frame_resource_acquire']['instruction_address_coverage']==[173,173]
    assert data['frame_resource_acquire']['remaining_scripted_helpers']==['0x1b044']
    assert data['scene_select']['cases']==375 and data['scene_select']['linked_instruction_addresses']==262
    assert data['scene_initial_setup']['linked_instruction_addresses']==328
    assert data['scene_initial_setup']['nested_selector_scripted_helpers']==['0x1b044']
    assert data['scene_initial_setup']['top_level_scripted_helpers']==[]
    assert data['scene_device_initialize']['instruction_address_coverage']==[25,25]
    assert data['frame_disc_layout']['modes'][2]['frozen_count']==16
    assert data['frame_disc_layout']['modes'][2]['matching_intervals']==0
    assert candidate['verified'] and candidate['cases']==284 and candidate['native_CPU_cases']==27
    assert candidate['host_guards']==362
    assert before==hashlib.sha256(proof_pointer.read_bytes()).hexdigest()
    report=dict(status='fresh_installed_acquire_scene_evidence_and_candidate_pass',
                recorded_at=datetime.now(timezone.utc).isoformat(),tools=names,topics=data,
                candidate=candidate,accepted_pointer_unchanged=True,native_Chat_verified=False,
                scope='Fresh installed MCP process and fixed candidate tool. No native Chat adoption, new weights or gameplay promotion.')
    (ROOT/'verification/acquire-scene-installed-MCP-current.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],topics=len(data),candidate_cases=candidate['cases'],
                          native_CPU_cases=candidate['native_CPU_cases'],host_guards=candidate['host_guards'])))


if __name__=='__main__':
    asyncio.run(main())
