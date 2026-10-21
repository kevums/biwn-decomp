"""Check the two source-specific word-coordinate formats against actual1B45A."""
import ctypes as c,itertools,json,subprocess,hashlib,os
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN
from unicorn.m68k_const import *
import check_biwn_overlay as overlay
import check_biwn_input_dispatch as dispatch
ROOT=overlay.ROOT;world=overlay.world;SP=world.SP;STOP=world.STOP;DEST=0x190000
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
def main():
 out=ROOT/'verification/biwn-overlay-format'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source=ROOT/'projects/black-ice-white-noise/restoration';lib=out/'liboverlay-format.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_overlay_format.c'),'-o',str(lib)];subprocess.run(cmd,check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});fn=c.CDLL(str(lib)).biwn_overlay_format;fn.argtypes=[c.POINTER(world.Bus),dispatch.W8]+[c.c_uint32]*2+[c.c_uint16]*3+[c.POINTER(c.c_uint32)];fn.restype=c.c_int;snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rows=[]
 try:
  for fmt,words in itertools.product([0x181da,0x181e9],itertools.product([0,1,7,16,0x7fff,0x8000,0xffff,0xffa0],repeat=3)):
   save(out/'status.json',{'status':'running','case':len(rows)});cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,snapshot);cpu.mem_write(DEST,b'\xa5'*50);cpu.mem_write(SP,STOP.to_bytes(4,'big')+DEST.to_bytes(4,'big')+fmt.to_bytes(4,'big')+b''.join(v.to_bytes(2,'big')for v in words));cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP);cpu.emu_start(0x1b45a,STOP,count=200000,timeout=2000000);assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
   memory=bytearray(snapshot);memory[DEST:DEST+50]=b'\xa5'*50
   def read(_,a,v):v[0]=memory[a];return 0
   def write(_,a,v):memory[a]=v;return 0
   r8=world.R8(read);w8=dispatch.W8(write);bus=world.Bus(r8,world.R16(),world.R32(),world.W16(),world.W32(),world.CALL(),None,0);d0=c.c_uint32(0xa55aa55a);assert fn(c.byref(bus),w8,DEST,fmt,*words,c.byref(d0))==0
   raw=bytes(memory[DEST:DEST+50]);expected=bytes(cpu.mem_read(DEST,50));assert raw==expected and d0.value==cpu.reg_read(UC_M68K_REG_D0)
   rows.append({'format':hex(fmt),'word_arguments':list(words),'text':raw.split(b'\0')[0].decode(),'full_D0':d0.value,'output_and_untouched_tail_match_original':True})
 except Exception as error:save(out/'status.json',{'status':'terminal_failed','error':repr(error)});raise
 save(out/'fixtures.json',rows);guards=[]
 for kind in ['null_bus','null_output','null_write','null_read','unsupported_format','changed_literal','write_error']:
  memory=bytearray(snapshot)
  if kind=='changed_literal':memory[0x181da]=ord('X')
  def read(_,a,v):v[0]=memory[a];return 0
  def write(_,a,v):memory[a]=v;return int(kind=='write_error'and a==DEST+2)
  r8=world.R8()if kind=='null_read'else world.R8(read);w8=dispatch.W8()if kind=='null_write'else dispatch.W8(write);bus=world.Bus(r8,world.R16(),world.R32(),world.W16(),world.W32(),world.CALL(),None,0);d0=c.c_uint32(0xa55aa55a);status=fn(None if kind=='null_bus'else c.byref(bus),w8,DEST,0 if kind=='unsupported_format'else 0x181da,0,0,0,None if kind=='null_output'else c.byref(d0));assert status and d0.value==0xa55aa55a;guards.append({'kind':kind,'rejected':True,'output_unchanged':True})
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'two_fixed_overlay_formats_output_and_D0_match_original1B45A','directory':str(out),'cases':len(rows),'host_guards':len(guards),'additional_original_components':0,'source_sha256':{n:hashlib.sha256((source/n).read_bytes()).hexdigest()for n in ['biwn_overlay_format.c','biwn_overlay_format.h']},'limits':['Only two frozen literal formats and signed16 arguments; not generalprintf or all1B45A behavior. Originalformatter private/global scratch effects not reproduced.','Exact50byte outputincludingNULanduntouchedtail plusfullD0(character count) compared; destination is finite separateRAM at190000. Destination overlap withformatterinternals excluded.']};save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',{'status':'terminal_pass'});save(ROOT/'verification/biwn-overlay-format-checks.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
