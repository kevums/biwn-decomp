"""Default-off IRQ-entry handoff in an isolated copy; existing cores untouched."""
import hashlib,json,os,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    parent=json.loads((ROOT/'verification/DSP-music-context-experimental-candidate.json').read_text())
    source=Path(parent['source']);out=ROOT/'verification/CPU-IRQ-owner-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    build=out/'source';shutil.copytree(source,build,symlinks=True,ignore=shutil.ignore_patterns('.git','*.o','*.dylib','*.so','*.dll','private'))
    path=build/'src/m68000/m68kinterface.c';original=path.read_text()
    needle='// Service an interrupt request and start exception processing\nvoid m68ki_exception_interrupt(uint32_t intLevel)'
    assert original.count(needle)==1
    addition='''/* Diagnostic default-off source IRQ-entry ownership. */
typedef int (*BIWNCPUIRQOwner)(uint32_t, uint32_t);
static BIWNCPUIRQOwner biwnCPUIRQOwner = NULL;
static uint64_t biwnCPUIRQOwned = 0, biwnCPUIRQOriginal = 0, biwnCPUIRQRejected = 0;
void BIWNSetCPUIRQOwner(BIWNCPUIRQOwner owner)
{
   biwnCPUIRQOwner = owner;
   biwnCPUIRQOwned = biwnCPUIRQOriginal = biwnCPUIRQRejected = 0;
}
uint64_t BIWNCPUIRQOwnedCount(void) { return biwnCPUIRQOwned; }
uint64_t BIWNCPUIRQOriginalCount(void) { return biwnCPUIRQOriginal; }
uint64_t BIWNCPUIRQRejectedCount(void) { return biwnCPUIRQRejected; }
/* Commit only the caller-owned exception-entry effects. ACK/queue machinery,
 * diagnostics and the pinned cycle charge remain core host services. */
void BIWNCommitCPUIRQEntry(const struct BIWNCPUState *state, uint32_t level)
{
   memcpy(regs.regs, state->registers, sizeof(state->registers));
   regs.usp = state->usp;
   regs.s = 1;
   regs.intmask = level;
   m68k_setpc(state->pc);
   M68KPrefetchFlush();
   regs.interruptCycles += 56;
}

'''
    text=original.replace(needle,addition+needle,1)
    needle='\t// Start exception processing\n\tsr = m68ki_init_exception();'
    assert text.count(needle)==1
    text=text.replace(needle,'''   if (biwnCPUIRQOwner != NULL)
   {
      if (biwnCPUIRQOwner(intLevel, vector) == 1)
         biwnCPUIRQOwned++;
      else
         biwnCPUIRQRejected++;
      return;
   }
   biwnCPUIRQOriginal++;

'''+needle,1);path.write_text(text)
    exports=['BIWNSetCPUIRQOwner','BIWNCPUIRQOwnedCount','BIWNCPUIRQOriginalCount','BIWNCPUIRQRejectedCount','BIWNCommitCPUIRQEntry','m68ki_exception_interrupt']
    p=build/'exports-test.list';p.write_text(p.read_text()+''.join('\n_'+name for name in exports)+'\n')
    p=build/'link-test.T';p.write_text(p.read_text().replace('global:','global:\n    '+'; '.join(exports)+';',1))
    report=dict(status='building',directory=str(out),source=str(build),parent_core=parent['core_path'],parent_core_sha256=parent['core_sha256'],default_owner_NULL=True,whole_game_complete=False,scope='Isolated diagnostic IRQ entry handoff after original device ACK/vector resolution. No timing-model or device change; pinned56-cycle charge retained only for compatibility. No hardware accuracy/standalone proof.')
    env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'}
    for label,cmd in [('C89-lint',['bash','scripts/c89-lint.sh','src/m68000/m68kinterface.c']),('compiler',['make','-j8','TEST_EXPORTS=1']),('core-tests',['make','TEST_EXPORTS=1','test'])]:
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        with (out/(label+'.log')).open('w')as log:run=subprocess.run(cmd,cwd=build,env=env,stdout=log,stderr=subprocess.STDOUT)
        report[label+'_exit']=run.returncode;assert run.returncode==0,(label,out)
    assert (source/'src/m68000/m68kinterface.c').read_text()==original
    core=build/'virtualjaguar_libretro.dylib';report.update(status='compiled_tested_pending_inertness_and_ownership',core_path=str(core),core_sha256=hashlib.sha256(core.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/CPU-IRQ-owner-experimental-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':main()
