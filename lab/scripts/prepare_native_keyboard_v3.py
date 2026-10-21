"""Derive a separate five-caller driver while preserving the tested v2 driver."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def main():
    source=ROOT/'scripts/run_biwn_native_keyboard_v2.py'
    text=source.read_text()
    def replace(old,new):
        nonlocal text
        assert text.count(old)==1,old
        text=text.replace(old,new)
    text=text.replace('including compiled scan/input/coordinate.', 'including compiled scan/input/face/coordinate/geometry.')
    text=text.replace('native-Deck-shared-reviewed-v2-current.json','native-Deck-shared-reviewed-v4-current.json')
    text=text.replace('terminal_fresh_three_native_Deck_callers_reviewed','terminal_fresh_five_native_Deck_callers_reviewed')
    text=text.replace('native-Deck-shared-v2-candidate-current.json','native-Deck-five-caller-geometry-v1-candidate-current.json')
    text=text.replace('native-keyboard-v2-','native-keyboard-v3-').replace('native-keyboard-v2-current.json','native-keyboard-v3-current.json')
    text=text.replace('native_preview_observer_v2.c','native_preview_observer_v3.c')
    text=text.replace('Three Caller Preview','Five Caller Preview')
    replace("ap.add_argument('--headless',action='store_true');", "ap.add_argument('--headless',action='store_true');ap.add_argument('--observer-off',action='store_true');")
    replace(' assert 1<=args.frames<=24000 and(not args.input_script or args.headless)',
            ' assert 1<=args.frames<=24000 and(not args.input_script or args.headless)and(not args.observer_off or args.headless)')
    replace(" parent=build;video_info=prior['video'];initial_video=(folder/'video-final.xrgb8888').read_bytes()",
            " parent=build;video_info=prior['video'];initial_video=(folder/'video-final.xrgb8888').read_bytes();assert hashlib.sha256(initial_video).hexdigest()==prior['checkpoint_video_sha256']")
    replace('def main():', "class FullCPU(c.Structure):\n _fields_=[('registers',c.c_uint32*16),('pc',c.c_uint32),('usp',c.c_uint32),('ssp',c.c_uint32),('sr',c.c_uint16)]\n\ndef main():")
    replace("native=(c.c_uint32*3)(*[syms['biwn_v2_'+name]for name in ['coordinate','input','scan']]);done=(c.c_uint32*3)(*[syms['biwn_v2_'+name+'_return']for name in ['coordinate','input','scan']])",
            "native=(c.c_uint32*5)(*[syms['biwn_v4_'+name]for name in ['coordinate','input','face','scan','geometry']]);done=(c.c_uint32*5)(*[syms['biwn_v4_'+name+'_return']for name in ['coordinate','input','face','scan','geometry']])")
    replace('core.BIWNSetCPUExecOwner(observer,0)', 'core.BIWNSetCPUExecOwner(OWNER()if args.observer_off else observer,0)')
    more="""  core.BIWNReadCPUState.argtypes=[c.POINTER(FullCPU)]
  def full_CPU():
   value=FullCPU();core.BIWNReadCPUState(c.byref(value));return dict(registers=list(value.registers),pc=value.pc,usp=value.usp,ssp=value.ssp,sr=value.sr)
  def processor_digest(name):
   fn=getattr(core,name+'StateSave');fn.argtypes=[c.c_void_p];fn.restype=c.c_size_t;buffer=c.create_string_buffer(65536);size=fn(buffer);assert 0<size<=65536;return hashlib.sha256(buffer.raw[:size]).hexdigest()
  def deck_counts(offset):return {name:monitor.preview_observer_stat(offset+i)for i,name in enumerate(['coordinate','input','face','scan','geometry'])}
"""
    replace('  if not args.headless:',more+'  if not args.headless:')
    lines=text.splitlines()
    old=next(x for x in lines if 'rows.append(dict(frame=frame,' in x)
    new="   rows.append(dict(frame=frame,CPU=core.m68k_get_reg(None,16),CPU_full=full_CPU(),GPU_sha256=processor_digest('GPU'),DSP_sha256=processor_digest('DSP'),RAM_sha256=hashlib.sha256(memory).hexdigest(),video_sha256=hashlib.sha256(video['raw']).hexdigest(),scene=get(0x49c64,2),mode=get(0x49c60,2),movie_flags=[get(0x47b80,2),get(0x47b82,2)],native_entries=deck_counts(5),native_returns=deck_counts(10),pressed_buttons=sorted(window.pressed if window else pressed)))"
    replace(old,new)
    replace('range(9,13)','range(15,21)')
    replace("save(out/'frames.json',rows);(out/'final-RAM.bin').write_bytes(memory);", "save(out/'frames.json',rows);(out/'final-video.xrgb8888').write_bytes(video['raw']);(out/'final-RAM.bin').write_bytes(memory);")
    old=next(x for x in text.splitlines()if "state.update(status='terminal_native_keyboard_frontend_stopped_pending_review'"in x)
    new="  state.update(status='terminal_native_keyboard_frontend_stopped_pending_review',frames=len(rows),elapsed_seconds=time.monotonic()-started,native_entries=deck_counts(5),native_returns=deck_counts(10),original_Deck_body_steps=deck_counts(15),invalid_task_identities=monitor.preview_observer_stat(20),GPU_entries=[monitor.preview_observer_stat(i)for i in range(21,29)],GPU_returns=[monitor.preview_observer_stat(i)for i in range(29,37)],all_GPU_Deck_guards_pass=True,immutable_native_code_unchanged=True,audio_callbacks=audio,keyboard_events=window.input_events if window else 0,observer_disabled=args.observer_off,checkpoint_metadata={k:prior[k]for k in ['requested_options','staged_cart_ROM_sha256','core_sha256','core']},final_video_info={k:video[k]for k in ['width','height','pitch']},source_sha256={str(p):sha(p)for p in [Path(__file__),source,proof_path,report_path,blob_path,ram_path,out/'frames.json',library]},scope=__doc__);mark();print({k:state[k]for k in ['status','frames','native_entries','native_returns']},flush=True)"
    replace(old,new)
    target=ROOT/'scripts/run_biwn_native_keyboard_v3.py'
    assert not target.exists()
    target.write_text(text)
    compile(text,str(target),'exec')
    print(target)


if __name__=='__main__':main()
