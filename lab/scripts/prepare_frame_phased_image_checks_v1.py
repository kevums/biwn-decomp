"""Prepare isolated final-address v40 checks; retain prior frozen evidence."""
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

def main():
 old=read(V/'input-arena-image-check-preparation-v1-current.json')
 mapping={name:name.replace('input_arena_image','frame_phased_image')for name in old['modules'].values()}
 out=V/'frame-phased-image-check-preparation-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);paths=[]
 for source,target in sorted(mapping.items()):
  p=ROOT/'scripts'/(source+'.py');text=p.read_text()
  for a,b in sorted(mapping.items(),key=lambda x:-len(x[0])):text=text.replace(a,b)
  text=text.replace('input_arena_image','frame_phased_image').replace('input-arena-image','frame-phased-image').replace('native-input-arena-disc-build-v1','frame-acquire-phased-disc-build-v1').replace('native-frame-phased-image-startup-heap-v1-current.json','frame-acquire-phased-image-startup-heap-v1-current.json').replace('terminal_v39_','terminal_v40_').replace('exact-v39','exact-v40').replace('exact_v39','exact_v40')
  dst=ROOT/'scripts'/(target+'.py');assert not dst.exists(),dst;compile(text,str(dst),'exec');dst.write_text(text);paths += [p,dst]
 proof=dict(status='terminal_v40_isolated_final_address_modules_prepared',directory=str(out),modules=mapping,new_predictions=0,new_training=False,source_sha256={str(p):sha(p)for p in [Path(__file__),V/'frame-acquire-phased-disc-build-v1-current.json',*paths]})
 save(out/'protocol.json',proof);save(V/'frame-phased-image-check-preparation-v1-current.json',proof);print('Prepared',len(mapping),'v40 modules')
if __name__=='__main__':main()
