"""Match nested text+inventory writes in existing original-game replay."""
import ctypes as c
import csv,json
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_inventory_pipeline as check
ROOT=check.ROOT
def read(p):return json.loads(p.read_text())
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')

def main():
    prior=read(ROOT/'verification/biwn-inventory-draw-runtime-review.json');out=Path(prior['directory']);report=read(ROOT/'verification/biwn-inventory-pipeline-checks.json')
    assert prior['groups_compared']==9 and prior['baseline9000_frames_commands_DSP_CPU_catalog_captures_identical']
    source=ROOT/'projects/black-ice-white-noise/restoration'
    for n,digest in report['source_sha256'].items():assert check.draw.binary_tools.sha(source/n)==digest
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);image=(session/'nextstage-68000-candidate.bin').read_bytes();assert check.draw.stage.digest(image)==check.draw.stage.STAGE_SHA
    library=c.CDLL(str(Path(report['directory'])/'libbiwn_inventory_pipeline.dylib'));fn=library.biwn_inventory_pipeline;fn.argtypes=[c.POINTER(check.Bus)];fn.restype=c.c_int
    with (out/'drawing-text-CPU-watch-events.csv').open()as stream:events=[e for e in csv.DictReader(stream,fieldnames=['seq','frame','halfline','type','who','pc','addr','value'])if e['who']=='6'and e['type']=='12'and (0x1b786<=int(e['pc'],16)<0x1bc78 or 0x14776<=int(e['pc'],16)<0x14caa)]
    groups=[]
    for previous in prior['groups']:
        first=int(previous['actual_records'][0]['seq']);last=int(previous['actual_records'][-1]['seq']);actual=[e for e in events if first<=int(e['seq'])<=last]
        case=previous['assumptions'];memory=check.Memory(image,case);status,_=check.translated(fn,memory);assert status==0 and not memory.errors
        predicted=[]
        for row in memory.trace:
            if row[0]=='w'and 0xf02200<=row[1]<=0xf0226c:
                _,address,width,value=row;assert width==4;predicted.extend([(address,(value>>16)&0xffff),(address+2,value&0xffff)])
        observed=[(int(e['addr'],16),int(e['value'],16))for e in actual]
        if observed!=predicted:
            save(out/'pipeline-nested-write-mismatch.json',{'first_frame':previous['first_frame'],'case':case,'actual':actual,'C_trace':memory.trace,'predicted_word_writes':predicted})
            raise AssertionError('Nested text/drawing writes differ; inspect retained mismatch')
        count=sum(0x14776<=int(e['pc'],16)<0x14caa for e in actual)
        groups.append({'first_frame':previous['first_frame'],'last_frame':previous['last_frame'],'snapshot_assumptions':case,'first_seq':first,'last_seq':last,'all_word_write_records':len(actual),'text_helper_word_write_records':count,'drawing_word_write_records':len(actual)-count,'matched':True,'actual':actual,'predicted_long_writes':[e for e in memory.trace if e[0]=='w'and 0xf02200<=e[1]<=0xf0226c]})
    result={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'coordinator_reviewed_connected_inventory_and_text_original_game_write_sequences','directory':str(out),'groups_compared':len(groups),'drawing_and_text_word_records':sum(g['all_word_write_records']for g in groups),'nested_text_word_records':sum(g['text_helper_word_write_records']for g in groups),'main_drawing_word_records':sum(g['drawing_word_write_records']for g in groups),'groups':groups,
            'baseline9000_frames_commands_DSP_CPU_catalog_captures_identical':True,'full_trace_sha256':prior['raw_trace_sha256'],'subset_sha256':check.draw.binary_tools.sha(out/'drawing-text-CPU-watch-events.csv'),
            'matched':'All9retained original-game drawing intervals match linked portableC drawing plus nestedtext MMIOwrite addresses,values,word-half ordering under stable postframe slot snapshots and preserved static assets.',
            'limits':['Only CPUwrites toF02200..F0226F compared. GPU mailbox reads/writes not in existing watch; linked CPU tests cover scripted mailboxschedules separately.','OriginalGPU/drawing processing runs in emulator, but Cdevice/pixelprocessing is not implemented. No reconstructed frame/hardware/whole-game equivalence.','Input/slotstate snapshots and money200are assumptions; instruction-time reads and transient changes not captured. Existing9calls only, not arbitrary game states.']}
    save(out/'pipeline-coordinator-review.json',result);save(ROOT/'verification/biwn-inventory-pipeline-runtime-review.json',result)
    print(json.dumps({k:result[k]for k in ['groups_compared','drawing_and_text_word_records','nested_text_word_records','main_drawing_word_records']}),flush=True)

if __name__=='__main__':main()
