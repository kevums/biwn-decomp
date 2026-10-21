"""Default-off, one-shot CPU observation only; preserve parent source/core."""
import pathlib,json,hashlib,shutil,subprocess,os
from datetime import datetime,timezone
ROOT=pathlib.Path(__file__).resolve().parents[1];base=json.loads((ROOT/'verification/BIWN-TOC-origin-build-current.json').read_text());source=pathlib.Path(base['diagnostic_source']);out=ROOT/'verification/BIWN-PC-observer-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);build=out/'source';shutil.copytree(source,build,symlinks=True,ignore=shutil.ignore_patterns('.git','*.o','*.dylib','*.so','*.dll','private'))
p=build/'src/core/jaguar.c';original=p.read_text();needle='void M68KInstructionHook(void)';assert original.count(needle)==1
addition='''/* One-shot diagnostic observation. Default NULL; never changes machine state. */
typedef void (*BIWNCPUObserver)(uint32_t, uint32_t);
static BIWNCPUObserver biwnCPUObserver = NULL;
static uint32_t biwnCPUObserverPC = 0;
static uint32_t biwnCPUObserverPreviousPC = 0;
void BIWNArmCPUObserver(uint32_t pc, BIWNCPUObserver observer)
{
   biwnCPUObserverPC = pc;
   biwnCPUObserver = observer;
   biwnCPUObserverPreviousPC = 0;
}

'''
text=original.replace(needle,addition+needle,1);needle='   uint32_t m68kPC = regs.pc;';assert text.count(needle)==1
text=text.replace(needle,needle+'''
   if (biwnCPUObserver != NULL)
   {
      uint32_t previous = biwnCPUObserverPreviousPC;
      biwnCPUObserverPreviousPC = m68kPC;
      if (m68kPC == biwnCPUObserverPC)
      {
         BIWNCPUObserver observer = biwnCPUObserver;
         biwnCPUObserver = NULL;
         observer(previous, m68kPC);
      }
   }
''',1);p.write_text(text)
p=build/'exports-test.list';p.write_text(p.read_text()+'\n_BIWNArmCPUObserver\n');p=build/'link-test.T';p.write_text(p.read_text().replace('global:','global:\n    BIWNArmCPUObserver;',1));env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'}
report=dict(directory=str(out),source_directory=str(source),diagnostic_source=str(build),parent_core_sha256=base['core_sha256'],scope='One-shot CPU observer at selected PC; previous PC recorded. Default NULL, no PC/register/IRQ/memory writes or halt. Snapshot callback effects require paired verification.',status='building');(out/'build.json').write_text(json.dumps(report,indent=2)+'\n');print(out,flush=True)
for name,cmd in [('lint',['bash','scripts/c89-lint.sh','src/core/jaguar.c']),('compiler',['make','-j8','TEST_EXPORTS=1'])]:
 with(out/(name+'.log')).open('w')as log:r=subprocess.run(cmd,cwd=build,env=env,stdout=log,stderr=subprocess.STDOUT)
 assert r.returncode==0,name
core=build/'virtualjaguar_libretro.dylib';assert(source/'src/core/jaguar.c').read_text()==original;report.update(status='built_observer_pair_pending',core_path=str(core),core_sha256=hashlib.sha256(core.read_bytes()).hexdigest());(out/'build.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/BIWN-PC-observer-build-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['core_sha256'],flush=True)
