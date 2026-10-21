"""Prior scheduler edge/layout/guard vectors against new fixed cases."""
import argparse,ctypes as c,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_scheduler as old
ROOT=old.ROOT

def main():
 p=argparse.ArgumentParser();p.add_argument('--library',type=Path,required=True);args=p.parse_args();out=ROOT/'verification/atomic-scheduler-regression'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 functions=old.bind(c.CDLL(str(args.library.resolve())));snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();native=old.Native();results=[];coverage=set();vectors=old.cases()
 try:
  for i,case in enumerate(vectors):
   a,b=old.cleanup.Script(snapshot,case),old.cleanup.Script(snapshot,case);RAM,cpu,steps=native.original(a,case,coverage);status,actual=old.translated(functions,b,case)
   assert not status and old.cpu_dict(cpu)==old.cpu_dict(actual)and RAM==b.memory,(i,case,status,old.cpu_dict(cpu),old.cpu_dict(actual))
   results.append(dict(case=i,entry=case['entry'],instructions=len(steps),CPU=old.cpu_dict(actual),RAM_sha256=hashlib.sha256(RAM).hexdigest()))
  guards=0
  for entry in old.RANGES:
   case=next(v for v in vectors if v['entry']==entry)
   for missing in range(4):
    script=old.cleanup.Script(snapshot,case);status,cpu=old.translated(functions,script,case,missing=missing);assert status==1 and old.cpu_dict(cpu)==old.cpu_dict(old.make_cpu(case))and not script.trace;guards+=1
   for arg in ['null_cpu','zero_limit']:
    script=old.cleanup.Script(snapshot,case);status,cpu=old.translated(functions,script,case,null_cpu=arg=='null_cpu',limit=0 if arg=='zero_limit'else 64);assert status==1 and old.cpu_dict(cpu)==old.cpu_dict(old.make_cpu(case))and not script.trace;guards+=1
  report=dict(status='scheduler_edges_CPU_RAM_and_required_callback_guards_match',directory=str(out),cases=len(results),guards=guards,library=str(args.library.resolve()),results=results,coverage_PC=sorted(coverage),new_unique_game_coverage=False,whole_game_complete=False)
  (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(results),guards)
 except BaseException as e:(out/'status.json').write_text(json.dumps(dict(status='failed',error=repr(e)))+'\n');raise
 finally:native.close()
if __name__=='__main__':main()
