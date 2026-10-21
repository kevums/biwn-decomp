"""Copied SDK rebuild of newly linked v39 pieces, not a source-only full game."""
import os
import subprocess
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha
from publish_geometry_records_progress_v1 import clone


def main():
    bp=V/'native-input-arena-disc-build-v1-current.json';b=read(bp)
    for p,h in b['source_sha256'].items():assert sha(p)==h,p
    out=V/'input-arena-image-copied-rebuild-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    copied=P/'workbench/builds/native-input-resource-arena-v39'/out.name;copied.mkdir(parents=True)
    nd=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';rows=[];logs=[]
    for name,source,args,binary,address in [
        ('shared','deck-shared-v34-record-strides-v1',['ADDRESS='+hex(b['shared_Deck_code_address']),'ARENA_ADDRESS='+hex(b['deck_arena_address'])],'native-shared.bin',b['shared_Deck_code_address']),
        ('outer','deck-outer-v32-compact-v1',['ADDRESS='+hex(b['outer_code_address']),'ARENA_ADDRESS='+hex(b['outer_arena_address']),'DECK_ADDRESS='+hex(b['deck_arena_address'])],'native-outer.bin',b['outer_code_address'])]:
        src=P/'workbench'/(nd/source).relative_to(ROOT)
        for path in (nd/source).iterdir():
            if path.is_file():assert (src/path.name).is_file()and sha(path)==sha(src/path.name),path
        relative=Path('../../../../../builds/native-input-resource-arena-v39')/out.name/name
        result=subprocess.run(['make','BUILD='+str(relative),*args],cwd=src,capture_output=True,text=True)
        log=out/(name+'-copied-build.log');log.write_text(result.stdout+result.stderr);logs.append(log);assert result.returncode==0,result.stderr
        blob=(copied/name/binary).read_bytes();expected=Path(b['component']).read_bytes()[address-b['resident_address']:address-b['resident_address']+len(blob)]
        assert blob==expected
        rows.append(dict(piece=name,bytes=len(blob),copied_binary=str(copied/name/binary),sha256=sha(copied/name/binary),identical=True))
    cross=str(P/'workbench/tools/m68k-elf/bin/m68k-elf-');src=Path(b['resource_arena_source_profile']);copied_source=P/'workbench'/src.relative_to(ROOT)
    for name in ['native-acquire.S','native.ld']:assert sha(src/name)==sha(copied_source/name)
    resource=copied/'resource';resource.mkdir()
    commands=[[cross+'as','-m68000','-o',str(resource/'native.o'),str(copied_source/'native-acquire.S')],
        [cross+'ld','--defsym=NATIVE_ADDRESS='+hex(b['resource_arena_code_address']),'--defsym=GPU_ARENA_BASE='+hex(b['arena_address']),'--defsym=ACQUIRE_BODY='+hex(b['symbols']['biwn_native_resource_acquire_body']),'-T',str(copied_source/'native.ld'),'-o',str(resource/'native.elf'),str(resource/'native.o')],
        [cross+'objcopy','-O','binary',str(resource/'native.elf'),str(resource/'native.bin')]]
    finalizer=copied/'finalizer';finalizer.mkdir()
    for name in ['finalizer.S','finalizer.ld']:clone(Path(b['directory'])/name,finalizer/name)
    commands +=[[cross+'as','-m68000','-o',str(finalizer/'native.o'),str(finalizer/'finalizer.S')],
        [cross+'ld','-T',str(finalizer/'finalizer.ld'),'-o',str(finalizer/'native.elf'),str(finalizer/'native.o')],
        [cross+'objcopy','-O','binary',str(finalizer/'native.elf'),str(finalizer/'native.bin')]]
    for index,command in enumerate(commands):
        result=subprocess.run(command,capture_output=True,text=True);log=out/f'command-{index}.log';log.write_text(result.stdout+result.stderr);logs.append(log);assert result.returncode==0,result.stderr
    for name,binary,address,count in [('resource',resource/'native.bin',b['resource_arena_code_address'],676),('finalizer',finalizer/'native.bin',b['deck_finalizer_address'],248)]:
        blob=binary.read_bytes();expected=Path(b['component']).read_bytes()[address-b['resident_address']:address-b['resident_address']+count];assert len(blob)==count and blob==expected
        clone(binary,out/(name+'-copied.bin'));rows.append(dict(piece=name,bytes=count,copied_binary=str(binary),sha256=sha(binary),identical=True))
    v6_path=V/'native-input-arena-admission-v6-current.json';v6=read(v6_path);input_binary=Path(v6['copied_build'])/'native-input.bin'
    assert input_binary.read_bytes()==Path(b['native_input_payload']).read_bytes()
    rows.append(dict(piece='input-v6',bytes=10580,copied_binary=str(input_binary),sha256=sha(input_binary),identical=True,prior_terminal_copied_build_reused=True))
    save(out/'pieces.json',rows);save(out/'commands.json',commands)
    paths=[Path(__file__),bp,v6_path,Path(b['component']),src/'native-acquire.S',src/'native.ld',Path(b['directory'])/'finalizer.S',Path(b['directory'])/'finalizer.ld',out/'pieces.json',out/'commands.json',out/'resource-copied.bin',out/'finalizer-copied.bin',*logs]
    state=dict(status='terminal_v39_newly_relinked_pieces_copied_SDK_byte_identical',directory=str(out),pid=os.getpid(),copied_build=str(copied),pieces=rows,newly_compiled_pieces=4,prior_input_rebuild_reused=True,full_source_only_game_rebuild=False,inherited_prefix_not_recompiled=True,disc_changed=False,new_predictions=0,optimizer_updates=0,source_sha256={str(p):sha(p)for p in paths},scope=__doc__)
    save(out/'protocol.json',state);save(V/'input-arena-image-copied-rebuild-v1-current.json',state);print(state['status'],flush=True)


if __name__=='__main__':main()
