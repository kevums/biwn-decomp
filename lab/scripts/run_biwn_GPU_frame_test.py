"""One-command live GPU reconstruction comparison and optional local evidence summary."""
import argparse,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--frames',type=int,choices=[4,60],default=4)
    ap.add_argument('--native-CPU-bridge',action='store_true');ap.add_argument('--native-GPU-bridge',action='store_true');ap.add_argument('--GPU-frame-only',action='store_true');ap.add_argument('--control-bundles',action='store_true');ap.add_argument('--setup-bundles',action='store_true');ap.add_argument('--material-bundles',action='store_true');ap.add_argument('--direction',choices=['none','U'],default='none');ap.add_argument('--with-local-review',action='store_true');args=ap.parse_args()
    core=json.loads((ROOT/'verification/BIWN-regular-GPU-owner-candidate.json').read_text())['core_path']
    candidate=json.loads((ROOT/'verification/renderer-bundle-candidate.json').read_text())
    accepted=json.loads((ROOT/'verification/regular-GPU-renderer-runtime-current.json').read_text())
    assert candidate['library']==accepted['library'] and accepted.get('overlay_libraries'),'Current overlay build lacks accepted runtime proof'
    if args.material_bundles:
        materials=json.loads((ROOT/'verification/material-bundle-candidate.json').read_text())
        accepted_materials=json.loads((ROOT/'verification/material-bundle-progress.json').read_text())
        assert {'none','U'}<=accepted_materials.keys(),'Material movement/control proofs missing'
        checked={x['library']for x in accepted_materials[args.direction]['material_libraries']}
        assert {x['library']for x in materials['overlays']}==checked,'Current material libraries lack accepted runtime proof'
    assert not args.control_bundles or args.material_bundles
    assert not args.setup_bundles or args.control_bundles
    if args.setup_bundles:
        setup=json.loads((ROOT/'verification/setup-bundle-candidate.json').read_text())
        control=json.loads((ROOT/'verification/control-GPU-bundle-candidate.json').read_text())
        checked=json.loads((ROOT/'verification/setup-bundle-progress.json').read_text())
        assert {'none','U'}<=checked.keys(),'Complete movement/control GPU proofs missing'
        assert checked[args.direction]['setup_source']['library']==setup['library'],'Setup library lacks accepted proof'
        assert {x['library']for x in checked[args.direction]['control_libraries']}=={x['library']for x in control['overlays']},'Control libraries lack accepted proof'
    assert not args.GPU_frame_only or args.native_GPU_bridge
    if args.native_GPU_bridge:
        assert args.setup_bundles
        native=json.loads((ROOT/'verification/native-GPU-runtime-current.json').read_text())
        build=json.loads((ROOT/'verification/fast-GPU-bridge-candidate.json').read_text())
        assert native['bridge']==build['library'],'Native GPU bridge lacks accepted proof'
    if args.native_CPU_bridge:
        assert args.native_GPU_bridge
        accepted_CPU=json.loads((ROOT/'verification/native-CPU-1200-current.json').read_text())
        build_CPU=json.loads((ROOT/'verification/fast-CPU-bridge-candidate.json').read_text())
        assert accepted_CPU['CPU_bridge']==build_CPU['library'],'NativeCPU bridge lacks accepted proof'
    stage='native'if args.native_GPU_bridge else'setup'if args.setup_bundles else'control'if args.control_bundles else'material'if args.material_bundles else'renderer'
    out=ROOT/'runs/GPU-frame-launcher'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    print('Normal-frame C CPU and GPU components; original startup, DSP and hardware services remain.',flush=True)
    print('Commands, reports and logs: '+str(out),flush=True);commands=[]
    for mode in ['trace','C']:
        command=[sys.executable,str(ROOT/'scripts/probe_biwn_frame_CPU_owner.py'),'--mode','C','--OP-GPU-mode','C',
                 '--regular-GPU-mode',mode,'--renderer-bundles','--renderer-overlays','--core',core,'--frames',str(args.frames),
                 '--direction',args.direction,'--output',str(out/mode)]
        if args.material_bundles:command.append('--material-bundles')
        if args.control_bundles:command.append('--control-bundles')
        if args.setup_bundles:command.append('--setup-bundles')
        if args.native_CPU_bridge:command+=['--native-CPU-bridge','--extended-CPU']
        if args.native_GPU_bridge:command.append('--native-GPU-bridge')
        if args.GPU_frame_only:command.append('--GPU-frame-only')
        commands.append(dict(mode=mode,command=command));(out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
        print('Running '+mode+' comparison path…',flush=True)
        with (out/(mode+'.log')).open('w')as log:process=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
        commands[-1]['exit_code']=process.returncode;(out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
        if process.returncode:raise SystemExit('Run rejected; inspect '+str(out/(mode+'.log')))
    compare=[sys.executable,str(ROOT/('scripts/record_biwn_material_bundles.py'if args.material_bundles else'scripts/record_biwn_renderer_bundles.py')),'--run-root',str(out)]
    if args.native_GPU_bridge:compare=[sys.executable,str(ROOT/'scripts/record_biwn_fast_frame_test.py'),'--run-root',str(out)]
    elif args.setup_bundles:compare.append('--setup')
    elif args.control_bundles:compare.append('--control')
    process=subprocess.run(compare,capture_output=True,text=True)
    (out/'comparison.log').write_text(process.stdout+process.stderr)
    if process.returncode:raise SystemExit('Exact comparison failed; inspect comparison.log')
    print(process.stdout,flush=True)
    comparison_result=json.loads(process.stdout.strip().splitlines()[-1])
    proof=json.loads(Path(comparison_result['report']).read_text())
    evidence_key='normal_frame_GPU_'+stage+'_component'
    print('Report: '+str(Path(proof['directory'])/'report.json'),flush=True)
    seen=set()
    for root in [ROOT,Path.home()/'.lmstudio/local-ai-lab']:
        p=root/'projects/black-ice-white-noise/analysis/current-session.json'
        if not p.exists():continue
        path=Path(json.loads(p.read_text())['directory'])/'emulator-runtime/summary.json'
        if path in seen:continue
        seen.add(path);data=json.loads(path.read_text());data[evidence_key]=proof
        path.write_text(json.dumps(data,indent=2)+'\n')
    if args.with_local_review:
        question=('Fetch frame_runtime once. Under65words summarize routine_latest: frames, C-owned/original GPU counts, '
                  'frame checks versus omitted GPUinstruction hashes, original startup/DSP/HLE/devices, silence and incompletegame. '
                  'State coordinator integration and SDK summary; no independent verification or newtraining.')
        process=subprocess.run([sys.executable,str(ROOT/'scripts/test_firmware_CD_routing.py'),'--thinking-off','--question',question],capture_output=True,text=True)
        (out/'local-model.log').write_text(process.stdout+process.stderr)
        if process.returncode:print('Comparison passed; local summary failed. See local-model.log.',flush=True)
        else:
            pointer=json.loads((ROOT/'verification/easy-firmware-CD-routing-pointer.json').read_text());protocol=Path(pointer['directory'])/'protocol.json'
            report=json.loads(protocol.read_text());print('Local assistant:\n'+report['results'][0]['answer'],flush=True)
            print('Exact prompts/responses: '+str(protocol),flush=True)
    print('Partial reconstruction; standalone game and all-path GPU/DSP coverage unfinished.',flush=True)
if __name__=='__main__':main()
