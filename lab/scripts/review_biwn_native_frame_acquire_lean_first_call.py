"""First live call phase equality and isolated pre-loader CPU cost, no device ticks."""
import json,struct
from pathlib import Path
from datetime import datetime,timezone
from check_biwn_scheduler import CPU,cpu_dict,Native
from check_biwn_native_button_digit import ROOT,sha,save

def main():
    pp=ROOT/'verification/native-frame-acquire-lean-first-call-current.json';p=json.loads(pp.read_text());assert p['status']=='terminal_read_only_first_call_pair_pending_review';source=Path(p['directory'])
    out=ROOT/'verification/native-frame-acquire-lean-first-call-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);(out/'reviewer-as-run.py').write_bytes(Path(__file__).read_bytes())
    for job in p['jobs']:
        assert job['exit_code']==0
        for name,h in job['source_sha256'].items():assert sha(name)==h
    states={};phases=[];inputs=[]
    for phase in ['entry','loader_entry','loader_return','return']:
        row={};states[phase]={}
        for lane in ['control','candidate']:
            d=source/lane;c=CPU.from_buffer_copy((d/(phase+'.cpu')).read_bytes());ram=(d/(phase+'.ram')).read_bytes();meta=json.loads((d/(phase+'.json')).read_text());states[phase][lane]=(c,ram);row[lane]=dict(cpu=cpu_dict(c),**meta);inputs += [d/(phase+'.cpu'),d/(phase+'.ram'),d/(phase+'.json')]
        a,ar=states[phase]['control'];b,br=states[phase]['candidate'];ac=cpu_dict(a);bc=cpu_dict(b);oldpc=ac.pop('pc');newpc=bc.pop('pc');assert ac==bc,(phase,'Actual full caller CPU excluding relocated PC differs')
        if phase in ['entry','loader_entry']:assert oldpc==newpc
        else:assert (oldpc,newpc)==((0x1ad7a,0x1627de) if phase=='loader_return' else (0x1ae54,0x162762))
        sp=states['entry']['control'][0].registers[15]
        diffs=[i for i,(x,y) in enumerate(zip(ar,br)) if x!=y];public_frame_equal=ar[sp-44:sp]==br[sp-44:sp];cache_equal=ar[0x15b4a0:0x15b530]==br[0x15b4a0:0x15b530]
        external=[i for i in diffs if not 0x1ac68<=i<0x1ac6e and not sp-8192<=i<sp-44]
        row.update(all_D_A_SR_USP_SSP_equal=True,declared_PC_mapping=[hex(oldpc),hex(newpc)],full_public_44bytes_equal=public_frame_equal,full_cache_equal=cache_equal,RAM_different_bytes=len(diffs),RAM_external_difference_addresses=[hex(i) for i in external]);phases.append(dict(phase=phase,**row))
        if phase=='entry':assert diffs==[0x1ac69,0x1ac6a,0x1ac6b,0x1ac6c,0x1ac6d]
        assert public_frame_equal and cache_equal
    entry,original=states['entry']['control'];_,candidate=states['entry']['candidate'];n=Native();runs={}
    try:
        for lane,image in [('control',original),('candidate',candidate)]:
            l=n.lib;n.device.seed(image,0);l.m68k_pulse_reset();l.m68k_set_irq(0);l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,entry.ssp);l.m68k_set_reg(17,0);l.m68k_set_reg(15,entry.usp);l.m68k_set_reg(17,entry.sr)
            for i,v in enumerate(entry.registers):l.m68k_set_reg(i,v)
            l.m68k_set_reg(16,entry.pc);steps=0;cycles=0
            while l.m68k_get_reg(None,16)!=0x1b044 and steps<500000:cycles+=l.m68k_execute(1);steps+=1
            assert l.m68k_get_reg(None,16)==0x1b044
            regs=[l.m68k_get_reg(None,i) for i in range(18)];regs += [n.prefix[16] if regs[17]&0x2000 else regs[15],regs[15] if regs[17]&0x2000 else n.prefix[17]];ram=n.device.ram();sp=regs[15];args=[n.device.read(sp+4+4*i,4) for i in range(5)];runs[lane]=dict(cpu=regs,args=args,steps=steps,cycles=cycles,ram=ram)
        a,b=runs['control'],runs['candidate'];assert a['cpu']==b['cpu'] and a['args']==b['args'];sp=entry.registers[15];diffs=[i for i,(x,y) in enumerate(zip(a['ram'],b['ram'])) if x!=y];external=[i for i in diffs if not 0x1ac68<=i<0x1ac6e and not sp-8192<=i<sp-44];assert not external,external[:30]
        assert a['ram'][sp-44:sp]==b['ram'][sp-44:sp]
        for row in runs.values():row.pop('ram')
    finally:n.close()
    result=dict(status='terminal_native_frame_acquire_first_call_CPU_public_frame_cache_match_timing_differs',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),capture_proof=str(pp),capture_proof_sha256=sha(pp),phases=phases,isolated_preloader=runs,isolated_preloader_full_CPU_args_public_RAM_equal=True,isolated_preloader_external_RAM_differences=external,source_entry_frame=phases[0]['control']['frame'],candidate_entry_frame=phases[0]['candidate']['frame'],source_loader_frame=phases[1]['control']['frame'],candidate_loader_frame=phases[1]['candidate']['frame'],source_return_frame=phases[-1]['control']['frame'],candidate_return_frame=phases[-1]['candidate']['frame'],whole_route_equivalent=False,default_promoted=False,new_training=False,physical_console_verified=False,whole_game_complete=False,scope='Same-layout fresh first call starts with identical full CPU and2MBRAM except five changed bytes in the six-byte entry JMP. Actual live loader entry full CPU/PC/args agree; loader return and final pre-RTS all D/A/SR/stackbanks,44public frame bytes and144cache bytes agree with mapped codePC. Before-loader isolated CPU runs disable IRQ/device ticks and agree in full publicRAM+CPU+args, with measured different native instruction/cycle costs. Live preloader external differences lie in asynchronously updated memory; later differences include scheduler resume/clock fields. This supports a timing explanation for the first divergence, not proof of all later differences, arbitrary timing preservation or entire gameplay equivalence. Guest RAM was never written in live captures; standalone replay is separately declared.',artifact_sha256={str(q):sha(q) for q in [*inputs,out/'reviewer-as-run.py']})
    save(out/'review.json',result);save(ROOT/'verification/native-frame-acquire-lean-first-call-reviewed-current.json',result);print(result['status'],{k:{x:v[x] for x in ['steps','cycles']} for k,v in runs.items()},flush=True)

if __name__=='__main__':main()
