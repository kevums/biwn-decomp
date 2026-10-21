"""Review bounded ABI/compiler development measurements and linked source gates."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def read(p):return json.loads(Path(p).read_text())
def main():
    v=ROOT/'verification';gp=v/'native-geometry-select-lean-current.json';bp=v/'native-geometry-select-lean-disc-build-current.json';gate,build=read(gp),read(bp)
    assert gate['status']=='terminal_native_geometry_select_lean_CPU_RAM_ordered_pass' and gate['source_accepted']
    assert(gate['native_cases'],gate['changing_coordinate_cases'],gate['binary_bytes'],gate['max_private_stack_bytes'])==(1280,512,298,64)
    assert build['status']=='terminal_native_geometry_select_lean_disc_built_entry_verified_pending_gameplay'
    assert(build['linked_component_bytes'],build['component_bytes'],build['linked_native_cases'],build['linked_changing_coordinate_cases'],build['entry_cases'])==(17382,20480,1280,512,96)
    proof_paths=[v/'native-geometry-select-tagged-addresses-current.json',v/'native-geometry-select-lean/20261019T045831.015743Z/protocol.json',gp,v/'native-geometry-select-lean-O2-current.json']
    labels=['original 324-byte scalar ABI','326-byte lean scalar ABI','298-byte typed lean ABI, Os','316-byte typed lean ABI, O2']
    proofs=[read(p)for p in proof_paths];measurements=[];baseline_fixtures=None;baseline_CPU=None
    for label,p in zip(labels,proofs):
        folder=Path(p['directory']);fixtures=read(folder/'fixtures.json');stable=read(folder/'results.json');changing=read(folder/'changing-coordinate-results.json')
        assert len(stable)==1280 and len(changing)==512 and p['original_instruction_coverage']==[46,46]
        states=[x['CPU']for x in stable+changing]
        if baseline_fixtures is None:baseline_fixtures=fixtures;baseline_CPU=states
        else:assert fixtures==baseline_fixtures and states==baseline_CPU,'Compare identical development inputs and complete outputs'
        measurements.append(dict(variant=label,proof=str(folder/'protocol.json'),bytes=p['binary_bytes'],private_stack=p['max_private_stack_bytes'],stable_cases=1280,changing_cases=512,original_cycle_sum=sum(x['original_cycles']for x in stable+changing),compiled_cycle_sum=sum(x['native_cycles']for x in stable+changing),success_fixture_original_cycles=stable[1]['original_cycles'],success_fixture_compiled_cycles=stable[1]['native_cycles']))
    selected=measurements[2];assert all(selected['compiled_cycle_sum']<=m['compiled_cycle_sum']for m in measurements)
    now=datetime.now(timezone.utc);out=v/'native-geometry-select-lean-reviewed'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={};aliases={}
    def bind(p,expected=None):
        p=Path(p).resolve();assert p.is_relative_to(ROOT);h=sha(p);assert expected is None or expected==h,str(p);q=p
        if p.name.endswith(('-current.json','-active.json')):
            q=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,q);aliases[str(p)]=str(q)
        deps[str(q)]=h
    for p in [gp,bp,*proof_paths]:bind(p)
    for proof in proofs:
        for p,h in proof['dependencies_sha256'].items():bind(p,h)
        for p in Path(proof['directory']).rglob('*'):
            if p.is_file():bind(p)
    for p,h in build['source_sha256'].items():bind(p,h)
    for p in Path(build['directory']).rglob('*'):
        if p.is_file() and p.suffix!='.cdi':bind(p)
    bind(build['derived_disc'],build['derived_disc_sha256'])
    for p in [Path(__file__),ROOT/'reports/native-geometry-select-prompts-and-responses.txt',ROOT/'reports/native-geometry-select-prediction-index.json',ROOT/'scripts/run_biwn_native_geometry_select_lean_route.py',ROOT/'scripts/check_biwn_scheduler.py',ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib']:bind(p)
    save(out/'development-component-costs.json',measurements);bind(out/'development-component-costs.json')
    reduction=1-selected['compiled_cycle_sum']/measurements[0]['compiled_cycle_sum'];report=ROOT/'reports/native-geometry-select-lean.txt'
    report.write_text('BIWN — LEAN NATIVE INDEXED SELECTOR\n'+now.isoformat()+'\n\n'
      'The coordinator selector now uses an explicit68000 object/header/record field layout and a smaller private register ABI. All field offsets and two-byte object alignment are compile-time checked. Volatile public access widths/order, signed16 gates/indices, partial registers, X/CCR and32bit tagged pointer values remain intact. The guest bus resolves addresses through24bits. No original opcode service replaces the C implementation.\n\n'
      'Four bounded development variants were measured on identical1280stable+512changing fixtures with identical full CPU outputs and original instruction coverage46/46. All passed native CPU/public-RAM and ordered-access gates. Selected Os typed variant:298bytes and64bytes private stack, versus324bytes and112bytes for the first accepted coordinator port. O2 passed but used316bytes/72stack and more measured cycles than Os; it was not selected.\n\n'
      f'Across the1792controlled cases, selected compiled cycle sum is {selected["compiled_cycle_sum"]:,}, versus {measurements[0]["compiled_cycle_sum"]:,} for the324byte version ({reduction:.2%} reduction). A successful fixture used1104cycles versus1290before and628for the original. These are pinned-emulator instruction charges in development component tests, not physical timing or a whole-game speedup. The compiled implementation remains slower than original in these measurements.\n\n'
      'The exact final-address selector also passed1280stable+512changing checks and96startup checks. Its isolated derived disc contains17,382resident bytes in the same20,480byte reservation after the unchanged17,084byte boundary parent. Heap floor and original CDI remain unchanged. Fresh retained-native candidate/original-entry gameplay comparisons are separate; their visual/audio/state agreement is measured, not inferred from these component results. No preview promotion or full console rebuild.\n\n'
      'All accepted C/ABI, compiler experiments, fixtures and integration are coordinator work. The earlier local Author and one repair both failed; the two same-weight reviews were unreliable. No new local game-code prediction or weights were produced by this optimization. Native Chat display remains unverified.\n')
    bind(report)
    result=dict(status='terminal_native_geometry_select_lean_component_final_address_costs_reviewed',recorded_at=now.isoformat(),directory=str(out),report=str(report),component=str(gp),build=str(bp),derived_disc=build['derived_disc'],derived_disc_sha256=build['derived_disc_sha256'],native_bytes=298,resident_bytes=17382,private_stack_bytes=64,stable_cases=1280,changing_cases=512,startup_cases=96,measurements=measurements,selected_compiled_cycle_reduction=reduction,source=gate['source'],source_sha256=gate['source_sha256'],authorship='Coordinator C/ABI/checks; no accepted local source',dependencies_sha256=deps,pointer_snapshots=aliases,new_training=False,native_Chat_verified=False,default_promoted=False,whole_game_complete=False,whole_game_speedup_demonstrated=False)
    save(out/'protocol.json',result);save(v/'native-geometry-select-lean-reviewed-current.json',result);print(json.dumps({k:result[k]for k in ['status','resident_bytes','native_bytes','selected_compiled_cycle_reduction','report']}),flush=True)
if __name__=='__main__':main()
