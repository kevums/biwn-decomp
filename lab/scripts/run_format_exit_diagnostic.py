"""Repeat both unmodified adaptive routes with an extra read-only C observer."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,subprocess
from run_biwn_native_fast_gameplay_route import ROOT,sha,save


def read(path):return json.loads(Path(path).read_text())


def main():
    parent_path=ROOT/'verification/native-format-optimized-long-route-current.json'
    parent=read(parent_path)
    assert parent['status']=='terminal_fresh_base_optimized_adaptive_routes_classified'
    old=Path(parent['directory']);probe=old/'fresh-route.py';observer=old/'resource-observer.c'
    assert sha(probe)==parent['source_sha256'][str(probe)]
    assert sha(observer)==parent['source_sha256'][str(observer)]
    out=ROOT/'verification/native-format-exit-diagnostic'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True);print(out,flush=True)
    extension=ROOT/'scripts/format_exit_diagnostic_extension.c'
    source=observer.read_text()
    point='int begin_observe(const void *memory,read_cpu_fn reader,int selected,'
    assert source.count(point)==1
    # rd16/rd32 and the CPU reader are defined above this insertion.
    source=source.replace(point,extension.read_text()+'\n'+point)
    point='    payload=code;payload_size=length;events=fopen(path,"wb");'
    assert source.count(point)==1
    source=source.replace(point,'    if(snprintf(diagnostic_prefix,sizeof(diagnostic_prefix),"%s",path)<0)return 1;\n'+point)
    point='int32_t observe(uint32_t pc) {\n'
    assert source.count(point)==1
    source=source.replace(point,point+'    diagnose_exit(pc);\n')
    point='    if(events&&fclose(events))errors++;'
    assert source.count(point)==1
    source=source.replace(point,'    if(diagnostic_file&&fclose(diagnostic_file))errors++;\n'+point)
    src=out/'resource-observer.c';src.write_text(source);library=out/'resource-observer.dylib'
    compiled=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(src),'-o',str(library)],capture_output=True,text=True)
    (out/'compile.log').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0,compiled.stderr
    lines=probe.read_text().splitlines(keepends=True)
    changes=[]
    for i,line in enumerate(lines):
        if line.startswith('        observer=c.CDLL('):
            changes.append(i+1);lines[i]='        observer=c.CDLL('+repr(str(library))+')\n'
    assert len(changes)==1
    derived=out/'fresh-route.py';derived.write_text(''.join(lines));compile(derived.read_text(),str(derived),'exec')
    state=dict(status='running_fresh_exit_diagnostic_pair',pid=os.getpid(),directory=str(out),
               parent=str(parent_path),parent_sha256=sha(parent_path),children=[],commands=[],
               game_source_or_disc_changes=False,controller_policy_changed=False,
               fresh_boot=True,checkpoint_restores=0,guest_RAM_writes=0,observer_replaces_instructions=False,
               native_Chat_verified=False,LLM_calls=0,training_updates=0,whole_game_complete=False,
               source_sha256={str(p):sha(p)for p in [Path(__file__),extension,probe,observer,derived,src,library]})
    for path,digest in parent['source_sha256'].items():
        assert sha(path)==digest,path
        state['source_sha256'][path]=digest

    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-format-exit-diagnostic-active.json',state)
    mark();children=[]
    try:
        for command in parent['commands']:
            lane=command['lane'];cmd=list(command['command'])
            assert cmd[2]==str(probe)
            cmd[2]=str(derived)
            cmd[cmd.index('--output')+1]=str(out/lane)
            # Exact previous ordinary inputs/criteria; no checkpoint or toggled
            # NPC/media state. Only host observation differs.
            log=(out/(lane+'.log')).open('w')
            child=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT)
            children.append((lane,child,log))
            state['children'].append(dict(lane=lane,pid=child.pid,status='running'))
            state['commands'].append(dict(lane=lane,command=cmd));mark()
        print('PIDs',[p.pid for _,p,_ in children],flush=True)
        results={}
        for lane,child,log in children:
            code=child.wait();log.close()
            next(x for x in state['children']if x['lane']==lane).update(status='terminal',exit_code=code);mark()
            assert code==0,(lane,code)
            report=read(out/lane/'report.json');prior=read(old/lane/'report.json')
            fields=['raw_player_X','raw_player_Z','player_mode_word','floor_word','scene_word','video_sha256','cumulative_nonzero_audio_samples']
            assert len(report['frames'])==len(prior['frames'])
            differences={k:sum(a[k]!=b[k]for a,b in zip(report['frames'],prior['frames']))for k in fields}
            assert not any(differences.values()),(lane,differences)
            assert all(a['navigation']==b['navigation']for a,b in zip(report['frames'],prior['frames']))
            assert report['audio']['nonzero_samples']==prior['audio']['nonzero_samples']
            obs=read(out/lane/'gameplay-observation.json');assert obs['errors']==obs['copy_errors']==obs['repair_code_errors']==0
            records=[json.loads(line)for line in (out/lane/'gameplay-events.bin.diagnostic.jsonl').read_text().splitlines()]
            snapshots={r['RAM']:sha(r['RAM'])for r in records if 'RAM'in r}
            results[lane]=dict(executed_frames=report['executed_frames'],prior_selected_frame_differences=differences,
                               navigation_and_buttons_repeat_exactly=True,diagnostic_records=len(records),
                               snapshots_sha256=snapshots,report_sha256=sha(out/lane/'report.json'),
                               diagnostic_sha256=sha(out/lane/'gameplay-events.bin.diagnostic.jsonl'),
                               media_requests=[r for r in records if r['pc']==0x1c9e8],
                               actor3_media_returns=[r for r in records if r['pc']==0x131c8])
        state.update(status='terminal_fresh_exit_diagnostic_pair_repeats_prior_routes',results=results);mark()
        save(ROOT/'verification/native-format-exit-diagnostic-current.json',state)
        print(json.dumps({lane:{k:v for k,v in r.items()if k not in ['media_requests','actor3_media_returns','snapshots_sha256']}for lane,r in results.items()}),flush=True)
    except BaseException as error:
        state.update(status='terminal_failed',error=repr(error));mark();raise


if __name__=='__main__':main()
