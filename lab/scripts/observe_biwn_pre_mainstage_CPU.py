"""Read-only fresh inventory of CPU bootstrap instructions before mainstage4000."""
import json,subprocess,os
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
    priorp=ROOT/'verification/native-formatter-C-fresh-pair-current.json';prior=json.loads(priorp.read_text());old=Path(prior['directory'])/'probe.py'
    assert sha(old)==prior['source_sha256'][str(old)]
    out=ROOT/'verification/pre-mainstage-CPU-inventory'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);(out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes());print(out,flush=True)
    text=old.read_text();marker="        entry_gate={'armed':False,'bootstrap_native_callbacks':0}";assert text.count(marker)==1
    extra='''
        import capstone
        bootstrap_decoder=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
        bootstrap_rows={};bootstrap_lengths={};bootstrap_outside={};bootstrap_errors=[]
        def observe_bootstrap(pc):
            if not 0<=pc<=0x1ffffe:
                bootstrap_outside[hex(pc)]=bootstrap_outside.get(hex(pc),0)+1
                return
            opcode=c.string_at(ram_pointer+pc,2)
            key=(pc,opcode)
            if key not in bootstrap_lengths:
                ins=next(bootstrap_decoder.disasm(c.string_at(ram_pointer+pc,min(24,0x200000-pc)),pc,count=1))
                bootstrap_lengths[key]=(ins.size,ins.mnemonic+' '+ins.op_str)
            size,assembly=bootstrap_lengths[key];code=c.string_at(ram_pointer+pc,size).hex();identity=(pc,code)
            if identity not in bootstrap_rows:
                bootstrap_rows[identity]=dict(address=hex(pc),bytes=code,size=size,assembly=assembly,executions=0,first_CPU=full_CPU())
            bootstrap_rows[identity]['executions']+=1
'''
    text=text.replace(marker,marker+extra)
    marker="                entry_gate['bootstrap_native_callbacks']+=1";assert text.count(marker)==1
    text=text.replace(marker,marker+"\n                try:observe_bootstrap(pc)\n                except BaseException as error:bootstrap_errors.append(repr(error))")
    marker="            entry_gate['armed']=True";assert text.count(marker)==1
    text=text.replace(marker,marker+"\n            (out/'main-entry-RAM.bin').write_bytes(c.string_at(ram_pointer,0x200000))")
    marker='        stats=finish_CPU()';assert text.count(marker)==1
    finish='''
        bootstrap_list=sorted(bootstrap_rows.values(),key=lambda row:(int(row['address'],16),row['bytes']))
        (out/'bootstrap-instructions.json').write_text(json.dumps(dict(instructions=bootstrap_list,outside_RAM=bootstrap_outside,errors=bootstrap_errors),indent=2)+'\\n')
        report['bootstrap_CPU_inventory']=dict(callbacks=entry_gate['bootstrap_native_callbacks'],static_variants=len(bootstrap_list),outside_RAM=bootstrap_outside,errors=bootstrap_errors,mainstage_reached=entry_gate['armed'],scope='Read-only instruction-byte inventory; no opcode ownership, guest writes or checkpoint restore. First-CPU samples are examples, not complete input domains.')
'''
    text=text.replace(marker,finish+marker);probe=out/'probe.py';compile(text,str(probe),'exec');probe.write_text(text)
    cmd=list(next(row['command']for row in prior['commands']if row['lane']=='reference'));cmd[2]=str(probe);cmd[cmd.index('--frames')+1]='200';cmd[cmd.index('--output')+1]=str(out/'reference');idx=cmd.index('--frame-controller-script');del cmd[idx:idx+2]
    state=dict(status='running_read_only_pre_mainstage_inventory',pid=os.getpid(),directory=str(out),command=cmd,source_sha256={str(p):sha(p)for p in [out/'runner-as-run.py',priorp,old,probe]},new_training=False,default_promoted=False,host_guest_RAM_writes=0,checkpoint_restores=0)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/pre-mainstage-CPU-inventory-active.json',state)
    mark()
    try:
        with(out/'reference.log').open('w')as log:
            child=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;mark();exit_code=child.wait()
        state['exit_code']=exit_code
        if exit_code:state['status']='terminal_bootstrap_inventory_child_rejected';mark();return
        result=json.loads((out/'reference/report.json').read_text());inventory=json.loads((out/'reference/bootstrap-instructions.json').read_text());assert not inventory['errors'] and not inventory['outside_RAM']
        assert result['bootstrap_CPU_inventory']['mainstage_reached'] and result['bootstrap_CPU_inventory']['callbacks']==sum(row['executions']for row in inventory['instructions'])
        control=json.loads((Path(prior['directory'])/'reference/report.json').read_text());assert result['core_sha256']==control['core_sha256'] and result['disc_sha256']==control['disc_sha256']
        fields=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256'];compare={name:sum(a[name]!=b[name]for a,b in zip(result['frames'],control['frames'][:200]))for name in fields};assert len(result['frames'])==200
        pcm=(out/'reference/frontend-PCM.s16le').read_bytes();reference_pcm=(Path(prior['directory'])/'reference/frontend-PCM.s16le').read_bytes()[:len(pcm)];assert pcm==reference_pcm
        state.update(status='terminal_read_only_bootstrap_inventory_equal'if not any(compare.values())else'terminal_bootstrap_observer_diverged',inventory=result['bootstrap_CPU_inventory'],comparisons=compare,PCM_prefix_equal=True,report_sha256=sha(out/'reference/report.json'),instructions_sha256=sha(out/'reference/bootstrap-instructions.json'),main_entry_RAM_sha256=sha(out/'reference/main-entry-RAM.bin'))
        mark();save(ROOT/'verification/pre-mainstage-CPU-inventory-current.json',state);print(json.dumps({k:state[k]for k in ['status','inventory','comparisons','PCM_prefix_equal']}),flush=True)
    except BaseException as error:state.update(status='terminal_bootstrap_inventory_driver_failed',error=repr(error));mark();raise

if __name__=='__main__':main()
