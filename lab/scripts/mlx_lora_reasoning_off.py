"""Run installed MLX LoRA with explicit reasoning-off dataset rendering.

The override lives only in this process. Installed libraries, model weights and
tokenizer files are unchanged. Use this same renderer for loss comparisons.
"""
import mlx_lm.lora as lora


class ReasoningOffTokenizer:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def __getattr__(self, name):
        return getattr(self.tokenizer, name)

    def apply_chat_template(self, *args, **kwargs):
        kwargs['enable_thinking'] = False
        return self.tokenizer.apply_chat_template(*args, **kwargs)


def main():
    import os,json
    if 'LOCAL_AI_TRAIN_CACHE_BYTES' in os.environ:
        import mlx.core as mx
        limit=int(os.environ['LOCAL_AI_TRAIN_CACHE_BYTES']);assert limit>=0
        previous=mx.set_cache_limit(limit)
        print(json.dumps({'process_MLX_cache_limit_bytes':limit,'previous_cache_limit_bytes':previous,'device_info':mx.device_info()}),flush=True)
    if 'LOCAL_AI_BATCH_AUDIT_PATH' in os.environ:
        from pathlib import Path
        from mlx_lm.tuner.trainer import iterate_batches,TrainingCallback
        original_train=lora.train
        counts={'train':0,'validation':0}
        audit=Path(os.environ['LOCAL_AI_BATCH_AUDIT_PATH'])
        chunk=int(os.environ.get('LOCAL_AI_TARGET_HEAD_CHUNK','0'))
        if chunk:
            from target_chunk_loss import make_loss
            custom_loss=make_loss(chunk)
        def ordered_batches(*args,**kwargs):
            stream=iter(iterate_batches(*args,**kwargs))
            if chunk and kwargs.get('loop') and os.environ.get('LOCAL_AI_LONGEST_FIRST')=='1':
                first=[next(stream)for _ in range(len(kwargs['dataset']))]
                first.sort(key=lambda b:b[0].shape[1],reverse=True)
                yield from first
            yield from stream
        def observed_batches(*args,**kwargs):
            kind='train'if kwargs.get('loop')else'validation'
            for batch in ordered_batches(*args,**kwargs):
                counts[kind]+=1
                lengths=batch[1].tolist()
                row={'kind':kind,'batch':counts[kind],'shape':list(batch[0].shape),'lengths':lengths}
                if chunk:
                    assert batch[0].shape[0]==1
                    offset=int(lengths[0][0]);row['static_prompt_offset']=offset;row['head_chunk']=chunk
                with audit.open('a')as stream:stream.write(json.dumps(row)+'\n')
                yield (*batch,offset)if chunk else batch
        class MemoryAudit(TrainingCallback):
            def __init__(self,parent):self.parent=parent
            def on_train_loss_report(self,report):
                with audit.with_name('training-memory.jsonl').open('a')as stream:stream.write(json.dumps(report)+'\n')
                if self.parent:self.parent.on_train_loss_report(report)
            def on_val_loss_report(self,report):
                with audit.with_name('training-validation.jsonl').open('a')as stream:stream.write(json.dumps(report)+'\n')
                if self.parent:self.parent.on_val_loss_report(report)
        def observed_train(*args,**kwargs):
            kwargs['iterate_batches']=observed_batches
            if chunk:
                kwargs['loss']=custom_loss
                kwargs['training_callback']=MemoryAudit(kwargs.get('training_callback'))
            return original_train(*args,**kwargs)
        lora.train=observed_train
    original_load = lora.load

    def load_off(*args, **kwargs):
        model, tokenizer = original_load(*args, **kwargs)
        return model, ReasoningOffTokenizer(tokenizer)

    lora.load = load_off
    lora.main()


if __name__ == '__main__':
    main()
