"""Rebuild both deployed compact-image modules with copied sources and SDK."""
import subprocess
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha

def main():
    bp=V/'native-outer-compact-disc-build-v1-current.json';b=read(bp)
    out=V/'outer-compact-copied-modules-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    resident=Path(b['component']).read_bytes();rows=[];sources=[];copied=[]
    for profile,stem,address,arena,extra in [
        ('deck-shared-v30-scene-gpu-commands-v1','native-shared',b['shared_Deck_code_address'],b['deck_arena_address'],[]),
        ('deck-outer-v32-compact-v1','native-outer',b['outer_code_address'],b['outer_arena_address'],['DECK_ADDRESS='+hex(b['deck_arena_address'])])]:
        src=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'/profile;dst=P/'workbench'/src.relative_to(ROOT)
        if not dst.exists():subprocess.run(['/bin/cp','-cR',str(src),str(dst)],check=True,capture_output=True)
        for path in src.rglob('*'):
            if path.is_file():assert sha(path)==sha(dst/path.relative_to(src));sources.append(path);copied.append(dst/path.relative_to(src))
        build=out/profile;command=['make','BUILD='+str(build),'ADDRESS='+hex(address),'ARENA_ADDRESS='+hex(arena),*extra]
        q=subprocess.run(command,cwd=dst,capture_output=True,text=True);(out/(profile+'-compiler.log')).write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
        payload=build/(stem+'.bin');data=payload.read_bytes();assert data==resident[address-b['resident_address']:address-b['resident_address']+len(data)]
        rows.append(dict(profile=profile,payload=str(payload),bytes=len(data),sha256=sha(payload),deployed_module_byte_identical=True,copied_source=str(dst)))
    save(out/'modules.json',rows)
    state=dict(status='terminal_both_compact_image_modules_copied_SDK_byte_identical',directory=str(out),modules=rows,copied_SDK=str(P/'workbench/tools/m68k-elf'),new_predictions=0,new_training=False,fresh_gameplay_verified=False,
        source_sha256={str(p):sha(p)for p in [Path(__file__),bp,*sources,out/'modules.json',*[Path(x['payload'])for x in rows]]},copied_source_sha256={str(p):sha(p)for p in copied})
    save(out/'protocol.json',state);save(V/'outer-compact-copied-modules-v1-current.json',state);print(state['status'],[x['bytes']for x in rows],flush=True)

if __name__=='__main__':main()
