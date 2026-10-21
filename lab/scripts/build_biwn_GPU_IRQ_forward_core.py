"""Default-off GPU IRQ ownership hook for source firmware handoff tests."""
import pathlib,json,hashlib,shutil,subprocess,os
from datetime import datetime,timezone
ROOT=pathlib.Path(__file__).resolve().parents[1];base=json.loads((ROOT/'verification/BIWN-SSI-chain-candidate.json').read_text());source=pathlib.Path(base['diagnostic_source']);out=ROOT/'verification/BIWN-GPU-IRQ-forward-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);build=out/'source';shutil.copytree(source,build,symlinks=True,ignore=shutil.ignore_patterns('.git','*.o','*.dylib','*.so','*.dll','private'))
p=build/'src/tom/gpu.c';original=p.read_text();needle='void GPUSetIRQLine(int irqline, int state)';assert original.count(needle)==1
addition="""/* Diagnostic-only external processor owner. NULL preserves original IRQ path. */
typedef int (*BIWNGPUIRQOwner)(int, int);
static BIWNGPUIRQOwner biwnGPUIRQOwner = NULL;
void BIWNSetGPUIRQOwner(BIWNGPUIRQOwner owner)
{
   biwnGPUIRQOwner = owner;
}

"""
s=original.replace(needle,addition+needle,1);needle='uint32_t mask = 0x0040 << irqline;';assert s.count(needle)==1;s=s.replace(needle,needle+"""

   if (biwnGPUIRQOwner != NULL && biwnGPUIRQOwner(irqline, state))
      return;
""",1);p.write_text(s)
p=build/'exports-test.list';p.write_text(p.read_text()+'\n_BIWNSetGPUIRQOwner\n');p=build/'link-test.T';p.write_text(p.read_text().replace('global:','global:\n    BIWNSetGPUIRQOwner;',1));env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'}
report=dict(directory=str(out),diagnostic_source=str(build),parent_source=str(source),parent_core_path=base['core_path'],parent_core_sha256=base['core_sha256'],status='building',scope='DefaultNULL external GPU IRQ owner. Nonzero callback return delegates IRQ state to explicit C-owned GPU. No original GPU opcode execution or changed default IRQ/timing behavior. Diagnostic only; physical/global validation unproved.')
(out/'build.json').write_text(json.dumps(report,indent=2)+'\n');print(out,flush=True)
for name,cmd in [('lint',['bash','scripts/c89-lint.sh','src/tom/gpu.c']),('compiler',['make','-j8','TEST_EXPORTS=1'])]:
 with(out/(name+'.log')).open('w')as log:r=subprocess.run(cmd,cwd=build,env=env,stdout=log,stderr=subprocess.STDOUT)
 assert not r.returncode,name
core=build/'virtualjaguar_libretro.dylib';assert(source/'src/tom/gpu.c').read_text()==original;report.update(status='built_GPU_IRQ_handoff_pending_checks',core_path=str(core),core_sha256=hashlib.sha256(core.read_bytes()).hexdigest());(out/'build.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/BIWN-GPU-IRQ-forward-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(report['core_sha256'],flush=True)
