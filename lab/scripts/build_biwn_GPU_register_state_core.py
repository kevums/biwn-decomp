"""Build isolated register-only GPU serialization APIs; legacy state untouched.

Adds diagnostic320byte variants of the existing4416byte routines. No hardware
instruction, clock, IRQ, bus or persistent-state format changes are made.
"""
import hashlib,json,os,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def function(text,signature):
    start=text.index(signature);opening=text.index('{',start);depth=0
    for end in range(opening,len(text)):
        if text[end]=='{':depth+=1
        elif text[end]=='}':
            depth-=1
            if depth==0:return text[start:end+1]
    raise ValueError('Unbalanced function')

def main():
    parent=ROOT/'verification/DSP-music-context-build/20261016T095846.040285Z/source'
    expected='cce83f2eb04ce3a439a7ed2dddc52c6702c706e9ea89e016b34427ae20f7a39a'
    assert hashlib.sha256((parent/'virtualjaguar_libretro.dylib').read_bytes()).hexdigest()==expected
    names=['src/tom/gpu.c','src/tom/gpu.h','exports-test.list','link-test.T']
    original={name:(parent/name).read_bytes()for name in names}
    out=ROOT/'verification/GPU-register-state-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=out/'source';print(out,flush=True)
    shutil.copytree(parent,source,symlinks=True,ignore=shutil.ignore_patterns('.git','*.o','*.dylib','*.so','*.dll','private'))
    text=original['src/tom/gpu.c'].decode();additions=[]
    for old,new,macro in [('GPUStateSave','BIWNGPUStateSaveRegisters','STATE_SAVE_BUF'),('GPUStateLoad','BIWNGPUStateLoadRegisters','STATE_LOAD_BUF')]:
        body=function(text,'size_t '+old+'(')
        needle='   '+macro+'(buf, gpu_ram_8, sizeof(gpu_ram_8));\n'
        assert body.count(needle)==1
        additions.append(body.replace(old+'(',new+'(',1).replace(needle,''))
    addition='\n\n/* Diagnostic register/private-context serialization only. Local GPU RAM\n * stays shared and is deliberately excluded. The legacy4416byte format\n * and its functions above remain byte-for-byte unchanged. */\n'+'\n\n'.join(additions)+'\n'
    (source/'src/tom/gpu.c').write_text(text+addition)
    header=original['src/tom/gpu.h'].decode();header=header.replace('#include "vjag_memory.h"','#include "vjag_memory.h"\n#include <stddef.h>',1)
    header=header.replace('void GPUInit(void);','/* Diagnostic320byte state suffix, excluding local RAM. */\nsize_t BIWNGPUStateSaveRegisters(uint8_t *buf);\nsize_t BIWNGPUStateLoadRegisters(const uint8_t *buf);\n\nvoid GPUInit(void);',1)
    (source/'src/tom/gpu.h').write_text(header)
    exports=source/'exports-test.list';exports.write_text(exports.read_text()+'\n_BIWNGPUStateSaveRegisters\n_BIWNGPUStateLoadRegisters\n')
    linker=source/'link-test.T';linker.write_text(linker.read_text().replace('global:','global:\n    BIWNGPUStateSaveRegisters;\n    BIWNGPUStateLoadRegisters;',1))
    report=dict(status='building_isolated_GPU_register_state_APIs',directory=str(out),source=str(source),parent_source=str(parent),parent_core_sha256=expected,
                parent_file_sha256={name:hashlib.sha256(raw).hexdigest()for name,raw in original.items()},
                diagnostic_state_bytes=320,legacy_GPU_state_bytes=4416,legacy_functions_unchanged=True,
                new_training=False,default_promoted=False,RetroArch_verified=False,whole_game_complete=False,
                scope='Only two diagnostic variants of existing serialization routines are added. Variants omit4096byteGPUlocalRAM and retain the identical320byte register/private-state suffix. Existing legacy serialization, instruction handlers, scheduling, clocks and devices unchanged. APIs compiled/tested separately; fast bridge, equivalence and performance remain unverified.')
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save();env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'}
    for label,command in [('C89-lint',['bash','scripts/c89-lint.sh','src/tom/gpu.c']),('compiler',['make','-j4','TEST_EXPORTS=1']),('core-tests',['make','-j4','TEST_EXPORTS=1','test'])]:
        report['phase']=label;save();print(label,flush=True)
        with(out/(label+'.log')).open('w')as log:
            child=subprocess.Popen(command,cwd=source,env=env,stdout=log,stderr=subprocess.STDOUT);report['child_pid']=child.pid;save();code=child.wait()
        report[label+'_exit']=code;save()
        if code:
            report.update(status='terminal_build_or_test_failed',failed_phase=label);save();raise RuntimeError(str(out/(label+'.log')))
    for name,raw in original.items():assert (parent/name).read_bytes()==raw
    assert hashlib.sha256((parent/'virtualjaguar_libretro.dylib').read_bytes()).hexdigest()==expected
    for name in ['GPUStateSave','GPUStateLoad']:assert function((source/'src/tom/gpu.c').read_text(),'size_t '+name+'(')==function(text,'size_t '+name+'(')
    core=source/'virtualjaguar_libretro.dylib';symbols=subprocess.check_output(['nm','-gU',str(core)],text=True)
    for name in ['BIWNGPUStateSaveRegisters','BIWNGPUStateLoadRegisters']:assert '_'+name in symbols
    report.update(status='compiled_core_tests_exit_zero_pending_register_API_equivalence',core_path=str(core),core_sha256=hashlib.sha256(core.read_bytes()).hexdigest(),source_sha256=hashlib.sha256((source/'src/tom/gpu.c').read_bytes()).hexdigest(),test_scope='Core-test process exit is recorded. Private-ROM skips are not live audio/RetroArch/whole-game acceptance.')
    save();(ROOT/'verification/GPU-register-state-experimental-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],flush=True)

if __name__=='__main__':main()
