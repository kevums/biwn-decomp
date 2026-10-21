"""Reuse checked instruction semantics for the boundary-disc extension."""
import biwn_cache_cluster_CPU_semantics as cache
import native_formatter_C_semantics as formatter


def handles(row):
    if cache.handles(row):
        return True
    op,args=cache.parts(row)
    return op=='movem.l' and all(not s.startswith('-(') and not s.endswith('+') for s in args)


def emit(row):
    if cache.handles(row):
        return cache.emit(row)
    # Includes the boundary shim's four-register forward MOVEM. The existing
    # formatter emitter captures the effective address before register loads.
    return formatter.emit(row)
