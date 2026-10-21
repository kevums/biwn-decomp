"""Retain v40 checks; actor helper checks protect original public save frames.

Phased actors have no parked C context across helpers. Their helper ABI,
original public save frames, return words and physical task bounds remain
observed. Legacy context counters now describe those public save frames.
"""
import re
import shared_deck_frame_phased_image_full_observer_v3 as prior
ROOT = prior.ROOT


def actor_watchers(text, build):
    ranges = {}
    for name in ['dispatch', 'initialize']:
        start = text.index('static void watch_actor_' + name + '(uint32_t pc){')
        end = text.index('\n}', start) + 2
        ranges[name] = (start, end, text[start:end])
    a, z, dispatch = ranges['dispatch']
    old = '''            uint32_t floor=call->sp-264u;
            if(call->native&&sp<floor){ad_child_below_context++;if(sp>=call->sp-336u)ad_context_SP_inside++;}
            if(sp>=floor&&sp-floor<ad_min_context_clearance)ad_min_context_clearance=sp-floor;
'''
    assert dispatch.count(old) == 1
    dispatch = dispatch.replace(old, '')
    old = 'if(call->native)for(unsigned i=0;i<18;i++)call->context[i]=rd32(call->sp-336u+4u*i);'
    new = 'if(call->native)for(unsigned i=0;i<4;i++){call->context[i]=rd32(call->sp-16u+4u*i);if(call->context[i]!=call->incoming.r[2u+i])ad_errors++;}'
    assert dispatch.count(old) == 1
    dispatch = dispatch.replace(old, new)
    old = 'for(unsigned i=0;i<18;i++)if(rd32(call->sp-336u+4u*i)!=call->context[i])ad_context_collisions++;'
    assert dispatch.count(old) == 1
    dispatch = dispatch.replace(old, 'for(unsigned i=0;i<4;i++)if(rd32(call->sp-16u+4u*i)!=call->context[i])ad_context_collisions++;')
    symbols = build['actor_phased_symbols']['dispatch']
    dispatch, count = re.subn(r'if\(pc==\d+u\|\|pc==\d+u\|\|pc==0x13b3au\|\|pc==0x13b50u\)',
        f"if(pc=={symbols['biwn_actor_dispatch_after_actor']}u||pc=={symbols['biwn_actor_dispatch_after_sprite']}u||pc==0x13b3au||pc==0x13b50u)", dispatch)
    assert count == 1
    old = str(build['actor_dispatch_return']) + 'u'
    assert dispatch.count(old) == 1
    dispatch = dispatch.replace(old, str(symbols['biwn_native_actor_dispatch_return']) + 'u')
    a, z, initialize = ranges['initialize']
    old = '''   for(unsigned i=0;i<19;i++)call->context[i]=rd32(call->sp-480u+4u*i);
   for(unsigned i=0;i<15;i++)if(call->context[i]!=current.r[i])ai_errors++;
   if(call->context[15]!=call->sp||(call->context[16]&0xffffu)!=current.sr)ai_errors++;'''
    new = '''   const unsigned saved[]={2,3,4,5,6,7,10,11};
   for(unsigned i=0;i<8;i++){call->context[i]=rd32(call->sp-32u+4u*i);if(call->context[i]!=call->incoming.r[saved[i]])ai_errors++;}'''
    assert initialize.count(old) == 1
    initialize = initialize.replace(old, new)
    old = 'for(unsigned i=0;i<19;i++)if(rd32(call->sp-480u+4u*i)!=call->context[i])ai_context_corruptions++;'
    assert initialize.count(old) == 1
    initialize = initialize.replace(old, 'for(unsigned i=0;i<8;i++)if(rd32(call->sp-32u+4u*i)!=call->context[i])ai_context_corruptions++;')
    symbols = build['actor_phased_symbols']['initialize']
    for kind in ['outside', 'inside', 'task']:
        old = str(build['actor_initialize_helper_returns'][kind]) + 'u'
        assert initialize.count(old) == 1
        initialize = initialize.replace(old, str(symbols['biwn_actor_initialize_after_' + kind]) + 'u')
    old = str(build['actor_initialize_return']) + 'u'
    assert initialize.count(old) == 1
    initialize = initialize.replace(old, str(symbols['biwn_native_actor_initialize_return']) + 'u')
    for name, replacement in [('initialize', initialize), ('dispatch', dispatch)]:
        start, end, _ = ranges[name]
        text = text[:start] + replacement + text[end:]
    return text


def observer_source(build, parent):
    text, source = prior.observer_source(build, parent)
    return actor_watchers(text, build), source
