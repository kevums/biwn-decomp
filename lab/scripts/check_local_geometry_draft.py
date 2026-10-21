"""Compile an inspected local C block and compare it with original CPU fixtures."""
import argparse,ctypes as c,json,subprocess,os
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_geometry as geometry
ROOT=geometry.ROOT

def main():
 parser=argparse.ArgumentParser();parser.add_argument('directory');args=parser.parse_args();folder=Path(args.directory).resolve();assert folder.is_relative_to(ROOT/'runs');body=(folder/'candidate-body.txt').read_text().strip()
 assert body.startswith('{')and body.endswith('}') and '#'not in body and '```'not in body
 # Coordinator has inspected the small function body before invoking this
 # tool. Its interface only receives private callbacks and a result pointer.
 source='#include "biwn_geometry.h"\nstatic int less32(uint32_t a,uint32_t b){return(a^0x80000000u)<(b^0x80000000u);}\nenum biwn_geometry_status local_candidate(struct biwn_world_bus *bus,uint32_t object,uint32_t incoming_d0,uint32_t *out_d0)\n'+body+'\n'
 path=folder/'candidate.c';path.write_text(source);library=folder/'candidate.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(ROOT/'projects/black-ice-white-noise/restoration'),str(path),'-o',str(library)];run=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(folder/'compiler.txt').write_text(run.stdout+run.stderr)
 if run.returncode:raise RuntimeError('Candidate compile failed; retained compiler.txt')
 lib=c.CDLL(str(library));fn=lib.local_candidate;fn.argtypes=[c.POINTER(geometry.world.Bus),c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];fn.restype=c.c_int
 snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();cases=[case for case in geometry.cases(snapshot)if case['entry']==0x1028e];cases += [dict(cases[42],kind='changing_X',read_queues=[{'address':0x80004,'width':4,'values':[0,200]}]),dict(cases[42],kind='changing_Z',read_queues=[{'address':0x8000a,'width':4,'values':[0,200]}])]
 rows=[]
 for i,case in enumerate(cases):
  a=geometry.boundary.Script(snapshot,case);b=geometry.boundary.Script(snapshot,case);d0,_=geometry.original(a,case,set());status,actual=geometry.translated({0x1028e:fn},b,case)
  rows.append({'case':i,'parameters':case,'original_D0':d0,'candidate_D0':actual,'candidate_status':status,'bus_trace_match':a.trace==b.trace,'RAM_match':a.memory==b.memory,'passed':status==0 and actual==d0 and a.trace==b.trace and a.memory==b.memory,'original_trace':a.trace,'candidate_trace':b.trace})
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'candidate_checked_pending_coordinator_review','directory':str(folder),'cases':len(rows),'passed':sum(row['passed']for row in rows),'failed':sum(not row['passed']for row in rows),'results':rows,'source_sha256':geometry.world.select.binary_tools.sha(path),'scope':'Original CPU function without helper stubs versus inspected local-model C body; exact fullD0/bus order and private RAM. Not full-game or general coding accuracy.'}
 (folder/'execution-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'directory':str(folder),'passed':report['passed'],'cases':len(rows),'first_failure':next((row for row in rows if not row['passed']),None)}),flush=True)
if __name__=='__main__':main()
