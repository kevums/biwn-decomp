"""Same original-CPU checks, with coordinator host-error latching repair.

V1 interpreted a failed return-address read as a bad return, overwriting the
latched bus error. V2 retains that first error; successful source behavior is
unchanged. Original local requests and V1 trials remain preserved.
"""
import json,sys
from pathlib import Path
import check_deck_coordinate_source_v1 as checker
def main():
 checker.SRC=checker.SRC.with_name('deck-coordinate-update-v2')
 result=checker.main()
 p=Path(sys.argv[2])/'protocol.json';report=json.loads(p.read_text())
 report['glue_version']=2
 report['glue_repair']='After deck_pop fails, preserve its latched bus error before checking return-address value. No successful-source behavior changed.'
 report['source_bindings'][str(Path(__file__).resolve())]=checker.sha(Path(__file__).read_bytes())
 checker.save(p,report);return result
if __name__=='__main__':sys.exit(main())
