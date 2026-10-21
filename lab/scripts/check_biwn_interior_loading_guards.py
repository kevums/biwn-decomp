"""Host error contracts for new fixed CPU loader group; no source trap emulation."""
import ctypes as c,json
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_interior_loading_cpu as check
ROOT=check.ROOT;save=check.save;read=check.read;CPU=check.CPU;cd=check.cd
proof=read(ROOT/'verification/biwn-C-loaded-interior-pipeline-checks.json');library=c.CDLL(str(Path(proof['directory'])/'libC-loaded-interior.dylib'));fn=library.biwn_interior_loading_cpu_body;fn.argtypes=[c.POINTER(cd.world.Bus),c.POINTER(CPU),cd.dispatch.W8,cd.world_cpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];fn.restype=c.c_int
baseline=(ROOT/'verification/biwn-render-actors-runtime/20261013T190116.161377Z/startup-C-0.bin').read_bytes()
def run(**opts):
 memory=bytearray(baseline);SP=check.SP;memory[SP:SP+4]=check.STOP.to_bytes(4,'big');memory[SP+4:SP+6]=(2).to_bytes(2,'big');state=CPU();state.registers[:]=[0]*15+[SP];state.pc=opts.get('pc',0x1aa40);state.usp=SP;state.ssp=SP;state.sr=0x2000
 if 'dividend'in opts:state.registers[0]=opts['dividend'];state.registers[3]=opts['divisor']
 traces=[]
 def reader(width):
  def cb(_,a,v):
   if opts.get('fail')==('read',width):return 1
   if not 0<=a<=len(memory)-width:return 1
   v[0]=int.from_bytes(memory[a:a+width],'big');traces.append(['r',a,width,v[0]]);return 0
  return cb
 def writer(width):
  def cb(_,a,v):
   if opts.get('fail')==('write',width):return 1
   if not 0<=a<=len(memory)-width:return 1
   memory[a:a+width]=v.to_bytes(width,'big');traces.append(['w',a,width,v]);return 0
  return cb
 types=[cd.world.R8,cd.world.R16,cd.world.R32,cd.world.W16,cd.world.W32,cd.dispatch.W8];callbacks=[types[0](reader(1)),types[1](reader(2)),types[2](reader(4)),types[3](writer(2)),types[4](writer(4)),types[5](writer(1))]
 if 'missing'in opts:callbacks[opts['missing']]=types[opts['missing']]()
 def service(_,bus,cpu,target):
  traces.append(['helper',target])
  if opts.get('corrupt_return'):cpu.contents.registers[15]+=4;return 0
  return 1
 callback=cd.world_cpu.SERVICE()if opts.get('null_service')else cd.world_cpu.SERVICE(service);bus=cd.world.Bus(*callbacks[:5],cd.world.CALL(),None,0);before=bytes(state);status=fn(None if opts.get('null_bus')else c.byref(bus),None if opts.get('null_cpu')else c.byref(state),callbacks[5],callback,None,opts.get('budget',10000),opts.get('stop_on_yield',0))
 return dict(status=status,CPU_unchanged=bytes(state)==before,events=traces,prior_RAM_store_bytes=sum(e[2]for e in traces if e[0]=='w'))
rows=[]
for opts in [dict(missing=i)for i in range(6)]+[dict(null_bus=True),dict(null_cpu=True),dict(null_service=True),dict(budget=0),dict(stop_on_yield=2)]:
 result=run(**opts);assert result['status']==1 and result['CPU_unchanged']and not result['events'];rows.append(dict(options=opts,result=result))
for opts,status in [(dict(pc=0),7),(dict(budget=1),4)]+[(dict(fail=(kind,w)),2)for kind,w in [('read',2),('read',4),('write',2),('write',4)]]+[(dict(pc=0x20cf8),3),(dict(pc=0x20cf8,corrupt_return=True),5),(dict(pc=0x1ad0c,dividend=1,divisor=0),8),(dict(pc=0x1ad0c,dividend=0x80000000,divisor=0xffff),9)]:
 result=run(**opts);assert result['status']==status and result['CPU_unchanged'],(opts,status,result);rows.append(dict(options=opts,result=result))
report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='loader_host_argument_bus_budget_helper_return_and_DIVS_domain_guards_pass',guards=len(rows),rows=rows,original_CPU_or_GPU_executed=False,source_DIVS_zero_overflow_exception_emulated=False,scope='Hostbadargs/bus/budget/helper/private-return errors preserveinputCPU/priorRAMstores; zero/overflowDIVSreturn8/9,notoriginalexceptions. NormalactualCPUloadingbehaviorcoveredbyseparate6loading/24combinedpipelinecomparisons. No additionalnormalpath coverage claimed.')
save(ROOT/'verification/biwn-interior-loading-guard-checks.json',report);print(json.dumps({k:v for k,v in report.items()if k!='rows'}))
