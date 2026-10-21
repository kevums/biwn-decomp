"""Prepare default/negative-control CCR-lowered sources from original facts."""
import json,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import m68k_fact_packet_v2 as facts
import lower_m68k_facts_to_C_v3 as lower
from run_biwn_native_fast_gameplay_route import sha,save
from check_native_string_candidate import validate_c


def main():
    image_path=ROOT/'render-assets/biwn-inventory-baseline.bin'
    assert sha(image_path)=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3'
    packet=facts.packet(image_path.read_bytes(),0x1b1a8,0x1b200)
    cert=ROOT/'verification/native-string-source-certificate-current.json';old=json.loads(cert.read_text())
    original=json.loads(Path(old['packet']).read_text());assert packet==original
    out=ROOT/'verification/native-string-ccr-preparation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    audit=lower.liveness(packet);source=lower.lower(packet);path=out/'format-string-ccr.c';path.write_text(source);ast=validate_c(source)
    bad=out/'format-string-bad-exit-flags.c';bad.write_text(lower.lower(packet,exit_flags=16));validate_c(bad.read_text())
    save(out/'liveness.json',audit);save(out/'instruction-facts.json',packet)
    changed=[row for row in audit['rows']if row['defines'] and row['defines']!=row['computed_flags']]
    result=dict(status='prepared_CCR_liveness_sources_pending_original_CPU_checks',directory=str(out),source=str(path),source_sha256=sha(path),
        negative_source=str(bad),negative_source_sha256=sha(bad),analysis=str(out/'liveness.json'),
        static_flag_defining_instructions=sum(bool(r['defines'])for r in audit['rows']),
        static_instructions_computing_flags=sum(bool(r['computed_flags'])for r in audit['rows']),
        changed_flag_calculations=[dict(pc=hex(r['pc']),before=r['defines'],after=r['computed_flags'])for r in changed],
        AST=ast,source_origin='coordinator_typed_IR_liveness_compiler',local_model_authored_C=False,
        original_certificate_unchanged=sha(cert),new_training=False,default_promoted=False,whole_game_complete=False,
        dependencies_sha256={str(p):sha(p)for p in [Path(__file__),Path(lower.__file__),Path(facts.__file__),image_path,cert,Path(old['packet']),path,bad,out/'liveness.json',out/'instruction-facts.json']})
    save(out/'report.json',result);save(ROOT/'verification/native-string-ccr-preparation-current.json',result)
    print(json.dumps({k:result[k]for k in ['status','directory','static_flag_defining_instructions','static_instructions_computing_flags']}))


if __name__=='__main__':main()
