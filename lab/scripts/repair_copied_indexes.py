"""Rebase mutable retrieval-index path columns after a package move.

Cached source filenames are regenerated; source documents and historical
evidence bytes remain unchanged. Preserve pre-repair indexes for review.
"""
import json
from pathlib import Path
import shutil
import sqlite3


def main():
    root=Path(__file__).resolve().parent
    origin=json.loads((root/'origin.json').read_text())
    layout=json.loads((root/'restore-layout.json').read_text())
    pairs=[(old,str(root))for old in layout['previous_restore_roots']]
    pairs.extend([(origin['original_runtime'],str(root/'runtime')),(str(Path(origin['original_runtime']).parent),str(root/'lmstudio-home')),(origin['original_workbench'],str(root/'workbench'))])
    pairs.sort(key=lambda row:-len(row[0]))
    records=[]
    for path in sorted((root/'runtime/indexes').glob('*.sqlite')):
        backup=root/('index-before-path-repair-'+path.name)
        if not backup.exists():
            shutil.copy2(path,backup)
        con=sqlite3.connect(path)
        changed=[]
        try:
            with con:
                for(old,)in con.execute('SELECT DISTINCT source FROM chunks').fetchall():
                    new=old
                    for prefix,replacement in pairs:
                        if old==prefix or old.startswith(prefix+'/'):
                            new=replacement+old[len(prefix):]
                            break
                    assert Path(new).resolve().is_relative_to(root)and Path(new).is_file(),new
                    if new!=old:
                        con.execute('UPDATE chunks SET source=? WHERE source=?',(new,old))
                        con.execute('UPDATE chunk_pages SET source=? WHERE source=?',(new,old))
                        changed.append(dict(original=old,current=new))
            records.append(dict(index=str(path),changed_sources=changed,all_sources_inside_package=True))
        finally:
            con.close()
    result=dict(status='copied_retrieval_index_paths_repaired',package_root=str(root),indexes=records,source_document_bytes_changed=False,historical_evidence_bytes_changed=False,scope=__doc__)
    (root/'index-repair-receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    main()
