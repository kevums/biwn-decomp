"""Build a separate Ghidra language candidate for word DIVU overflow behavior.

The existing processor/default language is left untouched. This candidate still
uses the upstream 68040 family decoder and does not model divide-by-zero traps.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
GHIDRA = ROOT / 'tools/ghidra_12.1.4_PUBLIC'
LANGUAGES = GHIDRA / 'Ghidra/Processors/68000/data/languages'
EXPECTED = 'fea0caad18cd91249bf2441a67678e3a38e375bface616310513341fc6baf948'
LANGUAGE_ID = '68000:BE:32:BIWN_DIVU_CANDIDATE'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = LANGUAGES / '68000.sinc'
    originals = {p.name: sha(p) for p in [source, LANGUAGES / '68040.sla', LANGUAGES / '68000.ldefs']}
    if originals[source.name] != EXPECTED:
        raise ValueError('Upstream processor source changed; re-review the proposed patch')
    text = source.read_text()
    begin = text.index(':divu.w eaw,reg9dn')
    end = text.index('\n#remyes', begin)
    old = text[begin:end]
    if old.count('VF') != 0 or 'reg9dn = (rem << 16) | (div & 0xffff);' not in old:
        raise ValueError('Unexpected word DIVU constructor')
    candidate = '''# Experimental BIWN candidate: successful word quotient flags,
# overflow flag and unchanged destination on overflow. Zero-divisor CPU trap
# behavior is not implemented by this candidate and is excluded from validation.
:divu.w eaw,reg9dn is (op=8 & reg9dn & op68=3)... & eaw
{
    local denom = zext(eaw);
    local divis = reg9dn;
    local div = divis / denom;
    local rem = divis % denom;
    CF=0;
    VF = div > 0xffff;
    if (VF != 0) goto <overflow>;
    NF = (div & 0x8000) != 0;
    ZF = (div & 0xffff) == 0;
    reg9dn = (rem << 16) | (div & 0xffff);
    <overflow>
}
'''
    patched = LANGUAGES / 'biwn_divu_candidate.sinc'
    patched.write_text(text[:begin] + candidate + text[end:])
    spec = LANGUAGES / 'biwn_divu_candidate.slaspec'
    spec.write_text('@define MC68040 ""\n@include "biwn_divu_candidate.sinc"\n')
    xml = ET.Element('language_definitions')
    language = ET.SubElement(xml, 'language', {
        'processor': '68000', 'endian': 'big', 'size': '32',
        'variant': 'BIWN_DIVU_CANDIDATE', 'version': '1.1',
        'slafile': 'biwn_divu_candidate.sla', 'processorspec': '68000.pspec',
        'manualindexfile': '../manuals/68000.idx', 'id': LANGUAGE_ID})
    ET.SubElement(language, 'description').text = 'Experimental 68040-family decoder with BIWN word DIVU candidate semantics'
    ET.SubElement(language, 'compiler', {'name': 'default', 'spec': '68000.cspec', 'id': 'default'})
    ET.SubElement(language, 'compiler', {'name': 'Two-byte stack slots candidate', 'spec': '68000_stack2_candidate.cspec', 'id': 'stack2candidate'})
    ET.indent(xml)
    definition = LANGUAGES / 'biwn_divu_candidate.ldefs'
    environment = os.environ.copy()
    environment['JAVA_HOME'] = str(ROOT / 'tools/jdk-21.0.12.1+1/Contents/Home')
    command = [str(GHIDRA / 'support/sleigh'), str(spec)]
    log = ROOT / 'verification/biwn-divu-language-build.log'
    with log.open('w') as stream:
        result = subprocess.run(command, env=environment, stdout=stream, stderr=subprocess.STDOUT, timeout=180)
    compiled = LANGUAGES / 'biwn_divu_candidate.sla'
    if result.returncode != 0 or not compiled.is_file():
        raise ValueError('Candidate language did not compile; inspect ' + str(log))
    definition.write_bytes(ET.tostring(xml, encoding='utf-8', xml_declaration=True) + b'\n')
    after = {name: sha(LANGUAGES / name) for name in originals}
    if after != originals:
        raise ValueError('An upstream default processor artifact changed unexpectedly')
    report = {
        'time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status': 'candidate_language_compiled_validation_pending', 'language_id': LANGUAGE_ID,
        'original_artifacts_unchanged': originals,
        'candidate_artifacts': {p.name: sha(p) for p in [patched, spec, definition, compiled]},
        'command': command, 'log': str(log), 'old_constructor': old, 'new_constructor': candidate,
        'primary_reference': 'https://www.nxp.com/docs/en/reference-manual/M68000PRM.pdf',
        'reference_section': 'DIVU/DIVUL, printed4-96',
        'scope': 'Word DIVU nonzero divisor behavior only; independent p-code comparison pending. Default language unchanged; still a68040 decoder superset, not strict68000.',
    }
    path = ROOT / 'verification/biwn-divu-language.json'
    path.write_text(json.dumps(report, indent=2) + '\n')
    print(path)


if __name__ == '__main__':
    main()
