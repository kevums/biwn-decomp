"""Supersede defective WORD trace evidence while retaining identical-disc gameplay."""
import json,shutil,hashlib
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
    v=ROOT/'verification';rp=v/'native-geometry-scan-live-reviewed-current.json';old=json.loads(rp.read_text());bp=v/'native-geometry-scan-corrected-build-current.json';build=json.loads(bp.read_text());cp=v/'native-geometry-scan-word-correction-current.json';correction=json.loads(cp.read_text())
    assert old['status']=='terminal_native_geometry_scan_two_live_routes_reviewed' and correction['status']=='terminal_linked_scanner_word_injection_corrected_pass'
    assert old['derived_disc_sha256']==build['derived_disc_sha256']==correction['derived_disc_sha256']==sha(build['derived_disc'])
    out=v/'native-geometry-scan-corrected-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);shutil.copy2(rp,out/'live-review-before-correction.json');shutil.copy2(bp,out/'corrected-build.json');shutil.copy2(cp,out/'correction.json');deps=dict(old['dependencies_sha256'])
    for p,h in correction['dependencies_sha256'].items():assert sha(p)==h,p;deps[p]=h
    for p in [out/'live-review-before-correction.json',out/'corrected-build.json',out/'correction.json',Path(__file__)]:deps[str(p)]=sha(p)
    report=ROOT/'reports/native-geometry-scan-corrected.txt';report.write_text('BIWN — SCANNER VERIFIER CORRECTION AND CURRENT VERIFIED RESULT\n\n'
      'An ordered-access tracer defect wrote four bytes when a declared changed-read injection was two bytes. The first C-provider scanner test exposed the discrepancy: final native/C CPU andRAM matched, but recorded access values did not. Earlier WORD changed-read ordered-event evidence is superseded. Original failed/as-run files are preserved.\n\n'
      'The versioned tracer writes exactly the declared width. All1377stable+768changing-read cases pass again for standalone and exact final-linked scanner bytes, with added native-versus-tracer publicRAM equality on both original and compiled sides. All69original instruction sites are reached. No scanner C, ABI, component or CDI byte changed. The correction therefore retains the prior96startup checks and fresh24996/24978frame native gameplay runs by exact disc identity; these runs were not repeated by this correction.\n\n'
      'Candidate live scanner checks:4753compiled calls,11success and4742failure returns,56868record iterations; zero errors/pending/stack-outside. Original-entry control:4787original calls,11success and4776failure returns. Candidate private depth64bytes/minimum task headroom678bytes. Both returned outdoors. Route frame counts, video/audio/CPU/GPU/DSP/navigation differ; no whole-machine/cycle or physical-console equivalence. Default preview is unchanged.\n\n'
      'All three local C candidates failed before any WORD changing-read fixture; their rejection and five saved prediction records remain applicable. The accepted code and verifier correction are coordinator work. No weights changed. The exact-disc C instruction provider separately passed105216atomic CPU/RAM/cost cases,1280+512indexed-selector function cases and1377+768scanner function cases. Its fresh C CPU/GPU/DSP/IRQ gameplay comparison is a separately observed job.\n\n'
      'Exact original gameplay review:\n'+old['report']+'\nCorrected verifier receipt:\n'+str(Path(correction['directory'])/'protocol.json')+'\nExact model prompts:\n'+str(ROOT/'reports/native-geometry-scan-prompts-and-responses.txt')+'\n')
    deps[str(report)]=sha(report);result=dict(old,recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),report=str(report),build=str(out/'corrected-build.json'),build_sha256=sha(out/'corrected-build.json'),verification_correction=str(out/'correction.json'),same_disc_gameplay_reused_by_sha256=True,dependencies_sha256=deps,scope='Corrected width-exact standalone/final-link verifier evidence plus unchanged exact-disc startup/native gameplay. Old WORD ordered values superseded; no game byte changes or new live run in this receipt.')
    save(out/'protocol.json',result);save(v/'native-geometry-scan-corrected-live-reviewed-current.json',result);print(result['report'])
if __name__=='__main__':main()
