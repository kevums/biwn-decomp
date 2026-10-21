"""Repeat the repaired fresh pair with bounded real-call snapshots; no guest edits."""
import hashlib,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save,make_probe
def main():
    parent_path=ROOT/'verification/native-format-selector-deck-pair-current.json';parent=json.loads(parent_path.read_text())
    assert parent['status']=='terminal_fresh_format_selector_deck_pair_classified'
    old=Path(parent['directory']);build=json.loads(Path(parent['build_proof']).read_text());repair=parent['shared_selector_repairs']
    for key,hkey in [('candidate','candidate_sha256'),('control','control_sha256')]:assert sha(repair[key])==repair[hkey]
    out=ROOT/'verification/native-format-live-capture'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    source=old/'format-observer.c';text=source.read_text();text=text.replace('#include <string.h>','#include <string.h>\n#include <sys/stat.h>')
    marker='struct format_pending {unsigned live,kind;uint32_t sp,ret,task;};';assert text.count(marker)==1
    text=text.replace(marker,'struct format_pending {unsigned live,kind;uint32_t sp,ret,task;unsigned ordinal,selected,last_supervisor,supervisor_excursions,supervisor_steps,other_task_steps,first_supervisor_PC;};')
    extension=ROOT/'scripts/format_live_capture_extension.c';marker='static void watch_format(uint32_t pc){';assert text.count(marker)==1
    text=text.replace(marker,extension.read_text()+'\n'+marker)
    marker='    return events?0:1;';assert text.count(marker)==1
    text=text.replace(marker,'    return events?capture_begin(path):1;')
    # Function is defined after begin_observe: declare it before first use.
    text=text.replace('int begin_observe(', 'static int capture_begin(const char *path);\nint begin_observe(')
    marker='format_returns[fp[j].kind]++;fp[j].live=0;';assert text.count(marker)==1
    text=text.replace(marker,'capture_event(0,&fp[j],&value);'+marker)
    marker='  fp[j]=(struct format_pending){1u,pc==0x1b1a8u,sp,rd32(sp),task};';assert text.count(marker)==1
    text=text.replace(marker,"  unsigned kind=pc==0x1b1a8u,ordinal=(unsigned)format_entries[kind];\n  fp[j]=(struct format_pending){.live=1u,.kind=kind,.sp=sp,.ret=rd32(sp),.task=task,.ordinal=ordinal,.selected=selected_call(kind,ordinal)};\n  capture_event(1,&fp[j],&value);")
    marker=' for(unsigned j=0;j<64;j++)if(fp[j].live&&!(value.sr&0x2000u)&&task==fp[j].task){';assert text.count(marker)==1
    addition=''' for(unsigned j=0;j<64;j++)if(fp[j].live){
  unsigned supervisor=!!(value.sr&0x2000u);
  if(supervisor){if(!fp[j].last_supervisor){fp[j].supervisor_excursions++;if(!fp[j].first_supervisor_PC)fp[j].first_supervisor_PC=pc;}fp[j].supervisor_steps++;}
  if(task!=fp[j].task)fp[j].other_task_steps++;
  fp[j].last_supervisor=supervisor;
 }
'''
    text=text.replace(marker,addition+marker)
    marker='    if(events&&fclose(events))errors++;';assert text.count(marker)==1
    text=text.replace(marker,marker+'\n    if(capture_events&&fclose(capture_events))capture_errors++;\n    errors+=capture_errors;')
    observer=out/'observer.c';observer.write_text(text);library=out/'observer.dylib';p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(observer),'-o',str(library)],capture_output=True,text=True);(out/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    probe=out/'fresh-capture-probe.py';probe.write_text(make_probe(ROOT/'scripts/probe_biwn_fresh_CD_boot.py',library,ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi',Path(build['component'])));compile(probe.read_text(),str(probe),'exec')
    inputs=old/'input.json';core=ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source/virtualjaguar_libretro.dylib'
    state=dict(status='running',pid=os.getpid(),directory=str(out),parent_proof=str(parent_path),parent_proof_sha256=sha(parent_path),commands=[],
               additional_guest_RAM_writes=0,checkpoint_restores=0,LLM_calls=0,training_updates=0,whole_game_complete=False,
               source_sha256={str(p):sha(p)for p in [Path(__file__),source,extension,observer,library,probe,inputs,core]})
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-format-live-capture-active.json',state)
    mark();children=[]
    try:
        for lane,disc in [('candidate',repair['candidate']),('control',repair['control'])]:
            cmd=[str(ROOT/'.venv/bin/python'),'-u',str(probe),'--boot','hle','--frames','2600','--core',str(core),'--disc',disc,'--frame-controller-script',str(inputs),'--capture-audio','--no-publish','--output',str(out/lane)]
            log=(out/(lane+'.log')).open('w');child=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT);children.append((lane,child,log));state['commands'].append(dict(lane=lane,pid=child.pid,command=cmd));mark()
        print('PIDs',[p.pid for _,p,_ in children],flush=True)
        codes={}
        for lane,child,log in children:codes[lane]=child.wait();log.close()
        state['exit_codes']=codes;assert not any(codes.values()),codes
        captures={}
        for lane in codes:
            directory=out/lane;report=json.loads((directory/'report.json').read_text());obs=json.loads((directory/'gameplay-observation.json').read_text())
            assert report['executed_frames']==2600 and not obs['errors']and not obs['format_tracking_errors']and obs['format_pending_at_finish']==0
            capture_dir=directory/'gameplay-events.bin-calls';events=[json.loads(line)for line in(capture_dir/'events.jsonl').read_text().splitlines()]
            entries=[e for e in events if e['event']=='entry'];returns=[e for e in events if e['event']=='return'];assert len(entries)==len(returns)>0
            assert [(e['kind'],e['ordinal'])for e in entries]==[(e['kind'],e['ordinal'])for e in returns]
            for e in events:assert(capture_dir/e['ram_file']).stat().st_size==0x200000
            old_report=json.loads((old/lane/'report.json').read_text());fields=['raw_player_X','raw_player_Z','scene_word','player_mode_word','floor_word','video_sha256']
            repeated={k:sum(x[k]!=y[k]for x,y in zip(report['frames'],old_report['frames']))for k in fields}
            captures[lane]=dict(directory=str(capture_dir),selected_pairs=len(entries),kind_counts={str(k):sum(e['kind']==k for e in entries)for k in [0,1]},
                observed_supervisor_excursions=sum(e['supervisor_excursions']for e in returns),calls_with_supervisor_execution=sum(e['supervisor_steps']>0 for e in returns),
                repeat_differences_vs_prior_same_lane=repeated,report_sha256=sha(directory/'report.json'),events_sha256=sha(capture_dir/'events.jsonl'))
        state.update(status='terminal_bounded_real_format_call_capture_complete',captures=captures,
                     scope='New2600frame freshHLE pair using the exact previously repaired discs and same fixed pad schedule. Read-only RAM/CPU snapshots at selected true helper entries/returns; observer returns0. Supervisor excursions are observed execution, not identified IRQ source/cycle-equivalence proof. Offline original/compiled replay remains separate.')
        mark();save(ROOT/'verification/native-format-live-capture-current.json',state);print(json.dumps(captures),flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
