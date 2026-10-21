"""Build a separately hashed CD repeated-seek experiment; pinned source untouched."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')

def main():
    source=ROOT/'tools/virtualjaguar-runtime-source'
    out=ROOT/'verification/BIWN-reseek-diagnostic-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    build=out/'source';shutil.copytree(source,build,symlinks=True,ignore=shutil.ignore_patterns('.git','*.o','*.dylib','*.so','*.dll','private'))
    original=(source/'src/cd/cdrom.c').read_text();text=original
    needle='static bool haveCDGoodness;';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n\n/* Explicit test-only input. Default preserves the pinned seek shortcut. */\nstatic bool biwnDiagnosticRepeatSeek = false;\nvoid BIWNDiagnosticRepeatSeek(uint32_t enabled)\n{\n   biwnDiagnosticRepeatSeek = (enabled != 0);\n}\n')
    needle='seekRedundant = (cdPlaying && newBlock == block && seekDelay <= 0 &&';assert text.count(needle)==1
    text=text.replace(needle,'seekRedundant = (!biwnDiagnosticRepeatSeek && cdPlaying && newBlock == block && seekDelay <= 0 &&')
    (build/'src/cd/cdrom.c').write_text(text)
    exports=build/'exports-test.list';exports.write_text(exports.read_text()+'\n_BIWNDiagnosticRepeatSeek\n')
    version_map=build/'link-test.T';version_map.write_text(version_map.read_text().replace('global:','global:\n    BIWNDiagnosticRepeatSeek;',1))
    report=dict(status='building',directory=str(out),source_directory=str(source),diagnostic_source=str(build),original_cdrom_sha256=hashlib.sha256(original.encode()).hexdigest(),diagnostic_cdrom_sha256=hashlib.sha256(text.encode()).hexdigest(),scope='Test-only runtime switch disables repeated-seek shortcut. Default disabled. Original source/archive and pinned core unchanged. No header/result/payload injection; no hardware behavior claim.',compiler_command=['make','-j8','TEST_EXPORTS=1'],new_hardware_rule=False)
    save(out/'build.json',report);print(out,flush=True)
    env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'}
    try:
        lint=subprocess.run(['bash','scripts/c89-lint.sh','src/cd/cdrom.c'],cwd=build,env=env,capture_output=True,text=True)
        (out/'lint.log').write_text(lint.stdout+lint.stderr);assert lint.returncode==0
        with(out/'compiler.log').open('w')as log:result=subprocess.run(report['compiler_command'],cwd=build,env=env,stdout=log,stderr=subprocess.STDOUT)
        assert result.returncode==0
        core=build/'virtualjaguar_libretro.dylib';assert core.exists()
        report.update(status='terminal_built_tests_pending',core_path=str(core),core_sha256=hashlib.sha256(core.read_bytes()).hexdigest())
        assert (source/'src/cd/cdrom.c').read_text()==original
        save(out/'build.json',report);save(ROOT/'verification/BIWN-reseek-diagnostic-build-current.json',report)
        print(json.dumps(dict(status=report['status'],core=str(core))),flush=True)
    except Exception as e:
        report.update(status='terminal_failed',error=repr(e));save(out/'build.json',report);raise

if __name__=='__main__':main()
