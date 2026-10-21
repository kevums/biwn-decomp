"""Keep baseline replay immutable; derive a parameterized counterfactual runner."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    parent=ROOT/'scripts/replay_native_format_live_calls.py';text=parent.read_text()
    text=text.replace('import hashlib,json,os,subprocess','import argparse,hashlib,json,os,subprocess')
    marker='def main():\n';assert text.count(marker)==1
    text=text.replace(marker,marker+"    parser=argparse.ArgumentParser();parser.add_argument('--bundle-proof',type=Path,required=True);parser.add_argument('--label',required=True);args=parser.parse_args()\n")
    marker="bp=ROOT/'verification/native-format-bundle-current.json'";assert text.count(marker)==1
    text=text.replace(marker,'bp=args.bundle_proof.resolve()')
    marker="out=ROOT/'verification/native-format-live-replay'/datetime.now(timezone.utc)";assert text.count(marker)==1
    text=text.replace(marker,"out=ROOT/'verification/native-format-optimization-replay'/args.label/datetime.now(timezone.utc)")
    marker="memory=path.read_bytes();actual=actual_path.read_bytes();assert memory[bundle['base']:bundle['base']+len(payload)]==payload";assert text.count(marker)==1
    text=text.replace(marker,"memory=path.read_bytes();actual=actual_path.read_bytes();assert memory[base_bundle['base']:base_bundle['base']+len(base_payload)]==base_payload")
    marker="baseline=ROOT/'render-assets/biwn-inventory-baseline.bin'";assert text.count(marker)==1
    text=text.replace(marker,"base_bp=ROOT/'verification/native-format-bundle-current.json';base_bundle=json.loads(base_bp.read_text());base_payload=Path(base_bundle['binary']).read_bytes();assert sha(base_bundle['binary'])==base_bundle['binary_sha256'];assert bundle['base']==base_bundle['base']and bundle['heap_start']==base_bundle['heap_start']and bundle['reserved_bytes']==base_bundle['reserved_bytes']\n    "+marker)
    marker="left=bytearray(memory);left[address:ENDS[kind]]=original_code[address:ENDS[kind]]";assert text.count(marker)==1
    text=text.replace(marker,"left=bytearray(memory);left[bundle['base']:bundle['heap_start']]=payload+bytes(bundle['reserved_bytes']-len(payload));left[address:ENDS[kind]]=original_code[address:ENDS[kind]]")
    marker="right=bytearray(memory);right[address:address+6]=";assert text.count(marker)==1
    text=text.replace(marker,"right=bytearray(memory);right[bundle['base']:bundle['heap_start']]=payload+bytes(bundle['reserved_bytes']-len(payload));right[address:address+6]=")
    marker="[Path(__file__),capture_path,bp,Path(bundle['binary']),baseline,source,library]";assert text.count(marker)==1
    text=text.replace(marker,"[Path(__file__),capture_path,bp,base_bp,Path(bundle['binary']),Path(base_bundle['binary']),baseline,source,library]")
    text=text.replace("ROOT/'verification/native-format-live-replay-active.json'","ROOT/'verification'/('native-format-optimization-replay-'+args.label+'-active.json')")
    text=text.replace("ROOT/'verification/native-format-live-replay-current.json'","ROOT/'verification'/('native-format-optimization-replay-'+args.label+'-current.json')")
    text=text.replace('terminal_identical_real_helper_entry_CPU_RAM_ordered_replays_pass','terminal_optimization_live_fixture_CPU_RAM_ordered_pass')
    marker='source_accepted=True,live_return_CPU_all_match=';assert text.count(marker)==1
    text=text.replace(marker,'source_accepted=False,full_fixture_gate_accepted=False,fresh_game_run=False,counterfactual_optimization=True,live_return_CPU_all_match=')
    marker='84selected real entries from both fresh repaired lanes, each replayed through original and exact linked helper with same full RAM/CPU and IRQ disabled.';assert text.count(marker)==1
    text=text.replace(marker,'84previously captured entries replayed counterfactually through original and new optimization variant with identical RAM/CPU and IRQ disabled. Both replay lanes install the new payload into the unchanged reserved code window. The new variant has not run in a fresh game; live-return comparisons use the prior base build captures.')
    path=ROOT/'scripts/replay_native_format_optimization_live_fixtures.py';compile(text,str(path),'exec');path.write_text(text)
    out=ROOT/'verification/native-format-optimization-replay-preparation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    (out/parent.name).write_bytes(parent.read_bytes());(out/path.name).write_bytes(path.read_bytes())
    proof=dict(status='separate_counterfactual_live_fixture_replay_prepared',directory=str(out),parent=str(parent),parent_sha256=sha(parent),derived=str(path),derived_sha256=sha(path),full_fixture_assertions_removed=False,whole_game_complete=False)
    (out/'preparation.json').write_text(json.dumps(proof,indent=2)+'\n');(ROOT/'verification/native-format-optimization-replay-preparation-current.json').write_text(json.dumps(proof,indent=2)+'\n')
if __name__=='__main__':main()
