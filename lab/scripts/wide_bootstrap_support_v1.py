"""Planning and assembly for an uninstalled wider-copy startup prototype.

The module, arena and heap providers still need relinking and final-image
qualification. A feasible layout is not a built or approved game image.
"""


def align(value, multiple):
    return (value + multiple - 1) // multiple * multiple


def plan_input_layout(build, module_bytes):
    if type(module_bytes) is not int or module_bytes < 2 or module_bytes % 2:
        raise ValueError('Module must have a positive even byte count')
    native = build['resident_address']
    input_address = build['deck_finalizer_address']
    finalizer = align(input_address + module_bytes, 4)
    deck = align(finalizer + 384, 64)
    outer = deck + build['deck_arena_bytes']
    heap = outer + build['outer_arena_bytes']
    copy_bytes = deck - native
    clear_bytes = align(40 + copy_bytes, 64)
    staging = 0xfe200 - clear_bytes
    if not (0 < copy_bytes <= 262144 and 0 < clear_bytes <= 262144
            and copy_bytes % 4 == clear_bytes % 4 == 0
            and staging >= 0xd9d28 and staging % 4 == 0 and heap < 0x1c0000):
        raise ValueError('Layout exceeds wide-loop, original blank staging or heap bounds')
    return dict(native_address=native, input_address=input_address,
        input_bytes=module_bytes, finalizer_address=finalizer,
        finalizer_reservation=384, deck_arena_address=deck,
        deck_arena_bytes=build['deck_arena_bytes'], outer_arena_address=outer,
        outer_arena_bytes=build['outer_arena_bytes'], heap_start=heap,
        initial_heap_bytes=0x1c0000-heap, copy_bytes=copy_bytes,
        clear_bytes=clear_bytes, staging_address=staging,
        legacy_word_copy_capacity=131072, wide_long_copy_capacity=262144,
        copy_exceeds_legacy_word_loop=copy_bytes>131072,
        clear_exceeds_legacy_word_loop=clear_bytes>131072,
        relink_module_arenas_and_heap_required=True,
        final_image_qualified=False, game_image_written=False)


def stage_clear_lines(staging, clear_bytes):
    if (type(staging) is not int or type(clear_bytes) is not int
            or staging < 0 or staging % 4 or clear_bytes < 4
            or clear_bytes > 262144 or clear_bytes % 4
            or staging + clear_bytes > 0x200000):
        raise ValueError('Invalid clear range')
    return [f'lea {hex(staging)},%a0',f'move.w #{clear_bytes//4-1},%d0',
            'wide_stage_clear:','clr.l (%a0)+','dbra %d0,wide_stage_clear']
