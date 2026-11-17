"""
Benchmark: 1 million calls to C add() via ctypes vs. 1 million a + b in a Python loop.

Run from the folder containing libmylib.so:
    python3 bench_add.py
"""
import ctypes
import os
import time

N = 1_000_000

lib = ctypes.CDLL(os.path.abspath("libmylib.so"))
lib.add.argtypes = [ctypes.c_int, ctypes.c_int]
lib.add.restype = ctypes.c_int
c_add = lib.add          # look up the function once, outside the loop

# Use variables, not the literals 3 + 4: Python's compiler folds "3 + 4"
# into the constant 7 before the program runs, so the loop would do no addition.
a, b = 3, 4


def bench_ctypes():
    for _ in range(N):
        c_add(a, b)


def bench_python():
    for _ in range(N):
        a + b


def bench_empty():
    for _ in range(N):
        pass


def best_of(fn, repeats=5):
    """Run fn several times and keep the fastest time (least noise)."""
    best = float("inf")
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - start)
    return best


# Sanity check that both compute the same thing.
assert c_add(a, b) == a + b == 7

t_empty = best_of(bench_empty)
t_py = best_of(bench_python)
t_c = best_of(bench_ctypes)

print(f"{'empty loop (baseline)':<24}{t_empty * 1000:8.1f} ms")
print(f"{'Python a + b':<24}{t_py * 1000:8.1f} ms   ({(t_py - t_empty) / N * 1e9:6.1f} ns per add, minus loop)")
print(f"{'ctypes c_add(a, b)':<24}{t_c * 1000:8.1f} ms   ({(t_c - t_empty) / N * 1e9:6.1f} ns per call, minus loop)")
print(f"\nratio ctypes / Python: {t_c / t_py:.1f}x")
