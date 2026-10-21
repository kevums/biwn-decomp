"""Compare emulated work for the SAME138014real input/CPU snapshots.
This is an isolated scalar-call benchmark, not wall time or hardware timing.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,subprocess,ctypes as c,os
import numpy as np
from replay_biwn_native_math_live import ROOT,sha,save,PAIR_DTYPE,CPU,Host,ORACLE
from check_biwn_scheduler import Native
class Result(c.Structure):_fields_=[('status',c.c_uint32),('index',c.c_uint32),('field',c.c_uint32),('steps',c.c_uint32),('completed',c.c_uint64),('original_instructions',c.c_uint64),('total_cycles',c.c_uint64),('got',CPU),('want',CPU)]
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--optimized-proof',type=Path);args=parser.parse_args()
 out=ROOT/'verification/native-math-live-cost'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 cap_path=ROOT/'verification/native-math-live-capture-current.json';cap=json.loads(cap_path.read_text());assert sha(cap['records'])==cap['records_sha256'];records=np.memmap(cap['records'],dtype=PAIR_DTYPE,mode='r')
 old_path=ROOT/'verification/native-bundle-math-current.json';old=json.loads(old_path.read_text());lanes=[('original',None),('current_bundle',old)]
 if args.optimized_proof:
  d=json.loads(args.optimized_proof.read_text());assert d['status']=='terminal_native_arithmetic_full_ABI_and_zero_exception_pass';lanes.append(('optimized_bundle',d))
 text=ORACLE.replace('uint64_t completed,original_instructions;','uint64_t completed,original_instructions,total_cycles;')
 text=text.replace('struct result*out){','struct result*out,uint64_t*costs){')
 text=text.replace('uint32_t i,j,pc,sp;', 'uint32_t i,j,pc,sp;uint64_t first_cycles;')
 text=text.replace('p=records+i;out->index=i;', 'p=records+i;out->index=i;first_cycles=out->total_cycles;')
 text=text.replace('if(pc<0xe540||pc>=0xe61c)', 'if(!((pc>=0xe540&&pc<0xe61c)||(pc>=0x15edc0&&pc<0x16edc0)))')
 text=text.replace('h->execute(1);out->original_instructions++;','int used=h->execute(1);if(used<=0){out->status=7;return 7;}out->total_cycles+=(uint32_t)used;out->original_instructions++;')
 text=text.replace('out->completed++;','costs[i]=out->total_cycles-first_cycles;out->completed++;')
 source=out/'work_benchmark.c';source.write_text(text);library=out/'libwork-benchmark.dylib';cmd=['clang','-dynamiclib','-std=c11','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(library)]
 p=subprocess.run(cmd,capture_output=True,text=True);(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 n=Native();n.device.lib.lab_device_observe(type(n.device.observer)());lib=n.lib;bridge=c.CDLL(str(library));bridge.original_replay.argtypes=[c.POINTER(Host),c.c_void_p,c.c_uint32,c.POINTER(Result),c.c_void_p];bridge.original_replay.restype=c.c_int
 original=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();rows=[]
 state=dict(status='benchmarking',pid=os.getpid(),directory=str(out),record_count=len(records),capture_proof=str(cap_path),capture_proof_sha256=sha(cap_path),whole_game_complete=False,physical_timing_verified=False)
 def checkpoint():save(out/'protocol.json',state);save(ROOT/'verification/native-math-live-cost-active.json',state)
 checkpoint();print(out,flush=True)
 try:
  for name,proof in lanes:
   image=bytearray(original)
   if proof:
    assert sha(proof['compiled_binary'])==proof['compiled_binary_sha256'];code=Path(proof['compiled_binary']).read_bytes();image[0x15edc0:0x15edc0+len(code)]=code
    for entry,symbol in [(0xe540,'biwn_native_multiply'),(0xe588,'biwn_native_division'),(0xe60a,'biwn_native_remainder')]:image[entry:entry+6]=b'\x4e\xf9'+int(proof['symbols'][symbol]).to_bytes(4,'big')
   n.device.seed(bytes(image),0);n.device.lib.lab_device_observe(type(n.device.observer)());host=Host(*[c.cast(getattr(lib,x),c.c_void_p)for x in ['m68k_pulse_reset','m68k_set_irq','m68k_set_reg','m68k_get_reg','m68k_execute']],n.device.pointer,c.cast(n.prefix,c.c_void_p));result=Result();costs=np.zeros(len(records),dtype=np.uint64)
   rc=bridge.original_replay(c.byref(host),c.c_void_p(records.ctypes.data),len(records),c.byref(result),c.c_void_p(costs.ctypes.data));assert rc==0,(name,rc,result.index,result.field)
   path=out/(name+'-cycles.u64le');path.write_bytes(costs.astype('<u8').tobytes());row=dict(lane=name,completed=result.completed,instructions=result.original_instructions,emulated_cycles=result.total_cycles,per_entry={hex(e):dict(calls=int(np.count_nonzero(records['entry']==e)),cycles=int(costs[records['entry']==e].sum()))for e in [0xe540,0xe588,0xe60a]},cycles_file=str(path),cycles_sha256=sha(path),full_return_state_matches=True)
   if proof:row.update(binary=proof['compiled_binary'],binary_sha256=proof['compiled_binary_sha256'])
   rows.append(row);print(json.dumps(row),flush=True)
  n.close();state.update(status='terminal_same_live_inputs_cost_benchmark',lanes=rows,source_sha256={str(p):sha(p)for p in [Path(__file__),source,library]},scope='All138014previously recorded real-call full return states match for each isolated lane. Emulated original-core retired cycle sums/instruction counts on identical inputs; no game/device/IRQ timeline, walltime, native console or all-input equivalence claim.')
  checkpoint();save(ROOT/'verification/native-math-live-cost-current.json',state)
 except BaseException as error:state.update(status='terminal_failed',error=repr(error));checkpoint();raise
if __name__=='__main__':main()
