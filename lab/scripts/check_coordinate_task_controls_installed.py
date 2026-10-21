"""Install updated retrieval glue, check fresh MCP and exercise real menu1."""
import argparse
import asyncio
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT = Path(__file__).resolve().parents[1]
RUNTIME = Path.home() / '.lmstudio/local-ai-lab'
def save(path, value): Path(path).write_text(json.dumps(value,indent=2)+'\n')
def unpack(result):
    assert not result.isError
    return json.loads('\n'.join(item.text for item in result.content if item.type=='text'))

async def mcp_check(out,flow_mode=False,yield_mode=False,clocked_mode=False,native_mode=False):
    params=StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools.py')],cwd=str(RUNTIME))
    async with stdio_client(params) as (reader,writer):
        async with ClientSession(reader,writer) as client:
            await client.initialize()
            evidence=unpack(await client.call_tool('project_evidence',{'topic':'input_dispatch'}))
    task=evidence['coordinate_task_controls_linkage']; natural=evidence['natural_coordinate_gameplay']
    assert task['cases']==2086 and task['native_cases']==18 and task['coordinate_remaining_fixture_helper_count']==2
    assert task['coordinate_remaining_fixture_helpers']==['0xdf60','0x20f78'] and not task['live_frame_runtime_changed']
    assert task['initial_raw_model_source_accepted'] is False and task['coordinator_edited_generated_repair'] is False
    assert natural['total_independent_continuation_frames']==3400 and natural['inherited_repair_bytes']==18
    assert not natural['readable_high_level_coordinate_API_in_live_frames']
    if flow_mode:
        flow=evidence['resumable_coordinate_flow'];linked=evidence['linked_resumable_coordinate_controls']
        assert flow['cases']==147 and flow['no_internal_polling_loop_or_callbacks'] and not flow['high_level_API_live_frame_runtime_changed']
        assert linked['cases']==2086 and linked['verification_driver_is_synchronous'] and not linked['actual_Jaguar_context_switch']
    report=dict(status='fresh_installed_MCP_task_controls_and_natural_scope_match',recorded_at=datetime.now(timezone.utc).isoformat(),
        task_controls=task,natural_coordinate_gameplay=natural,native_Chat=False,new_training=False)
    if flow_mode:report.update(resumable_coordinate_flow=flow,linked_resumable_coordinate_controls=linked)
    if yield_mode:
        bridge=evidence['task_owned_coordinate_yield'];captured=evidence['captured_coordinate_scheduler']
        assert bridge['guard_count']==77 and bridge['pending_observations']==17
        assert bridge['completed_once'] and bridge['native_snapshots_supplied'] and not bridge['actual_live_frame_installation']
        assert captured['matched_transitions']==17 and captured['excluded_interrupt_transitions']==1 and captured['supplied_OP_writebacks']==24
        report.update(task_owned_coordinate_yield=bridge,captured_coordinate_scheduler=captured)
    if clocked_mode:
        clocked=evidence['clocked_native_coordinate_request_backend']
        assert clocked['actual_other_source_task_body_contexts']==17 and clocked['actual_source_IRQ_entries']==5
        assert clocked['monitored_source_CPU_instructions']==13883 and clocked['attach_guard_count']==20
        assert not clocked['whole_logical_coordinate_engine_in_frames']and clocked['native_boundary_request']
        assert clocked['intermediate_task_CPU_or_RAM_transplants']==clocked['test_supplied_MMIO_results']==clocked['test_supplied_OP_writebacks']==clocked['test_supplied_firmware_ABI_outputs']==0
        assert clocked['ownership']['inherited_repair_bytes']==18 and clocked['ownership']['DSP_inactive_qualified']
        report['clocked_native_coordinate_request_backend']=clocked
    if native_mode:
        native=evidence['native_M68000_button_digit'];toolchain=evidence['native_m68k_toolchain']
        assert native['cases']==5151 and native['binary_bytes']==132 and native['full_registers_verified']==16
        assert native['CCR_input_states']==32 and native['caller_saved_registers_and_CCR_verified']
        assert native['D1_original_mask_restored']and native['guided_model_repair']and not native['coordinator_edited_model_source']
        assert not native['bootable_Jaguar_CD_image']and not native['native_game_frame_integration_verified']
        assert toolchain['status']=='terminal_toolchain_smoke_pass'and toolchain['smoke_cases']==64
        report.update(native_M68000_button_digit=native,native_m68k_toolchain=toolchain)
    name='native-button-installed-MCP-current.json' if native_mode else 'clocked-coordinate-installed-MCP-current.json' if clocked_mode else 'coordinate-yield-installed-MCP-current.json' if yield_mode else 'coordinate-flow-installed-MCP-current.json' if flow_mode else 'coordinate-task-controls-installed-MCP-current.json'
    save(out/'MCP.json',report);save(ROOT/'verification'/name,report)
    return report

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--flow',action='store_true');parser.add_argument('--yield-bridge',action='store_true');parser.add_argument('--clocked',action='store_true');parser.add_argument('--native',action='store_true');args=parser.parse_args()
    prefix='native-button-menu' if args.native else 'clocked-coordinate-menu' if args.clocked else 'coordinate-yield-menu' if args.yield_bridge else 'coordinate-flow-menu' if args.flow else 'coordinate-task-controls-menu'
    out=ROOT/'verification'/prefix/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True);print(out,flush=True)
    # Native plugin invokes its workspace helper directly; the installed
    # lightweight Terminal runtime has no scripts directory.
    for name in ['chat_tools.py','assistant_chat.py']:
        shutil.copy2(ROOT/name,RUNTIME/name)
    for name in ['coordinate-task-controls-current.json','task-gates-current.json','natural-coordinate-gameplay-current.json','coordinate-flow-current.json','coordinate-task-controls-flow-current.json','coordinate-services-current.json','coordinate-yield-current.json','natural-coordinate-scheduler-current.json','clocked-coordinate-yield-current.json','coordinate-yield-attach-current.json']:
        shutil.copy2(ROOT/'verification'/name,RUNTIME/'verification'/name)
    if args.native:
        for name in ['native-button-digit-current.json','native-button-full-ABI-current.json','m68k-toolchain-current.json']:shutil.copy2(ROOT/'verification'/name,RUNTIME/'verification'/name)
    asyncio.run(mcp_check(out,args.flow,args.yield_bridge,args.clocked,args.native))
    question=('How far has coordinate entry progressed? In under140words distinguish natural gameplay from readable C linkage. '
        'Give the latest test counts, who wrote task pause/resume, remaining external services and whether the readable API runs in live frames.')
    if args.flow:
        question=('What changed in resumable coordinate entry, and does it now switch Jaguar tasks or run in live frames? '
            'In under120words explain pending requests, what was checked, who wrote it and what remains.')
    if args.yield_bridge:
        question=('What changed in resumable coordinate entry task switching? In under120words explain who wrote it, '
            'the pending request, latest scheduler/bridge checks, supplied snapshots/display effects and live-frame limitations.')
    if args.clocked:
        question=('What does the clocked coordinate-entry task backend now prove? In under140words explain who wrote it, '
            'how pending work resumes, the latest execution/guard counts, inherited repairs, remaining providers and whether the whole logical caller runs in frames.')
    if args.native:
        question=('Can we recompile anything for the same console yet? In under110words say which routine was built, '
            'its test counts and execution model, who wrote the model part, and what remains before a bootable game.')
    launcher=RUNTIME/'Start Local AI.command'
    started=time.monotonic();prior=set((ROOT/'runs').glob('ask-*-game'))
    with (out/'menu.log').open('w') as log:
        child=subprocess.Popen(['/bin/zsh',str(launcher)],stdin=subprocess.PIPE,stdout=log,stderr=subprocess.STDOUT,text=True)
        state=dict(status='running',question=question,child_pid=child.pid,directory=str(out),launcher=str(launcher),native_Chat=False,new_training=False)
        save(out/'protocol.json',state);save(ROOT/'verification'/(prefix+'-active.json'),state)
        child.communicate('1\n'+question+'\n/quit\n')
    state.update(status='terminal_pending_source_review',exit_code=child.returncode,wall_seconds=time.monotonic()-started)
    runs=set((ROOT/'runs').glob('ask-*-game'))-prior
    assert child.returncode==0 and len(runs)==1
    run=runs.pop();state['run']=str(run)
    protocol=json.loads((run/'session.json').read_text());state['turn']=protocol['turns'][0]
    save(out/'protocol.json',state);save(ROOT/'verification'/(prefix+'-current.json'),state)
    save(ROOT/'verification'/(prefix+'-active.json'),state)
    print(json.dumps(dict(status=state['status'],run=str(run),seconds=state['wall_seconds'])),flush=True)

if __name__=='__main__':main()
