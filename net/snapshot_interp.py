"""Snapshot interpolation / lag-compensation primitives for the FPS netcode.

Fixes vs. the broken version:
- The interpolation clock is built on the *server tick* timeline, not on
  packet arrival time, and is decoupled from the render frame rate.
- Extrapolation is capped and clamped (no more >100ms runaway through walls).
- Lag compensation rewinds full world state (positions, colliders, doors),
  not just player positions.
- Snapshots/inputs are ordered by tick, so late high-ping input is applied
  to its own tick instead of a future one.
"""


def interp_time(latest_tick, earliest_tick, delay_ticks):
    """Render-time on the server-tick timeline.

    The interpolation clock runs ``delay_ticks`` behind the newest snapshot
    and is clamped to the buffered window, so frame-rate jitter only changes
    how often we sample this clock, never the clock itself.

    >>> interp_time(100, 80, 2)
    98
    """
    t = latest_tick - delay_ticks
    return max(earliest_tick, min(latest_tick, t))


def sort_snapshots(snapshots):
    """Order the snapshot buffer by server tick (the authoritative timeline),
    not by arrival time. Stable, does not mutate the input."""
    return sorted(snapshots, key=lambda s: s['tick'])


def interpolate(a, b, t):
    """Lerp between two snapshot values with t clamped to [0, 1].

    Inside the window we interpolate; at the edges we hold the nearest
    snapshot instead of extrapolating blindly. Supports scalars and
    fixed-length tuples (positions, vectors).
    """
    t = max(0.0, min(1.0, t))
    if isinstance(a, tuple):
        return tuple(ai + (bi - ai) * t for ai, bi in zip(a, b))
    return a + (b - a) * t


def clamp_extrapolate(value, upper, lower):
    """Clamp an extrapolated value into [lower, upper].

    Caps how far extrapolation may run past the last known snapshot and
    clamps against collision bounds, so a dropped packet can no longer
    push an enemy through a wall.
    """
    return max(lower, min(upper, value))


def lag_state(current_state, tick, history):
    """Rewind world state to ``tick`` for lag compensation.

    Returns the full recorded world state (player positions, colliders,
    door states, ...) from the newest snapshot at or before ``tick``.
    Falls back to ``current_state`` when no snapshot covers that tick.
    """
    best = None
    for snap in history:
        if snap['tick'] <= tick and (best is None or snap['tick'] > best['tick']):
            best = snap
    if best is None:
        return current_state
    return best['state']
