"""Adapt previously original-checked movie code to atomic outer GPU bundles."""
import hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    generation=session/'media-video-gpu-21ea0/sequence-C-generation.json'
    metadata=json.loads(generation.read_text())
    original=ROOT/'projects/black-ice-white-noise/restoration'
    stem='biwn_movie_sequence_GPU'
    out=ROOT/'verification/movie-GPU-bundle-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    body=(original/(stem+'.c')).read_text();header=(original/(stem+'.h')).read_text()
    assert body.count('while(budget--)')==1
    body=body.replace(stem+'_run(',stem+'_bundle_run(')
    body=body.replace('while(budget--){unsigned delayed=pending;','while(budget||pending){unsigned delayed=pending;if(!delayed)budget--;')
    end='return BIWN_MOVIE_SEQUENCE_GPU_WORK_LIMIT;}'
    assert body.count(end)==1
    body=body.replace(end,'*state=s;return BIWN_MOVIE_SEQUENCE_GPU_OK;}')
    (out/(stem+'.c')).write_text(body);(out/(stem+'.h')).write_text(header)
    library=out/'libmovie-GPU-bundle.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(out/(stem+'.c')),'-o',str(library)]
    result=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'compiler.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
    programs=json.loads((ROOT/'verification/interior-GPU-bundle-experimental-candidate.json').read_text())['programs']
    programs.append(dict(name='movie_sequence',stem=stem,function=stem+'_bundle_run',kind='movie',library=str(library),instructions_decoded=metadata['instructions_decoded'],source_sha256=hashlib.sha256(body.encode()).hexdigest(),original_generation=str(generation)))
    exit_stem='biwn_gpu_movie_exit'
    exit_body=(original/(exit_stem+'.c')).read_text().replace(exit_stem+'_run(',exit_stem+'_bundle_run(')
    assert exit_body.count('while(budget--)')==1
    exit_body=exit_body.replace('while(budget--){unsigned delayed=pending;','while(budget||pending){unsigned delayed=pending;if(!delayed)budget--;')
    assert exit_body.count('return BIWN_GPU_MOVIE_EXIT_WORK_LIMIT;}')==1
    exit_body=exit_body.replace('return BIWN_GPU_MOVIE_EXIT_WORK_LIMIT;}','*state=s;return BIWN_GPU_MOVIE_EXIT_OK;}')
    (out/(exit_stem+'.c')).write_text(exit_body);(out/(exit_stem+'.h')).write_bytes((original/(exit_stem+'.h')).read_bytes())
    exit_library=out/'libmovie-exit-GPU-bundle.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(out/(exit_stem+'.c')),'-o',str(exit_library)]
    result=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'exit-compiler.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
    exit_generation=session/'GPU-movie-exit-C-generation.json'
    programs.append(dict(name='movie_exit',stem=exit_stem,function=exit_stem+'_bundle_run',kind='movie_exit',library=str(exit_library),instructions_decoded=json.loads(exit_generation.read_text())['instructions_decoded'],source_sha256=hashlib.sha256(exit_body.encode()).hexdigest(),original_generation=str(exit_generation)))
    witness=ROOT/'runs/merchant-GPU-last-four-discovery/regular-GPU-bundles/unknown-000-GPU.bin'
    if witness.exists():
        raw=witness.read_bytes();assert len(raw)==4416 and raw[4395]==0
        decoder=ROOT/'tools/jaguar-disasm/jaguar-disasm';rows=[]
        for pc,size,expected in [(0xf03240,6,'movei   $f032c8,r0'),(0xf03246,2,'jump    (r0)'),(0xf03248,2,'nop')]:
            data=raw[pc-0xf03000:pc-0xf03000+size]
            result=subprocess.run([str(decoder),'gpu',hex(pc)],input=data,capture_output=True);assert result.returncode==0
            address,length,assembly=result.stdout.decode().strip().split('\t');assert assembly==expected and int(address,16)==pc and int(length,16)==size
            rows.append(dict(address=pc,size=size,bytes=data.hex(),assembly=assembly))
        trampoline_stem='biwn_gpu_movie_trampoline'
        header=(original/(exit_stem+'.h')).read_text().replace('biwn_gpu_movie_exit',trampoline_stem).replace('BIWN_GPU_MOVIE_EXIT','BIWN_GPU_MOVIE_TRAMPOLINE')
        body='''#include "biwn_gpu_movie_trampoline.h"
/* Three observed source instructions; no original GPU or runtime decoder. */
enum biwn_gpu_movie_trampoline_status biwn_gpu_movie_trampoline_bundle_run(struct biwn_gpu_movie_trampoline_bus *bus,struct biwn_gpu_movie_trampoline_state *state,uint32_t budget){
 struct biwn_gpu_movie_trampoline_state s;unsigned pending=0;uint32_t target=0;
 if(!bus||!state||!budget||state->active_bank)return 1;s=*state;
 while(budget||pending){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed){budget--;if(bus->observe_PC)bus->observe_PC(bus->context,s.pc);}s.instructions++;
 switch(s.pc){case 0xf03240u:s.registers[0][0]=0xf032c8u;s.pc=0xf03246u;break;
 case 0xf03246u:pending=1;target=s.registers[0][0];s.pc=0xf03248u;break;
 case 0xf03248u:s.pc=0xf0324au;break;default:return 3;}
 if(delayed){if(pending)return 5;s.pc=resume;}}
 *state=s;return 0;}
'''
        # Keep the ABI declarations, removing inherited handler commentary.
        header=header[:header.index('/*10execution-proven')]+'''/* Three captured bank0 movie-to-dispatcher trampoline instructions. */
enum biwn_gpu_movie_trampoline_status biwn_gpu_movie_trampoline_bundle_run(struct biwn_gpu_movie_trampoline_bus *,struct biwn_gpu_movie_trampoline_state *,uint32_t);
#endif
'''
        (out/(trampoline_stem+'.c')).write_text(body);(out/(trampoline_stem+'.h')).write_text(header)
        trampoline_lib=out/'libmovie-trampoline-GPU-bundle.dylib'
        result=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(out/(trampoline_stem+'.c')),'-o',str(trampoline_lib)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
        (out/'trampoline-compiler.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
        programs.append(dict(name='movie_trampoline',stem=trampoline_stem,function=trampoline_stem+'_bundle_run',kind='movie_exit',library=str(trampoline_lib),instructions_decoded=rows,source_sha256=hashlib.sha256(body.encode()).hexdigest(),original_witness=str(witness)))
    report=dict(status='compiled_unverified',directory=str(out),programs=programs,new_training=False,coordinator_authored=True,whole_game_complete=False)
    (ROOT/'verification/movie-GPU-bundle-experimental-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(out,flush=True)

if __name__=='__main__':main()
