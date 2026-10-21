"""Reveal the scoped experimental loader CDI without promoting a default."""
from pathlib import Path
import argparse,hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--print',action='store_true',dest='print_only');args=p.parse_args();v=ROOT/'verification';bp=v/'native-load-scan-disc-build-current.json';b=json.loads(bp.read_text());entry=json.loads((v/'native-load-scan-disc-entry-current.json').read_text());rp=v/'native-load-scan-route-current.json';route=json.loads(rp.read_text());a=json.loads((v/'native-load-scan-route-analysis-current.json').read_text())
 assert b['status']=='terminal_partial_native_load_disc_built_pending_execution'and entry['build_proof_sha256']==route['build_proof_sha256']==sha(bp);assert entry['status']=='terminal_native_entry_heap_and_component_pass'and a['route_proof_sha256']==sha(rp)and a['both_completed']
 disc=Path(b['derived_disc']);assert sha(disc)==b['derived_disc_sha256']
 print('Experimental source-built loader candidate. Component/startup/adaptive route checks passed. Fixed-input behavior differs from native26; full-game reconstruction remains incomplete. The existing playable preview is unchanged.',flush=True)
 print(disc,flush=True)
 if not args.print_only:subprocess.run(['/usr/bin/open','-R',str(disc)],check=True)
if __name__=='__main__':main()
