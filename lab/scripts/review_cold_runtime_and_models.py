"""Review actual moved-runtime tools and copied-weight loading separately from quality."""
import json
import re
import shutil
import subprocess
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save


def read(p):return json.loads(Path(p).read_text())


def main():
    v=ROOT/'verification';cold=read(v/'cold-runtime-move-current.json');package=Path(cold['package'])
    calls=read(Path(cold['directory'])/'MCP-attempt-v1/MCP-protocol.json');boundaries=read(v/'cold-runtime-boundaries-current.json');models=read(v/'cold-copied-model-inference-current.json')
    assert calls['failed_calls']==0 and calls['tool_count']==18 and calls['calls_completed']==7
    assert boundaries['status']=='terminal_cold_moved_runtime_boundaries_pass'and len(boundaries['negative_controls'])==4
    assert cold['verified_weight_shards']==10 and cold['verified_model_files']==39
    assert models['completed_predictions']==2 and models['default_model_restored']and models['temporary_links_removed']and models['temporary_definitions_removed']
    out=v/'cold-runtime-model-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    deps={}
    def bind(p,copy=False):
        p=Path(p).resolve();digest=sha(p)
        if copy or not p.is_relative_to(ROOT):
            import hashlib
            target=out/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,target);p=target
        deps[str(p)]=digest
    for name,obj in [('cold-copy.json',cold),('MCP-calls.json',calls),('boundaries.json',boundaries),('configured-models.json',models)]:
        save(out/name,obj);bind(out/name)
    for p in[package/'restore-layout.json',package/'path-repair-receipt.json',package/'index-repair-receipt.json',package/'runtime/portable_runtime_paths_v3.py',package/'runtime/sitecustomize.py',package/'runtime/portable_chat_tools_v3.py',package/'Restore Local AI Lab.command',package/'repair_copied_runtime.py',package/'repair_copied_indexes.py']:
        bind(p,copy=True)
    for p,h in cold['source_sha256'].items():assert sha(p)==h,p;bind(p,copy=True)
    for p,h in boundaries['source_sha256'].items():assert sha(p)==h,p;bind(p,copy=True)
    audits=[]
    for p in package.glob('path-audit-*.json'):
        a=read(p)
        if a['allowed_restore_root']==str(package):
            audits.append(dict(pid=a['pid'],denied=len(a['denied']),restored_paths=len(a['restored_paths'])));bind(p,copy=True)
    assert sum(a['denied']for a in audits)==3
    runs=[]
    for p in sorted((ROOT/'runs').glob('cold-copied-model-inference-*/protocol.json')):
        obj=read(p)
        if obj.get('package')==str(package):runs.append((p,obj))
    raw=next((p,obj)for p,obj in runs if obj.get('completed_predictions')==2 and obj.get('results')and not obj.get('temporary_definitions_removed'))
    checks=[]
    for role in['researcher','reviewer']:
        before=read(Path(raw[1]['directory'])/role/'response.json');after=read(Path(models['directory'])/role/'response.json')
        assert not before['text'].strip()and before['usage']['completion_tokens_details']['reasoning_tokens']==399
        assert after['text'].strip()and after['request'].get('reasoning')=='off'and after['usage']['completion_tokens_details']['reasoning_tokens']==0
        sentences=len(re.findall(r'[.!?](?:\s|$)',after['text']))
        checks.append(dict(role=role,raw_seconds=before['seconds'],configured_seconds=after['seconds'],words=len(after['text'].split()),sentences=sentences,requested_two_sentences_met=sentences==2))
    assert checks[0]['sentences']==2 and checks[1]['sentences']==3
    for p,obj in runs:
        bind(p,copy=True)
        for name in['prompts-and-responses.txt','temporary-resource-bindings.json','restored-daily-loaded.json']:
            path=p.parent/name
            if path.exists():bind(path)
        for path in p.parent.rglob('response.json'):bind(path)
        for path in p.parent.rglob('request.json'):bind(path)
    bind(ROOT/'scripts/run_copied_model_inference.py');bind(ROOT/'scripts/run_copied_model_inference_v2.py');bind(ROOT/'scripts/run_copied_model_inference_v3.py')
    inventory=read(Path(read(v/'relocated-model-copy-current.json')['directory'])/'frozen-inventory.json')
    for name in['advertising-qwen38','advertising-reviewer-experimental']:
        p=package/'lmstudio-home/hub/models/local'/name/'model.yaml';expected=next(row['sha256']for row in inventory if row['target_home_relative']=='.lmstudio/hub/models/local/'+name+'/model.yaml')
        assert sha(p)==expected;bind(p,copy=True)
    loaded=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],text=True));assert len(loaded)==1 and loaded[0]['modelKey']=='local/advertising-qwen38'and loaded[0]['contextLength']==32768
    save(out/'current-daily-loaded.json',loaded);bind(out/'current-daily-loaded.json')
    report=out/'review.txt'
    report.write_text('COLD PACKAGE RESTORE AND COPIED MODEL INFERENCE\n\n'
        f'Actual package cloned outside the workbench to:{package}\n8,080files/14symlinks,50,756,643,153logicalbytes. Copied bundledPython rebuilt the venv path, relativePythonlink and MCPentry; mutable game/advertising index source columns rebased with backups. Original origin/source/evidencebytes unchanged.\n\n'
        'The moved existing18toolMCP registers; seven toolkinds return correct outputs,includingactualnativeCPUworker and inventoryimage. Current-parent/worker audits are separate from copied historicalaudits. Copied evidence corruption, rawoldworkbench/runtime reads and symlinkback reject; restored exactbytes. No originfallback in these guarded tests. Samehost only; hook is not a general security sandbox.\n\n'
        'Both actual copied dailybase and trainedstep8Reviewer weights load through existing LMStudio using temporarylocal model directory links; bindings record actual resolved packagepaths.39modelresources/10shards verified against frozen hashes after coldcopy. First preparation used the wrong inventorylabel and ran0predictions; retained. Rawdirectory profile then loaded bothmodels but spent399tokens on reasoning and returned0finalwords at17.32/18.67s. This was a failed final-output test.\n\n'
        'Binding the copied model definitions,withtheir customthinkingdefaults,to the copiedweightresources yields finalresponses at2.61/2.85s withreasoningoff/0reasoningtokens; model load5.43/6.07s,8Kcontext/1worker. Same two prompts and copiedweights; this is configuration/loadability evidence,not newtraining or a model-quality comparison. Temporarylinks/definitionsremoved; originaldaily27Brestored32K/1worker. ActualSDKcontrolclient was the originalworkbench; SDK/fullCLI workflows have not been restored to the copiedPythonenvironment.\n\n'
        'Output scope: hypothetical supplied study,not a publication or heldoutbenchmark. Researcher correctly distinguishes assignment/measurement but says the design supports a causalclaim thatdisclosureaffects liking without results; revise wording to designcanidentifyaneffect,notproofaneffectexists. Reviewer correctlyrejectsmeasured-aversioncausality and inventedresults,butreturns3sentenceswhere2requested. Thus loading/finalgenerationverified; broadresearch/teaching/taskquality and format reliability are not established.\n\n'
        'No nativeChat-window demonstration, qualitygain, independentmultiagentreview, newoptimizersteps, offmachinerestore or futurehardwareverification. Full18toolbehavior/toolchain/training/sourcebuild/portableCLIlaunchers/onboarding remain pending. Copiedcanonicalstatussnapshot is26,220,not live28,380 or newdevelopment28,448.\n\n'+json.dumps(checks,indent=2)+'\n')
    bind(report);bind(Path(__file__))
    result=dict(status='terminal_cold_moved_runtime_and_copied_models_reviewed_partial_restore',directory=str(out),report=str(report),package=str(package),cloned_files=8080,preserved_symlinks=14,logical_bytes=cold['logical_bytes'],model_files_verified=39,weight_shards_verified=10,registered_tools=18,tested_tool_kinds=7,boundary_controls=4,origin_fallback=False,copied_model_loads=2,copied_model_final_responses=2,actual_predictions=4,configured_prediction_seconds=[2.61,2.85],raw_profile_final_responses=0,output_checks=checks,default_model_restored=True,temporary_bindings_removed=True,restored_SDK_or_full_CLI_workflows=False,whole_workbench_restored=False,all_tools_verified=False,native_Chat_verified=False,off_machine_verified=False,future_hardware_verified=False,new_training=False,model_quality_gain_demonstrated=False,dependencies_sha256=deps,scope=__doc__)
    save(out/'protocol.json',result);save(v/'cold-runtime-model-reviewed-current.json',result)
    print(json.dumps({k:result[k]for k in['status','tested_tool_kinds','copied_model_loads','copied_model_final_responses','default_model_restored']}))


if __name__=='__main__':main()
