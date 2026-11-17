# My benchmark results

All runs were on my COMP 211 dev container: **Python 3.12.3, NumPy 2.5.5, aarch64 (ARM) Linux, running on a Mac**. Each benchmark keeps the best of several runs to reduce noise. Your numbers will be different on a different machine, but the pattern should be the same.

## demo.py: calling C with ctypes

```
5
7.0
```

With the `lib.sum_array.restype` line deleted, ctypes assumed the function returns an `int` and read the wrong register:

```
5
-1678636568
```

## bench_add.py: 1 million tiny calls into C vs plain Python

```
empty loop (baseline)       14.4 ms
Python a + b                22.8 ms   (   8.4 ns per add, minus loop)
ctypes c_add(a, b)         774.3 ms   ( 759.9 ns per call, minus loop)

ratio ctypes / Python: 33.9x
```

**Takeaway:** calling C once per number is about 34x *slower*, because each Python → C crossing costs about 760 ns.

## bench_batch.py: one call into C that loops 1 million times

```
Python loop over 1M floats        12.75 ms
ONE ctypes call, C loops 1M        0.94 ms
  one-time list -> C array copy   124.65 ms

speedup (loop only): 14x
copy + one C call vs Python loop: 9.8x the Python time
```

**Takeaway:** the C loop is 14x faster, but converting the Python list into a C array first costs about 10x more than just summing in Python.

## bench_numpy.py: where NumPy wins and where it doesn't

```
Python loop over list                 13.16 ms
builtin sum(list)  (also C)            6.78 ms
ctypes copy list -> C array          124.16 ms
np.array(list) conversion             28.92 ms
build array in NumPy directly          2.61 ms
np.sum(a)                              0.17 ms
your sum_array on NumPy buffer         0.94 ms
Python loop over NumPy array         118.38 ms
```

**Takeaways:**
- `np.sum` is about **77x** faster than the Python loop.
- `sum()` is also written in C, but it's only about 1.9x faster than the loop, because it still works on Python objects.
- My plain C loop on NumPy's buffer is 7.2x faster than `sum()` (raw data, no per-element type checks).
- `np.sum` is still 5.5x faster than my C loop (NumPy's loop is tuned for SIMD).
- 1.9 × 7.2 × 5.5 ≈ 77.
- Looping over a NumPy array *in Python* is 9x slower than looping over a list, because every element gets turned back into a Python object.
