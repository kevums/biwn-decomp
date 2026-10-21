"""Error contracts exercised on actual sparse-codebook/delta-frame commands."""
import ctypes as c,json
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_movie_sequence_GPU as sequence
from check_biwn_movie_GPU import state_from_raw,logical,Bus,OBS
ROOT=sequence.ROOT;save=sequence.save;sha=sequence.sha

def main():
    proof=json.loads((ROOT/'verification/BIWN-movie-sequence-GPU-C.json').read_text());capture=Path(proof['directory']);witnesses=json.loads((capture/'new-code-witnesses.json').read_text())
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);setup=json.loads((session/'media-setup-fullCPU-generation.json').read_text());setup_proof=json.loads((ROOT/'verification/biwn-media-setup-cpu-checks.json').read_text())
    runtime=sequence.media.Runtime(Path(setup_proof['directory'])/'libmedia-setup.dylib',setup['instructions_decoded'])
    out=ROOT/'verification/BIWN-movie-sequence-GPU-guards'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);v=sequence.Verifier(runtime,runtime.core,out);rows=[]
    root=capture/'new-code-witnesses'
    def execute(options,frame=False):
        w=next(x for x in witnesses if x['command']%2==(1 if frame else 0));stem=w['stem']
        v.restore((root/f'{stem}-before-machine.bin').read_bytes());s=state_from_raw((root/f'{stem}-before-GPU.bin').read_bytes());bus=Bus.from_buffer_copy(bytes(v.bus));v.trace=__import__('hashlib').sha256();v.blocks=0;v.fail=options.get('fail')
        if 'missing' in options:setattr(bus,options['missing'],type(getattr(bus,options['missing']))())
        if options.get('bad_PC'):s.pc=0
        if options.get('bad_bank'):s.active_bank=1
        if 'bad_flag' in options:setattr(s,options['bad_flag'],2)
        if options.get('no_trace'):bus.observe_PC=OBS()
        before=bytes(s);count=v.counter.value
        status=v.run(None if options.get('null_bus') else c.byref(bus),None if options.get('null_state') else c.byref(s),options.get('budget',1000000))
        assert v.counter.value==count
        return status,s,bytes(s)==before,stem
    try:
        for options in [dict(missing=n) for n in ['read8','read16','read32','write32']]+[dict(null_bus=True),dict(null_state=True),dict(budget=0),dict(bad_bank=True)]+[dict(bad_flag=k) for k in ['z','c','n']]:
            status,_,unchanged,stem=execute(options);assert status==1 and unchanged;rows.append(dict(options=options,status=status,witness=stem))
        for options,expected in [(dict(bad_PC=True),3),(dict(budget=1),4),(dict(fail=('read',1)),2),(dict(fail=('read',2)),2),(dict(fail=('read',4)),2),(dict(fail=('write',4)),2)]:
            status,_,unchanged,stem=execute(options,frame=options.get('fail') in [('read',1),('read',4)]);assert status==expected and unchanged,(options,status,unchanged);rows.append(dict(options=options,status=status,witness=stem))
        status,s,_,stem=execute(dict(no_trace=True));expected=(root/f'{stem}-after-GPU.bin').read_bytes();assert status==0 and logical(s)==expected[:4396];rows.append(dict(optional_trace=True,status=0,witness=stem))
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='sparse_book_delta_frame_C_GPU_error_contract_checked',directory=str(out),host_guards=len(rows),source_sha256=proof['C_GPU_checks']['source_sha256'],script_sha256=sha(Path(__file__).read_bytes()),rows=rows,original_GPU_instructions_on_C_side=0,whole_game_complete=False,new_published_components=0)
        save(out/'report.json',report);save(ROOT/'verification/BIWN-movie-sequence-GPU-guards.json',report);save(out/'status.json',dict(status='terminal_pass'));print(json.dumps(dict(directory=str(out),guards=len(rows))))
    except Exception as e:save(out/'status.json',dict(status='terminal_failed',error=repr(e)));raise
    finally:runtime.oracle.close()

if __name__=='__main__':main()
