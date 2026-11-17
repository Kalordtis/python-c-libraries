"""
Where NumPy wins and where it doesn't: summing 1 million floats.

Run from the folder containing libmylib.so (needs NumPy: pip install numpy):
    python3 bench_numpy.py
"""
import ctypes
import os
import time

import numpy as np

N = 1_000_000

lib = ctypes.CDLL(os.path.abspath("libmylib.so"))
lib.sum_array.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_size_t]
lib.sum_array.restype = ctypes.c_double

nums = [float(i % 100) for i in range(N)]       # Python list of float objects


def best_of(fn, repeats=5):
    """Run fn several times and keep the fastest time (least noise)."""
    best = float("inf")
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - start)
    return best


def py_loop_list():
    total = 0.0
    for x in nums:
        total += x
    return total


a = np.array(nums)                              # float64 array: one contiguous double[N]
b = (np.arange(N) % 100).astype(np.float64)     # built directly in C, no Python floats


def py_loop_numpy():
    total = 0.0
    for x in a:                                 # each element gets boxed into a new Python object
        total += x
    return total


def ctypes_on_numpy():
    # Pass NumPy's own buffer pointer to your C function: no copy at all.
    ptr = a.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    return lib.sum_array(ptr, a.size)


# Sanity check: every method gives the same sum.
expected = py_loop_list()
for result in (a.sum(), b.sum(), ctypes_on_numpy(), py_loop_numpy()):
    assert abs(result - expected) < 1e-6

rows = [
    ("Python loop over list", best_of(py_loop_list)),
    ("builtin sum(list)  (also C)", best_of(lambda: sum(nums))),
    ("ctypes copy list -> C array", best_of(lambda: (ctypes.c_double * N)(*nums), 3)),
    ("np.array(list) conversion", best_of(lambda: np.array(nums))),
    ("build array in NumPy directly", best_of(lambda: (np.arange(N) % 100).astype(np.float64))),
    ("np.sum(a)", best_of(lambda: np.sum(a))),
    ("your sum_array on NumPy buffer", best_of(ctypes_on_numpy)),
    ("Python loop over NumPy array", best_of(py_loop_numpy, 3)),
]

for name, t in rows:
    print(f"{name:<34}{t * 1000:9.2f} ms")
