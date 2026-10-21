"""Full-context masked loss with checkpointed, bounded untied output-head chunks.

This preserves installed MLX trainer mask semantics, including padded boundaries.
No prompt/source tokens are removed from the transformer input.
"""
import mlx.core as mx
import mlx.nn as nn


def make_loss(chunk_size):
    if not isinstance(chunk_size,int)or chunk_size<1:raise ValueError('Positive head chunk required')
    def loss(model,batch,lengths,prompt_offset):
        if batch.shape[0]!=1:raise ValueError('Suffix projection requires batch size1')
        if not isinstance(prompt_offset,int):raise ValueError('Pass audited static prompt offset')
        text=model.language_model
        if text.args.tie_word_embeddings:raise ValueError('Only untied output heads supported')
        inputs=batch[:,:-1];targets=batch[:,1:]
        start=max(0,prompt_offset-1)
        if start>=inputs.shape[1]:raise ValueError('No supervised suffix')
        hidden=text.model(inputs)[:,start:]
        targets=targets[:,start:]
        steps=mx.arange(start+1,inputs.shape[1]+1)
        mask=mx.logical_and(steps>=lengths[:,0:1],steps<=lengths[:,1:])
        head=text.lm_head
        def chunk_ce(t,m):
            def projected_ce(params,h):
                head.update(params)
                logits=head(h)
                return (nn.losses.cross_entropy(logits,t)*m).astype(mx.float32).sum()
            return mx.checkpoint(projected_ce)
        total=mx.array(0.0,mx.float32)
        for i in range(0,hidden.shape[1],chunk_size):
            total=total+chunk_ce(targets[:,i:i+chunk_size],mask[:,i:i+chunk_size])(
                head.trainable_parameters(),hidden[:,i:i+chunk_size])
        tokens=mask.sum()
        return total/tokens,tokens
    return loss
