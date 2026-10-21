"""Bind prior exact-v39 copied shared-piece rebuild to this final bridge payload."""
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
from publish_geometry_records_progress_v1 import clone
def main():
 gp=V/'scene17-input-arena-image-final-bridge-v1-current.json';g=read(gp)
 cp=V/'input-arena-image-copied-rebuild-v1-current.json';c=read(cp)
 for proof in [g,c]:
  for p,h in proof['source_sha256'].items():assert sha(p)==h,p
 piece=next(p for p in c['pieces']if p['piece']=='shared');assert piece['bytes']==54134 and piece['identical']
 assert Path(piece['copied_binary']).read_bytes()==Path(g['payload']).read_bytes()
 out=V/'input-arena-image-final-copied-rebuild-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 blob=out/'checked-copied-shared.bin';clone(Path(piece['copied_binary']),blob)
 state=dict(status='terminal_copied_shared_final_bridge_bytes_match_prior_exact_v39_rebuild',directory=str(out),payload=str(blob),bytes=54134,same_as_selected_prototype_module=True,reused_terminal_new_piece_proof=True,new_compilation=False,new_predictions=0,new_training=False,final_disc_integrated=True,final_disc_gameplay_verified=False,source_sha256={str(p):sha(p)for p in [Path(__file__),gp,cp,blob]})
 save(out/'protocol.json',state);save(V/'input-arena-image-final-copied-rebuild-v1-current.json',state);print(state['status'])
if __name__=='__main__':main()
