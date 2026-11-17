# Slide text: copy and paste

Each slide has three parts: **what goes on the slide**, **which image to paste** (if any), and **what to say**. The "what to say" parts together run about 6 minutes. Practice them out loud, but don't read them word for word.

---

## Slide 1: Title

**On the slide:**
- Title: Why is NumPy 77x faster than a Python loop?
- Subtitle: Python Libraries Implemented in C
- Srikar Ponugoti, COMP 211 Checkoff 3

**Say:**
Hi, I'm Srikar. My topic is Python libraries that are implemented in C, like NumPy. We've spent the whole semester writing C, so I wanted to see how C ends up powering Python. The 77x in the title is a real number I measured myself.

---

## Slide 2: The question

**On the slide:**
- Title: Same task: add up 1,000,000 numbers
- Python for-loop: 13.16 ms
- NumPy np.sum(): 0.17 ms
- Same computer, same numbers. Why is NumPy 77x faster?

**Say:**
I added up a million numbers two ways in my COMP 211 dev container. A normal Python for-loop took about 13 milliseconds, and NumPy took 0.17 milliseconds. That's 77 times faster for the exact same math. It turns out the reason is mostly stuff we've learned about memory in this class.

---

## Slide 3: Why Python is slow

**On the slide:**
- Title: Every Python number is a separate object
- Image: `1_memory_layout.png`

**Say:**
On the left is a C array like the ones we use in class: one block of memory, with the numbers right next to each other. On the right is a Python list. It's actually an array of pointers, and each number is its own 24-byte object on the heap, with a reference count and a type. So every time Python adds two numbers, it has to follow a pointer, check the type, find the right add function, and create a new object for the result. C does the same addition in about one instruction.

---

## Slide 4: Calling C from Python

**On the slide:**
- Title: I wrote a C function and called it from Python
- Step 1, write normal C (mylib.c):
```c
double sum_array(const double *arr, size_t n) {
    double total = 0.0;
    for (size_t i = 0; i < n; i++)
        total += arr[i];
    return total;
}
```
- Step 2, compile it into a shared library:
```
gcc -shared -fPIC -o libmylib.so mylib.c
```
- Step 3, load it in Python with ctypes:
```python
lib = ctypes.CDLL("./libmylib.so")
lib.sum_array.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_size_t]
lib.sum_array.restype = ctypes.c_double
```
- Bug I tried on purpose: deleting the restype line made it print -1678636568 instead of 7.0

**Say:**
To understand how this works, I did it myself with a tool called ctypes. Step one is a normal C function. Step two compiles it with -shared and -fPIC, which makes a library instead of a program, so there's no main. Step three loads it from Python. The catch is that Python can't read C header files, so you have to tell it the types yourself. I tested that by deleting the restype line. Python then assumed the function returned an int, and I got a garbage number instead of 7.0.

---

## Slide 5: Prediction (audience question)

**On the slide:**
- Title: Quick prediction: which is faster?
- I add two numbers 1,000,000 times:
  - A) Call my C add() function through ctypes
  - B) Plain Python: a + b
- Raise your hand: A or B?

**Say:**
Quick prediction. I wrote an add function in C and called it a million times from Python. Then I did a + b in plain Python a million times. We all know C is faster than Python, right? Raise your hand if you think A, C through ctypes, is faster. Now B, plain Python. *(Pause and count the hands.)*

---

## Slide 6: The answer

**On the slide:**
- Title: Plain Python won. C was 34x slower.
- Image: `2_ctypes_vs_python.png`
- Every trip from Python into C costs about 750 ns. The addition itself takes about 1 ns.

**Say:**
The answer is B, by a lot. The C version was 34 times slower. The addition inside C is basically free. But every call from Python into C has to convert the Python numbers into C ints, make the call, and convert the answer back into a Python object. That crossing cost about 760 nanoseconds per call. So if each call does almost no work, going into C is a waste.

---

## Slide 7: Cross into C once

**On the slide:**
- Title: Cross into C once, not a million times
- Summing 1,000,000 numbers:
  - Python loop: 12.75 ms
  - ONE C call that loops 1M times: 0.94 ms (14x faster)
- The catch: copying the Python list into a C array first took 124.65 ms, 10x longer than just summing in Python

**Say:**
So I flipped it around. I called C once and let the loop run inside C. Now C wins by 14 times. But my numbers started out in a Python list, and copying them into a C array took 124 milliseconds, ten times longer than just adding them up in Python. So C only helps if the data is already in C form. That's exactly the problem NumPy solves.

---

## Slide 8: How NumPy works

**On the slide:**
- Title: NumPy stores numbers the C way
- Image: `4_numpy_layout.png`
- Arrays are created in C (np.arange, np.zeros), math runs in C (a + b, a.sum()), and results stay in C
- 1 million floats: 8 MB in NumPy vs about 32 MB in a Python list

**Say:**
A NumPy array is basically a C array with one small Python header in front. The header says where the data is, the shape, and the type. The numbers themselves are raw doubles packed together, just like the C array from earlier. NumPy doesn't make converting data cheap. It makes converting rare: you create arrays in C, do math with one call that loops in C, and the results stay in C. It also uses about a quarter of the memory.

---

## Slide 9: Where the 77x comes from

**On the slide:**
- Title: Being written in C is only part of the story
- Image: `3_four_ways_to_sum.png`
- Compiled C (loop → sum()): 1.9x
- Raw data + one type check (sum() → my C loop): 7.2x
- SIMD-tuned loop (my C loop → np.sum): 5.5x
- 1.9 × 7.2 × 5.5 ≈ 77

**Say:**
I wanted to know which part actually makes NumPy fast, so I lined up four versions. Python's built-in sum() is also written in C, but it's only about 2 times faster than the loop, because it still goes through a list of pointers and checks every element's type. My own C loop on NumPy's raw data is 7 times faster than that: no pointers, no objects, and one type check for the whole array. Then np.sum is still 5.5 times faster than my C, because NumPy's loop is tuned to use SIMD, which adds several numbers at once. Multiply those together and you get the 77. The biggest piece is the memory layout, not just the fact that it's written in C.

---

## Slide 10: Surprises

**On the slide:**
- Title: NumPy can be slower than plain Python
- Looping over a NumPy array in Python: 118.38 ms, 9x slower than looping over a list (every element gets turned back into a Python object)
- np.sum() on a Python list: the list → array conversion alone takes 28.92 ms, more than the whole Python loop

**Say:**
Two things surprised me. First, if you write a normal for-loop over a NumPy array, it's 9 times slower than looping over a list, because NumPy has to turn every raw number back into a Python object. Second, if you call np.sum on a regular list, NumPy has to convert the whole list first, and that conversion alone takes longer than just looping in Python. So NumPy is only fast if you stay inside NumPy.

---

## Slide 11: Takeaway + Questions

**On the slide:**
- Takeaway: Crossing from Python into C costs something every time. C only wins when each call does a lot of work on data that's already in C.
- Questions?
- Code and benchmarks: github.com/[your-username]/[repo-name]

**Say:**
If you remember one thing: crossing from Python into C has a cost every time. Calling C on single numbers loses, and converting a list every time loses. C wins when you cross once and do a lot of work on data that's already stored the C way, and that's what NumPy is built around. What surprised me most is that "written in C" was the smallest part of the speedup. The memory layout mattered more, which is kind of the whole lesson of this class. Thanks! Any questions?
