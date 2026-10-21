"""Derive exact new-build checks from the already-run optimization drivers.
Only artifact selection, expected new hashes/sizes and output names change.
"""
from pathlib import Path
from datetime import datetime,timezone
import json
from run_biwn_native_fast_gameplay_route import ROOT,sha,save


def main():
    source_bundle=ROOT/'verification/native-string-ccr-bundle-current.json';bundle=json.loads(source_bundle.read_text())
    assert bundle['binary_bytes']==8482 and sha(bundle['binary'])==bundle['binary_sha256']
    parent_path=Path(bundle['parent_bundle_proof']);parent=json.loads(parent_path.read_text())
    bp=ROOT/'verification/native-ccr-format-bundle-current.json';save(bp,bundle)
    out=ROOT/'verification/native-ccr-format-preparation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    records=[];makefile=Path(bundle['directory'])/'Makefile';old_make=Path(parent['directory'])/'Makefile'
    def write(name,new_name=None,extras=None):
        original=ROOT/'scripts'/name;text=original.read_text()
        text=text.replace('native-optimized-format','native-ccr-format').replace('native_optimized_format','native_ccr_format')
        text=text.replace(str(old_make),str(makefile)).replace(parent['binary_sha256'],bundle['binary_sha256'])
        text=text.replace(str(parent_path),str(bp))
        text=text.replace('binary_bytes=9042','binary_bytes=8482').replace('==9042','==8482').replace('Exact9042byte','Exact8482byte').replace('actual9042byte','actual8482byte')
        text=text.replace('bytes(174)','bytes(734)')
        if extras:
            for before,after in extras:
                assert before in text,(name,before);text=text.replace(before,after)
        target=ROOT/'scripts'/(new_name or name.replace('native_optimized_format','native_ccr_format'))
        compile(text,str(target),'exec');target.write_text(text)
        (out/('parent-'+name)).write_bytes(original.read_bytes());(out/target.name).write_bytes(target.read_bytes())
        records.append(dict(parent=str(original),parent_sha256=sha(original),derived=str(target),derived_sha256=sha(target),tests_or_assertions_removed=False))
    for kind in ['controller','rng','tasks','scheduler','heap','copy','free','release','acquire','allocator','initialize','heap_witness','lifecycle','readiness']:
        write(f'check_biwn_native_optimized_format_bundle_{kind}.py')
    write('check_biwn_native_optimized_format_loader_readiness.py')
    write('build_biwn_native_optimized_format_disc.py');write('check_biwn_native_optimized_format_disc_entry.py')
    write('check_optimized_format_integration.py','check_ccr_format_integration.py',[
        ('bytes(734)','bytes(734)')])
    for name,new_name in [('check_biwn_optimized_format_helpers.py','check_biwn_ccr_format_helpers.py'),('check_biwn_optimized_format_callers.py','check_biwn_ccr_format_callers.py')]:write(name,new_name)
    write('run_biwn_native_optimized_format_selector_deck_pair.py')
    # This read-only cost experiment has CLI-selected bundle/proof paths.
    write('replay_native_format_optimization_live_fixtures.py','replay_native_format_ccr_live_fixtures.py',[
        ('no new source/training/default/whole-game proof.','New typed-CCR source has separate full gates; no training/default/whole-game proof.')])
    write('run_format_optimized_long_routes.py','run_format_ccr_long_routes.py',[
        ("[('base','native-format'),('optimized','native-ccr-format')]","[('parent','native-optimized-format'),('ccr','native-ccr-format')]"),
        ("builds['optimized']","builds['ccr']"),("builds['base']","builds['parent']"),
        ('native-format-optimized-long-route','native-ccr-format-long-route')])
    result=dict(status='CCR_install_component_and_live_drivers_prepared',directory=str(out),bundle=str(bp),bundle_sha256=sha(bp),
                binary_sha256=bundle['binary_sha256'],binary_bytes=8482,makefile=str(makefile),makefile_sha256=sha(makefile),drivers=records,
                same_reservation_and_heap=True,new_training=False,default_promoted=False,whole_game_complete=False)
    save(out/'preparation.json',result);save(ROOT/'verification/native-ccr-format-preparation-current.json',result)
    print(out,flush=True)


if __name__=='__main__':main()
