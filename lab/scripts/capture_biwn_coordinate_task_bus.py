"""Inert observer for every source CPU data access in coordinate's yield.

No task CPU/RAM is substituted. Records hardware data and native writer
events so a separate host can execute other task bodies from one initial
state instead of transplanting their recorded continuations.
"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess

from check_biwn_natural_coordinate_scheduler import ROOT, sha, save

OBSERVER = r'''
static uint64_t task_first=FIRST_INDEXull,task_last=LAST_INDEXull,task_head;
static int task_active,task_finished;
static FILE *task_bus,*task_events;
static int task_log(char kind,unsigned width,uint32_t address,uint32_t value)
{
    if(!task_active)return 0;
    return fprintf(task_bus,"%llu %c %u %u %u\n",(unsigned long long)(S.calls-1),kind,width,address,value)<0;
}
static int task_flush_events(uint64_t index)
{
    uint64_t end=vjtrace_ring_head(),i;vjtrace_ev event;
    if(end<task_head||end-task_head>100000)return 1;
    for(i=task_head;i<end;i++){
        if(!vjtrace_ring_read(i,&event))return 1;
        if(fprintf(task_events,"%llu %llu %u %u %u %u %u %u %u\n",
             (unsigned long long)index,(unsigned long long)event.seq,event.frame,
             (unsigned)event.halfline,(unsigned)event.type,(unsigned)event.who,
             event.pc,event.addr,event.value)<0)return 1;
    }
    task_head=end;return 0;
}
static int task_observe(void)
{
    uint64_t index=S.calls-1;char path[4096];const char *directory;int length;
    if(task_finished||index<task_first)return 0;
    if(!task_active){
        if(index!=task_first||vjtrace_armed||vjtrace_nwatch)return 1;
        directory=getenv("BIWN_COORDINATE_TASK_BUS_DIR");if(!directory)return 1;
        length=snprintf(path,sizeof(path),"%s/CPU-bus.txt",directory);
        if(length<0||(size_t)length>=sizeof(path))return 1;
        task_bus=fopen(path,"w");if(!task_bus)return 1;
        length=snprintf(path,sizeof(path),"%s/native-events.txt",directory);
        if(length<0||(size_t)length>=sizeof(path))return 1;
        task_events=fopen(path,"w");if(!task_events)return 1;
        vjtrace_init();task_head=vjtrace_ring_head();
        if(vjtrace_watch_add(0,0x1fffffu,2)<0)return 1;
        vjtrace_arm();task_active=1;return 0;
    }
    if(task_flush_events(index))return 1;
    if(index==task_last){
        vjtrace_disarm();vjtrace_watch_clear();task_active=0;task_finished=1;
        if(fclose(task_bus)||fclose(task_events))return 1;
    }
    return 0;
}
'''


def main():
    out=ROOT/'verification/coordinate-task-bus'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    captured_path=ROOT/'verification/natural-coordinate-scheduler-current.json'
    captured=json.loads(captured_path.read_text())
    plan=json.loads((Path(captured['directory'])/'capture-plan.json').read_text())
    runtime=json.loads((ROOT/'verification/unified-restore-runtime-candidate.json').read_text())
    base=json.loads(Path(runtime['native_CPU_candidate']).read_text())
    source_path=Path(base['directory'])/'fast_CPU_bridge.c'
    assert sha(source_path)==base['source_sha256']
    source=source_path.read_text()
    marker='static int rd8(void*x'
    assert source.count(marker)==1
    source=source.replace(marker,OBSERVER.replace('FIRST_INDEX',str(plan['first'])).replace('LAST_INDEX',str(plan['last']))+'\n'+marker)
    for width,typ in [(8,'uint8_t'),(16,'uint16_t'),(32,'uint32_t')]:
        old=f'*p=({typ})H.read{width}(a);return 0;' if width!=32 else '*p=H.read32(a);return 0;'
        assert source.count(old)==1,old
        source=source.replace(old,old.replace('return 0;',f'return task_log(\'r\',{width//8},a,*p);'))
        old=f'H.write{width}(a,v);return 0;'
        assert source.count(old)==1
        source=source.replace(old,f'if(task_log(\'w\',{width//8},a,v))return 1;H.write{width}(a,v);return 0;')
    marker='if(s.pc!=PC)return fail(PC,91);if(state_file)'
    assert source.count(marker)==1
    source=source.replace(marker,'if(s.pc!=PC)return fail(PC,91);if(task_observe())return fail(PC,179);if(state_file)')
    core=Path(runtime['core']);assert sha(core)==runtime['core_sha256']
    source='#define VJ_TRACE 1\n#include "'+str(core.parent/'src/core/vjtrace.h')+'"\n'+source
    target=out/'capture_bridge.c';target.write_text(source)
    shutil.copytree(source_path.parent/'pinned-CPU-headers',out/'pinned-CPU-headers')
    command=runtime['commands'][1][:];command[command.index(str(source_path))]=str(target);command[-1]=str(out/'libcapture-bus.dylib');command.insert(command.index('-o'),str(core))
    env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'}
    result=subprocess.run(command,capture_output=True,text=True,env=env);(out/'compiler.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0,result.stderr
    candidate=out/'candidate.json';save(candidate,dict(base,directory=str(out),library=command[-1],source_sha256=sha(target)))
    baseline=Path(captured['baseline']);protocol=json.loads((baseline/'protocol.json').read_text())
    run=next(row['command'][:] for row in protocol['commands']if row['phase']=='C')
    run[run.index('--native-CPU-candidate')+1]=str(candidate);run[run.index('--output')+1]=str(out/'observed')
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),first=plan['first'],last=plan['last'],
               prior_capture_proof=str(captured_path),prior_capture_proof_sha256=sha(captured_path),
               compile_command=command,command=run,source_sha256=sha(target),library_sha256=sha(command[-1]),
               actual_other_task_execution=False,whole_game_complete=False)
    def checkpoint():
        save(out/'protocol.json',state);save(ROOT/'verification/coordinate-task-bus-active.json',state)
    checkpoint()
    try:
        with(out/'runtime.log').open('w')as log:
            child=subprocess.Popen(run,stdout=log,stderr=subprocess.STDOUT,env={**env,'BIWN_COORDINATE_TASK_BUS_DIR':str(out)})
            state.update(status='capturing',child_pid=child.pid);checkpoint();print(out,'PID',child.pid,flush=True);code=child.wait()
        state['exit_code']=code;assert code==0,out/'runtime.log'
        names=['CPU-before-instructions.bin','retired-instruction-costs.bin','warm-RAM.bin','final-RAM.bin','final-video.bin','final-serialized-state.bin','frontend-PCM.s16le']
        same={name:sha(out/'observed'/name)==sha(baseline/'C'/name)for name in names};assert all(same.values()),same
        counts={};mmio={};bus_count=0
        for line in(out/'CPU-bus.txt').read_text().splitlines():
            index,kind,width,address,value=line.split();bus_count+=1
            if int(address)>=0x200000:mmio[(kind,int(address),int(width))]=mmio.get((kind,int(address),int(width)),0)+1
        for line in(out/'native-events.txt').read_text().splitlines():
            row=list(map(int,line.split()));assert len(row)==9
            if row[4]==12:counts[row[5]]=counts.get(row[5],0)+1
        state.update(status='terminal_inert_bus_capture',unchanged_source_run=same,CPU_bus_accesses=bus_count,
                     MMIO_accesses=[dict(kind=key[0],address=hex(key[1]),width=key[2],count=value)for key,value in mmio.items()],
                     native_RAM_write_counts_by_writer=counts,bus_sha256=sha(out/'CPU-bus.txt'),events_sha256=sha(out/'native-events.txt'))
        checkpoint();save(ROOT/'verification/coordinate-task-bus-current.json',state)
        print(json.dumps({key:state[key]for key in ['status','CPU_bus_accesses','MMIO_accesses','native_RAM_write_counts_by_writer']}),flush=True)
    except BaseException as error:
        state.update(status='terminal_failed',error=repr(error));checkpoint();raise


if __name__=='__main__':main()
