"""Build an explicit partial native BIWN CDI derivative; preserve original.
The mainstage entry loader copies freshly compiled C into a reserved region
below a deliberately raised heap base. No unproven forever-free BSS cave.
The CD staging region is used immediately before original entry setup; it
has no lifetime requirement after copying. Mixed original/native build.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,subprocess,shutil,hashlib,os
from check_biwn_native_button_digit import ROOT,save,sha
from extract_biwn_stage import swap16,STAGE_SHA,IMAGE_SHA
LOAD=0x4000;STAGING=0xff000;RESIDENT=0x15edc0

def main():
 out=ROOT/'builds/BIWN-native-bundle'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 state=dict(status='prepared',directory=str(out),pid=os.getpid(),whole_game_complete=False,physical_console_verified=False,original_disc_modified=False,build_kind='Original game image plus four compiled/native entry contracts, staging cleanup and coordinator startup/heap layout changes.')
 def checkpoint():save(out/'build.json',state);save(ROOT/'verification/native-bundle-disc-build-active.json',state)
 checkpoint();print(out,flush=True)
 try:
  session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'nextstage-mapping.json').read_text());stage=(session/'nextstage-68000-candidate.bin').read_bytes();assert hashlib.sha256(stage).hexdigest()==STAGE_SHA
  original=ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi';assert sha(original)==IMAGE_SHA
  native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';build=out/'component';prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-')
  command=['make','-f','Makefile.bundle','bundle','BUILD='+str(build),'COMPONENT_BASE='+hex(RESIDENT)]
  p=subprocess.run(command,cwd=native,capture_output=True,text=True);(out/'component-build.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
  component=build/'native-bundle.bin';payload=component.read_bytes();assert 0<len(payload)<0xe00 and len(payload)%2==0
  previous=json.loads((ROOT/'verification/native-math-current.json').read_text())
  for path,digest in previous['source_sha256'].items():assert sha(path)==digest
  symbols={}
  for line in subprocess.check_output([prefix+'nm','--defined-only',str(build/'native-bundle.elf')],text=True).splitlines():
   row=line.split()
   if len(row)==3:symbols[row[2]]=int(row[0],16)
  assert symbols['biwn_native_button_digit']==RESIDENT
  assert stage[STAGING-LOAD:0x100000-LOAD]==bytes(0x1000)
  save(out/'symbols.json',symbols)
  reserve=(len(payload)+7)&~7;heap=RESIDENT+reserve
  assembly=out/'native-stage-entry.S';assembly.write_text(f'''.text
.globl biwn_native_stage_entry
biwn_native_stage_entry:
move.w #0x2700,%sr
movea.l #0x200000,%sp
movem.l %d0-%d7/%a0-%a6,-(%sp)
lea biwn_resident_payload(%pc),%a0
lea {hex(RESIDENT)},%a1
move.w #{len(payload)//2-1},%d0
1: move.w (%a0)+,(%a1)+
dbra %d0,1b
jmp {hex(symbols['biwn_native_startup_finalize'])}
.balign 2
biwn_resident_payload:
.incbin "{component}"
''')
  subprocess.run([prefix+'as','-m68000','-o',str(out/'entry.o'),str(assembly)],check=True)
  linker=out/'entry.ld';linker.write_text(f'ENTRY(biwn_native_stage_entry)\nSECTIONS {{ . = {hex(STAGING)}; .text : {{ *(.text*) }} /DISCARD/ : {{ *(.comment) *(.note*) *(.eh_frame*) }} }}\nASSERT(SIZEOF(.text) < 0x1000,"Staging exceeds declared temporary window")\n')
  subprocess.run([prefix+'ld','-T',str(linker),'-o',str(out/'native-entry.elf'),str(out/'entry.o')],check=True)
  subprocess.run([prefix+'objcopy','-O','binary',str(out/'native-entry.elf'),str(out/'native-entry.bin')],check=True)
  entry=(out/'native-entry.bin').read_bytes();(out/'entry-disassembly.txt').write_text(subprocess.check_output([prefix+'objdump','-d',str(out/'native-entry.elf')],text=True))
  candidate=bytearray(stage);patches=[]
  def patch(address,expected,replacement,reason):
   off=address-LOAD;assert candidate[off:off+len(expected)]==expected,(hex(address),candidate[off:off+len(expected)].hex(),expected.hex());assert len(expected)==len(replacement)
   candidate[off:off+len(expected)]=replacement;patches.append(dict(address=hex(address),original=expected.hex(),replacement=replacement.hex(),reason=reason))
  patch(LOAD,bytes.fromhex('46fc27002e7c00200000'),b'\x4e\xf9'+STAGING.to_bytes(4,'big')+b'\x4e\x71'*2,'Native entry executes original SR/SP setup, preserves registers, copies compiled payload and continues400A.')
  patch(STAGING,bytes(len(entry)),entry,'Temporary stage-delivered loader/data; consumed before original startup and then disposable.')
  patch(0x1b718,stage[0x1b718-LOAD:0x1b71e-LOAD],b'\x4e\xf9'+RESIDENT.to_bytes(4,'big'),'Tail jump into freshly compiled resident component with original caller stack unchanged.')
  for address,name in [(0xe540,'biwn_native_multiply'),(0xe588,'biwn_native_division'),(0xe60a,'biwn_native_remainder')]:
   patch(address,stage[address-LOAD:address-LOAD+6],b'\x4e\xf9'+symbols[name].to_bytes(4,'big'),'Tail jump to newly compiled arithmetic/ABI routine, including new native DIVU zero-exception handling.')
  for address,old in [(0x1521c,RESIDENT),(0x1526c,RESIDENT),(0x1557c,RESIDENT),(0x1558c,RESIDENT),(0x15592,RESIDENT),(0x15598,RESIDENT+4),(0x1559e,RESIDENT+8)]:
   patch(address,old.to_bytes(4,'big'),(old+reserve).to_bytes(4,'big'),'Raise explicit heap boundary/initial free-header pointers to reserve native component; retain eight-byte alignment.')
  (out/'mainstage-native-partial.bin').write_bytes(candidate);save(out/'stage-patches.json',dict(patches=patches,original_stage_sha256=STAGE_SHA,derived_stage_sha256=hashlib.sha256(candidate).hexdigest(),source_loader_buffer=[hex(LOAD),'0x100000'],reserved_native_region=[hex(RESIDENT),hex(heap)],heap_bytes_removed=reserve,read_only_staging_lifetime='Read/execute immediately at original mainstage entry before regular initialization; no assumption it remains unused later.'))
  offset=mapping['payload_raw_cdi_offset']
  with original.open('rb')as f:f.seek(offset);assert swap16(f.read(len(stage)))==stage
  disc=out/'BIWN-23-native-math-bundle-experimental.cdi';shutil.copyfile(original,disc)
  with disc.open('r+b')as f:
   for patchrow in patches:
    off=int(patchrow['address'],16)-LOAD;old=bytes.fromhex(patchrow['original']);new=bytes.fromhex(patchrow['replacement']);assert off%2==len(old)%2==0
    f.seek(offset+off);assert f.read(len(old))==swap16(old);f.seek(offset+off);f.write(swap16(new))
   f.flush();os.fsync(f.fileno())
  with disc.open('rb')as f:f.seek(offset);assert swap16(f.read(len(stage)))==candidate
  # Independently prove every other CDI byte and all track metadata unchanged.
  intervals=sorted((offset+int(p['address'],16)-LOAD,offset+int(p['address'],16)-LOAD+len(bytes.fromhex(p['original'])))for p in patches)
  differences=0;position=0
  with original.open('rb')as a,disc.open('rb')as b:
   while True:
    left=a.read(1048576);right=b.read(1048576);assert len(left)==len(right)
    if not left:break
    if left!=right:
     for i,(x,y)in enumerate(zip(left,right)):
      if x!=y:assert any(lo<=position+i<hi for lo,hi in intervals),('undeclared CDI change',position+i);differences+=1
    position+=len(left)
  assert position==original.stat().st_size and sha(original)==IMAGE_SHA
  sources=[Path(__file__),native/'Makefile',native/'Makefile.movable',native/'Makefile.math',native/'Makefile.bundle',native/'bundle.ld',native/'math-results.c',native/'math-shims.S',native/'startup-finalize.S',native/'button-digit-movable-shim.S',native.parent/'biwn_camera.c',native.parent/'biwn_signed_division.c',native.parent/'biwn_inventory_select.c',native.parent/'biwn_inventory_select.h',assembly,linker]
  state.update(status='terminal_partial_native_bundle_disc_built_pending_execution',original_disc=str(original),original_disc_sha256=IMAGE_SHA,derived_disc=str(disc),derived_disc_sha256=sha(disc),derived_disc_bytes=disc.stat().st_size,changed_disc_bytes=differences,original_stage_sha256=STAGE_SHA,derived_stage=str(out/'mainstage-native-partial.bin'),derived_stage_sha256=sha(out/'mainstage-native-partial.bin'),component=str(component),component_sha256=sha(component),component_bytes=len(payload),native_rebuilt_entries=4,math_proof=str(ROOT/'verification/native-math-current.json'),math_proof_sha256=sha(ROOT/'verification/native-math-current.json'),symbols=symbols,staging_cleared_by_resident_finalizer=True,runtime_archive=str(ROOT/'tools/m68k-elf/m68000-soft/libgcc.a'),runtime_archive_sha256=sha(ROOT/'tools/m68k-elf/m68000-soft/libgcc.a'),native_entry_bytes=len(entry),staging_address=STAGING,resident_address=RESIDENT,heap_start=heap,heap_bytes_reserved=reserve,patch_manifest=str(out/'stage-patches.json'),patch_manifest_sha256=sha(out/'stage-patches.json'),source_sha256={str(p):sha(p)for p in sources},build_command=command,game_byte_repairs_beyond_native_layout=0,bootable_image_verified=False)
  checkpoint();save(ROOT/'verification/native-bundle-disc-build-current.json',state);print(json.dumps({k:state[k]for k in ['status','derived_disc','changed_disc_bytes','component_bytes','heap_bytes_reserved']}),flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));checkpoint();raise
if __name__=='__main__':main()
