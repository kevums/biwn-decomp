"""Build a separate explicit M68000 soft-float libgcc; preserve default tools."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,shutil,subprocess
from check_biwn_native_button_digit import ROOT,sha,save

def main():
 out=ROOT/'tools/m68k-68000-runtime-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 tool=json.loads((ROOT/'verification/m68k-toolchain-current.json').read_text());sourcebuild=Path(tool.get('directory',''))
 # Original build is preserved by the established toolchain builder.
 sourcebuild=ROOT/'tools/m68k-build/20261018T015624.082655Z/build-gcc'
 target=out/'build/m68k-elf/libgcc';target.parent.mkdir(parents=True);shutil.copytree(sourcebuild/'m68k-elf/libgcc',target,symlinks=True)
 (out/'build/gcc').symlink_to(sourcebuild/'gcc',target_is_directory=True)
 state=dict(status='prepared',directory=str(out),pid=os.getpid(),original_default_archive_changed=False,whole_game_complete=False,commands=[])
 def checkpoint():save(out/'protocol.json',state);save(ROOT/'verification/m68000-libgcc-active.json',state)
 checkpoint();print(out,flush=True)
 try:
  for phase,cmd in [('clean_private_copy',['make','clean']),('build_68000_soft_runtime',['make','-j6','all','CFLAGS=-g -O2 -m68000 -msoft-float'])]:
   state['commands'].append(dict(phase=phase,command=cmd));state['status']=phase;checkpoint()
   with(out/(phase+'.log')).open('w')as log:
    child=subprocess.Popen(cmd,cwd=target,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;checkpoint();code=child.wait()
   assert code==0,(phase,out/(phase+'.log'))
  archive=target/'libgcc.a';assert archive.is_file();installed=ROOT/'tools/m68k-elf/m68000-soft';installed.mkdir(exist_ok=True);shutil.copy2(archive,installed/'libgcc.a')
  state.update(status='terminal_explicit_M68000_soft_libgcc_built_pending_native_checks',archive=str(installed/'libgcc.a'),archive_sha256=sha(installed/'libgcc.a'),source_tree=str(sourcebuild.parent/'gcc-15.2.0/libgcc'),source_file_sha256=sha(sourcebuild.parent/'gcc-15.2.0/libgcc/config/m68k/lb1sf68.S'),compiler=str(ROOT/'tools/m68k-elf/bin/m68k-elf-gcc'),target_flags=['-m68000','-msoft-float'],test_script_sha256=sha(__file__))
  checkpoint();save(ROOT/'verification/m68000-libgcc-current.json',state);print(state['status'],flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));checkpoint();raise
if __name__=='__main__':main()
