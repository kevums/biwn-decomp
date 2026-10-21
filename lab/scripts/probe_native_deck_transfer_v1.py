"""Inspect/continue the exact stalled machine using retained frame execution."""
import argparse,ctypes as c,json,os,struct
from datetime import datetime,timezone
from pathlib import Path
import check_native_deck_fresh_restore_v1 as common
import check_biwn_world_movement_pipeline as hardware
ROOT=common.ROOT;V=ROOT/'verification';read=common.read;save=common.save;sha=common.sha

def decode(blob):
    assert blob[:4]==b'HLE1';offset=4
    result={'pending':blob[offset]};offset+=1
    for name in ['read_dest','read_end','read_progress','gpu_base','post_lba','align_track','align_phase']:
        result[name]=struct.unpack_from('<I',blob,offset)[0];offset+=4
    result.update(active=blob[offset],bufValid=blob[offset+1]);offset+=2
    for name in ['lba','bufOff','dest','total','reqTotal','written','accFrac','d1','statusBase','sigD0','sigD1','sigA0','sigA1','speedMult','startDelay']:
        result[name]=struct.unpack_from('<I',blob,offset)[0];offset+=4
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--frames',type=int,default=120);args=ap.parse_args();assert 0<=args.frames<=600
    out=V/'native-Deck-transfer-probe'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    witness=read(V/'native-Deck-ordinary-input-reviewed-current.json');folder=Path(witness['candidate']['directory']);report=read(folder/'report.json');core_path=Path(report['core']);disc=Path(report['disc'])
    assert sha(core_path)==report['core_sha256']and sha(disc)==report['disc_sha256']
    build=read(V/'mode3-world-render-device-build-current.json');device=hardware.Device(Path(build['library']),core=core_path);core=c.CDLL(str(core_path))
    state=dict(status='restoring',directory=str(out),pid=os.getpid(),new_training=False,whole_game_complete=False,native_disc_changed=False)
    def mark():save(out/'protocol.json',state);save(V/'native-Deck-transfer-probe-current.json',state)
    mark()
    try:
        class Game(c.Structure):_fields_=[('path',c.c_char_p),('data',c.c_void_p),('size',c.c_size_t),('meta',c.c_char_p)]
        core.retro_load_game.argtypes=[c.POINTER(Game)];core.retro_load_game.restype=c.c_bool;assert core.retro_load_game(c.byref(Game(str(disc).encode(),None,0,None)))
        blob=(folder/'state-final.bin').read_bytes();assert sha(folder/'state-final.bin')==report['final_serialized_state_sha256']
        core.retro_unserialize.argtypes=[c.c_void_p,c.c_size_t];core.retro_unserialize.restype=c.c_bool;assert core.retro_unserialize(c.create_string_buffer(blob),len(blob))
        core.retro_serialize_size.restype=c.c_size_t;core.retro_serialize.argtypes=[c.c_void_p,c.c_size_t];core.retro_serialize.restype=c.c_bool;copy=c.create_string_buffer(core.retro_serialize_size());assert core.retro_serialize(copy,len(copy))and copy.raw==blob
        device.pointer=device.lib.lab_device_ram();assert device.ram()==(folder/'RAM-final.bin').read_bytes()
        core.JaguarCDHLEStateSize.restype=c.c_size_t;core.JaguarCDHLEStateSave.argtypes=[c.c_void_p];core.JaguarCDHLEStateSave.restype=c.c_size_t
        core.JaguarCDHLEStreamArmCount.restype=c.c_uint32
        core.m68k_get_reg.argtypes=[c.c_void_p,c.c_int];core.m68k_get_reg.restype=c.c_uint32
        def sample(frame):
            buf=c.create_string_buffer(core.JaguarCDHLEStateSize());assert core.JaguarCDHLEStateSave(buf)==len(buf)
            ram=device.ram();return dict(frame=frame,HLE=decode(buf.raw),arm_count=core.JaguarCDHLEStreamArmCount(),progress=int.from_bytes(ram[0xbd848:0xbd84c],'big'),CPU=core.m68k_get_reg(None,16),task=int.from_bytes(ram[0xc0920:0xc0924],'big'),RAM_sha256=__import__('hashlib').sha256(ram).hexdigest())
        rows=[sample(0)];save(out/'initial-HLE.json',rows[0]);print('initial',rows[0],flush=True);state['status']='running_retained_frame_continuation';mark()
        for frame in range(1,args.frames+1):
            core.retro_run();rows.append(sample(frame))
            if frame%30==0:state['frames']=frame;save(out/'samples.json',rows);mark();print('frame',frame,'arms',rows[-1]['arm_count'],'written',hex(rows[-1]['HLE']['written']),flush=True)
        save(out/'samples.json',rows);(out/'final-RAM.bin').write_bytes(device.ram());assert core.retro_serialize(copy,len(copy));(out/'final-state.bin').write_bytes(copy.raw)
        state.update(status='terminal_retained_transfer_continuation_observed',frames=args.frames,initial=rows[0],final=rows[-1],source_sha256={str(p):sha(p)for p in [Path(__file__),folder/'report.json',folder/'state-final.bin',folder/'RAM-final.bin',core_path,out/'samples.json']},scope='Exact restored native ordinary-input final machine and retained emulator frame execution with harness no-input callbacks. No CPU/RAM/task/GPU seed, extra code repair or fabricated disc completion. Checkpoint continuation, not fresh boot or native-versus-original loader proof.');mark();print(state['status'],flush=True)
    except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise
    finally:device.close()

if __name__=='__main__':main()
