"""Check exact original checkpoint deserialization before any candidate edits."""
import ctypes as c,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_world_movement_pipeline as hardware
ROOT=hardware.ROOT;sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 path=ROOT/'runs/zero-warm-whole-merchant-reference/report.json';j=json.loads(path.read_text());folder=Path(j['directory']);core_path=Path(j['core']);assert sha(core_path.read_bytes())==j['core_sha256']
 build=json.loads((ROOT/'verification/mode3-world-render-device-build-current.json').read_text());device=hardware.Device(Path(build['library']),core=core_path);core=c.CDLL(str(core_path))
 try:
  class Game(c.Structure):_fields_=[('path',c.c_char_p),('data',c.c_void_p),('size',c.c_size_t),('meta',c.c_char_p)]
  disc=ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi';core.retro_load_game.argtypes=[c.POINTER(Game)];core.retro_load_game.restype=c.c_bool;assert core.retro_load_game(c.byref(Game(str(disc).encode(),None,0,None)))
  blob=(folder/'final-serialized-state.bin').read_bytes();core.retro_unserialize.argtypes=[c.c_void_p,c.c_size_t];core.retro_unserialize.restype=c.c_bool;assert core.retro_unserialize(c.create_string_buffer(blob),len(blob))
  core.retro_serialize_size.restype=c.c_size_t;core.retro_serialize.argtypes=[c.c_void_p,c.c_size_t];core.retro_serialize.restype=c.c_bool;copy=c.create_string_buffer(core.retro_serialize_size());assert core.retro_serialize(copy,len(copy))and copy.raw==blob
  device.pointer=device.lib.lab_device_ram();ram=device.ram();assert ram==(folder/'final-RAM.bin').read_bytes()
  core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];core.GPUReadLong.restype=c.c_uint32;core.GPUGetPC.restype=c.c_uint32
  report=dict(status='recorded_original_machine_byte_exact_restore_verified',recorded_at=datetime.now(timezone.utc).isoformat(),checkpoint_report=str(path),core_path=str(core_path),core_sha256=j['core_sha256'],state_path=str(folder/'final-serialized-state.bin'),state_sha256=sha(blob),RAM_sha256=sha(ram),GPU_PC=hex(core.GPUGetPC()),GPU_mailbox={hex(a):hex(core.GPUReadLong(a,0))for a in [0xf03200,0xf03204,0xf03208]},new_instructions_executed=False,scope='Same captured reference core; exact serializedmachine roundtrip andwholeRAM equality before any instruction/candidate patch. Not a continuation/gameplay/boot or modified-program proof.')
  (ROOT/'verification/mode3-recorded-machine-restore-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],report['GPU_PC'],report['GPU_mailbox'])
 finally:device.close()
if __name__=='__main__':main()
