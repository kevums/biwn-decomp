"""Link the explicit repaired loader with prior native components; no acceptance."""
from pathlib import Path
from datetime import datetime,timezone
import json,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def main():
 nd=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';out=ROOT/'verification/native-load-scan-bundle-preflight'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);build=out/'build';command=['make','-f','Makefile.load-scan-bundle','load-scan-bundle','BUILD='+str(build)];p=subprocess.run(command,cwd=nd,capture_output=True,text=True);(out/'make.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 binary=build/'native-load-scan-bundle.bin';prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');symbols={}
 for line in subprocess.check_output([prefix+'nm','--defined-only',str(build/'native-load-scan-bundle.elf')],text=True).splitlines():
  t=line.split()
  if len(t)==3:symbols[t[2]]=int(t[0],16)
 (out/'disassembly.txt').write_text(subprocess.check_output([prefix+'objdump','-dr',str(build/'native-load-scan-bundle.elf')],text=True));assert 0<len(binary.read_bytes())<=7680 and symbols['biwn_native_button_digit']==0x15edc0 and symbols['biwn_native_heap_start']==0x160bc0
 state=dict(status='linked_repaired_loader_bundle_pending_exact_binary_gates',directory=str(out),command=command,binary=str(binary),binary_sha256=sha(binary),binary_bytes=binary.stat().st_size,resident_base=0x15edc0,reserved_bytes=7680,padding_bytes=7680-binary.stat().st_size,heap_start=0x160bc0,symbols=symbols,source_sha256={str(p):sha(p)for pattern in ['Makefile*','*.c','*.h','*.S','*.ld']for p in nd.glob(pattern)},source_accepted=False,new_disc_built=False,whole_game_complete=False,new_training=False)
 save(out/'protocol.json',state);save(ROOT/'verification/native-load-scan-bundle-preflight-current.json',state)
 padded=out/'native-load-scan-padded-fixture.bin';padded.write_bytes(binary.read_bytes()+bytes(state['padding_bytes']))
 names={0x15200:('biwn_native_heap_compact',10),0x152a2:('biwn_native_heap_allocate',6),0xe3e0:('biwn_native_copy_source_first',6),0xe3ee:('biwn_native_copy_destination_first',6),0xde08:('biwn_native_scheduler_dispatch',6),0xdeb6:('biwn_native_scheduler_remove',6)}
 patches=out/'linked-fixture-patches.json';save(patches,dict(patches=[dict(address=hex(a),replacement=(b'\x4e\xf9'+symbols[k].to_bytes(4,'big')+b'\x4e\x71'*((n-6)//2)).hex())for a,(k,n)in names.items()]))
 save(ROOT/'verification/native-load-scan-bundle-linked-fixture-current.json',dict(status='linked_fixture_only_no_disc',resident_address=state['resident_base'],heap_start=state['heap_start'],component_bytes=state['reserved_bytes'],component=str(padded),component_sha256=sha(padded),patch_manifest=str(patches),patch_manifest_sha256=sha(patches),symbols=symbols,new_disc_built=False))
 print(state['status'],state['binary_bytes'],'/',state['reserved_bytes'],state['binary_sha256'],flush=True)
if __name__=='__main__':main()
