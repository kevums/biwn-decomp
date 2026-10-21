"""Full native scheduler after source-loaded4000 handoff; no asset/movie ABI.

Captured firmware/ROM/CD/SSI/early GPUstack diagnostics still inputs.
Video callback is a passive frontend sink; no counters/PC/payload writes.
"""
import argparse,ctypes as c,json,struct,zlib
from pathlib import Path
from datetime import datetime,timezone
import observe_biwn_relocated_firmware as host
import biwn_firmware_checkpoint as checkpoint
ROOT=host.ROOT;save=host.save;sha=host.sha

def write_native_video_png(path,raw,width,height,pitch):
 def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
 lines=bytearray()
 for y in range(height):
  row=raw[y*pitch:y*pitch+width*4];rgb=bytearray(width*3);rgb[0::3]=row[2::4];rgb[1::3]=row[1::4];rgb[2::3]=row[0::4];lines.append(0);lines.extend(rgb)
 path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(lines))+chunk(b'IEND',b''))

parser=argparse.ArgumentParser();parser.add_argument('--frames',type=int,default=600);parser.add_argument('--input-test',action='store_true');options=parser.parse_args();assert 0<options.frames<=600
handoff=json.loads((ROOT/'verification/source-stage-handoff-current.json').read_text());input_path=Path(handoff['captured']['directory'])/'checkpoint.json';out=ROOT/'verification/BIWN-native-game-frames'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);runtime,record,loaded=checkpoint.restore_current(host,input_path);core=runtime.core;rows=[];pixels=[];index=[0];errors=[];last_capture={}
try:
 input_calls=[0]
 INPUT=c.CFUNCTYPE(c.c_int16,c.c_uint32,c.c_uint32,c.c_uint32,c.c_uint32)
 def input_state(port,device,slot,button):
  input_calls[0]+=1;held=4 if 360<=index[0]<420 else 6 if 420<=index[0]<450 else None
  if port!=0 or device!=1 or held is None:return 0
  return (1<<held)if button==256 else int(button==held)
 input_callback=INPUT(input_state)
 if options.input_test:core.retro_set_input_state.argtypes=[INPUT];core.retro_set_input_state(input_callback)
 assert runtime.cpu().pc==0x4000 and record['native_CD_scheduler_enabled'];core.GPUGetPC.restype=c.c_uint32;core.DSPGetPC.restype=c.c_uint32;core.retro_run.argtypes=[]
 VIDEO=c.CFUNCTYPE(None,c.c_void_p,c.c_uint32,c.c_uint32,c.c_size_t)
 def video(data,width,height,pitch):
  try:
   if not data:return
   assert 0<width<=2048 and 0<height<=2048 and width*4<=pitch<=8192
   if index[0]%60==0 or index[0]==options.frames:
    raw=c.string_at(data,pitch*height);write_native_video_png(out/('frame-'+str(index[0])+'.png'),raw,width,height,pitch);last_capture.update(frame=index[0],width=width,height=height,pitch=pitch,pixel_format='XRGB8888 little-endian BGRX',sha256=sha(raw));pixels.append(dict(last_capture))
  except BaseException as e:errors.append(repr(e))
 callback=VIDEO(video);core.retro_set_video_refresh.argtypes=[VIDEO];core.retro_set_video_refresh(callback)
 for number in range(1,options.frames+1):
  index[0]=number;core.retro_run();RAM=runtime.device.ram();cpu=runtime.cpu();row=dict(frame=number,CPU_PC=hex(cpu.pc),GPU_PC=hex(core.GPUGetPC()),DSP_PC=hex(core.DSPGetPC()),current_task=hex(int.from_bytes(RAM[0xc0920:0xc0924],'big')),source_clock=int.from_bytes(RAM[0x778cc:0x778d0],'big'),CD_progress=hex(int.from_bytes(RAM[0xbd848:0xbd84c],'big')),resource_state=RAM[0xbd85c:0xbd860].hex(),draw_busy=int.from_bytes(RAM[0x10a684:0x10a688],'big'),player_state={hex(a):int.from_bytes(RAM[a:a+w],'big')for a,w in [(0x49c50,4),(0x49c54,2),(0x49c56,4),(0x49c5a,2),(0x49c5c,2),(0x49c5e,2),(0x49c60,2),(0x49cc4,4)]},game_held=int.from_bytes(RAM[0x49ba4:0x49ba8],'big'),game_pressed=int.from_bytes(RAM[0x49bac:0x49bb0],'big'),input_test_held=('Up'if 360<=number<420 else'Left'if 420<=number<450 else'none')if options.input_test else'none',RAM_sha256=sha(RAM));rows.append(row)
  if number%60==0:save(out/'frames.json',rows);save(out/'video-captures.json',pixels);save(out/'status.json',dict(status='running',last=row));print(json.dumps(row),flush=True)
 assert not errors,errors;(out/'RAM-after.bin').write_bytes(runtime.device.ram());save(out/'frames.json',rows);save(out/'video-captures.json',pixels)
 report=dict(status='native_game_full_scheduler_frame_budget_observed',directory=str(out),input_checkpoint=str(input_path),restore=loaded,frames=len(rows),final=rows[-1],CPU=host.media.scheduler.cpu_dict(runtime.cpu()),hardware=runtime.snapshot()['hardware'],video=pixels,input_test=options.input_test,input_callback_calls=input_calls[0],no_host_PC_register_counter_RAM_write_after_restore=True,no_asset_movie_BIOS_ABI_adapter=True,no674byte_asset_phase_provider=True,no_nominal_movie_SSI_VBI_clock_provider=True,captured_diagnostic_inputs=record['additional_diagnostic_inputs'],execution_core_sha256=loaded['execution_core_sha256'],ordinary_fresh_boot_verified=False,physical_hardware_verified=False,whole_game_complete=False,scope='All original CPU/GPU/DSP/video/CD processors advance together in retro_run from captured source-loaded state. Passive frontend video sink. EarlyROM/CD/SSI/GPUstack diagnostic inputs and cross-process snapshot remain; frame budget is observation, not full-game/playability proof.');save(out/'report.json',report);save(ROOT/('verification/native-game-input-frames-current.json'if options.input_test else'verification/native-game-frames-current.json'),report);save(out/'status.json',dict(status='terminal_observed'));print(report['status'],flush=True)
except BaseException as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
finally:runtime.oracle.close()
