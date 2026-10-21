"""Rebind worked O2 validators to the exact Os compact bundle and owner ranges."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def main():
 pp=ROOT/'verification/native-acquire-compact-preflight-current.json';b=json.loads(pp.read_text());assert sha(b['binary'])==b['binary_sha256'];oldsha='0c5d35966cb6ae0d92d650f0f684528cd3bab1c2c80f4047cbf14d82e239cbb0';rows=[]
 for kind in ['controller','rng','tasks','scheduler','heap','copy','free','initialize','acquire','allocator','release','lifecycle','heap_witness','readiness']:
  old=ROOT/'scripts'/('check_biwn_native_acquire_bundle_'+kind+'.py');new=ROOT/'scripts'/('check_biwn_native_acquire_compact_bundle_'+kind+'.py')
  s=old.read_text().replace('acquire-bundle','acquire-compact-bundle').replace('check_biwn_native_acquire_bundle','check_biwn_native_acquire_compact_bundle').replace(oldsha,b['binary_sha256'])
  if kind=='readiness':
   s=s.replace('0x160dc0','0x1605c0').replace("bundle['component_bytes']==8192","bundle['component_bytes']==6144").replace('reserves8192bytes','reserves6144bytes')
   oldline="        rt.acquire_private_ranges=[(symbols['biwn_native_resource_acquire'],symbols['biwn_native_resource_acquire']+int(asmrow[2],16)),(int(bodyrow[0],16),int(bodyrow[0],16)+int(bodyrow[1],16))]"
   assert s.count(oldline)==1
   s=s.replace(oldline,"""        owned={}
        for line in subprocess.check_output([prefix+'nm','-S','--defined-only',str(build/'resource-acquire-native.o')],text=True).splitlines():
            fields=line.split()
            if len(fields)==4 and fields[2].lower()=='t':owned[fields[3]]=int(fields[1],16)
        rt.acquire_private_ranges=[(symbols['biwn_native_resource_acquire'],symbols['biwn_native_resource_acquire']+int(asmrow[2],16))]
        found=[]
        for line in subprocess.check_output([prefix+'nm','-S','--defined-only',str(build/'native-acquire-compact-bundle.elf')],text=True).splitlines():
            fields=line.split()
            if len(fields)==4 and fields[3]in owned:
                assert int(fields[1],16)==owned[fields[3]]
                found.append(fields[3]);rt.acquire_private_ranges.append((int(fields[0],16),int(fields[0],16)+int(fields[1],16)))
        assert sorted(found)==sorted(owned),found
""".rstrip())
  compile(s,str(new),'exec');new.write_text(s);rows.append(dict(kind=kind,original=str(old),original_sha256=sha(old),adapted=str(new),adapted_sha256=sha(new),changes='Build target/namespace/exactbinarySHA; readiness uses6144reservation and exact compiler-owned function ranges derived from object+ELF. Fixtures, memory exclusions and comparison assertions unchanged.'))
 # Fixture reservation at6144 in both lanes; this is not an on-disc installation.
 d=Path(b['directory']);padded=d/'native-acquire-compact-padded-fixture.bin';padded.write_bytes(Path(b['binary']).read_bytes()+bytes(b['padding_bytes']))
 names={0x15200:('biwn_native_heap_compact',10),0x152a2:('biwn_native_heap_allocate',6),0xe3e0:('biwn_native_copy_source_first',6),0xe3ee:('biwn_native_copy_destination_first',6),0xde08:('biwn_native_scheduler_dispatch',6),0xdeb6:('biwn_native_scheduler_remove',6)}
 patches=d/'linked-fixture-patches.json';save(patches,dict(patches=[dict(address=hex(a),replacement=(b'\x4e\xf9'+b['symbols'][key].to_bytes(4,'big')+b'\x4e\x71'*((size-6)//2)).hex())for a,(key,size)in names.items()]))
 save(ROOT/'verification/native-acquire-compact-bundle-linked-fixture-current.json',dict(status='compact_linked_fixture_only_no_disc',resident_address=b['resident_base'],heap_start=b['heap_start'],component_bytes=b['reserved_bytes'],component=str(padded),component_sha256=sha(padded),patch_manifest=str(patches),patch_manifest_sha256=sha(patches),symbols=b['symbols'],new_disc_built=False))
 prep=dict(status='prepared_pinned_compact_checks',recorded_at=datetime.now(timezone.utc).isoformat(),bundle_proof=str(pp),bundle_proof_sha256=sha(pp),target_binary_sha256=b['binary_sha256'],gates=rows[:8],extra_checks=rows[8:],new_game_image=False)
 save(ROOT/'verification/native-acquire-compact-gates-preparation-current.json',prep)
 old=ROOT/'scripts/run_biwn_acquire_bundle_gates.py';new=ROOT/'scripts/run_biwn_acquire_compact_bundle_gates.py';s=old.read_text().replace('native-acquire-gates-preparation','native-acquire-compact-gates-preparation').replace('native-acquire-bundle','native-acquire-compact-bundle');compile(s,str(new),'exec');new.write_text(s)
 print('Prepared compact gates and6144fixture',b['binary_sha256'])
if __name__=='__main__':main()
