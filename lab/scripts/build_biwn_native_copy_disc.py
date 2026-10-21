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
LOAD=0x4000;STAGING=0xfc000;RESIDENT=0x15edc0

def main():
 out=ROOT/'builds/BIWN-native-copy'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 state=dict(status='prepared',directory=str(out),pid=os.getpid(),whole_game_complete=False,physical_console_verified=False,original_disc_modified=False,build_kind='Original game image plus eight C RNG routines, C keypad, C controller, C task creation with stack entry, C scheduler selection with native dispatch/removal boundaries, two same-address trap entries, C allocator and compactor, both C copy calling conventions atE3E0/E3EE, three same-address source-assembled arithmetic helpers and the verified on-disc marker repair. Resident padded to6144bytes and heap reserve6144bytes to hold startup copy/cleanup work fixed relative to the previous prototype. Other original code/providers remain. RNG nonzero-divisor component scope; not whole-game or exception equivalence.')
 def checkpoint():save(out/'build.json',state);save(ROOT/'verification/native-copy-disc-build-active.json',state)
 checkpoint();print(out,flush=True)
 try:
  session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'nextstage-mapping.json').read_text());stage=(session/'nextstage-68000-candidate.bin').read_bytes();assert hashlib.sha256(stage).hexdigest()==STAGE_SHA
  original=ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi';assert sha(original)==IMAGE_SHA
  native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';build=out/'component';prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-')
  command=['make','-f','Makefile.copy-bundle','copy-bundle','BUILD='+str(build),'COMPONENT_BASE='+hex(RESIDENT)]
  p=subprocess.run(command,cwd=native,capture_output=True,text=True);(out/'component-build.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
  component=build/'native-copy-bundle.bin';payload=component.read_bytes();assert 0<len(payload)<=0x1800 and len(payload)%2==0
  previous=json.loads((ROOT/'verification/native-copy-bundle-rng-current.json').read_text())
  assert previous['status']=='terminal_native_rng_nonzero_divisor_components_pass' and previous['cpu_cases']==1682 and previous['trace_cases']==298 and not previous['limit'] and previous['phase']=='both','Full native RNG component review required before disc build'
  for path,digest in previous['source_sha256'].items():assert sha(path)==digest
  controller_path=ROOT/'verification/native-copy-bundle-controller-current.json';controller=json.loads(controller_path.read_text())
  assert controller['status']=='terminal_native_controller_CPU_RAM_and_ordered_MMIO_pass' and not controller['limit'] and controller['native_cases']==1216 and controller['trace_cases']==1024
  for path,digest in controller['source_sha256'].items():assert sha(path)==digest
  assert sha(component)==controller['compiled_binary_sha256']
  task_path=ROOT/'verification/native-copy-bundle-tasks-current.json';task=json.loads(task_path.read_text())
  assert task['source_accepted'] and task['native_cases']==1280 and task['trace_cases']==1280 and task['empty_pool_exception_cases']==128
  for path,digest in task['source_sha256'].items():assert sha(path)==digest
  assert sha(component)==task['compiled_binary_sha256'] and sha(native/'task-create-native.c')==task['candidate_sha256']
  scheduler_path=ROOT/'verification/native-copy-bundle-scheduler-current.json';scheduler=json.loads(scheduler_path.read_text())
  assert scheduler['source_accepted'] and scheduler['native_cases']==1664 and scheduler['trace_cases']==896 and not scheduler['limit']
  for path,digest in scheduler['source_sha256'].items():assert sha(path)==digest
  assert sha(component)==scheduler['compiled_binary_sha256'] and sha(native/'scheduler-native.c')==scheduler['candidate_sha256']
  heap_path=ROOT/'verification/native-copy-bundle-heap-current.json';heap_gate=json.loads(heap_path.read_text())
  assert heap_gate['source_accepted'] and heap_gate['native_cases']==3392 and heap_gate['trace_cases']==3392 and heap_gate['phase']=='both'
  for path,digest in heap_gate['source_sha256'].items():assert sha(path)==digest
  assert sha(component)==heap_gate['compiled_binary_sha256']
  assert heap_gate['symbols']['biwn_native_heap_start']==RESIDENT+6144
  copy_path=ROOT/'verification/native-copy-bundle-current.json';copy_gate=json.loads(copy_path.read_text())
  assert copy_gate['source_accepted'] and copy_gate['native_cases']==copy_gate['trace_cases']==3260 and copy_gate['raw_count_prefix_cases']==12
  for path,digest in copy_gate['source_sha256'].items():assert sha(path)==digest,path
  assert sha(component)==copy_gate['compiled_binary_sha256']
  witness_path=ROOT/'verification/native-copy-bundle-heap-blitter-witness-current.json';witness=json.loads(witness_path.read_text())
  assert witness['payload_bytes_checked']==232 and witness['profiles'][1]['compiled_copy_body_calls']==2 and witness['profiles'][1]['old_copy_body_steps']==0
  assert witness['component_proof_sha256']==sha(heap_path)
  scan_path=ROOT/'verification/native-word-scan-build-current.json';scan=json.loads(scan_path.read_text());scan_binary=Path(scan['binary']);assert sha(scan_binary)==scan['binary_sha256']
  assert scan_binary.read_bytes().hex()==scan['repaired_fragment'] and len(scan_binary.read_bytes())==18

  symbols={}
  for line in subprocess.check_output([prefix+'nm','--defined-only',str(build/'native-copy-bundle.elf')],text=True).splitlines():
   row=line.split()
   if len(row)==3:symbols[row[2]]=int(row[0],16)
  assert symbols['biwn_native_button_digit']==RESIDENT
  assert stage[STAGING-LOAD:STAGING-LOAD+0x2000]==bytes(0x2000)
  save(out/'symbols.json',symbols)
  assert sha(component)==previous['compiled_binary_sha256']
  linked_component=component;linked_payload=payload
  runtime=build/'runtime-original.bin';runtime_bytes=runtime.read_bytes()
  assert runtime_bytes==stage[0xe540-LOAD:0xe61c-LOAD] and sha(runtime)==previous['fixed_runtime_binary_sha256']
  assert len(payload)==previous['binary_bytes'] and len(payload)<=6144
  payload=payload+bytes(6144-len(payload))
  component=build/'native-copy-padded.bin';component.write_bytes(payload)
  reserve=(len(payload)+7)&~7;assert reserve==6144;heap=RESIDENT+reserve
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
  linker=out/'entry.ld';linker.write_text(f'ENTRY(biwn_native_stage_entry)\nSECTIONS {{ . = {hex(STAGING)}; .text : {{ *(.text*) }} /DISCARD/ : {{ *(.comment) *(.note*) *(.eh_frame*) }} }}\nASSERT(SIZEOF(.text) < 0x2000,"Staging exceeds declared temporary window")\n')
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
  patch(0xe540,stage[0xe540-LOAD:0xe61c-LOAD],runtime_bytes,'Three source-assembled arithmetic helpers at original fixed addresses; 220 bytes reproduce original exactly, no extra entry jump.')
  patch(0xe4c0,stage[0xe4c0-LOAD:0xe4c6-LOAD],b'\x4e\xf9'+symbols['biwn_native_controller_poll'].to_bytes(4,'big'),'Native controller body directly scans four MMIO rows and updates held/edge globals; wrapper preserves full original register and CCR contract.')
  patch(0x15200,stage[0x15200-LOAD:0x15200-LOAD+10],b'\x4e\xf9'+symbols['biwn_native_heap_compact'].to_bytes(4,'big')+b'\x4e\x71'*2,'Native target-compiled compactor; target-compiled copy entry calls emulated blitter. Whole prologue instructions replaced.')
  patch(0x152a2,stage[0x152a2-LOAD:0x152a2-LOAD+6],b'\x4e\xf9'+symbols['biwn_native_heap_allocate'].to_bytes(4,'big'),'Native target-compiled allocator, coupled to native compactor with full caller registers/CCR frame.')
  for address,key in [(0xe3e0,'biwn_native_copy_source_first'),(0xe3ee,'biwn_native_copy_destination_first')]:
   patch(address,stage[address-LOAD:address-LOAD+6],b'\x4e\xf9'+symbols[key].to_bytes(4,'big'),'Target-compiled copy calling convention, exact byte/blitter path and public stack save/restore contract; emulated hardware remains.')
  patch(0xde08,stage[0xde08-LOAD:0xde08-LOAD+6],b'\x4e\xf9'+symbols['biwn_native_scheduler_dispatch'].to_bytes(4,'big'),'Native outgoing-frame dispatch and model C selection with original USP/RTE boundary.')
  patch(0xdeb6,stage[0xdeb6-LOAD:0xdeb6-LOAD+6],b'\x4e\xf9'+symbols['biwn_native_scheduler_remove'].to_bytes(4,'big'),'Native task unlink/free and selection with original exception-frame discard, no dead-task save.')
  for address,filename in [(0xdf60,'scheduler-yield.bin'),(0xdf7a,'scheduler-remove.bin')]:
   rebuilt=(build/filename).read_bytes();assert rebuilt==stage[address-LOAD:address-LOAD+len(rebuilt)]
   patch(address,stage[address-LOAD:address-LOAD+len(rebuilt)],rebuilt,'Source-assembled byte-identical trap entry at original address to preserve saved return PC.')
  patch(0xde5c,stage[0xde5c-LOAD:0xde5c-LOAD+6],b'\x4e\xf9'+symbols['biwn_native_task_create'].to_bytes(4,'big'),'Target-compiled task creation, original full register/CCR contract and original DEB4 ILLEGAL path retained.')
  patch(0xdf6c,stage[0xdf6c-LOAD:0xdf6c-LOAD+8],b'\x4e\xf9'+symbols['biwn_native_task_create_stack'].to_bytes(4,'big')+b'\x4e\x71','Source assembly stack-argument entry, complete original eight-byte load pair replaced.')
  patch(0x1b0ee,bytes.fromhex(scan['original_fragment']),scan_binary.read_bytes(),'Previously verified exact source-assembled18byte two-byte-stride marker repair, delivered on disc before loading.')
  for address,name in [(0x1a6e0,'init'),(0x1a6f8,'current'),(0x1a77c,'indexed'),(0x1a7f4,'fill'),(0x1a87a,'select'),(0x1a8c6,'seed'),(0x1a8e2,'get'),(0x1a8f8,'set')]:
   patch(address,stage[address-LOAD:address-LOAD+6],b'\x4e\xf9'+symbols['biwn_native_rng_'+name].to_bytes(4,'big'),'Tail jump to complete newly compiled RNG routine/ABI frame. Nonzero game Q-divisors are the validated component scope.')
  for address,old in [(0x1521c,RESIDENT),(0x1526c,RESIDENT),(0x1557c,RESIDENT),(0x1558c,RESIDENT),(0x15592,RESIDENT),(0x15598,RESIDENT+4),(0x1559e,RESIDENT+8)]:
   patch(address,old.to_bytes(4,'big'),(old+reserve).to_bytes(4,'big'),'Raise explicit heap boundary/initial free-header pointers to reserve native component; retain eight-byte alignment.')
  (out/'mainstage-native-partial.bin').write_bytes(candidate);save(out/'stage-patches.json',dict(patches=patches,original_stage_sha256=STAGE_SHA,derived_stage_sha256=hashlib.sha256(candidate).hexdigest(),source_loader_buffer=[hex(LOAD),'0x100000'],reserved_native_region=[hex(RESIDENT),hex(heap)],heap_bytes_removed=reserve,read_only_staging_lifetime='Read/execute immediately at original mainstage entry before regular initialization; no assumption it remains unused later.'))
  offset=mapping['payload_raw_cdi_offset']
  with original.open('rb')as f:f.seek(offset);assert swap16(f.read(len(stage)))==stage
  disc=out/'BIWN-23-native-copy-experimental.cdi';shutil.copyfile(original,disc)
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
  sources=[Path(__file__),native/'Makefile',native/'Makefile.movable',native/'Makefile.math',native/'Makefile.bundle',native/'Makefile.optimized',native/'Makefile.native',native/'Makefile.controller-lean-bundle',native/'controller-bundle.ld',native/'controller-native.c',native/'controller-lean-shim.S',native/'Makefile.fast-rng',native/'fast-rng.ld',native/'rng-fast-math.S',native/'runtime-original.S',native/'runtime-original.ld',native/'rng-native.c',native/'rng-native.h',native/'rng-shims.S',native/'rng.ld',native/'math-results-optimized.c',native/'bundle.ld',native/'math-results.c',native/'math-shims.S',native/'startup-finalize.S',native/'button-digit-movable-shim.S',native.parent/'biwn_camera.c',native.parent/'biwn_signed_division.c',native.parent/'biwn_inventory_select.c',native.parent/'biwn_inventory_select.h',assembly,linker,task_path,scan_path,scan_binary,scheduler_path,heap_path,*[native/n for n in ["heap-allocate-native.c","heap-compact-native.c","heap-native.h","heap-shims.S","heap-bundle.ld","Makefile.copy-bundle","startup-finalize-heap.S"]],*[native/n for n in ["scheduler-native.c","scheduler-shims.S","scheduler-traps.S","scheduler-traps.ld","scheduler-bundle.ld","Makefile.scheduler-bundle"]],*[native/n for n in ["task-create-native.c","task-create-shim.S","task-bundle.ld","Makefile.task-create-bundle"]]]
  sources += [copy_path,witness_path]+[native/name for name in ['copy-native.c','copy-native.h','copy-shims.S','copy-bundle.ld','Makefile.copy-bundle','Makefile.copy','copy.ld']]
  state.update(status='terminal_partial_native_copy_disc_built_pending_execution',original_disc=str(original),original_disc_sha256=IMAGE_SHA,derived_disc=str(disc),derived_disc_sha256=sha(disc),derived_disc_bytes=disc.stat().st_size,changed_disc_bytes=differences,original_stage_sha256=STAGE_SHA,derived_stage=str(out/'mainstage-native-partial.bin'),derived_stage_sha256=sha(out/'mainstage-native-partial.bin'),component=str(component),component_sha256=sha(component),component_bytes=len(payload),linked_component=str(linked_component),linked_component_sha256=sha(linked_component),linked_component_bytes=len(linked_payload),padding_bytes=len(payload)-len(linked_payload),fixed_runtime_binary=str(runtime),fixed_runtime_binary_sha256=sha(runtime),fixed_runtime_bytes=220,public_runtime_entry_jump_overhead=0,resident_redirect_entries=18,native_rebuilt_entries=23,controller_component_proof=str(controller_path),controller_component_proof_sha256=sha(controller_path),controller_source_unchanged_from_model_edits=True,rng_rebuilt_entries=8,rng_component_proof=str(ROOT/'verification/native-copy-bundle-rng-current.json'),rng_component_proof_sha256=sha(ROOT/'verification/native-copy-bundle-rng-current.json'),symbols=symbols,staging_cleared_by_resident_finalizer=True,runtime_archive=str(ROOT/'tools/m68k-elf/m68000-soft/libgcc.a'),runtime_archive_sha256=sha(ROOT/'tools/m68k-elf/m68000-soft/libgcc.a'),native_entry_bytes=len(entry),staging_address=STAGING,resident_address=RESIDENT,heap_start=heap,heap_bytes_reserved=reserve,patch_manifest=str(out/'stage-patches.json'),patch_manifest_sha256=sha(out/'stage-patches.json'),source_sha256={str(p):sha(p)for p in sources},build_command=command,game_byte_repairs_beyond_native_layout=18,marker_repair_actual_changed_bytes=14,task_component_proof=str(task_path),task_component_proof_sha256=sha(task_path),marker_component_proof=str(scan_path),marker_component_proof_sha256=sha(scan_path),scheduler_component_proof=str(scheduler_path),scheduler_component_proof_sha256=sha(scheduler_path),scheduler_rebuilt_entry_contracts=4,source_assembled_trap_bytes=14,heap_component_proof=str(heap_path),heap_component_proof_sha256=sha(heap_path),heap_rebuilt_entry_contracts=2,staging_bytes_cleared=8192,staging_end=STAGING+8192,copy_component_proof=str(copy_path),copy_component_proof_sha256=sha(copy_path),copy_payload_witness_proof=str(witness_path),copy_rebuilt_entry_contracts=2,copy_dependency="Both public copy entries redirect to targetC; emulatedCPU/blitter and other original engine code remain",bootable_image_verified=False)
  checkpoint();save(ROOT/'verification/native-copy-disc-build-current.json',state);print(json.dumps({k:state[k]for k in ['status','derived_disc','changed_disc_bytes','component_bytes','heap_bytes_reserved']}),flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));checkpoint();raise
if __name__=='__main__':main()
