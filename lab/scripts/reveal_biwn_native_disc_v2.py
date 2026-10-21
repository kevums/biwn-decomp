"""Reveal the actual latest published, hash-checked experimental disc."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 root=ROOT;config=root/'config/biwn-native-reference.json'
 if config.is_file():root=Path(json.loads(config.read_text())['core']).resolve().parents[2]
 parser=argparse.ArgumentParser();parser.add_argument('--print',action='store_true',dest='print_only');args=parser.parse_args();publication=json.loads((root/'verification/current-biwn-latest-publication-current.json').read_text())
 assert publication['schema_version']==2 and publication['status']=='terminal_native_geometry_status_v2_published','Latest publication is not verified'
 build=publication['facts']['experimental_build'];disc=Path(build['derived_disc']).resolve();assert disc.is_relative_to(root/'builds')and disc.is_file()
 with disc.open('rb')as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==build['derived_disc_sha256'],'Published disc changed'
 if args.print_only:print(disc)
 else:subprocess.run(['/usr/bin/open','-R',str(disc)],check=True)
if __name__=='__main__':main()
