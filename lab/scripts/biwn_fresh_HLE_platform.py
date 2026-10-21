"""Load the preserved CDI through libretro on an already constructed runtime."""
import ctypes as c
from pathlib import Path
from probe_biwn_fresh_CD_boot import Variable,Game

ROOT=Path(__file__).resolve().parents[1]


def load(runtime,out):
    core=runtime.core
    system=out/'fresh-empty-system';system.mkdir(exist_ok=True)
    saves=out/'fresh-private-saves';saves.mkdir(exist_ok=True)
    options={b'virtualjaguar_bios':b'enabled',b'virtualjaguar_usefastblitter':b'enabled',
             b'virtualjaguar_cd_boot_mode':b'hle',b'virtualjaguar_crash_detect':b'enabled'}
    paths={9:str(system).encode(),30:str(system).encode(),31:str(saves).encode()}
    errors=[]
    ENV=c.CFUNCTYPE(c.c_bool,c.c_uint,c.c_void_p)
    VIDEO=c.CFUNCTYPE(None,c.c_void_p,c.c_uint,c.c_uint,c.c_size_t)
    AUDIO=c.CFUNCTYPE(None,c.c_int16,c.c_int16)
    BATCH=c.CFUNCTYPE(c.c_size_t,c.c_void_p,c.c_size_t)
    POLL=c.CFUNCTYPE(None)
    INPUT=c.CFUNCTYPE(c.c_int16,c.c_uint,c.c_uint,c.c_uint,c.c_uint)
    def environment(cmd,data):
        try:
            cmd &= 255
            if cmd in paths:c.cast(data,c.POINTER(c.c_char_p))[0]=paths[cmd];return True
            if cmd in [10,16,67]:return True
            if cmd==15:
                var=c.cast(data,c.POINTER(Variable)).contents;var.value=options.get(var.key);return var.value is not None
            if cmd==17:c.cast(data,c.POINTER(c.c_bool))[0]=False;return True
            return False
        except BaseException as error:errors.append(repr(error));return False
    callbacks=[ENV(environment),VIDEO(lambda *_:None),AUDIO(lambda *_:None),
               BATCH(lambda _,frames:frames),POLL(lambda:None),INPUT(lambda *_:0)]
    core.retro_unload_game()
    for name,callback in zip(['environment','video_refresh','audio_sample','audio_sample_batch','input_poll','input_state'],callbacks):
        fn=getattr(core,'retro_set_'+name);fn.argtypes=[type(callback)];fn(callback)
    disc=ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi'
    core.retro_load_game.argtypes=[c.POINTER(Game)];core.retro_load_game.restype=c.c_bool
    assert core.retro_load_game(c.byref(Game(str(disc).encode(),None,0,None))), 'fresh HLE content load failed'
    assert not errors,errors
    runtime._fresh_HLE_callbacks=callbacks
    runtime.device.pointer=runtime.device.lib.lab_device_ram()
    runtime.rom=c.c_void_p.in_dll(core,'jaguarMainROM').value
    runtime.trace=__import__('hashlib').sha256();runtime.trace_count=0;runtime.bus_events=[]
    return {'fresh_libretro_content_load':True,'disc':str(disc),
            'platform_HLE':True,'saved_state_loaded':False,'manually_seeded_game_CPU':False,
            'options':{k.decode():v.decode() for k,v in options.items()}}
