"""Fresh repaired-disc CPU source-provider comparison; no checkpoint restore.

Retained original GPU/DSP/devices run in both lanes. The C lane owns every
68000 instruction beginning with mainstage4000; HLE bootstrap is separate.
"""
import argparse,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--frames',type=int,default=1600);args=ap.parse_args()
 cp=ROOT/'verification/native-formatter-C-bridge-current.json';candidate=json.loads(cp.read_text());bp=ROOT/'verification/native-fast-core-wait-format-disc-build-current.json';build=json.loads(bp.read_text())
 for p,h in candidate['source_sha256'].items():assert sha(p)==h,p
 assert sha(build['derived_disc'])==build['derived_disc_sha256']
 out=ROOT/'verification/native-formatter-C-fresh-pair'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 source=ROOT/'scripts/probe_biwn_fresh_CD_boot.py';text=source.read_text();text='import sys\nsys.path.insert(0,'+repr(str(ROOT/'scripts'))+')\n'+text
 replacements={'ROOT = Path(__file__).resolve().parents[1]':'ROOT = Path('+repr(str(ROOT))+')','    args = parser.parse_args()':"    parser.add_argument('--disc',type=Path,required=True)\n    parser.add_argument('--CPU-mode',choices=['reference','C'],required=True)\n    args = parser.parse_args()","    disc = ROOT / 'projects/black-ice-white-noise/originals/BIWN#23.cdi'":"    disc = args.disc.resolve()","    button_ids = {'U': 4, 'D': 5, 'L': 6, 'R': 7, 'A': 8,\n                  'B': 0, 'C': 1, 'OPTION': 3, 'PAUSE': 2}":"    from biwn_controller import JOYPAD_BUTTONS\n    button_ids=JOYPAD_BUTTONS"}
 for marker,value in replacements.items():assert text.count(marker)==1,marker;text=text.replace(marker,value)
 install=f'''
        import biwn_fast_CPU_bridge as CPU_bridge
        owner,retired,CPU_library,CPU_host,finish_CPU=CPU_bridge.install(core,out,args.CPU_mode,ram_pointer,Path({candidate['native_CPU_candidate']!r}),trace=False)
        entry_gate={{'armed':False,'bootstrap_native_callbacks':0}}
        def gate_entry(pc):
            if pc!=0x4000:
                entry_gate['bootstrap_native_callbacks']+=1
                return 0
            entry_gate['armed']=True
            core.BIWNSetCPUExecOwner(owner,int(args.CPU_mode=='C'))
            return owner(pc)
        GATE=c.CFUNCTYPE(c.c_int32,c.c_uint32);gate=GATE(gate_entry)
        core.BIWNSetCPUExecOwner.argtypes=[GATE,c.c_int]
        core.BIWNSetCPUExecOwner(gate,0)
        for name in ['Owned','Original','Rejected']:
            getattr(core,'BIWNCPU'+name+'InstructionCount').restype=c.c_uint64
        def full_CPU():
            value=CPU_bridge.media.CPU();core.BIWNReadCPUState(c.byref(value))
            return dict(registers=list(value.registers),pc=value.pc,usp=value.usp,ssp=value.ssp,sr=value.sr)
        def processor_digest(name):
            fn=getattr(core,name+'StateSave');fn.argtypes=[c.c_void_p];fn.restype=c.c_size_t
            buffer=c.create_string_buffer(65536);size=fn(buffer);assert 0<size<=65536
            return hashlib.sha256(buffer.raw[:size]).hexdigest()
'''
 marker='        assert ram_pointer';assert text.count(marker)==1;text=text.replace(marker,marker+install)
 marker="                       stage_sha256=hashlib.sha256(ram[0x4000:0x100000]).hexdigest())";assert text.count(marker)==1
 text=text.replace(marker,"                       CPU_full=full_CPU(),\n                       full_RAM_sha256=hashlib.sha256(ram).hexdigest(),\n                       full_GPU_state_sha256=processor_digest('GPU'),\n                       full_DSP_state_sha256=processor_digest('DSP'),\n                       video_sha256=hashlib.sha256(video.get('raw',b'')).hexdigest(),\n                       floor_word=int.from_bytes(ram[0x49c62:0x49c64],'big'),\n"+marker)
 marker="        report.update(status='terminal_fresh_libretro_CD_probe', frames=rows,";assert text.count(marker)==1
 finish='''
        stats=finish_CPU()
        report['C_CPU_backend']=dict(mode=args.CPU_mode,entry_gate=entry_gate,stats=stats,counts={name:getattr(core,'BIWNCPU'+name+'InstructionCount')()for name in ['Owned','Original','Rejected']},scope='OnlyHLE bootstrap before mainstage4000 uses original68000opcodes in C lane; GPU,DSP,devices,IRQ decisions remainretainedemulator. No guestRAMpatch or checkpointrestore.')
'''
 text=text.replace(marker,finish+marker);probe=out/'probe.py';compile(text,str(probe),'exec');probe.write_text(text)
 prefixp=ROOT/'verification/whole-merchant-global-fixed-input.json';windows=[dict(row,stop_frame=min(row['stop_frame'],args.frames+1))for row in json.loads(prefixp.read_text())['windows']if row['start_frame']<args.frames+1];inputs=out/'input.json';save(inputs,dict(windows=windows))
 core=ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source/virtualjaguar_libretro.dylib'
 state=dict(status='running_fresh_native_vs_C_formatter_pair',pid=os.getpid(),directory=str(out),frames=args.frames,CPU_bridge_proof=str(cp),CPU_bridge_proof_sha256=sha(cp),build_proof=str(bp),build_proof_sha256=sha(bp),commands=[],source_sha256={str(p):sha(p)for p in [Path(__file__),source,probe,cp,bp,core,inputs,prefixp,Path(build['derived_disc'])]},checkpoint_restores=0,host_guest_RAM_writes=0,new_training=False,default_promoted=False,whole_game_complete=False)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-formatter-C-fresh-pair-active.json',state)
 mark();children=[]
 try:
  for lane in ['reference','C']:
   command=[str(ROOT/'.venv/bin/python'),'-u',str(probe),'--boot','hle','--frames',str(args.frames),'--core',str(core),'--disc',build['derived_disc'],'--CPU-mode',lane,'--frame-controller-script',str(inputs),'--capture-audio','--no-publish','--output',str(out/lane)]
   log=(out/(lane+'.log')).open('w');child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);children.append((lane,child,log));state['commands'].append(dict(lane=lane,pid=child.pid,command=command));mark()
  codes={}
  for lane,child,log in children:codes[lane]=child.wait();log.close()
  state['exit_codes']=codes
  if any(codes.values()):state['status']='terminal_C_fresh_pair_child_rejected';mark();print(json.dumps(codes),flush=True);return
  reports={lane:json.loads((out/lane/'report.json').read_text())for lane in ['reference','C']};fields=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256'];comparisons={field:dict(different_frames=sum(a[field]!=b[field]for a,b in zip(reports['reference']['frames'],reports['C']['frames'])),first_different_frame=next((a['frame']for a,b in zip(reports['reference']['frames'],reports['C']['frames'])if a[field]!=b[field]),None))for field in fields}
  backend=reports['C']['C_CPU_backend'];assert backend['entry_gate']['armed']and backend['stats']['steps']>0 and backend['stats']['errors']==0 and backend['counts']['Original']==0 and backend['counts']['Rejected']==0
  state.update(status='terminal_fresh_C_formatter_pair_equal'if not any(v['different_frames']for v in comparisons.values())else'terminal_fresh_C_formatter_pair_diverged',comparisons=comparisons,C_backend=backend,report_sha256={lane:sha(out/lane/'report.json')for lane in reports},audio_PCM_equal=sha(out/'reference/frontend-PCM.s16le')==sha(out/'C/frontend-PCM.s16le'),C_after_mainstage_original_opcode_fallback=0)
  mark();save(ROOT/'verification/native-formatter-C-fresh-pair-current.json',state);print(json.dumps(dict(status=state['status'],comparisons=comparisons,C_backend=backend),indent=2),flush=True)
 except BaseException as error:state.update(status='terminal_pair_driver_failure',error=repr(error));mark();raise
if __name__=='__main__':main()
