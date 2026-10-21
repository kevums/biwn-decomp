"""Default-NULL DSP observer in an isolated core copy; never edits the parent.

Observe main dispatch and inline branch delays. Idle-probe internal dispatch
is outside this observer's scope. No processor execution is delegated here.
"""
import hashlib,json,os,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    parent=ROOT/'verification/BIWN-regular-GPU-owner-build/20261016T035215.288859Z/source'
    out=ROOT/'verification/DSP-instruction-observer-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);copy=out/'source'
    shutil.copytree(parent,copy,symlinks=True,ignore=shutil.ignore_patterns('.git','*.o','*.dylib','*.so','*.dll','private'))
    path=copy/'src/jerry/dsp.c';old=path.read_text()
    needle='void DSPExec(int32_t cycles)';assert old.count(needle)==1
    addition='''/* Default-NULL diagnostic observer; does not own DSP execution.
 * hazards bit0: inline delay, bit1: late load armed, bit2: divide/store armed.
 * Idle probe's internal opcode dispatch is outside this callback's scope. */
typedef void (*BIWNDSPInstructionObserver)(uint32_t, uint16_t, uint32_t, uint32_t, uint32_t);
static BIWNDSPInstructionObserver biwnDSPInstructionObserver = NULL;
static uint64_t biwnDSPObservedInstructions = 0;
void BIWNSetDSPInstructionObserver(BIWNDSPInstructionObserver observer)
{
   biwnDSPInstructionObserver = observer;
   biwnDSPObservedInstructions = 0;
}
uint64_t BIWNDSPObservedInstructionCount(void)
{
   return biwnDSPObservedInstructions;
}
static void BIWNObserveDSPInstruction(uint32_t pc, uint16_t opcode, uint32_t hazards)
{
   if (biwnDSPInstructionObserver != NULL)
   {
      biwnDSPObservedInstructions++;
      biwnDSPInstructionObserver(pc, opcode, dspFlagsRetireDelay,
         dspPreStoreBank == dsp_reg_bank_0 ? 0u : 1u, hazards);
   }
}

'''
    # Forward declaration is needed by inline delay handlers below.
    source=old.replace(needle,addition+needle,1)
    marker='\t\tindex = opcode >> 10;\n\t\tdsp_opcode_first_parameter'
    assert source.count(marker)==1
    source=source.replace(marker,'\t\tBIWNObserveDSPInstruction(pcThis, opcode,\n\t\t   (ldxArmed != NULL ? 2u : 0u) | (divArmed != NULL ? 4u : 0u));\n'+marker,1)
    marker='\t\tds_index = ds_opcode >> 10;'
    assert source.count(marker)==2
    source=source.replace(marker,'\t\tBIWNObserveDSPInstruction(dsp_pc, ds_opcode, 1u);\n'+marker)
    path.write_text(source)
    for name,symbols in [('exports-test.list','\n_BIWNSetDSPInstructionObserver\n_BIWNDSPObservedInstructionCount\n'),('link-test.T','')]:
        p=copy/name
        if name=='exports-test.list':p.write_text(p.read_text()+symbols)
        else:p.write_text(p.read_text().replace('global:','global:\n    BIWNSetDSPInstructionObserver; BIWNDSPObservedInstructionCount;',1))
    env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'}
    report={'status':'building_observer_no_execution_owner','directory':str(out),'source':str(copy),'parent_source':str(parent),'parent_core_sha256':hashlib.sha256((parent/'virtualjaguar_libretro.dylib').read_bytes()).hexdigest(),'scope':'DefaultNULL observer at main DSP dispatch and inline jump/jr delays. No execution delegation or idle-probe coverage claim.'}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out,flush=True)
    for name,cmd in [('C89-lint',['bash','scripts/c89-lint.sh','src/jerry/dsp.c']),('compiler',['make','-j8','TEST_EXPORTS=1'])]:
        with (out/(name+'.log')).open('w')as log:result=subprocess.run(cmd,cwd=copy,env=env,stdout=log,stderr=subprocess.STDOUT)
        assert result.returncode==0,(name,str(out))
    assert (parent/'src/jerry/dsp.c').read_text()==old
    report.update(status='compiled_pending_inertness_audio_and_core_tests',core_path=str(copy/'virtualjaguar_libretro.dylib'),core_sha256=hashlib.sha256((copy/'virtualjaguar_libretro.dylib').read_bytes()).hexdigest())
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/DSP-observer-experimental-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],flush=True)
if __name__=='__main__':main()
