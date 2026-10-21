"""Isolated default-NULL DSP instruction owner and logical-state commit ABI.

The writer preserves pipeline/retirement state instead of using DSPStateLoad.
Original code remains the reference when the owner returns zero.
"""
import hashlib,json,os,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    prior=json.loads((ROOT/'verification/DSP-observer-experimental-candidate.json').read_text());parent=Path(prior['source'])
    out=ROOT/'verification/DSP-instruction-owner-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);copy=out/'source'
    shutil.copytree(parent,copy,symlinks=True,ignore=shutil.ignore_patterns('.git','*.o','*.dylib','*.so','*.dll','private'))
    path=copy/'src/jerry/dsp.c';old=path.read_text();marker='typedef void (*BIWNDSPInstructionObserver)'
    addition='''/* Default-NULL external owner. Positive return is one outer instruction
 * plus its optional mandatory inline delay (1 or 2 source instructions).
 * Callback commits logical DSP state and final operand indices. Hardware
 * IRQ recognition and D_FLAGS retirement remain in DSPExec. */
typedef int (*BIWNDSPInstructionOwner)(uint32_t, uint16_t, uint32_t);
static BIWNDSPInstructionOwner biwnDSPInstructionOwner = NULL;
static uint64_t biwnDSPOwnedInstructions, biwnDSPOriginalInstructions, biwnDSPRejectedInstructions;
void BIWNSetDSPInstructionOwner(BIWNDSPInstructionOwner owner)
{
   biwnDSPInstructionOwner = owner;
   biwnDSPOwnedInstructions = biwnDSPOriginalInstructions = biwnDSPRejectedInstructions = 0;
}
uint64_t BIWNDSPOwnedInstructionCount(void) { return biwnDSPOwnedInstructions; }
uint64_t BIWNDSPOriginalInstructionCount(void) { return biwnDSPOriginalInstructions; }
uint64_t BIWNDSPRejectedInstructionCount(void) { return biwnDSPRejectedInstructions; }
void BIWNDSPSetLastOperands(uint32_t first, uint32_t second)
{
   dsp_opcode_first_parameter = first;
   dsp_opcode_second_parameter = second;
}

'''
    assert old.count(marker)==1;source=old.replace(marker,addition+marker,1)
    # Reject ownership when an old interpreted load/store hazard is active.
    marker='\t\tindex = opcode >> 10;\n\t\tdsp_opcode_first_parameter'
    owner='''\t\tif (biwnDSPInstructionOwner != NULL)
\t\t{
\t\t\tuint32_t unsupported = (dsp_reg != dsp_reg_bank_0 ? 1u : 0u)
\t\t\t   | (ldxArmed != NULL ? 2u : 0u) | (divArmed != NULL ? 4u : 0u)
\t\t\t   | (dspFlagsRetireDelay && dspPreStoreBank != dsp_reg_bank_0 ? 8u : 0u);
\t\t\tint claimed = biwnDSPInstructionOwner(pcThis, opcode, unsupported);
\t\t\tif (claimed < 0 || claimed > 2)
\t\t\t{
\t\t\t\tbiwnDSPRejectedInstructions++;
\t\t\t\tcycles = 0;
\t\t\t\tbreak;
\t\t\t}
\t\t\tif (claimed > 0)
\t\t\t{
\t\t\t\tbiwnDSPOwnedInstructions += (uint32_t)claimed;
\t\t\t\tdsp_exec_opcode_count += (uint32_t)claimed;
\t\t\t\tcycles -= dsp_opcode_cycles[opcode >> 10];
\t\t\t\tif (claimed == 2) dspFlagsRetireDelay = 0;
\t\t\t\telse if (dspFlagsRetireDelay) dspFlagsRetireDelay--;
\t\t\t\tcontinue;
\t\t\t}
\t\t}
\t\tbiwnDSPOriginalInstructions++;
'''
    assert source.count(marker)==1;source=source.replace(marker,owner+marker,1)
    marker='\t\tds_index = ds_opcode >> 10;';assert source.count(marker)==2;source=source.replace(marker,'\t\tbiwnDSPOriginalInstructions++;\n'+marker)
    # The affine probe calls interpreted opcode helpers internally; keep
    # ownership counts honest by declining that optimization in owned mode.
    marker='\twhile ((cycles > 0 || ldxArmed || divArmed) && DSP_RUNNING)';assert source.count(marker)==1
    source=source.replace(marker,'\tif (biwnDSPInstructionOwner != NULL) idleSkipActive = 0;\n'+marker)
    start=source.index('   STATE_LOAD_BUF(buf, dsp_ram_8',source.index('size_t DSPStateLoad('));end=source.index('   /* The state format carries',start)
    loads=source[start:end]
    writer='''
/* Commit logical fields only. Delayed flags retirement, pre-store bank,
 * pipeline, in-exec/release state and IRQ-private fields remain untouched. */
size_t BIWNDSPWriteLogicalState(const uint8_t *buf)
{
   const uint8_t *start = buf;
   uint8_t active_bank;
'''+loads+'''   return (size_t)(buf - start);
}
'''
    source+=writer;path.write_text(source)
    symbols=['BIWNSetDSPInstructionOwner','BIWNDSPOwnedInstructionCount','BIWNDSPOriginalInstructionCount','BIWNDSPRejectedInstructionCount','BIWNDSPSetLastOperands','BIWNDSPWriteLogicalState']
    p=copy/'exports-test.list';p.write_text(p.read_text()+'\n'+'\n'.join('_'+s for s in symbols)+'\n');p=copy/'link-test.T';p.write_text(p.read_text().replace('global:','global:\n    '+'; '.join(symbols)+';',1))
    report={'status':'building_default_NULL_DSP_owner','directory':str(out),'source':str(copy),'parent_source':str(parent),'scope':'Diagnostic owner; NULL preserves original dispatch. Logical writer preserves private retirement fields. Active ownership declines idle-probe internal interpretation. Not DSP/audio proof.'};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out,flush=True)
    env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'}
    for name,cmd in [('C89-lint',['bash','scripts/c89-lint.sh','src/jerry/dsp.c']),('compiler',['make','-j8','TEST_EXPORTS=1'])]:
        with (out/(name+'.log')).open('w')as log:result=subprocess.run(cmd,cwd=copy,env=env,stdout=log,stderr=subprocess.STDOUT)
        assert result.returncode==0,(name,str(out))
    assert (parent/'src/jerry/dsp.c').read_text()==old
    report.update(status='compiled_pending_default_inertness_core_audio_tests_and_owned_DSP_comparison',core_path=str(copy/'virtualjaguar_libretro.dylib'),core_sha256=hashlib.sha256((copy/'virtualjaguar_libretro.dylib').read_bytes()).hexdigest())
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/DSP-owner-experimental-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],flush=True)
if __name__=='__main__':main()
