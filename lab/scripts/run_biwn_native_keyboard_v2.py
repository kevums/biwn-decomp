"""Keyboard preview of the verified repaired native disc, restored outdoors.

The reference emulator executes the mixed original/compiled68000 image,
including compiled scan/input/coordinate. This restores an outdoor checkpoint;
it is not a fresh boot, full-game decompilation or physical-console proof.
No source-CPU/GPU replacement, RAM repair or input script in keyboard mode.
"""
import argparse,ctypes as c,hashlib,json,os,signal,struct,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
from probe_biwn_fresh_CD_boot import Game,Variable,write_video_PNG
from biwn_controller import JOYPAD_BUTTONS
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--headless',action='store_true');ap.add_argument('--check-only',action='store_true');ap.add_argument('--frames',type=int,default=24000);ap.add_argument('--input-script',type=Path);ap.add_argument('--capture-frame',type=int,action='append',default=[]);ap.add_argument('--play-audio',action='store_true');args=ap.parse_args()
 assert 1<=args.frames<=24000 and(not args.input_script or args.headless)
 assert len(args.capture_frame)<=8 and all(1<=x<=args.frames for x in args.capture_frame)
 proof_path=ROOT/'verification/native-Deck-shared-reviewed-v2-current.json';proof=read(proof_path);assert proof['status']=='terminal_fresh_three_native_Deck_callers_reviewed'
 build=read(proof['build']);run=read(ROOT/'verification/native-Deck-shared-v2-candidate-current.json');folder=Path(run['directory'])/'candidate';report_path=folder/'report.json';prior=read(report_path)
 core_path=Path(prior['core']);disc=Path(build['derived_disc']);blob_path=folder/'state-final.bin';ram_path=folder/'RAM-final.bin'
 for p,digest in [(proof['build'],proof['build_sha256']),(disc,proof['disc_sha256']),(core_path,prior['core_sha256']),(blob_path,prior['final_serialized_state_sha256']),(ram_path,prior['final_RAM_sha256'])]:assert sha(p)==digest,p
 parent=build;video_info=prior['video'];initial_video=(folder/'video-final.xrgb8888').read_bytes()
 windows=read(args.input_script)['windows']if args.input_script else []
 for w in windows:assert 1<=w['start_frame']<w['stop_frame']<=args.frames+1 and all(k in JOYPAD_BUTTONS for k in w['buttons'])
 out=ROOT/'runs'/('native-keyboard-v2-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir();print('Native BIWN preview — '+str(out),flush=True)
 state=dict(status='validated_not_launched'if args.check_only else'preparing',directory=str(out),pid=os.getpid(),disc=str(disc),disc_sha256=sha(disc),checkpoint=str(blob_path),checkpoint_sha256=sha(blob_path),headless=args.headless,keyboard_window_verified=False,restoration_changes_original_behavior=True,whole_game_complete=False,physical_console_verified=False,new_training=False)
 pointer=ROOT/'verification/native-keyboard-v2-current.json'
 def mark():save(out/'protocol.json',state);save(pointer,state)
 mark()
 if args.check_only:return
 system=out/'empty-system';system.mkdir();saves=out/'private-saves';saves.mkdir();paths={9:str(system).encode(),30:str(system).encode(),31:str(saves).encode()}
 options={k.encode():v.encode()for k,v in prior['requested_options'].items()};errors=[];video=dict(raw=initial_video,width=video_info['width'],height=video_info['height'],pitch=video_info['pitch']);audio=dict(frames=0,nonzero_samples=0);frame=0;pressed=set();rows=[];window=None;sink=None
 ENV=c.CFUNCTYPE(c.c_bool,c.c_uint,c.c_void_p);VIDEO=c.CFUNCTYPE(None,c.c_void_p,c.c_uint,c.c_uint,c.c_size_t);AUDIO=c.CFUNCTYPE(None,c.c_int16,c.c_int16);BATCH=c.CFUNCTYPE(c.c_size_t,c.c_void_p,c.c_size_t);POLL=c.CFUNCTYPE(None);INPUT=c.CFUNCTYPE(c.c_int16,c.c_uint,c.c_uint,c.c_uint,c.c_uint)
 def environment(cmd,data):
  try:
   cmd&=255
   if cmd in paths:c.cast(data,c.POINTER(c.c_char_p))[0]=paths[cmd];return True
   if cmd==10:return c.cast(data,c.POINTER(c.c_uint))[0]==1
   if cmd in [16,67]:return True
   if cmd==15:
    var=c.cast(data,c.POINTER(Variable)).contents;var.value=options.get(var.key);return var.value is not None
   if cmd==17:c.cast(data,c.POINTER(c.c_bool))[0]=False;return True
   return False
  except BaseException as error:errors.append(repr(error));return False
 def refresh(data,width,height,pitch):
  if data and data!=c.c_void_p(-1).value and width and height:
   if pitch<width*4:errors.append('Unexpected pixel format');return
   video.update(raw=c.string_at(data,pitch*height),width=width,height=height,pitch=pitch)
 def sample(left,right):
  audio['frames']+=1;audio['nonzero_samples']+=int(left!=0)+int(right!=0)
  if sink:sink.submit(struct.pack('<hh',left,right))
 def batch(data,count):
  audio['frames']+=count
  if data:
   raw=c.string_at(data,count*4);audio['nonzero_samples']+=sum(raw[i:i+2]!=b'\0\0'for i in range(0,len(raw),2))
   if sink:sink.submit(raw)
  return count
 def input_state(port,device,index,button):
  if port or index:return 0
  if device==1:return int(button in (window.pressed if window else pressed))
  if device==3 and window:return int(button in window.keyboard_pressed)
  return 0
 callbacks=[ENV(environment),VIDEO(refresh),AUDIO(sample),BATCH(batch),POLL(lambda:None),INPUT(input_state)]
 core=c.CDLL(str(core_path))
 for name,callback in zip(['environment','video_refresh','audio_sample','audio_sample_batch','input_poll','input_state'],callbacks):getattr(core,'retro_set_'+name)(callback)
 core.retro_init();core.retro_set_controller_port_device(0,1)
 core.retro_load_game.argtypes=[c.POINTER(Game)];core.retro_load_game.restype=c.c_bool;core.retro_unserialize.argtypes=[c.c_void_p,c.c_size_t];core.retro_unserialize.restype=c.c_bool;core.retro_serialize_size.restype=c.c_size_t;core.retro_serialize.argtypes=[c.c_void_p,c.c_size_t];core.retro_serialize.restype=c.c_bool;core.retro_get_memory_data.argtypes=[c.c_uint];core.retro_get_memory_data.restype=c.c_void_p
 monitor=None
 try:
  assert core.retro_load_game(c.byref(Game(str(disc).encode(),None,0,None)))
  rom=c.c_void_p.in_dll(core,'jaguarMainROM').value;assert hashlib.sha256(c.string_at(rom,0x40000)).hexdigest()==prior['staged_cart_ROM_sha256'],'Mounted ROM provider differs from tested run'
  blob=blob_path.read_bytes();assert core.retro_unserialize(c.create_string_buffer(blob),len(blob));roundtrip=c.create_string_buffer(core.retro_serialize_size());assert core.retro_serialize(roundtrip,len(roundtrip))and roundtrip.raw==blob
  ram=core.retro_get_memory_data(2);assert ram and c.string_at(ram,0x200000)==ram_path.read_bytes()
  source=ROOT/'scripts/native_preview_observer_v2.c';library=out/'libnative-preview-observer.dylib';compiled=subprocess.run(['clang','-dynamiclib','-O2','-std=c99','-Wall','-Wextra','-Werror',str(source),'-o',str(library)],capture_output=True,text=True);assert compiled.returncode==0,compiled.stderr
  monitor=c.CDLL(str(library));monitor.preview_observer_setup.argtypes=[c.c_void_p,c.POINTER(c.c_uint32),c.POINTER(c.c_uint32),c.POINTER(c.c_uint32),c.POINTER(c.c_uint32)];monitor.preview_observer_stat.argtypes=[c.c_uint];monitor.preview_observer_stat.restype=c.c_uint64
  keys=list(parent['mailbox_roots']);g=(c.c_uint32*8)(*[parent['mailbox_roots'][k]['native_entry']for k in keys]);gr=(c.c_uint32*8)(*[parent['mailbox_symbols'][parent['mailbox_roots'][k]['symbol']+'_return']for k in keys]);syms=parent['shared_Deck_symbols'];native=(c.c_uint32*3)(*[syms['biwn_v2_'+name]for name in ['coordinate','input','scan']]);done=(c.c_uint32*3)(*[syms['biwn_v2_'+name+'_return']for name in ['coordinate','input','scan']]);monitor.preview_observer_setup(ram,native,done,g,gr)
  OWNER=c.CFUNCTYPE(c.c_int32,c.c_uint32);core.BIWNSetCPUExecOwner.argtypes=[OWNER,c.c_int];observer=OWNER(('preview_observer_own',monitor));core.BIWNSetCPUExecOwner(observer,0)
  core.m68k_get_reg.argtypes=[c.c_void_p,c.c_int];core.m68k_get_reg.restype=c.c_uint32
  if not args.headless:
   from biwn_live_window import LiveWindow,KEYS
   class NativeWindow(LiveWindow):
    # A single frontend shortcut sends the same ordinary B+C pad chord.
    # Keep the original manual X+C binding and all source-preview keys.
    def key_down(self,event):
     super().key_down(event)
     if 'd'in self.keys_down:self.pressed.update([0,1])
    def key_up(self,event):
     super().key_up(event)
     if 'd'in self.keys_down:self.pressed.update([0,1])
     elif event.keysym.lower()=='d':
      for button in [0,1]:
       if not any(KEYS.get(k)==button for k in self.keys_down):self.pressed.discard(button)
   window=NativeWindow();window.root.title('BIWN — Three Caller Preview (Experimental)')
   for widget in window.root.winfo_children():
    if isinstance(widget,window.tk.Label):
     text=widget.cget('text')
     if '1 then tap X+C'in text:widget.configure(text=text.replace('1 then tap X+C','1 then D').replace('2 then tap X+C','2 then D')+'\nD sends B+C; manual X+C also works.')
   signal.signal(signal.SIGINT,lambda *_:window.close());signal.signal(signal.SIGTERM,lambda *_:window.close())
  if args.play_audio:
   try:
    from biwn_audio_output import AudioOutput,core_audio_rate
    sink=AudioOutput(core_audio_rate(core));sink.set_state(suspended=False)
    if window:window.audio_output=sink;window.audio_message='Audio on'
   except Exception as error:
    state['audio_output_error']=repr(error)
    if window:window.audio_message='Audio unavailable'
  state.update(status='running',exact_machine_and_RAM_restored=True,CPU_GPU_mode='Retained original emulator executing mixed original/compiled68000 game image',new_CPU_or_GPU_seeds=False,host_guest_RAM_repairs=False);mark();started=time.monotonic()
  for frame in range(1,args.frames+1):
   if window:
    if not window.poll(video,frame-1):break
    if sink:sink.set_state(suspended=window.paused)
    while window.paused and not window.closed:
     time.sleep(.02);window.poll({},frame-1)
    if window.closed:break
    if sink:sink.set_state(suspended=False)
   else:pressed={JOYPAD_BUTTONS[k]for w in windows if w['start_frame']<=frame<w['stop_frame']for k in w['buttons']}
   core.retro_run();assert not errors,errors
   memory=c.string_at(ram,0x200000);get=lambda a,w=4:int.from_bytes(memory[a:a+w],'big')
   rows.append(dict(frame=frame,CPU=core.m68k_get_reg(None,16),RAM_sha256=hashlib.sha256(memory).hexdigest(),video_sha256=hashlib.sha256(video['raw']).hexdigest(),scene=get(0x49c64,2),mode=get(0x49c60,2),movie_flags=[get(0x47b80,2),get(0x47b82,2)],native_coordinate_entries=monitor.preview_observer_stat(3),native_coordinate_returns=monitor.preview_observer_stat(6),native_input_entries=monitor.preview_observer_stat(4),native_input_returns=monitor.preview_observer_stat(7),native_scan_entries=monitor.preview_observer_stat(5),native_scan_returns=monitor.preview_observer_stat(8),original_face_entries=monitor.preview_observer_stat(29),original_face_returns=monitor.preview_observer_stat(30),pressed_buttons=sorted(window.pressed if window else pressed)))
   if frame in args.capture_frame:write_video_PNG(out/('frame-'+str(frame)+'.png'),video['raw'],video['width'],video['height'],video['pitch'])
   if frame%60==0:state['frames']=len(rows);save(out/'frames.json',rows);mark()
  core.BIWNSetCPUExecOwner(OWNER(),0)
  memory=c.string_at(ram,0x200000);component=Path(parent['component']).read_bytes();base=parent['resident_address']
  for lo,hi in [(base,parent['arena_address']),(parent['arena_end'],parent['deck_arena_address'])]:assert memory[lo:hi]==component[lo-base:hi-base]
  for a,n,stride in [(parent['arena_address'],102,256),(parent['deck_arena_address'],101,1024)]:
   for i in range(n):
    lo=a+i*stride;assert memory[lo:lo+16]==component[lo-base:lo-base+16]and memory[lo+stride-16:lo+stride]==component[lo-base+stride-16:lo-base+stride]
  for i in range(101):
   at=parent['deck_arena_address']+i*1024
   for lo,hi in parent['deck_fences']:assert memory[at+lo:at+hi]==component[at-base+lo:at-base+hi]
  assert all(monitor.preview_observer_stat(i)==0 for i in range(9,13))
  save(out/'frames.json',rows);(out/'final-RAM.bin').write_bytes(memory);assert core.retro_serialize(roundtrip,len(roundtrip));(out/'final-state.bin').write_bytes(roundtrip.raw);write_video_PNG(out/'final.png',video['raw'],video['width'],video['height'],video['pitch'])
  state.update(status='terminal_native_keyboard_frontend_stopped_pending_review',frames=len(rows),elapsed_seconds=time.monotonic()-started,native_coordinate_entries=monitor.preview_observer_stat(3),native_coordinate_returns=monitor.preview_observer_stat(6),native_input_entries=monitor.preview_observer_stat(4),native_input_returns=monitor.preview_observer_stat(7),native_scan_entries=monitor.preview_observer_stat(5),native_scan_returns=monitor.preview_observer_stat(8),original_face_entries=monitor.preview_observer_stat(29),original_face_returns=monitor.preview_observer_stat(30),original_Deck_body_steps=[monitor.preview_observer_stat(i)for i in range(9,12)],invalid_task_identities=monitor.preview_observer_stat(12),GPU_entries=[monitor.preview_observer_stat(i)for i in range(13,21)],GPU_returns=[monitor.preview_observer_stat(i)for i in range(21,29)],all_GPU_Deck_guards_pass=True,immutable_native_code_unchanged=True,audio_callbacks=audio,keyboard_events=window.input_events if window else 0,source_sha256={str(p):sha(p)for p in [Path(__file__),source,proof_path,report_path,blob_path,ram_path,out/'frames.json',library]},scope=__doc__);mark();print({k:state[k]for k in ['status','frames','native_coordinate_entries','native_coordinate_returns']},flush=True)
 except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise
 finally:
  if sink:sink.close()
  if window and not window.closed:window.close()
  core.retro_unload_game();core.retro_deinit()
if __name__=='__main__':main()
