import pytest

from net.snapshot_interp import (
    interp_time,
    sort_snapshots,
    interpolate,
    clamp_extrapolate,
    lag_state
)


def test_interp_time():
    assert interp_time(100, 80, 2) == 98

def test_interp_time_zero():
    assert interp_time(100, 80, 0) == 100

def test_sort():
    assert sort_snapshots([{'tick': 2}, {'tick': 1}]) == [{'tick': 1}, {'tick': 2}]

def test_interp_0():
    assert interpolate(1.0, 2.0, 0.0) == 1.0

def test_interp_1():
    assert interpolate(1.0, 2.0, 1.0) == 2.0

def test_interp_half():
    assert interpolate(1.0, 2.0, 0.5) == pytest.approx(1.5)

def test_clamp_max():
    assert clamp_extrapolate(100, 150, 50) == 100

def test_clamp_neg():
    assert clamp_extrapolate(100, 50, 50) == 50

def test_lag_state():
    assert lag_state({'hp': 10}, 5, [{'tick': 5, 'state': {'hp': 10}}]) == {'hp': 10}

def test_lag_missing():
    assert lag_state({'hp': 10}, 9, [{'tick': 5, 'state': {'hp': 10}}]) == {'hp': 10}

def test_lag_empty():
    assert lag_state({'hp': 10}, 5, []) == {'hp': 10}

def test_sort_empty():
    assert sort_snapshots([]) == []

def test_interp_negative():
    assert interpolate(1.0, 2.0, -0.5) == 1.0

def test_interp_over():
    assert interpolate(1.0, 2.0, 1.5) == 2.0

def test_interp_tuple():
    assert interpolate((0.0, 1.0), (2.0, 3.0), 0.5) == pytest.approx((1.0, 2.0))
