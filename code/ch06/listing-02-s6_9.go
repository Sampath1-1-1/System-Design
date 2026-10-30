// Extracted from manuscript/book1-traditional/06-operating-systems.md §6.9 (listing 2). Edit the manuscript, not this file.
// Three counters incremented by many goroutines: racy, mutex, atomic.
package main

import (
	"fmt"
	"sync"
	"sync/atomic"
)

const goroutines = 8
const increments = 100_000

func main() {
	var wg sync.WaitGroup

	// 1. Racy: counter++ is a read-modify-write, not one indivisible step.
	racy := 0
	for g := 0; g < goroutines; g++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for i := 0; i < increments; i++ {
				racy++
			}
		}()
	}
	wg.Wait()

	// 2. Mutex: only one goroutine at a time inside the critical section.
	var mu sync.Mutex
	locked := 0
	for g := 0; g < goroutines; g++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for i := 0; i < increments; i++ {
				mu.Lock()
				locked++
				mu.Unlock()
			}
		}()
	}
	wg.Wait()

	// 3. Atomic: the hardware performs the increment indivisibly.
	var atomicCount atomic.Int64
	for g := 0; g < goroutines; g++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for i := 0; i < increments; i++ {
				atomicCount.Add(1)
			}
		}()
	}
	wg.Wait()

	fmt.Println("expected:", goroutines*increments)
	fmt.Println("racy:    ", racy)
	fmt.Println("mutex:   ", locked)
	fmt.Println("atomic:  ", atomicCount.Load())
}
