"""Fresh exact-layout drivers for complete native formatter; retain matrices."""
import json
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def main():
 bp=ROOT/'verification/native-core-format-bundle-current.json';bundle=json.loads(bp.read_text());pp=Path(bundle['parent_bundle_proof']);parent=json.loads(pp.read_text());assert bundle['binary_bytes']==15408
 out=ROOT/'verification/native-core-format-preparation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);records=[]
 oldmake=str(Path(parent['directory'])/'Makefile');newmake=str(Path(bundle['directory'])/'Makefile')
 def transform(text):
  return text.replace('native-number-format','native-core-format').replace('native_number_format','native_core_format').replace('check_number_format_integration','check_core_format_integration').replace('number-format','core-format').replace(oldmake,newmake).replace(parent['binary_sha256'],bundle['binary_sha256']).replace('11224','15408').replace('11264','16384').replace('bytes(40)','bytes(976)').replace('0x1619c0','0x162dc0')
 def emit(name,newname=None,edits=()):
  old=ROOT/'scripts'/name;text=transform(old.read_text())
  for a,b in edits:assert a in text,(name,a);text=text.replace(a,b)
  target=ROOT/'scripts'/(newname or name.replace('native_number_format','native_core_format').replace('number_format','core_format'));compile(text,str(target),'exec');target.write_text(text)
  (out/('parent-'+name)).write_bytes(old.read_bytes());(out/target.name).write_bytes(target.read_bytes());records.append(dict(parent=str(old),parent_sha256=sha(old),derived=str(target),derived_sha256=sha(target)))
 for kind in ['controller','rng','tasks','scheduler','heap','copy','free','release','acquire','allocator','initialize','heap_witness','lifecycle','readiness']:emit(f'check_biwn_native_number_format_bundle_{kind}.py')
 emit('check_biwn_native_number_format_loader_readiness.py')
 emit('check_biwn_native_number_format_disc_entry.py',edits=[('range(30000)','range(100000)'),('12288','24576'),('FB000','F8000')])
 emit('check_number_format_integration.py','check_core_format_integration.py')
 emit('build_biwn_native_number_format_disc.py',edits=[("(0x1b212,'biwn_native_format_number')]","(0x1b212,'biwn_native_format_number'),(0x1b29c,'biwn_native_format_core'),(0x1b45a,'biwn_native_format_variadic')]"),('12KB','24KB')])
 emit('check_biwn_number_format_helpers.py')
 emit('check_biwn_number_format_math_linked.py')
 emit('check_biwn_number_format_number_linked.py')
 # New full formatter gate, exact15408byte bundle; no rebuild/substituted calls.
 old=ROOT/'scripts/check_biwn_native_format_core.py';text=old.read_text().replace('BASE=0x160000;','BASE=0x15edc0;')
 start=text.index("  result=subprocess.run(['make'");end=text.index('  symbols=',start)
 text=text[:start]+"  bundle_path=ROOT/'verification/native-core-format-bundle-current.json';bundle=json.loads(bundle_path.read_text());binary=Path(bundle['binary']);elf=Path(bundle['ELF']);payload=binary.read_bytes();assert sha(binary)==bundle['binary_sha256'];prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-')\n  paths.append(bundle_path)\n"+text[end:]
 text=text.replace('verification/native-format-core-active.json','verification/native-core-format-core-active.json').replace('verification/native-format-core-current.json','verification/native-core-format-core-current.json').replace("ROOT/'verification/native-format-core'/","ROOT/'verification/native-core-format-core'/")
 target=ROOT/'scripts/check_biwn_core_format_core_linked.py';compile(text,str(target),'exec');target.write_text(text);(out/'parent-core-checker.py').write_bytes(old.read_bytes());(out/target.name).write_bytes(target.read_bytes());records.append(dict(parent=str(old),parent_sha256=sha(old),derived=str(target),derived_sha256=sha(target)))
 state=dict(status='full_formatter_expanded_layout_drivers_prepared',directory=str(out),bundle=str(bp),bundle_sha256=sha(bp),binary_sha256=bundle['binary_sha256'],binary_bytes=bundle['binary_bytes'],makefile=newmake,makefile_sha256=sha(newmake),drivers=records,same_reservation_and_heap=False,heap_start=bundle['heap_start'],reserved_bytes=bundle['reserved_bytes'],staging=bundle['staging'],staging_clear_bytes=bundle['staging_clear_bytes'],new_training=False,default_promoted=False,whole_game_complete=False)
 save(out/'preparation.json',state);save(ROOT/'verification/native-core-format-preparation-current.json',state);print(out)
if __name__=='__main__':main()
