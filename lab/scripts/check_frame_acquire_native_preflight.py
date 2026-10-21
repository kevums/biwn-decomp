"""OriginalUnicorn versus pinnedoriginalCPU,includingprivateguest scratch."""
import ctypes as c,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import check_local_frame_resource_acquire as a
ROOT=a.ROOT;SP=a.SP;STOP=a.STOP;SCRATCH=a.SCRATCH
snapshot,cases=a.fixtures();core_path=Path(json.loads((ROOT/'verification/DSP-music-context-experimental-candidate.json').read_text())['core_path']);oracle=a.media.scheduler.Native(diagnostic_core=core_path);runtime=a.media.Runtime.__new__(a.media.Runtime);runtime.oracle,runtime.device,runtime.core=oracle,oracle.device,oracle.lib;writers={}
for width in [2,4]:
 wr=getattr(runtime.core,'m68k_write_memory_'+str(width*8));wr.argtypes=[c.c_uint32,c.c_uint32];wr.restype=None;writers[width]=wr
rows=[];chosen=[x for x in cases if x['mode_word']==3 and x['count_word']in[1,2,3,36]and x['reserved_word']in[0,15]and x['adjusted_word']<32768 and not x.get('read_queues')]
try:
 for i,case in enumerate(chosen):
  left=a.Script(snapshot,case);expected=a.original(left,case,set());right=a.Script(snapshot,case);memory=bytearray(right.memory);memory[SP:SP+6]=STOP.to_bytes(4,'big')+case['id_word'].to_bytes(2,'big');memory[a.LOADER:a.LOADER+2]=b'\x4e\x75';cpu=a.media.CPU();cpu.registers[:15]=case['incoming'];cpu.registers[15]=SP;cpu.pc=0x1ac68;cpu.sr=0x2000;cpu.usp=0x180000;cpu.ssp=SP;runtime.device.seed(bytes(memory),0);runtime.seed_cpu(cpu);steps=0;calls=[]
  while runtime.cpu().pc!=STOP and steps<20000:
   state=runtime.cpu()
   if state.pc==a.LOADER:
    ram=runtime.device.ram();sp=state.registers[15];args=[int.from_bytes(ram[sp+4+n*4:sp+8+n*4],'big')for n in range(5)];calls.append(args);state.registers[0]=right.call(args,state.registers[0])
    for addr,width,v in right.changed:writers[width](addr,v)
    runtime.seed_cpu(state)
   runtime.core.m68k_execute(1);steps+=1
  state=runtime.cpu();ram=bytearray(runtime.device.ram());ram[a.LOADER:a.LOADER+2]=left.memory[a.LOADER:a.LOADER+2];wanted_calls=[e[2]for e in left.trace if e[0]=='call'];assert state.pc==STOP and state.registers[15]==SP+4 and state.registers[0]==expected and calls==wanted_calls,(i,state.pc,state.registers[0],expected)
  assert ram[:SP-0x1000]==left.memory[:SP-0x1000]and ram[SP+6:]==left.memory[SP+6:]and ram[SCRATCH:SCRATCH+4]==left.memory[SCRATCH:SCRATCH+4]
  rows.append(dict(mode_word=case['mode_word'],count_word=case['count_word'],reserved_word=case['reserved_word'],pattern=case['pattern'],adjusted_word=case['adjusted_word'],full_D0=expected,steps=steps,loader_calls=calls))
finally:oracle.close()
report=dict(status='frame_acquisition_original_Unicorn_native_selected_match',recorded_at=datetime.now(timezone.utc).isoformat(),cases=len(rows),rows=rows,core_path=str(core_path),core_sha256=hashlib.sha256(core_path.read_bytes()).hexdigest(),scope='Original173instruction acquisition: selectednonzeroDIVS descriptorcases fullD0/externalRAM/loaderargs/private4bytescratch agree acrossUnicorn andpinnedJaguarCPU. Loaderremainsfixture; no proposed C/zeroexception/hardware/gameplay claim.')
(ROOT/'verification/frame-resource-acquire-native-preflight-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(rows),'loadercalls',sum(len(x['loader_calls'])for x in rows))
