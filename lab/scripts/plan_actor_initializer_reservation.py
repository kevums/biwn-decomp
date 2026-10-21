"""Read-only relocation/capacity plan; never changes heap, loader or a disc."""
import json,subprocess
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
 v=ROOT/'verification';bp=v/'native-actor-dispatch-gap320-disc-build-current.json';build=json.loads(bp.read_text());ip=v/'native-actor-initialize-current.json';init=json.loads(ip.read_text());raw=Path(build['linked_component']).read_bytes();floor=build['heap_start'];resident=build['resident_address'];assert len(raw)==19460 and floor==0x163dc0 and build['component_bytes']==20480
 out=v/'actor-initializer-layout-plan'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 command=[str(ROOT/'tools/m68k-elf/bin/m68k-elf-objdump'),'-D','-b','binary','-m','m68k:68000','--adjust-vma='+hex(resident),build['linked_component']]
 assembly=subprocess.check_output(command,text=True);asm=out/'current-resident.asm';asm.write_text(assembly);lines={int(p,16):line.strip()for line in assembly.splitlines()if ':'in line and (p:=line.split(':',1)[0].strip())and all(x in'0123456789abcdef'for x in p)}
 refs=[]
 for delta in [0,4,8]:
  value=floor+delta
  for i in range(len(raw)-3):
   if raw[i:i+4]!=value.to_bytes(4,'big'):continue
   pc=resident+i-2;line=lines[pc];assert f'{value:x}'in line and any(x in line for x in ['move','sub','clr','cmp']),line
   refs.append(dict(operand_address=hex(resident+i),instruction_address=hex(pc),old_value=hex(value),new_value=hex(resident+24512+delta),source_instruction=line))
 assert len(refs)==7
 stage=Path(build['derived_stage']).read_bytes();at=build['staging_address']-0x4000;loader=stage[at:at+40];assert loader[24:28]==bytes.fromhex('303c27ff')and(int.from_bytes(loader[26:28],'big')+1)*2==20480
 reserve=24512;heap=resident+reserve;assert heap==0x164d80 and 40+reserve<=build['staging_bytes_cleared']==24576
 initializer_address=(resident+len(raw)+3)&~3;alignment=initializer_address-resident-len(raw);total=len(raw)+alignment+init['binary_bytes'];assert init['binary_bytes']==1620 and total==21080
 facts=dict(status='terminal_read_only_initializer_layout_plan_no_changes',directory=str(out),parent_used=19460,current_reserve=20480,proposed_reserve=reserve,reserve_increase=4032,current_heap_floor=hex(floor),proposed_heap_floor=hex(heap),heap_end='0x1c0000',current_initial_heap_bytes=0x1c0000-floor,proposed_initial_heap_bytes=0x1c0000-heap,heap_floor_operand_relocations=refs,loader_count=dict(operand_address=hex(build['staging_address']+26),old_WORD='0x27ff',new_WORD=hex(reserve//2-1),instruction=loader[24:28].hex()),old_native_entry_bytes=build['native_entry_bytes'],new_native_entry_bytes=40+reserve,staging_clear_bytes=24576,remaining_cleared_staging_tail=24576-40-reserve,initializer_address=hex(initializer_address),initializer_bytes=1620,alignment_bytes=alignment,proposed_used=total,proposed_reserve_free=reserve-total,changes_made=False,adoption_requirements=['Relocate the seven decoded heap-floor/+4/+8 operands and loader WORD count with byte provenance, then relink initializer at final address.','Recheck full native heap/allocator/compaction/resource/task and startup/loader behavior for new boundary/capacity; no assumption that a raw literal scan proves every dependency.','Joint native13AE0/134DCframes need actual context-canary/interval guards; SPbelowparent-context is not itself a collision when the child intentionally skips to a deeper private frame.','Run real-child gameplay against layout-only and original-entry controls, retaining existing timing/media limitations; broader resource paths remain necessary.'],source_sha256={str(p):sha(p)for p in [Path(__file__),bp,ip,Path(build['linked_component']),Path(build['derived_stage']),ROOT/'projects/black-ice-white-noise/restoration/native-m68k/heap-initialize.S',ROOT/'projects/black-ice-white-noise/restoration/native-m68k/heap-native.h',asm]},scope=__doc__)
 save(out/'protocol.json',facts);save(v/'actor-initializer-layout-plan-current.json',facts);print(json.dumps({k:facts[k]for k in ['status','proposed_reserve','proposed_heap_floor','initializer_address','proposed_used','proposed_reserve_free','remaining_cleared_staging_tail']}))

if __name__=='__main__':main()
