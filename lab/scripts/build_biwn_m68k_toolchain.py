"""Build an isolated GNU m68k-elf C toolchain; no system/PATH modification.

Pinned GNU source releases. This is a compiler foundation, not a bootable
Jaguar image. Resume an existing failed build with --resume DIRECTORY;
never start another copy while its recorded process is still alive.
"""
import argparse,fcntl,hashlib,json,os,shutil,subprocess,sys,tarfile
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def sha(path):
 with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--resume',type=Path);args=parser.parse_args()
 base=ROOT/'tools/m68k-build';base.mkdir(parents=True,exist_ok=True)
 out=args.resume.resolve()if args.resume else base/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
 assert out.parent==base.resolve()
 out.mkdir(exist_ok=True);prefix=ROOT/'tools/m68k-elf';prefix.mkdir(exist_ok=True)
 lock=(base/'.build.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 state=json.loads((out/'protocol.json').read_text())if args.resume else dict(directory=str(out),prefix=str(prefix),commands=[],archives={},source_releases={'gcc':'15.2.0','binutils':'2.45'},official_sources=['https://gcc.gnu.org/releases.html','https://gcc.gnu.org/install/prerequisites.html','https://gcc.gnu.org/onlinedocs/gcc/M680x0-Options.html','https://sourceware.org/binutils/'],whole_game_complete=False,bootable_Jaguar_image_built=False)
 if args.resume and 'error'in state:
  state.setdefault('earlier_failures',[]).append(dict(error=state.pop('error'),failed_at=state.pop('failed_at',None)))
 state.update(status='preparing',pid=os.getpid(),started_at=datetime.now(timezone.utc).isoformat(),host_system_zlib=True)
 env={**os.environ,'PATH':str(prefix/'bin')+os.pathsep+os.environ['PATH'],'CONFIG_SHELL':'/bin/bash','CC':'/usr/bin/clang','CXX':'/usr/bin/clang++','MAKEINFO':'true','DEVELOPER_DIR':'/Library/Developer/CommandLineTools'}
 def checkpoint():save(out/'protocol.json',state);save(ROOT/'verification/m68k-toolchain-active.json',state)
 def run(phase,command,cwd):
  logfile=out/(phase+'.log')
  with logfile.open('a')as stream:
   child=subprocess.Popen(command,cwd=cwd,env=env,stdout=stream,stderr=subprocess.STDOUT)
   row=dict(phase=phase,command=command,cwd=str(cwd),log=str(logfile),pid=child.pid)
   state['commands'].append(row);state.update(status='running_'+phase,child_pid=child.pid);checkpoint();print(phase,'PID',child.pid,flush=True)
   code=child.wait();row['exit_code']=code;checkpoint()
  if code:raise RuntimeError(phase+' failed; see '+str(logfile))
 def download(name,url):
  path=out/name
  if not path.exists():
   partial=out/(name+'.part');run('download-'+name,['/usr/bin/curl','--fail','--location','--retry','2','--connect-timeout','20','--max-time','1200','--output',str(partial),url],out);partial.rename(path)
  state['archives'][name]=dict(url=url,sha256=sha(path),bytes=path.stat().st_size);checkpoint();return path
 def extract(archive,dirname):
  target=out/dirname
  if not target.exists():
   state.update(status='extracting_'+dirname);checkpoint()
   with tarfile.open(archive)as tar:tar.extractall(out,filter='data')
  assert target.is_dir();return target
 checkpoint();print(out,flush=True)
 try:
  binutils_archive=download('binutils-2.45.tar.xz','https://ftp.gnu.org/gnu/binutils/binutils-2.45.tar.xz')
  binutils=extract(binutils_archive,'binutils-2.45');build=out/'build-binutils';build.mkdir(exist_ok=True)
  if not(build/'Makefile').exists():
   run('configure-binutils',['/bin/bash',str(binutils/'configure'),'--target=m68k-elf','--prefix='+str(prefix),'--disable-nls','--disable-werror','--disable-gprofng','--disable-gdb','--disable-sim','--enable-deterministic-archives','--disable-shared','--with-system-zlib'],build)
  run('build-binutils',['/usr/bin/make','-j8','MAKEINFO=true'],build)
  run('install-binutils',['/usr/bin/make','install','MAKEINFO=true'],build)
  gcc_archive=download('gcc-15.2.0.tar.xz','https://ftp.gnu.org/gnu/gcc/gcc-15.2.0/gcc-15.2.0.tar.xz')
  checksum=download('gcc-sha512.sum','https://gcc.gnu.org/pub/gcc/releases/gcc-15.2.0/sha512.sum')
  expected=next(line.split()[0]for line in checksum.read_text().splitlines()if line.split()[-1].lstrip('*')=='gcc-15.2.0.tar.xz')
  with gcc_archive.open('rb')as stream:assert hashlib.file_digest(stream,'sha512').hexdigest()==expected
  state['archives'][gcc_archive.name]['official_SHA512_verified']=True;checkpoint()
  gcc=extract(gcc_archive,'gcc-15.2.0')
  script=gcc/'contrib/download_prerequisites'
  assert '--no-isl' in script.read_text()and 'sha512' in script.read_text()
  if not all((gcc/name).exists()for name in ['gmp','mpfr','mpc']):run('gcc-prerequisites',['/bin/bash',str(script),'--no-isl'],gcc)
  state['prerequisite_script_sha256']=sha(script)
  build=out/'build-gcc';build.mkdir(exist_ok=True)
  if not(build/'Makefile').exists():
   run('configure-gcc',['/bin/bash',str(gcc/'configure'),'--target=m68k-elf','--prefix='+str(prefix),'--enable-languages=c','--disable-bootstrap','--disable-multilib','--disable-nls','--disable-shared','--disable-threads','--disable-libssp','--disable-libgomp','--disable-libquadmath','--disable-libatomic','--disable-libsanitizer','--without-headers','--with-newlib','--with-system-zlib','--with-gnu-as','--with-gnu-ld','--with-as='+str(prefix/'bin/m68k-elf-as'),'--with-ld='+str(prefix/'bin/m68k-elf-ld')],build)
  run('build-gcc',['/usr/bin/make','-j8','all-gcc','all-target-libgcc','MAKEINFO=true'],build)
  run('install-gcc',['/usr/bin/make','install-gcc','install-target-libgcc','MAKEINFO=true'],build)
  smoke=out/'smoke';smoke.mkdir(exist_ok=True)
  (smoke/'smoke.c').write_text('typedef unsigned long u32;\nu32 biwn_native_smoke(u32 a,u32 b){return a*3u+(b>>2);}\n')
  (smoke/'smoke.ld').write_text('ENTRY(biwn_native_smoke)\nSECTIONS { . = 0x10000; .text : { *(.text*) } .data : { *(.data*) } .bss : { *(.bss*) } }\n')
  compiler=prefix/'bin/m68k-elf-gcc'
  run('compile-smoke',[str(compiler),'-m68000','-msoft-float','-ffreestanding','-fno-pie','-fno-pic','-fno-stack-protector','-O2','-nostdlib','-Wl,-T,'+str(smoke/'smoke.ld'),str(smoke/'smoke.c'),'-o',str(smoke/'smoke.elf')],smoke)
  run('objcopy-smoke',[str(prefix/'bin/m68k-elf-objcopy'),'-O','binary',str(smoke/'smoke.elf'),str(smoke/'smoke.bin')],smoke)
  import random
  from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN
  from unicorn.m68k_const import UC_CPU_M68K_M68000,UC_M68K_REG_PC,UC_M68K_REG_SR,UC_M68K_REG_A7,UC_M68K_REG_D0,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6
  rng=random.Random(0x68000);pairs=[(0,0),(1,1),(0xffffffff,0xffffffff),(0x80000000,0x7fffffff)]+[(rng.getrandbits(32),rng.getrandbits(32))for _ in range(60)];rows=[];code=(smoke/'smoke.bin').read_bytes()
  saved_regs=[UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6]
  for a,b in pairs:
   cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0x10000,code);cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,0x180000);cpu.mem_write(0x180000,(0x1f0000).to_bytes(4,'big')+a.to_bytes(4,'big')+b.to_bytes(4,'big'));saved=[rng.getrandbits(32)for _ in saved_regs]
   for reg,value in zip(saved_regs,saved):cpu.reg_write(reg,value)
   cpu.emu_start(0x10000,0x1f0000,count=10000);expected=(a*3+(b>>2))&0xffffffff
   assert cpu.reg_read(UC_M68K_REG_PC)==0x1f0000 and cpu.reg_read(UC_M68K_REG_D0)==expected and cpu.reg_read(UC_M68K_REG_A7)==0x180004
   assert all(cpu.reg_read(reg)==value for reg,value in zip(saved_regs,saved));rows.append(dict(a=a,b=b,D0=expected))
  save(smoke/'cases.json',rows)
  state.update(status='terminal_toolchain_smoke_pass',completed_at=datetime.now(timezone.utc).isoformat(),smoke_cases=len(rows),compiler=str(compiler),target='m68k-elf',compile_CPU='68000',smoke_is_game_routine=False,compiler_version=subprocess.check_output([str(compiler),'--version'],text=True).splitlines()[0],binaries_sha256={str(path):sha(path)for path in(prefix/'bin').iterdir()if path.is_file()},next_work='Compile recovered BIWN routines with real original helper ABI, compare original M68000 behavior, then test packaged Jaguar image. Toolchain smoke is not a BIWN rebuild.')
  checkpoint();save(ROOT/'verification/m68k-toolchain-current.json',state);print(json.dumps(dict(status=state['status'],directory=str(out),compiler=str(compiler),smoke_cases=len(rows))),flush=True)
 except BaseException as error:
  state.update(status='terminal_failed',error=repr(error),failed_at=datetime.now(timezone.utc).isoformat());checkpoint();raise

if __name__=='__main__':main()
