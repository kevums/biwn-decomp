"""Build the real checked navigation group using copied source and toolchain.
A portable Makefile quotes executable paths and is invoked from its source folder;
the original as-run Makefile/source stay unchanged. No game/model behavior changes.
"""
import json,os,subprocess,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def main():
 v=ROOT/'verification';state=json.loads((v/'portable-sdk-workbench-current.json').read_text());p=Path(state['package']);nd=p/'workbench/projects/black-ice-white-noise/restoration/native-m68k';out=p/'test-results'/('native-build-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir(parents=True)
 original=nd/'Makefile.actor-navigation';text=original.read_text();text=text.replace('ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/../../../..)','ROOT := $(abspath ../../../..)').replace('SOURCE_DIR := $(dir $(lastword $(MAKEFILE_LIST)))','SOURCE_DIR := ./')
 for tool in ['gcc','objcopy']:text=text.replace('$(PREFIX)'+tool,'"$(PREFIX)'+tool+'"')
 portable=nd/'Makefile.actor-navigation-portable';expected_makefile='# Run from this directory; the supplied launcher handles cwd and quoted paths.\n'+text
 if portable.exists():assert portable.read_text()==expected_makefile
 else:portable.write_text(expected_makefile)
 env={k:x for k,x in os.environ.items()if k not in ['PYTHONPATH','PYTHONHOME','VIRTUAL_ENV']};command=['make','-f','Makefile.actor-navigation-portable','actor-navigation','BUILD='+str(out/'build'),'NAV_SOURCE=./actor-navigation-hybrid-v1.c','ADDRESS=0x165ce0'];run=subprocess.run(command,cwd=nd,env=env,capture_output=True,text=True,timeout=120);(out/'build.log').write_text(run.stdout+run.stderr)
 assert run.returncode==0,run.stderr
 expected=json.loads((v/'native-navigation-hybrid-final-current.json').read_text());binary=out/'build/actor-navigation.bin';assert binary.stat().st_size==1588 and sha(binary)==sha(expected['binary'])
 gcc=p/'workbench/tools/m68k-elf/bin/m68k-elf-gcc';search=subprocess.check_output([str(gcc),'-print-search-dirs'],cwd=nd,env=env,text=True);(out/'compiler-search-dirs.txt').write_text(search);assert str(ROOT)not in search and str(p/'workbench/tools/m68k-elf')in search
 result=dict(status='terminal_copied_source_toolchain_native_binary_identical',directory=str(out),package=str(p),binary=str(binary),binary_bytes=1588,binary_sha256=sha(binary),expected_binary_sha256=sha(expected['binary']),actual_source_build=True,original_makefile_changed=False,space_in_package_path_handled=True,new_training=False,whole_game_rebuild=False,scope=__doc__);save(out/'protocol.json',result);save(p/'portable-native-build-current.json',result);save(v/'portable-native-build-current.json',result);print(json.dumps({k:result[k]for k in ['status','binary_bytes','binary_sha256']}))
if __name__=='__main__':main()
