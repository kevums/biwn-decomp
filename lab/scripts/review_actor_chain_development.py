"""Review a shared C ABI refactor without promoting it as gameplay-tested."""
import json
from pathlib import Path
from datetime import datetime,timezone
import capstone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save


def read(p):return json.loads(Path(p).read_text())


def main():
    v=ROOT/'verification'
    out=v/'actor-chain-development-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    names=['native-actor-chain-current.json','native-actor-chain-final-current.json','actor-chain-contexts-current.json','actor-chain-source-defects-current.json','native-actor-chain-build-normalized-current.json','actor-chain-final-startup-current.json']
    records={};deps={}
    for name in names:
        obj=read(v/name);save(out/name,obj);deps[str(out/name)]=sha(out/name)
        for p,h in obj.get('source_sha256',{}).items():
            assert sha(p)==h,p
            deps[p]=h
        records[name]=obj
    prototype,final,contexts,defects,build,startup=[records[n]for n in names]
    assert all(g['collision_cases']==5120 and g['movement_cases']==2560 and g['binary_bytes']==5188 for g in[prototype,final])
    assert final['code_address']==0x16489c and build['linked_component_bytes']==28448 and build['free_reserved_bytes']==96
    assert contexts['cases']==7680 and contexts['completed']==15360 and contexts['max_native_private_depth']==564 and contexts['minimum_headroom']==354
    assert len(contexts['negative_controls'])==5 and len(defects['controls'])==2 and startup['cases']==96
    baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();decoder=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
    sites={ins.address for ins in decoder.disasm(baseline[0x13b5a:0x13f12],0x13b5a)}
    assert sites==set(final['original_sites'])and len(sites)==301
    old=read(v/'native-movement-collision-joint-current.json')
    a=read(Path(old['directory'])/'results.json');b=[row for row in read(Path(final['directory'])/'results.json')if row['group']=='movement']
    assert read(Path(old['directory'])/'fixtures.json')==read(Path(final['directory'])/'movement-fixtures.json')
    assert all(x['original_steps']==y['original_steps']for x,y in zip(a,b))
    steps=dict(cases=len(a),old_separate_wrappers=sum(row['compiled_steps']for row in a),shared_C_chain=sum(row['candidate_steps']for row in b),scope='Finite matched movement fixtures with prescribedE220GPUeffects,notliveFPSorwholegameperformance')
    save(out/'matched-fixture-step-counts.json',steps)
    report=out/'review.txt'
    report.write_text('SOURCE-OWNED MOVEMENT / COLLISION C CALL CHAIN\n\n'
        'This refactors the three already-reconstructed roots13C9A/13B5A/13BB0; it does not add newly recovered game functions. Movement now invokes collision through a C pointer ABI with one shared80byte context. Original-facing public roots and remaining actual direction/geometry/GPU helper boundaries remain. Internal collision entry compares shadowCPU state to original physicalentry; it is not an assertion of physical C-ABI register equality.\n\n'
        'Prototype/final-address matrices eachpass7,680cases:5,120directcollision+2,560movement,coveringall301original instruction sites. FullreturnedCPU/SR/banks/public2MBRAM/orderedaccess and actual remaining helperCPU/SP/SR/arguments match. OnlyE220effects prescribed in movementfixtures; directcollisionhasnoprescribedhelpers. Finalsharedcode5,188bytes at16489C.\n\n'
        '15,360original/C native executions qualify sharedcontext/taskheader/lowerguard checks,8,969physicalcontextchecks and1,094virtualcollision checks. Native maxprivate564versusprior894; minimum354bytes headroom at the same918byte root allowance,versusprior24. Five decoded-observation corruptions reject without changing nativeCPU/RAM. Two actual compiled virtualJSR-width/geometry-anchor defects reject in bounded guest execution; correct fixture also matches original in nativeCPU.\n\n'
        'Matched fixture instruction totals: '+json.dumps(steps)+'. This is approximately0.47%fewer instructions over this finite movement matrix,not a demonstrated gameplay speedup.\n\n'
        'New development CDI uses28,448residentbytes,28,544reservation/free96,unchangedheap165D40/stagingF7000/trailer and first23,260residentbytes.4,511changedCDIbytes confined to declaredtail/entryregions; parent and originaluserCDI unchanged.96completepayload startup cases pass.\n\n'
        'Fresh actual gameplay and a monitor aware of the sharedcontext/virtualCboundaries remain pending. OldmovementmonitorassumesrootSP-488/72bytes and physicalcollisionentry; do not reuse it unchanged. Newcontext isrootSP-360/80bytes for movement,with320private reserve. The unnormalized build receipt retains obsolete inherited standaloneinterval fields; use the separate normalized build metadata, preserving the original96case startup receipt.\n\n'
        'Latest published gameplay-tested disc remains28,380bytes. The visible preview remains older/unchanged. Retained native emulator processors/platform/HLE, timing/media/state disagreements, indoorlivecoverage0 and fullreadablegame/sameconsole/physicalconsole limits remain. Coordinator code/integration; no new localAuthor output, training or weights.\n')
    deps[str(report)]=sha(report);deps[str(Path(__file__))]=sha(Path(__file__));deps[str(out/'matched-fixture-step-counts.json')]=sha(out/'matched-fixture-step-counts.json')
    result=dict(status='terminal_source_owned_actor_chain_component_startup_pass_gameplay_pending',directory=str(out),report=str(report),latest_built_resident_bytes=28448,latest_published_gameplay_resident_bytes=28380,prototype_cases=7680,final_cases=7680,original_instruction_sites=301,context_executions=15360,physical_context_checks=8969,virtual_collision_checks=1094,max_native_private_depth=564,minimum_fixture_headroom=354,prior_nested_private_depth=894,prior_fixture_headroom=24,startup_cases=96,matched_instruction_counts=steps,normalized_build=str(v/'native-actor-chain-build-normalized-current.json'),new_functions_recovered=False,new_training=False,new_local_code_adopted=False,gameplay_tested=False,default_promoted=False,dependencies_sha256=deps,scope=__doc__)
    save(out/'protocol.json',result);save(v/'actor-chain-development-reviewed-current.json',result)
    print(json.dumps({k:result[k]for k in['status','latest_built_resident_bytes','max_native_private_depth','minimum_fixture_headroom']}))


if __name__=='__main__':main()
