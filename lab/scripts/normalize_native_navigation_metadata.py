"""Scope inherited movement metadata separately from the newly added navigation group."""
import json,copy
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
 v=ROOT/'verification';p=v/'native-actor-navigation-disc-build-current.json';b=json.loads(p.read_text());out=v/'native-navigation-build-metadata'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);save(out/'as-built.json',b);n=copy.deepcopy(b)
 for key in ['final_gate_command']:n.pop(key,None)
 n.update(source=b['navigation_source'],sources=list(dict.fromkeys(b['sources']+[b['navigation_source']])),semantic_code_bytes=1428,new_native_bytes=1428,replaced_native_bytes=0,navigation_context_bytes=72,navigation_private_reserve=96,calling_convention='Fourleafnavigationroots retain original public ABI;72byte logicalCPUcontext/private96bytes. Inherited shared movement/collision chain separately retains80byte context/private320bytes.',metadata_correction='Generic new-source/bytes fields now identify navigation,not the inherited chain. Original as-built receipt and its layout gates remain immutable.',superseded_build_metadata=str(out/'as-built.json'),superseded_build_metadata_sha256=sha(out/'as-built.json'))
 n['source_sha256'].update({str(Path(__file__)):sha(Path(__file__)),str(out/'as-built.json'):sha(out/'as-built.json')});save(out/'normalized-build.json',n);save(v/'native-actor-navigation-build-normalized-current.json',n);print('Normalized navigation metadata; image unchanged')
if __name__=='__main__':main()
