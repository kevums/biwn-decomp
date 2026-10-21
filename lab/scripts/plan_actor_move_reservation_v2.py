"""Read-only movement integration plan with Atari trailer explicitly preserved."""
import json,subprocess
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
 bp=ROOT/'verification/native-sprite-create-disc-build-current.json';mp=ROOT/'verification/native-actor-move-direction-current.json';b=read(bp);m=read(mp);raw=Path(b['linked_component']).read_bytes();stage=Path(b['derived_stage']).read_bytes();resident=b['resident_address'];floor=b['heap_start'];assert len(raw)==23260 and b['component_bytes']==24512 and m['cases']==2624 and m['binary_bytes']==2960
 out=ROOT/'verification/actor-move-layout-plan'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);asm=out/'current-resident.asm';assembly=subprocess.check_output([str(ROOT/'tools/m68k-elf/bin/m68k-elf-objdump'),'-D','-b','binary','-m','m68k:68000','--adjust-vma='+hex(resident),b['linked_component']],text=True);asm.write_text(assembly);lines={int(p,16):line.strip()for line in assembly.splitlines()if':'in line and(p:=line.split(':',1)[0].strip())and all(x in'0123456789abcdef'for x in p)}
 reserve=28544;newfloor=resident+reserve;refs=[]
 for delta in [0,4,8]:
  value=floor+delta
  for i in range(len(raw)-3):
   if raw[i:i+4]!=value.to_bytes(4,'big'):continue
   pc=resident+i-2;line=lines[pc];assert(f'{value:x}'in line or str(value)in line)and any(x in line for x in ['move','sub','clr','cmp']),line;refs.append(dict(operand=hex(resident+i),instruction=hex(pc),old=hex(value),new=hex(newfloor+delta),decoded=line))
 assert len(refs)==7
 current_staging=b['staging_address'];new_staging=current_staging-4096;new_clear=28672;assert new_staging==0xf7000 and new_staging+new_clear==0xfe000 and not any(stage[new_staging-0x4000:current_staging-0x4000])
 trailer=stage[0xfe000-0x4000:0xff000-0x4000];nonzero=[i for i,v in enumerate(trailer)if v];assert len(nonzero)==94 and trailer[0x520:].startswith(b'ATARI APPROVED DATA TAILER ')
 # Merely growing the old staging buffer would overlap the real trailer.
 assert current_staging+40+reserve>0xfe520
 assert stage[:6]==bytes.fromhex('4ef9000f8000')
 loader=stage[current_staging-0x4000:current_staging-0x4000+40];assert loader[24:28]==bytes.fromhex('303c2fdf')
 assert raw[0x14:0x1e]==bytes.fromhex('41f9000f8000303c2fff')
 address=(resident+len(raw)+3)&~3;used=address-resident+m['binary_bytes'];assert address==0x16489c and used==26220 and newfloor==0x165d40
 state=dict(status='terminal_read_only_actor_move_layout_plan_no_changes',directory=str(out),current_resident_bytes=23260,new_movement_bytes=2960,proposed_used=used,proposed_reserve=reserve,proposed_free_bytes=reserve-used,current_heap_floor=hex(floor),proposed_heap_floor=hex(newfloor),proposed_initial_heap_bytes=0x1c0000-newfloor,heap_capacity_reduction=reserve-b['component_bytes'],heap_operands=refs,proposed_code_address=hex(address),staging=dict(old=hex(current_staging),new=hex(new_staging),old_clear=24576,new_clear=new_clear,final_clear_end='0xfe000',newly_used_original_zero_bytes=4096,new_copy_WORD=hex(reserve//2-1),new_clear_WORD=hex(new_clear//2-1),payload_bytes_with_loader=40+reserve,cleared_tail_bytes=new_clear-40-reserve,requires_4000_JMP_and_resident_finalizer_LEA=True),trailer=dict(range=['0xfe000','0xff000'],nonzero_bytes=94,first_nonzero='0xfe520',label='ATARI APPROVED DATA TAILER',sha256=__import__('hashlib').sha256(trailer).hexdigest(),preserved_by_proposed_copy_clear=True,naive_old_staging_growth_would_overlap=True),changes_made=False,adoption_requirements=['Rebuild a layout-only clone with all seven heap operands, shifted staging, startup JMP, finalizer LEA and clear/copy counts; preserve exact trailer bytes and source disc.','Full CPU/bank/RAM copy+clear startup and native/ordered allocator/compactor/copy/capacity validation at new boundary, then final-address movement relink.','Qualify saved-context canaries and actual original direction/GPU/collision helper/task frames; current672private fixture depth is not a live task bound.','Run whole real-helper gameplay against layout-only/original-entry control, retain video/audio/state disagreements and current default preview.'],source_sha256={str(p):sha(p)for p in [Path(__file__),bp,mp,Path(b['linked_component']),Path(b['derived_stage']),Path(m['binary']),asm]},scope=__doc__)
 save(out/'protocol.json',state);save(ROOT/'verification/actor-move-layout-plan-current.json',state);print(json.dumps({k:state[k]for k in ['status','proposed_used','proposed_reserve','proposed_free_bytes','proposed_heap_floor','proposed_code_address']}))
if __name__=='__main__':main()
