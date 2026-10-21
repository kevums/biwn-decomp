"""Bind acquire/readiness/lifecycle checks to the pinned relocated bundle."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def pin(s):
 matches=list(re.finditer(r'(?m)^( +)[^\n]*payload\s*=\s*binary\.read_bytes\(\)[^\n]*$',s));assert len(matches)==1
 m=matches[0];return s[:m.end()]+'\n'+m.group(1)+'assert sha(binary)=='+repr(TARGET)+', "Wrong linked bundle"'+s[m.end():]
def main():
 global TARGET
 bp=ROOT/'verification/native-acquire-bundle-preflight-current.json';b=json.loads(bp.read_text());TARGET=b['binary_sha256'];assert sha(b['binary'])==TARGET;rows=[]
 def write(old,new,s):
  compile(s,str(new),'exec');new.write_text(s);rows.append(dict(original=str(old),original_sha256=sha(old),adapted=str(new),adapted_sha256=sha(new)))
 old=ROOT/'scripts/check_biwn_native_resource_acquire.py';new=ROOT/'scripts/check_biwn_native_acquire_bundle_acquire.py';s=old.read_text().replace('= 0x140000, 0x144000', '= 0x15edc0, 0x144000').replace("'Makefile.resource-acquire','resource-acquire'","'Makefile.acquire-bundle','acquire-bundle'").replace('native-resource-acquire','native-acquire-bundle-acquire')
 # Restore only the linked ELF/bin stems; source/header names are unchanged.
 s=s.replace("'native-acquire-bundle-acquire'","'native-acquire-bundle'").replace('native-acquire-bundle-acquire.bin','native-acquire-bundle.bin').replace('native-acquire-bundle-acquire.elf','native-acquire-bundle.elf')
 needle="        (out/'make.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr"
 assert s.count(needle)==1
 s=s.replace(needle,needle+"\n        rp=subprocess.run(['make','-f','Makefile.resource-acquire','BUILD='+str(build),str(build/'acquire-providers.bin')],cwd=nd,capture_output=True,text=True)\n        (out/'providers-make.log').write_text(rp.stdout+rp.stderr);assert rp.returncode==0,rp.stderr")
 write(old,new,pin(s))
 old=ROOT/'scripts/check_biwn_native_acquire_allocator.py';new=ROOT/'scripts/check_biwn_native_acquire_bundle_allocator.py';s=old.read_text().replace('import check_biwn_native_resource_acquire as a','import check_biwn_native_acquire_bundle_acquire as a').replace('native-heap-bundle-current.json','native-acquire-bundle-heap-current.json').replace('native-acquire-allocator','native-acquire-bundle-allocator').replace("'Makefile.resource-acquire','resource-acquire'","'Makefile.acquire-bundle','acquire-bundle'").replace("'native-resource-acquire'","'native-acquire-bundle'").replace('native-resource-acquire.bin','native-acquire-bundle.bin')
 s=s.replace(needle,needle+"\n        rp=subprocess.run(['make','-f','Makefile.resource-acquire','BUILD='+str(build),str(build/'acquire-providers.bin')],cwd=nd,capture_output=True,text=True)\n        (out/'providers-make.log').write_text(rp.stdout+rp.stderr);assert rp.returncode==0,rp.stderr")if needle in s else s
 # This checker logs make on its subprocess line, so insert the provider build after that exact line.
 if "providers-make.log"not in s:
  target=next(l for l in s.splitlines()if "(out/'make.log').write_text"in l)
  s=s.replace(target,target+"\n        rp=subprocess.run(['make','-f','Makefile.resource-acquire','BUILD='+str(build),str(build/'acquire-providers.bin')],cwd=nd,capture_output=True,text=True)\n        (out/'providers-make.log').write_text(rp.stdout+rp.stderr);assert rp.returncode==0,rp.stderr")
 write(old,new,pin(s))
 old=ROOT/'scripts/check_biwn_native_resource_release.py';new=ROOT/'scripts/check_biwn_native_acquire_bundle_release.py';s=old.read_text().replace('resource-bundle','acquire-bundle').replace('native-resource-release-bundle','native-acquire-bundle-release');write(old,new,pin(s))
 old=ROOT/'scripts/check_biwn_native_resource_lifecycle.py';new=ROOT/'scripts/check_biwn_native_acquire_bundle_lifecycle.py';s=old.read_text().replace('native-resource-bundle','native-acquire-bundle').replace('native-resource-lifecycle','native-acquire-bundle-lifecycle');write(old,new,s)
 # Checked fixture metadata: identical proposed bytes, not an installed disc.
 d=Path(b['directory']);padded=d/'native-acquire-padded-fixture.bin';padded.write_bytes(Path(b['binary']).read_bytes()+bytes(b['padding_bytes']))
 sizes={0x15200:10,0x152a2:6,0xe3e0:6,0xe3ee:6,0xde08:6,0xdeb6:6};names={0x15200:'biwn_native_heap_compact',0x152a2:'biwn_native_heap_allocate',0xe3e0:'biwn_native_copy_source_first',0xe3ee:'biwn_native_copy_destination_first',0xde08:'biwn_native_scheduler_dispatch',0xdeb6:'biwn_native_scheduler_remove'}
 patches=d/'linked-fixture-patches.json';save(patches,dict(patches=[dict(address=hex(a),replacement=(b'\x4e\xf9'+b['symbols'][names[a]].to_bytes(4,'big')+b'\x4e\x71'*((sizes[a]-6)//2)).hex())for a in names]))
 meta=dict(status='linked_fixture_only_no_disc',resident_address=b['resident_base'],heap_start=b['heap_start'],component_bytes=b['reserved_bytes'],component=str(padded),component_sha256=sha(padded),patch_manifest=str(patches),patch_manifest_sha256=sha(patches),symbols=b['symbols'],new_disc_built=False)
 save(ROOT/'verification/native-acquire-bundle-linked-fixture-current.json',meta)
 old=ROOT/'scripts/check_biwn_native_acquire_readiness.py';new=ROOT/'scripts/check_biwn_native_acquire_bundle_readiness.py';s=old.read_text().replace('BASE=0x140000','BASE=0x15edc0').replace("'Makefile.resource-acquire','resource-acquire'","'Makefile.acquire-bundle','acquire-bundle'").replace('native-resource-acquire','native-acquire-bundle').replace('native26','relocated').replace('Native26','Relocated').replace('native-resource-disc-build-current.json','native-acquire-bundle-linked-fixture-current.json').replace('0x1605c0','0x160dc0').replace("bundle['component_bytes']==6144","bundle['component_bytes']==8192").replace('reserves6144bytes','reserves8192bytes').replace('native-acquire-readiness','native-acquire-bundle-readiness')
 s=s.replace('not(BASE<=pc<BASE+len(payload))','not any(x<=pc<y for x,y in self.acquire_private_ranges)')
 needle="cases=[x['case']for x in json.loads((od/'fixtures.json').read_text())]"
 assert needle in s
 line=next(l for l in s.splitlines()if needle in l)
 suffix="""
        asmrow=next(l.split()for l in subprocess.check_output([prefix+'objdump','-h',str(build/'resource-acquire-shim.o')],text=True).splitlines()if '.text.biwn_native_resource_acquire 'in l)
        bodyrow=next(l.split()for l in subprocess.check_output([prefix+'nm','-S','--defined-only',str(build/'native-acquire-bundle.elf')],text=True).splitlines()if l.split()[-1]=='biwn_native_resource_acquire_body')
        rt.acquire_private_ranges=[(symbols['biwn_native_resource_acquire'],symbols['biwn_native_resource_acquire']+int(asmrow[2],16)),(int(bodyrow[0],16),int(bodyrow[0],16)+int(bodyrow[1],16))]
        state['acquire_compiler_private_PC_ranges']=rt.acquire_private_ranges
"""
 s=s.replace(line,line+suffix.rstrip());write(old,new,pin(s))
 save(ROOT/'verification/native-acquire-linked-checks-preparation-current.json',dict(status='prepared_pinned_linked_acquire_readiness_release_lifecycle_checks',bundle_proof=str(bp),bundle_proof_sha256=sha(bp),target_binary_sha256=TARGET,adaptations=rows,fixture_metadata=str(ROOT/'verification/native-acquire-bundle-linked-fixture-current.json')))
 print('Prepared acquire,allocator,readiness,release,lifecycle; fixture bytes match',TARGET)
if __name__=='__main__':main()
