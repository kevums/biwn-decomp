"""Derive resource/lifecycle gates for the exact format payload and heap floor."""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
OLD_SHA='130639a231a37d872a52226927b30545cfef214f568377751de61897398d0c73'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def main():
    bp=ROOT/'verification/native-format-bundle-current.json';b=json.loads(bp.read_text())
    dp=ROOT/'verification/native-format-disc-build-current.json';d=json.loads(dp.read_text())
    assert sha(b['binary'])==b['binary_sha256']
    assert d['linked_component']==b['binary'] and d['linked_component_bytes']==b['binary_bytes']==8742
    assert d['component_bytes']==b['reserved_bytes']==9216
    assert d['heap_start']==b['heap_start']==0x1611c0
    assert sha(d['patch_manifest'])==d['patch_manifest_sha256']
    padded=Path(d['component']).read_bytes()
    assert padded==Path(b['binary']).read_bytes()+bytes(b['padding_bytes'])
    out=ROOT/'verification/native-format-resource-preparation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    layout=dict(status='checked_exact_format_payload_fixture_metadata_not_a_new_game_run',
                resident_address=b['base'],heap_start=b['heap_start'],component_bytes=b['reserved_bytes'],
                component=d['component'],component_sha256=sha(d['component']),symbols=b['symbols'],
                patch_manifest=d['patch_manifest'],patch_manifest_sha256=d['patch_manifest_sha256'],
                bundle_proof=str(bp),bundle_proof_sha256=sha(bp),disc_proof=str(dp),disc_proof_sha256=sha(dp))
    lp=ROOT/'verification/native-format-bundle-linked-fixture-current.json';save(lp,layout);save(out/'linked-fixture.json',layout)
    target=dict(status='exact_format_linked_payload_for_existing_loader_matrix',binary=b['binary'],
                binary_sha256=b['binary_sha256'],symbols=b['symbols'],resident_base=b['base'],
                bundle_proof=str(bp),bundle_proof_sha256=sha(bp),whole_game_complete=False)
    tp=ROOT/'verification/native-format-loader-target-current.json';save(tp,target);save(out/'loader-target.json',target)
    records=[]
    for kind in ['acquire','allocator','initialize','heap_witness','lifecycle','readiness']:
        parent=ROOT/'scripts'/f'check_biwn_native_load_scan_bundle_{kind}.py';source=parent.read_text();text=source
        transforms=[]
        if "'Makefile.load-scan-bundle'" in text:
            assert text.count("'Makefile.load-scan-bundle'")==text.count("'load-scan-bundle'")==1
            text=text.replace("'Makefile.load-scan-bundle'",repr(str(Path(b['directory'])/'Makefile'))).replace("'load-scan-bundle'","'format-bundle'")
            transforms.append('Select new Makefile/format-bundle target')
        if OLD_SHA in text:
            assert text.count(OLD_SHA)==1
            text=text.replace(OLD_SHA,b['binary_sha256']);transforms.append('Require exact new linked binary hash')
        text=text.replace('native-load-scan-bundle','native-format-bundle').replace('check_biwn_native_load_scan_bundle','check_biwn_native_format_bundle')
        transforms.append('Separate outputs/binary stem and point dependencies/imports at new exact-build gates')
        if kind=='readiness':
            assert text.count('0x160bc0')==1 and text.count('7680')==2
            text=text.replace('0x160bc0','0x1611c0').replace('7680','9216')
            transforms.append('Assert new exact heap floor/reservation; update scope number only')
        if kind=='lifecycle':
            old="payload=Path(g['compiled_binary']).read_bytes();assert sha(g['compiled_binary'])==g['compiled_binary_sha256'];"
            assert text.count(old)==1
            text=text.replace(old,old+"assert g['compiled_binary_sha256']=="+repr(b['binary_sha256'])+";")
            transforms.append('Strengthen full lifecycle proof to require the exact new hash')
        path=ROOT/'scripts'/f'check_biwn_native_format_bundle_{kind}.py';compile(text,str(path),'exec');path.write_text(text)
        (out/parent.name).write_bytes(parent.read_bytes());(out/path.name).write_bytes(path.read_bytes())
        records.append(dict(kind=kind,parent=str(parent),parent_sha256=sha(parent),derived=str(path),derived_sha256=sha(path),transformations=transforms,test_vectors_or_assertions_removed=False))
    parent=ROOT/'scripts/check_biwn_native_load_kernel_readiness.py';source=parent.read_text()
    needle='verification/native-load-scan-bundle-linked-fixture-current.json';assert source.count(needle)==1
    text=source.replace(needle,'verification/native-format-bundle-linked-fixture-current.json')
    assert text.count('(7680 if combined else 6144)')==1
    text=text.replace('(7680 if combined else 6144)','(9216 if combined else 6144)')
    needle="payload=binary.read_bytes();symbols=component['symbols'];"
    assert text.count(needle)==1
    text=text.replace(needle,needle+"assert component['compiled_binary_sha256']=="+repr(b['binary_sha256'])+";")
    path=ROOT/'scripts/check_biwn_native_format_loader_readiness.py';compile(text,str(path),'exec');path.write_text(text)
    (out/parent.name).write_bytes(parent.read_bytes());(out/path.name).write_bytes(path.read_bytes())
    records.append(dict(kind='loader_readiness',parent=str(parent),parent_sha256=sha(parent),derived=str(path),derived_sha256=sha(path),transformations=['Use existing kernel-aware parent, retaining its exact ELF/object-derived scan ownership range','Use exact new layout proof','Assert new9216byte reservation','Strengthen component hash assertion'],test_vectors_or_assertions_removed=False))
    report=dict(status='resource_lifecycle_exact_build_drivers_prepared',directory=str(out),binary_sha256=b['binary_sha256'],binary_bytes=8742,
                heap_start=b['heap_start'],reservation_bytes=9216,drivers=records,
                bundle_proof=str(bp),bundle_proof_sha256=sha(bp),layout=str(lp),layout_sha256=sha(lp),loader_target=str(tp),loader_target_sha256=sha(tp),
                whole_game_complete=False,source_accepted=False)
    save(out/'preparation.json',report);save(ROOT/'verification/native-format-resource-preparation-current.json',report)
    print(json.dumps(dict(status=report['status'],directory=str(out),drivers=len(records)),indent=2))
if __name__=='__main__':main()
