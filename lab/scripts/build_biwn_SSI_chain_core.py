"""Opt-in diagnostic single SSI chain on real serial-clock programming writes."""
import pathlib,json,hashlib,shutil,subprocess,os
from datetime import datetime,timezone
ROOT=pathlib.Path(__file__).resolve().parents[1]
base=json.loads((ROOT/'verification/BIWN-DSP-IRQ-forward-candidate.json').read_text());source=pathlib.Path(base['diagnostic_source']);out=ROOT/'verification/BIWN-SSI-chain-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);build=out/'source'
shutil.copytree(source,build,symlinks=True,ignore=shutil.ignore_patterns('.git','*.o','*.dylib','*.so','*.dll','private'))
p=build/'src/jerry/jerry.c';original=p.read_text();needle='void JERRYRescheduleI2S(void)';assert original.count(needle)==1
addition="""/* Opt-in diagnostic cleanup on source SCLK programming; never at state load. */
static uint32_t biwnSSISingleChain = 0;
static uint32_t biwnSSISourceReschedules = 0;
void BIWNSetSSISingleChain(uint32_t enabled)
{
   biwnSSISingleChain = enabled ? 1 : 0;
   biwnSSISourceReschedules = 0;
}
uint32_t BIWNGetSSISourceReschedules(void)
{
   return biwnSSISourceReschedules;
}

"""
s=original.replace(needle,addition+needle,1);needle='void JERRYRescheduleI2S(void)\n{\n   double usecs;';assert s.count(needle)==1
s=s.replace(needle,needle+"""
   unsigned i;

   if (biwnSSISingleChain)
   {
      /* RemoveCallback removes only one match; the held diagnostic export
       * may contain multiple prior chains. Bound by event-list capacity. */
      for (i = 0; i < 32; i++)
         RemoveCallback(JERRYI2SCallback);
      biwnSSISourceReschedules++;
   }
""",1);p.write_text(s)
for filename in ['exports-test.list','link-test.T']:
 p=build/filename
 if filename=='exports-test.list':p.write_text(p.read_text()+'\n_BIWNSetSSISingleChain\n_BIWNGetSSISourceReschedules\n')
 else:p.write_text(p.read_text().replace('global:','global:\n    BIWNSetSSISingleChain; BIWNGetSSISourceReschedules;',1))
env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'}
report=dict(directory=str(out),diagnostic_source=str(build),parent_source=str(source),parent_core_path=base['core_path'],parent_core_sha256=base['core_sha256'],status='building',default_enabled=False,scope='Opt-in diagnostic single SSI chain only when source SCLK writes call existing JERRYRescheduleI2S. No initial state/queue rebuild at restore. No changed clock formula, IRQ code, waveform, device registers or C game code. External flag is not serialized and must be explicitly reattached; not a physical-timing or normal-boot proof.')
(out/'build.json').write_text(json.dumps(report,indent=2)+'\n');print(out,flush=True)
for name,cmd in [('lint',['bash','scripts/c89-lint.sh','src/jerry/jerry.c']),('compiler',['make','-j8','TEST_EXPORTS=1'])]:
 with(out/(name+'.log')).open('w')as log:run=subprocess.run(cmd,cwd=build,env=env,stdout=log,stderr=subprocess.STDOUT)
 assert not run.returncode,name
core=build/'virtualjaguar_libretro.dylib';assert(source/'src/jerry/jerry.c').read_text()==original
report.update(status='built_opt_in_SSI_chain_pending_source_checks',core_path=str(core),core_sha256=hashlib.sha256(core.read_bytes()).hexdigest(),JERRY_source_sha256=hashlib.sha256((build/'src/jerry/jerry.c').read_bytes()).hexdigest())
(out/'build.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/BIWN-SSI-chain-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(report['core_sha256'],flush=True)
