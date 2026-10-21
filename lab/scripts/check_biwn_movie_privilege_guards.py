"""Source user STOP/IRQ event input failures, masked IRQ and retained writes."""
import ctypes as c,json
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_media_setup_cpu as media
ROOT=media.ROOT;save=media.save

def main():
    proof=json.loads((ROOT/'verification/BIWN-user-movie-STOP-C.json').read_text());lib=c.CDLL(str(Path(proof['directory'])/'libuser-STOP.dylib'));functions={name:getattr(lib,name) for name in ['biwn_movie_user_STOP_exception','biwn_movie_wait_GPU_interrupt','biwn_movie_user_VBI_event']}
    for f in functions.values():f.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU)];f.restype=c.c_int
    stop=lib.biwn_movie_privilege_STOP_event;stop.argtypes=[c.POINTER(media.CPU)];stop.restype=c.c_int;cases=[]
    def check(name,options,expected):
        memory=bytearray(0x200000);memory[0x20:0x24]=(0 if options.get('bad_vector') else 0xddfe).to_bytes(4,'big');memory[0x100:0x104]=(0 if options.get('bad_vector') else 0xe7d4).to_bytes(4,'big');writes=[]
        def read(_,a,v):
            if options.get('fail_read'):return 1
            v[0]=int.from_bytes(memory[a:a+4],'big');return 0
        def write(w):
            def cb(_,a,v):
                if options.get('fail_write'+str(w)):return 1
                memory[a:a+w]=v.to_bytes(w,'big');writes.append([a,w,v]);return 0
            return cb
        cb=[media.scheduler.cleanup.world.R8(),media.scheduler.cleanup.world.R16(),media.scheduler.cleanup.world.R32(read),media.scheduler.cleanup.world.W16(write(2)),media.scheduler.cleanup.world.W32(write(4))]
        if 'missing' in options:cb[options['missing']]=type(cb[options['missing']])()
        bus=media.Bus(*cb,media.scheduler.cleanup.world.CALL(),None,0);cpu=media.CPU();cpu.pc={'biwn_movie_user_STOP_exception':0x22a0e,'biwn_movie_wait_GPU_interrupt':0xde02,'biwn_movie_user_VBI_event':0xd4a8}[name];cpu.sr=0x2000 if name=='biwn_movie_wait_GPU_interrupt' else 0;cpu.usp=0x180000;cpu.ssp=0x200000;cpu.registers[15]=cpu.ssp if cpu.sr&0x2000 else cpu.usp
        if options.get('bad_PC'):cpu.pc=0
        if options.get('trace'):cpu.sr|=0x8000
        if options.get('bad_mode'):cpu.sr^=0x2000
        if options.get('masked'):cpu.sr|=0x700
        before=bytes(cpu);status=functions[name](None if options.get('null_bus') else c.byref(bus),None if options.get('null_CPU') else c.byref(cpu));assert status==expected,(name,options,status)
        if status or options.get('masked'):assert bytes(cpu)==before
        if not options:
            assert cpu.ssp==cpu.registers[15]==0x1ffffa and cpu.usp==0x180000
            assert memory[0x1ffffa:0x200000]==((0x2000 if name=='biwn_movie_wait_GPU_interrupt' else 0).to_bytes(2,'big')+({'biwn_movie_user_STOP_exception':0x22a0e,'biwn_movie_wait_GPU_interrupt':0xde02,'biwn_movie_user_VBI_event':0xd4a8}[name]).to_bytes(4,'big'))
        cases.append(dict(name=name,options=options,status=status,state_unchanged=bytes(cpu)==before,writes=writes))
    for name in functions:
        for options in [dict(null_bus=True),dict(null_CPU=True)]+[dict(missing=i) for i in [2,3,4]]+[dict(bad_PC=True),dict(trace=True)]:check(name,options,1)
        if name!='biwn_movie_user_VBI_event':check(name,dict(bad_mode=True),1)
        for options,expected in [(dict(fail_read=True),2),(dict(fail_write4=True),2),(dict(fail_write2=True),2),(dict(bad_vector=True),7),({},0)]:check(name,options,expected)
        if name!='biwn_movie_user_STOP_exception':check(name,dict(masked=True),0)
    for kind in ['null','bad_PC','user','valid']:
        cpu=media.CPU();cpu.pc=0 if kind=='bad_PC' else 0xddfe;cpu.sr=0 if kind=='user' else 0x2700;cpu.registers[15]=cpu.ssp=0x1ffffa;before=bytes(cpu);status=stop(None if kind=='null' else c.byref(cpu));assert status==(0 if kind=='valid' else 1)
        if kind!='valid':assert bytes(cpu)==before
        else:assert cpu.pc==0xde02 and cpu.sr==0x2000
        cases.append(dict(name='handler_STOP',kind=kind,status=status))
    out=ROOT/'verification/BIWN-movie-privilege-guards'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);report=dict(status='userSTOP_privilege_nestedIRQ_VBI_host_contracts_checked',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),checks=len(cases),cases=cases,source_sha256=proof['source_sha256'],whole_game_complete=False)
    save(out/'report.json',report);save(ROOT/'verification/BIWN-movie-privilege-guards.json',report);print(json.dumps(dict(directory=str(out),checks=len(cases))))
if __name__=='__main__':main()
