"""Real 72-frame asset: original CPU/GPU versus C consumer/decoder output."""
import argparse,json,random,sys,hashlib
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import animation_renderer as renderer
import check_biwn_animation_images as images
world=images.world;SP=world.SP;STOP=world.STOP
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
def original(runtime,entry,incoming,object=None):
 ram=runtime.ram();cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_map(0xf02000,0x2000);cpu.mem_write(0,ram);args=b''if object is None else object.to_bytes(4,'big');cpu.mem_write(SP,STOP.to_bytes(4,'big')+args)
 for reg,value in zip(world.REGS,incoming):cpu.reg_write(reg,value)
 cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP);steps=[];callee_input=None
 def code(e,a,w,_):
  nonlocal callee_input
  assert 0xea20<=a<0xec04 or 0xe2b8<=a<0xe2f4 or 0xe098<=a<0xe0a6,hex(a);steps.append(a)
  if a in[0xe2b8,0xeac4]:
   stack=e.reg_read(UC_M68K_REG_A7);n=3 if a==0xe2b8 else 4;values=[int.from_bytes(e.mem_read(stack+4+i*4,4),'big')for i in range(n)];event=['call',a,values];runtime.calls.append(event);runtime.trace.append(event)
   if a==0xe2b8:callee_input=e.reg_read(UC_M68K_REG_D0)
  if a==0xeaaa:assert e.reg_read(UC_M68K_REG_D0)==callee_input
 def read(e,access,a,w,v,_):
  if SP-0x1000<=a<SP+8:return
  e.mem_write(a,runtime.read(a,w).to_bytes(w,'big'))
 def write(e,access,a,w,v,_):
  if SP-0x1000<=a<SP+8:return
  runtime.write(a,w,v&((1<<(8*w))-1))
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(entry,STOP,count=200000,timeout=30000000)
 assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
 for i,reg in enumerate(world.REGS):
  if entry==0xea20 or i not in[0,1,8,9]:assert cpu.reg_read(reg)==incoming[i]
 assert bytes(cpu.mem_read(SP+4,len(args)))==args
 return cpu.reg_read(UC_M68K_REG_D0),len(steps)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opts=ap.parse_args();manifest,snapshot=renderer.assets();out=ROOT/'verification/biwn-animation-frames'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);runtime=renderer.Runtime(tracing=True);rng=random.Random(0xea28);rows=[]
 producer_proof=json.loads((ROOT/'verification/biwn-animation-checks.json').read_text());runtime.enable_producer(Path(producer_proof['directory'])/'libanimation.dylib')
 try:
  for index in range(opts.limit or 72):
   for flip in[False,True]:
    save(out/'status.json',{'status':'running','frame_index':index,'flip':flip});ram,info=renderer.frame_ram(snapshot,index,flip);incoming=[rng.getrandbits(32)for _ in world.REGS]
    runtime.seed(ram,0);d0,steps=original(runtime,0xea28,incoming);oa=runtime.ram();ta=list(runtime.trace);sa=runtime.stats()
    runtime.seed(ram,1);result=runtime.consume(incoming[0]);ob=runtime.ram();tb=list(runtime.trace);sb=runtime.stats()
    if d0!=result or oa!=ob or ta!=tb:
     save(out/'mismatch.json',{'frame_index':index,'flip':flip,'original_D0':d0,'C_D0':result,'original_trace':ta,'C_trace':tb,'RAM_differences':[[i,oa[i],ob[i]]for i in range(len(oa))if oa[i]!=ob[i]][:100]});raise AssertionError(str(out/'mismatch.json'))
    output=info['output'];width,height=info['width'],info['height'];end=output+16+info['maximum_pixels']*2
    assert ob[end:end+8]==ram[end:end+8]and int.from_bytes(ob[0x112940:0x112942],'big')==0
    assert int.from_bytes(ob[output+8:output+12],'big')==((width<<16)|height|(0x80000000 if flip else 0))
    assert d0==width*4 and sa['original_GPU_sprite_decodes']==1 and sb['C_sprite_decodes']==1 and not sb['original_GPUExec1_calls']and not sb['original_GPU_sprite_decodes']and not sb['game_frames_executed']and not sb['device_error']
    raw=ob[output+16:output+16+width*height*2]
    row={'frame_index':index,'flip_header':flip,'dimensions':[width,height],'full_D0':d0,'header_hex':ob[output:output+16].hex(),'raw_sha256':renderer.sha(raw),'raw_bytes':len(raw),'original_CPU_instructions':steps,'original':sa,'rebuilt':sb,'whole_visible_RAM_exactly_matches':True,'CPU_trace_exactly_matches':True,'output_guard_unchanged':True};rows.append(row)
    if not flip:
     folder=out/'frames'/f'{index:02d}';folder.mkdir(parents=True);(folder/'frame.raw16be').write_bytes(raw);(folder/'frame.png').write_bytes(renderer.image_png(raw,width,height));save(folder/'frame.json',row)
  # Actual original animation records, with equal externally supplied delta.
  sequence=bytearray(snapshot)
  for a,w,v in[(0x49cb4,4,0x44544),(0x49d16,2,1),(0x49d18,2,1),(0x49cae,2,1),(0x4c24e,2,25),(0x112940,2,0)]:sequence[a:a+w]=v.to_bytes(w,'big')
  left=bytes(sequence);right=left;left_d0=right_d0=0;sequence_rows=[]
  for step in range(16):
   save(out/'status.json',{'status':'running_sequence','step':step});incoming=[rng.getrandbits(32)for _ in world.REGS];incoming[0]=left_d0
   runtime.seed(left,0);runtime.direct(0x4c24e,2,25);producer_d0,producer_steps=original(runtime,0xeb04,incoming,0x49c4c);produced=runtime.ram();incoming[0]=producer_d0;consumer_d0,consumer_steps=original(runtime,0xea28,incoming);left=runtime.ram();original_trace=list(runtime.trace);original_calls=list(runtime.calls);original_stats=runtime.stats();left_d0=consumer_d0
   runtime.seed(right,1);runtime.direct(0x4c24e,2,25);actual_producer=runtime.update(0x49c4c,right_d0);assert actual_producer==producer_d0 and runtime.ram()==produced
   actual_consumer=runtime.consume(actual_producer);right=runtime.ram();right_d0=actual_consumer
   assert actual_consumer==consumer_d0 and left==right and original_trace==runtime.trace and original_calls==runtime.calls,('sequence',step)
   stats=runtime.stats();assert not stats['original_GPUExec1_calls']and not stats['original_GPU_sprite_decodes']and not stats['game_frames_executed']and not stats['device_error']
   output=int.from_bytes(right[0x112d58:0x112d5c],'big');packed=int.from_bytes(right[output+8:output+12],'big');width=(packed>>16)&0x7fff;height=packed&0xffff;assert 0<width<=255 and 0<height<=255
   raw=right[output+16:output+16+width*height*2];folder=out/'sequence'/f'{step:02d}';folder.mkdir(parents=True);(folder/'frame.png').write_bytes(renderer.image_png(raw,width,height));(folder/'frame.raw16be').write_bytes(raw)
   sequence_rows.append({'step':step,'external_delta_word':25,'current_record':hex(int.from_bytes(right[0x49cb0:0x49cb4],'big')),'decoded_indices':[call[2][1]for call in runtime.calls if call[1]==0xe2b8],'calls':list(runtime.calls),'dimensions':[width,height],'raw_sha256':renderer.sha(raw),'producer_full_D0':producer_d0,'consumer_full_D0':consumer_d0,'original_CPU_instructions':producer_steps+consumer_steps,'original':original_stats,'rebuilt':stats,'original_C_producer_and_consumer_RAM_and_traces_match':True})
  save(out/'sequence.json',sequence_rows)
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
 finally:runtime.close()
 save(out/'fixtures.json',rows)
 if opts.limit:save(out/'status.json',{'status':'terminal_preflight','frame_cases':len(rows),'sequence_steps':len(sequence_rows)});print(json.dumps({'frame_cases':len(rows),'sequence_steps':16,'directory':str(out)}));return
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'real_animation_frames_consumer_CPU_GPU_and_C_match','directory':str(out),'frame_cases':len(rows),'distinct_frames':72,'flip_header_cases':72,'producer_consumer_sequence_steps':16,'queue_consumer_linked_to_sprite_decoder':True,'queue_consumer_linked_to_captured_task_ring':False,'raw_pixels_and_headers_match':True,'whole_visible_RAM_and_CPU_trace_match':True,'buffer_guard_checks':144,'original_resource':manifest['original_resource'],'asset_sha256':manifest['assets'],'consumer_source_sha256':json.loads((ROOT/'verification/biwn-animation-images-checks.json').read_text())['source_sha256'],'rebuilt_original_CPU_instructions':0,'rebuilt_original_GPU_instructions':0,'complete_game_frames_executed':0,'matched':['All72frozenresourceframes withbothflipheaderstates: originalEA28/E2B8CPU andGPU4B00 vsCconsumer/CPUprotocol/Cdecoder. WholevisibleRAM,exactCPUtraces,fullconsumerD0,headers/raw16bitpixels andoutputguards match.','Sixteen sequential originalanimation-record producer/consumer stages with equalexternaldelta25:realEB04/EAC4/EA28andGPUdecode vsCcounterparts;bothphaseRAM/fullD0/calls/traces match.'],'limits':['Host-invoked sequential stages, not the captured rendering task/main loop or concurrentCPU/GPU/DSPtiming. Coremailboxcompletion modeledsynchronously as in earlier pipeline.','No completeviewport/blitterplacement/flipdisplay interpretation, actorlifecycle,physicalhardware orfullgame frames. Preview color conversion usespinnedCRYtables;raw16bitcomparison isprimaryproof.','Frozenresource/frameassets,finiteoutputbuffer andexternallysupplieddeltas;notgeneralassetloading orallgameanimations.']}
 save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-animation-frames-checks.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
