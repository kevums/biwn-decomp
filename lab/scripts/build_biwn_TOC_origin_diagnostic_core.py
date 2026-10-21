"""Separate, default-off TOC coordinate-origin diagnostic; not production fix."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
base=json.loads((ROOT/'verification/BIWN-reseek-diagnostic-build-current.json').read_text())
source=Path(base['diagnostic_source']);out=ROOT/'verification/BIWN-TOC-origin-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
build=out/'source';shutil.copytree(source,build,symlinks=True,ignore=shutil.ignore_patterns('.git','*.o','*.dylib','*.so','*.dll','private'))
p=build/'src/cd/cdintf.c';original=p.read_text();text=original
needle='uint8_t CDIntfGetSessionInfo(uint32_t session, uint32_t offset)';assert text.count(needle)==1
text=text.replace(needle,'/* Test-only TOC origin hypothesis. Raw disc addressing is untouched. */\nvoid BIWNDiagnosticTOCOrigin(uint32_t enabled)\n{\n   biwnDiagnosticTOCOrigin = ((enabled & 1) != 0);\n   biwnDiagnosticTOCReadOrigin = ((enabled & 2) != 0);\n}\n\n'+needle)
needle='uint32_t absLBA = disc.sessions[session].leadOutLBA + 150;';assert text.count(needle)==1
text=text.replace(needle,needle+'\n         if (biwnDiagnosticTOCOrigin)\n         {\n            if (session == 0)\n            {\n               uint32_t lastIdx = disc.sessions[session].lastTrack - 1;\n               absLBA = disc.tracks[lastIdx].startLBA + disc.tracks[lastIdx].lengthLBA;\n            }\n            else\n               absLBA = disc.sessions[session].leadOutLBA;\n         }')
needle='absLBA = tocLBA + 150;';assert text.count(needle)==1
text=text.replace(needle,needle+'\n   if (biwnDiagnosticTOCOrigin)\n      absLBA = tocLBA;')
text=text.replace('uint32_t absLBA = disc.sessions[session].leadOutLBA + 150;\n', 'uint32_t absLBA = disc.sessions[session].leadOutLBA + 150;\n         uint8_t m, s, f;\n', 1)
text=text.replace('         }\n         uint8_t m, s, f;\n', '         }\n', 1)
text=text.replace('static struct CDIntfDisc disc;', 'static struct CDIntfDisc disc;\nstatic bool biwnDiagnosticTOCOrigin = false;\nstatic bool biwnDiagnosticTOCReadOrigin = false;', 1)
needle='bool CDIntfReadBlock(uint32_t sector, uint8_t *buffer)'
pos=text.index(needle);before=text[:pos];after=text[pos:]
needle='   if (!disc.loaded || !buffer)'
assert after.count(needle)==1
after=after.replace(needle, '   if (biwnDiagnosticTOCReadOrigin)\n      sector += 150;\n\n'+needle,1)
text=before+after
p.write_text(text)
exports=build/'exports-test.list';exports.write_text(exports.read_text()+'\n_BIWNDiagnosticTOCOrigin\n')
p=build/'link-test.T';p.write_text(p.read_text().replace('global:','global:\n    BIWNDiagnosticTOCOrigin;',1))
report=dict(status='building',directory=str(out),source_directory=str(source),diagnostic_source=str(build),parent_core_sha256=base['core_sha256'],original_cdintf_sha256=hashlib.sha256(original.encode()).hexdigest(),diagnostic_cdintf_sha256=hashlib.sha256(text.encode()).hexdigest(),scope='Default-off metadata hypothesis: track/global leadout MSF omits additional150frames; session0 leadout uses its last track end excluding intersession gap. Independent flag2 adds150 to CDIntfReadBlock sector address to test the same coordinate origin in reads; metadata flag1 separate. Both default off. No expected checksum or TOC/RAM/stub injection. Not hardware fix or production promotion.',compiler_command=['make','-j8','TEST_EXPORTS=1'])
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
save(out/'build.json',report);print(out,flush=True);env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'}
with(out/'lint.log').open('w')as log:r=subprocess.run(['bash','scripts/c89-lint.sh','src/cd/cdintf.c'],cwd=build,env=env,stdout=log,stderr=subprocess.STDOUT)
assert r.returncode==0
with(out/'compiler.log').open('w')as log:r=subprocess.run(report['compiler_command'],cwd=build,env=env,stdout=log,stderr=subprocess.STDOUT)
assert r.returncode==0
core=build/'virtualjaguar_libretro.dylib';report.update(status='built_diagnostic_tests_pending',core_path=str(core),core_sha256=hashlib.sha256(core.read_bytes()).hexdigest());assert (source/'src/cd/cdintf.c').read_text()==original
save(out/'build.json',report);save(ROOT/'verification/BIWN-TOC-origin-build-current.json',report);print(json.dumps(report),flush=True)
