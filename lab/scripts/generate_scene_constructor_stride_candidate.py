"""Separate, unpromoted mode3 count/selector13 restoration hypothesis.

Preserve original image and canonical sources. Native reference runs the same
explicit guest-code overlay as the generated candidate, not an argument hook.
This establishes modified-program equivalence, never original-game equivalence.
"""
import argparse,hashlib,json
from pathlib import Path
import generate_scene_constructor_cpu as original

ROOT=original.ROOT
TRAMPOLINE=0x190100

def emit(row):
    if row['assembly']=='nop':
        return f'  case {hex(row["address"])}u: /* nop; unreachable overlay padding */\n   s.cpu.pc={hex(row["address"]+row["size"])}u;break;'
    return original.emit(row)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--inline',action='store_true');options=parser.parse_args()
    source=ROOT/('projects/black-ice-white-noise/restoration/experimental/selector13-inline' if options.inline else 'projects/black-ice-white-noise/restoration/experimental/selector13')
    source.mkdir(parents=True,exist_ok=True)
    atlas_path=ROOT/'verification/zero-warm-startup-instruction-atlas.bin'
    original_ram=atlas_path.read_bytes();ram=bytearray(original_ram)
    assert ram[0x464a6:0x464a8]==b'\x00\x10'
    if not options.inline:assert not any(ram[TRAMPOLINE:TRAMPOLINE+16])
    # JMP trampoline; NOP. Trampoline: MULU.W #13,D0; original saved-ID
    # MOVE.W D0,$403D8; JMP $10ACA. No source acquisition argument adapter.
    patches=[(0x464a6,bytes.fromhex('000d')),
             (0x10ac2,bytes.fromhex('4ef9001901004e71')),
             (TRAMPOLINE,bytes.fromhex('c0fc000d33c0000403d84ef900010aca'))]
    if options.inline:
        # Original36bytes:shift/save/push/call/store/adjust/compareRAM/branch.
        # Multiply needs2extra bytes; comparing the just-saved D0.w directly
        # saves4bytes versus rereading ordinaryRAM. Pad2bytes with NOP.
        block=bytes.fromhex('c0fc000d33c0000403d83f004eb90001ac6833c0000403da584f0c40ffff670000be4e71')
        assert len(block)==0x10ae6-0x10ac2
        patches=[(0x464a6,bytes.fromhex('000d')),(0x10ac2,block)]
    patch_records=[]
    for address,data in patches:
        patch_records.append(dict(address=hex(address),original=ram[address:address+len(data)].hex(),replacement=data.hex()))
        ram[address:address+len(data)]=data
    decoded=[]
    for low,high in [*original.RANGES.items(),*([]if options.inline else[(TRAMPOLINE,TRAMPOLINE+16)])]:
        decoded+=original.loader.base.binary_tools.m68k_instructions(ram[low:high],low)[0]
    canonical=ROOT/'projects/black-ice-white-noise/restoration/experimental/biwn_scene_constructor_cpu.c'
    text=canonical.read_text();start=text.index('  case ');end=text.index('  default:',start)
    text=text[:start]+'\n'.join(emit(row)for row in decoded)+'\n'+text[end:]
    (source/'biwn_scene_constructor_cpu.c').write_text(text)
    header=canonical.with_suffix('.h');(source/header.name).write_bytes(header.read_bytes())
    (source/'patched-test-RAM.bin').write_bytes(ram)
    report=dict(status='generated_unverified_inline_restoration_candidate' if options.inline else 'generated_unverified_restoration_candidate',directory=str(source),
        instructions_decoded=decoded,instructions=len(decoded),patches=patch_records,
        original_atlas_sha256=hashlib.sha256(original_ram).hexdigest(),patched_atlas_sha256=hashlib.sha256(ram).hexdigest(),
        source_sha256=hashlib.sha256(text.encode()).hexdigest(),coordinator_authored=True,
        original_image_modified=False,canonical_source_modified=False,default_promoted=False,heap_trampoline_used=not options.inline,
        scope='Count13 and selector asset*13 guest-code overlay. Same explicit modified program used for native/C comparison. Intended format,other descriptors,cache lifetime/rendering,natural use,whole game and physical hardware unverified.')
    name='scene-constructor-selector13-inline-generation-current.json' if options.inline else 'scene-constructor-selector13-generation-current.json'
    (ROOT/'verification'/name).write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'],len(decoded))

if __name__=='__main__':main()
