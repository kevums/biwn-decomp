"""Default-off diagnostic IRQ ownership handoff; preserve prior core/source."""
import pathlib,json,hashlib,shutil,subprocess,os
from datetime import datetime,timezone
ROOT=pathlib.Path(__file__).resolve().parents[1]
base=json.loads((ROOT/'verification/BIWN-PC-observer-build-current.json').read_text());source=pathlib.Path(base['diagnostic_source'])
out=ROOT/'verification/BIWN-DSP-IRQ-forward-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);build=out/'source'
shutil.copytree(source,build,symlinks=True,ignore=shutil.ignore_patterns('.git','*.o','*.dylib','*.so','*.dll','private'))
p=build/'src/jerry/dsp.c';original=p.read_text();needle='void DSPSetIRQLine(int irqline, int state)';assert original.count(needle)==1
addition="""/* Diagnostic-only external processor owner. NULL preserves original IRQ path. */
typedef int (*BIWNDSPIRQOwner)(int, int);
static BIWNDSPIRQOwner biwnDSPIRQOwner = NULL;
void BIWNSetDSPIRQOwner(BIWNDSPIRQOwner owner)
{
   biwnDSPIRQOwner = owner;
}

"""
s=original.replace(needle,addition+needle,1);needle='uint32_t mask = (irqline < 5) ? (INT_LAT0 << irqline) : INT_LAT5;';assert s.count(needle)==1
s=s.replace(needle,needle+"""

   if (biwnDSPIRQOwner != NULL && biwnDSPIRQOwner(irqline, state))
      return;
""",1);p.write_text(s)
p=build/'exports-test.list';p.write_text(p.read_text()+'\n_BIWNSetDSPIRQOwner\n_GetTimeToNextEvent\n_HandleNextEvent\n_SubtractEventTimes\n_EventStateSave\n_JERRYI2SCallback\n_JERRYPIT1Callback\n_JERRYPIT2Callback\n_JERRYRescheduleI2S\n_JERRYResetPIT1\n_JERRYResetPIT2\n_RemoveCallback\n');p=build/'link-test.T';p.write_text(p.read_text().replace('global:','global:\n    BIWNSetDSPIRQOwner; GetTimeToNextEvent; HandleNextEvent; SubtractEventTimes; EventStateSave; JERRYI2SCallback; JERRYPIT1Callback; JERRYPIT2Callback; JERRYRescheduleI2S; JERRYResetPIT1; JERRYResetPIT2; RemoveCallback;',1))
env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'}
report=dict(directory=str(out),diagnostic_source=str(build),parent_source=str(source),parent_core_path=base['core_path'],parent_core_sha256=base['core_sha256'],status='building',scope='Default-NULL external diagnostic DSP IRQ owner. Nonzero callback return bypasses only original DSP IRQ state update; callback must maintain explicit C-owned DSP state. Hardware event handlers and original execution functions are unchanged. Not a global emulation/playability proof.')
(out/'build.json').write_text(json.dumps(report,indent=2)+'\n');print(out,flush=True)
for name,cmd in [('lint',['bash','scripts/c89-lint.sh','src/jerry/dsp.c']),('compiler',['make','-j8','TEST_EXPORTS=1'])]:
 with(out/(name+'.log')).open('w')as log:run=subprocess.run(cmd,cwd=build,env=env,stdout=log,stderr=subprocess.STDOUT)
 assert not run.returncode,name
core=build/'virtualjaguar_libretro.dylib';assert(source/'src/jerry/dsp.c').read_text()==original
report.update(status='built_diagnostic_IRQ_handoff_pending_checks',core_path=str(core),core_sha256=hashlib.sha256(core.read_bytes()).hexdigest(),DSP_source_sha256=hashlib.sha256((build/'src/jerry/dsp.c').read_bytes()).hexdigest())
(out/'build.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/BIWN-DSP-IRQ-forward-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(report['core_sha256'],flush=True)
