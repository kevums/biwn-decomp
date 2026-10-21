"""Build final scene module with copied sources and copied68000SDK."""
import shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha

def main():
 gate=read(V/'scene17-clear-final-bridge-v1-current.json');build=read(V/'native-scene17-clear-disc-build-v1-current.json')
 for path,h in gate['source_sha256'].items():assert sha(path)==h,path
 sources=[]
 for rel in ['projects/black-ice-white-noise/restoration/native-m68k/deck-shared-v26-scene-clear','projects/black-ice-white-noise/restoration/experimental/scene-draw-structured-v1','projects/black-ice-white-noise/restoration/experimental/scene-rotation-structured-v1','projects/black-ice-white-noise/restoration/experimental/scene-clear-structured-v1']:
  src=ROOT/rel;dst=P/'workbench'/rel
  if dst.exists():
   for path in src.rglob('*'):
    if path.is_file():assert sha(path)==sha(dst/path.relative_to(src)),path
  else:subprocess.run(['/bin/cp','-cR',str(src),str(dst)],check=True,capture_output=True)
  sources += [p for p in dst.rglob('*')if p.is_file()]
 out=V/'scene17-clear-copied-rebuild-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 copied=P/'workbench/projects/black-ice-white-noise/restoration/native-m68k/deck-shared-v26-scene-clear';command=['make','BUILD='+str(out/'copied-build'),'ADDRESS='+hex(build['shared_Deck_code_address']),'ARENA_ADDRESS='+hex(build['deck_arena_address'])];p=subprocess.run(command,cwd=copied,capture_output=True,text=True);(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 payload=out/'copied-build/native-shared.bin';assert payload.read_bytes()==Path(gate['payload']).read_bytes()
 state=dict(status='terminal_copied_scene17_final_module_byte_identical',directory=str(out),copied_source=str(copied),copied_SDK=str(P/'workbench/tools/m68k-elf'),payload=str(payload),bytes=payload.stat().st_size,sha256=sha(payload),same_as_final_deployed_module=True,new_predictions=0,new_training=False,disc_changed=False,whole_game_complete=False,source_sha256={str(p):sha(p)for p in [Path(__file__),V/'scene17-clear-final-bridge-v1-current.json',payload]},copied_source_sha256={str(p):sha(p)for p in sources});save(out/'protocol.json',state);save(V/'scene17-clear-copied-rebuild-v1-current.json',state);print(state['status'],state['bytes'])
if __name__=='__main__':main()
