"""Freeze the first odd-PC ring inside the instruction callback, before exception loops overwrite it."""
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import subprocess
from publish_scene_reset_fresh_v1 import ROOT, V, read, save, sha


def main():
    pointer = V/'native-frame-phased-image-fresh-input-v1-candidate-current.json'
    original = read(pointer)
    folder = Path(original['directory'])
    out = V/'v40-input-transition-fault-trace-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    parent_snapshot=out/'parent-run-at-launch.json';save(parent_snapshot,original)
    text = (folder/'observer.c').read_text()
    assert text.count('int32_t observe(uint32_t pc)') == 1
    text = text.replace('int32_t observe(uint32_t pc)', 'static int32_t qualified_observe(uint32_t pc)')
    extra = r'''
struct diag_row { uint32_t frame,pc,task; struct cpu cpu; uint64_t resource_errors,input_errors,aliases; };
static struct diag_row diag_ring[2048];
static uint64_t diag_count;
static unsigned diag_done,diag_frozen;
int32_t observe(uint32_t pc){
 int32_t result=qualified_observe(pc);
 if(frame>=8000u&&!diag_done&&!diag_frozen){
  struct diag_row *r=&diag_ring[diag_count++%2048u];
  memset(r,0,sizeof(*r));r->frame=frame;r->pc=pc;r->task=rd32(0xc0920u);read_cpu(&r->cpu);
  r->resource_errors=r39_errors;r->input_errors=i39_errors;r->aliases=r39_alias_errors;
  if((pc&1u)||acquire_monitor_errors||acquire_user_stack_outside){
   diag_frozen=1;
   FILE *saved=fopen(DIAG_FIRST_RAM,"wb");if(saved){fwrite(ram,0x200000u,1,saved);fclose(saved);}
  }
 }
 return result;
}
int diag_tick(void){
 struct cpu cpu;read_cpu(&cpu);
 if(diag_done||frame<8000u||(!(cpu.pc&1u)&&!r39_errors&&!i39_errors&&!r39_alias_errors&&!diag_frozen))return diag_done;
 diag_done=1;
 FILE *f=fopen(DIAG_META,"w");if(!f)return -1;
 fprintf(f,"{\"frame\":%u,\"pc\":%u,\"task\":%u,\"ring_count\":%llu,\"row_bytes\":%zu,\"resource_errors\":%llu,\"input_errors\":%llu,\"aliases\":%llu}\n",frame,cpu.pc,rd32(0xc0920u),(unsigned long long)diag_count,sizeof(struct diag_row),(unsigned long long)r39_errors,(unsigned long long)i39_errors,(unsigned long long)r39_alias_errors);fclose(f);
 f=fopen(DIAG_RING,"wb");if(!f)return -1;
 uint64_t start=diag_count>2048u?diag_count-2048u:0;
 for(uint64_t i=start;i<diag_count;i++)if(fwrite(&diag_ring[i%2048u],sizeof(struct diag_row),1,f)!=1){fclose(f);return -1;}
 fclose(f);return 1;
}
'''
    extra = extra.replace('DIAG_FIRST_RAM',json.dumps(str(out/'first-watch-RAM.bin'))).replace('DIAG_META', json.dumps(str(out/'first-fault.json'))).replace('DIAG_RING', json.dumps(str(out/'instruction-ring.bin')))
    source, library = out/'observer.c', out/'observer.dylib'
    source.write_text(text+extra)
    command = ['clang', '-dynamiclib', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror', str(source), str(folder/'direction-shadow-model.c'), '-o', str(library)]
    result = subprocess.run(command, capture_output=True, text=True)
    (out/'compiler.log').write_text(result.stdout+result.stderr)
    assert result.returncode == 0, result.stderr
    probe_source = folder/'probe.py'
    probe_text = probe_source.read_text().replace(repr(str(folder/'observer.dylib')), repr(str(library)))
    needle = '            core.retro_run()'
    assert probe_text.count(needle) == 1
    probe_text = probe_text.replace(needle, needle+"\n            diagnostic=observer.diag_tick()\n            assert diagnostic>=0\n            if diagnostic:\n                save(out/'diagnostic-CPU.json',full_CPU())\n                (out/'diagnostic-RAM.bin').write_bytes(c.string_at(ram_pointer,0x200000))\n                break")
    probe = out/'probe.py'
    probe.write_text(probe_text)
    command = list(original['command'])
    command[2] = str(probe)
    command[command.index('--frames')+1] = '12000'
    command[command.index('--output')+1] = str(out/'candidate')
    state = dict(status='running_fresh_transition_diagnostic', directory=str(out), pid=os.getpid(), command=command, parent_run=str(pointer), game_image_changed=False, snapshot_restores=0, host_guest_RAM_writes=0, host_CPU_or_task_seeds=0, new_predictions=0, new_training=False)
    target = V/'v40-input-transition-fault-trace-v1-current.json'
    def mark():
        save(out/'protocol.json', state)
        save(target, state)
    mark()
    with (out/'runtime.log').open('w') as log:
        child = subprocess.Popen(command, cwd='/', env={**os.environ, 'PYTHONPATH': str(ROOT/'scripts')}, stdout=log, stderr=subprocess.STDOUT)
        state['child_pid'] = child.pid
        mark()
        code = child.wait()
    fault = out/'first-fault.json'
    state.update(status='terminal_transition_diagnostic_fault_recorded' if fault.exists() else 'terminal_transition_diagnostic_no_selected_fault', child_pid=None, child_exit_code=code, probe_gate_pass=code == 0, fault=read(fault) if fault.exists() else None, source_sha256={str(p): sha(p) for p in [Path(__file__), parent_snapshot, folder/'observer.c', folder/'observer.dylib', folder/'direction-shadow-model.c', probe_source, source, library, probe, *[p for p in out.rglob('*') if p.is_file() and p.name != 'protocol.json']]})
    mark()
    print(state['status'], state['fault'], flush=True)


if __name__ == '__main__':
    main()
