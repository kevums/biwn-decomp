"""Fresh repaired-disc comparison with C CPU, GPU, DSP and IRQ providers.

The coordinator assembles existing checked providers. No local-model source
authorship or training is attributed to this integration driver.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
from datetime import datetime, timezone

from run_biwn_native_fast_gameplay_route import ROOT, sha, save


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--merchant', action='store_true')
    parser.add_argument('--frames', type=int, default=1600)
    parser.add_argument('--sprint', action='store_true', help='Fresh fixed Up+C gameplay input, with observed locomotion state')
    args = parser.parse_args()
    assert not args.sprint or (not args.merchant and args.frames>=800)
    prior_path = ROOT/'verification'/('native-formatter-C-merchant-pair-current.json' if args.merchant else 'native-formatter-C-fresh-pair-current.json')
    prior = json.loads(prior_path.read_text())
    assert prior['status'] in ['terminal_fresh_C_merchant_pair_equal', 'terminal_fresh_C_formatter_pair_equal']
    template = Path(prior['directory'])/'probe.py'
    assert sha(template) == prior['source_sha256'][str(template)]
    gpu_path = ROOT/'verification/CPU-IRQ-selection-GPU-experimental-candidate.json'
    dsp_path = ROOT/'verification/CPU-IRQ-selection-DSP-experimental-candidate.json'
    gpu = json.loads(gpu_path.read_text())
    dsp = json.loads(dsp_path.read_text())
    core = Path(gpu['required_core_path'])
    assert sha(core) == gpu['required_core_sha256'] == dsp['required_core_sha256']
    out = ROOT/'verification/native-formatter-C-processors'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    runner=out/'runner-as-run.py'
    runner.write_bytes(Path(__file__).read_bytes())
    print(out, flush=True)
    source = template.read_text()
    marker = '        core.BIWNSetCPUExecOwner(gate,0)'
    assert source.count(marker) == 1
    install = f'''
        GPU_source = DSP_source = IRQ_source = None
        if args.CPU_mode == 'C':
            import biwn_fast_GPU_bridge, biwn_DSP_program_router, biwn_CPU_IRQ_select_owner
            GPU_source = biwn_fast_GPU_bridge.install(core,out,'C',False,Path({str(gpu_path)!r}))
            DSP_source = biwn_DSP_program_router.install(core,out,Path({str(dsp_path)!r}))
            IRQ_source = biwn_CPU_IRQ_select_owner.install(core,out)
        def finish_processors():
            return dict(GPU=GPU_source[4]() if GPU_source else None,
                        DSP=DSP_source[3]() if DSP_source else None,
                        IRQ=IRQ_source[4]() if IRQ_source else None)
'''
    source = source.replace(marker, marker+install)
    marker = '            core.retro_run()'
    assert source.count(marker) == 1
    guard = '''
            if GPU_source and (core.BIWNGPURejectedBundleCount() or core.BIWNGPUOriginalBundleCount() or core.BIWNDSPRejectedInstructionCount() or core.BIWNDSPOriginalInstructionCount() or core.BIWNCPUIRQRejectedCount() or core.BIWNCPUInterruptRejectedCount()):
                report['C_processor_backends'] = finish_processors()
                raise RuntimeError('Source processor uncovered/rejected in frame '+str(current_frame))
'''
    source = source.replace(marker, marker+guard)
    marker = '        stats=finish_CPU()'
    assert source.count(marker) == 1
    source = source.replace(marker, "        report['C_processor_backends']=finish_processors()\n"+marker)
    source = source.replace("        report['source_C_execution']=args.CPU_mode=='C'\n", '')
    marker = "        report.update(status='terminal_fresh_libretro_CD_probe'"
    assert source.count(marker) == 1
    source = source.replace(marker, "        report['source_C_execution']=args.CPU_mode=='C'\n"+marker)
    marker='                       CPU_full=full_CPU(),'
    assert source.count(marker)==1
    source=source.replace(marker,"                       locomotion_state=int.from_bytes(ram[0x49cb8:0x49cba],'big'),\n                       held_buttons=int.from_bytes(ram[0x49ba4:0x49ba8],'big'),\n"+marker)
    # The inherited template's scope strings describe the previous CPU-only
    # experiment. Replace them rather than presenting stale provider claims.
    source = source.replace('GPU,DSP,devices,IRQ decisions remainretainedemulator.',
                            'C GPU/DSP/IRQ selection+entry providers installed; original device/IRQ line+ACK/commit/cost/HLE services retained.')
    probe = out/'probe.py'
    compile(source, str(probe), 'exec')
    probe.write_text(source)
    input_path=None
    if args.sprint:
        input_path=out/'input.json'
        save(input_path,dict(windows=[dict(start_frame=600,stop_frame=args.frames+1,buttons=['U','C'])]))
    commands = []
    for lane in ['reference', 'C']:
        old = next(row['command'] for row in prior['commands'] if row['lane'] == lane)
        command = list(old)
        command[2] = str(probe)
        command[command.index('--output')+1] = str(out/lane)
        if not args.merchant:
            command[command.index('--frames')+1] = str(args.frames)
        if input_path:
            command[command.index('--frame-controller-script')+1]=str(input_path)
        commands.append((lane, command))
    dependencies = [runner, prior_path, template, probe, gpu_path, dsp_path, core]
    if input_path:dependencies.append(input_path)
    dependencies += [ROOT/'scripts'/name for name in ['biwn_fast_GPU_bridge.py', 'biwn_DSP_program_router.py', 'biwn_DSP_music_owner.py', 'biwn_CPU_IRQ_select_owner.py', 'biwn_CPU_IRQ_owner.py']]
    dependencies += [ROOT/'verification'/name for name in ['CPU-IRQ-selection-core-experimental-candidate.json', 'CPU-IRQ-bridge-experimental-candidate.json', 'local-CPU-IRQ-selector-author-current.json']]
    dependencies += [Path(gpu[k]) for k in ['library', 'kernel_library']]
    dependencies += [Path(dsp[k]) for k in ['library', 'music_library', 'media_library']]
    for name in ['CPU-IRQ-bridge-experimental-candidate.json', 'local-CPU-IRQ-selector-author-current.json']:
        manifest = json.loads((ROOT/'verification'/name).read_text())
        dependencies.append(Path(manifest['library']))
    state = dict(status='running_fresh_C_processors', pid=os.getpid(), directory=str(out),
                 merchant=args.merchant, sprint=args.sprint, commands=[],
                 source_sha256={str(p):sha(p) for p in dependencies},
                 checkpoint_restores=0, host_guest_RAM_writes=0,
                 scope='Fresh HLE CDI entry; C CPU after4000 plus existing byte-fenced C GPU/DSP and source interrupt selection/entry. Original bootstrap, device/queue/IRQline/ACK/vector resolution/commit/prefetch/cost/HLE/blitter/objectprocessor services remain. No physical-console or standalone proof.',
                 new_training=False, native_Chat_verified=False, default_promoted=False,
                 coordinator_authored_integration=True, new_model_authorship=False,
                 whole_game_complete=False)
    def mark():
        save(out/'protocol.json', state)
        save(ROOT/'verification/native-formatter-C-processors-active.json', state)
    mark()
    children=[]
    try:
        for lane, command in commands:
            log=(out/(lane+'.log')).open('w')
            child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
            children.append((lane,child,log))
            state['commands'].append(dict(lane=lane,pid=child.pid,command=command))
            mark()
        codes={}
        for lane,child,log in children:
            codes[lane]=child.wait()
            log.close()
        state['exit_codes']=codes
        reports={lane:json.loads((out/lane/'report.json').read_text()) for lane in ['reference','C']}
        state['report_sha256']={lane:sha(out/lane/'report.json') for lane in reports}
        if any(codes.values()):
            state.update(status='terminal_fresh_C_processors_child_rejected',
                         child_errors={lane:report.get('errors') for lane,report in reports.items()},
                         C_processor_backends=reports['C'].get('C_processor_backends'))
        else:
            rows={lane:report['frames'] for lane,report in reports.items()}
            assert len(rows['C'])==len(rows['reference']) > 0
            fields=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons']
            comparisons={field:dict(different_frames=sum(a[field]!=b[field] for a,b in zip(rows['reference'],rows['C'])),
                first_different_frame=next((a['frame'] for a,b in zip(rows['reference'],rows['C']) if a[field]!=b[field]),None)) for field in fields}
            backends=reports['C']['C_processor_backends']
            CPU=reports['C']['C_CPU_backend']
            assert CPU['entry_gate']['armed'] and CPU['stats']['steps'] > 0
            assert CPU['stats']['errors']==CPU['counts']['Original']==CPU['counts']['Rejected']==0
            assert backends['GPU']['C_source_instructions'] > 0
            assert backends['GPU']['counts']['Original']==backends['GPU']['counts']['Rejected']==backends['GPU']['stats']['errors']==0
            assert backends['DSP']['owned'] > 0
            assert backends['DSP']['core_counts']['Original']==backends['DSP']['core_counts']['Rejected']==backends['DSP']['errors']==0
            assert backends['IRQ']['core']['Owned'] > 0 and backends['IRQ']['selection']['Owned'] > 0
            assert all(backends['IRQ'][kind][name]==0 for kind in ['core','selection'] for name in ['Original','Rejected'])
            PCM_equal=sha(out/'reference/frontend-PCM.s16le')==sha(out/'C/frontend-PCM.s16le')
            results={lane:dict(frames=len(data),final_navigation=data[-1]['navigation'],
                final_X=data[-1]['raw_player_X'],final_Z=data[-1]['raw_player_Z'],
                scene=data[-1]['scene_word'],mode=data[-1]['player_mode_word'],floor=data[-1]['floor_word'],
                nonzero_audio_samples=reports[lane]['audio']['nonzero_samples']) for lane,data in rows.items()}
            if args.sprint:
                for lane,data in rows.items():
                    results[lane]['recorded_run_state_frames']=sum(row['locomotion_state']==8 and row['held_buttons']&0x102000==0x102000 for row in data)
                    assert results[lane]['recorded_run_state_frames']>0
            if args.merchant:
                for lane,data in rows.items():
                    assert any(row['player_mode_word']==2 and row['floor_word']==2 and row['scene_word']==314 and abs(row['raw_player_X']-12832)<=16 and abs(row['raw_player_Z']-42385)<=16 for row in data)
                    assert results[lane]['mode']==1 and results[lane]['floor']==0 and results[lane]['final_navigation']['outdoor_hold']>=120
            equal=not any(v['different_frames'] for v in comparisons.values()) and PCM_equal
            state.update(status='terminal_fresh_C_processors_equal' if equal else 'terminal_fresh_C_processors_diverged',
                         comparisons=comparisons,frames=len(rows['C']),results=results,
                         C_CPU_backend=CPU,C_processor_backends=backends,audio_PCM_equal=PCM_equal)
        mark()
        save(ROOT/'verification/native-formatter-C-processors-current.json',state)
        print(json.dumps({k:v for k,v in state.items() if k not in ['commands','source_sha256']},indent=2),flush=True)
    except BaseException as error:
        state.update(status='terminal_fresh_C_processors_driver_failure',error=repr(error))
        mark()
        raise


if __name__=='__main__':
    main()
