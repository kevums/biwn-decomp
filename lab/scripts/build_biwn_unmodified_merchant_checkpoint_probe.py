"""Derive a separate frozen probe for the zero-repair merchant proof only."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parent = ROOT / 'scripts/build_biwn_source_checkpoint_probe.py'
    text = parent.read_text()
    changes = {
        "ROOT / 'verification/source-checkpoint-probe-build'": "ROOT / 'verification/unmodified-merchant-checkpoint-probe-build'",
        "ROOT / 'scripts/biwn_verified_source_checkpoint.py'": "ROOT / 'scripts/biwn_verified_unmodified_merchant_checkpoint.py'",
        "ROOT / 'verification/source-checkpoint-probe-candidate.json'": "ROOT / 'verification/unmodified-merchant-checkpoint-probe-candidate.json'",
        'complete existing cold-route verdict': 'complete zero-repair unmodified merchant cold-route verdict',
        'inherited18byte repair disclosure': 'zero inherited repair and separate disclosure of any continuation repair',
    }
    for old, new in changes.items():
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    # Execute only the inspected, exact derivative of the local builder. No
    # parent, existing frozen build, pinned runtime or preview is modified.
    namespace = {'__name__': '__merchant_probe_builder__', '__file__': str(parent)}
    exec(compile(text, str(parent), 'exec'), namespace)
    namespace['main']()
    pointer = ROOT / 'verification/unmodified-merchant-checkpoint-probe-candidate.json'
    record = json.loads(pointer.read_text())
    record.update(builder_parent=str(parent), builder_parent_sha256=hashlib.sha256(parent.read_bytes()).hexdigest(),
                  builder_derivation=changes, checkpoint_kind='zero_repair_unmodified_source_merchant_only',
                  runtime_verified=False)
    encoded = json.dumps(record, indent=2) + '\n'
    pointer.write_text(encoded)
    (Path(record['directory']) / 'build.json').write_text(encoded)


if __name__ == '__main__':
    main()
