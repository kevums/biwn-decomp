"""Choose actual saved weights using macro mean of three frozen development losses."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def select_checkpoint(model,tokenizer,job,data):
    import mlx.core as mx
    from mlx_lm.tuner.utils import load_adapters
    from target_chunk_loss import make_loss
    job=Path(job);data=Path(data);manifest=json.loads((data/'split-manifest.json').read_text())
    assert sha(data/'valid.jsonl')==manifest['split_sha256']['valid']
    rows=[json.loads(line)['messages']for line in(data/'valid.jsonl').read_text().splitlines()];assert len(rows)==3
    cases=[]
    for messages in rows:
        full=tokenizer.apply_chat_template(messages,tokenize=True,add_generation_prompt=False,enable_thinking=False)
        prefix=tokenizer.apply_chat_template(messages[:-1],tokenize=True,add_generation_prompt=True,enable_thinking=False)
        assert full[:len(prefix)]==prefix and len(full)<=8960
        cases.append((mx.array([full]),mx.array([[len(prefix),len(full)]]),len(prefix)))
    checkpoints=sorted((job/'adapters').glob('[0-9]*_adapters.safetensors'));assert [int(p.name.split('_')[0])for p in checkpoints]==list(range(8,65,8))
    load_adapters(model,str(job/'adapters'));model.eval();loss_function=make_loss(128);scores=[]
    for path in checkpoints:
        step=int(path.name.split('_')[0]);model.load_weights(str(path),strict=False);mx.eval(model.parameters());losses=[]
        for batch,lengths,offset in cases:
            value,count=loss_function(model,batch,lengths,offset);mx.eval(value,count);assert int(count.item())>0
            losses.append(dict(masked_loss=float(value.item()),supervised_tokens=int(count.item())));mx.clear_cache()
        macro=sum(row['masked_loss']for row in losses)/len(losses)
        scores.append(dict(step=step,validation_loss=macro,per_example=losses,adapter_sha256=sha(path)))
        print('actual advertising checkpoint',step,'macro validation',round(macro,6),flush=True)
    best=min(scores,key=lambda r:(r['validation_loss'],r['step']));selected=job/'selected-adapter';selected.mkdir()
    path=job/'adapters'/f'{best["step"]:07d}_adapters.safetensors'
    shutil.copy2(path,selected/'adapters.safetensors');shutil.copy2(job/'adapters/adapter_config.json',selected/'adapter_config.json')
    model.load_weights(str(path),strict=False);mx.eval(model.parameters());mx.clear_cache()
    proof=job/'checkpoint-selection-proof';proof.mkdir()
    trainer=Path(__import__('mlx_lm.tuner.trainer',fromlist=['__file__']).__file__)
    for source,name in [(Path(__file__),'selector-as-run.py'),(trainer,'installed-trainer-as-run.py'),(ROOT/'scripts/target_chunk_loss.py','loss-as-run.py')]:shutil.copy2(source,proof/name)
    selection=dict(selected_step=best['step'],validation_loss=best['validation_loss'],validation_checkpoints=scores,selected_adapter=str(selected),adapter_sha256=sha(selected/'adapters.safetensors'),validation_sha256=sha(data/'valid.jsonl'),
       policy='Arithmetic mean of three per-example masked losses on actual saved8..64checkpoints; earliest ties. Test outputs not used.',trainer_log_selection_used=False,test_generated_before_selection=False,selector_sha256=sha(Path(__file__)),loss_sha256=sha(ROOT/'scripts/target_chunk_loss.py'),recorded_at=datetime.now(timezone.utc).isoformat())
    (job/'checkpoint-selection.json').write_text(json.dumps(selection,indent=2)+'\n')
    (ROOT/'verification/advertising-v10-checkpoint-selection-current.json').write_text(json.dumps(selection,indent=2)+'\n')
    return selection
