// Extracted from manuscript/book1-traditional/05-computer-architecture.md §5.4.3 (listing 1). Edit the manuscript, not this file.
/* traverse.c — build: gcc -O2 -std=c11 traverse.c -o traverse */
#define _POSIX_C_SOURCE 199309L
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define N 8192                 /* 8192 x 8192 ints = 256 MiB */

static double now(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + t.tv_nsec / 1e9;
}

int main(void) {
    int *m = malloc((size_t)N * N * sizeof *m);
    if (!m) return 1;
    for (size_t i = 0; i < (size_t)N * N; i++) m[i] = 1;

    long long sum = 0;
    double t0 = now();
    for (size_t r = 0; r < N; r++)          /* row-major: consecutive addresses */
        for (size_t c = 0; c < N; c++)
            sum += m[r * N + c];
    double t1 = now();
    for (size_t c = 0; c < N; c++)          /* column-major: jumps of N*4 bytes */
        for (size_t r = 0; r < N; r++)
            sum += m[r * N + c];
    double t2 = now();

    printf("row-major:    %.3f s\n", t1 - t0);
    printf("column-major: %.3f s\n", t2 - t1);
    printf("checksum: %lld\n", sum);         /* stops the compiler deleting loops */
    free(m);
    return 0;
}
