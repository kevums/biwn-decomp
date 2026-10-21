"""Revalidate inline-specialized image with unchanged full matrices/layout."""
import json
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def main():
 bp=ROOT/'verification/native-fast-core-format-bundle-current.json';bundle=json.loads(bp.read_text());pp=Path(bundle['parent_bundle_proof']);parent=json.loads(pp.read_text());out=ROOT/'verification/native-fast-core-format-preparation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);records=[]
 oldmake=str(Path(parent['directory'])/'Makefile');newmake=str(Path(bundle['directory'])/'Makefile')
 def transform(text):return text.replace('native-core-format','native-fast-core-format').replace('native_core_format','native_fast_core_format').replace('check_core_format_integration','check_fast_core_format_integration').replace(oldmake,newmake).replace(parent['binary_sha256'],bundle['binary_sha256']).replace('15408',str(bundle['binary_bytes'])).replace('bytes(976)','bytes('+str(bundle['padding_bytes'])+')')
 def emit(name,newname=None,edits=()):
  old=ROOT/'scripts'/name;text=transform(old.read_text())
  for a,b in edits:assert a in text,(name,a);text=text.replace(a,b)
  target=ROOT/'scripts'/(newname or name.replace('core_format','fast_core_format'));compile(text,str(target),'exec');target.write_text(text)
  (out/('parent-'+name)).write_bytes(old.read_bytes());(out/target.name).write_bytes(target.read_bytes());records.append(dict(parent=str(old),parent_sha256=sha(old),derived=str(target),derived_sha256=sha(target)))
 for kind in ['controller','rng','tasks','scheduler','heap','copy','free','release','acquire','allocator','initialize','heap_witness','lifecycle','readiness']:emit(f'check_biwn_native_core_format_bundle_{kind}.py')
 emit('check_biwn_native_core_format_loader_readiness.py')
 emit('check_biwn_native_core_format_disc_entry.py')
 emit('check_core_format_integration.py','check_fast_core_format_integration.py')
 emit('build_biwn_native_core_format_disc.py')
 emit('check_biwn_core_format_helpers.py')
 emit('check_biwn_core_format_math_linked.py')
 for kind in ['number','core']:
  emit(f'check_biwn_core_format_{kind}_linked.py',edits=[('  paths.append(bundle_path)',"  paths.append(bundle_path);paths += [Path(p)for p in bundle['optimized_sources'].values()]+[Path(bundle['optimized_header'])]")])
 state=dict(status='inline_formatter_full_exact_layout_drivers_prepared',directory=str(out),bundle=str(bp),bundle_sha256=sha(bp),binary_sha256=bundle['binary_sha256'],binary_bytes=bundle['binary_bytes'],makefile=newmake,makefile_sha256=sha(newmake),drivers=records,same_reservation_and_heap=True,heap_start=bundle['heap_start'],reserved_bytes=bundle['reserved_bytes'],staging=bundle['staging'],staging_clear_bytes=bundle['staging_clear_bytes'],new_training=False,default_promoted=False,whole_game_complete=False)
 save(out/'preparation.json',state);save(ROOT/'verification/native-fast-core-format-preparation-current.json',state);print(out)
if __name__=='__main__':main()
