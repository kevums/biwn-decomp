"""Original GPU/CD steps from restored source firmware state; CPU/DSP held."""
import ctypes as c,json,struct,re
from collections import Counter

def run(host,runtime,out,args,clock,CD_remainder):
 core=runtime.core;core.GPUGetPC.restype=c.c_uint32;core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];core.GPUReadLong.restype=c.c_uint32;core.GPUExec.argtypes=[c.c_int32]
 counter=c.c_uint32.in_dll(core,'gpu_exec_opcode_count');start=counter.value;source=(host.ROOT/'tools/virtualjaguar-runtime-source/src/tom/gpu.c').read_text();table=source.split('static const uint8_t gpu_opcode_cycles[64] =',1)[1].split('}',1)[0].split('{',1)[1];table=re.sub(r'/\*.*?\*/','',table,flags=re.S);costs=[int(v)for v in re.findall(r'\b\d+\b',table)];assert len(costs)==64;CPU=bytes(runtime.cpu());buffer=c.create_string_buffer(12000);assert runtime.savers['GPU'](buffer)==4416;(out/'GPU-before.bin').write_bytes(buffer.raw[:4416]);trace=host.hashlib.sha256();rows=Counter();blocks=delays=ticks=cycles=0;rem=CD_remainder*2;stop='budget';samples=[]
 for i in range(args.GPU_budget):
  control=core.GPUReadLong(0xf02114,0)
  if not control&1:stop='source_GPU_GO_cleared';break
  pc=core.GPUGetPC()
  if not 0xf03000<=pc<0xf04000:stop='GPU_PC_outside_local_RAM';break
  raw=c.string_at(core.GPUGetRAM()+pc-0xf03000,6);op=int.from_bytes(raw[:2],'big')>>10;code=raw[:6 if op==38 else 2];following=c.string_at(core.GPUGetRAM()+pc-0xf03000+2,6);rows[(pc,code)]+=1;trace.update(struct.pack('>I',pc)+code);before=counter.value;core.GPUExec(1);consumed=(counter.value-before)&0xffffffff;blocks+=1
  if consumed>1 and op in [52,53]:
   code=following[:6 if int.from_bytes(following[:2],'big')>>10==38 else 2];rows[(pc+2,code)]+=1;trace.update(struct.pack('>I',pc+2)+code);delays+=1
  elapsed=int(costs[op]);cycles+=elapsed;rem+=elapsed
  while rem>=clock['CPU_cycles_per_BUTCH_tick']*2:core.BUTCHExec(0);ticks+=1;rem-=clock['CPU_cycles_per_BUTCH_tick']*2
  if i and i%100000==0:
   sample=dict(blocks=i,PC=hex(core.GPUGetPC()),BUTCH_ticks=ticks,control=hex(core.GPUReadLong(0xf02114,0)));samples.append(sample);print(json.dumps(sample),flush=True)
 assert bytes(runtime.cpu())==CPU;assert runtime.savers['GPU'](buffer)==4416;after=buffer.raw[:4416];(out/'GPU-after.bin').write_bytes(after);(out/'RAM-after-GPU.bin').write_bytes(runtime.device.ram())
 report=dict(status='original_GPU_CD_source_stage_observation',stop_reason=stop,execution_blocks=blocks,original_GPU_instructions=(counter.value-start)&0xffffffff,detected_branch_delays=delays,final_GPU_PC=hex(core.GPUGetPC()),final_control=hex(core.GPUReadLong(0xf02114,0)),BUTCH_ticks=ticks,pinned_outer_opcode_cycles=cycles,CPU_held_unchanged=True,PC_bytes_trace_sha256=trace.hexdigest(),logical_GPU_sha256=host.sha(after[:4396]),visited_instructions=[{**host.generation.loader.base.binary_tools.jaguar_instructions(code,pc,'gpu')[0][0],'count':count}for(pc,code),count in sorted(rows.items())],samples=samples,source_C_GPU_used=False,host_GPU_PC_or_mailbox_write=False,scope='Restored source state, original GPUExec1 with actual CD device and BUTCH ticks from outer GPU opcode costs. Nested branch delays uncharged per pinned core. CPU/DSP/JERRY SSI/video/PIT held; physical/global schedule unverified.')
 host.save(out/'GPU-report.json',report);return report,rem/2
