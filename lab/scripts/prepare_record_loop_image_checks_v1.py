"""Isolate new deployed-image checks from terminal v34/prototype evidence."""
from pathlib import Path
import json,hashlib
import prepare_record_stride_image_checks_v1 as old
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'scripts';V=ROOT/'verification'

def main():
    sources=set(old.MODULES.values())|{'check_native_record_strides_final_v1'}
    mapping={n:n.replace('record_strides','record_loop_image')for n in sources}
    bp=V/'native-record-loop-advance-disc-build-v1-current.json';alias=V/'native-record-loop-image-disc-build-v1-current.json'
    data=bp.read_bytes();build=json.loads(data)
    assert build['profile']=='deck-shared-v37-record-loop-advance-v2'and build['shared_Deck_code_bytes']==54060
    if alias.exists():assert alias.read_bytes()==data
    else:alias.write_bytes(data)
    for source,target in mapping.items():
        text=(S/(source+'.py')).read_text().replace('deck-shared-v34-record-strides-v1','deck-shared-v37-record-loop-advance-v2')
        for a,b in sorted(mapping.items(),key=lambda x:-len(x[0])):text=text.replace(a,b)
        text=text.replace('record-strides','record-loop-image').replace('54134','54060').replace('geometry-records-strides-v1','coordinator-record-loop-advance-v2').replace('terminal_v34_','terminal_v37_')
        # Original CPU maps and existing record begin/end labels are immutable.
        assert 'record-loop-image-fullCPU-generation'not in text
        compile(text,str(S/(target+'.py')),'exec');p=S/(target+'.py')
        if p.exists():assert p.read_text()==text,p
        else:p.write_text(text)
    pipeline=(S/'run_record_stride_qualification_pipeline_v2.py').read_text()
    for a,b in sorted(mapping.items(),key=lambda x:-len(x[0])):pipeline=pipeline.replace(a,b)
    pipeline=pipeline.replace('record-strides','record-loop-image').replace('record-stride-image-qualification-pipeline-v2','record-loop-image-qualification-pipeline-v1').replace('terminal_record_stride','terminal_record_loop_image')
    pipeline=pipeline.replace(" except BaseException as error:"," except subprocess.TimeoutExpired as error:\n  state.update(status='observation_timeout_children_may_be_live',error=repr(error));mark();raise\n except BaseException as error:")
    p=S/'run_record_loop_image_qualification_pipeline_v1.py';compile(pipeline,str(p),'exec')
    if p.exists():assert p.read_text()==pipeline
    else:p.write_text(pipeline)
    proof=dict(status='terminal_isolated_v37_image_check_sources_prepared',same_built_image_pointer=str(alias),canonical_build_pointer=str(bp),both_pointer_bytes_sha256=hashlib.sha256(data).hexdigest(),modules=mapping,new_predictions=0,new_training=False)
    (V/'record-loop-image-check-preparation-v1-current.json').write_text(json.dumps(proof,indent=2)+'\n')
    print('Prepared',len(mapping),'isolated image modules;build alias is byte-identical.',flush=True)

if __name__=='__main__':main()
