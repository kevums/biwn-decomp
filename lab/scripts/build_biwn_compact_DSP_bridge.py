"""Isolated DSP scalar snapshots with live local RAM; defaults stay unchanged."""
import hashlib
import ctypes as c
import json
import os
from pathlib import Path
import shutil
import random
import subprocess
from datetime import datetime,timezone
from build_biwn_fast_DSP_router import once,compile_library

ROOT=Path(__file__).resolve().parents[1]


def function(text,name):
    start=text.index('size_t '+name+'(');brace=text.index('{',start);depth=1;end=brace+1
    while depth:
        depth+=(text[end]=='{')-(text[end]=='}');end+=1
    return text[start:end]


def check_transport(core_path):
    core=c.CDLL(str(core_path));core.DSPInit()
    for name in ['DSPStateSave','DSPStateLoad','BIWNDSPWriteLogicalState','BIWNDSPStateSaveWithoutRAM','BIWNDSPWriteLogicalStateWithoutRAM']:
        fn=getattr(core,name);fn.argtypes=[c.c_void_p];fn.restype=c.c_size_t
    core.DSPGetRAM.restype=c.c_void_p
    core.BIWNDSPReadRetirementContext.argtypes=[c.POINTER(c.c_uint32),c.POINTER(c.c_uint32)]
    def context():
        delay=c.c_uint32();bank=c.c_uint32();core.BIWNDSPReadRetirementContext(c.byref(delay),c.byref(bank));return(delay.value,bank.value)
    def snapshot():
        raw=c.create_string_buffer(32768);size=core.DSPStateSave(raw);return raw.raw[:size]
    base=snapshot();rng=random.Random(0x43535044)
    for case in range(64):
        assert core.DSPStateLoad(c.create_string_buffer(base))==len(base)
        current=snapshot();before_context=context();partial=c.create_string_buffer(bytes([0xa5])*32768)
        assert core.BIWNDSPStateSaveWithoutRAM(partial)==len(current)
        assert partial.raw[:8192]==bytes([0xa5])*8192 and partial.raw[8192:len(current)]==current[8192:]
        assert snapshot()==current and context()==before_context
        edited=bytearray(current)
        edited[:8192]=rng.randbytes(8192)
        edited[8192:8495]=rng.randbytes(303)
        edited[8236:8239]=bytes([case&1,(case>>1)&1,(case>>2)&1]);edited[8495]=case&1
        data=c.create_string_buffer(bytes(edited))
        assert core.BIWNDSPWriteLogicalState(data)==8496
        expected=snapshot();expected_context=context()
        assert core.DSPStateLoad(c.create_string_buffer(base))==len(base)
        c.memmove(core.DSPGetRAM(),bytes(edited[:8192]),8192)
        assert core.BIWNDSPWriteLogicalStateWithoutRAM(data)==8496
        assert snapshot()==expected and context()==expected_context
    core.DSPStateLoad(c.create_string_buffer(base))
    return dict(status='compact_DSP_transport_equivalence_pass',read_cases=64,commit_cases=64,
        snapshot_bytes=len(base),local_RAM_bytes_omitted_per_copy=8192,
        scope='Exact full serializedDSP and retirement context comparison for64 seeded logical commits; compact reads leaveRAMprefix untouched and do not mutate core. No DSP instructions,audio or frame scheduling executed by this test.')


def main():
    original_core=json.loads((ROOT/'verification/DSP-music-context-experimental-candidate.json').read_text())
    parent=Path(original_core['source'])
    prior=json.loads((ROOT/'verification/fast-DSP-router-experimental-candidate.json').read_text())
    old=Path(prior['directory'])
    out=ROOT/'verification/compact-DSP-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=out/'source'
    shutil.copytree(parent,source,symlinks=True,ignore=shutil.ignore_patterns('.git','*.o','*.dylib','*.so','*.dll','private'))
    path=source/'src/jerry/dsp.c';before=path.read_text()
    save=function(before,'DSPStateSave').replace('DSPStateSave(','BIWNDSPStateSaveWithoutRAM(',1)
    save=once(save,'STATE_SAVE_BUF(buf, dsp_ram_8, sizeof(dsp_ram_8));','buf += sizeof(dsp_ram_8); /* live local RAM is supplied separately */')
    commit=function(before,'BIWNDSPWriteLogicalState').replace('BIWNDSPWriteLogicalState(','BIWNDSPWriteLogicalStateWithoutRAM(',1)
    commit=once(commit,'STATE_LOAD_BUF(buf, dsp_ram_8, sizeof(dsp_ram_8));','buf += sizeof(dsp_ram_8); /* source engine already wrote live local RAM */')
    path.write_text(before+'\n/* Experimental owner helpers. Existing savestate ABI is unchanged. */\n'+save+'\n'+commit+'\n')
    symbols=['BIWNDSPStateSaveWithoutRAM','BIWNDSPWriteLogicalStateWithoutRAM']
    exports=source/'exports-test.list';exports.write_text(exports.read_text()+''.join('\n_'+symbol+'\n'for symbol in symbols))
    linker=source/'link-test.T';linker.write_text(linker.read_text().replace('global:','global:\n'+''.join('    '+symbol+';\n'for symbol in symbols),1))
    report=dict(status='building',directory=str(out),source=str(source),parent_source=str(parent),
        parent_core_sha256=original_core['core_sha256'],default_promoted=False,new_training=False,
        RetroArch_verified=False,whole_game_complete=False)
    def publish():
        text=json.dumps(report,indent=2)+'\n';(out/'report.json').write_text(text)
        (ROOT/'verification/compact-DSP-build-current.json').write_text(text)
    publish();print(out,flush=True)
    env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'}
    for label,command in [('C89-lint',['bash','scripts/c89-lint.sh','src/jerry/dsp.c']),
                          ('compiler',['make','-j8','TEST_EXPORTS=1']),
                          ('core-tests',['make','TEST_EXPORTS=1','test'])]:
        report['status']='running_'+label;publish()
        with (out/(label+'.log')).open('w')as log:result=subprocess.run(command,cwd=source,env=env,stdout=log,stderr=subprocess.STDOUT)
        report[label+'_exit']=result.returncode;publish();assert result.returncode==0,(label,out)
    core=source/'virtualjaguar_libretro.dylib'
    report['transport_check']=check_transport(core)
    bridge=(old/'DSP_music_bridge.c').read_text()
    bridge=once(bridge,'static struct host H;static struct stats S;static uint8_t raw[32768];',
        'static struct host H;static struct stats S;static uint8_t raw[32768];static uint8_t *live_RAM;\nint biwn_DSP_music_bind_live_RAM(uint8_t*p){if(!p)return 1;live_RAM=p;return 0;}')
    bridge=once(bridge,'s->local_RAM=raw;','s->local_RAM=live_RAM;')
    bridge=bridge.replace('memcmp(raw+pc-0xf1b000u,','memcmp(live_RAM+pc-0xf1b000u,')
    bridge=bridge.replace('memcmp(raw+pc+2u-0xf1b000u,','memcmp(live_RAM+pc+2u-0xf1b000u,')
    bridge=once(bridge,'if(s.local_RAM!=raw)','if(s.local_RAM!=live_RAM)')
    bridge=once(bridge,'if(!h||!h->save||!h->commit','if(!live_RAM||!h||!h->save||!h->commit')
    (out/'DSP_music_bridge.c').write_text(bridge)
    for name in ['biwn_dsp_music_engine.c','biwn_dsp_music_engine.h']:
        (out/name).write_bytes((old/name).read_bytes())
    music=compile_library(out,'libDSP-music-compact.dylib',[out/'DSP_music_bridge.c',out/'biwn_dsp_music_engine.c'])
    router=(old/'DSP_program_router.c').read_text()
    insertion='''
extern int biwn_DSP_music_bind_live_RAM(uint8_t*);
static size_t(*compact_save)(void*);
static size_t(*compact_commit)(const void*);
static uint8_t *compact_RAM;
int biwn_DSP_router_bind_compact(size_t(*save)(void*),size_t(*commit)(const void*),uint8_t*RAM){if(!save||!commit||!RAM)return 1;compact_save=save;compact_commit=commit;compact_RAM=RAM;return 0;}
'''
    point=router.index('int biwn_DSP_router_begin(');router=router[:point]+insertion+router[point:]
    router=once(router,'int biwn_DSP_router_begin(const struct host*h){','int biwn_DSP_router_begin(const struct host*h){struct host music_host;')
    router=once(router,'if(biwn_DSP_music_begin(h)||biwn_DSP_media_begin(h))return 2;',
        'if(!compact_save||!compact_commit||!compact_RAM)return 3;music_host=*h;music_host.save=compact_save;music_host.commit=compact_commit;if(biwn_DSP_music_bind_live_RAM(compact_RAM)||biwn_DSP_music_begin(&music_host)||biwn_DSP_media_begin(h))return 2;')
    (out/'DSP_program_router.c').write_text(router)
    library=compile_library(out,'libDSP-compact-router.dylib',[out/'DSP_program_router.c'],[music,prior['media_library']])
    report.update(status='compiled_core_tests_exit_zero_pending_equivalence_and_performance',
        core_path=str(core),core_sha256=hashlib.sha256(core.read_bytes()).hexdigest(),library=str(library),
        required_core_sha256=hashlib.sha256(core.read_bytes()).hexdigest(),compact_live_RAM=True,
        media_library=prior['media_library'],music_library=str(music),
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in [path,out/'DSP_program_router.c',out/'DSP_music_bridge.c']},
        error_semantics='Experimental live localRAM writes may remain after a source rejection, as prior bus writes do. Standalone/staged snapshot rollback ABI is not claimed.',
        scope='Compact helpers preserve old scalar layout and private pipeline/IRQ commit rules while omitting redundant localRAM copies. Music reads/writes liveDSPRAM; media/unknown diagnostics retain full snapshots. No opcode semantics or emulator scheduling change. No speedup or equivalence claim until measured.')
    publish()
    (ROOT/'verification/compact-DSP-router-experimental-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    assert(parent/'src/jerry/dsp.c').read_text()==before
    print(report['status'],flush=True)


if __name__=='__main__':main()
