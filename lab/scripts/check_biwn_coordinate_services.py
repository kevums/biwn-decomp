"""Check exactly-once boundary obligations: external requests do no work."""
import ctypes as c
from datetime import datetime, timezone
import json
from pathlib import Path
import hashlib
import check_biwn_coordinate_flow as flow

ROOT=flow.ROOT
world=flow.original.boundary.world
W8=flow.original.W8
def save(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n')
def main():
 proof=json.loads((ROOT/'verification/coordinate-task-controls-flow-current.json').read_text())
 for path,digest in proof['sources_sha256'].items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest,path
 library=c.CDLL(proof['library']);service=library.biwn_coordinate_service_request
 service.argtypes=[c.POINTER(world.Bus),W8,c.POINTER(flow.Request),c.POINTER(c.c_uint32)];service.restype=c.c_int
 out=ROOT/'verification/coordinate-services'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 rows=[]
 def run(request,failure=False,missing=None):
  trace=[]
  def rd(width):
   def reader(context,address,result):
    assert context==0x12345678
    trace.append(['r',address,width]);result[0]=0x89abcdef&((1<<(8*width))-1)
    return int(failure)
   return reader
  def wr(width):
   def writer(context,address,value):
    assert context==0x12345678
    trace.append(['w',address,width,value]);return int(failure)
   return writer
  def external(*args):trace.append(['unexpected_call']);return 1
  callbacks=[world.R8(rd(1)),world.R16(rd(2)),world.R32(rd(4)),world.W16(wr(2)),world.W32(wr(4)),world.CALL(external),W8(wr(1))]
  if isinstance(missing,int):callbacks[missing]=type(callbacks[missing])()
  bus=world.Bus(*callbacks[:6],0x12345678,0);result=c.c_uint32(flow.SENTINEL)
  status=service(None if missing=='bus' else c.byref(bus),callbacks[6],None if missing=='request' else c.byref(request),None if missing=='out' else c.byref(result))
  return status,result.value,trace
 for target,count in [(0xdf60,0),(0x20f78,1),(0xdead,0)]:
  req=flow.Request(1,1,7,target,0,count,1,0x76543210)
  status,value,trace=run(req)
  assert status==1 and value==flow.SENTINEL and not trace
  rows.append(dict(case='external_helper',target=hex(target),request_not_executed=True,out_unchanged=True))
 for kind,width in [(1,1),(2,2),(3,4),(4,1),(5,2),(6,4)]:
  req=flow.Request(1,1,kind,0x80000,0x89abcdef,0,0,0)
  status,value,trace=run(req)
  assert status==0 and len(trace)==1
  assert value==(0x89abcdef&((1<<(width*8))-1) if kind<=3 else 0)
  for failure in [True]:
   status,value,trace=run(req,failure=failure)
   assert status==3 and value==flow.SENTINEL and len(trace)==1
  rows.append(dict(case='direct_bus_completion_and_failure',kind=kind,width=width,failure_out_unchanged=True,context_forwarded=True))
 req=flow.Request(1,1,3,0x80000,0,0,0,0)
 for missing in ['bus','request','out']+list(range(7)):
  status,value,trace=run(req,missing=missing)
  assert status==2 and value==flow.SENTINEL and not trace
  rows.append(dict(case='missing_argument',missing=missing,no_effects=True))
 invalid=[flow.Request(0,1,3,0x80000,0,0,0,0),flow.Request(1,0,3,0x80000,0,0,0,0),
          flow.Request(1,1,99,0,0,0,0,0),flow.Request(1,1,3,0,0,1,0,0)]
 for target,count in [(0x12620,0),(0x1b718,0),(0xe4c0,1),(0x20e8c,1),(0xdf22,1),(0xdf3e,1),(0xdf60,1),(0x20f78,0)]:
  invalid.append(flow.Request(1,1,7,target,0,count,1,0))
 for req in invalid:
  status,value,trace=run(req)
  assert status==2 and value==flow.SENTINEL and not trace
  rows.append(dict(case='malformed_request',kind=req.kind,target=hex(req.address),count=req.argument_count,no_effects=True))
 save(out/'cases.json',rows)
 report=dict(status='coordinate_services_external_and_bus_boundary_guards_pass',recorded_at=datetime.now(timezone.utc).isoformat(),
  directory=str(out),cases=len(rows),linked_controls_proof=str(ROOT/'verification/coordinate-task-controls-flow-current.json'),
  external_helper_requests_not_executed=True,missing_or_malformed_requests_have_no_effects=True,
  direct_bus_success_and_failure_and_context_checked=True,owned_helper_semantics_checked_by_linked_controls=True,
  physical_async_scheduling_verified=False,scope='Service boundary guards plus separate2086case owned-helper comparison. EXTERNAL status is pending work for the host, not successful completion. Host still owns request deduplication and genuine scheduler/scene execution.')
 save(out/'report.json',report);save(ROOT/'verification/coordinate-services-current.json',report)
 print(json.dumps(dict(status=report['status'],cases=len(rows))),flush=True)
if __name__=='__main__':main()
