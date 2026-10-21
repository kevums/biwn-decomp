"""Isolated byte-fenced external DSP cases, retaining immutable music/media providers."""
import argparse,json,re,subprocess,shutil
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
import generate_biwn_music_DSP_engine as generator

def read(p):return json.loads(Path(p).read_text())
def once(t,a,b):assert t.count(a)==1,a;return t.replace(a,b)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--author',type=Path,default=ROOT/'verification/external-DSP-Code-Author-current.json');args=parser.parse_args()
    author=read(args.author);source=Path(author['source']);assert sha(source)==author['source_text_sha256']
    observation_path=ROOT/'verification/merchant-DSP-transition-observation-current.json';observed=read(observation_path)
    assert observed['status']=='terminal_native_DSP_transition_observed_equal'
    rows=[]
    for key,count in observed['outside_DSP_local_RAM_instruction_counts'].items():
        pc,word=[int(x,16)for x in key.split(':')];op=word>>10;assert op in [0,1,47,55,57] and count==1
        rows.append(dict(address=pc,bytes=f'{word:04x}',size=2,assembly=f'Observed DSP op{op} r{(word>>5)&31},r{word&31}'))
    rows.sort(key=lambda r:r['address']);assert len(rows)==460 and [r['address']for r in rows]==list(range(0,0x398,2))
    prior_path=ROOT/'verification/CPU-IRQ-selection-DSP-experimental-candidate.json';prior=read(prior_path);original=Path(prior['directory'])
    out=ROOT/'verification/external-DSP-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    (out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes());save(out/'external-identities.json',rows)
    shutil.copy2(source,out/'biwn_external_arithmetic.c')
    body=(original/'biwn_dsp_music_engine.c').read_text();cases=[]
    for row in rows:
        word=int(row['bytes'],16);op=word>>10;m=(word>>5)&31;n=word&31;N=f's.registers[s.bank][{n}]';M=f's.registers[s.bank][{m}]'
        if op==1:code=f'case {hex(row["address"])}u: {N}=biwn_external_addc(&s,{N},{M});s.pc={hex(row["address"]+2)}u;break;'
        elif op==55:code=f'case {hex(row["address"])}u: {N}=biwn_external_mtoi({M});zn(&s,{N});s.pc={hex(row["address"]+2)}u;break;'
        else:code=generator.emit(row)
        code=code.replace('u:',f'u:biwn_DSP_last_operands[0]={m}u;biwn_DSP_last_operands[1]={n}u;',1);cases.append(code)
    body=once(body,'default:return BIWN_DSP_MUSIC_ENGINE_BAD_PC;','\n'.join(cases)+'\ndefault:return BIWN_DSP_MUSIC_ENGINE_BAD_PC;')
    rename=lambda t:t.replace('biwn_dsp_music_engine','biwn_dsp_external_engine').replace('BIWN_DSP_MUSIC_ENGINE','BIWN_DSP_EXTERNAL_ENGINE').replace('biwn_DSP_get_last_operands','biwn_external_last_operands')
    body=rename(body);(out/'biwn_dsp_external_engine.c').write_text(body)
    header=rename((original/'biwn_dsp_music_engine.h').read_text());header=once(header,'#endif','uint32_t biwn_external_addc(struct biwn_dsp_external_engine_state*,uint32_t,uint32_t);\nuint32_t biwn_external_mtoi(uint32_t);\n#endif');(out/'biwn_dsp_external_engine.h').write_text(header)
    bridge=rename((original/'DSP_music_bridge.c').read_text()).replace('biwn_DSP_music_','biwn_DSP_external_')
    identities=''.join('{'+str(row['address'])+',2,{'+','.join(str(x)for x in bytes.fromhex(row['bytes']))+'}},'for row in rows)
    bridge,count=re.subn(r'(static const struct identity identities\[\]=\{).*?(\};\nextern)',lambda m:m[1]+identities+m[2],bridge,count=1,flags=re.S);assert count==1
    bridge=once(bridge,'unsigned operands[2];','unsigned operands[2],j;')
    bridge=once(bridge,'if(pc<0xf1b000u||pc+i->size>0xf1d000u||memcmp(raw+pc-0xf1b000u,i->bytes,i->size))return fail(pc,92);','if(opcode!=((uint16_t)i->bytes[0]<<8|i->bytes[1]))return fail(pc,92);for(j=0;j<i->size;j++)if(H.read8(pc+j,2)!=i->bytes[j])return fail(pc,92);')
    (out/'DSP_external_bridge.c').write_text(bridge)
    def compile_library(name,sources,links=()):
        library=out/name;command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*map(str,sources),*map(str,links),'-o',str(library)]
        result=subprocess.run(command,capture_output=True,text=True);(out/(name+'.log')).write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr;return library
    external=compile_library('libDSP-external.dylib',[out/'DSP_external_bridge.c',out/'biwn_dsp_external_engine.c',out/'biwn_external_arithmetic.c'])
    router=(original/'DSP_program_router.c').read_text();router='extern int biwn_DSP_external_begin(const void*);\nextern int biwn_DSP_external_owner(unsigned,unsigned short,unsigned);\n'+router
    router=once(router,'if(match(music_identities,','if(pc<=0x396u){profile=3;result=biwn_DSP_external_owner(pc,opcode,unsupported);}\nelse if(match(music_identities,')
    router=once(router,'else P.media+=(unsigned)result;','else if(profile==2)P.media+=(unsigned)result;')
    router=once(router,'if(biwn_DSP_music_begin(h)||biwn_DSP_media_begin(h))','if(biwn_DSP_music_begin(h)||biwn_DSP_media_begin(h)||biwn_DSP_external_begin(h))')
    router=once(router,'S.uncovered++;return 0;','S.uncovered++;return -1; /* strict: never interpret an uncovered instruction */')
    (out/'DSP_program_router.c').write_text(router)
    library=compile_library('libDSP-external-router.dylib',[out/'DSP_program_router.c'],[Path(prior['music_library']),Path(prior['media_library']),external])
    candidate=dict(prior,status='compiled_external_DSP_pending_native_checks',directory=str(out),library=str(library),external_library=str(external),external_instructions=len(rows),strict_unknown_reject=True,
        source_sha256={str(p):sha(p)for p in [out/'runner-as-run.py',out/'external-identities.json',out/'biwn_external_arithmetic.c',out/'biwn_dsp_external_engine.c',out/'biwn_dsp_external_engine.h',out/'DSP_external_bridge.c',out/'DSP_program_router.c',external,library,Path(author['directory'])/'protocol.json',source,Path(observed['directory'])/'protocol.json',prior_path]},
        code_authorship=author.get('code_authorship','Local Code Author arithmetic helpers unedited; coordinator generated fixed observed cases, fences and integration. Existing music/media bodies retained. Not new original game functions or trained weights.'),new_training=False,runtime_promoted=False)
    save(out/'candidate.json',candidate);save(ROOT/'verification/external-DSP-experimental-candidate-current.json',candidate);print(out,flush=True)

if __name__=='__main__':main()
