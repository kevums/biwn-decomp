"""Retest original CPU/source acquisition for all groups with repaired mode3 table.

Same real-disc provider and guards as the prior partial14case matrix. Only
the supplied mode3 table changes16 to13; original/source algorithms remain.
"""
import os,signal,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_native_deck_fresh_restore_v1 as common
ROOT=common.ROOT;V=ROOT/'verification';read=common.read;save=common.save;sha=common.sha
def main():
    out=V/'frame-acquire-selector13-qualification'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    template=ROOT/'scripts/check_frame_acquire_real_disc.py';text=template.read_text()
    text=text.replace('frame-acquire-real-disc','frame-acquire-selector13-disc')
    anchor=";manifest,snapshot=native.prior.prior.render.assets();assert atlas[0x1ac68:0x1ae56]"
    assert text.count(anchor)==1
    text=text.replace(anchor,";atlas=bytearray(atlas);assert atlas[0x464a6:0x464a8]==bytes.fromhex('0010');atlas[0x464a6:0x464a8]=bytes.fromhex('000d');atlas=bytes(atlas)"+anchor)
    anchor=" report=dict(status='seven_real_disc_loads_and_reuse_verified_two_groups_unresolved'";assert text.count(anchor)==1
    text=text.replace(anchor," assert len(rows)==18 and not unresolved\n report=dict(status='nine_repaired_selector13_disc_loads_and_reuse_verified'")
    runner=out/'matrix-as-run.py';runner.write_text(text)
    state=dict(status='running_original_CPU_source_real_disc_selector13_matrix',directory=str(out),pid=os.getpid(),source_sha256={str(p):sha(p)for p in [Path(__file__),template,runner]},new_training=False,whole_game_complete=False,native_disc_changed=False)
    pointer=V/'frame-acquire-selector13-qualified-current.json'
    def mark():save(out/'protocol.json',state);save(pointer,state)
    child=None;mark()
    try:
        with(out/'matrix.log').open('w')as log:
            child=subprocess.Popen([str(ROOT/'.venv/bin/python3.12'),'-u',str(runner)],stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONPATH':str(ROOT/'scripts')},start_new_session=True);state['child_pid']=child.pid;mark()
            try:code=child.wait(timeout=900)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait();raise
        state['child_pid']=None;assert code==0,(out/'matrix.log').read_text()[-4000:]
        report=read(V/'frame-acquire-selector13-disc-current.json');assert report['cases']==18 and report['cold_loads']==9 and report['unresolved_group_count']==0
        report['legacy_template_scope_replaced']=report['scope']
        report['scope']='Original pinned Jaguar CPU versus accepted portable source acquisition with original loader/copy/CD-offset code, real normalized internal disc bytes and existing BIOS303C/3042 plus DF60 completion adapters. Only supplied mode3 frame table changes16 to13, so mode3 group requests are0/13/26. All9coldloads and9cache reuses match returnedD0,declaredvisibleRAM,helper/disc event histories and checkedhardware. Payload bytes independently match preserved disc markers. No actual compiled native caller, fresh natural input, IRQ timing or physicalconsole claim; those require separate gameplay evidence.'
        reviewed=Path(report['directory'])/'reviewed-report.json';save(reviewed,report)
        state.update(status='terminal_original_CPU_source_selector13_all_disc_groups_match',proof_directory=report['directory'],reviewed_report=str(reviewed),reviewed_report_sha256=sha(reviewed),cases=18,cold_loads=9,cached_reuses=9,payload_bytes=report['payload_bytes'],scope=report['scope']);mark();print(state['status'],flush=True)
    except BaseException as error:state.update(status='terminal_failed',error=repr(error),child_pid=None if child is None or child.poll()is not None else child.pid);mark();raise
if __name__=='__main__':main()
