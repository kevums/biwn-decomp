"""Reveal the checked typed-IR source without starting any model or job."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--print',action='store_true');a=p.parse_args();d=json.loads((ROOT/'verification/fact-lifted-native-C-current.json').read_text());source=Path(d['source']).resolve();assert d['verified']and source.is_relative_to(ROOT/'runs/fact-chat-candidates')and hashlib.sha256(source.read_bytes()).hexdigest()==d['source_sha256']
 print(source,flush=True)
 if not a.print:subprocess.run(['open','-R',str(source)],check=True)
if __name__=='__main__':main()
