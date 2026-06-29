"""Tests for the z-score anomaly detector."""
from aengus import zscore


def test_returns_zero_when_too_little_history():
    # fewer than 5, values not enough to judge should return 0
    assert zscore([1.0, 2.0, 3.0]) == 0.0


def test_returns_zero_on_flat_history():
    # all identical, standard deviation is 0 no deviation possible
    assert zscore([5.0, 5.0, 5.0, 5.0, 5.0, 5.0]) == 0.0


def test_flags_a_clear_spike():
    # steady-ish baseline then a big jump should score well above 3
    history = [2.0, 2.1, 1.9, 2.0, 2.05, 10.0]
    assert zscore(history) > 3


def test_normal_value_scores_low():
    # a value close to the recent mean should score near zero
    history = [2.0, 2.1, 1.9, 2.0, 2.05, 2.02]
    assert abs(zscore(history)) < 1