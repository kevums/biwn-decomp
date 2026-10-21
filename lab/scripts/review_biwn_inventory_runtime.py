"""Compare observed active UI bus shapes/write values with checked C block."""
import ctypes as c
import csv,json
from datetime import datetime,timezone
from pathlib import Path
from collections import Counter
import check_biwn_inventory_select as check
ROOT=check.stage.ROOT
def read(path):return json.loads(path.read_text())
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n')


def main():
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    raw=read(session/'emulator-runtime/inventory-current.json');out=Path(raw['directory'])
    assert raw['inputs_core_previous_observer_unchanged']and raw['all9000_baseline_frames_commands_DSP_CPU_catalog_and_captures_identical']
    checks=read(ROOT/'verification/biwn-inventory-select-checks.json');source=ROOT/'projects/black-ice-white-noise/restoration'
    for name,digest in checks['source_sha256'].items():assert check.binary_tools.sha(source/name)==digest
    lib=c.CDLL(str(Path(checks['directory'])/'libbiwn_inventory_select.dylib'));fn=lib.biwn_inventory_select;fn.argtypes=[c.POINTER(check.Bus),c.POINTER(check.State)];fn.restype=c.c_int
    with (out/'inventory-watch-events.csv').open()as stream:events=list(csv.DictReader(stream))
    with (out/'inventory-frames.csv').open()as stream:frames=list(csv.DictReader(stream))
    assert len(frames)==9000
    widths={0x1a1f6:4,0x1a200:1,0x1a20a:2,0x1a214:2,0x1a21c:2,0x1a224:4,0x1a22c:2,0x1a236:2,0x1a23e:2,0x1a244:2}
    groups=[]
    for change in raw['post621_slot_state_changes']:
        frame=change['frame'];word=int(change['input'],16);before=[int(x,16)for x in change['before']];after=[int(x,16)for x in change['after']]
        script=check.Script(word,*before);status,state=check.translated(fn,script,[0]*15);assert status==0 and not script.errors
        result=[int.from_bytes(script.memory[0x49d54-check.BASE:0x49d54-check.BASE+2],'big'),int.from_bytes(script.memory[0x49d56-check.BASE:0x49d56-check.BASE+2],'big')];assert result==after
        actual=[e for e in events if int(e['frame'])==frame and e['who']=='6'and 0x1a1f0<=int(e['pc'],16)<0x1a254]
        actual_shape=[];actual_writes=[]
        for event in actual:
            pc=int(event['pc'],16);assert pc in widths
            kind='r'if event['type']=='11'else'w';assert event['type']in('11','12')
            address=int(event['addr'],16);width=widths[pc];actual_shape.append((kind,address,width))
            if kind=='r':assert event['value']=='00000000' # Pinned emitter placeholder, NOT measured read data.
            else:actual_writes.append((kind,address,width,int(event['value'],16)))
        predicted_shape=[tuple(e[:3])for e in script.trace if e[0]!='call'];predicted_writes=[e for e in script.trace if e[0]=='w']
        assert actual_shape==predicted_shape and actual_writes==predicted_writes,(change,actual_shape,predicted_shape,actual_writes,predicted_writes)
        assert script.trace[-1]==('call',0x1b786)
        groups.append({'frame':frame,'postframe_input_word':hex(word),'before':before,'after':after,'C_final_D0_D1_A0':state,
                       'C_scripted_bus_trace':script.trace,'actual_bus_records':actual,'read_address_order_width_shape_matches':True,'write_values_order_match':True,
                       'limits':'Read widths inferred from original instructions and emitter; read data is not recorded. C inputs are postframe snapshots, not per-instruction capture. Actual redraw sideeffects not compared.'})
    copies=[e for e in events if e['who']=='6'and e['type']=='12'and e['pc']=='01a244'and e['addr']=='049d56'and int(e['frame'])>=622]
    assert len(copies)==len(groups)==8
    locals=read(ROOT/'verification/biwn-inventory-local-review.json')
    assert locals['roles'][0]['text']==locals['roles'][1]['text']
    for role in locals['roles']:
        obj=json.loads(role['text']);assert obj['zero_digit_full_D0_example']=='12340000'
    locals.update(recorded_at=datetime.now(timezone.utc).isoformat(),status='coordinator_reviewed_partial_facts_contract_rejected',
                  review=['Both roles preserve CLR.W example and bit priority, but their rereads field incorrectly includes49D56. In this block49D56is written only;49D54is read for copying. Reject this as a complete translation contract.',
                          'Both omit distinct repeated source reads and fallthrough-versus-RTS detail. Reviewer copies analyst and reports errorsnone; not independent review.',
                          'MinifiedJSON wordcount1 is a whitespace count, not evidence of concise explanatory quality. No role output used to replace checked C.'],
                  corrected_contract='Input32 and byte49BAE are read separately; digit path rereads input32. Cycle path compares49D54and rereads ifnot9. Subtract/copy reread49D54;49D56receives a write. Block falls through1A254after modeled1B786call; actual renderer excluded.')
    save(ROOT/'verification/biwn-inventory-local-review.json',locals);save(Path(locals['directory'])/'coordinator-review.json',locals)
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'coordinator_reviewed_eight_runtime_selection_write_groups',
            'directory':str(out),'raw_report':str(out/'report.json'),'baseline_replay_all9000_frames_and_DSP_CSVs_catalog_captures_identical':True,
            'active_selection_groups':groups,'all_observed_selection_copy_writes_covered':8,
            'observed_slot_changes':raw['post621_slot_state_changes'],'final_slot_state':raw['final_inventory_state'],
            'trace_counts':{'records':raw['watched_records'],'unreadable':raw['unreadable_records'],'max_frame_events':raw['max_frame_events']},
            'source_watch_read_warning':{'file':str(ROOT/'tools/virtualjaguar-runtime-source/src/core/jaguar.c'),'sha256':check.binary_tools.sha(ROOT/'tools/virtualjaguar-runtime-source/src/core/jaguar.c'),
                                         'fact':'Pinned m68k_read_memory_8/16/32 watch sites emit value0before reading memory. Reads are address/PC events with placeholderzero and no width field; not actualreadvalues.'},
            'matched':'All8observed active selection groups match checked C read-address/order shapes with statically inferred widths, exact write-value/order sequences and postframe slot-state outcomes under stable scripted snapshot inputs.',
            'limits':['Postframe input/state values are not instruction-time register/memory capture. Unrecorded/transient changes and other schedules are not excluded.',
                      'Original read values are notlogged; zero is a recorder placeholder. Widths inferred from source instructions/emitter, not stored in events.',
                      'Calls to actual1B786renderer, complete1A188function, physical controller mapping/hardware and reconstructed-game behavior remain unverified.'],
            'next_step':'Reconstruct drawing/data dependencies at1B786 and validate broader UI/state behavior; keep whole-game integration incomplete.'}
    save(out/'coordinator-review.json',report);save(ROOT/'verification/biwn-inventory-runtime-review.json',report)
    print(json.dumps({'groups':len(groups),'write_value_order':'all match','read_shapes':'all match; data notlogged','baseline9000':'identical','local_contracts':'rejected due false read49D56'}))


if __name__=='__main__':main()
