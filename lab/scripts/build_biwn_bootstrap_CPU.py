"""Extend the experimental C CPU with fixed initial-disc loader instructions."""
import json,subprocess
from datetime import datetime,timezone
from pathlib import Path
import capstone
import generate_biwn_atomic_startup_math as math
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(path):return json.loads(Path(path).read_text())

def main():
    ip=ROOT/'verification/pre-mainstage-CPU-inventory-current.json';observed=read(ip);assert observed['status']=='terminal_read_only_bootstrap_inventory_equal'
    inventory=read(Path(observed['directory'])/'reference/bootstrap-instructions.json')
    dp=ROOT/'verification/CPU-division-fresh-gameplay-current.json';division=read(dp);assert division['status']=='terminal_fresh_division_gameplay_equal'
    cp=Path(division['directory'])/'CPU-candidate.json';base=read(cp)
    out=ROOT/'verification/bootstrap-CPU-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);(out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes());print(out,flush=True)
    atlas=bytearray(Path(base['instruction_RAM_source']).read_bytes());entry=Path(observed['directory'])/'reference/main-entry-RAM.bin';ram=entry.read_bytes()
    atlas[0x180000:0x180188]=ram[0x180000:0x180188]
    for row in inventory['instructions']:
        pc=int(row['address'],16);code=bytes.fromhex(row['bytes']);assert ram[pc:pc+len(code)]==code
        atlas[pc:pc+len(code)]=code
    atlasp=out/'bootstrap-instruction-atlas.bin';atlasp.write_bytes(atlas)
    decoder=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
    instructions=[];last=0x180000
    for ins in decoder.disasm(bytes(atlas[0x180000:0x180188]),0x180000):
        assert ins.address==last;last+=ins.size;assert not ins.mnemonic.startswith('dc.')
        row=math.base.binary_tools.m68k_instructions(bytes(ins.bytes),ins.address)[0][0]
        instructions.append(dict(address=hex(ins.address),bytes=row['bytes'],size=row['size'],assembly=row['assembly']))
    assert last==0x180188
    for row in inventory['instructions']:
        if int(row['address'],16)<0x180000:instructions.append({k:row[k]for k in ['address','bytes','size','assembly']})
    listing=out/'static-listing.json';save(listing,dict(instructions=instructions,scope='Fixed CPU loader[180000,180188) plus observed HLE RTS sites. Includes statically decoded unexecuted branch arms; static entries are not execution coverage.'))
    candidate=out/'CPU-candidate.json';reference=Path(base['warm_RAM_source']).parent
    command=[str(ROOT/'.venv/bin/python'),'-u',str(ROOT/'scripts/build_biwn_route_CPU.py'),'--reference',str(reference),'--output-manifest',str(candidate),'--base-candidate',str(cp),'--static-listing',str(listing),'--instruction-RAM',str(atlasp),'--function','biwn_bootstrap_and_game_CPU_step','--movie-privileged-events']
    result=subprocess.run(command,capture_output=True,text=True);(out/'CPU-build.log').write_text(result.stdout+result.stderr)
    if result.returncode:
        state=dict(status='terminal_bootstrap_CPU_requires_additional_semantics',directory=str(out),command=command,returncode=result.returncode,compiler_output=result.stdout+result.stderr,new_training=False,default_promoted=False)
        save(out/'build.json',state);save(ROOT/'verification/bootstrap-CPU-build-current.json',state);print(result.stdout+result.stderr,flush=True);return
    built=read(candidate);nativep=out/'native-CPU-candidate.json';cost=read(ROOT/'verification/CPU-division-provider-build-current.json')['cost_candidate']
    private=ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source'
    command2=[str(ROOT/'.venv/bin/python'),'-u',str(ROOT/'scripts/build_biwn_fast_CPU_bridge.py'),'--CPU-candidate',str(candidate),'--candidate-output',str(nativep),'--CPU-private-source',str(private),'--cost-candidate',cost]
    result=subprocess.run(command2,capture_output=True,text=True);(out/'bridge-build.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stdout+result.stderr;native=read(nativep)
    state=dict(status='terminal_bootstrap_CPU_compiled_pending_execution',directory=str(out),CPU_candidate=str(candidate),native_CPU_candidate=str(nativep),
        observed_unique_instructions=77,static_instruction_entries=len(instructions),new_static_cases=len(built['selected_case_sources'])-len(base['selected_case_sources']),
        atlas_is_not_runtime_state=True,source_sha256={str(p):sha(p)for p in [out/'runner-as-run.py',ip,dp,cp,Path(base['library']),entry,atlasp,listing,ROOT/'scripts/build_biwn_route_CPU.py',ROOT/'scripts/build_biwn_fast_CPU_bridge.py',candidate,Path(built['library']),Path(built['directory'])/'biwn_route_CPU.c',nativep,Path(native['library']),Path(native['directory'])/'fast_CPU_bridge.c',Path(cost)]},
        scope='Static C translation for fixed initial loader plus prior game providers. Unexecuted branch arms not validated. HLE functions/clock/device services remain original; no whole-game/physical or training claim.',new_training=False,default_promoted=False)
    save(out/'build.json',state);save(ROOT/'verification/bootstrap-CPU-build-current.json',state);print(json.dumps({k:state[k]for k in ['status','observed_unique_instructions','static_instruction_entries','new_static_cases','native_CPU_candidate']}),flush=True)

if __name__=='__main__':main()
