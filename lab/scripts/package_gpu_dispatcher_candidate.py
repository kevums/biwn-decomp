"""Wrap unchanged local31case bodies in a fixed coordinator-owned C engine."""
import hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path
import package_gpu6380_candidate as prior
ROOT=prior.ROOT
def main():
    author=Path(json.loads((ROOT/'verification/GPU-dispatcher-local-author-current.json').read_text())['directory']);body=(author/'candidate-cases.txt').read_text();session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'gpu-dispatcher-loop/source-decode.json').read_text());expected=[r['address']for r in mapping['rows']]
    plain=re.sub(r'/\*.*?\*/|//[^\n]*','',body,flags=re.S);assert not any(v in plain for v in ['#','"',"'",'`']);found=[int(v,16)for v in re.findall(r'case\s+(0x[0-9a-fA-F]+)u?\s*:',plain)];assert found==expected
    assert not re.search(r'\bs\.(pending|target)\b',plain), 'Branch controls are engine locals, not state members'
    allowed={'case','s','registers','pc','z','c','n','v','pending','target','bus','CHECK','rd32','wr32','add','sub','condition','if','else','break','void','uint32_t'};identifiers=set(re.findall(r'\b[A-Za-z_]\w*\b',re.sub(r'0x[0-9a-fA-F]+[uU]?|\b\d+[uU]?','0',plain)));assert identifiers<=allowed,identifiers-allowed
    def rename(s):return s.replace('consumer6380','dispatcher').replace('CONSUMER6380','DISPATCHER')
    header=rename(prior.HEADER).replace(' int (*read16)(void *,uint32_t,uint16_t *);\n','');a=header.index('/* Fixed original');b=header.index('enum biwn_gpu_dispatcher_status biwn_gpu_dispatcher_run',a)
    header=header[:a]+'''/* Original31-instruction dispatcher loop F031BE..F03200, bank0.
 * Caller supplies finite valid program headers/payloads and complete GPU/main
 * RAM bus. Return at external program entry or, when yield_idle=1, idle poll
 * F031CE with mailboxFFFF and busy0, matching the draw host's stop boundary.
 * yield_idle=0 follows source polling; caller/device supplies any commands.
 * No program execution, full mainGPUboot, timing/interrupt or fullgame claim.
 * Errors preserve input state but retain prior external stores.
 */
'''+header[b:];header=header.replace('state *,uint32_t);','state *,uint32_t,uint32_t);').replace('void (*observe_PC)(void *,uint32_t);','void (*observe_PC)(void *,uint32_t,uint32_t,uint32_t,uint32_t);')
    prefix=rename(prior.PREFIX);prefix='\n'.join(line for line in prefix.splitlines()if not line.startswith('static int loadw('))+'\n';prefix=prefix.replace('uint32_t budget){','uint32_t budget,uint32_t yield_idle){').replace('!bus->read16||','').replace('!bus||!state||!budget||','!bus||!state||!budget||yield_idle>1||')
    prefix=prefix.replace('pending=0;if(!delayed&&bus->observe_PC)', 'pending=0;if(!delayed&&yield_idle&&s.pc==0xf031ceu){CHECK(rd32(bus,0xf03204u,&v));if(v==0xffffffffu){CHECK(rd32(bus,0xf03200u,&v));if(v==0){*state=s;return BIWN_GPU_DISPATCHER_OK;}}}if(!delayed&&bus->observe_PC)')
    prefix=prefix.replace('bus->observe_PC(bus->context,s.pc);','bus->observe_PC(bus->context,s.pc,s.z,s.c,s.n);')
    suffix=rename(prior.SUFFIX).replace('s.pc==0xf031beu||s.pc==0xf03440u||s.pc==0xf03ca0u','s.pc<0xf031beu||s.pc>=0xf03200u')
    # All source operations here use add/sub/condition. No Z/N-only helper.
    # add/sub still call zn internally, so retain its implementation.
    out=author/'candidate';out.mkdir(exist_ok=True);(out/'biwn_gpu_dispatcher.h').write_text(header);(out/'biwn_gpu_dispatcher.c').write_text(prefix+body+'\n'+suffix)
    report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='packaged_unverified',directory=str(out),author_directory=str(author),case_bodies_sha256=hashlib.sha256(body.encode()).hexdigest(),coordinator_edited_case_bodies=False,local_model='advertising-scholar/local27Bbase',coordinator_authored='interface, fixed engine and host idle boundary, primitives, typed source operands, native observer, fixtures and tests',source_instructions=31,payload_sha256=mapping['payload_sha256'],source_sha256={name:hashlib.sha256((out/name).read_bytes()).hexdigest()for name in ['biwn_gpu_dispatcher.c','biwn_gpu_dispatcher.h']},full_main_GPU_program_reconstructed=False,full_renderer_C=False)
    provenance_path=author/'case-block-provenance.json'
    if provenance_path.exists():
        provenance=json.loads(provenance_path.read_text());report.update(case_block_provenance=str(provenance_path),coordinator_assembled_by_source_PC=True,coordinator_added_case_labels=[r['PC']for r in provenance if r.get('coordinator_added_case_label')],model_instruction_text_edited_by_coordinator=False)
    (out/'package.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
