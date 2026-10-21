"""Compare CPU routine writes with original-game watch records (split words)."""
import ctypes as c
import csv,json
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_inventory_draw as check
ROOT=check.stage.ROOT
def read(path):return json.loads(path.read_text())
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n')

def main():
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    raw=read(session/'emulator-runtime/inventory-draw-current.json');out=Path(raw['directory'])
    assert raw['all9000_baseline_frames_commands_DSP_CPU_catalog_and_captures_identical']and raw['inputs_core_previous_observer_unchanged']and raw['unreadable_records']==0
    report=read(ROOT/'verification/biwn-inventory-draw-checks.json');source=ROOT/'projects/black-ice-white-noise/restoration'
    for name,digest in report['source_sha256'].items():assert check.binary_tools.sha(source/name)==digest
    image=(session/'nextstage-68000-candidate.bin').read_bytes();assert check.stage.digest(image)==check.stage.STAGE_SHA
    lib=c.CDLL(str(Path(report['directory'])/'libbiwn_inventory_draw.dylib'));fn=lib.biwn_inventory_draw;fn.argtypes=[c.POINTER(check.Bus)];fn.restype=c.c_int
    with (out/'inventory-frames.csv').open()as stream:frames={int(x['frame']):x for x in csv.DictReader(stream)}
    subset=out/'drawing-CPU-watch-events.csv'
    # The retained rg subset has no header. Filter exact PCs again, rather than trusting its regex as a routine boundary.
    with subset.open()as stream:events=[x for x in csv.DictReader(stream,fieldnames=['seq','frame','halfline','type','who','pc','addr','value'])if x['who']=='6'and x['type']=='12'and 0x1b786<=int(x['pc'],16)<0x1bc78]
    grouped=[]
    for event in events:
        if event['pc']=='01b78e'and event['addr']=='f02200':grouped.append([])
        assert grouped,'Partial group before first routine destination store'
        grouped[-1].append(event)
    results=[]
    for actual in grouped:
        frame=int(actual[0]['frame']);last_frame=int(actual[-1]['frame'])
        snapshot=frames[frame]
        for sampled_frame in range(frame,last_frame+1):
            for key in ['state_49d54','state_49d56']+['slot_'+str(i)for i in range(10)]:assert frames[sampled_frame][key]==snapshot[key]
        ids=[int(snapshot['slot_'+str(i)],16)for i in range(10)];assert ids==[65,36,41,70,0,0,0,0,0,0]
        case={'start':int(snapshot['state_49d54'],16),'selected':int(snapshot['state_49d56'],16),'layout':'real','money':200,'profile':'static'}
        memory=check.Memory(image,case);assert check.translated(fn,memory)==0 and not memory.errors
        predicted=[]
        for row in memory.trace:
            if row[0]=='w':
                _,address,width,value=row;assert width==4
                predicted.extend([(address,(value>>16)&0xffff),(address+2,value&0xffff)])
        observed=[(int(e['addr'],16),int(e['value'],16))for e in actual]
        if observed!=predicted:
            save(out/'drawing-write-mismatch.json',{'frame':frame,'snapshot':snapshot,'actual':actual,'predicted':predicted,'C_trace':memory.trace})
            raise AssertionError('Drawing writes differ; inspect retained mismatch')
        results.append({'first_frame':frame,'last_frame':last_frame,'postframe_slot_snapshots_stable_across_interval':True,'snapshot':snapshot,'assumptions':case,'CPU_long_writes':len(predicted)//2,'actual_word_write_records':len(actual),'write_values_addresses_order_match':True,'actual_records':actual,'predicted_long_writes':[e for e in memory.trace if e[0]=='w']})
    assert len(results)>0 and sum(x['actual_word_write_records']for x in results)==len(events)
    result={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'coordinator_reviewed_original_game_inventory_drawing_write_sequences',
            'directory':str(out),'baseline9000_frames_commands_DSP_CPU_catalog_captures_identical':True,'unreadable_records':0,
            'groups_compared':len(results),'original_routine_word_write_records':len(events),'groups':results,
            'source_watch_semantics':'Pinned m68k_write_memory_32 delegates blitter-area longs to two m68k_write_memory_16 calls. Watch records are high-word at address followed by low-word at address+2, with original CPU PC. C long writes expanded to exactly these ordered 16bit halves.',
            'subset_sha256':check.binary_tools.sha(subset),'raw_trace_sha256':raw['artifact_sha256']['inventory-watch-events.csv'],
            'scope':'Original game in assisted emulator, one prior GPU stack intervention. Routine-level store addresses/values/order match checked C under postframe slot snapshots and static asset tables. Original graphics helpers execute in emulator; their writes/call arguments and rendered pixels are not compared with portable C.',
            'limits':['No instruction-time input/slot read values or complete call argument capture. Snapshot assumptions may miss transient states.','Actual sprite/text processing is not implemented in C. GPU/DSP/device semantics, hardware, condition flags and whole-game equivalence remain unverified.','Broad watch also logs unrelated CPU/GPU traffic; only exact CPU interval records compared, 5.8GiB full trace retained. Money200 is a fixture assumption irrelevant to the compared routine-level MMIO writes.']}
    save(out/'drawing-coordinator-review.json',result);save(ROOT/'verification/biwn-inventory-draw-runtime-review.json',result)
    print(json.dumps({k:result[k]for k in ['groups_compared','original_routine_word_write_records','baseline9000_frames_commands_DSP_CPU_catalog_captures_identical']}),flush=True)

if __name__=='__main__':main()
