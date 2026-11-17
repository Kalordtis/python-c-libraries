import ctypes, os

lib = ctypes.CDLL(os.path.abspath("libmylib.so"))

lib.add.argtypes = [ctypes.c_int, ctypes.c_int]
lib.add.restype  = ctypes.c_int

lib.sum_array.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_size_t]
lib.sum_array.restype  = ctypes.c_double

print(lib.add(2, 3))

nums = [1.5, 2.5, 3.0]
arr = (ctypes.c_double * len(nums))(*nums)
print(lib.sum_array(arr, len(nums)))
