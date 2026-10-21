"""Native original versus source IRQ entry, including vector/stack aliasing."""
import ctypes as c
import argparse
import hashlib
import itertools
import json
import random
import os
import subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_media_setup_cpu as media
import biwn_CPU_IRQ_owner as owner
ROOT=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--core',type=Path);args=parser.parse_args()
    manifest=(dict(core_path=str(args.core.resolve()),core_sha256=hashlib.sha256(args.core.read_bytes()).hexdigest(),core_suite_pending=True)
              if args.core else json.loads((ROOT/'verification/CPU-IRQ-owner-experimental-candidate.json').read_text()))
    core_path=Path(manifest['core_path']);assert hashlib.sha256(core_path.read_bytes()).hexdigest()==manifest['core_sha256']
    oracle=media.scheduler.Native(diagnostic_core=core_path);runtime=media.Runtime.__new__(media.Runtime)
    runtime.oracle,runtime.device,runtime.core=oracle,oracle.device,oracle.lib;core=oracle.lib
    core.BIWNSetCPUIRQOwner.argtypes=[c.c_void_p];core.m68ki_exception_interrupt.argtypes=[c.c_uint32];core.m68ki_exception_interrupt.restype=None
    core.M68KStateSave.argtypes=[c.c_void_p];core.M68KStateSave.restype=c.c_size_t
    out=ROOT/'verification/CPU-IRQ-entry-checks'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    # Compile a fixture-only accessor against the actual pinned private layout.
    # Resetting deferred cycles is an explicit common input, not a product fix.
    fixture=out/'private_fixture.c'
    fixture.write_text('#include "'+str(core_path.parent/'src/m68000/cpudefs.h')+'"\nvoid biwn_fixture_irq_seed(struct regstruct *state,unsigned usp,unsigned isp){state->interruptCycles=0;state->usp=usp;state->isp=isp;}\n')
    fixture_library=out/'libprivate-fixture.dylib'
    subprocess.run(['clang','-dynamiclib','-std=c99',str(fixture),'-o',str(fixture_library)],check=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    fixture_fn=c.CDLL(str(fixture_library)).biwn_fixture_irq_seed;fixture_fn.argtypes=[c.c_void_p,c.c_uint32,c.c_uint32]
    private=c.addressof((c.c_uint8*1).in_dll(core,'regs'))
    rng=random.Random(0x68);rows=[]
    def run(memory,initial,level,source):
        core.BIWNSetCPUIRQOwner(None);runtime.device.seed(bytes(memory),0);runtime.seed_cpu(initial)
        # pulse_reset does not clear deferred interruptCycles. Restore the
        # same declared zero-cycle input instead of comparing different seeds.
        fixture_fn(private,initial.usp,initial.ssp)
        before=c.create_string_buffer(512);assert core.M68KStateSave(before)==148
        keep=owner.install(core,out)if source else None
        core.m68ki_exception_interrupt(level)
        cpu=media.scheduler.cpu_dict(runtime.cpu());raw=c.create_string_buffer(512);size=core.M68KStateSave(raw);assert size==148,size
        result=dict(CPU=cpu,private_CPU_state=raw.raw[:size],RAM=runtime.device.ram(),initial_private_CPU=before.raw[:148])
        if keep:
            stats=keep[3]();assert stats['core']==dict(Owned=1,Original=0,Rejected=0)and stats['source']['errors']==0
        core.BIWNSetCPUIRQOwner(None);return result
    try:
        for flags,supervisor,level,present,alias in itertools.product(range(32),[False,True],[1,2,7],[False,True],[False,True]):
            vector=64 if level==2 else 24+level
            memory=bytearray(0x200000);handler=0x19104 if present else 0x19120
            memory[vector*4:vector*4+4]=(0x19104 if present else 0).to_bytes(4,'big');memory[0x3c:0x40]=(0x19120).to_bytes(4,'big')
            initial=media.CPU();initial.registers[:]=[rng.getrandbits(32)for _ in range(16)];initial.pc=0x12340
            initial.sr=(0x2000 if supervisor else 0)|flags;initial.usp=0x180800;initial.ssp=(vector*4+4 if present else 0x40)if alias else 0x1e0000
            initial.registers[15]=initial.ssp if supervisor else initial.usp
            a=run(memory,initial,level,False);b=run(memory,initial,level,True)
            if a!=b:
                detail=dict(flags=flags,supervisor=supervisor,level=level,present=present,alias=alias,original_CPU=a['CPU'],source_CPU=b['CPU'],private_state_equal=a['private_CPU_state']==b['private_CPU_state'],RAM_equal=a['RAM']==b['RAM'],private_byte_differences=[dict(offset=i,original=x,source=y)for i,(x,y)in enumerate(zip(a['private_CPU_state'],b['private_CPU_state']))if x!=y])
                detail['initial_private_byte_differences']=[dict(offset=i,original=x,source=y)for i,(x,y)in enumerate(zip(a['initial_private_CPU'],b['initial_private_CPU']))if x!=y]
                (out/'mismatch.json').write_text(json.dumps(detail,indent=2)+'\n');raise AssertionError(out/'mismatch.json')
            assert a['CPU']['pc']==handler
            rows.append(dict(flags=flags,supervisor=supervisor,level=level,vector_present=present,vector_stack_alias=alias,CPU=b['CPU'],initial_private_state_sha256=hashlib.sha256(a['initial_private_CPU']).hexdigest(),private_state_sha256=hashlib.sha256(b['private_CPU_state']).hexdigest(),RAM_sha256=hashlib.sha256(b['RAM']).hexdigest()))
        (out/'cases.json').write_text(json.dumps(rows,indent=2)+'\n')
        assert hashlib.sha256(core_path.read_bytes()).hexdigest()==manifest['core_sha256']
        report=dict(status='native_original_and_source_IRQ_entry_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(rows),core=str(core_path),core_sha256=manifest['core_sha256'],core_suite_pending=manifest.get('core_suite_pending',False),all_public_CPU_full_private_CPU_and_main_RAM=True,coordinator_authored=True,local_model_authored=False,whole_game_complete=False,scope='Direct exception-entry calls after actual device ACK: all32CCR combinations,user/supervisor,levels1/2/7,initialized/uninitializedvector,normal/vector-aliasing supervisor stacks. FullpublicCPU/private148-byteCPUstate/2MBRAM exact original. IRQ selection/masking/event scheduling and full-game adoption excluded.')
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/CPU-IRQ-entry-checks-current.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
    finally:core.BIWNSetCPUIRQOwner(None);oracle.close()
if __name__=='__main__':main()
