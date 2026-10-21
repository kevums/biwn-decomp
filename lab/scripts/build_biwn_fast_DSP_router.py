"""Isolated snapshot-RAM alias owner; no live core or default manifest edits."""
import hashlib,json,os,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new)


def compile_library(out,name,sources,links=()):
    library=out/name
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*map(str,sources),*map(str,links),'-o',str(library)]
    result=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/(name+'.compiler.log')).write_text(result.stdout+result.stderr)
    assert result.returncode==0,result.stderr
    return library


def main():
    prior=json.loads((ROOT/'verification/DSP-program-router-experimental-candidate.json').read_text())
    music=json.loads((ROOT/'verification/DSP-music-owner-experimental-candidate.json').read_text())
    media=json.loads((ROOT/'verification/DSP-media-owner-experimental-candidate.json').read_text())
    out=ROOT/'verification/fast-DSP-router-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    original=Path(music['directory'])
    header=(original/'biwn_dsp_music_engine.h').read_text()
    header=once(header,'uint8_t local_RAM[8192];','uint8_t *local_RAM; /* owner-only alias of the staged serialized RAM, not live core RAM */')
    header=header.replace('Errors preserve input state with prior bus writes retained.','Owner-only ABI: staged RAM may change on errors; the owner never commits an errored snapshot. Original standalone ABI remains unchanged.')
    (out/'biwn_dsp_music_engine.h').write_text(header)
    (out/'biwn_dsp_music_engine.c').write_bytes((original/'biwn_dsp_music_engine.c').read_bytes())
    bridge=(original/'DSP_music_bridge.c').read_text()
    bridge=once(bridge,'memcpy(s->local_RAM,raw,8192);','s->local_RAM=raw;')
    bridge=once(bridge,'memcpy(raw,s->local_RAM,8192);','/* RAM already resides in the staged raw buffer. */')
    bridge=once(bridge,'pack(&s);if(H.commit(raw)!=8496)','if(s.local_RAM!=raw)return fail(pc,96);pack(&s);if(H.commit(raw)!=8496)')
    (out/'DSP_music_bridge.c').write_text(bridge)
    fast_music=compile_library(out,'libDSP-music-snapshot-alias.dylib',[out/'DSP_music_bridge.c',out/'biwn_dsp_music_engine.c'])
    router=(Path(prior['directory'])/'DSP_program_router.c').read_text()
    begin=router.index('static int match(');end=router.index('\nint biwn_DSP_router_begin',begin)
    replacement='''static int bytes_match(uint32_t pc,const struct identity*i){unsigned n;if(pc<0xf1b000u||pc+i->size>0xf1d000u)return 0;for(n=0;n<i->size;n++)if(H.read8(pc+n,2)!=i->bytes[n])return 0;return 1;}
static int match(const struct identity*table,size_t count,uint32_t pc,uint16_t opcode){const struct identity*i,*delay;i=find(table,count,pc);if(!i||!bytes_match(pc,i))return 0;if((opcode>>10)==52||(opcode>>10)==53){delay=find(table,count,pc+2u);if(!delay||!bytes_match(pc+2u,delay))return 0;}return 1;}
int biwn_DSP_router_owner(uint32_t pc,uint16_t opcode,uint32_t unsupported){size_t n;int result;unsigned profile=0;S.calls++;if(S.errors)return -1;
if(match(music_identities,sizeof(music_identities)/sizeof(music_identities[0]),pc,opcode)){profile=1;result=biwn_DSP_music_owner(pc,opcode,unsupported);}
else if(match(media_identities,sizeof(media_identities)/sizeof(media_identities[0]),pc,opcode)){profile=2;result=biwn_DSP_media_owner(pc,opcode,unsupported);}
else{if(!S.uncovered){n=H.save(raw);if(n<8496||n>sizeof(raw)){S.errors++;S.error_PC=pc;S.error_code=91;return -1;}S.error_PC=pc;S.error_code=96;memcpy(unknown,raw,n);unknown_size=n;}S.uncovered++;return 0;}
if(result<1||result>2){S.errors++;S.error_PC=pc;S.error_code=100;return -1;}S.owned+=(unsigned)result;if(P.last&&P.last!=profile)P.switches++;P.last=profile;if(profile==1)P.music+=(unsigned)result;else P.media+=(unsigned)result;return result;}
'''
    router=router[:begin]+replacement+router[end:]
    router=once(router,'if(!h||!h->save)return 1;','if(!h||!h->save||!h->read8)return 1;')
    path=out/'DSP_program_router.c';path.write_text(router)
    library=compile_library(out,'libDSP-fast-router.dylib',[path],[fast_music,media['library']])
    report=dict(status='compiled_pending_original_comparisons',directory=str(out),library=str(library),required_core_sha256=prior['required_core_sha256'],prior_router=str(Path(prior['directory'])/'DSP_program_router.c'),music_library=str(fast_music),media_library=media['library'],source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in [path,out/'DSP_music_bridge.c',out/'biwn_dsp_music_engine.c',out/'biwn_dsp_music_engine.h']},changes=['Music state local_RAM aliases its private staged raw buffer; eliminates unpack/pack and per-step array copies.','Router checks complete instruction/delay bytes via side-effect-free DSP local-RAM byte reads instead of a full snapshot.','Original core, scalar commits, IRQ/device writes, media owner and default manifests unchanged.'],error_semantics='Staged RAM can mutate on error, but no logical-state commit occurs; prior bus writes remain retained.',standalone_state_ABI_compatible=False,owner_Host_ABI_compatible=True,whole_game_complete=False,new_training=False,runtime_promoted=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/fast-DSP-router-experimental-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(out,flush=True)


if __name__=='__main__':main()
