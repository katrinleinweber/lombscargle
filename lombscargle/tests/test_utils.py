from __future__ import division
import warnings

import numpy as np
from numpy.testing import (assert_allclose, assert_equal,
                           assert_warns, assert_no_warnings)
import pytest

from .._utils import (factorial, extirpolate, bitceil, trig_sum)


try:
    from scipy.special import factorial as scipy_factorial
except ImportError:
    scipy_factorial = None


def test_factorial():
    if scipy_factorial is None:
        return
    for i in range(20):
        assert_equal(factorial(i), scipy_factorial(i))


@pytest.fixture
def extirpolate_data():
    rng = np.random.RandomState(0)
    x = 100 * rng.rand(50)
    y = np.sin(x)
    f = lambda x: np.sin(x / 10)
    return x, y, f


@pytest.mark.parametrize('N', [100, None])
@pytest.mark.parametrize('M', [5])
def test_extirpolate(N, M, extirpolate_data):
    x, y, f = extirpolate_data
    y_hat = extirpolate(x, y, N, M)
    x_hat = np.arange(len(y_hat))
    assert_allclose(np.dot(f(x), y), np.dot(f(x_hat), y_hat))


@pytest.fixture
def extirpolate_int_data():
    rng = np.random.RandomState(0)
    x = 100 * rng.rand(50)
    x[:25] = x[:25].astype(int)
    y = np.sin(x)
    f = lambda x: np.sin(x / 10)
    return x, y, f


@pytest.mark.parametrize('N', [100, None])
@pytest.mark.parametrize('M', [5])
def test_extirpolate_with_integers(N, M, extirpolate_int_data):
    x, y, f = extirpolate_int_data
    y_hat = extirpolate(x, y, N, M)
    x_hat = np.arange(len(y_hat))
    assert_allclose(np.dot(f(x), y), np.dot(f(x_hat), y_hat))


def slow_bitceil(N):
    return int(2 ** np.ceil(np.log2(N)))


@pytest.mark.parametrize('N', 2 ** np.arange(1, 12))
@pytest.mark.parametrize('offset', [-1, 0, 1])
def test_bitceil(N, offset):
    assert_equal(slow_bitceil(N + offset), bitceil(N + offset))


@pytest.fixture
def trig_sum_data():
    rng = np.random.RandomState(0)
    t = 10 * rng.rand(50)
    h = np.sin(t)
    return t, h

@pytest.mark.parametrize('f0', [0, 1])
@pytest.mark.parametrize('adjust_t', [True, False])
@pytest.mark.parametrize('freq_factor', [1, 2])
@pytest.mark.parametrize('df', [0.1])
def test_trig_sum(f0, adjust_t, freq_factor, df, trig_sum_data):
    t, h = trig_sum_data

    tfit = t - t.min() if adjust_t else t
    S1, C1 = trig_sum(tfit, h, df, N=1000, use_fft=True,
                      f0=f0, freq_factor=freq_factor, oversampling=10)
    S2, C2 = trig_sum(tfit, h, df, N=1000, use_fft=False,
                      f0=f0, freq_factor=freq_factor, oversampling=10)
    assert_allclose(S1, S2, atol=1E-2)
    assert_allclose(C1, C2, atol=1E-2)
