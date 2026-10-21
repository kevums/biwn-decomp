"""Scene test runtime with independently controlled outer/nested host budgets."""
import check_scene17_structured_host_v1 as base
from check_scene17_structured_host_v1 import cd,c,queue
world=queue.world
make_cpu=queue.make_cpu
ENTRIES=queue.ENTRIES
SCRIPTS=queue.SCRIPTS
class Runtime(base.Runtime):
    def translated(self,ram,case,missing=None,null_bus=False,null_cpu=False,null_service=False,budget=10000,fail=None,bad_pc=False,stop_flag=None,nested_budget=None):
        self.reset(ram,case,1)
        def reader(w):
            def cb(_,a,v):
                if fail==('read',w):return 1
                try:v[0]=self.read(a,w);return 0
                except Exception as e:self.errors.append(repr(e));return 1
            return cb
        def writer(w):
            def cb(_,a,v):
                if fail==('write',w):return 1
                try:self.write(a,w,v);return 0
                except Exception as e:self.errors.append(repr(e));return 1
            return cb
        types=[world.R8,world.R16,world.R32,world.W16,world.W32,cd.dispatch.W8];callbacks=[types[0](reader(1)),types[1](reader(2)),types[2](reader(4)),types[3](writer(2)),types[4](writer(4)),types[5](writer(1))]
        if missing is not None:callbacks[missing]=types[missing]()
        bus=world.Bus(*callbacks[:5],world.CALL(),None,0)
        def service(_,passed,state,target):
            if fail==('helper',target):return 1
            try:
                if target in ENTRIES:
                    row={'target':target,'actual_body':True,'incoming':cd.scheduler.cpu_dict(state.contents)};self.calls.append(row);status=self.fn(passed,state,callbacks[5],callback,None,budget if nested_budget is None else nested_budget,0);row['return']=cd.scheduler.cpu_dict(state.contents);return status
                assert target in SCRIPTS,hex(target);self.scripted(state.contents,target);return 0
            except Exception as e:self.errors.append(repr(e));return 1
        callback=cd.world_cpu.SERVICE()if null_service else cd.world_cpu.SERVICE(service);s=make_cpu(case)
        if bad_pc:s.pc=0
        before=bytes(s);f=self.fn if case['body']or case['render']else self.call;status=f(None if null_bus else c.byref(bus),None if null_cpu else c.byref(s),callbacks[5],callback,None,budget,int(case['render'])if stop_flag is None else stop_flag)
        return self.device.ram(),s,{'status':status,'CPU_unchanged':before==bytes(s),'calls':self.calls,'trace':list(self.trace),'errors':self.errors,'device':self.stats()}
