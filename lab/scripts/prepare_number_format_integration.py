"""Derive fresh exact-layout gates; keep every parent test assertion/matrix."""
import json
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def main():
 bp=ROOT/'verification/native-number-format-bundle-current.json';bundle=json.loads(bp.read_text())
 pp=Path(bundle['parent_bundle_proof']);parent=json.loads(pp.read_text());assert bundle['binary_bytes']==11224
 out=ROOT/'verification/native-number-format-preparation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);records=[]
 oldmake=str(Path(parent['directory'])/'Makefile');newmake=str(Path(bundle['directory'])/'Makefile')
 def transform(text):
  return text.replace('native-unsigned-format','native-number-format').replace('native_unsigned_format','native_number_format').replace('check_unsigned_format_integration','check_number_format_integration').replace('unsigned-format','number-format').replace(oldmake,newmake).replace(parent['binary_sha256'],bundle['binary_sha256']).replace('8956','11224').replace('9216','11264').replace('bytes(260)','bytes(40)').replace('0x1611c0','0x1619c0')
 def emit(name,newname=None,edits=()):
  old=ROOT/'scripts'/name;text=transform(old.read_text())
  for a,b in edits:assert a in text,(name,a);text=text.replace(a,b)
  target=ROOT/'scripts'/(newname or name.replace('native_unsigned_format','native_number_format').replace('unsigned_format','number_format'));compile(text,str(target),'exec');target.write_text(text)
  (out/('parent-'+name)).write_bytes(old.read_bytes());(out/target.name).write_bytes(target.read_bytes());records.append(dict(parent=str(old),parent_sha256=sha(old),derived=str(target),derived_sha256=sha(target)))
 for kind in ['controller','rng','tasks','scheduler','heap','copy','free','release','acquire','allocator','initialize','heap_witness','lifecycle','readiness']:emit(f'check_biwn_native_unsigned_format_bundle_{kind}.py')
 emit('check_biwn_native_unsigned_format_loader_readiness.py')
 emit('check_biwn_native_unsigned_format_disc_entry.py')
 emit('check_unsigned_format_integration.py','check_number_format_integration.py')
 emit('build_biwn_native_unsigned_format_disc.py',edits=[("(0xe67c,'biwn_native_unsigned_remainder')]","(0xe67c,'biwn_native_unsigned_remainder'),(0x1b212,'biwn_native_format_number')]")])
 emit('check_biwn_unsigned_format_helpers.py')
 emit('check_biwn_unsigned_format_callers.py',edits=[
  ('0xe67c:12}','0xe67c:12,0x1b212:56}'),
  ('pc==0xe67c)&&!active','pc==0xe67c||pc==0x1b212)&&!active'),
  ('(0xe67c,6),','(0xe67c,6),(0x1b212,6),'),
  ('(0xe67c,0xe68c)]','(0xe67c,0xe68c),(0x1b212,0x1b29c)]'),
  ("(0xe67c,'biwn_native_unsigned_remainder')]","(0xe67c,'biwn_native_unsigned_remainder'),(0x1b212,'biwn_native_format_number')]"),
  ('Nested original E61C inside E67C is observed only at the outer helper boundary; direct math matrices separately compare both entry contracts.','Nested original math inside number and E61C inside E67C are observed only at their outer helper boundary; direct number/math matrices separately compare each entry contract.')])
 # Linked math uses the whole installed payload because number text follows it.
 emit('check_biwn_native_unsigned_division_linked.py','check_biwn_number_format_math_linked.py',[
  ("verification/native-unsigned-bundle-current.json","verification/native-number-format-bundle-current.json"),
  ("BASE=_bundle['symbols']['biwn_native_unsigned_divide']","BASE=_bundle['base']"),
  ("offset=bundle['symbols']['biwn_native_unsigned_divide']-bundle['base'];payload=full[offset:];assert len(payload)==474","payload=full;assert len(payload)==11224"),
  ('native-unsigned-division','native-number-format-math')])
 # Number gate: same fixtures and comparisons, no rebuild and no substitutions.
 old=ROOT/'scripts/check_biwn_native_format_number.py';text=old.read_text();text=text.replace('BASE=0x160000;','BASE=0x15edc0;')
 start=text.index("  result=subprocess.run(['make'");end=text.index("  symbols=",start)
 text=text[:start]+"  bundle_path=ROOT/'verification/native-number-format-bundle-current.json';bundle=json.loads(bundle_path.read_text());binary=Path(bundle['binary']);elf=Path(bundle['ELF']);payload=binary.read_bytes();assert sha(binary)==bundle['binary_sha256'];prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-')\n  paths.append(bundle_path)\n"+text[end:]
 text=text.replace('verification/native-format-number-active.json','verification/native-number-format-number-active.json').replace('verification/native-format-number-current.json','verification/native-number-format-number-current.json').replace("ROOT/'verification/native-format-number'/","ROOT/'verification/native-number-format-number'/")
 target=ROOT/'scripts/check_biwn_number_format_number_linked.py';compile(text,str(target),'exec');target.write_text(text);(out/'parent-number-checker.py').write_bytes(old.read_bytes());(out/target.name).write_bytes(target.read_bytes());records.append(dict(parent=str(old),parent_sha256=sha(old),derived=str(target),derived_sha256=sha(target)))
 state=dict(status='number_install_component_and_formatter_drivers_prepared',directory=str(out),bundle=str(bp),bundle_sha256=sha(bp),binary_sha256=bundle['binary_sha256'],binary_bytes=bundle['binary_bytes'],makefile=newmake,makefile_sha256=sha(newmake),drivers=records,same_reservation_and_heap=False,heap_start=bundle['heap_start'],reserved_bytes=bundle['reserved_bytes'],new_training=False,default_promoted=False,whole_game_complete=False)
 save(out/'preparation.json',state);save(ROOT/'verification/native-number-format-preparation-current.json',state);print(out)
if __name__=='__main__':main()
