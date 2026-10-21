"""Reveal the current hash-checked disc; --print performs no UI action."""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from native_deck_status_evidence_v1 import load


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--print', action='store_true', dest='print_only')
    args = parser.parse_args()
    packet = load(ROOT)
    disc = Path(packet['experimental_build']['derived_disc']).resolve()
    assert disc.is_file() and disc.is_relative_to(ROOT/'builds')
    if args.print_only:
        print(disc)
    else:
        subprocess.run(['/usr/bin/open', '-R', str(disc)], check=True)


if __name__ == '__main__':
    main()
