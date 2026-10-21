"""Read-only scene/provider timing trace; compare replay hashes to prior prefix."""
import argparse,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

WATCH=r'''
/* Host-only trace. No guest stores, CPU ownership, deadlines or return edits. */
static FILE *tt_file;
static unsigned tt_errors,tt_events;
int timing_trace_begin(const char *path){tt_file=fopen(path,"w");return !tt_file;}
static void tt_watch(uint32_t pc){
 if(frame<370u||frame>390u)return;
 const uint32_t points[]={TT_POINTS};unsigned selected=0;
 for(unsigned i=0;i<sizeof(points)/sizeof(points[0]);i++)selected|=pc==points[i];
 if(!selected)return;
 if(!tt_file){tt_errors++;return;}
 struct cpu c;read_cpu(&c);uint32_t task=rd32(0xc0920u),delta=task-0xc0928u;
 unsigned valid=delta<0x19400u&&!(delta&1023u);uint32_t f=valid?TT_ARENA+delta+144u:0u;
 uint32_t ret=c.r[15]<=0x1ffffcu?rd32(c.r[15]):0u;
 uint32_t ctrl=mb_gpu_read?mb_gpu_read(0xf03200u,0):0u;
 uint32_t ack=mb_gpu_read?mb_gpu_read(0xf03204u,0):0u;
 if(fprintf(tt_file,"{\"frame\":%u,\"instruction_ordinal\":%llu,\"pc\":%u,\"task\":%u,\"physical_SP\":%u,\"physical_SR\":%u,\"physical_return\":%u,\"logical_frame_valid\":%u,\"logical_active\":%u,\"logical_pc\":%u,\"logical_return\":%u,\"GPU_ctrl\":%u,\"GPU_ack\":%u}\n",frame,(unsigned long long)steps,pc,task,c.r[15],c.sr,ret,valid,valid?rd32(f+114u):0u,valid?rd32(f+68u):0u,valid?rd32(f+110u):0u,ctrl,ack)<0)tt_errors++;
 tt_events++;
}
int32_t observe(uint32_t pc){tt_watch(pc);return tt_prior_observe(pc);}
int timing_trace_finish(void){if(tt_file){tt_errors+=fclose(tt_file)!=0;tt_file=0;}return tt_errors||!tt_events;}
'''

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--control',action='store_true');args=ap.parse_args();lane='control'if args.control else'candidate'
    jp=V/f'record-strides-fixed-prefix-v1-{lane}-current.json';j=read(jp)
    assert j['status']=='terminal_fixed_prefix_boundary_checked_measurement_not_route_acceptance'
    for p,h in j['source_sha256'].items():assert sha(p)==h,p
    b=read(V/'native-record-strides-disc-build-v1-current.json');symbols=b['shared_Deck_symbols']
    points={0x17e0e,0x17f10,0x17f12,0x17f14,0xe098,0xe220,0xe3e0,0xe03a,0x185b2}
    points.update(symbols[k]for k in ['biwn_v4_scene','biwn_v4_scene_return','biwn_v4_scene_helper_return','biwn_v4_capture_scene_record_copy','biwn_v4_capture_scene_record_matrix','biwn_v33_records_begin','biwn_v33_records_end'])
    prior=Path(j['directory']);out=V/'record-strides-timing-trace-v1'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')+'-'+lane);out.mkdir(parents=True)
    old=(prior/'observer.c').read_text();anchor='int32_t observe(uint32_t pc){r33_watch(pc);return r33_retained_observe(pc); }';assert old.count(anchor)==1
    source=old.replace(anchor,anchor.replace('int32_t observe','static int32_t tt_prior_observe'))+'\n'+WATCH.replace('TT_POINTS',','.join(str(x)+'u'for x in sorted(points))).replace('TT_ARENA',str(b['deck_arena_address'])+'u')
    cfile=out/'observer.c';cfile.write_text(source);lib=out/'observer.dylib'
    # Reuse the same direction shadow source and all old monitors without edits.
    legacy=read(V/'native-scene17-wait-fresh-v2-control-current.json');direction=Path(legacy['directory'])/'direction-shadow-model.c'
    q=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(cfile),str(direction),'-o',str(lib)],capture_output=True,text=True);(out/'compiler.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
    source=(prior/'probe.py').read_text().replace(str(prior/'observer.dylib'),str(lib))
    anchor='        observer.set_frame.argtypes=[c.c_uint32]';assert source.count(anchor)==1
    source=source.replace(anchor,anchor+"\n        observer.timing_trace_begin.argtypes=[c.c_char_p];observer.timing_trace_begin.restype=c.c_int\n        assert observer.timing_trace_begin(str(out/'scene-timing.jsonl').encode())==0")
    anchor="        observer.fixed_prefix_boundary.argtypes=[c.c_char_p];observer.fixed_prefix_boundary.restype=c.c_int";assert source.count(anchor)==1
    source=source.replace(anchor,"        assert observer.timing_trace_finish()==0\n"+anchor)
    probe=out/'probe.py';probe.write_text(source);command=list(j['command']);command[2]=str(probe);command[command.index('--output')+1]=str(out/'measurement')
    state=dict(status='running_readonly_timing_trace',directory=str(out),pid=os.getpid(),child_pid=None,lane=lane,command=command,source_prefix=str(jp),new_predictions=0,new_training=False,host_guest_RAM_writes=0)
    pointer=V/f'record-strides-timing-trace-v1-{lane}-current.json'
    def mark():save(out/'protocol.json',state);save(pointer,state)
    mark()
    try:
        with(out/'runtime.log').open('w')as log:
            child=subprocess.Popen(command,cwd='/',env={**os.environ,'PYTHONPATH':str(ROOT/'scripts')},stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;mark();code=child.wait(timeout=300)
        state['child_pid']=None;state['exit_code']=code;assert code==0,(out/'runtime.log').read_text()[-3000:]
        report=read(out/'measurement/report.json');baseline=read(j['report']);assert len(report['frames'])==1000
        keys=['video_sha256','CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','held_buttons']
        assert all(a.get(k)==b.get(k)for a,b in zip(report['frames'],baseline['frames'])for k in keys),'read-only trace changed observed game state'
        events=[__import__('json').loads(line)for line in(out/'measurement/scene-timing.jsonl').read_text().splitlines()];assert events
        state.update(status='terminal_readonly_timing_trace_prior_1000_frame_hashes_preserved',events=len(events),report=str(out/'measurement/report.json'),trace=str(out/'measurement/scene-timing.jsonl'),watched_PCs=sorted(points),prior_prefix_all_recorded_CPU_RAM_GPU_DSP_video_hashes_identical=True,source_sha256={str(p):sha(p)for p in [Path(__file__),jp,prior/'observer.c',prior/'probe.py',cfile,lib,probe,direction,out/'measurement/report.json',out/'measurement/scene-timing.jsonl']});mark();print(lane,state['status'],len(events),flush=True)
    except subprocess.TimeoutExpired as error:state.update(status='observation_timeout_child_may_be_live',error=repr(error));mark();raise
    except BaseException as error:
        live='child'in locals()and child.poll()is None
        state.update(status='observation_error_child_may_be_live'if live else'terminal_readonly_timing_trace_failed',error=repr(error));mark();raise

if __name__=='__main__':main()
