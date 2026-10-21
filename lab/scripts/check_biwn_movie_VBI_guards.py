"""VBI event host errors, exact source frame layout and masked IRQ behavior."""
import ctypes as c,json,struct
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_full_movie_caller as caller
media=caller.media;ROOT=caller.ROOT;save=caller.save

def main():
    proof=json.loads((ROOT/'verification/BIWN-full-movie-caller.json').read_text());lib=c.CDLL(str(Path(proof['directory'])/'libfull-movie.dylib'));fn=lib.biwn_movie_VBI_event;fn.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU)];fn.restype=c.c_int;cases=[]
    def check(options,expected):
        memory=bytearray(0x200000);memory[0x100:0x104]=(0 if options.get('bad_vector') else 0xe7d4).to_bytes(4,'big');writes=[]
        def read(_,a,v):
            if options.get('fail_read'):return 1
            v[0]=int.from_bytes(memory[a:a+4],'big');return 0
        def write(w):
            def cb(_,a,v):
                if options.get('fail_write'+str(w)):return 1
                memory[a:a+w]=v.to_bytes(w,'big');writes.append([a,w,v]);return 0
            return cb
        callbacks=[media.scheduler.cleanup.world.R8(),media.scheduler.cleanup.world.R16(),media.scheduler.cleanup.world.R32(read),media.scheduler.cleanup.world.W16(write(2)),media.scheduler.cleanup.world.W32(write(4))]
        if 'missing' in options:callbacks[options['missing']]=type(callbacks[options['missing']])()
        bus=media.Bus(*callbacks,media.scheduler.cleanup.world.CALL(),None,0);cpu=media.CPU();cpu.pc=0 if options.get('bad_pc') else 0xd4a8;cpu.sr=0x2704 if options.get('masked') else 0x704 if options.get('user') else 0x2004;cpu.registers[15]=cpu.ssp=0x1fffb4;cpu.usp=0x1fe000;before=bytes(cpu)
        status=fn(None if options.get('null_bus') else c.byref(bus),None if options.get('null_cpu') else c.byref(cpu));assert status==expected,(options,status)
        if status or options.get('masked'):assert bytes(cpu)==before
        if not options:
            assert cpu.pc==0xe7d4 and cpu.sr==0x2204 and cpu.ssp==cpu.registers[15]==0x1fffae
            assert memory[0x1fffae:0x1fffb4]==struct.pack('>HI',0x2004,0xd4a8)
        cases.append(dict(options=options,status=status,state_unchanged=bytes(cpu)==before,writes=writes))
    for options in [dict(null_bus=True),dict(null_cpu=True)]+[dict(missing=i) for i in [2,3,4]]+[dict(bad_pc=True),dict(user=True)]:check(options,1)
    for options,expected in [(dict(fail_read=True),2),(dict(fail_write4=True),2),(dict(fail_write2=True),2),(dict(bad_vector=True),7),(dict(masked=True),0),({},0)]:check(options,expected)
    out=ROOT/'verification/BIWN-movie-VBI-guards'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);report=dict(status='typed_VBI_event_contracts_and_exact_sixbyte_frame_checked',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),checks=len(cases),cases=cases,source_sha256=proof['source_sha256']['biwn_movie_VBI_event.c'],whole_game_complete=False)
    save(out/'report.json',report);save(ROOT/'verification/BIWN-movie-VBI-guards.json',report);print(json.dumps(dict(directory=str(out),checks=len(cases))))
if __name__=='__main__':main()
