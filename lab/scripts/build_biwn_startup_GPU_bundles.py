"""Clone source startup kernels into one-outer-instruction GPU bundles."""
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def replace_once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new)


def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    prior=json.loads((ROOT/'verification/movie-GPU-bundle-experimental-candidate.json').read_text())
    out=ROOT/'verification/startup-GPU-bundle-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    programs=list(prior['programs'])
    for name,stem,mapping_name,kind in [
        ('cold_boot','biwn_game_firstboot_GPU','game-firstboot-GPU-C-generation.json','firstboot'),
        ('main_boot','biwn_gpu_main_boot','main-GPU-boot-C-generation.json','movie_exit')]:
        source=ROOT/'projects/black-ice-white-noise/restoration'/(stem+'.c')
        body=source.read_text()
        original_hash=hashlib.sha256(body.encode()).hexdigest()
        mapping=json.loads((session/mapping_name).read_text())
        assert mapping['source_sha256'][stem+'.c']==original_hash
        body=replace_once(body,stem+'_run(',stem+'_bundle_run(')
        if kind=='firstboot':
            body=replace_once(body,'uint32_t budget,uint32_t stopPC)','uint32_t budget)')
            body=replace_once(body,'if(!pending&&s.pc==stopPC)','if(!pending)')
        else:
            body=replace_once(body,'if(s.pc==0xf031beu)','if(!pending)')
        body=replace_once(body,'while(budget--){','do{')
        marker='}}return '+('BIWN_GAME_FIRSTBOOT_GPU'if kind=='firstboot'else'BIWN_GPU_MAIN_BOOT')+'_WORK_LIMIT;}'
        body=replace_once(body,marker,'}}while(1);return '+('BIWN_GAME_FIRSTBOOT_GPU'if kind=='firstboot'else'BIWN_GPU_MAIN_BOOT')+'_WORK_LIMIT;}')
        target=out/(stem+'.c')
        target.write_text(body)
        header=ROOT/'projects/black-ice-white-noise/restoration'/(stem+'.h')
        (out/header.name).write_text(header.read_text())
        library=out/('lib'+name+'.dylib')
        command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(target),'-o',str(library)]
        result=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
        (out/(name+'-compiler.log')).write_text(result.stdout+result.stderr)
        assert result.returncode==0,result.stderr
        programs.append(dict(name=name,stem=stem,function=stem+'_bundle_run',kind=kind,
                             library=str(library),instructions_decoded=mapping['instructions_decoded'],
                             source_original=str(source),source_original_sha256=original_hash,
                             bundle_source_sha256=hashlib.sha256(body.encode()).hexdigest()))
    report=dict(status='compiled_pending_live_startup_comparison',directory=str(out),programs=programs,
                scope='Single outer instruction plus actual branch delay; original source kernels unchanged.',
                whole_game_complete=False,new_training=False)
    (ROOT/'verification/startup-GPU-bundles-experimental-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    print(out,flush=True)


if __name__=='__main__':
    main()
