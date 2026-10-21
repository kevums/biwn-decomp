"""Compile a separate static-C instruction provider for the tested native disc.

This is instruction-provider integration, not new original-game source recovery.
The atlas is build metadata only; it is never restored into a gameplay machine.
"""
import json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
import capstone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
 bp=ROOT/'verification/native-fast-core-wait-format-disc-build-current.json';build=json.loads(bp.read_text());assert sha(build['derived_disc'])==build['derived_disc_sha256']
 recipep=ROOT/'verification/interactive-preview-recipe.json';recipe=json.loads(recipep.read_text());command=recipe['candidate'];basep=Path(command[command.index('--CPU-candidate')+1]);base=json.loads(basep.read_text());atlasp=Path(base['instruction_RAM_source']);before=atlasp.read_bytes();assert len(before)==0x200000
 atlas=bytearray(before);atlas[0x4000:0x100000]=Path(build['derived_stage']).read_bytes();payload=Path(build['component']).read_bytes();atlas[build['resident_address']:build['resident_address']+len(payload)]=payload
 out=ROOT/'verification/native-formatter-C-runtime-preparation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 atlasfile=out/'instruction-atlas.bin';atlasfile.write_bytes(atlas)
 decoder=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
 def instruction(memory,pc):
  value=next(decoder.disasm(memory[pc:pc+24],pc,count=1));assert not value.mnemonic.startswith('dc.'),(hex(pc),value.mnemonic);return value
 rows={};affected=[];discard=[]
 patches=json.loads(Path(build['patch_manifest']).read_text())['patches']
 jumps={int(p['address'],16):bytes.fromhex(p['replacement'])for p in patches if bytes.fromhex(p['replacement'])[:2]==b'\x4e\xf9'}
 old_overlay=Path(command[command.index('--experimental-code-overlay')+1]);variant_blocks=[]
 for patch in json.loads(old_overlay.read_text())['patches']:
  start=int(patch['address'],16);stop=start+len(bytes.fromhex(patch['replacement']))
  if any(start<=int(key,16)<stop for key in base['selected_case_sources']):
   variant_blocks.append((start,stop));affected.append([start,stop])
   position=start
   while position<stop:
    ins=instruction(atlas,position);rows[position]=ins;position+=ins.size
    if ins.mnemonic=='jmp':break
 # Existing instruction starts inside a new absolute JMP operand are dead
 # metadata, not valid instructions. Remove them from the new identity atlas.
 for key in base['selected_case_sources']:
  pc=int(key,16)
  if pc in [0x303c,0x3042,0x304e,0x4088]:continue
  if any(start<=pc<stop for start,stop in variant_blocks):
   if pc not in rows:discard.append(pc)
   continue
  if any(start<pc<start+6 for start in jumps):discard.append(pc);affected.append([pc,pc+2]);continue
  old=instruction(before,pc)
  if before[pc:pc+old.size]!=atlas[pc:pc+old.size]:
   ins=instruction(atlas,pc);rows[pc]=ins;affected.append([pc,pc+old.size])
 for start,stop in [(build['staging_address'],build['staging_address']+40)]:
  position=start
  while position<stop:
   ins=instruction(atlas,position);assert ins.address==position and position+ins.size<=stop
   rows[position]=ins;position+=ins.size
  assert position==stop
 bundlep=ROOT/'verification/native-fast-core-format-bundle-current.json';bundle=json.loads(bundlep.read_text())
 assert Path(build['linked_component']).read_bytes()[:bundle['binary_bytes']]==Path(bundle['binary']).read_bytes()
 elf_sources=[Path(bundle['ELF']),Path(build['directory'])/'wait.elf'];prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-')
 for index,elf in enumerate(elf_sources):
  listing_text=subprocess.check_output([prefix+'objdump','-d',str(elf)],text=True);(out/f'ELF-{index}-disassembly.txt').write_text(listing_text)
  for line in listing_text.splitlines():
   fields=line.split('\t')
   if len(fields)<3 or not fields[0].strip().endswith(':')or not fields[2].strip():continue
   try:pc=int(fields[0].strip()[:-1],16)
   except ValueError:continue
   assert build['resident_address']<=pc<build['resident_address']+build['linked_component_bytes']
   rows[pc]=instruction(atlas,pc)
 # Include every stage redirect, including a start absent from an older
 # static catalogue. Unchanged original-source entries remain inherited.
 for pc in jumps:
  if pc>=build['staging_address']:continue
  rows[pc]=instruction(atlas,pc);affected.append([pc,pc+6])
 listing=out/'new-instructions.json';save(listing,dict(instructions=[dict(address=hex(pc),size=ins.size,bytes=bytes(ins.bytes).hex(),assembly=ins.mnemonic+' '+ins.op_str)for pc,ins in sorted(rows.items())],static_addresses_are_not_execution_coverage=True,discarded_stale_instruction_starts=[hex(x)for x in discard]))
 candidate=out/'CPU-candidate.json';builder=ROOT/'scripts/build_biwn_route_CPU.py';reference=Path(base['warm_RAM_source']).parent
 cmd=[str(ROOT/'.venv/bin/python'),'-u',str(builder),'--reference',str(reference),'--base-candidate',str(basep),'--output-manifest',str(candidate),'--static-listing',str(listing),'--instruction-RAM',str(atlasfile),'--function','biwn_native_formatter_translated_step','--movie-privileged-events']
 for lo,hi in sorted(set(map(tuple,affected))):cmd+=['--replace-source-range',hex(lo),hex(hi)]
 state=dict(status='building_static_C_native_formatter_provider',pid=os.getpid(),directory=str(out),base_CPU_candidate=str(basep),build_proof=str(bp),build_proof_sha256=sha(bp),instruction_atlas=str(atlasfile),atlas_is_metadata_only=True,new_static_instruction_starts=len(rows),discarded_stale_starts=len(discard),candidate=str(candidate),command=cmd,source_sha256={str(p):sha(p)for p in [Path(__file__),bp,recipep,basep,atlasp,Path(base['library']),Path(build['derived_stage']),Path(build['component']),Path(build['patch_manifest']),atlasfile,listing,builder]},new_training=False,default_promoted=False,whole_game_complete=False)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-formatter-C-runtime-preparation-active.json',state)
 mark()
 with(out/'build.log').open('w')as log:
  child=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;mark();code=child.wait()
 state.update(status='terminal_static_C_provider_compiled_pending_verification'if code==0 else'terminal_C_provider_requires_additional_semantics',exit_code=code)
 if code==0:
  d=json.loads(candidate.read_text());state.update(C_library=d['library'],C_library_sha256=sha(d['library']),generated_source=str(Path(d['directory'])/'biwn_route_CPU.c'),generated_source_sha256=d['source_sha256'],selected_cases=len(d['selected_case_sources']))
 mark();save(ROOT/'verification/native-formatter-C-runtime-preparation-current.json',state);print(json.dumps({k:state[k]for k in ['status','new_static_instruction_starts','discarded_stale_starts','exit_code']}),flush=True)
 if code:print((out/'build.log').read_text()[-4000:],flush=True)

if __name__=='__main__':main()
