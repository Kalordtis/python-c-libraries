"""
Benchmark: summing 1 million floats with a Python loop vs. ONE ctypes call
to the C function sum_array(), which loops over a C array.

Run from the folder containing libmylib.so:
    python3 bench_batch.py
"""
import ctypes
import os
import time

N = 1_000_000

lib = ctypes.CDLL(os.path.abspath("libmylib.so"))
lib.sum_array.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_size_t]
lib.sum_array.restype = ctypes.c_double

nums = [float(i % 100) for i in range(N)]       # a normal Python list of float objects

# One-time conversion: copy every Python float into a contiguous C double[N].
start = time.perf_counter()
arr = (ctypes.c_double * N)(*nums)
t_convert = time.perf_counter() - start


def py_loop():
    total = 0.0
    for x in nums:
        total += x
    return total


def c_one_call():
    return lib.sum_array(arr, N)                # cross into C once; C does all N adds


def best_of(fn, repeats=5):
    """Run fn several times and keep the fastest time (least noise)."""
    best = float("inf")
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - start)
    return best


# Sanity check that both compute the same sum.
assert abs(py_loop() - c_one_call()) < 1e-6

t_py = best_of(py_loop)
t_c = best_of(c_one_call)

print(f"{'Python loop over 1M floats':<30}{t_py * 1000:9.2f} ms")
print(f"{'ONE ctypes call, C loops 1M':<30}{t_c * 1000:9.2f} ms")
print(f"{'  one-time list -> C array copy':<30}{t_convert * 1000:9.2f} ms")
print(f"\nspeedup (loop only): {t_py / t_c:.0f}x")
print(f"copy + one C call vs Python loop: {(t_convert + t_c) / t_py:.1f}x the Python time")
