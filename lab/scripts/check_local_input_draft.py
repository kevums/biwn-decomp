"""After coordinator inspection, execute a local C draft versus original CPU."""
from datetime import datetime,timezone
from pathlib import Path
import argparse,ctypes as c,json,os,subprocess,re
import check_biwn_input_poll as poll
ROOT=poll.ROOT
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def main():
 parser=argparse.ArgumentParser();parser.add_argument('directory');parser.add_argument('role',choices=['author','reviewer','remediator']);parser.add_argument('--diagnostic-warnings',action='store_true');args=parser.parse_args();folder=Path(args.directory).resolve();assert folder.is_relative_to(ROOT/'runs');raw=(folder/(args.role+'-body.txt')).read_text().strip();body=raw;format_cleanup=False;tag=args.role+('-diagnostic'if args.diagnostic_warnings else'')
 if body.startswith('```c\n')and body.endswith('```'):body=body[len('```c\n'):-3].strip();format_cleanup=True
 assert body.startswith('{')and body.endswith('}')and not re.search(r'(?m)^\s*#',body)and '```'not in body
 # Coordinator must inspect this complete small body before invoking this
 # script; generated code only receives private scoped callbacks.
 source='#include "biwn_input_poll.h"\nstatic uint32_t ror32(uint32_t v,unsigned n){return(v>>n)|(v<<(32u-n));}\nstatic uint32_t rol32(uint32_t v,unsigned n){return(v<<n)|(v>>(32u-n));}\nenum biwn_input_status biwn_input_poll(struct biwn_world_bus *bus)\n'+body+'\n'
 path=folder/(args.role+'-candidate.c');path.write_text(source);library=folder/(tag+'-candidate.dylib');command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra']+([]if args.diagnostic_warnings else['-Werror'])+['-I',str(ROOT/'projects/black-ice-white-noise/restoration'),str(path),'-o',str(library)];run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(folder/(tag+'-compiler.txt')).write_text(run.stdout+run.stderr)
 if run.returncode:save(folder/(tag+'-execution.json'),{'status':'compile_failed','compiler':run.stderr,'accepted':False});print(json.dumps({'role':args.role,'compiled':False}));return
 lib=c.CDLL(str(library));fn=lib.biwn_input_poll;fn.argtypes=[c.POINTER(poll.world.Bus)];fn.restype=c.c_int;snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();cases=poll.cases();rows=[];coverage=set()
 for i,case in enumerate(cases):
  a=poll.Script(snapshot,case);b=poll.Script(snapshot,case);poll.original(a,[0x12340000+j for j in range(15)],coverage);status=poll.translated(fn,b);passed=status==0 and a.trace==b.trace and a.memory==b.memory
  rows.append({'case':i,'passed':passed,'candidate_status':status,'original_held':int.from_bytes(a.memory[0x49ba4:0x49ba8],'big'),'C_held':int.from_bytes(b.memory[0x49ba4:0x49ba8],'big'),'original_edges':int.from_bytes(a.memory[0x49bac:0x49bb0],'big'),'C_edges':int.from_bytes(b.memory[0x49bac:0x49bb0],'big'),'trace_match':a.trace==b.trace})
 guards=[]
 # The coordinator inspection has confirmed a null/required-callback guard.
 guards.append({'case':'null_bus','status':fn(None),'expected':1})
 for missing in range(3):
  script=poll.Script(snapshot,cases[0]);status=poll.translated(fn,script,missing);guards.append({'case':'missing_callback_'+str(missing),'status':status,'expected':1,'no_effects':not script.trace})
 for row in range(4):
  for kind in['fail_read','fail_write']:
   script=poll.Script(snapshot,cases[0]);setattr(script,kind,(0xf14000,4 if kind=='fail_read'else 2,row));status=poll.translated(fn,script);guards.append({'case':kind+'_MMIO_'+str(row),'status':status,'expected':2,'trace':script.trace})
 for kind,address in[('fail_read',0x49ba4),('fail_write',0x49ba4),('fail_write',0x49bac)]:
  script=poll.Script(snapshot,cases[2]);setattr(script,kind,(address,4));status=poll.translated(fn,script);guards.append({'case':kind+'_'+hex(address),'status':status,'expected':2,'trace':script.trace})
 guard_pass=sum(x['status']==x['expected']and x.get('no_effects',True)for x in guards);passed=sum(x['passed']for x in rows)
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'candidate_checked_pending_coordinator_review','role':args.role,'directory':str(folder),'library':str(library),'cases':len(rows),'passed':passed,'failed':len(rows)-passed,'guards':guards,'guards_passed':guard_pass,'guards_total':len(guards),'all_rows_passed':passed==len(rows)and guard_pass==len(guards),'source_sha256':poll.world.select.binary_tools.sha(path),'format_cleanup':format_cleanup,'strict_warnings':not args.diagnostic_warnings,'results':rows,'accepted':False,'scope':'Inspected generated body, originalCPU exactRAM/bus oracle and addedhostguards; nativepad/task integration still separate. Same-weight author/reviewer are correlated, not independent verification. Diagnostic warning mode cannot qualify for acceptance.'}
 save(folder/(tag+'-execution.json'),report);print(json.dumps({'role':args.role,'strict_warnings':not args.diagnostic_warnings,'passed':passed,'cases':len(rows),'guards_passed':guard_pass,'guards_total':len(guards),'format_cleanup':format_cleanup}),flush=True)
if __name__=='__main__':main()
