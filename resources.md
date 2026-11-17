# Resources

## Official documentation

- [ctypes: A foreign function library for Python](https://docs.python.org/3/library/ctypes.html): how to load shared libraries and declare `argtypes` / `restype`. It confirms that functions are assumed to return a C `int` unless `restype` is set, which explains my garbage-number bug.
- [Integer Objects (Python 3.12 C API)](https://docs.python.org/3.12/c-api/long.html): Python ints are objects, and CPython caches small ints (−5 to 256 in 3.12).
- [What's New in Python 3.11](https://docs.python.org/3/whatsnew/3.11.html): the specializing interpreter, which speeds up common operations like int and float addition.
- [Internal organization of NumPy arrays](https://numpy.org/doc/stable/dev/internals.html): a NumPy array is a data buffer plus metadata describing it.
- [NumPy C-API: Python types and C-structures](https://numpy.org/doc/stable/reference/c-api/types-and-structures.html): the `PyArrayObject` struct (`data`, `dimensions`, `strides`, `descr`, …).
- [numpy.ndarray.ctypes](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.ctypes.html): `a.ctypes.data_as(...)`, which passes NumPy's buffer to C without copying.
- [numpy.sum](https://numpy.org/doc/stable/reference/generated/numpy.sum.html): its Notes section says NumPy uses partial pairwise summation.

## Things I tested myself

- Deleting `restype` in `demo.py` printed garbage (`-1678636568`) instead of `7.0`, confirming what the ctypes docs say about the default return type.
- I added a `sum()` line to `bench_numpy.py` to check the claim that "compiled C" alone doesn't explain NumPy's speed. It held: `sum()` was only about 1.9× faster than the loop.
- All the benchmark numbers in [`results/my_results.md`](results/my_results.md) come from my own runs.

## Other claims you can check yourself

- `python3 -c "import dis; dis.dis('3 + 4')"` shows that Python folds `3 + 4` into the constant `7` before running, which is why `bench_add.py` uses variables.
- `python3 -c "import sys; print(sys.getsizeof(1.0))"` prints `24`, the size of a Python float object.

## AI conversation

- Learning conversation with Claude: https://claude.ai/share/f21b3ddc-ac97-48bd-850a-b7035ffd13c8
