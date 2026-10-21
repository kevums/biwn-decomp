"""Rebuild the component with copied sources/SDK;never reuse its object files."""
import subprocess
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha
from publish_geometry_records_progress_v1 import clone


def main():
    rp=V/'native-input-prototype-v1-current.json';r=read(rp)
    assert r['cases']==425 and r['payload_bytes']==10240
    for path,digest in r['source_sha256'].items():assert sha(path)==digest,path
    relative=Path('projects/black-ice-white-noise/restoration/native-m68k/input-dispatch-native-v1')
    source=ROOT/relative;copied=P/'workbench'/relative;copied.mkdir(parents=True,exist_ok=True)
    for file in source.iterdir():
        if file.is_file():clone(file,copied/file.name)
    for name in ['biwn_input_dispatch.h','biwn_world_update.h','biwn_signed_division.c','biwn_signed_division.h']:
        original=ROOT/'projects/black-ice-white-noise/restoration'/name
        target=P/'workbench'/original.relative_to(ROOT)
        assert target.exists()and sha(target)==sha(original),target
    sdk=P/'workbench/tools/m68k-elf';gcc=sdk/'bin/m68k-elf-gcc'
    assert gcc.resolve().is_relative_to(P) and sha(gcc)==sha(ROOT/'tools/m68k-elf/bin/m68k-elf-gcc')
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out=V/'native-input-copied-build-v1'/stamp;out.mkdir(parents=True)
    build=P/'workbench/builds/native-input-copied-v1'/stamp
    command=['make','BUILD='+str(build)];q=subprocess.run(command,cwd=copied,capture_output=True,text=True)
    (out/'compiler.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
    payload=build/'native-input.bin';assert payload.read_bytes()==Path(r['payload']).read_bytes()
    clone(payload,out/'copied-native-input.bin')
    facts=dict(status='terminal_native_input_copied_sources_SDK_build_byte_identical',directory=str(out),
        copied_source=str(copied),copied_build=str(build),copied_SDK=str(sdk),bytes=payload.stat().st_size,
        copied_compiler_resolves_inside_package=True,byte_identical=True,new_predictions=0,new_training=False,
        new_disc_built=False,source_sha256={str(p):sha(p)for p in [Path(__file__),rp,out/'compiler.log',out/'copied-native-input.bin']},
        copied_source_sha256={str(p):sha(p)for p in copied.iterdir()if p.is_file()})
    save(out/'review.json',facts);save(V/'native-input-copied-build-v1-current.json',facts)
    print(facts['status'],facts['bytes'],'bytes',flush=True)


if __name__=='__main__':main()
