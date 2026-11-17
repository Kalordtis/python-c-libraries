# Why Is NumPy 77× Faster? Python Libraries Implemented in C

**COMP 211 Checkoff 3** · Srikar Ponugoti

Python is known for being easy to write and slow to run, yet libraries like NumPy let Python crunch millions of numbers in under a millisecond. The trick is that the heavy lifting isn't done in Python at all; it's done in C. For this project I explored how that works. I wrote my own C function, called it from Python, and benchmarked plain Python, my own C code and NumPy against each other to find out *where* the speed actually comes from.

## What I explored

1. **Why Python is slow.** Every Python number is a separate heap object (with a reference count and a type pointer), and a Python list is really an array of pointers to those objects. Every `+` means following pointers, checking types, and allocating a new object for the result.
2. **Calling C from Python.** I wrote a C function, compiled it into a shared library (`.so`), and called it from Python using `ctypes`.
3. **The cost of crossing from Python into C.** I benchmarked tiny calls into C against plain Python, then one big call against a Python loop.
4. **How NumPy works.** A NumPy array is a small Python header plus a raw, contiguous C buffer, the same layout as a C array.
5. **Where NumPy's speed comes from.** I lined up a Python loop, `sum()`, my own C loop and `np.sum()` to separate out the different reasons.

## Most interesting discoveries

- **Calling C can make code *slower*.** Calling my C `add()` function a million times through `ctypes` was **34× slower** than plain Python `a + b`. Each crossing from Python into C costs about 760 ns, while the addition itself takes about 1 ns.
- **Cross once, not a million times.** One C call that loops over a million numbers was **14× faster** than a Python loop. But copying a Python list into a C array first took **10× longer** than just summing it in Python.
- **"It's written in C" is only part of the story.** Python's built-in `sum()` is also C, but it's only about 2× faster than a loop. The full **77×** of `np.sum` breaks down as:
  - **1.9×** from compiled C (loop → `sum()`)
  - **7.2×** from raw contiguous data and a single type check (`sum()` → my C loop on NumPy's buffer)
  - **5.5×** from NumPy's SIMD-tuned loop (my C loop → `np.sum`)
  - 1.9 × 7.2 × 5.5 ≈ 77
- **NumPy can be slower than plain Python.** A Python `for` loop over a NumPy array was **9× slower** than looping over a list, because NumPy has to turn every raw number back into a Python object.
- **Forgetting a type declaration fails silently.** Without `restype`, ctypes assumed my function returned an `int` and printed `-1678636568` instead of `7.0`. It didn't crash, it just returned garbage.

**Key takeaway:** crossing from Python into C costs something every time. C only wins when each call does a lot of work on data that's already stored the C way, and NumPy is built around exactly that.

My full numbers are in [`results/my_results.md`](results/my_results.md).

## Repository layout

```
README.md               this file
code/
  mylib.c               C functions: add() and sum_array()
  demo.py               calls mylib.c from Python with ctypes
  bench_add.py          1M tiny ctypes calls vs plain Python a + b
  bench_batch.py        one ctypes call that loops 1M times vs a Python loop
  bench_numpy.py        Python loop vs sum() vs my C loop vs NumPy
results/
  my_results.md         the output I got on my machine
slides/
  slides.pdf            presentation slides
  slides_text.md        slide text and speaking notes
  *.png                 diagrams and charts used in the slides
resources.md            documentation and references I used
```

## How to run the code

You need `gcc`, Python 3, and NumPy (only needed for `bench_numpy.py`). I ran everything on Linux (my COMP 211 dev container).

```bash
cd code

# 1. Compile the C file into a shared library
gcc -shared -fPIC -O2 -o libmylib.so mylib.c

# 2. Call C from Python (should print 5 and 7.0)
python3 demo.py

# 3. Run the benchmarks
python3 bench_add.py
python3 bench_batch.py

# 4. NumPy benchmark (install NumPy first if needed)
python3 -m pip install numpy
python3 bench_numpy.py
```

On macOS without a container, the same `gcc` command works. On Windows, use WSL.

## How I used AI

I learned this topic through a conversation with Claude. I asked questions, ran every experiment myself, reported my results back, explained the topic in my own words to get it checked, and quizzed myself. My written reflection covers the process in more detail.
