"""Exercise rebuilt helpers on prior edge vectors without publishing old gates."""
import argparse,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_startup_rng_cpu as rng
ROOT=rng.ROOT

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--library',type=Path,required=True);parser.add_argument('--per-entry',type=int,default=8);args=parser.parse_args()
 session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rows=json.loads((session/'startup-fullCPU-generation.json').read_text())['instructions_decoded']+json.loads((session/'actor-factory-fullCPU-generation.json').read_text())['instructions_decoded']
 for a,b in [(0xe540,0xe61c),(0x1a77c,0x1a7f4)]:rows+=rng.gen.loader.base.binary_tools.m68k_instructions(snapshot[a:b],a)[0]
 out=ROOT/'verification/atomic-helper-regression'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);runtime=rng.Runtime(args.library.resolve(),rows);results=[];coverage=set()
 try:
  for ram,case in rng.cases(snapshot,args.per_entry):
   left,expected,native=runtime.native(ram,case,coverage);right,actual,rebuilt=runtime.translated(ram,case)
   assert rebuilt['status']==0 and not rebuilt['errors'],(case,rebuilt)
   if bytes(expected)!=bytes(actual)or left!=right:
    (out/'mismatch.json').write_text(json.dumps(dict(case=case,native_CPU=rng.queue.cd.scheduler.cpu_dict(expected),C_CPU=rng.queue.cd.scheduler.cpu_dict(actual),RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(left,right))if a!=b][:80]),indent=2)+'\n');raise AssertionError(out/'mismatch.json')
   results.append(dict(entry=hex(case['entry']),id=case['id'],supervisor=bool(case['SR']&0x2000),instructions=native['instructions'],CPU=rng.queue.cd.scheduler.cpu_dict(actual),RAM_sha256=hashlib.sha256(right).hexdigest()))
  report=dict(status='full_CPU_RAM_math_nested_call_edges_native_C_match',directory=str(out),cases=len(results),supervisor_cases=sum(x['supervisor']for x in results),library=str(args.library.resolve()),library_sha256=hashlib.sha256(args.library.read_bytes()).hexdigest(),results=results,new_unique_game_coverage=False,new_weight_training=False,scope='Prior startup RNG entry edge vectors, including nested new math, both stack banks. Independent emulator instruction execution is reference; not whole game/global timing or model-generalization proof.',whole_game_complete=False)
  (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(results),flush=True)
 except BaseException as e:(out/'status.json').write_text(json.dumps(dict(status='failed',error=repr(e)))+'\n');raise
 finally:runtime.close()
if __name__=='__main__':main()
