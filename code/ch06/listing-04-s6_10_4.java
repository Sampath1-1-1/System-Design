// Extracted from manuscript/book1-traditional/06-operating-systems.md §6.10.4 (listing 4). Edit the manuscript, not this file.
import java.util.concurrent.atomic.AtomicLong;

/** A lock-free "max seen so far" tracker built from a compare-and-swap retry loop. */
public class CasCounter {
    private final AtomicLong max = new AtomicLong(Long.MIN_VALUE);
    private final AtomicLong retries = new AtomicLong();

    void offer(long candidate) {
        while (true) {
            long current = max.get();                       // 1. read
            if (candidate <= current) return;               // nothing to do
            if (max.compareAndSet(current, candidate)) {    // 2. swap only if unchanged
                return;
            }
            retries.incrementAndGet();                      // 3. someone beat us: retry
        }
    }

    public static void main(String[] args) throws InterruptedException {
        CasCounter tracker = new CasCounter();
        Thread[] workers = new Thread[4];
        for (int t = 0; t < workers.length; t++) {
            final int id = t;
            workers[t] = new Thread(() -> {
                for (long i = 0; i < 1_000_000; i++) {
                    tracker.offer(i * workers.length + id);
                }
            });
            workers[t].start();
        }
        for (Thread w : workers) w.join();
        System.out.println("max     = " + tracker.max.get());   // 3999999
        System.out.println("retries = " + tracker.retries.get());
    }
}
