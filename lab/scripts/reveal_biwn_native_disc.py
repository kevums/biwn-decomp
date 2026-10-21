from pathlib import Path
import json,subprocess,argparse
root=Path(__file__).resolve().parents[1]
config=root/'config/biwn-native-reference.json'
if config.is_file():root=Path(json.loads(config.read_text())['core']).resolve().parents[2]
parser=argparse.ArgumentParser();parser.add_argument('--print',action='store_true',dest='print_only');args=parser.parse_args()
for name in ['native-resource-publication-current.json','native-free-publication-current.json','native-copy-publication-current.json','native-heap-publication-current.json','native-scheduler-publication-current.json','native-task-create-publication-current.json','native-word-scan-publication-current.json','native-controller-publication-current.json','native-fast-gameplay-publication-current.json','native-rng-publication-current.json','native-optimized-publication-current.json','native-bundle-publication-current.json','native-disc-build-current.json']:
 path=root/'verification'/name
 if path.is_file():disc=Path(json.loads(path.read_text())['derived_disc']);break
else:raise RuntimeError('No native disc build found')
assert disc.is_file()
if args.print_only:print(disc)
else:subprocess.run(['/usr/bin/open','-R',str(disc)],check=True)
