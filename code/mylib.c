#include <stddef.h>

int add(int a, int b) {
    return a + b;
}

double sum_array(const double *arr, size_t n) {
    double total = 0.0;
    for (size_t i = 0; i < n; i++)
        total += arr[i];
    return total;
}
