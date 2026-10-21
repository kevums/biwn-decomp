"""Prepare new exact-payload tests; retain prior test matrices and assertions."""
from pathlib import Path
from datetime import datetime,timezone
import json,re
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
bundle_path=ROOT/'verification/native-unsigned-bundle-current.json';bundle=json.loads(bundle_path.read_text());parent_path=Path(bundle['parent_bundle_proof']);parent=json.loads(parent_path.read_text());assert bundle['binary_bytes']==8956
alias=ROOT/'verification/native-unsigned-format-bundle-current.json';save(alias,bundle)
out=ROOT/'verification/native-unsigned-format-preparation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);records=[]
oldmake=Path(parent['directory'])/'Makefile';newmake=Path(bundle['directory'])/'Makefile'
def derive(name,new_name=None,edits=()):
 old=ROOT/'scripts'/name;text=old.read_text();text=text.replace('native-ccr-format','native-unsigned-format').replace('native_ccr_format','native_unsigned_format').replace('CCR-format','unsigned-format')
 text=text.replace(str(oldmake),str(newmake)).replace(parent['binary_sha256'],bundle['binary_sha256']).replace(str(parent_path),str(alias))
 text=text.replace('8482','8956').replace('bytes(734)','bytes(260)')
 for before,after in edits:
  assert before in text,(name,before);text=text.replace(before,after)
 target=ROOT/'scripts'/(new_name or name.replace('native_ccr_format','native_unsigned_format'));compile(text,str(target),'exec');target.write_text(text)
 (out/('parent-'+name)).write_bytes(old.read_bytes());(out/target.name).write_bytes(target.read_bytes());records.append(dict(parent=str(old),parent_sha256=sha(old),derived=str(target),derived_sha256=sha(target)))
for kind in ['controller','rng','tasks','scheduler','heap','copy','free','release','acquire','allocator','initialize','heap_witness','lifecycle','readiness']:derive(f'check_biwn_native_ccr_format_bundle_{kind}.py')
derive('check_biwn_native_ccr_format_loader_readiness.py')
derive('build_biwn_native_ccr_format_disc.py',edits=[("[(0x1b160,'biwn_native_format_pad'),(0x1b1a8,'biwn_native_format_string')]","[(0x1b160,'biwn_native_format_pad'),(0x1b1a8,'biwn_native_format_string'),(0xe61c,'biwn_native_unsigned_divide'),(0xe67c,'biwn_native_unsigned_remainder')]")])
derive('check_biwn_native_ccr_format_disc_entry.py')
derive('check_ccr_format_integration.py','check_unsigned_format_integration.py')
# Reuse complete formatter cases, adding outer unsigned arithmetic call observation.
old=ROOT/'scripts/check_biwn_ccr_format_callers.py';text=old.read_text().replace('native-ccr-format','native-unsigned-format')
text=text.replace('HELPERS={0x1b160:4,0x1b1a8:8}','HELPERS={0x1b160:4,0x1b1a8:8,0xe61c:0,0xe67c:12}')
text=text.replace('if(pc==0x1b160||pc==0x1b1a8){if(active){out->status=5;return 5;}','if((pc==0x1b160||pc==0x1b1a8||pc==0xe61c||pc==0xe67c)&&!active){')
text=text.replace('[(0x1b160,0x1b1a0),(0x1b1a8,0x1b200)]','[(0x1b160,0x1b1a0),(0x1b1a8,0x1b200),(0xe61c,0xe67c),(0xe67c,0xe68c)]')
text=text.replace('[(0x1b160,6),(0x1b1a8,6)]','[(0x1b160,6),(0x1b1a8,6),(0xe61c,6),(0xe67c,6)]')
# Actual normalized() has separate inline tuples rather than the list above.
text=text.replace('(0x1b160,6),(0x1b1a8,6),','(0x1b160,6),(0x1b1a8,6),(0xe61c,6),(0xe67c,6),')
text=text.replace('if pc in HELPERS:\n            assert active is None','if pc in HELPERS and active is None:\n            assert active is None')
text=text.replace("[(0x1b160,'biwn_native_format_pad'),(0x1b1a8,'biwn_native_format_string')]","[(0x1b160,'biwn_native_format_pad'),(0x1b1a8,'biwn_native_format_string'),(0xe61c,'biwn_native_unsigned_divide'),(0xe67c,'biwn_native_unsigned_remainder')]")
text=text.replace('native-ccr-format-callers','native-unsigned-format-callers')
text=text.replace('Original complete formatter/format-core and original unsigned math execute, calling target-linked native pad/string.', 'Original formatter/core execute with target-linked pad/string and unsigned quotient/remainder C. Nested original E61C inside E67C is observed only at the outer helper boundary; direct math matrices separately compare both entry contracts.')
target=ROOT/'scripts/check_biwn_unsigned_format_callers.py';compile(text,str(target),'exec');target.write_text(text);(out/'parent-format-callers.py').write_bytes(old.read_bytes());(out/target.name).write_bytes(target.read_bytes());records.append(dict(parent=str(old),parent_sha256=sha(old),derived=str(target),derived_sha256=sha(target),observation_change='Original E67C nests E61C but compiled C shares a C body; compare outer helper boundaries, full return and ordered public access sequence. New direct math entries have separate full matrices.'))
# Exact linked unsigned tail; do not rebuild or change previously tested reference script.
old=ROOT/'scripts/check_biwn_native_unsigned_division.py';text=old.read_text();start=text.index("  cmd=['make'");end=text.index("  for line in subprocess.check_output",start)
replacement="""  bundle_path=ROOT/'verification/native-unsigned-bundle-current.json';bundle=json.loads(bundle_path.read_text());full=Path(bundle['binary']).read_bytes();assert sha(bundle['binary'])==bundle['binary_sha256']
  offset=bundle['symbols']['biwn_native_unsigned_divide']-bundle['base'];payload=full[offset:];assert len(payload)==474
  binary=out/'linked-tail.bin';binary.write_bytes(payload);elf=Path(bundle['ELF']);prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');symbols={}
"""
text=text[:start]+replacement+text[end:];text=text.replace("BASE=0x160000;SP=", "_bundle=json.loads((ROOT/'verification/native-unsigned-bundle-current.json').read_text());BASE=_bundle['symbols']['biwn_native_unsigned_divide'];SP=")
text=text.replace("default='reference'","default='linked-reference'").replace("args.label=='reference'","args.label=='linked-reference'")
text=text.replace("verification/native-unsigned-division-current.json","verification/native-unsigned-division-linked-current.json")
target=ROOT/'scripts/check_biwn_native_unsigned_division_linked.py';compile(text,str(target),'exec');target.write_text(text);(out/'parent-unsigned-checker.py').write_bytes(old.read_bytes());(out/target.name).write_bytes(target.read_bytes());records.append(dict(parent=str(old),parent_sha256=sha(old),derived=str(target),derived_sha256=sha(target),target_change='Run exact relocated474byte tail from8956byte linked payload, same3592normal/ordered and512zero fixtures.'))
# Finite gameplay runners: new candidate vs its immediate parent.
derive('run_biwn_native_ccr_format_selector_deck_pair.py',edits=[])
derive('run_format_ccr_long_routes.py','run_format_unsigned_long_routes.py',[
 ("[('parent','native-optimized-format'),('ccr','native-unsigned-format')]","[('parent','native-ccr-format'),('unsigned','native-unsigned-format')]"),
 ("builds['ccr']","builds['unsigned']")])
state=dict(status='unsigned_install_component_and_gameplay_drivers_prepared',directory=str(out),bundle=str(alias),bundle_sha256=sha(alias),binary_sha256=bundle['binary_sha256'],binary_bytes=8956,makefile=str(newmake),makefile_sha256=sha(newmake),drivers=records,same_reservation_and_heap=True,new_training=False,default_promoted=False,whole_game_complete=False)
save(out/'preparation.json',state);save(ROOT/'verification/native-unsigned-format-preparation-current.json',state);print(out)
