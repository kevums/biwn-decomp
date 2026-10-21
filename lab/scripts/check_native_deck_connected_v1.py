"""Paired original/native-compiled Deck run with real helpers/GPU/scheduler.

Original allocator reserves payload and arena in the captured heap on both
lanes. Movable reservations are a finite test fixture: any compaction or
reservation loss is rejected. No disc or native-console deployment claim.
"""
import hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_native_deck_coordinate_v1 as component
ROOT=component.ROOT;V=ROOT/'verification'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def reserve(out):
 gate=read(V/'native-deck-coordinate-current.json');assert gate['completed']==576 and gate['task_slots_covered']==101
 for p,h in gate['source_sha256'].items():assert sha(p)==h,p
 engine=component.original.Engine();ram=(ROOT/'runs/zero-warm-whole-merchant-CPU-GPU-DSP/final-RAM.bin').read_bytes();rows=[]
 try:
  for size in [gate['code_bytes'],101*1024]:
   memory=bytearray(ram);sp=0x1f8000;stop=0x190000;memory[sp:sp+8]=stop.to_bytes(4,'big')+size.to_bytes(4,'big')
   cpu=component.CPU();cpu.registers[15]=sp;cpu.pc=0x152a2;cpu.usp=sp;cpu.ssp=0x1ff000;cpu.sr=0
   engine.native.device.seed(bytes(memory),0);engine.set_cpu(cpu,True);steps=[]
   for _ in range(20000):
    cpu=engine.cpu()
    if cpu.pc==stop:break
    assert cpu.pc!=0x15200,'Compaction is not valid for pinned executable reservations.'
    steps.append(cpu.pc);engine.core.m68k_execute(1)
   else:raise AssertionError('allocator instruction bound')
   ram=engine.native.device.ram();handle=cpu.registers[0];assert 0x112960<=handle<0x112d60
   pointer=int.from_bytes(ram[handle:handle+4],'big');assert pointer and pointer+size<=0x1c0000
   rows.append(dict(requested=size,handle=handle,pointer=pointer,instructions=len(steps)))
 finally:engine.native.close()
 code,arena=[row['pointer']for row in rows];build=out/'build'
 p=subprocess.run(['make','BUILD='+str(build),'ADDRESS='+hex(code),'ARENA_ADDRESS='+hex(arena)],cwd=component.SRC,capture_output=True,text=True);(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 payload=(build/'native-deck.bin').read_bytes();assert len(payload)==gate['code_bytes'];syms=component.symbols(build/'symbols.txt')
 memory=bytearray(ram);memory[code:code+len(payload)]=payload;memory[arena:arena+101*1024]=bytes([0xa5])*(101*1024)
 image=out/'reserved-RAM.bin';image.write_bytes(memory)
 proof=dict(status='terminal_original_allocator_reserved_native_fixture',reservations=rows,code=code,arena=arena,code_bytes=len(payload),arena_bytes=101*1024,symbols=syms,RAM=str(image),RAM_sha256=sha(image),payload=str(build/'native-deck.bin'),payload_sha256=sha(build/'native-deck.bin'),whole_game_complete=False)
 save(out/'reservation.json',proof);return proof
def main():
 out=V/'native-deck-connected'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);reservation=reserve(out)
 template=ROOT/'scripts/check_mode3_source_flow.py';text=template.read_text()
 anchor=next(line for line in text.splitlines()if line.lstrip().startswith("proof_name='mode3-recorded-world-loop-roundtrip'"));text=text.replace(anchor," proof_name='native-deck-connected-world-loop-v1'")
 # Both lanes execute real CPU/GPU instructions. The candidate lane differs
 # only by the compiled root redirect; the C library supplies device helpers.
 text=text.replace("if mode=='native':","if mode in ['native','C']:").replace("int(mode=='C')","0")
 text=text.replace("ram=bytearray((ROOT/'runs/zero-warm-whole-merchant-CPU-GPU-DSP/final-RAM.bin').read_bytes())","ram=bytearray(Path("+repr(reservation['RAM'])+").read_bytes())")
 text=text.replace("   disc=Disc();cpu=",'''   if mode=='C':
    runtime.device.direct(0x11d1a,2,0x4ef9);runtime.device.direct(0x11d1c,4,NATIVE_ENTRY)
   native_active=None
   def normalized(raw):
    data=bytearray(raw);data[ARENA:ARENA+ARENA_BYTES]=ram[ARENA:ARENA+ARENA_BYTES];data[0x11d1a:0x11d20]=ram[0x11d1a:0x11d20]
    if mode=='C'and native_active is not None:
     sp,ret=native_active
     if int.from_bytes(data[sp:sp+4],'big')==HELPER_RETURN:data[sp:sp+4]=ret.to_bytes(4,'big')
    return bytes(data)
   disc=Disc();cpu=''' )
 # Normalization is limited to the reserved private arena, root redirect and
 # active compiler return word. Original guest stack contents are compared.
 text=text.replace('sha(runtime.device.ram())','sha(normalized(runtime.device.ram()))')
 text=text.replace("final=runtime.device.ram();(out/","final=normalized(runtime.device.ram());(out/")
 text=text.replace('    nonlocal cpu','    nonlocal cpu,native_active')
 anchor='      trace.append(pc)'
 replacement='''      assert pc!=0x15200,'Pinned native-code reservation would be moved by compaction.'
      if mode=='C'and pc in [0xe26c,0xe540]:
       current=runtime.cpu();sp=current.registers[15]
       if runtime.device.read(sp,4)==HELPER_RETURN:
        frame=ARENA+16+runtime.device.read(0xc0920,4)-0xc0928
        assert runtime.device.read(frame+88,4)==sp
        native_active=(sp,runtime.device.read(frame+92,4))
      if mode=='C'and pc==ROOT_RETURN:native_active=None
'''+anchor
 assert text.count(anchor)>=1;text=text.replace(anchor,replacement,1)
 anchor="     mark('boundary_'+str(frame));frame+=1";assert anchor in text;text=text.replace(anchor,anchor+"\n     if frame==1:pads.set_buttons([0])")
 old="  assert results[1]['original_CPU_instructions']==results[1]['original_GPU_opcodes']==results[1]['statistics'][4]==results[1]['statistics'][8]==0"
 assert old in text;text=text.replace(old,"""  assert all(row['original_CPU_instructions']>0 and row['original_GPU_opcodes']>0 for row in results)
  candidate_pcs=results[1]['original_CPU_addresses'];assert NATIVE_ENTRY in candidate_pcs
  assert not any(0x11d20<=pc<0x11e64 for pc in candidate_pcs)
  for row in RESERVATIONS:assert int.from_bytes(runtime.device.ram()[row['handle']:row['handle']+4],'big')==row['pointer']
  raw=runtime.device.ram()
  for i in range(101):
   base=ARENA+i*1024
   assert raw[base:base+16]==bytes([0xa5])*16 and raw[base+1008:base+1024]==bytes([0xa5])*16
""")
 anchor="  report['heap_trampoline_used']=not options.inline_selector";assert anchor in text
 text=text.replace(anchor,"""  report['compiled_native_coordinate_calls']=results[1]['original_CPU_addresses'].count(NATIVE_ENTRY) # uniquePC presence only
  report['both_lanes_execute_native_CPU_GPU']=True
  report['candidate_original_coordinate_body_executed']=False
  report['native_payload_reservation_fixture']=RESERVATIONS
  report['native_arenas_guarded']=101
  report['native_return_word_normalization']='Onlyactivehelperreturnword,restoredbybridgeaftereachactualhelper;privatearena/rootredirectdeclared.'
  report['original_CPU_GPU_on_C_path']=True
"""+anchor)
 # The canonical file retains its own source-runtime wording. This wrapper
 # records the actual native-vs-native scope separately and authoritatively.
 prefix='NATIVE_ENTRY='+str(reservation['symbols']['biwn_native_deck_coordinate'])+'\nHELPER_RETURN='+str(reservation['symbols']['biwn_native_deck_helper_return'])+'\nROOT_RETURN='+str(reservation['symbols']['biwn_native_deck_coordinate_return'])+'\nARENA='+str(reservation['arena'])+'\nARENA_BYTES='+str(reservation['arena_bytes'])+'\nRESERVATIONS='+repr(reservation['reservations'])+'\n'
 runner=out/'pipeline-as-run.py';runner.write_text(prefix+text)
 state=dict(status='running',pid=os.getpid(),directory=str(out),reservation=reservation,runner=str(runner),runner_sha256=sha(runner),whole_game_complete=False,native_disc_changed=False,new_training=False)
 def mark():save(out/'protocol.json',state);save(V/'native-deck-connected-current.json',state)
 mark()
 try:
  with(out/'pipeline.log').open('w')as log:
   child=subprocess.Popen([str(ROOT/'.venv/bin/python3.12'),str(runner),'--frames','16','--inline-selector','--inventory-entry','--exit-viewer','--world-entry','--world-loop'],stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONPATH':str(ROOT/'scripts')},start_new_session=True);state['child_pid']=child.pid;mark();code=child.wait(timeout=600)
  state['child_pid']=None;assert code==0,(out/'pipeline.log').read_text()[-6000:]
  result=read(V/'native-deck-connected-world-loop-v1-current.json');state.update(status='terminal_native_coordinate_connected_real_helpers_match',proof_directory=result['directory'],paired_checkpoints=result['paired_checkpoints'],GPU_commands=[len(x['events'])for x in result['results']],scope=__doc__,source_sha256={str(p):sha(p)for p in [Path(__file__),template,runner]});mark();print(state['status'],flush=True)
 except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise
if __name__=='__main__':main()
