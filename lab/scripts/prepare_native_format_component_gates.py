"""Derive separate existing full matrices for the exact new linked payload."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OLD_SHA='130639a231a37d872a52226927b30545cfef214f568377751de61897398d0c73'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    bp=ROOT/'verification/native-format-bundle-current.json';bundle=json.loads(bp.read_text());assert sha(bundle['binary'])==bundle['binary_sha256']
    directory=Path(bundle['directory']);makefile=directory/'Makefile';records=[]
    for kind in ['controller','rng','tasks','scheduler','heap','copy','free','release']:
        parent=ROOT/'scripts'/f'check_biwn_native_load_scan_bundle_{kind}.py';source=parent.read_text()
        assert source.count("'Makefile.load-scan-bundle'")==1
        assert source.count("'load-scan-bundle'")==1
        assert source.count(OLD_SHA)==1
        text=source.replace("'Makefile.load-scan-bundle'",repr(str(makefile))).replace("'load-scan-bundle'","'format-bundle'")
        text=text.replace('native-load-scan-bundle','native-format-bundle').replace(OLD_SHA,bundle['binary_sha256'])
        # Only output/build selection and the exact expected linked hash change.
        # Vectors, loops, comparisons, instruction whitelists and limits remain.
        path=ROOT/'scripts'/f'check_biwn_native_format_bundle_{kind}.py';compile(text,str(path),'exec');path.write_text(text)
        snapshots=directory/'component-gate-sources';snapshots.mkdir(exist_ok=True)
        (snapshots/parent.name).write_bytes(parent.read_bytes());(snapshots/path.name).write_bytes(path.read_bytes())
        records.append(dict(kind=kind,parent=str(parent),parent_sha256=sha(parent),derived=str(path),derived_sha256=sha(path),transformations=['Use separately generated format-bundle Makefile and target','Separate output/proof paths and artifact stem','Replace exact expected native28 binary hash with exact expected new linked binary hash'],test_vectors_or_assertions_removed=False))
    report=dict(status='eight_linked_component_full_matrix_drivers_prepared',bundle_proof=str(bp),bundle_proof_sha256=sha(bp),binary_sha256=bundle['binary_sha256'],makefile=str(makefile),makefile_sha256=sha(makefile),drivers=records,source_accepted=False)
    (ROOT/'verification/native-format-component-driver-preparation-current.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
