from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
from pathlib import Path
p=V/'frame-acquire-phased-image-startup-heap-v1-current.json';g=read(p)
assert g['native_startup_cases']==g['Unicorn_startup_cases']==6 and g['heap_initialize_cases']==192
for f,h in g['source_sha256'].items():assert sha(f)==h,f
g=dict(g,reused_terminal_exact_v40_startup=True,source_sha256={**g['source_sha256'],str(p):sha(p),str(Path(__file__)):sha(__file__)})
save(V/'native-Deck-frame-phased-image-startup-heap-v1-current.json',g)
print('Reused terminal exact-v40 wide startup/heap proof')
