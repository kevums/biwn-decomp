"""Assemble both repair sites and compare exact installed native-disc bytes."""
import subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_native_deck_fresh_restore_v1 as common
ROOT=common.ROOT;V=ROOT/'verification';read=common.read;save=common.save;sha=common.sha
def main():
    out=V/'native-Deck-selector13-source'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    source=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';prefix=ROOT/'tools/m68k-elf/bin/m68k-elf-';asm=source/'deck-selector13-restoration.S';ld=source/'deck-selector13-restoration.ld'
    commands=[[str(prefix)+'gcc','-m68000','-c',str(asm),'-o',str(out/'repair.o')],[str(prefix)+'ld','-T',str(ld),str(out/'repair.o'),'-o',str(out/'repair.elf')]]
    for section,name in [('selector13','selector.bin'),('frame_count','count.bin')]:commands.append([str(prefix)+'objcopy','-O','binary','--only-section=.'+section,str(out/'repair.elf'),str(out/name)])
    for command in commands:
        result=subprocess.run(command,capture_output=True,text=True);assert result.returncode==0,result.stderr
    build=read(V/'native-Deck-asset-repair-build-current.json');stage=Path(build['derived_stage']).read_bytes();rows=[]
    for address,name,size in [(0x10ac2,'selector.bin',36),(0x464a6,'count.bin',2)]:
        data=(out/name).read_bytes();assert len(data)==size and data==stage[address-0x4000:address-0x4000+size]
        rows.append(dict(address=hex(address),bytes=size,hex=data.hex(),installed_stage_exact=True))
    state=dict(status='terminal_source_assembled_38byte_Deck_repair_matches_installed_stage',directory=str(out),commands=commands,sites=rows,new_training=False,local_model_authored=False,native_disc_changed=False,whole_game_complete=False,source_sha256={str(p):sha(p)for p in [Path(__file__),asm,ld,Path(build['derived_stage']),out/'repair.elf',out/'selector.bin',out/'count.bin']},scope='Actual68000assembler/linker output for the38byte two-site restoration repair, exact installed stage match. Retained whole program is not rebuilt from source; original behavior changes16 to13 and returned-D0 error check.')
    save(out/'report.json',state);save(V/'native-Deck-selector13-source-current.json',state);print(state['status'],flush=True)
if __name__=='__main__':main()
