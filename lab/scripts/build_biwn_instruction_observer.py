"""Copy/instrument reconstructed CPU case bodies; no emulator-core changes."""
import json,hashlib,subprocess,os,re
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]

def main():
    previous=json.loads((ROOT/'verification/source-runtime-rebuild-current.json').read_text())
    out=ROOT/'verification/C-instruction-observer-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    copied=out/'source';copied.mkdir();source=ROOT/'projects/black-ice-white-noise/restoration'
    files=[Path(v)for v in previous['compiler']if v.endswith('.c')];changed={}
    for p in files:
        text=p.read_text();needle='switch(s.cpu.pc){';n=text.count(needle)
        if n:
            text='extern void biwn_instruction_observe(const void *);\n'+text.replace(needle,'biwn_instruction_observe(&s.cpu);'+needle)
            changed[p.name]=n
        (copied/p.name).write_text(text)
    hook=copied/'biwn_instruction_observer.c';hook.write_text('''#include <stdint.h>
typedef void (*biwn_cpu_observer)(const void *);
static biwn_cpu_observer observer;
static uint64_t observations;
void biwn_set_instruction_observer(biwn_cpu_observer callback){observer=callback;observations=0;}
uint64_t biwn_instruction_observer_count(void){return observations;}
void biwn_instruction_observe(const void *state){if(observer){observations++;observer(state);}}
''')
    library=out/'libinstruction-observer.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(source),*[str(copied/p.name)for p in files],str(hook),'-o',str(library)]
    built=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(built.stdout+built.stderr);assert not built.returncode,built.stderr
    report=dict(status='compiled_observer_not_yet_runtime_verified',directory=str(out),library=str(library),library_sha256=hashlib.sha256(library.read_bytes()).hexdigest(),compiler=command,
        instrumented_files=changed,source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in files},copied_source_sha256={p.name:hashlib.sha256((copied/p.name).read_bytes()).hexdigest()for p in files},
        emulator_core_changed=False,observer_role='Read-only callback before each generated CPU instruction case; not new recovered code or complete instruction coverage.',whole_game_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/C-instruction-observer-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(out)

if __name__=='__main__':main()
