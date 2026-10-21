"""Copied SDK builds changed v40 pieces; unchanged input/resource proofs reused."""
import os
import subprocess
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha
from publish_geometry_records_progress_v1 import clone


def main():
    bp=V/'frame-acquire-phased-disc-build-v1-current.json';b=read(bp)
    for path,digest in b['source_sha256'].items():assert sha(path)==digest,path
    out=V/'frame-phased-image-copied-rebuild-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    copied=P/'workbench/builds/frame-phased-image-v40'/out.name;copied.mkdir(parents=True)
    nd=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';rows=[];paths=[Path(__file__),bp,Path(b['component'])]
    for name,profile,args,pieces in [
        ('shared','deck-shared-v34-record-strides-v1',['ADDRESS='+hex(b['shared_Deck_code_address']),'ARENA_ADDRESS='+hex(b['deck_arena_address'])],[('shared','native-shared.bin',b['shared_Deck_code_address'],54134)]),
        ('outer','deck-outer-v32-compact-v1',['ADDRESS='+hex(b['outer_code_address']),'ARENA_ADDRESS='+hex(b['outer_arena_address']),'DECK_ADDRESS='+hex(b['deck_arena_address'])],[('outer','native-outer.bin',b['outer_code_address'],6060)]),
        ('frame','frame-acquire-phased-split-v2',['ADDRESS='+hex(b['frame_phased_early_address']),'TAIL_ADDRESS='+hex(b['frame_phased_tail_address'])],[('frame-early','early.bin',b['frame_phased_early_address'],1536),('frame-tail','tail.bin',b['frame_phased_tail_address'],240)])]:
        source=nd/profile;dest=P/'workbench'/source.relative_to(ROOT)
        for p in source.iterdir():
            if not p.is_file():continue
            if profile=='frame-acquire-phased-split-v2':clone(p,dest/p.name)
            assert sha(p)==sha(dest/p.name),p
            paths.append(p)
        header=nd/'frame-acquire-lean.h';clone(header,P/'workbench'/header.relative_to(ROOT));paths.append(header)
        relative=Path('../../../../../builds/frame-phased-image-v40')/out.name/name
        result=subprocess.run(['make','BUILD='+str(relative),*args],cwd=dest,capture_output=True,text=True)
        log=out/(name+'-copied-build.log');log.write_text(result.stdout+result.stderr);paths.append(log);assert result.returncode==0,result.stderr
        for piece,binary,address,count in pieces:
            p=copied/name/binary;blob=p.read_bytes();assert len(blob)==count and blob==Path(b['component']).read_bytes()[address-b['resident_address']:address-b['resident_address']+count]
            saved=out/(piece+'-copied.bin');clone(p,saved);paths.append(saved);rows.append(dict(piece=piece,bytes=count,copied_binary=str(p),sha256=sha(p),identical=True,new_compilation=True))
    final=copied/'finalizer';final.mkdir();cross=str(P/'workbench/tools/m68k-elf/bin/m68k-elf-')
    for name in ['finalizer.S','finalizer.ld']:clone(Path(b['directory'])/name,final/name);paths.append(Path(b['directory'])/name)
    commands=[[cross+'as','-m68000','-o',str(final/'native.o'),str(final/'finalizer.S')],[cross+'ld','-T',str(final/'finalizer.ld'),'-o',str(final/'native.elf'),str(final/'native.o')],[cross+'objcopy','-O','binary',str(final/'native.elf'),str(final/'native.bin')]]
    for index,command in enumerate(commands):
        result=subprocess.run(command,capture_output=True,text=True);log=out/f'finalizer-{index}.log';log.write_text(result.stdout+result.stderr);paths.append(log);assert result.returncode==0,result.stderr
    blob=(final/'native.bin').read_bytes();at=b['deck_finalizer_address']-b['resident_address'];assert len(blob)==248 and blob==Path(b['component']).read_bytes()[at:at+248]
    saved=out/'finalizer-copied.bin';clone(final/'native.bin',saved);paths.append(saved);rows.append(dict(piece='finalizer',bytes=248,copied_binary=str(final/'native.bin'),sha256=sha(saved),identical=True,new_compilation=True))
    prior_path=V/'input-arena-image-copied-rebuild-v1-current.json';prior=read(prior_path);paths.append(prior_path)
    for r in prior['pieces']:
        if r['piece']not in ['resource','input-v6']:continue
        address=b['resource_arena_code_address']if r['piece']=='resource'else b['native_input_address'];blob=Path(r['copied_binary']).read_bytes()
        assert len(blob)==r['bytes'] and blob==Path(b['component']).read_bytes()[address-b['resident_address']:address-b['resident_address']+len(blob)]
        saved=out/(r['piece']+'-retained.bin');saved.write_bytes(blob);paths.append(saved);rows.append(dict(r,new_compilation=False,prior_terminal_exact_piece_reused=True))
    assert len(rows)==7 and sum(r['new_compilation']for r in rows)==5
    save(out/'pieces.json',rows);paths.append(out/'pieces.json')
    state=dict(status='terminal_v40_changed_pieces_copied_SDK_byte_identical',directory=str(out),pid=os.getpid(),pieces=rows,newly_compiled_pieces=5,new_builds=4,prior_input_and_resource_rebuilds_reused=True,inherited_prefix_not_fully_recompiled=True,full_source_only_game_rebuild=False,new_predictions=0,new_training=False,source_sha256={str(p):sha(p)for p in paths})
    save(out/'protocol.json',state);save(V/'frame-phased-image-copied-rebuild-v1-current.json',state);print(state['status'],flush=True)


if __name__=='__main__':main()
