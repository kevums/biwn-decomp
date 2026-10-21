"""Separate exact O2-lean install/component/resource drivers; no defaults changed."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
OLD='130639a231a37d872a52226927b30545cfef214f568377751de61897398d0c73'
def main():
    candidates=read(ROOT/'verification/native-format-optimization-builds-current.json');selected=next(x for x in candidates['candidates']if x['kind']=='O2-lean')
    bundle=read(selected['bundle_proof']);assert sha(bundle['binary'])==bundle['binary_sha256']and bundle['binary_bytes']==9042
    for p,h in bundle['source_sha256'].items():assert sha(p)==h,p
    bp=ROOT/'verification/native-optimized-format-bundle-current.json';save(bp,bundle)
    out=ROOT/'verification/native-optimized-format-preparation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    makefile=Path(bundle['directory'])/'Makefile';records=[]
    def write(parent,name,text,changes):
        path=ROOT/'scripts'/name;compile(text,str(path),'exec');path.write_text(text)
        (out/parent.name).write_bytes(parent.read_bytes());(out/name).write_bytes(path.read_bytes())
        records.append(dict(parent=str(parent),parent_sha256=sha(parent),derived=str(path),derived_sha256=sha(path),transformations=changes,tests_or_assertions_removed=False))
    for kind in ['controller','rng','tasks','scheduler','heap','copy','free','release','acquire','allocator','initialize','heap_witness','lifecycle','readiness']:
        parent=ROOT/'scripts'/f'check_biwn_native_load_scan_bundle_{kind}.py';text=parent.read_text();changes=[]
        if "'Makefile.load-scan-bundle'"in text:
            assert text.count("'Makefile.load-scan-bundle'")==text.count("'load-scan-bundle'")==1
            text=text.replace("'Makefile.load-scan-bundle'",repr(str(makefile))).replace("'load-scan-bundle'","'format-bundle'");changes.append('Select exact O2-lean Makefile/format-bundle target')
        if OLD in text:
            assert text.count(OLD)==1;text=text.replace(OLD,bundle['binary_sha256']);changes.append('Require exact O2-lean linked hash')
        text=text.replace('native-load-scan-bundle','native-optimized-format-bundle').replace('check_biwn_native_load_scan_bundle','check_biwn_native_optimized_format_bundle')
        # Output/proof names change; actual build artifacts retain their Makefile names.
        for suffix in ['', '.bin','.elf']:
            text=text.replace(repr('native-optimized-format-bundle'+suffix),repr('native-format-bundle'+suffix))
        text=text.replace('native-optimized-format-bundle.bin','native-format-bundle.bin').replace('native-optimized-format-bundle.elf','native-format-bundle.elf')
        changes.append('Separate output/proof and new dependency/import paths; preserve actual binary stem')
        if kind=='readiness':
            assert text.count('0x160bc0')==1 and text.count('7680')==2;text=text.replace('0x160bc0','0x1611c0').replace('7680','9216');changes.append('Same9216byte reserve and1611C0floor as selected build')
        if kind=='lifecycle':
            marker="payload=Path(g['compiled_binary']).read_bytes();assert sha(g['compiled_binary'])==g['compiled_binary_sha256'];";assert text.count(marker)==1
            text=text.replace(marker,marker+"assert g['compiled_binary_sha256']=="+repr(bundle['binary_sha256'])+";");changes.append('Strengthen exact linked hash assertion')
        write(parent,f'check_biwn_native_optimized_format_bundle_{kind}.py',text,changes)
    parent=ROOT/'scripts/check_biwn_native_load_kernel_readiness.py';text=parent.read_text()
    marker='verification/native-load-scan-bundle-linked-fixture-current.json';assert text.count(marker)==1
    text=text.replace(marker,'verification/native-optimized-format-bundle-linked-fixture-current.json')
    assert text.count('(7680 if combined else 6144)')==1;text=text.replace('(7680 if combined else 6144)','(9216 if combined else 6144)')
    marker="payload=binary.read_bytes();symbols=component['symbols'];";assert text.count(marker)==1
    text=text.replace(marker,marker+"assert component['compiled_binary_sha256']=="+repr(bundle['binary_sha256'])+";")
    write(parent,'check_biwn_native_optimized_format_loader_readiness.py',text,['Existing kernel-aware gate retained; select new layout/proof names,9216reserve and exact hash'])
    for old,new in [('build_biwn_native_format_disc.py','build_biwn_native_optimized_format_disc.py'),('check_biwn_native_format_disc_entry.py','check_biwn_native_optimized_format_disc_entry.py')]:
        parent=ROOT/'scripts'/old;text=parent.read_text().replace('native-format','native-optimized-format')
        write(parent,new,text,['Separate bundle/build/output proof names only; entry/reservation/rawCDI assertions unchanged'])
    report=dict(status='optimized_install_and_component_resource_drivers_prepared',directory=str(out),bundle=str(bp),bundle_sha256=sha(bp),binary_sha256=bundle['binary_sha256'],binary_bytes=9042,
                makefile=str(makefile),makefile_sha256=sha(makefile),drivers=records,source_accepted=False,whole_game_complete=False)
    save(out/'preparation.json',report);save(ROOT/'verification/native-optimized-format-preparation-current.json',report)
    print(out,flush=True)
def read(p):return json.loads(Path(p).read_text())
if __name__=='__main__':main()
