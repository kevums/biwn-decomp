"""Default-NULL diagnostic callback around OP-requested GPU execution."""
from pathlib import Path
from datetime import datetime,timezone
import json,shutil,subprocess,os,hashlib
ROOT=Path(__file__).resolve().parents[1]
def main():
 prior=json.loads((ROOT/'verification/BIWN-CPU-IRQ-state-export-candidate.json').read_text());source=Path(prior['core_path']).parent;out=ROOT/'verification/BIWN-OP-GPU-owner-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);build=out/'source';shutil.copytree(source,build,symlinks=True,ignore=shutil.ignore_patterns('.git','*.o','*.dylib','*.so','*.dll','private'))
 p=build/'src/tom/op.c';original=p.read_text();needle='// Private function prototypes';assert original.count(needle)==1
 addition='''/* Diagnostic-only OP GPU executor. NULL retains the original path.
 * Phase0 may return nonzero after executing the requested source slice;
 * phase1 observes completion without executing another slice. */
typedef int (*BIWNOPGPUExecOwner)(int, int32_t);
static BIWNOPGPUExecOwner biwnOPGPUExecOwner = NULL;
void BIWNSetOPGPUExecOwner(BIWNOPGPUExecOwner owner)
{
   biwnOPGPUExecOwner = owner;
}

'''
 text=original.replace(needle,addition+needle,1);needle='                  GPUExec(OP_GPU_RELEASE_STEP_CYCLES);';assert text.count(needle)==1;text=text.replace(needle,'''                  if (biwnOPGPUExecOwner == NULL
                        || !biwnOPGPUExecOwner(0, OP_GPU_RELEASE_STEP_CYCLES))
                     GPUExec(OP_GPU_RELEASE_STEP_CYCLES);
                  if (biwnOPGPUExecOwner != NULL)
                     biwnOPGPUExecOwner(1, OP_GPU_RELEASE_STEP_CYCLES);''',1);p.write_text(text)
 for name in ['exports-test.list','link-test.T']:
  p=build/name;text=p.read_text();text=text+'\n_BIWNSetOPGPUExecOwner\n'if name.endswith('.list')else text.replace('global:','global:\n    BIWNSetOPGPUExecOwner;',1);p.write_text(text)
 report=dict(status='building',directory=str(out),diagnostic_source=str(build),parent_core=prior['core_path'],original_source_sha256=hashlib.sha256(original.encode()).hexdigest(),scope='DefaultNULL preserves original OP/GPU execution. Optional diagnostic before/after callback delegates only OP GPU slices; not new emulation timing or physical validation.')
 (out/'build.json').write_text(json.dumps(report,indent=2)+'\n');print(out,flush=True);env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'}
 for label,cmd in [('lint',['bash','scripts/c89-lint.sh','src/tom/op.c']),('compiler',['make','-j8','TEST_EXPORTS=1']),('suite',['make','-j8','TEST_EXPORTS=1','test'])]:
  with(out/(label+'.log')).open('w')as log:result=subprocess.run(cmd,cwd=build,env=env,stdout=log,stderr=subprocess.STDOUT)
  report[label+'_exit_code']=result.returncode;(out/'build.json').write_text(json.dumps(report,indent=2)+'\n');assert result.returncode==0,label
 core=build/'virtualjaguar_libretro.dylib';report.update(status='built_OP_GPU_owner_default_NULL_suite_pass',core_path=str(core),core_sha256=hashlib.sha256(core.read_bytes()).hexdigest());(out/'build.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/BIWN-OP-GPU-owner-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],flush=True)
if __name__=='__main__':main()
