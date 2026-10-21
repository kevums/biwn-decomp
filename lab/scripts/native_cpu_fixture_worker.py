"""Pinned original M68000, private synthetic register-only program, child process."""
import json,sys,time,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from check_biwn_scheduler import Native

def run(request,native=None):
 raw=bytes.fromhex(request['raw']);starts={int(x['address']):x for x in request['decoded']};base,stack,stop=0x4000,0x10800,0x20000;own=native is None;n=native or Native();core=n.lib
 try:
  ram=bytearray(0x200000);ram[0:4]=stack.to_bytes(4,'big');ram[4:8]=base.to_bytes(4,'big');ram[base:base+len(raw)]=raw;ram[stack:stack+4]=stop.to_bytes(4,'big');n.device.seed(bytes(ram),0);core.m68k_pulse_reset();core.m68k_set_irq(0);core.m68k_set_reg(17,0x2700|request['initial_ccr']);core.m68k_set_reg(15,stack)
  for i in range(8):core.m68k_set_reg(i,request['initial'].get(f'D{i}',0))
  core.m68k_set_reg(16,base);trace=[];failure=None;started=time.monotonic()
  for _ in range(256):
   pc=core.m68k_get_reg(None,16)
   if pc==stop:break
   if pc not in starts:failure='Execution left decoded fixture boundaries';break
   if time.monotonic()-started>0.05:failure='Fixture CPU execution exceeded50ms';break
   trace.append(pc);core.m68k_execute(1)
  pc=core.m68k_get_reg(None,16);sp=core.m68k_get_reg(None,15);completed=not failure and pc==stop and sp==stack+4 and trace and starts[trace[-1]]['assembly']=='rts'
  if not completed and not failure:failure='Fixture did not complete by RTS within256instructions/50ms'
  result=dict(status='bounded_fixture_completed'if completed else'fixture_rejected_or_incomplete',CPU_model='Pinned Virtual Jaguar original emulated M68000',bytes_sha256=hashlib.sha256(raw).hexdigest(),bytes_hex=raw.hex(),decoder=request['decoder'],initial_registers={f'D{i}':f'0x{request["initial"].get(f"D{i}",0):08x}'for i in range(8)},initial_CCR=request['initial_ccr'],instructions_executed=len(trace),trace_addresses=list(map(hex,trace)),executed_instructions=[{k:starts[address][k]for k in ['address','size','bytes','assembly']}for address in dict.fromkeys(trace)],final_PC=hex(pc),stack_return_checked=bool(completed),final_registers_available=bool(completed),condition_codes_available=bool(completed),scope='Supplied private register-arithmetic/branch fixture. Original emulated CPU effects, not physical hardware, full game, recovered purpose or C-code validation.')
  if completed:
   values={f'D{i}':core.m68k_get_reg(None,i)for i in range(8)};sr=core.m68k_get_reg(None,17);result.update(final_registers={k:f'0x{v:08x}'for k,v in values.items()},signed_final_registers={k:v if v<0x80000000 else v-0x100000000 for k,v in values.items()},final_SR=f'0x{sr:04x}',final_CCR=sr&31,condition_codes={name:int(bool(sr&mask))for name,mask in [('X',16),('N',8),('Z',4),('V',2),('C',1)]})
  if failure:result['error']=failure
  return result
 finally:
  if own:n.close()

if __name__=='__main__':
 request=json.load(sys.stdin);print(json.dumps(run(request)),flush=True)
