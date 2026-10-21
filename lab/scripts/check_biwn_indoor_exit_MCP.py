"""Exercise the installed saved-exit planner, latest evidence and PNG over MCP."""
import asyncio
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = Path.home() / '.lmstudio/local-ai-lab'


def unpack(result):
    assert not result.isError
    return json.loads(next(c.text for c in result.content if c.type == 'text'))


async def main():
    expected = json.loads((ROOT / 'verification/building570-exit-route-current.json').read_text())
    scene_path = Path(json.loads((RUNTIME / 'verified-previews/latest-scene.json').read_text())['source_report']).resolve()
    loop_path = ROOT / 'verification/fast-building570-loop-current.json'
    merchant_path = ROOT / 'verification/merchant-gated-full-route-verdict-current.json'
    assert scene_path in [ROOT / 'verification/building570-exit-route-current.json', loop_path, merchant_path]
    scene = json.loads(scene_path.read_text())
    async with asyncio.timeout(45):
        params = StdioServerParameters(command=str(RUNTIME / '.venv/bin/python'),
                                       args=[str(RUNTIME / 'chat_tools.py')], cwd=str(RUNTIME))
        async with stdio_client(params) as (reader, writer):
            async with ClientSession(reader, writer) as client:
                await client.initialize()
                tools = {t.name: t for t in (await client.list_tools()).tools}
                assert tools['plan_checked_indoor_exit'].annotations.readOnlyHint is True
                plan = unpack(await client.call_tool('plan_checked_indoor_exit', {}))
                assert plan['candidates'][0]['plan'] == expected['controller_plan']
                assert plan['source_RAM_sha256'] == expected['source_RAM_sha256']
                assert plan['memory_written'] is plan['buttons_executed'] is plan['live_game_state'] is False
                historical = plan['historical_exit_verification']
                assert historical['status'] == expected['status'] and historical['frames'] == 600
                assert historical['DSP_counts'] == dict(Owned=0, Original=0, Rejected=0)
                status = unpack(await client.call_tool('project_evidence', {'topic': 'status'}))
                latest = status['latest_checked_scene_integration']
                assert latest['proof'] == str(scene_path)
                assert latest['whole_game_complete'] is False and latest['native_keyboard_verified'] is False
                if scene_path == merchant_path:
                    assert latest['continuous_merchant_elevator_outdoor_chain_verified'] and latest['frames'] == 24738
                    assert latest['initial_checkpoint_restored'] is False and latest['all_comparison_gates_passed']
                    assert latest['audio']['total_nonzero_channel_samples'] == 1609546
                elif scene_path == loop_path:
                    assert latest['no_intermediate_restore'] and latest['frames'] == 4600
                else:
                    assert latest['source_publication'] == expected['source_publication']
                image = await client.call_tool('show_latest_checked_scene', {})
                assert not image.isError
                pixels = base64.b64decode(next(c.data for c in image.content if c.type == 'image'))
                assert pixels == (Path(scene['directory']) / 'C/final-frame.png').read_bytes()
                caption=next(c.text for c in image.content if c.type == 'text')
                assert ('Captured PCM includes nonzero audio' if scene_path == merchant_path else 'PCM was silent') in caption
                interrupts = unpack(await client.call_tool('project_evidence', {'topic': 'interrupts'}))
                irq = interrupts['full_route_verdict']
                assert irq['frames'] == 24738 and irq['all_comparison_gates_passed'] is True
                assert irq['source_IRQ_selection'] == dict(Owned=443751355, Original=0, Rejected=0)
                assert irq['source_IRQ_entry'] == dict(Owned=147257, Original=0, Rejected=0)
                assert irq['continuous_merchant_elevator_outdoor_chain_verified'] is False
                merchant=interrupts['merchant_gated_full_route_verdict']
                assert merchant['continuous_merchant_elevator_outdoor_chain_verified'] and merchant['source_IRQ_entry']['Owned'] == 148817
                attack_result=unpack(await client.call_tool('project_evidence', {'topic': 'attack_effect'}))
                attack=attack_result['readable_natural_invocation_replay']
                assert attack['natural_calls'] == 17 and attack['damage_calls'] == 2 and attack['observer_inert']
                assert attack['concurrent_OP_effects_supplied'] and attack['high_level_component_in_frame_runtime'] is False
                live_attack=attack_result['live_CPU_compatible_attack_body']
                assert live_attack['native_fixture_cases']==20480 and live_attack['coordinator_repair_sites']==15
                assert live_attack['CPU_compatible_component_in_frame_runtime'] is True
                assert live_attack['high_level_attack_effect_API_used'] is live_attack['concurrent_OP_effects_supplied'] is False
                assert [case['attack_calls']for case in live_attack['cases']]==[9,8]
                assert [case['reached_instruction_locations']for case in live_attack['cases']]==[35,35]
                assert live_attack['full_cold_24738_route_with_this_body_verified'] is False
                optional_loop=status['separate_readable_scene_stream']['source_checkpoint_building_loop']
                assert optional_loop['frames']==4600 and optional_loop['CPU_instructions']==80750042
                assert optional_loop['original_checkpoint_restored'] is False and optional_loop['no_intermediate_restore']
                assert optional_loop['source_checkpoint']['origin']=='verified_source_execution'
                assert optional_loop['inherited_program_repair_bytes']==18 and optional_loop['new_program_repair_applied'] is False
                assert optional_loop['source_IRQ_entry']==dict(Owned=27579,Original=0,Rejected=0)
                assert optional_loop['attack_calls_in_this_route']==0 and optional_loop['raw_failed_checks']==['DSP_owned_positive']
                assert optional_loop['optional_O_preview']['default_P_changed'] is False
                route532=status['separate_readable_scene_stream']['source_checkpoint_route532']
                assert route532['frames']==6000 and route532['CPU_instructions']==104663679
                assert route532['final_state']==dict(mode=2,scene=532)
                assert route532['source_checkpoint']['origin']=='verified_source_execution'
                assert route532['inherited_program_repair_bytes']==18 and route532['new_program_repair_applied'] is False
                assert route532['source_IRQ_entry']==dict(Owned=35973,Original=0,Rejected=0)
                assert route532['source_IRQ_selection']==dict(Owned=104663679,Original=0,Rejected=0)
                assert route532['GPU_source_instructions']==2906581963 and route532['attack_calls']==0
                assert route532['raw_failed_checks']==['DSP_owned_positive'] and route532['DSP_counts']==dict(Owned=0,Original=0,Rejected=0)
                assert route532['verified_image']['sha256']==hashlib.sha256((RUNTIME/'verified-previews/source-checkpoint-building532.png').read_bytes()).hexdigest()
                unmodified=status['separate_readable_scene_stream']['source_owned_unmodified_merchant']
                assert unmodified['frames']==23538 and unmodified['CPU_instructions']==395449715
                assert unmodified['repair_bytes']==0 and unmodified['initial_checkpoint_restored'] is False
                assert unmodified['all_comparison_gates_passed'] and unmodified['source_CPU_compatible_attack_calls']==8
                continuations=status['separate_readable_scene_stream']['source_merchant_continuations']
                assert continuations['inherited_program_repair_bytes']==0 and continuations['original_checkpoint_restored'] is False
                assert [case['attack_calls']for case in continuations['cases']]==[9,8,0]
                assert [case['continuation_repair_bytes']for case in continuations['cases']]==[0,0,18]
                assert [case['raw_failed_checks']for case in continuations['cases']]==[['DSP_owned_positive']]*3
                primary=status['separate_readable_scene_stream']['primary_source_preview']
                assert primary['default_P_changed'] is True
                assert primary['source_checkpoint']['origin']=='verified_source_execution'
                assert primary['source_checkpoint']['source_frame']==23538
                assert primary['inherited_repair_bytes']==0 and primary['post_restore_repair_bytes']==56
                assert primary['Deck_mail_retention']['mail_message_calls']==1
                assert [case['continuation_repair_bytes']for case in primary['same_profile_gameplay']]==[56,56,56]
                assert primary['bounded_headless_measurement']['frames']==600
                assert primary['bounded_headless_measurement']['native_window_FPS_verified'] is False
    for name in ['chat_tools.py', 'biwn_indoor_exit_planner.py', 'biwn_doorway_planner.py', 'assistant_chat.py']:
        assert (ROOT / name).read_bytes() == (RUNTIME / name).read_bytes()
    report = dict(status='fresh_installed_MCP_indoor_plan_latest_evidence_and_image_pass',
                  recorded_at=datetime.now(timezone.utc).isoformat(),
                  planner=plan, latest_checked_scene=latest, IRQ_full_route_verdict=irq,
                  merchant_gated_full_route_verdict=merchant, readable_natural_invocation_replay=attack,
                  live_CPU_compatible_attack_body=live_attack,
                  source_checkpoint_optional_loop=optional_loop,
                  additional_source_checkpoint_route532=route532,
                  unmodified_source_merchant=unmodified, unmodified_source_merchant_continuations=continuations,
                  primary_source_preview=primary,
                  image_sha256=hashlib.sha256(pixels).hexdigest(), installed_modules_equal=True,
                  native_Chat_verified=False, whole_game_complete=False,
                  scope='Fresh stdio connection through the installed minimal MCP interpreter. Verifies registered tool, saved-plan provenance, current status selection and exact PNG delivery. No inference, native Chat display or live controller action in this check.')
    (ROOT / 'verification/indoor-exit-MCP-current.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'])


if __name__ == '__main__':
    asyncio.run(main())
