// Extracted from manuscript/book1-traditional/05-computer-architecture.md §5.4.7 (listing 2). Edit the manuscript, not this file.
/* false_sharing.c — build: gcc -O2 -std=c11 -pthread false_sharing.c -o fs */
#define _POSIX_C_SOURCE 199309L
#include <pthread.h>
#include <stdalign.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <time.h>

#define ITERATIONS 50000000ULL   /* 5 x 10^7 increments per thread */
#define CACHE_LINE 64            /* x86-64 line size; check yours */

/* Variant A: two counters 8 bytes apart -> same cache line. */
struct packed {
    _Atomic uint64_t a;
    _Atomic uint64_t b;
};

/* Variant B: each counter starts its own 64-byte cache line. */
struct padded {
    alignas(CACHE_LINE) _Atomic uint64_t a;
    alignas(CACHE_LINE) _Atomic uint64_t b;
};

static struct packed P;
static struct padded Q;

static void *worker(void *arg) {
    _Atomic uint64_t *counter = arg;
    for (uint64_t i = 0; i < ITERATIONS; i++)
        atomic_fetch_add_explicit(counter, 1, memory_order_relaxed);
    return NULL;
}

static double run(_Atomic uint64_t *x, _Atomic uint64_t *y) {
    struct timespec t0, t1;
    pthread_t ta, tb;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    pthread_create(&ta, NULL, worker, (void *)x);
    pthread_create(&tb, NULL, worker, (void *)y);
    pthread_join(ta, NULL);
    pthread_join(tb, NULL);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    return (double)(t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec) / 1e9;
}

int main(void) {
    printf("gap between counters: packed=%td B, padded=%td B\n",
           (char *)&P.b - (char *)&P.a, (char *)&Q.b - (char *)&Q.a);
    printf("packed (false sharing): %.2f s\n", run(&P.a, &P.b));
    printf("padded (separate lines): %.2f s\n", run(&Q.a, &Q.b));
    return 0;
}
