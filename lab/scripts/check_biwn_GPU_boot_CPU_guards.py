"""Typed host errors and retained BIOS3000 private frame for sourceE00A."""
import ctypes as c,json
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_movie_source_boot_exit_AV as joined
media=joined.media;ROOT=joined.ROOT;save=joined.save;sha=joined.sha

def main():
    proof=json.loads((ROOT/'verification/BIWN-movie-source-boot-exit-AV.json').read_text());lib=c.CDLL(str(Path(proof['directory'])/'libcontroller-AV.dylib'));fn=lib.biwn_GPU_boot_cpu_call
    fn.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),media.W8,media.world_cpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];fn.restype=c.c_int
    cases=[]
    def check(options,expected):
        ram=bytearray(0x200000);ram[0x40a0:0x40a8]=bytes.fromhex('00f030000000009e');ram[0x1ff000:0x1ff004]=joined.controller.STOP.to_bytes(4,'big');writes=[];bios=[]
        types=[media.scheduler.cleanup.world.R8,media.scheduler.cleanup.world.R16,media.scheduler.cleanup.world.R32,media.scheduler.cleanup.world.W16,media.scheduler.cleanup.world.W32]
        def rd(w):
            def cb(_,a,v):
                if options.get('fail_read'):return 1
                v[0]=int.from_bytes(ram[a:a+w],'big') if a<0x200000 else 0;return 0
            return cb
        def wr(w):
            def cb(_,a,v):
                if options.get('fail_write'):return 1
                if a<0x200000:ram[a:a+w]=v.to_bytes(w,'big')
                writes.append([a,w,v]);return 0
            return cb
        callbacks=[types[0](rd(1)),types[1](rd(2)),types[2](rd(4)),types[3](wr(2)),types[4](wr(4))]
        if 'missing' in options:callbacks[options['missing']]=type(callbacks[options['missing']])()
        bus=media.Bus(*callbacks,media.scheduler.cleanup.world.CALL(),None,0);w8=media.W8() if options.get('null_w8') else media.W8(wr(1))
        def service(_,b,s,target):
            assert target==0x3000 and s.contents.registers[8]==0xf03050;bios.append(dict(target=hex(target),A0=hex(s.contents.registers[8]),stack=s.contents.registers[15],return_PC=hex(int.from_bytes(ram[s.contents.registers[15]:s.contents.registers[15]+4],'big'))))
            if options.get('bad_return'):s.contents.registers[15]+=4
            return int(options.get('fail_service',False))
        svc=media.world_cpu.SERVICE() if options.get('null_service') else media.world_cpu.SERVICE(service)
        cpu=media.CPU();cpu.pc=0 if options.get('bad_pc') else 0xe00a;cpu.sr=0x2700;cpu.ssp=cpu.registers[15]=0x1ff000;cpu.usp=0x1fe000;initial=bytes(cpu)
        status=fn(None if options.get('null_bus') else c.byref(bus),None if options.get('null_CPU') else c.byref(cpu),w8,svc,None,options.get('budget',10000),options.get('yield',1));assert status==expected,(options,status)
        if status:assert bytes(cpu)==initial
        else:assert cpu.pc==joined.controller.STOP and len(bios)==1 and bios[0]['return_PC']=='0xe024' and len([x for x in writes if 0xf03000<=x[0]<0xf04000])==159
        cases.append(dict(options=options,status=status,state_unchanged=bytes(cpu)==initial,bios_calls=bios,external_writes=len(writes)))
    for options in [dict(missing=i) for i in range(5)]+[dict(null_bus=True),dict(null_CPU=True),dict(null_w8=True),dict(null_service=True),dict(budget=0),{'yield':2}]:check(options,1)
    for options,status in [(dict(bad_pc=True),7),(dict(budget=1),4),(dict(fail_read=True),2),(dict(fail_write=True),2),(dict(fail_service=True),3),(dict(bad_return=True),5),({},0)]:check(options,status)
    out=ROOT/'verification/BIWN-GPU-boot-CPU-guards'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);report=dict(status='source_E00A_host_contracts_and_actual_BIOS_JSR_frame_checked',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),checks=len(cases),cases=cases,source_sha256={n:proof['source_sha256'][n] for n in ['biwn_GPU_boot_cpu.c']},BIOS_actual_firmware=False,whole_game_complete=False)
    save(out/'report.json',report);save(ROOT/'verification/BIWN-GPU-boot-CPU-guards.json',report);print(json.dumps(dict(directory=str(out),checks=len(cases))))
if __name__=='__main__':main()
