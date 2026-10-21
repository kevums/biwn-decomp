"""Score actual saved adapter weights on frozen validation, before any resource generation."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]

def select_checkpoint(model,tokenizer,job,data):
    import mlx.core as mx
    from mlx_lm.tuner.utils import load_adapters
    from target_chunk_loss import make_loss
    job=Path(job);data=Path(data);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    manifest=json.loads((data/'split-manifest.json').read_text());assert sha(data/'valid.jsonl')==manifest['split_sha256']['valid']
    validation=[json.loads(line)['messages']for line in(data/'valid.jsonl').read_text().splitlines()];assert len(validation)==1
    cases=[]
    for messages in validation:
        full=tokenizer.apply_chat_template(messages,tokenize=True,add_generation_prompt=False,enable_thinking=False)
        prefix=tokenizer.apply_chat_template(messages[:-1],tokenize=True,add_generation_prompt=True,enable_thinking=False)
        assert full[:len(prefix)]==prefix and len(full)<=8960
        cases.append((mx.array([full]),mx.array([[len(prefix),len(full)]]),len(prefix)))
    checkpoints=sorted((job/'adapters').glob('[0-9]*_adapters.safetensors'));assert len(checkpoints)==8
    # Install LoRA modules once; subsequent loads update only their weights.
    load_adapters(model,str(job/'adapters'));model.eval();loss_function=make_loss(128);scores=[]
    for path in checkpoints:
        step=int(path.name.split('_')[0]);model.load_weights(str(path),strict=False);mx.eval(model.parameters())
        total=0.0;tokens=0
        for batch,lengths,offset in cases:
            value,count=loss_function(model,batch,lengths,offset);mx.eval(value,count);total+=float(value.item())*int(count.item());tokens+=int(count.item())
        assert tokens>0;scores.append(dict(step=step,validation_loss=total/tokens,supervised_tokens=tokens,adapter_sha256=sha(path)))
        mx.clear_cache();print('actual saved checkpoint',step,'validation',round(total/tokens,6),flush=True)
    best=min(scores,key=lambda row:(row['validation_loss'],row['step']));selected=job/'selected-adapter';selected.mkdir(exist_ok=True)
    original=job/'checkpoint-selection.json'
    if original.exists():shutil.copy2(original,job/'initial-log-selection-not-used.json')
    path=job/'adapters'/f'{best["step"]:07d}_adapters.safetensors';shutil.copy2(path,selected/'adapters.safetensors');shutil.copy2(job/'adapters/adapter_config.json',selected/'adapter_config.json')
    # Leave the caller's model on exactly the selected weights.
    model.load_weights(str(path),strict=False);mx.eval(model.parameters());mx.clear_cache()
    trainer=Path(__import__('mlx_lm.tuner.trainer',fromlist=['__file__']).__file__)
    proof_directory=job/'checkpoint-selection-proof';proof_directory.mkdir(exist_ok=True)
    for source,name in [(Path(__file__),'selector-as-run.py'),(trainer,'installed-trainer-as-run.py'),(ROOT/'scripts/target_chunk_loss.py','loss-as-run.py')]:shutil.copy2(source,proof_directory/name)
    selection=dict(selected_step=best['step'],validation_loss=best['validation_loss'],validation_checkpoints=scores,selected_adapter=str(selected),adapter_sha256=sha(selected/'adapters.safetensors'),
        test_generated_before_selection=False,recorded_at=datetime.now(timezone.utc).isoformat(),policy='Lowest loss on the frozen scheduler validation target, evaluated on actual saved checkpoints; earliest step wins ties.',
        source='Actual checkpoint rescoring, not pre-update trainer log labels',reason='Installed trainer evaluates before updateN then saves checkpointN after that update. Initial log-based selection is archived and not used for resource generation.',
        validation_sha256=sha(data/'valid.jsonl'),trainer_source=str(trainer),trainer_sha256=sha(trainer),selector_sha256=sha(Path(__file__)),loss_function_sha256=sha(ROOT/'scripts/target_chunk_loss.py'),resource_targets_used=False)
    original.write_text(json.dumps(selection,indent=2)+'\n');(ROOT/'verification/game-geometry-checkpoint-selection-v4-current.json').write_text(json.dumps(selection,indent=2)+'\n')
    return selection
