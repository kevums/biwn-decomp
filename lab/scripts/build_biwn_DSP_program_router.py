"""Route observed DSP instruction images to unchanged music/media kernels.

Byte identities include MOVEI operands and branch-delay instructions. Unknown
images remain counted as uncovered; strict run comparisons forbid fallback.
"""
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    music = json.loads((ROOT/'verification/DSP-music-owner-experimental-candidate.json').read_text())
    media = json.loads((ROOT/'verification/DSP-media-owner-experimental-candidate.json').read_text())
    core = json.loads((ROOT/'verification/DSP-music-context-experimental-candidate.json').read_text())
    out = ROOT/'verification/DSP-program-router-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    tables = []
    origins = {}
    for kind, candidate, filename in [('music', music, 'DSP_music_bridge.c'), ('media', media, 'DSP_media_bridge.c')]:
        path = Path(candidate['directory'])/filename
        text = path.read_text()
        table = re.search(r'static const struct identity identities\[\]=\{.*?\};', text, re.S).group()
        tables.append(table.replace('identities[]', kind+'_identities[]'))
        origins[kind] = dict(library=candidate['library'], identity_source=str(path),
                             identity_source_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    source = '''#include <stdint.h>
#include <stddef.h>
#include <string.h>
struct host {size_t(*save)(void*);size_t(*commit)(const void*);uint8_t(*read8)(uint32_t,uint32_t);uint32_t(*read32)(uint32_t,uint32_t);void(*write32)(uint32_t,uint32_t,uint32_t);void(*operands)(uint32_t,uint32_t);void(*write16)(uint32_t,uint16_t,uint32_t);void(*context)(uint32_t*,uint32_t*);};
struct stats {uint64_t calls,owned,uncovered,errors;uint32_t error_PC,error_code;};
struct profiles {uint64_t music,media,switches;uint32_t last;};
struct identity {uint32_t PC;uint8_t size,bytes[6];};
static struct host H;static struct stats S;static struct profiles P;static uint8_t raw[32768],unknown[32768];static size_t unknown_size;
extern int biwn_DSP_music_begin(const void*);
extern int biwn_DSP_media_begin(const void*);
extern int biwn_DSP_music_owner(uint32_t,uint16_t,uint32_t);
extern int biwn_DSP_media_owner(uint32_t,uint16_t,uint32_t);
'''+'\n'.join(tables)+'''
static const struct identity *find(const struct identity *table,size_t count,uint32_t pc){size_t lo=0,hi=count;while(lo<hi){size_t m=(lo+hi)/2;if(table[m].PC==pc)return &table[m];if(table[m].PC<pc)lo=m+1;else hi=m;}return NULL;}
static int match(const struct identity *table,size_t count,uint32_t pc,uint16_t opcode){const struct identity *i,*delay;i=find(table,count,pc);if(!i||pc<0xf1b000u||pc+i->size>0xf1d000u||memcmp(raw+pc-0xf1b000u,i->bytes,i->size))return 0;if((opcode>>10)==52||(opcode>>10)==53){delay=find(table,count,pc+2u);if(!delay||memcmp(raw+pc+2u-0xf1b000u,delay->bytes,delay->size))return 0;}return 1;}
int biwn_DSP_router_owner(uint32_t pc,uint16_t opcode,uint32_t unsupported){size_t n;int result;unsigned profile=0;S.calls++;if(S.errors)return -1;n=H.save(raw);if(n<8496||n>sizeof(raw)){S.errors++;S.error_PC=pc;S.error_code=91;return -1;}
 if(match(music_identities,sizeof(music_identities)/sizeof(music_identities[0]),pc,opcode)){profile=1;result=biwn_DSP_music_owner(pc,opcode,unsupported);}
 else if(match(media_identities,sizeof(media_identities)/sizeof(media_identities[0]),pc,opcode)){profile=2;result=biwn_DSP_media_owner(pc,opcode,unsupported);}
 else{if(!S.uncovered){S.error_PC=pc;S.error_code=96;memcpy(unknown,raw,n);unknown_size=n;}S.uncovered++;return 0;}
 if(result<1||result>2){S.errors++;S.error_PC=pc;S.error_code=100;return -1;}S.owned+=(unsigned)result;if(P.last&&P.last!=profile)P.switches++;P.last=profile;if(profile==1)P.music+=(unsigned)result;else P.media+=(unsigned)result;return result;}
int biwn_DSP_router_begin(const struct host*h){if(!h||!h->save)return 1;H=*h;memset(&S,0,sizeof(S));memset(&P,0,sizeof(P));unknown_size=0;if(biwn_DSP_music_begin(h)||biwn_DSP_media_begin(h))return 2;return 0;}
const struct stats *biwn_DSP_router_stats(void){return &S;}
const struct profiles *biwn_DSP_router_profiles(void){return &P;}
size_t biwn_DSP_router_host_size(void){return sizeof(struct host);}
size_t biwn_DSP_router_stats_size(void){return sizeof(struct stats);}
size_t biwn_DSP_router_profiles_size(void){return sizeof(struct profiles);}
size_t biwn_DSP_router_unknown_state(void*destination){if(destination&&unknown_size)memcpy(destination,unknown,unknown_size);return unknown_size;}
'''
    path = out/'DSP_program_router.c'
    path.write_text(source)
    library = out/'libDSP-program-router.dylib'
    command = ['clang', '-dynamiclib', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror',
               str(path), music['library'], media['library'], '-o', str(library)]
    result = subprocess.run(command, capture_output=True, text=True,
                            env={**os.environ, 'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'compiler.log').write_text(result.stdout+result.stderr)
    assert result.returncode == 0, result.stderr
    report = dict(status='compiled_pending_music_and_media_router_comparisons', directory=str(out),
                  library=str(library), required_core_sha256=core['core_sha256'], sources=origins,
                  source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                  matching='PC plus complete instruction bytes and branch delay bytes; music then media',
                  original_opcode_fallback_for_uncovered=True,
                  strict_comparison_requires_zero_original_and_uncovered=True, whole_game_complete=False)
    text = json.dumps(report, indent=2)+'\n'
    (out/'report.json').write_text(text)
    (ROOT/'verification/DSP-program-router-experimental-candidate.json').write_text(text)
    print(out, flush=True)


if __name__ == '__main__':
    main()
