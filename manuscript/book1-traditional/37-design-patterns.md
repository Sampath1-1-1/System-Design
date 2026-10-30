# Chapter 37 — Design Patterns

> **Level:** 2 · **Track:** A (Traditional) · **Estimated reading time:** 3.5 h

A carpenter who has built a hundred staircases does not reinvent the stringer, the tread and the riser each time. They recognize the problem ("connect two floors safely in this much space"), recall a solution shape that has worked before, and adapt it to the room. Software has the same kind of recurring problems: "create the right object without hard-coding its class", "add retries to a client without editing it", "let five subsystems react when an order is placed". A **design pattern** is a named, reusable solution shape for one of these problems. This chapter catalogs the patterns that keep appearing in the code behind large systems, shows each one in runnable Python, and connects each to the system-level idea it foreshadows: Observer to publish/subscribe, Proxy to API gateways and sidecars, Chain of Responsibility to middleware, producer–consumer to message queues.

::: definition
**Definition — Design pattern.** A named description of a recurring design problem, the core of a solution (a set of collaborating classes or functions and their responsibilities), and the trade-offs of applying it. A pattern is a template you adapt, not a library you import [Gamma et al. 1994].
:::

The canonical catalog is the "Gang of Four" (GoF) book, which grouped 23 patterns into three families [Gamma et al. 1994]: **creational** patterns (how objects are made: Factory Method, Abstract Factory, Builder, Singleton, Prototype), **structural** patterns (how objects are composed: Adapter, Decorator, Proxy, Facade, Composite, Bridge, Flyweight) and **behavioral** patterns (how objects divide work and communicate: Strategy, Observer, Command, State, Template Method, Chain of Responsibility and others). Two further families matter for system design: **enterprise** patterns such as Repository [Fowler 2002] and Dependency Injection [Fowler 2004], and **concurrency** patterns such as producer–consumer and thread pools [Schmidt et al. 2000; Goetz et al. 2006].

::: concept
**Patterns depend on the language.** The GoF book was written for C++ and Smalltalk. In a language with first-class functions, modules and duck typing, several patterns shrink: a Strategy becomes a function argument, a Singleton becomes a module, a Command becomes a closure. Norvig observed in 1996 that most GoF patterns are simpler or invisible in dynamic languages [Norvig 1996]. This chapter shows the classic structure first, because interviewers and Java codebases use it, and then the idiomatic Python form.
:::

Every pattern below uses the same compact structure: intent, the problem it solves in a real system, the structure as a Mermaid class diagram, a Python implementation (all run under Python 3.13), a short Java sketch only where Java adds something language-specific, when to use and when not, related patterns, and one interview question. Most examples share one running system: the order service of an online store, which takes orders, charges payments, sends notifications and talks to cloud storage.

## 37.1 Learning objectives

After this chapter you should be able to:

- State the intent, structure and trade-offs of the Factory, Abstract Factory, Builder, Singleton, Strategy, Observer, Adapter, Decorator, Proxy, Command, Repository, State, Template Method and Chain of Responsibility patterns, and draw each as a class diagram.
- Implement each pattern in idiomatic Python and recognize where a function, module or closure replaces a class hierarchy.
- Explain why Singleton is often an anti-pattern, write a thread-safe variant, and explain why a "singleton" in a 50-pod deployment is really 50 objects.
- Distinguish the GoF Decorator from the Python `@decorator` syntax, and Adapter from Decorator from Proxy.
- Apply constructor injection and a composition root, and relate them to the Dependency Inversion Principle (§36.7).
- Build producer–consumer pipelines, thread pools and futures, size a thread pool with the utilization formula, and explain why double-checked locking is broken without a memory-model guarantee.
- Choose a pattern for a stated problem and name the trade-off you accept.

## 37.2 Prerequisites

- Classes, interfaces, polymorphism and composition over inheritance — §35.3–§35.9 (every pattern here is built from them).
- Cohesion and coupling — §35.10 (most patterns trade a little indirection for lower coupling).
- SOLID principles, especially Open/Closed (§36.4) and Dependency Inversion (§36.7) — patterns are the concrete mechanisms that realize them.
- Threads, locks, condition variables and read-write locks — §6.3, §6.9–§6.10 (needed for Singleton thread safety and §37.16).
- Little's Law — §4.11 (used to size thread pools).

## 37.3 Factory

Creating an object with `EmailNotifier()` is the simplest thing in programming, and it is also a hidden decision: the calling code now knows, and depends on, one concrete class. When the choice of class depends on configuration, input or environment, that decision should live in exactly one place. Factories put it there.

### 37.3.1 Simple factory

#### Intent

::: definition
**Definition — Simple factory.** A function or static method that takes a description of what is wanted (a string, an enum, a config value) and returns an instance of the matching concrete class, behind a common interface. It is an idiom rather than a GoF pattern, but it is the most common factory in practice.
:::

#### Problem it solves

The order service sends notifications by email, SMS or push, and the channel comes from each user's preferences. Without a factory, every call site contains the same `if channel == "email": ... elif ...` chain, and adding WhatsApp means editing all of them. With a factory, call sites ask for "a notifier for this channel" and only the factory knows the mapping.

#### Structure

**Figure 37.1 — Simple factory for notifiers.**

```mermaid
classDiagram
  class Notifier {
    <<interface>>
    +send(to, msg) str
  }
  class EmailNotifier
  class SmsNotifier
  class PushNotifier
  class NotifierFactory {
    -registry dict
    +make_notifier(channel) Notifier
  }
  class OrderService
  Notifier <|.. EmailNotifier
  Notifier <|.. SmsNotifier
  Notifier <|.. PushNotifier
  NotifierFactory ..> Notifier : creates
  OrderService ..> NotifierFactory : asks
  OrderService ..> Notifier : uses
```

**Reading the diagram.** `Notifier` is the interface every channel implements; the three concrete classes realize it (dotted arrows with hollow heads). `NotifierFactory` owns a registry from channel name to class and is the only component that names concrete classes. `OrderService` depends on the factory and on the interface, never on a concrete notifier. All calls are synchronous, in-process method calls. The registry is the only state, held in memory. The failure point is an unknown channel name, which the factory should reject loudly rather than return `None`. Adding a channel extends the registry without touching callers, which is the Open/Closed Principle (§36.4) in action.

### 37.3.2 Factory method

#### Intent

::: definition
**Definition — Factory method.** A method declared in a base class that returns a product through an interface, which subclasses override to decide which concrete product to create. The base class's other methods use the product without knowing its class [Gamma et al. 1994].
:::

#### Problem it solves

A framework defines the workflow and lets applications supply the parts. An alerting framework's `AlertJob.run()` always formats a message and sends it, but a paging job must use SMS and a daily digest job must use email. The base class cannot know which; the subclass can. Real frameworks are full of factory methods: Python's `socketserver` and `unittest` let subclasses decide the handler or test objects the framework creates, and Java's `Collection.iterator()` lets each collection return its own iterator class.

#### Structure

**Figure 37.2 — Factory method.**

```mermaid
classDiagram
  class AlertJob {
    <<abstract>>
    +run(to, msg) str
    +create_notifier()* Notifier
  }
  class PagerAlertJob {
    +create_notifier() Notifier
  }
  class DigestAlertJob {
    +create_notifier() Notifier
  }
  class Notifier {
    <<interface>>
    +send(to, msg) str
  }
  AlertJob <|-- PagerAlertJob
  AlertJob <|-- DigestAlertJob
  AlertJob ..> Notifier : uses
  PagerAlertJob ..> SmsNotifier : creates
  DigestAlertJob ..> EmailNotifier : creates
  Notifier <|.. SmsNotifier
  Notifier <|.. EmailNotifier
```

**Reading the diagram.** The abstract creator `AlertJob` defines `run()`, which calls the abstract `create_notifier()` (the asterisk marks it abstract). Each concrete creator overrides that one method and names one concrete product. Control flows downward through inheritance (solid arrows with hollow heads) and the creation dependency points from each subclass to its product. Everything is synchronous and in-process; no state is stored beyond the objects themselves. The design scales by adding a creator subclass per product variant, which is also its weakness: two independent variation axes (channel and urgency, say) multiply subclasses, and composition (Strategy, §37.7, or injection, §37.14) is then the better tool.

#### Python implementation

```python
from abc import ABC, abstractmethod


class Notifier(ABC):
    @abstractmethod
    def send(self, to: str, msg: str) -> str: ...


class EmailNotifier(Notifier):
    def send(self, to, msg):
        return f"email to {to}: {msg}"


class SmsNotifier(Notifier):
    def send(self, to, msg):
        return f"sms to {to}: {msg[:160]}"          # SMS segments are 160 chars


class PushNotifier(Notifier):
    def send(self, to, msg):
        return f"push to {to}: {msg}"


# --- Simple factory: one place owns the "which class?" decision ---
_REGISTRY: dict[str, type[Notifier]] = {
    "email": EmailNotifier, "sms": SmsNotifier, "push": PushNotifier,
}


def make_notifier(channel: str) -> Notifier:
    try:
        return _REGISTRY[channel]()
    except KeyError:
        raise ValueError(f"unknown channel {channel!r}") from None


# --- Factory method: subclasses decide what the base class creates ---
class AlertJob(ABC):
    @abstractmethod
    def create_notifier(self) -> Notifier: ...      # the factory method

    def run(self, to: str, msg: str) -> str:        # fixed workflow uses it
        return self.create_notifier().send(to, f"[ALERT] {msg}")


class PagerAlertJob(AlertJob):
    def create_notifier(self):
        return SmsNotifier()


class DigestAlertJob(AlertJob):
    def create_notifier(self):
        return EmailNotifier()


if __name__ == "__main__":
    print(make_notifier("push").send("user-42", "Order shipped"))
    for job in (PagerAlertJob(), DigestAlertJob()):
        print(job.run("oncall", "p99 latency above SLO"))
    try:
        make_notifier("fax")
    except ValueError as e:
        print("rejected:", e)
```

Output:

```text
push to user-42: Order shipped
sms to oncall: [ALERT] p99 latency above SLO
email to oncall: [ALERT] p99 latency above SLO
rejected: unknown channel 'fax'
```

What to notice:

- The registry is a dictionary of classes. In Python, classes are objects, so a simple factory needs no `if` chain and plugins can register themselves at import time.
- The factory fails loudly on unknown input. A factory that returns `None` moves the crash to a distant call site.
- `AlertJob.run()` never names a concrete class; only the one-line overrides do.

#### When to use and when not

Use a simple factory when the concrete class is chosen at run time from data (config, a request field, a feature flag). Use a factory method when a base class or framework owns a workflow and subclasses supply a part. Do not add a factory when there is only one implementation and no realistic second one: `Thing()` is clearer than `ThingFactory.create()`. In Python, passing a class or a callable (`notifier_cls=SmsNotifier`) often replaces a factory-method hierarchy.

#### Related patterns

Abstract Factory (§37.4) is a set of factory methods for a family of products. Template Method (§37.15.2) is the general form of "base class owns the workflow". Dependency injection (§37.14) usually decides which factory is used.

#### Interview question

::: tip
**Q.** What is the difference between a simple factory and the factory method pattern? **A.** A simple factory is one function that maps a parameter to a concrete class; callers pass data in. A factory method is an overridable method in a class hierarchy; the subclass, not a parameter, decides the product, and the base class's own logic uses it. The first centralizes a run-time choice; the second lets a framework defer a decision to its extensions.
:::

## 37.4 Abstract factory

### Intent

::: definition
**Definition — Abstract factory.** An interface for creating a *family* of related objects (for example a blob store and a work queue) without naming their concrete classes, so that a client receives products that are guaranteed to belong together [Gamma et al. 1994].
:::

### Problem it solves

The order service stores invoices as blobs and enqueues work for a background worker. In production it uses a cloud object store and a cloud queue; in unit tests it uses in-memory fakes; on a laptop it uses the local disk. Mixing families (a disk blob store with a cloud queue whose workers cannot read the disk) is a bug that type checks cannot catch unless the families are created together. An abstract factory makes "which environment am I in?" one decision, made once, at startup. Portable libraries use the same idea: Java's `javax.xml.parsers.DocumentBuilderFactory` hides which XML parser implementation is installed.

### Structure

**Figure 37.3 — Abstract factory for infrastructure families.**

```mermaid
classDiagram
  class InfraFactory {
    <<interface>>
    +blob_store() BlobStore
    +work_queue() WorkQueue
  }
  class MemoryInfra
  class DiskInfra
  class BlobStore {
    <<interface>>
    +put(key, data)
    +get(key) bytes
  }
  class WorkQueue {
    <<interface>>
    +push(item)
    +pop() str
  }
  InfraFactory <|.. MemoryInfra
  InfraFactory <|.. DiskInfra
  BlobStore <|.. MemBlobStore
  BlobStore <|.. DiskBlobStore
  WorkQueue <|.. MemQueue
  WorkQueue <|.. DiskQueue
  MemoryInfra ..> MemBlobStore : creates
  MemoryInfra ..> MemQueue : creates
  DiskInfra ..> DiskBlobStore : creates
  DiskInfra ..> DiskQueue : creates
  IngestService ..> InfraFactory : uses
```

**Reading the diagram.** There are two product interfaces (`BlobStore`, `WorkQueue`) and one factory interface with one creation method per product. Each concrete factory creates one consistent family: `MemoryInfra` creates the in-memory store and queue, `DiskInfra` the file-based ones. `IngestService` depends only on the three interfaces. Calls are synchronous and in-process here; in production the products would wrap network clients, and the storage boundary would sit behind `BlobStore.put` and `WorkQueue.push`, which are the failure points (timeouts, throttling). Adding a family (a cloud one) is easy; adding a product type (a cache) is hard, because every factory must change.

### Python implementation

```python
import os
import tempfile
from abc import ABC, abstractmethod
from collections import deque


class BlobStore(ABC):
    @abstractmethod
    def put(self, key: str, data: bytes) -> None: ...
    @abstractmethod
    def get(self, key: str) -> bytes: ...


class WorkQueue(ABC):
    @abstractmethod
    def push(self, item: str) -> None: ...
    @abstractmethod
    def pop(self) -> str | None: ...


class InfraFactory(ABC):
    @abstractmethod
    def blob_store(self) -> BlobStore: ...
    @abstractmethod
    def work_queue(self) -> WorkQueue: ...


# Family 1: in-memory, for unit tests
class MemBlobStore(BlobStore):
    def __init__(self): self._d: dict[str, bytes] = {}
    def put(self, key, data): self._d[key] = data
    def get(self, key): return self._d[key]


class MemQueue(WorkQueue):
    def __init__(self): self._q: deque[str] = deque()
    def push(self, item): self._q.append(item)
    def pop(self): return self._q.popleft() if self._q else None


class MemoryInfra(InfraFactory):
    def blob_store(self): return MemBlobStore()
    def work_queue(self): return MemQueue()


# Family 2: local disk, for a developer laptop
class DiskBlobStore(BlobStore):
    def __init__(self, root): self.root = root
    def put(self, key, data):
        with open(os.path.join(self.root, key), "wb") as f:
            f.write(data)
    def get(self, key):
        with open(os.path.join(self.root, key), "rb") as f:
            return f.read()


class DiskQueue(WorkQueue):
    def __init__(self, root):
        self.path, self.read_pos = os.path.join(root, "queue.log"), 0
    def push(self, item):
        with open(self.path, "a") as f:
            f.write(item + "\n")
    def pop(self):
        if not os.path.exists(self.path):
            return None
        with open(self.path) as f:
            lines = f.read().splitlines()
        if self.read_pos >= len(lines):
            return None
        self.read_pos += 1
        return lines[self.read_pos - 1]


class DiskInfra(InfraFactory):
    def __init__(self): self.root = tempfile.mkdtemp()
    def blob_store(self): return DiskBlobStore(self.root)
    def work_queue(self): return DiskQueue(self.root)


def ingest(infra: InfraFactory, name: str, payload: bytes) -> str:
    store, queue = infra.blob_store(), infra.work_queue()   # one consistent family
    store.put(name, payload)
    queue.push(name)
    key = queue.pop()
    return f"{type(infra).__name__}: {key} -> {store.get(key)!r}"


if __name__ == "__main__":
    factories = {"test": MemoryInfra, "dev": DiskInfra}
    for env in ("test", "dev"):
        print(ingest(factories[env](), "invoice-17.txt", b"total=4999"))
```

Output:

```text
MemoryInfra: invoice-17.txt -> b'total=4999'
DiskInfra: invoice-17.txt -> b'total=4999'
```

What to notice:

- `ingest` is written once and runs unchanged against both families; the environment is chosen in one dictionary lookup at the top.
- The factory guarantees compatibility: `DiskQueue` items name files that `DiskBlobStore` can read.
- The cost is many small classes. In Python you can often replace the factory class with a small dataclass of two callables, or a module per environment.

### When to use and when not

Use an abstract factory when you have several product types that must vary together (per cloud, per database vendor, per UI theme, per test versus production). Do not use it when products vary independently, when there is only one family, or when you expect to add product types frequently, since each new product forces a change to every factory.

### Related patterns

Each creation method is a factory method (§37.3.2). Concrete factories are often configured by dependency injection (§37.14) and are sometimes, unwisely, made singletons (§37.6). Hexagonal architecture (§33.10) generalizes the idea: ports are the product interfaces and each environment supplies adapters.

### Interview question

::: tip
**Q.** Your service must run on two cloud providers. How would you keep provider-specific code out of business logic? **A.** Define ports for each capability (blob storage, queue, secrets) and one abstract factory per provider that builds a consistent set of adapters. Business logic receives the factory or the built adapters via constructor injection; provider choice is made once in the composition root from configuration. Contract tests run against every family. Accept that new capabilities require changes to every provider's factory.
:::

## 37.5 Builder

### Intent

::: definition
**Definition — Builder.** A separate object that assembles a complex product step by step, validates the combination of choices, and returns a finished (ideally immutable) product from a final `build()` call [Gamma et al. 1994; Bloch 2018].
:::

### Problem it solves

An outbound HTTP request in the order service has a method, URL, headers, an optional body, a timeout and a retry count, and some combinations are invalid: a `GET` with a body, a timeout of 0, or a retried `POST` without an idempotency key (which risks charging a customer twice, §22.15). A constructor with eight positional arguments is unreadable, and setters on a mutable object allow half-built requests to escape. A builder collects choices fluently, checks cross-field rules once, and emits a frozen object. Real APIs use exactly this shape: Java 11's `HttpRequest.newBuilder()`, and the `newBuilder()` methods that Protocol Buffers generates for every Java message class.

### Structure

**Figure 37.4 — Builder producing an immutable request.**

```mermaid
classDiagram
  class HttpRequestBuilder {
    -method str
    -headers dict
    -body bytes
    -timeout_s float
    -max_retries int
    +method(m) HttpRequestBuilder
    +header(k, v) HttpRequestBuilder
    +json(text) HttpRequestBuilder
    +timeout(s) HttpRequestBuilder
    +retries(n) HttpRequestBuilder
    +build() HttpRequest
  }
  class HttpRequest {
    <<frozen>>
    +method str
    +url str
    +headers Mapping
    +timeout_s float
    +max_retries int
  }
  class PaymentClient
  PaymentClient ..> HttpRequestBuilder : configures
  HttpRequestBuilder ..> HttpRequest : builds
```

**Reading the diagram.** The client (`PaymentClient`) talks only to the mutable builder, whose setters each return the builder so calls chain. `build()` is the single validation point and the only path to the immutable `HttpRequest`. Everything is synchronous and in memory; no I/O happens until a transport later sends the product. The failure point is `build()`, which raises on an invalid combination, so an invalid request can never exist. Immutable products are safe to share across threads and to cache.

### Python implementation

```python
from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class HttpRequest:
    method: str
    url: str
    headers: MappingProxyType
    body: bytes | None
    timeout_s: float
    max_retries: int


class HttpRequestBuilder:
    def __init__(self, url: str):
        self._url, self._method = url, "GET"
        self._headers: dict[str, str] = {}
        self._body: bytes | None = None
        self._timeout_s, self._max_retries = 2.0, 0

    def method(self, m):   self._method = m.upper(); return self
    def header(self, k, v): self._headers[k.lower()] = v; return self
    def timeout(self, s):  self._timeout_s = s; return self
    def retries(self, n):  self._max_retries = n; return self

    def json(self, text: str):
        self._body = text.encode()
        return self.header("Content-Type", "application/json")

    def build(self) -> HttpRequest:
        if self._body is not None and self._method in ("GET", "HEAD"):
            raise ValueError(f"{self._method} must not carry a body")
        if self._max_retries and self._method == "POST" \
                and "idempotency-key" not in self._headers:
            raise ValueError("retried POST needs an Idempotency-Key header")
        if not 0 < self._timeout_s <= 30:
            raise ValueError("timeout must be in (0, 30] seconds")
        return HttpRequest(self._method, self._url,
                           MappingProxyType(dict(self._headers)),  # read-only copy
                           self._body, self._timeout_s, self._max_retries)


if __name__ == "__main__":
    req = (HttpRequestBuilder("https://payments.internal/charges")
           .method("post").json('{"amount": 4999}')
           .header("Idempotency-Key", "order-17-charge").timeout(0.5).retries(3)
           .build())
    print(req.method, req.timeout_s, req.max_retries, dict(req.headers))
    try:
        HttpRequestBuilder("https://payments.internal/charges").method("POST").retries(3).build()
    except ValueError as e:
        print("rejected:", e)
```

Output:

```text
POST 0.5 3 {'content-type': 'application/json', 'idempotency-key': 'order-17-charge'}
rejected: retried POST needs an Idempotency-Key header
```

What to notice:

- Cross-field rules (retries require an idempotency key) live in `build()`, the one place that sees all fields together.
- The product is frozen and its headers are a read-only `MappingProxyType` copy, so later builder calls cannot mutate a request already in flight.

### Java sketch

Python has keyword arguments with defaults, so `HttpRequest(url=..., timeout_s=0.5)` already reads well; a builder earns its keep mainly for cross-field validation. Java has no named or default parameters, so constructors with many parameters ("telescoping constructors") are common, and the static nested Builder is the standard cure [Bloch 2018]:

```java
public final class RequestSpec {
    private final String url, method;
    private final int timeoutMs, maxRetries;

    private RequestSpec(Builder b) {                       // only the builder can construct
        url = b.url; method = b.method; timeoutMs = b.timeoutMs; maxRetries = b.maxRetries;
    }
    public static Builder newBuilder(String url) { return new Builder(url); }

    public static final class Builder {
        private final String url;
        private String method = "GET";
        private int timeoutMs = 2000, maxRetries = 0;
        private Builder(String url) { this.url = url; }
        public Builder method(String m)     { method = m; return this; }
        public Builder timeoutMs(int t)     { timeoutMs = t; return this; }
        public Builder maxRetries(int n)    { maxRetries = n; return this; }
        public RequestSpec build() {
            if (timeoutMs <= 0) throw new IllegalStateException("timeout must be positive");
            return new RequestSpec(this);
        }
    }
}
// RequestSpec r = RequestSpec.newBuilder("https://api.example.com/orders")
//                            .method("POST").timeoutMs(500).maxRetries(3).build();
```

### When to use and when not

Use a builder for objects with many optional parts, cross-field invariants, or a need for immutability after construction (requests, queries, configuration, test fixtures). Do not use one for objects with two or three fields; in Python, a frozen dataclass with keyword arguments and a `__post_init__` check is usually enough.

### Related patterns

Abstract Factory (§37.4) returns a product in one call; Builder assembles one in steps. A builder is often created by a factory method (`newBuilder()`). Test-data builders are a common use in tests of Repository-based code (§37.13).

### Interview question

::: tip
**Q.** Why make the built object immutable? **A.** Immutability means validation in `build()` holds forever: no later setter can break an invariant. Immutable objects can be shared between threads without locks, used as cache keys and dictionary keys, and retried safely because the request that is retried is exactly the one that was validated.
:::

## 37.6 Singleton

### Intent

::: definition
**Definition — Singleton.** A class that guarantees it has exactly one instance within a scope and provides a global access point to it [Gamma et al. 1994]. The scope is almost always one process, a fact that matters greatly in distributed systems.
:::

### Problem it solves

Some resources should exist once per process: a metrics registry that aggregates counters before export, a connection pool, a configuration object loaded at startup, the logging hierarchy. Creating a second connection pool by accident doubles database connections; two metrics registries split counters so dashboards undercount. Python's `logging.getLogger(name)` returns the same logger object for the same name every time, which is a registry of singletons keyed by name.

### Structure

**Figure 37.5 — Singleton with lazy, thread-safe creation.**

```mermaid
classDiagram
  class MetricsRegistry {
    <<singleton>>
    -_instance MetricsRegistry$
    -_lock Lock$
    -counters dict
    +get()$ MetricsRegistry
    +inc(name)
  }
  class OrderService
  class PaymentClient
  OrderService ..> MetricsRegistry : get
  PaymentClient ..> MetricsRegistry : get
```

**Reading the diagram.** `MetricsRegistry` holds a class-level (static, underlined `$`) reference to its only instance and a lock that guards first creation. Any component calls the static `get()` and receives the same object, synchronously and in-process. The state (counters) lives in that process's memory only. The failure points are a race during first creation (two threads both see "no instance"), hidden coupling (callers do not declare the dependency, so tests cannot substitute it), and shared mutable state that every caller can corrupt. It does not scale across processes: each process has its own.

### Python implementation

```python
import json
import sys
import threading
import time


class NaiveRegistry:
    _instance, created = None, 0

    @classmethod
    def get(cls):
        if cls._instance is None:           # check ...
            time.sleep(0.05)                # slow initialization widens the window
            cls.created += 1
            cls._instance = cls()           # ... then act: not atomic
        return cls._instance


class SafeRegistry:
    _instance, created = None, 0
    _lock = threading.Lock()

    @classmethod
    def get(cls):
        if cls._instance is None:           # fast path: no lock after creation
            with cls._lock:
                if cls._instance is None:   # re-check while holding the lock
                    time.sleep(0.05)
                    cls.created += 1
                    cls._instance = cls()
        return cls._instance


def hammer(getter, n_threads=8):
    barrier = threading.Barrier(n_threads)   # release all threads at once
    def worker():
        barrier.wait()
        getter()
    threads = [threading.Thread(target=worker) for _ in range(n_threads)]
    for t in threads: t.start()
    for t in threads: t.join()


if __name__ == "__main__":
    hammer(NaiveRegistry.get)
    hammer(SafeRegistry.get)
    print("naive instances created:", NaiveRegistry.created)
    print("safe instances created: ", SafeRegistry.created)
    # The idiomatic Python singleton is a module: imports are cached.
    import json as again
    print("module is cached:", again is json is sys.modules["json"])
```

Output (the naive count can vary between runs; it was 8 in every run we tried):

```text
naive instances created: 8
safe instances created:  1
module is cached: True
```

What to notice:

- Check-then-act without a lock is a race condition (§6.9): all eight threads saw `None` before any assigned.
- The safe version re-checks under the lock. In CPython this double-check is correct because an object is fully built before the assignment publishes it; the same code in Java needs `volatile` (§37.16.5).
- A **module-level singleton** is the Python idiom: put `registry = MetricsRegistry()` in `metrics.py`, and every `import metrics` returns the module object cached in `sys.modules`. Import itself is protected by the interpreter's import lock.

### Java sketch

Java offers two idioms that use language guarantees instead of hand-written locking. An `enum` with one constant is serialization-safe and reflection-safe [Bloch 2018]; the **initialization-on-demand holder** relies on the JVM's guarantee that class initialization is lazy and thread-safe:

```java
public enum MetricsRegistry {
    INSTANCE;
    private final java.util.concurrent.ConcurrentHashMap<String, Long> counters =
        new java.util.concurrent.ConcurrentHashMap<>();
    public void inc(String name) { counters.merge(name, 1L, Long::sum); }
}

final class AppConfig {
    private AppConfig() { /* read files, environment */ }
    private static final class Holder { static final AppConfig INSTANCE = new AppConfig(); }
    static AppConfig get() { return Holder.INSTANCE; }   // Holder initialized on first call
}
```

### When to use and when not

Singleton is often an **anti-pattern** because it is a global variable with a class around it. It hides dependencies (a function's signature does not reveal that it writes metrics), makes tests order-dependent (state leaks from one test to the next), prevents running two configurations side by side, and invites lock contention on a hot shared object. Prefer creating one instance in the composition root and passing it in (§37.14); you keep "exactly one" by construction and gain testability. Reserve true singletons for stateless or effectively immutable process-wide facilities (logging, a metrics registry), and give them a reset hook for tests.

::: mistake
**Mistake — "A singleton guarantees one instance in the system."** It guarantees one per process (per class loader in Java). An order service running 50 pods with 4 worker processes each has 200 "singleton" connection pools; at 10 connections each, that is 2,000 database connections, which can exhaust a PostgreSQL server configured for a few hundred. A system-wide single instance (one scheduler, one leader) needs leader election and leases (§26.5, §26.11), not a class pattern.
:::

### Related patterns

Dependency injection (§37.14) is the usual replacement. Abstract factories and registries are sometimes singletons. Double-checked locking (§37.16.5) is the classic lazy-initialization idiom and its classic bug.

### Interview question

::: tip
**Q.** How would you make a singleton testable? **A.** Stop calling `get()` from business code. Create the instance once at startup and inject it through constructors; tests then pass a fake. If legacy code must call a global accessor, provide a test-only `reset()` or an override hook, and keep the singleton's state immutable or behind a narrow interface.
:::

## 37.7 Strategy

### Intent

::: definition
**Definition — Strategy.** A family of interchangeable algorithms, each behind a common interface, so that a client can be configured with one at run time without changing its code [Gamma et al. 1994].
:::

### Problem it solves

The order service retries calls to the payment provider. Which backoff policy is right depends on the dependency: a fixed delay for an internal cache, exponential backoff with **full jitter** for a shared external API, where synchronized retries from thousands of clients would otherwise arrive in waves (§22.12) [Brooker 2015]. Hard-coding the policy in the retry loop means editing and retesting the loop for every new policy. Strategy separates "when to retry" (the client's job) from "how long to wait" (the policy). The standard library is full of strategies: the `key=` argument of Python's `sorted`, Java's `Comparator`, and pluggable load-balancing policies (Chapter 19).

### Structure

**Figure 37.6 — Strategy for retry backoff.**

```mermaid
classDiagram
  class Backoff {
    <<interface>>
    +delay(attempt) float
  }
  class Fixed
  class Exponential
  class FullJitter
  class RetryingClient {
    -backoff Backoff
    -max_attempts int
    +call(op)
  }
  Backoff <|.. Fixed
  Backoff <|.. Exponential
  Backoff <|.. FullJitter
  RetryingClient o--> Backoff : has-a
```

**Reading the diagram.** `RetryingClient` (the context) holds a reference to one `Backoff` (aggregation, hollow diamond) and asks it for a delay after each failure. Three concrete strategies implement the same one-method interface. The call to the strategy is synchronous and in-process; the expensive, failure-prone call is the remote operation the client wraps. Strategies here are stateless except for the random generator, so one instance can be shared by many clients. Adding a policy adds a class (or function) and touches nothing else.

### Python implementation

In Python a one-method interface is just a callable, so strategies are functions.

```python
import random
from typing import Callable

Backoff = Callable[[int], float]      # attempt number (0-based) -> seconds to wait


def fixed(delay: float) -> Backoff:
    return lambda attempt: delay


def exponential(base: float, cap: float) -> Backoff:
    return lambda attempt: min(cap, base * 2 ** attempt)


def full_jitter(base: float, cap: float, rng: random.Random) -> Backoff:
    return lambda attempt: rng.uniform(0, min(cap, base * 2 ** attempt))


class RetryingClient:
    def __init__(self, backoff: Backoff, max_attempts: int = 5):
        self.backoff, self.max_attempts = backoff, max_attempts

    def call(self, op, sleep=lambda s: None):
        waits = []
        for attempt in range(self.max_attempts):
            try:
                return op(), waits
            except ConnectionError:
                wait = self.backoff(attempt)
                waits.append(round(wait, 3))
                sleep(wait)                     # injected so the demo runs instantly
        raise TimeoutError(f"gave up after {self.max_attempts} attempts; waits={waits}")


def flaky(fail_times: int):
    state = {"n": 0}
    def op():
        state["n"] += 1
        if state["n"] <= fail_times:
            raise ConnectionError("503")
        return "charged"
    return op


if __name__ == "__main__":
    rng = random.Random(7)
    for name, policy in [("fixed", fixed(0.2)),
                         ("exponential", exponential(0.1, 2.0)),
                         ("full jitter", full_jitter(0.1, 2.0, rng))]:
        result, waits = RetryingClient(policy).call(flaky(fail_times=4))
        print(f"{name:12} {result} after waits {waits}")
```

Output:

```text
fixed        charged after waits [0.2, 0.2, 0.2, 0.2]
exponential  charged after waits [0.1, 0.2, 0.4, 0.8]
full jitter  charged after waits [0.032, 0.03, 0.26, 0.058]
```

What to notice:

- The retry loop never changes; swapping a closure changes the policy.
- Closures capture configuration (`base`, `cap`, `rng`), which is all a strategy object's fields would do.
- Injecting `sleep` and a seeded `rng` makes time-dependent code deterministic in tests, a small taste of §37.14.

### When to use and when not

Use Strategy when several algorithms solve the same problem and the choice depends on configuration, data or tenant (pricing rules, compression codecs, eviction policies, load-balancing algorithms). Do not use it for a choice that never varies, and do not build a class hierarchy in Python when a function argument suffices.

### Related patterns

State (§37.15.1) has the same structure, but the state object changes itself; a strategy is chosen from outside. Template Method (§37.15.2) varies steps by inheritance; Strategy varies them by composition. Decorator (§37.10) adds behavior around a call; Strategy replaces the algorithm inside.

### Interview question

::: tip
**Q.** How does Strategy relate to the Open/Closed Principle? **A.** The context is closed for modification and open for extension: new behavior arrives as a new strategy, not as another `elif` in the context. The choice of strategy moves to configuration or the composition root, and each strategy can be unit-tested in isolation.
:::

## 37.8 Observer

### Intent

::: definition
**Definition — Observer.** A one-to-many dependency in which a **subject** keeps a list of **observers** and notifies each of them when its state changes, so that the subject does not depend on what the observers do [Gamma et al. 1994].
:::

### Problem it solves

When an order is placed, the store must send a receipt, reserve stock and record analytics, and next quarter it will also award loyalty points. If `place_order()` calls each of these directly, the order module imports every other module, and adding loyalty means editing checkout. With Observer, checkout announces "an order was placed" and each interested module subscribes. GUI toolkits (button click listeners), Java's `PropertyChangeListener`, and Kubernetes client informers with registered event handlers all follow this shape.

### Structure

**Figure 37.7 — Observer for order events.**

```mermaid
classDiagram
  class OrderEvents {
    -observers list
    +subscribe(obs) unsubscribe
    +publish(event) errors
  }
  class Observer {
    <<interface>>
    +__call__(event)
  }
  class OrderPlaced {
    <<frozen>>
    +order_id str
    +user str
    +total_cents int
  }
  class Checkout
  Checkout ..> OrderEvents : publish
  OrderEvents o--> "0..*" Observer : notifies
  Observer <|.. send_receipt
  Observer <|.. reserve_stock
  Observer <|.. record_analytics
  OrderEvents ..> OrderPlaced : passes
```

**Reading the diagram.** `Checkout` publishes an immutable `OrderPlaced` event to the subject, `OrderEvents`, which holds zero or more observers and calls each in turn. In the classic pattern every call is synchronous and in-process, so checkout's latency includes every observer's latency and an observer that blocks blocks checkout. The subscriber list is in-memory state; it is lost on restart, and so is any event being delivered when the process crashes. Failure points are a throwing observer (must be isolated) and a slow one (must be moved off the request path). Scaling beyond one process is where the pattern becomes publish/subscribe through a broker.

### Python implementation

```python
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class OrderPlaced:
    order_id: str
    user: str
    total_cents: int


Observer = Callable[[OrderPlaced], None]


class OrderEvents:                                   # the subject
    def __init__(self):
        self._observers: list[Observer] = []

    def subscribe(self, obs: Observer) -> Callable[[], None]:
        self._observers.append(obs)
        return lambda: self._observers.remove(obs)   # caller keeps the unsubscribe handle

    def publish(self, event: OrderPlaced) -> list[str]:
        errors = []
        for obs in list(self._observers):            # copy: observers may unsubscribe
            try:
                obs(event)
            except Exception as e:                   # isolate a failing observer
                errors.append(f"{obs.__name__}: {e}")
        return errors


log = []
def send_receipt(e):     log.append(f"receipt to {e.user}")
def record_analytics(e): log.append(f"analytics +{e.total_cents}")
def reserve_stock(e):
    if e.order_id == "o-2":
        raise RuntimeError("warehouse timeout")
    log.append(f"stock reserved for {e.order_id}")


if __name__ == "__main__":
    events = OrderEvents()
    events.subscribe(send_receipt)
    events.subscribe(reserve_stock)
    stop_analytics = events.subscribe(record_analytics)
    print(events.publish(OrderPlaced("o-1", "ana", 4999)), log)
    log.clear(); stop_analytics()
    print(events.publish(OrderPlaced("o-2", "ben", 1999)), log)
```

Output:

```text
[] ['receipt to ana', 'stock reserved for o-1', 'analytics +4999']
['reserve_stock: warehouse timeout'] ['receipt to ben']
```

What to notice:

- A failing observer is reported but does not stop the receipt from being sent; without the `try`, one bug in analytics would break checkout.
- `subscribe` returns an unsubscribe handle. Forgotten subscriptions are a classic memory leak (the "lapsed listener" problem): the subject keeps dead observers alive. `weakref.WeakMethod` is the Python remedy for bound methods.
- Observers run in subscription order and synchronously. Code must not depend on that order.

### Observer and publish/subscribe

Observer is publish/subscribe inside one process. Chapter 30 (§30.5) takes the idea across the network.

**Table 37.1 — Observer versus broker-based publish/subscribe.**

| Aspect | Observer (in-process) | Publish/subscribe (§30.5) |
|---|---|---|
| Coupling | Subject holds observer references | Publisher knows only a topic |
| Timing | Synchronous, same call stack | Asynchronous; subscribers may be offline |
| Durability | None; lost on crash | Broker persists messages |
| Failure isolation | Manual (`try` per observer) | Process boundary; retries, dead-letter queues (§30.11) |
| Latency | Microseconds | Milliseconds |
| Choose when | Same deployable, same transaction | Different services, independent scaling |

A common production arrangement uses both: an in-process observer writes the event to an outbox table in the same database transaction, and a relay publishes it to the broker (the transactional outbox, §32.5).

### When to use and when not

Use Observer when one change must trigger an open-ended set of reactions inside a process (UI updates, cache invalidation, domain events). Do not use it when the reactions must be atomic with the change and failure must roll it back (call them directly in the transaction), or when observers live in other services (use a broker).

### Related patterns

Mediator centralizes many-to-many communication; Observer distributes one-to-many. Command (§37.12) objects are often what gets queued when observers become asynchronous. Publish/subscribe (§30.5) and event-driven architecture (§30.6) are the distributed forms.

### Interview question

::: tip
**Q.** A slow analytics observer is adding 300 ms to checkout. What do you do? **A.** Take it off the request path: have the observer enqueue the event (an in-process queue drained by a worker, or a broker topic) and return immediately. If the event must not be lost, write it to an outbox in the order's transaction. Then decide the delivery guarantee (at-least-once plus an idempotent consumer is typical, §30.8).
:::

## 37.9 Adapter

### Intent

::: definition
**Definition — Adapter.** A wrapper that converts the interface of an existing class into the interface its clients expect, so that classes with incompatible interfaces can work together [Gamma et al. 1994].
:::

### Problem it solves

The order service defines its own `PaymentGateway.charge(amount, currency, token)` port, returning a `ChargeResult`. The acquiring bank's SDK, which you cannot modify, exposes `make_payment(amount_cents, card_token, currency_code)` and returns a dictionary of status codes. An adapter translates units (decimal to integer cents), argument order and error conventions in one class, so neither side changes. SLF4J's bindings, which route one logging API to Logback, Log4j or `java.util.logging`, are adapters, as are JDBC drivers that present each database's wire protocol through one Java interface.

### Structure

**Figure 37.8 — Object adapter for a legacy payment SDK.**

```mermaid
classDiagram
  class PaymentGateway {
    <<interface>>
    +charge(amount, currency, token) ChargeResult
  }
  class LegacyPayAdapter {
    -client LegacyPayClient
    +charge(amount, currency, token) ChargeResult
  }
  class LegacyPayClient {
    +make_payment(amount_cents, card_token, currency_code) dict
  }
  class OrderService
  OrderService ..> PaymentGateway : uses
  PaymentGateway <|.. LegacyPayAdapter
  LegacyPayAdapter o--> LegacyPayClient : wraps
```

**Reading the diagram.** `OrderService` depends on its own interface (the **target**). `LegacyPayAdapter` implements the target and holds the third-party **adaptee**, translating every call. Calls are synchronous; the adaptee call crosses the network to the payment processor, so it is the failure point (timeouts, declines, malformed responses), and the adapter is where vendor error codes become your domain's results. The adapter holds no state of its own. Swapping vendors means writing a new adapter, not editing the service.

### Python implementation

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


class LegacyPayClient:                       # third-party SDK: cannot be changed
    def make_payment(self, amount_cents, card_token, currency_code):
        if card_token.startswith("tok_bad"):
            return {"status_code": 402, "err": "card_declined"}
        return {"status_code": 200, "txn": f"T-{amount_cents}-{currency_code}"}


@dataclass(frozen=True)
class ChargeResult:
    ok: bool
    reference: str


class PaymentGateway(ABC):                   # our port (the target interface)
    @abstractmethod
    def charge(self, amount: Decimal, currency: str, token: str) -> ChargeResult: ...


class LegacyPayAdapter(PaymentGateway):
    def __init__(self, client: LegacyPayClient):
        self._client = client

    def charge(self, amount, currency, token):
        cents = int((amount * 100).to_integral_value())     # Decimal -> integer cents
        resp = self._client.make_payment(cents, token, currency.upper())
        if resp["status_code"] == 200:
            return ChargeResult(True, resp["txn"])
        return ChargeResult(False, resp.get("err", f"http {resp['status_code']}"))


if __name__ == "__main__":
    gateway: PaymentGateway = LegacyPayAdapter(LegacyPayClient())
    print(gateway.charge(Decimal("49.99"), "usd", "tok_visa"))
    print(gateway.charge(Decimal("19.99"), "eur", "tok_bad_cvc"))
```

Output:

```text
ChargeResult(ok=True, reference='T-4999-USD')
ChargeResult(ok=False, reference='card_declined')
```

What to notice:

- All translation lives in one place: unit conversion, argument order, casing, and error codes become domain values.
- Money uses `Decimal`; converting a binary float like `49.99` to cents can be off by one.
- Tests of `OrderService` use a fake `PaymentGateway`; only the adapter's own tests touch the SDK.

### When to use and when not

Use an adapter at every boundary with code you do not own (vendor SDKs, legacy modules, another team's API) and when migrating between implementations. Do not use one to paper over your own inconsistent interfaces; fix those instead. An adapter that grows business logic has become a service and should be named and tested as one.

### Related patterns

Decorator (§37.10) keeps the interface and adds behavior; Adapter changes the interface. Facade simplifies a whole subsystem behind a new, smaller interface. Hexagonal architecture (§33.10) is named "ports and adapters" after this pattern, and the anti-corruption layer of domain-driven design (§34.5) is an adapter at a bounded-context boundary.

### Interview question

::: tip
**Q.** What is the difference between an object adapter and a class adapter? **A.** An object adapter holds an instance of the adaptee and delegates (composition); it works with any subclass of the adaptee and is the norm in Python and Java. A class adapter inherits from both the target and the adaptee (multiple inheritance in C++, or extending the adaptee class while implementing the target interface in Java); it can override adaptee behavior but couples you to one concrete class.
:::

## 37.10 Decorator

### Intent

::: definition
**Definition — Decorator (GoF).** An object that implements the same interface as the object it wraps, forwards calls to it, and adds behavior before or after them, so responsibilities can be added at run time and stacked in any order without subclassing [Gamma et al. 1994].
:::

### Problem it solves

The order service reads prices from a database-backed `PriceSource`. Some deployments need a cache, all need retries on transient errors, and some need metrics. Subclassing gives a class per combination (`CachingRetryingMetricsDbPriceSource`): with three optional behaviors that is $2^3 = 8$ classes. Decorators give three small wrappers that compose. Java's I/O library is the textbook case: `new BufferedInputStream(new GZIPInputStream(new FileInputStream(f)))` stacks buffering and decompression on a file stream, and Python's `io` module layers a `TextIOWrapper` over a `BufferedReader` over a raw `FileIO` in the same way.

### Structure

**Figure 37.9 — Decorators stacked around a price source.**

```mermaid
classDiagram
  class PriceSource {
    <<interface>>
    +price(sku) int
  }
  class DbPriceSource {
    +price(sku) int
  }
  class PriceSourceDecorator {
    <<abstract>>
    -inner PriceSource
    +price(sku) int
  }
  class CachingPriceSource {
    -cache dict
    -ttl_s float
  }
  class RetryingPriceSource {
    -attempts int
  }
  PriceSource <|.. DbPriceSource
  PriceSource <|.. PriceSourceDecorator
  PriceSourceDecorator <|-- CachingPriceSource
  PriceSourceDecorator <|-- RetryingPriceSource
  PriceSourceDecorator o--> PriceSource : wraps
```

**Reading the diagram.** Every decorator *is a* `PriceSource` and *has a* `PriceSource`; that double relationship is what lets wrappers nest to any depth. A call enters the outermost decorator and flows inward to `DbPriceSource`, the only component that crosses the storage boundary; results flow back out. Everything is synchronous. The cache holds in-process state with a TTL (stale reads are the trade-off, §20.8). Failure points: the database call, which the retry wrapper absorbs for transient errors, and the stacking order, which changes behavior (a cache outside the retry hides retries on hits; inside, it does not).

### Python implementation

```python
import functools
import time
from abc import ABC, abstractmethod


class PriceSource(ABC):
    @abstractmethod
    def price(self, sku: str) -> int: ...


class DbPriceSource(PriceSource):
    def __init__(self, failures_before_success=1):
        self.calls, self._fail = 0, failures_before_success
    def price(self, sku):
        self.calls += 1
        if self._fail:
            self._fail -= 1
            raise ConnectionError("db connection reset")
        return {"A1": 1999, "B2": 4999}[sku]


class CachingPriceSource(PriceSource):            # GoF decorator 1
    def __init__(self, inner, ttl_s=60.0, clock=time.monotonic):
        self._inner, self._ttl, self._clock, self._cache = inner, ttl_s, clock, {}
    def price(self, sku):
        hit = self._cache.get(sku)
        if hit and self._clock() - hit[1] < self._ttl:
            return hit[0]
        value = self._inner.price(sku)
        self._cache[sku] = (value, self._clock())
        return value


class RetryingPriceSource(PriceSource):           # GoF decorator 2
    def __init__(self, inner, attempts=3):
        self._inner, self._attempts = inner, attempts
    def price(self, sku):
        for i in range(self._attempts):
            try:
                return self._inner.price(sku)
            except ConnectionError:
                if i == self._attempts - 1:
                    raise


# Python's @decorator syntax: wraps a *function* at definition time.
def timed(fn):
    @functools.wraps(fn)                          # keep name, docstring
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            wrapper.last_ms = (time.perf_counter() - start) * 1000
    return wrapper


@timed
def quote(source: PriceSource, sku: str, qty: int) -> int:
    return source.price(sku) * qty


if __name__ == "__main__":
    db = DbPriceSource()
    source = CachingPriceSource(RetryingPriceSource(db))     # stack at run time
    print(quote(source, "B2", 2), quote(source, "B2", 1), "db calls:", db.calls)
    print(quote.__name__, f"{quote.last_ms:.3f} ms" if quote.last_ms < 5 else "slow")
```

Output (the time varies by machine):

```text
9998 4999 db calls: 2
quote 0.002 ms
```

What to notice:

- Two database calls: the first failed and was retried; the second quote was a cache hit.
- The stack is built at run time from configuration; no class names the combination.
- `@timed` is Python syntax for `quote = timed(quote)`. `functools.wraps` copies `__name__` and `__doc__`, without which logs and tracebacks name every function `wrapper`.

::: warning
**Python decorators are not the GoF Decorator.** The GoF pattern wraps an *object* at run time behind the *same interface*. Python's `@decorator` (PEP 318) is syntax that passes a function or class to another callable at *definition time* and rebinds the name to whatever it returns [PEP 318]. It can implement a GoF-style wrapper for a function (`@functools.lru_cache`, a retry decorator), but it is equally used for registration (`@app.route("/orders")` adds a URL mapping and returns the function unchanged), for `@property`, and for class transformations (`@dataclass`), none of which is the GoF pattern. Ask "does this wrap an object and keep its interface?"
:::

### When to use and when not

Use decorators for cross-cutting concerns that you want to combine freely: caching, retries, metrics, logging, authorization, compression, rate limiting. Do not use them when the wrapped interface is wide (every method must be forwarded; Python's `__getattr__` helps but hides the contract), when order-dependent stacks become hard to reason about, or when identity matters (`wrapped is not inner`).

### Related patterns

Proxy (§37.11) has the same structure but controls access rather than adding features. Adapter (§37.9) changes the interface. Chain of Responsibility (§37.15.3) is a decorator stack expressed as a pipeline; HTTP middleware is both.

### Interview question

::: tip
**Q.** Design a client library that supports optional caching, retries and circuit breaking. **A.** Define one client interface; implement the network client; implement each concern as a decorator of that interface; build the stack in a factory from configuration. Document the order: retry inside the circuit breaker so an open circuit stops retries (§22.13), cache outermost so hits avoid both.
:::

## 37.11 Proxy

### Intent

::: definition
**Definition — Proxy.** A surrogate that implements the same interface as a real subject and controls access to it [Gamma et al. 1994]. A **virtual proxy** delays creating an expensive object until first use; a **protection proxy** checks permissions before forwarding; a **remote proxy** (a stub) makes an object in another address space look local.
:::

### Problem it solves

The invoice service is expensive to start (it loads templates and opens a connection pool) but most requests never need it; a virtual proxy defers that cost. Only users with the billing role may read invoices; a protection proxy enforces that at one choke point. In a microservice deployment the invoice service runs elsewhere; a remote proxy (a gRPC or REST client stub) lets callers write `invoices.get_invoice("o-17")`.

::: industry
**Spring Framework transactions.** Spring applies `@Transactional` and other aspects by wrapping a bean in a proxy, a JDK dynamic proxy when the bean implements an interface and a generated subclass otherwise. The proxy begins the transaction, calls the real method and commits or rolls back. The documented trade-off: a call from one method of the bean to another on `this` bypasses the proxy, so the annotation on the inner method has no effect.
*Evidence: Primary* — [Spring Docs]
:::

### Structure

**Figure 37.10 — Virtual, protection and remote proxies.**

```mermaid
classDiagram
  class InvoiceService {
    <<interface>>
    +get_invoice(order_id) dict
  }
  class RealInvoiceService
  class LazyInvoiceService {
    -real RealInvoiceService
  }
  class AuthorizingInvoiceService {
    -inner InvoiceService
    -roles set
  }
  class RemoteInvoiceStub {
    -transport callable
  }
  InvoiceService <|.. RealInvoiceService
  InvoiceService <|.. LazyInvoiceService
  InvoiceService <|.. AuthorizingInvoiceService
  InvoiceService <|.. RemoteInvoiceStub
  LazyInvoiceService ..> RealInvoiceService : creates on first use
  AuthorizingInvoiceService o--> InvoiceService : guards
  RemoteInvoiceStub ..> RealInvoiceService : JSON over transport
```

**Reading the diagram.** All four classes share one interface, so a client cannot tell which it holds. The virtual proxy creates the real subject on first call and caches it. The protection proxy wraps any `InvoiceService` and refuses calls that fail its check. The remote stub serializes the call, sends it over a transport (HTTP or gRPC in production; a function here), and deserializes the reply; that edge crosses a process and network boundary, so it adds latency (~0.5 ms in a datacenter at best) and new failure modes (timeouts, partial failure, retries). Scaling the remote side happens behind the stub (load balancing, §19).

### Python implementation

```python
import json
from abc import ABC, abstractmethod


class InvoiceService(ABC):
    @abstractmethod
    def get_invoice(self, order_id: str) -> dict: ...


class RealInvoiceService(InvoiceService):
    def __init__(self):
        print("  (expensive init: templates loaded, DB pool opened)")
        self._db = {"o-17": {"order_id": "o-17", "total_cents": 4999}}
    def get_invoice(self, order_id):
        return self._db[order_id]


class LazyInvoiceService(InvoiceService):            # virtual proxy
    def __init__(self):
        self._real = None
    def get_invoice(self, order_id):
        if self._real is None:
            self._real = RealInvoiceService()
        return self._real.get_invoice(order_id)


class AuthorizingInvoiceService(InvoiceService):     # protection proxy
    def __init__(self, inner: InvoiceService, roles: set[str]):
        self._inner, self._roles = inner, roles
    def get_invoice(self, order_id):
        if "billing" not in self._roles:
            raise PermissionError("billing role required")
        return self._inner.get_invoice(order_id)


class RemoteInvoiceStub(InvoiceService):             # remote proxy (client stub)
    def __init__(self, transport):
        self._send = transport
    def get_invoice(self, order_id):
        reply = json.loads(self._send(json.dumps(
            {"method": "get_invoice", "args": [order_id]})))
        if "error" in reply:
            raise RuntimeError(reply["error"])
        return reply["result"]


def make_server(impl: InvoiceService):               # server skeleton
    allowed = {"get_invoice"}                        # never dispatch arbitrary names
    def handle(wire: str) -> str:
        req = json.loads(wire)
        try:
            if req["method"] not in allowed:
                raise ValueError("no such method")
            return json.dumps({"result": getattr(impl, req["method"])(*req["args"])})
        except Exception as e:
            return json.dumps({"error": repr(e)})
    return handle


if __name__ == "__main__":
    lazy = LazyInvoiceService()
    print("proxy created; nothing loaded yet")
    print(lazy.get_invoice("o-17"))
    try:
        AuthorizingInvoiceService(lazy, {"support"}).get_invoice("o-17")
    except PermissionError as e:
        print("denied:", e)
    stub = RemoteInvoiceStub(make_server(lazy))
    print(stub.get_invoice("o-17"))
    try:
        stub.get_invoice("o-99")
    except RuntimeError as e:
        print("remote error:", e)
```

Output:

```text
proxy created; nothing loaded yet
  (expensive init: templates loaded, DB pool opened)
{'order_id': 'o-17', 'total_cents': 4999}
denied: billing role required
{'order_id': 'o-17', 'total_cents': 4999}
remote error: KeyError('o-99')
```

What to notice:

- The expensive initialization ran once, on first use, not at construction.
- The remote stub changes failure semantics: a `KeyError` on the server becomes a `RuntimeError` carrying a string. Remote proxies cannot fully hide the network, which is the first fallacy of distributed computing (§24.5).
- The skeleton dispatches only allowed method names. Dispatching any name from the wire is a remote-code-execution hole.

### Java sketch

Java can generate proxies at run time for any interface with `java.lang.reflect.Proxy`, which is how frameworks add transactions, security checks and tracing without hand-written wrapper classes:

```java
import java.lang.reflect.Proxy;

interface Invoices { String get(String orderId); }

class Proxies {
    @SuppressWarnings("unchecked")
    static <T> T timed(T target, Class<T> iface) {
        return (T) Proxy.newProxyInstance(iface.getClassLoader(), new Class<?>[]{iface},
            (proxy, method, args) -> {
                long t0 = System.nanoTime();
                try { return method.invoke(target, args); }
                finally { System.out.printf("%s took %d us%n", method.getName(),
                                            (System.nanoTime() - t0) / 1000); }
            });
    }
}
// Invoices inv = Proxies.timed(orderId -> "invoice " + orderId, Invoices.class);
```

### Proxies at the system level

The same three roles reappear as infrastructure. A reverse proxy (§7.12) and an API gateway (§34.6) are protection proxies for whole services: they authenticate, authorize and rate-limit before forwarding. A service-mesh sidecar such as Envoy (§34.10) is a remote proxy deployed next to each service: the application talks to `localhost`, and the sidecar handles discovery, TLS, retries and telemetry. Content delivery networks (Chapter 21) act as caching proxies.

**Table 37.2 — Four wrappers that look alike.**

| Pattern | Interface seen by client | Purpose | Typical example |
|---|---|---|---|
| Adapter | Different from the wrapped object | Make incompatible interfaces fit | Vendor SDK behind your port |
| Decorator | Same | Add behavior, stackable | Caching, retries, buffering |
| Proxy | Same | Control access: lazy, permission, remote | Lazy entity, auth check, RPC stub |
| Facade | New, simpler | Hide a subsystem | One `checkout()` over five services |

### When to use and when not

Use a proxy when access needs control: deferred creation of something expensive, a permission check at one point, a remote object, or a smart reference that counts or logs. Avoid remote proxies that make chatty remote calls look like cheap local ones; design coarse-grained remote interfaces instead.

### Related patterns

Decorator (§37.10) is structurally identical; the difference is intent. Adapter changes the interface. API gateways and sidecars are proxies at deployment scale.

### Interview question

::: tip
**Q.** Why are lazy-loading ORM proxies a common source of performance bugs? **A.** Each proxy triggers a query on first access, so iterating 100 orders and touching each order's lazily loaded customer issues 1 + 100 queries (the N+1 problem). The proxy hides the I/O. Fix it with eager fetching or a join for that query, and detect it by counting queries per request in tests.
:::

## 37.12 Command

### Intent

::: definition
**Definition — Command.** An object that encapsulates a request (the operation and its arguments) so that it can be stored, passed around, queued, logged, replayed and undone [Gamma et al. 1994]. In this book's terminology a command is a request to do something, as opposed to an event, a fact that has happened.
:::

### Problem it solves

A shopping cart editor needs undo and redo. A background job system needs to put "send receipt for order 17" on a queue and run it later on another machine. An audit log needs a durable record of every requested change. All three need the request itself to be a value, not just a method call that vanishes once made. Java's `Runnable` and `Callable` passed to an executor, Celery tasks, and the operations in a write-ahead log are commands.

### Structure

**Figure 37.11 — Command with undo/redo history.**

```mermaid
classDiagram
  class Command {
    <<interface>>
    +execute(cart)
    +undo(cart)
  }
  class AddItem {
    +sku str
    +qty int
  }
  class RemoveItem {
    +sku str
    -prev int
  }
  class History {
    -done list
    -undone list
    +run(cmd)
    +undo()
    +redo()
  }
  class Cart {
    +items dict
  }
  Command <|.. AddItem
  Command <|.. RemoveItem
  History o--> "0..*" Command : stacks
  AddItem ..> Cart : receiver
  RemoveItem ..> Cart : receiver
```

**Reading the diagram.** The **invoker** (`History`) runs commands and keeps two stacks. Each concrete command knows its **receiver** (`Cart`) and how to reverse itself; `RemoveItem` stores the quantity it removed so that undo can restore it. Calls are synchronous here, but because a command is a value it can cross an asynchronous boundary: serialize it, put it on a queue, execute it on a worker. State lives in the receiver and, for undo, in the history stacks; those stacks are in memory unless you persist them. Failure points: a command whose undo is not the exact inverse, and a queued command executed twice (make handlers idempotent, §32.10).

### Python implementation

```python
import json
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field


class Cart:
    def __init__(self):
        self.items: dict[str, int] = {}


class Command(ABC):
    @abstractmethod
    def execute(self, cart: Cart) -> None: ...
    @abstractmethod
    def undo(self, cart: Cart) -> None: ...


@dataclass
class AddItem(Command):
    sku: str
    qty: int
    def execute(self, cart):
        cart.items[self.sku] = cart.items.get(self.sku, 0) + self.qty
    def undo(self, cart):
        left = cart.items[self.sku] - self.qty
        if left:
            cart.items[self.sku] = left
        else:
            del cart.items[self.sku]


@dataclass
class RemoveItem(Command):
    sku: str
    _prev: int = field(default=0, repr=False)   # captured for undo
    def execute(self, cart):
        self._prev = cart.items.pop(self.sku, 0)
    def undo(self, cart):
        if self._prev:
            cart.items[self.sku] = self._prev


class History:                                   # the invoker
    def __init__(self, cart):
        self.cart, self._done, self._undone = cart, [], []
    def run(self, cmd):
        cmd.execute(self.cart); self._done.append(cmd); self._undone.clear()
    def undo(self):
        if self._done:
            cmd = self._done.pop(); cmd.undo(self.cart); self._undone.append(cmd)
    def redo(self):
        if self._undone:
            cmd = self._undone.pop(); cmd.execute(self.cart); self._done.append(cmd)


TYPES = {"AddItem": AddItem, "RemoveItem": RemoveItem}

def to_message(cmd: Command) -> str:             # commands are values: serialize them
    data = {k: v for k, v in asdict(cmd).items() if not k.startswith("_")}
    return json.dumps({"type": type(cmd).__name__, **data})

def from_message(text: str) -> Command:
    data = json.loads(text)
    return TYPES[data.pop("type")](**data)


if __name__ == "__main__":
    h = History(Cart())
    for cmd in (AddItem("A1", 2), AddItem("B2", 1), RemoveItem("A1")):
        h.run(cmd)
    print("after 3 commands:", h.cart.items)
    h.undo(); h.undo()
    print("after 2 undos:   ", h.cart.items)
    h.redo()
    print("after redo:      ", h.cart.items)

    queue = [to_message(c) for c in (AddItem("A1", 2), RemoveItem("A1"), AddItem("C3", 5))]
    print("queued:", queue[0])
    replica = Cart()
    for msg in queue:                            # a worker replays the queue
        from_message(msg).execute(replica)
    print("replayed cart:   ", replica.items)
```

Output:

```text
after 3 commands: {'B2': 1}
after 2 undos:    {'A1': 2}
after redo:       {'A1': 2, 'B2': 1}
queued: {"type": "AddItem", "sku": "A1", "qty": 2}
replayed cart:    {'C3': 5}
```

What to notice:

- Running a new command clears the redo stack; otherwise redo would reapply a change on top of a different history.
- `RemoveItem` captures the state it destroys (a small memento) so undo is exact.
- Serialized commands are messages: a queue of them is a job queue, and a durable, ordered log of them is a replay log, the core idea behind write-ahead logs and, with events instead of commands, event sourcing (§32.3).

### When to use and when not

Use Command for undo/redo, job queues, scheduled or retried work, macro recording, transactional scripts that must be logged before execution, and any API where the caller and executor are separated in time or space. In Python, a closure or `functools.partial` is enough when you only need deferred execution; reach for command classes when you need undo, serialization or introspection.

### Related patterns

Memento stores the state that undo restores. Strategy (§37.7) varies *how* something is done; Command captures *what* to do. Producer–consumer (§37.16.1) and message queues (§30.4) transport commands. CQRS (§32.4) separates command handling from queries.

### Interview question

::: tip
**Q.** How would you implement undo for operations that call external systems, such as "send email"? **A.** You cannot unsend an email, so undo must be a compensating action (send a correction) or the operation must be delayed until undo is no longer possible (an "undo send" window that queues the command and executes it after 10 s). The same reasoning drives compensating transactions in sagas (§32.7).
:::

## 37.13 Repository

### Intent

::: definition
**Definition — Repository.** An object that mediates between the domain model and data storage, presenting stored aggregates as an in-memory collection with methods such as `add`, `get` and domain-specific finders, so that domain code never sees SQL, ORM sessions or storage APIs [Fowler 2002; Evans 2003].
:::

### Problem it solves

If `OrderService.place()` builds SQL strings, then every business rule test needs a database, the service cannot move from PostgreSQL to DynamoDB without rewriting business logic, and query code is scattered. A repository gives the domain one interface (`OrderRepository`) expressed in domain terms ("orders for this user"), with a database implementation for production and an in-memory one for fast tests. Spring Data generates repository implementations from interfaces such as `interface OrderRepository extends CrudRepository<Order, Long>` [Spring Data Docs].

### Structure

**Figure 37.12 — Repository with interchangeable storage.**

```mermaid
classDiagram
  class Order {
    +order_id str
    +user str
    +total_cents int
    +status str
  }
  class OrderRepository {
    <<interface>>
    +add(order)
    +get(order_id) Order
    +for_user(user) list
  }
  class SqliteOrderRepository {
    -conn Connection
  }
  class InMemoryOrderRepository {
    -rows dict
  }
  class OrderService {
    +place(order_id, user, total)
  }
  OrderService ..> OrderRepository : uses
  OrderRepository <|.. SqliteOrderRepository
  OrderRepository <|.. InMemoryOrderRepository
  OrderRepository ..> Order : stores
```

**Reading the diagram.** `OrderService` depends on the `OrderRepository` interface and on the domain object `Order`, nothing else. Two implementations sit behind the interface: the SQLite one crosses the storage boundary (SQL over a database connection; in production a network hop to a database server, where timeouts and constraint violations occur) and the in-memory one keeps rows in a dictionary for tests. Calls are synchronous. Scaling concerns such as read replicas, partitioning (Chapter 14) and caching can be hidden inside an implementation without changing the service.

### Python implementation

```python
import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    order_id: str
    user: str
    total_cents: int
    status: str = "PENDING"


class OrderRepository(ABC):
    @abstractmethod
    def add(self, order: Order) -> None: ...
    @abstractmethod
    def get(self, order_id: str) -> Order | None: ...
    @abstractmethod
    def for_user(self, user: str) -> list[Order]: ...


class InMemoryOrderRepository(OrderRepository):
    def __init__(self): self._rows: dict[str, Order] = {}
    def add(self, order): self._rows[order.order_id] = order
    def get(self, order_id): return self._rows.get(order_id)
    def for_user(self, user):
        return sorted((o for o in self._rows.values() if o.user == user),
                      key=lambda o: o.order_id)


class SqliteOrderRepository(OrderRepository):
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        conn.execute("CREATE TABLE IF NOT EXISTS orders (order_id TEXT PRIMARY KEY, "
                     "user TEXT NOT NULL, total_cents INTEGER NOT NULL, status TEXT NOT NULL)")
        conn.execute("CREATE INDEX IF NOT EXISTS orders_user ON orders(user)")
    def add(self, order):
        with self._conn:                                     # one transaction
            self._conn.execute("INSERT OR REPLACE INTO orders VALUES (?, ?, ?, ?)",
                               (order.order_id, order.user, order.total_cents, order.status))
    def get(self, order_id):
        row = self._conn.execute("SELECT * FROM orders WHERE order_id = ?",
                                 (order_id,)).fetchone()
        return Order(*row) if row else None
    def for_user(self, user):
        rows = self._conn.execute("SELECT * FROM orders WHERE user = ? ORDER BY order_id",
                                  (user,)).fetchall()
        return [Order(*r) for r in rows]


class OrderService:
    def __init__(self, repo: OrderRepository):
        self._repo = repo
    def place(self, order_id, user, total_cents):
        if total_cents <= 0:
            raise ValueError("total must be positive")
        if self._repo.get(order_id):
            return "duplicate"                               # idempotent retry
        self._repo.add(Order(order_id, user, total_cents))
        return "placed"


def contract_test(repo: OrderRepository) -> str:             # same test, every implementation
    svc = OrderService(repo)
    assert svc.place("o-1", "ana", 4999) == "placed"
    assert svc.place("o-1", "ana", 4999) == "duplicate"
    svc.place("o-2", "ana", 1999); svc.place("o-3", "ben", 500)
    assert [o.order_id for o in repo.for_user("ana")] == ["o-1", "o-2"]
    assert repo.get("o-9") is None
    return f"{type(repo).__name__}: contract passed"


if __name__ == "__main__":
    print(contract_test(InMemoryOrderRepository()))
    print(contract_test(SqliteOrderRepository(sqlite3.connect(":memory:"))))
```

Output:

```text
InMemoryOrderRepository: contract passed
SqliteOrderRepository: contract passed
```

What to notice:

- `OrderService` contains the business rules and no SQL; it runs against either implementation.
- One **contract test** runs against every implementation. This is what keeps the in-memory fake honest; a fake that drifts from the real repository makes tests pass while production fails.
- Queries use placeholders (`?`), never string formatting, which prevents SQL injection (Chapter 10).

### When to use and when not

Use a repository per **aggregate** (a cluster of objects changed together, such as an order and its lines, §34.4) when domain logic is rich enough to be worth testing without a database. Avoid a generic `Repository<T>` with `find_by_anything(**filters)`: it leaks query concerns back into the domain and becomes a weak ORM. For reporting and read-heavy screens, query the database directly or use a separate read model (CQRS, §32.4); forcing analytics through aggregate repositories causes N+1 queries.

### Related patterns

Unit of Work tracks changes across repositories and commits them in one transaction [Fowler 2002]. Data Mapper and Active Record are the alternatives Fowler catalogs for mapping objects to tables. Adapter (§37.9): a repository implementation is an adapter from a domain port to a storage technology. Dependency injection (§37.14) supplies the right implementation.

### Interview question

::: tip
**Q.** Is a repository just a DAO? **A.** A data access object is organized around tables and storage operations; a repository is organized around domain aggregates and speaks the domain's language (`orders.for_user(ana)` rather than `select(table="orders", where=...)`). In small systems they converge. The distinction matters when one aggregate spans several tables or stores: the repository hides that, a DAO usually does not.
:::

## 37.14 Dependency injection

### Intent

::: definition
**Definition — Dependency injection (DI).** A technique in which an object receives the objects it depends on (its dependencies) from outside, typically through its constructor, instead of creating or looking them up itself. The code that creates and connects all objects is the **composition root** [Fowler 2004].
:::

### Problem it solves

An `OrderService` that calls `PostgresOrderRepository()`, `VendorPayClient()` and `datetime.now()` inside its methods cannot be tested without a database, a payment sandbox and a frozen clock, and it cannot be reconfigured without editing it. The Dependency Inversion Principle (§36.7) says high-level policy should depend on abstractions; DI is the mechanism that hands the concrete implementations of those abstractions in. Fowler named the pattern in 2004 to distinguish it from the broader term "inversion of control", and contrasted it with the **Service Locator**, in which objects ask a global registry for dependencies [Fowler 2004]. Section 36.7.4 separates DI, dependency inversion and inversion of control in detail.

### Structure

**Figure 37.13 — Constructor injection with a composition root.**

```mermaid
classDiagram
  class OrderService {
    -repo OrderRepository
    -notifier Notifier
    -clock Clock
    +__init__(repo, notifier, clock)
    +place(order_id, user)
  }
  class Clock {
    <<interface>>
    +now() datetime
  }
  class Notifier {
    <<interface>>
    +send(to, msg)
  }
  class CompositionRoot {
    +build_app(config) OrderService
  }
  class Container {
    -providers dict
    +register(iface, provider)
    +resolve(iface) object
  }
  OrderService ..> Clock
  OrderService ..> Notifier
  Clock <|.. SystemClock
  Clock <|.. FixedClock
  Notifier <|.. EmailNotifier
  Notifier <|.. RecordingNotifier
  CompositionRoot ..> OrderService : constructs
  CompositionRoot ..> Container : may use
```

**Reading the diagram.** `OrderService` declares its dependencies as constructor parameters typed by interfaces and never constructs them. The composition root, at the program's entry point (`main`, the web app factory, the test fixture), chooses implementations: `SystemClock` and `EmailNotifier` in production, `FixedClock` and `RecordingNotifier` in tests. A container is optional automation of that wiring. Wiring happens once at startup, synchronously; the failure point moves there too, which is good: a missing dependency fails at boot rather than on the first request at 3 a.m.

### Python implementation

```python
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import get_type_hints
import inspect


class Clock(ABC):
    @abstractmethod
    def now(self) -> datetime: ...

class Notifier(ABC):
    @abstractmethod
    def send(self, to: str, msg: str) -> None: ...

class SystemClock(Clock):
    def now(self): return datetime.now(timezone.utc)

class FixedClock(Clock):
    def __init__(self): self._t = datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc)
    def now(self): return self._t

class RecordingNotifier(Notifier):
    def __init__(self): self.sent = []
    def send(self, to, msg): self.sent.append((to, msg))


class OrderService:
    def __init__(self, notifier: Notifier, clock: Clock):    # constructor injection
        self._notifier, self._clock = notifier, clock
    def place(self, order_id: str, user: str) -> str:
        stamp = self._clock.now().isoformat()
        self._notifier.send(user, f"order {order_id} placed at {stamp}")
        return stamp


class Container:                                   # a minimal auto-wiring container
    def __init__(self):
        self._providers, self._instances = {}, {}
    def register(self, iface, impl):
        self._providers[iface] = impl
    def resolve(self, iface):
        if iface not in self._instances:           # one instance per container
            impl = self._providers.get(iface, iface)
            hints = get_type_hints(impl.__init__) if inspect.isclass(impl) else {}
            deps = {n: self.resolve(t) for n, t in hints.items() if n != "return"}
            self._instances[iface] = impl(**deps)
        return self._instances[iface]


if __name__ == "__main__":
    # 1. Test: wire by hand with fakes -- no framework needed.
    notifier = RecordingNotifier()
    OrderService(notifier, FixedClock()).place("o-17", "ana")
    print(notifier.sent)
    # 2. Container: same graph, wired from registrations.
    c = Container()
    c.register(Notifier, RecordingNotifier)
    c.register(Clock, FixedClock)
    svc = c.resolve(OrderService)
    svc.place("o-18", "ben")
    print(c.resolve(Notifier).sent, c.resolve(Notifier) is c.resolve(Notifier))
```

Output:

```text
[('ana', 'order o-17 placed at 2026-01-01T09:00:00+00:00')]
[('ben', 'order o-18 placed at 2026-01-01T09:00:00+00:00')] True
```

What to notice:

- The test needs no mocking library: fakes are ordinary classes passed to the constructor.
- The container reads constructor type hints, resolves each recursively, and caches instances; that cache gives you "one per application" without a Singleton class (§37.6).
- The container is the only code that knows concrete classes. Business code never calls `resolve`; if it did, the container would degrade into a service locator with hidden dependencies.

### Java and frameworks

In Java, DI containers are the norm: Spring and Guice build the object graph from annotations or configuration, and Spring recommends constructor injection for required dependencies, which keeps fields `final` and objects complete after construction [Spring Docs]. Python services more often wire by hand in the composition root or use framework hooks such as FastAPI's `Depends`. Either way the principle is the same; a container is a convenience, not the pattern.

### When to use and when not

Use constructor injection by default for anything with I/O, time, randomness or configuration, which is what tests need to control. Prefer constructor injection over setter injection (objects are never half-built) and over field injection (dependencies stay visible in the signature). A constructor with eight parameters is a design smell revealing a class with too many responsibilities (§36.3), not a reason to switch to a locator. Do not inject value objects or pure utilities.

### Related patterns

Factory (§37.3) and Abstract Factory (§37.4) are often what you inject when an object must create things later. Service Locator is the alternative Fowler contrasts it with. Strategy (§37.7) and Repository (§37.13) are the most commonly injected roles.

### Interview question

::: tip
**Q.** What is the difference between dependency injection and the Dependency Inversion Principle? **A.** Dependency inversion is a design principle: high-level modules and low-level modules should both depend on abstractions, and the abstraction is owned by the high-level side (§36.7). Dependency injection is a technique for supplying concrete implementations from outside. You can inject concrete classes (DI without inversion) or depend on abstractions but look them up from a global (inversion without injection); good designs do both.
:::

## 37.15 State, Template Method and Chain of Responsibility

These three behavioral patterns each organize *control flow*: State by the object's current mode, Template Method by a fixed skeleton with variable steps, Chain of Responsibility by a sequence of handlers.

### 37.15.1 State

#### Intent

::: definition
**Definition — State.** An object delegates its behavior to a separate state object and changes behavior by swapping that state object, so it appears to change its class; each state class handles the transitions that are legal from it [Gamma et al. 1994].
:::

#### Problem it solves

An order moves from `PENDING` to `PAID` to `SHIPPED`, and can be cancelled while pending or paid (with a refund if paid) but not after shipping. Implemented with `if self.status == ...` inside every method, the rules for one state are spread across all methods, and an illegal transition (shipping an unpaid order) slips through whichever method forgot a check. The GoF book's own motivating example was a `TCPConnection` whose `open()`, `close()` and `acknowledge()` behave differently in the Established, Listen and Closed states.

#### Structure

**Figure 37.14 — State pattern for the order lifecycle.**

```mermaid
classDiagram
  class Order {
    -state OrderState
    +pay()
    +ship()
    +cancel()
  }
  class OrderState {
    <<abstract>>
    +pay(order)
    +ship(order)
    +cancel(order)
  }
  Order o--> OrderState : delegates to
  OrderState <|-- Pending
  OrderState <|-- Paid
  OrderState <|-- Shipped
  OrderState <|-- Cancelled
```

**Reading the diagram.** `Order` (the context) forwards every action to its current `OrderState`. The abstract state rejects every action by default; each concrete state overrides only the actions legal from it and performs the transition by replacing the context's state object. Calls are synchronous. The current state is the only data that must be persisted (a status column); the state objects are stateless and can be shared. The failure point is concurrent transitions on the same order from two requests; protect them with optimistic concurrency (a version column) in the repository.

#### Python implementation

```python
class IllegalTransition(Exception):
    pass


class OrderState:
    name = "?"
    def _reject(self, action):
        raise IllegalTransition(f"cannot {action} an order that is {self.name}")
    def pay(self, order):    self._reject("pay")
    def ship(self, order):   self._reject("ship")
    def cancel(self, order): self._reject("cancel")


class Pending(OrderState):
    name = "PENDING"
    def pay(self, order):    order.state = PAID
    def cancel(self, order): order.state = CANCELLED


class Paid(OrderState):
    name = "PAID"
    def ship(self, order):   order.state = SHIPPED
    def cancel(self, order):
        order.refund_due = True
        order.state = CANCELLED


class Shipped(OrderState):   name = "SHIPPED"
class Cancelled(OrderState): name = "CANCELLED"

PENDING, PAID, SHIPPED, CANCELLED = Pending(), Paid(), Shipped(), Cancelled()  # shared


class Order:
    def __init__(self):
        self.state, self.refund_due = PENDING, False
    def pay(self):    self.state.pay(self)
    def ship(self):   self.state.ship(self)
    def cancel(self): self.state.cancel(self)


if __name__ == "__main__":
    for actions in (["pay", "ship"], ["pay", "cancel"], ["ship"], ["pay", "ship", "cancel"]):
        o = Order()
        try:
            for a in actions:
                getattr(o, a)()
            print(f"{'+'.join(actions):16} -> {o.state.name}, refund_due={o.refund_due}")
        except IllegalTransition as e:
            print(f"{'+'.join(actions):16} -> rejected: {e}")
```

Output:

```text
pay+ship         -> SHIPPED, refund_due=False
pay+cancel       -> CANCELLED, refund_due=True
ship             -> rejected: cannot ship an order that is PENDING
pay+ship+cancel  -> rejected: cannot cancel an order that is SHIPPED
```

What to notice: every rule about the `PAID` state is in one class; illegal transitions are rejected by default rather than by remembered checks; and the state objects hold no per-order data, so four shared instances serve every order. For small machines, a transition table (`{(PENDING, "pay"): PAID, ...}`) is a lighter alternative; Chapter 38 draws such machines as state diagrams.

#### When to use and when not

Use State when behavior differs substantially per mode and transitions have rules (orders, payments, connections, workflow steps, circuit breakers with closed, open and half-open states, §22.13). Use a table or an enum with a transition map when states differ only in which transitions are allowed. Related: Strategy (§37.7) has the same shape but is chosen externally. **Interview question:** *Where does the state live when the service has 20 replicas?* In the database row, not in memory; each request loads the order, applies the transition through the state object, and writes back with a version check so two replicas cannot both ship and cancel the same order.

### 37.15.2 Template Method

#### Intent

::: definition
**Definition — Template Method.** A method in a base class that defines the skeleton of an algorithm as a fixed sequence of steps, some of which are abstract **primitive operations** or overridable **hooks** that subclasses supply, so subclasses vary steps without changing the sequence [Gamma et al. 1994].
:::

#### Problem it solves

The store exports orders nightly in CSV for finance and JSON Lines for the data lake. Both exports filter, format each row, add an optional header and write output, in that order; only the filter and formatting differ. Duplicating the loop means a fix to one (say, skipping test orders) is forgotten in the other. Frameworks use template methods everywhere: `unittest.TestCase.run()` calls your `setUp`, test method and `tearDown`; `threading.Thread.start()` arranges for your `run()` to execute; Java's `AbstractList` implements iteration on top of your `get()` and `size()`.

#### Structure

**Figure 37.15 — Template Method for export jobs.**

```mermaid
classDiagram
  class ExportJob {
    <<abstract>>
    +run(rows) str
    +include(row) bool
    +header() str
    +format_row(row)* str
  }
  class CsvExport {
    +header() str
    +format_row(row) str
  }
  class JsonLinesExport {
    +include(row) bool
    +format_row(row) str
  }
  ExportJob <|-- CsvExport
  ExportJob <|-- JsonLinesExport
```

**Reading the diagram.** `run()` in the base class is the template method; it is not overridden. `format_row()` is abstract (a primitive operation every subclass must supply), while `include()` and `header()` are hooks with defaults that subclasses may override. Control flows from the base class down into subclass code, the "Hollywood principle" ("don't call us, we'll call you"). Everything is synchronous; output would cross a storage boundary when written to object storage. The fragility point is the inheritance coupling: a change to the skeleton affects every subclass.

#### Python implementation

```python
import json
from abc import ABC, abstractmethod


class ExportJob(ABC):
    def run(self, rows: list[dict]) -> str:          # the template method
        kept = [r for r in rows if self.include(r)]
        lines = [self.format_row(r) for r in kept]
        header = self.header()
        return "\n".join(([header] if header else []) + lines)

    def include(self, row) -> bool: return not row.get("test", False)   # hook
    def header(self) -> str | None: return None                         # hook
    @abstractmethod
    def format_row(self, row) -> str: ...                               # primitive op


class CsvExport(ExportJob):
    def header(self): return "order_id,total_cents"
    def format_row(self, r): return f"{r['order_id']},{r['total_cents']}"


class JsonLinesExport(ExportJob):
    def include(self, r): return super().include(r) and r["status"] == "PAID"
    def format_row(self, r): return json.dumps(r, sort_keys=True)


if __name__ == "__main__":
    rows = [{"order_id": "o-1", "total_cents": 4999, "status": "PAID"},
            {"order_id": "o-2", "total_cents": 1999, "status": "PENDING"},
            {"order_id": "o-3", "total_cents": 100, "status": "PAID", "test": True}]
    print(CsvExport().run(rows))
    print(JsonLinesExport().run(rows))
```

Output:

```text
order_id,total_cents
o-1,4999
o-2,1999
{"order_id": "o-1", "status": "PAID", "total_cents": 4999}
```

What to notice: the test-order filter lives once, in the base hook, and `JsonLinesExport` extends it with `super()`; neither subclass can reorder the steps.

#### When to use and when not

Use Template Method in frameworks and base classes where the sequence is invariant and must be enforced (test lifecycles, request handling, ETL jobs). Prefer Strategy (§37.7) or passing functions when steps vary independently or must be combined at run time, since inheritance fixes the combination at class-definition time (composition over inheritance, §35.8). **Interview question:** *Template Method or Strategy for a pluggable ETL pipeline?* Template Method if the pipeline shape is fixed and you own the base class; Strategy (inject `extract`, `transform` and `load` objects) if teams must mix and match steps, which is the usual case at scale.

### 37.15.3 Chain of Responsibility

#### Intent

::: definition
**Definition — Chain of Responsibility.** A request is passed along a chain of handler objects; each handler either handles it, or does some work and passes it to the next, so the sender does not know which handler will act [Gamma et al. 1994].
:::

#### Problem it solves

Every HTTP request to the order API must be logged, authenticated and rate-limited before reaching the application, and some requests must be stopped early (401, 429). Putting all of that at the top of every endpoint duplicates code and mixes concerns. A chain of middleware applies the concerns in a configured order, and any link can short-circuit. Java servlet filters, Express and ASGI middleware, gRPC interceptors and Envoy's HTTP filter chain all work this way.

::: industry
**Django middleware.** Django builds its request pipeline from the `MIDDLEWARE` setting: each middleware is a factory that receives `get_response` (the next handler) and returns a callable. Requests pass through the list top to bottom and responses bottom to top, and a middleware can return a response without calling `get_response`, short-circuiting the chain. The documentation stresses that order matters, for example placing session middleware before authentication middleware, which reads the session.
*Evidence: Primary* — [Django Docs]
:::
 The classic GoF form, in which exactly one handler takes the request (a support ticket escalating from bot to agent to engineer, or nested exception handlers), is the same structure with a different stopping rule.

#### Structure

**Figure 37.16 — Middleware pipeline as a chain of responsibility.**

```mermaid
classDiagram
  class Handler {
    <<interface>>
    +__call__(request) response
  }
  class Middleware {
    <<interface>>
    +__call__(next_handler) Handler
  }
  class logging_mw
  class auth_mw
  class rate_limit_mw {
    -counts dict
    -limit int
  }
  class app
  Handler <|.. app
  Middleware <|.. logging_mw
  Middleware <|.. auth_mw
  Middleware <|.. rate_limit_mw
  Middleware ..> Handler : wraps next
```

**Reading the diagram.** A `Handler` turns a request into a response. A `Middleware` takes the next handler and returns a new handler that wraps it, so building the chain is function composition: `logging(auth(rate_limit(app)))`. A request flows inward through each link and the response flows back out, so the first middleware sees both the raw request and the final response (ideal for logging and timing). Links run synchronously in one request's call stack. `rate_limit_mw` holds in-memory per-client counters; across replicas this state must move to a shared store (§22.8). Any link can short-circuit, which is also the main failure mode: a misordered chain (rate limiting before authentication, so attackers exhaust real users' quotas).

#### Python implementation

```python
from typing import Callable

Request = dict
Response = tuple[int, str]
Handler = Callable[[Request], Response]
LOG: list[str] = []


def logging_mw(next_h: Handler) -> Handler:
    def handle(req):
        status, body = next_h(req)
        LOG.append(f"{req['client']} {req['path']} -> {status}")
        return status, body
    return handle


def auth_mw(next_h: Handler) -> Handler:
    def handle(req):
        if req.get("token") != "valid":
            return 401, "unauthorized"                 # short-circuit the chain
        return next_h(req)
    return handle


def rate_limit_mw(limit: int):
    counts: dict[str, int] = {}
    def middleware(next_h: Handler) -> Handler:
        def handle(req):
            counts[req["client"]] = counts.get(req["client"], 0) + 1
            if counts[req["client"]] > limit:
                return 429, "too many requests"
            return next_h(req)
        return handle
    return middleware


def app(req: Request) -> Response:
    return 200, f"orders for {req['client']}"


def build(handler: Handler, middlewares) -> Handler:   # first listed = outermost
    for mw in reversed(middlewares):
        handler = mw(handler)
    return handler


if __name__ == "__main__":
    pipeline = build(app, [logging_mw, auth_mw, rate_limit_mw(limit=2)])
    for client, token in [("ana", "valid")] * 3 + [("eve", "forged")]:
        pipeline({"client": client, "token": token, "path": "/orders"})
    print("\n".join(LOG))
```

Output:

```text
ana /orders -> 200
ana /orders -> 200
ana /orders -> 429
eve /orders -> 401
```

What to notice: because authentication runs before rate limiting, the forged request never consumes a rate-limit slot; and because logging is outermost, it records short-circuited responses too. Reordering the list changes behavior without changing any handler.

#### When to use and when not

Use a chain when several independent handlers must process or filter a request in a configurable order: middleware, validation pipelines, approval workflows, event filters. Avoid long chains with no clear ordering contract; debugging "which link swallowed my request?" requires per-link logging or tracing. **Interview question:** *In what order would you put authentication, rate limiting, request logging, compression and caching middleware, and why?* Logging and tracing outermost to see everything; then a coarse per-IP rate limit to shed floods cheaply; then authentication; then per-user rate limiting; then the cache (keyed by user if responses are personalized); compression closest to the network on the way out.

## 37.16 Concurrency patterns

The patterns so far organize code within one thread of control. Concurrency patterns organize work across threads: who produces work, who executes it, how results come back, and how shared data is protected. They are catalogued in *Pattern-Oriented Software Architecture, Volume 2* [Schmidt et al. 2000], which also covers Reactor and Proactor (the event-loop designs of §6.13), Active Object, Monitor Object and Leader/Followers, and they are treated for the JVM in *Java Concurrency in Practice* [Goetz et al. 2006]. The primitives underneath (mutexes, condition variables, atomics) are in §6.10.

::: note
**Python and the GIL.** In standard CPython builds the global interpreter lock lets only one thread execute Python bytecode at a time, so threads speed up I/O-bound work (the lock is released while waiting on sockets and disks) but not CPU-bound Python code; use processes (`ProcessPoolExecutor`) for that. Python 3.13 added an experimental free-threaded build without the GIL [PEP 703]. Correct code must not rely on the GIL for thread safety in either case.
:::

### 37.16.1 Producer–consumer

#### Intent and problem

::: definition
**Definition — Producer–consumer.** Producers put work items into a shared **bounded** buffer and consumers take them out, decoupling the rate at which work is created from the rate at which it is processed; when the buffer is full, producers block or are rejected, which is **backpressure** (§22.10).
:::

The order service's request threads produce "send receipt" jobs faster at peak than the email provider accepts them. Calling the provider inline couples checkout latency to the provider; an unbounded in-memory list grows until the process runs out of memory. A bounded queue between request threads and a fixed set of sender threads absorbs bursts and pushes back when sustained load exceeds capacity. Message brokers (Chapter 30) are this pattern across machines.

**Figure 37.17 — Producer–consumer with a bounded queue.**

```mermaid
classDiagram
  class Producer {
    +run()
  }
  class BoundedQueue {
    -maxsize int
    -items deque
    -not_full Condition
    -not_empty Condition
    +put(item) blocks if full
    +get() blocks if empty
  }
  class Consumer {
    +run()
  }
  Producer ..> BoundedQueue : put
  Consumer ..> BoundedQueue : get
```

**Reading the diagram.** Producers and consumers never reference each other; both depend only on the queue. Inside the queue a lock and two condition variables (§6.10.3) implement blocking: `put` waits on "not full", `get` waits on "not empty". The hand-off is asynchronous from the producer's point of view. Items in the queue live only in process memory and are lost if the process crashes, which is the reason to use a durable broker when jobs must survive restarts. Failure points: a consumer that dies silently (work piles up), a poison item that crashes every consumer, and shutdown (consumers must be told to stop). Scale by adding consumers until the downstream resource saturates.

```python
import queue
import threading
import time


def producer(q: queue.Queue, pid: int, n: int, stats: dict):
    for i in range(n):
        t0 = time.perf_counter()
        q.put(f"receipt-{pid}-{i}")                    # blocks while the queue is full
        stats["blocked_s"] += time.perf_counter() - t0


def consumer(q: queue.Queue, done: list, lock: threading.Lock):
    while True:
        item = q.get()
        if item is None:                               # sentinel: shut down
            break
        time.sleep(0.002)                              # simulated call to email provider
        with lock:
            done.append(item)


if __name__ == "__main__":
    q: queue.Queue = queue.Queue(maxsize=10)           # bounded: backpressure
    done, lock, stats = [], threading.Lock(), {"blocked_s": 0.0}
    consumers = [threading.Thread(target=consumer, args=(q, done, lock)) for _ in range(4)]
    producers = [threading.Thread(target=producer, args=(q, p, 100, stats)) for p in range(2)]
    for t in consumers + producers:
        t.start()
    for t in producers:
        t.join()
    for _ in consumers:
        q.put(None)                                    # one sentinel per consumer
    for t in consumers:
        t.join()
    print(f"processed {len(done)} jobs; queue never exceeded {q.maxsize}; "
          f"producers spent time blocked: {stats['blocked_s'] > 0.01}")
```

Output:

```text
processed 200 jobs; queue never exceeded 10; producers spent time blocked: True
```

What to notice: producers generate 200 jobs instantly but consumers handle about 4 / 0.002 s = 2,000 jobs/s, so producers spend time blocked in `put`; that waiting is backpressure doing its job. One sentinel per consumer gives a clean shutdown. In a web request path, prefer `put(timeout=...)` or `put_nowait` and return 503 rather than blocking a request thread indefinitely (load shedding, §22.9).

### 37.16.2 Thread pool

#### Intent and problem

::: definition
**Definition — Thread pool.** A fixed or bounded set of worker threads that take tasks from a queue and execute them, so the cost of creating threads is paid once and the number of concurrent tasks is capped [Goetz et al. 2006].
:::

Creating a thread per request costs memory (often 1 MiB or more of reserved stack per thread, §6.3.5) and scheduling overhead, and under a spike it creates thousands of threads that thrash. A pool is producer–consumer with tasks as the items: callers submit tasks (Commands, §37.12) and receive futures. Java's `ThreadPoolExecutor` and Python's `concurrent.futures.ThreadPoolExecutor` are standard implementations. The key design decision is the pool size.

**Figure 37.18 — Thread pool returning futures.**

```mermaid
classDiagram
  class Executor {
    -work_queue Queue
    -workers list
    +submit(fn, args) Future
    +shutdown(wait)
  }
  class Worker {
    +run()
  }
  class Future {
    -state str
    -result object
    -exception Exception
    +result(timeout) object
    +done() bool
    +add_done_callback(fn)
  }
  class Client
  Client ..> Executor : submit
  Executor *--> "N" Worker : owns
  Executor ..> Future : returns
  Worker ..> Future : completes
  Client ..> Future : waits or registers callback
```

**Reading the diagram.** The client submits a callable and immediately receives a `Future`; submission is asynchronous. The executor owns N workers (composition, filled diamond), which pull tasks from the internal queue, run them, and complete the matching future with a result or an exception. The client later blocks on `result(timeout)` or registers a callback. State lives in memory: the task queue (which should be bounded) and the futures. Failure points: an unbounded queue that hides overload until memory runs out, tasks that block forever and starve the pool, and exceptions that vanish if no one calls `result()`. Scale by sizing N (below) and by separate pools per dependency (bulkheads, §22.14).

#### Mathematical foundations

::: formula
**Thread-pool sizing for mixed CPU and I/O work [Goetz et al. 2006]**

$$N_{threads} = N_{cpu} \times U_{cpu} \times \left(1 + \frac{W}{C}\right)$$

| Symbol | Meaning | Units |
|---|---|---|
| $N_{threads}$ | Number of worker threads that keeps the CPU at the target utilization | threads |
| $N_{cpu}$ | Number of CPU cores available to the process | cores |
| $U_{cpu}$ | Target CPU utilization, between 0 and 1 | dimensionless |
| $W$ | Time a task spends waiting (I/O, locks) per task | ms |
| $C$ | CPU time a task spends computing per task | ms |
:::

::: example
**Worked example — Sizing the receipt-rendering pool.** Each task spends $C = 5$ ms of CPU rendering a receipt and $W = 95$ ms waiting on the template store and the email provider. The service has $N_{cpu} = 8$ cores and you target $U_{cpu} = 0.75$ to leave headroom.

1. Wait-to-compute ratio: $W/C = 95/5 = 19$.
2. Threads: $N_{threads} = 8 \times 0.75 \times (1 + 19) = 8 \times 0.75 \times 20 = 120$.
3. Throughput ceiling, by Little's Law (§4.11) with each task holding a thread for $W + C = 100$ ms: $\lambda_{max} = 120 / 0.1\ \text{s} = 1{,}200$ tasks/s.
4. CPU check: $1{,}200 \times 5$ ms $= 6$ core-seconds per second, which is $6/8 = 75\%$ of the cores, matching the target.

**Interpretation.** A pool of 8 (one per core) would cap throughput at $8/0.1 = 80$ tasks/s with the CPU 95% idle; a pool of 1,000 would not raise throughput above what the CPU and the downstream provider allow, and would add memory and contention. **Engineering implication.** Measure $W$ and $C$ under realistic load, size the pool from the formula, and check the downstream limit separately: if the email provider allows only 500 requests/s, the provider, not the pool, is the bottleneck, and the pool should be sized for 500 tasks/s ($500 \times 0.1 = 50$ threads).
:::

```python
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def fetch_rate(currency: str) -> tuple[str, float]:
    time.sleep(0.05)                                   # simulated 50 ms I/O call
    if currency == "XXX":
        raise ValueError("unknown currency")
    return currency, {"USD": 1.0, "EUR": 1.08}.get(currency, 0.5)


if __name__ == "__main__":
    currencies = ["USD", "EUR"] * 31 + ["GBP", "XXX"]  # 64 tasks
    t0 = time.perf_counter()
    ok, failed = 0, []
    with ThreadPoolExecutor(max_workers=16) as pool:
        futures = {pool.submit(fetch_rate, c): c for c in currencies}
        for fut in as_completed(futures):              # in completion order
            try:
                fut.result(timeout=1.0)
                ok += 1
            except ValueError as e:
                failed.append(f"{futures[fut]}: {e}")
    elapsed = time.perf_counter() - t0
    print(f"{ok} ok, failed={failed}")
    print(f"sequential would take {len(currencies) * 0.05:.1f} s; pool took {elapsed:.1f} s")
```

Output:

```text
63 ok, failed=['XXX: unknown currency']
sequential would take 3.2 s; pool took 0.2 s
```

What to notice: 64 tasks of 50 ms on 16 workers take $\lceil 64/16 \rceil \times 0.05 = 0.2$ s. The exception raised inside a worker is re-raised by `result()` in the caller; if nobody calls `result()`, it is silently lost. The `with` block shuts the pool down and waits for running tasks.

### 37.16.3 Future and promise

::: definition
**Definition — Future and promise.** A **future** is a read-only placeholder for a result that will be available later; a **promise** (Java's `CompletableFuture`, Python's `asyncio.Future`) is the writable side that the producer completes with a value or an error. Together they let a caller start work, continue, and later wait for or chain on the result.
:::

Futures turn "call and wait" into "call, do other work, join". Their real power is composition: start the price lookup and the stock check in parallel and combine them when both finish, so latency is the maximum of the two rather than the sum. Composition is where Java adds something language-specific: `CompletableFuture` chains asynchronous stages without blocking a thread.

**Figure 37.19 — Composing futures.**

```mermaid
classDiagram
  class CompletableFuture~T~ {
    +supplyAsync(supplier, executor)$ CompletableFuture
    +thenApply(fn) CompletableFuture
    +thenCombine(other, fn) CompletableFuture
    +exceptionally(fn) CompletableFuture
    +orTimeout(t, unit) CompletableFuture
    +join() T
  }
  class Executor
  class QuoteService {
    +quote(sku) CompletableFuture
  }
  QuoteService ..> CompletableFuture~T~ : composes
  CompletableFuture~T~ ..> Executor : runs stages on
```

**Reading the diagram.** `QuoteService` starts two asynchronous stages on an executor and combines their futures with `thenCombine`; each stage runs on a pool thread and completes its future, which triggers dependent stages. No thread blocks until the final `join()` (or never, if the result is returned as a future to an asynchronous web framework). Results live in memory. Failure points are a stage that never completes (add `orTimeout`) and errors, which propagate along the chain until handled by `exceptionally`. Scaling depends on the executor; using the default common pool for blocking I/O is a classic mistake.

```java
import java.util.concurrent.*;

public class Quote {
    public static void main(String[] args) {
        ExecutorService io = Executors.newFixedThreadPool(8);   // dedicated pool for I/O
        CompletableFuture<Integer> price = CompletableFuture.supplyAsync(() -> sleepThen(80, 4999), io);
        CompletableFuture<Integer> stock = CompletableFuture.supplyAsync(() -> sleepThen(60, 3), io);
        long t0 = System.nanoTime();
        String quote = price.thenCombine(stock, (p, s) -> s > 0 ? "price " + p : "out of stock")
                            .orTimeout(500, TimeUnit.MILLISECONDS)
                            .exceptionally(e -> "fallback: cached price")
                            .join();
        System.out.printf("%s in ~%d ms%n", quote, (System.nanoTime() - t0) / 1_000_000);
        io.shutdown();
    }
    static int sleepThen(int ms, int v) {
        try { Thread.sleep(ms); } catch (InterruptedException e) { throw new RuntimeException(e); }
        return v;
    }
}
```

The program prints `price 4999 in ~80 ms` (the time varies slightly): the two calls overlap, so latency is the longer one, not 140 ms. In Python the same composition is `asyncio.gather(price(), stock())` inside an event loop, or two `executor.submit` calls followed by two `result()` calls.

### 37.16.4 Read-write lock

::: definition
**Definition — Read-write lock.** A lock that allows any number of concurrent readers or exactly one writer, never both; it improves throughput when reads greatly outnumber writes and each read holds the lock long enough for contention to matter (§6.10.5).
:::

A routing table or price list in memory is read by every request and replaced a few times per minute. A plain mutex serializes all readers; a read-write lock lets them proceed together. The design question is fairness: a reader-preferring lock can starve writers forever under constant reads, so most implementations prefer waiting writers. Python's standard library has no read-write lock; Java provides `ReentrantReadWriteLock` and `StampedLock` (which adds optimistic reads).

**Figure 37.20 — A writer-preferring read-write lock.**

```mermaid
classDiagram
  class RWLock {
    -cond Condition
    -readers int
    -writer bool
    -waiting_writers int
    +read_locked() context
    +write_locked() context
  }
  class PriceTable {
    -lock RWLock
    -prices dict
    +get(sku) int
    +replace_all(new_prices)
  }
  class RequestThread
  class RefreshThread
  PriceTable *--> RWLock
  RequestThread ..> PriceTable : get under read lock
  RefreshThread ..> PriceTable : replace under write lock
```

**Reading the diagram.** `PriceTable` owns a `RWLock` built from one condition variable and three counters. Many request threads read at once; the refresh thread takes the write lock, which waits for active readers to drain and blocks new readers while it waits (writer preference). All access is synchronous and in-process; the protected data is in memory. Failure points: writer starvation (prevented here), upgrading a read lock to a write lock (deadlocks if two readers try), and long work done while holding the lock. An alternative that often scales better is copy-on-write: build a new immutable table and swap one reference, so readers take no lock at all.

```python
import threading
import time
from contextlib import contextmanager


class RWLock:
    def __init__(self):
        self._cond = threading.Condition()
        self._readers, self._writer, self._waiting_writers = 0, False, 0

    @contextmanager
    def read_locked(self):
        with self._cond:
            while self._writer or self._waiting_writers:   # writer preference
                self._cond.wait()
            self._readers += 1
        try:
            yield
        finally:
            with self._cond:
                self._readers -= 1
                if self._readers == 0:
                    self._cond.notify_all()

    @contextmanager
    def write_locked(self):
        with self._cond:
            self._waiting_writers += 1
            while self._writer or self._readers:
                self._cond.wait()
            self._waiting_writers -= 1
            self._writer = True
        try:
            yield
        finally:
            with self._cond:
                self._writer = False
                self._cond.notify_all()


if __name__ == "__main__":
    lock, accounts = RWLock(), {"a": 500, "b": 500}     # invariant: a + b == 1000
    stats = {"violations": 0, "active": 0, "peak": 0}
    stats_lock = threading.Lock()

    def reader():
        for _ in range(300):
            with lock.read_locked():
                with stats_lock:
                    stats["active"] += 1
                    stats["peak"] = max(stats["peak"], stats["active"])
                time.sleep(0.0002)                      # simulated work: readers overlap
                if accounts["a"] + accounts["b"] != 1000:
                    stats["violations"] += 1
                with stats_lock:
                    stats["active"] -= 1

    def writer():
        for i in range(200):
            with lock.write_locked():
                accounts["a"] -= 1                      # invariant broken ...
                time.sleep(0)                           # yield mid-update
                accounts["b"] += 1                      # ... and restored
    threads = [threading.Thread(target=reader) for _ in range(6)] + [threading.Thread(target=writer)]
    for t in threads: t.start()
    for t in threads: t.join()
    print(f"violations seen by readers: {stats['violations']}; "
          f"readers overlapped: {stats['peak'] > 1}; final {accounts}")
```

Output:

```text
violations seen by readers: 0; readers overlapped: True; final {'a': 300, 'b': 700}
```

What to notice: readers never observe the moment between the writer's two updates, yet several readers hold the lock simultaneously. Releasing in `finally` ensures an exception inside the critical section cannot leave the lock held forever.

### 37.16.5 Double-checked locking and its pitfalls

::: definition
**Definition — Double-checked locking.** A lazy-initialization idiom that checks whether an object exists without a lock (fast path), and only if it does not, takes a lock, checks again, and creates it. It avoids locking on every access but is only correct if the language's memory model guarantees that a thread seeing the reference also sees the fully constructed object.
:::

The Singleton in §37.6 used this idiom safely in Python. In Java before the Java 5 memory model (JSR-133, 2004), and in Java today without `volatile`, it is broken [Bacon et al.; Manson et al. 2005]. The compiler and CPU may reorder the steps of `instance = new Config()` (allocate memory, run the constructor, publish the reference) so that the reference is published *before* the constructor finishes. A second thread on the fast path sees a non-null reference, skips the lock, and reads fields that still hold default values.

**Figure 37.21 — How double-checked locking fails without volatile.**

```mermaid
sequenceDiagram
  participant A as Thread A
  participant M as Shared memory
  participant B as Thread B
  A->>M: read instance, null
  A->>A: acquire lock, re-check null
  A->>M: allocate object, fields default
  A->>M: publish reference, reordered early
  B->>M: read instance, not null
  B->>M: read config.timeout, sees 0
  Note over B: uses half-built object
  A->>M: constructor sets timeout to 500
  A->>A: release lock
```

**Reading the diagram.** Thread A takes the slow path and Thread B the fast path; both read and write shared memory. Without a happens-before edge, A's write of the reference may become visible to B before A's writes of the fields: B never takes the lock, so nothing orders its reads after A's constructor. The failure is silent and rare, appearing under load on weakly ordered hardware or after a JIT optimization. The fixes below create the missing ordering; none adds a lock to the fast path.

```java
public final class ConfigHolder {
    private static volatile Config instance;      // volatile: safe publication

    static Config get() {
        Config local = instance;                   // one volatile read on the fast path
        if (local == null) {
            synchronized (ConfigHolder.class) {
                local = instance;
                if (local == null) {
                    instance = local = new Config(500);   // fully built before publication
                }
            }
        }
        return local;
    }

    static final class Config {
        final int timeoutMs;                       // final fields add a further guarantee
        Config(int timeoutMs) { this.timeoutMs = timeoutMs; }
    }
}
```

What to notice: `volatile` makes the write of `instance` a release and the read an acquire, so a thread that sees the reference also sees the constructor's writes. Simpler fixes usually win: the holder idiom or an enum (§37.6), eager initialization, or a plain `synchronized` method if the access is not hot. In Python, the risk is not reordering but the unlocked check-then-act race shown in §37.6.

**Table 37.3 — Concurrency failure scenarios.**

| What goes wrong | Why | Detection | Recovery | Prevention |
|---|---|---|---|---|
| Unbounded queue exhausts memory | Producers faster than consumers, no backpressure | Queue depth and memory climb steadily | Shed load, restart | Bounded queues, reject or block when full |
| Pool starvation | Tasks block waiting on tasks in the same pool | All workers busy, throughput zero, no CPU | Restart, raise timeouts | Separate pools per dependency; no nested waits |
| Lost exceptions | Future never inspected | Missing results, no error logs | Re-run failed tasks | Always call `result()` or attach a callback that logs |
| Writer starvation | Reader-preferring lock under constant reads | Config refresh latency grows without bound | Pause readers | Writer-preferring lock or copy-on-write swap |
| Half-built object visible | Unsafe publication in double-checked locking | Rare `NullPointerException` or default values under load | Restart | `volatile`, holder idiom, immutable objects |

## 37.17 Choosing a pattern

Patterns are answers; start from the question. Name the force that hurts (a growing `if` chain, an untestable class, a slow dependency on the request path), find the pattern that addresses that force, and state the trade-off you accept. If you cannot name the force, you do not need the pattern.

**Table 37.4 — Pattern selection: problem → pattern → trade-off.**

| Problem you have | Pattern | Trade-off you accept |
|---|---|---|
| Concrete class chosen at run time from data | Simple factory (§37.3.1) | One more indirection; registry must be kept complete |
| Framework workflow needs a part supplied by extensions | Factory method (§37.3.2) | A subclass per variant |
| Several products must vary together per environment | Abstract factory (§37.4) | Adding a product type changes every factory |
| Object with many optional parts and cross-field rules | Builder (§37.5) | Extra class; mostly unnecessary with keyword arguments |
| Exactly one instance per process | Module or composition-root instance; Singleton (§37.6) | Global state, hidden dependencies, test leakage |
| Interchangeable algorithms chosen by config | Strategy (§37.7) | Clients must know which strategy to pick |
| Open-ended reactions to a change in one process | Observer (§37.8) | Synchronous fan-out latency; lapsed listeners |
| Third-party interface does not match yours | Adapter (§37.9) | Translation layer to maintain |
| Optional cross-cutting behavior to combine freely | Decorator (§37.10) | Many small objects; order-dependent stacks |
| Lazy creation, access control or remote object | Proxy (§37.11) | Hidden cost (N+1 queries, network calls) |
| Undo, queueing, logging or replaying requests | Command (§37.12) | A class per operation; undo must be exact |
| Domain logic tangled with storage code | Repository (§37.13) | Fake drifts unless contract-tested; poor for reporting |
| Classes create their own dependencies; hard to test | Dependency injection (§37.14) | Wiring code or a container to understand |
| Behavior and legal actions depend on mode | State (§37.15.1) | A class per state; transition logic spread across classes |
| Fixed algorithm skeleton with variable steps | Template Method (§37.15.2) | Inheritance coupling |
| Ordered, short-circuiting request processing | Chain of Responsibility (§37.15.3) | Order bugs; harder debugging |
| Bursty work must not overwhelm a slow consumer | Producer–consumer (§37.16.1) | Queueing delay; in-memory work lost on crash |
| Many short tasks, bounded concurrency | Thread pool + futures (§37.16.2–3) | Sizing, starvation and lost exceptions to manage |
| Read-mostly shared data | Read-write lock or copy-on-write (§37.16.4) | Writer starvation or copy cost |
| Hot lazy initialization | Holder idiom, `volatile` DCL (§37.16.5) | Subtle memory-model reasoning |

::: recommendation
**Recommendation — Earn each pattern.** Write the straightforward version first. Introduce a pattern when the second variant arrives (a second notifier, a second storage backend) or when a test cannot be written. In Python, try the lightest form first: a function argument before a Strategy hierarchy, a module before a Singleton, a closure before a Command class. Patterns applied speculatively add indirection that every future reader pays for.
:::

## 37.18 Summary and revision notes

::: summary
- A **design pattern** is a named solution shape with known trade-offs. GoF groups patterns as creational, structural and behavioral; Repository and DI are enterprise patterns; producer–consumer, thread pools and futures are concurrency patterns.
- **Creational:** a simple factory centralizes a run-time class choice; a factory method lets subclasses choose the product; an abstract factory creates consistent families; a builder validates cross-field rules and emits an immutable product.
- **Singleton** means one instance *per process*; prefer one instance created in the composition root and injected. In Python, a module is the idiomatic singleton; in Java, the enum or holder idiom.
- **Strategy** swaps algorithms by composition; in Python a strategy is often a function. **State** swaps behavior as the object changes mode. **Template Method** fixes a skeleton and varies steps through inheritance.
- **Observer** is in-process, synchronous publish/subscribe; isolate failing observers and move slow ones behind a queue or broker (§30.5).
- **Adapter** changes an interface, **Decorator** keeps it and adds behavior, **Proxy** keeps it and controls access, **Facade** simplifies a subsystem. Python's `@decorator` syntax is a language feature, not the GoF pattern.
- **Command** turns requests into values for undo, queueing and replay. **Chain of Responsibility** underlies middleware; order matters.
- **Repository** hides storage behind a domain collection interface; contract-test every implementation. **Dependency injection** supplies dependencies from a composition root and realizes dependency inversion (§36.7).
- **Concurrency:** bound every queue; size pools with $N_{cpu} U_{cpu} (1 + W/C)$ and check downstream limits; always inspect futures; prefer writer-preferring read-write locks or copy-on-write for read-mostly data; double-checked locking in Java requires `volatile`.
:::

## 37.19 Knowledge checkpoint

1. What problem does a simple factory solve that a constructor call does not?
2. When does an abstract factory become painful to extend?
3. Name two reasons to make a builder's product immutable.
4. A service with a "singleton" cache runs 30 pods with 2 processes each. How many caches exist?
5. Why does the naive singleton in §37.6 create several instances under concurrency?
6. How do Strategy and State differ, given that their class diagrams are almost identical?
7. List two differences between Observer and broker-based publish/subscribe.
8. Classify each as Adapter, Decorator or Proxy: a retry wrapper; a gRPC client stub; a wrapper converting a vendor SDK's dictionaries into domain objects.
9. Name two uses of Python's `@` decorator syntax that are not the GoF Decorator.
10. Why does running a new command clear the redo stack?
11. What keeps an in-memory fake repository honest?
12. What is the difference between dependency injection and a service locator?
13. Using the sizing formula, how many threads for 16 cores, 50% target utilization, $W = 40$ ms and $C = 10$ ms?
14. Why should authentication run before per-user rate limiting in a middleware chain?
15. What exactly goes wrong in Java double-checked locking without `volatile`?

<details><summary>Answers</summary>

1. It moves the "which concrete class?" decision, driven by run-time data, into one place, so callers depend only on the interface and new variants do not touch call sites.
2. When you add a new product type: every concrete factory must implement a new creation method.
3. Invariants checked in `build()` cannot later be broken; immutable objects are thread-safe to share and safe to use as cache keys or to retry.
4. $30 \times 2 = 60$ independent caches, each with its own contents.
5. Check-then-act is not atomic: all threads read `None` before any assigns, and each constructs an instance.
6. A strategy is chosen by the client from outside and usually stays fixed; a state object changes the context's state itself as transitions occur.
7. Observer is synchronous and in-process with no durability; pub/sub through a broker is asynchronous, durable, and decouples publisher and subscribers in time and deployment.
8. Retry wrapper: Decorator. gRPC stub: Proxy (remote). SDK translator: Adapter.
9. Registration (`@app.route`), `@property`, `@dataclass` and `@staticmethod` transform or register rather than wrap an object behind the same interface.
10. Redo replays undone commands on the state they were undone from; after a new command, that state no longer exists, so replaying them would corrupt the history.
11. A shared contract test suite run against both the fake and the real implementation.
12. With DI, dependencies are passed in and visible in the constructor; with a service locator, the object fetches them from a registry, hiding them and coupling it to the locator.
13. $16 \times 0.5 \times (1 + 40/10) = 16 \times 0.5 \times 5 = 40$ threads.
14. Unauthenticated (possibly forged) requests would otherwise consume a real user's quota, enabling a cheap denial of service against that user; also, user identity is not known until authentication runs.
15. The write publishing the reference can become visible before the constructor's field writes; a thread on the unlocked fast path sees a non-null reference to a partially constructed object.
</details>

## 37.20 Interview questions

### Basic

**Q1. What is the Strategy pattern? Give a system-design example.** **Answer.** It encapsulates interchangeable algorithms behind one interface, chosen at run time. Examples: load-balancing policies (round robin, least connections) in a proxy, cache eviction policies (LRU, LFU), and retry backoff policies. It keeps the context closed to modification and makes each algorithm testable alone.

**Q2. Why is Singleton considered an anti-pattern?** **Answer.** It is global mutable state: dependencies are hidden, tests leak state into one another, two configurations cannot coexist, and it invites contention. It also misleads in distributed systems, being one per process, not per system. Create one instance in the composition root and inject it instead.

### Intermediate

**Q3. Compare Adapter, Decorator and Proxy.** **Answer.** All wrap another object. Adapter presents a *different* interface to make incompatible code fit; Decorator presents the *same* interface and adds behavior, and decorators stack; Proxy presents the same interface and controls access (lazy creation, permissions, remoteness). Infrastructure analogues: an anti-corruption layer (adapter), a caching or retrying client (decorator), an API gateway or sidecar (proxy).

**Q4. How would you make an `OrderService` unit-testable if it currently constructs a database client, an HTTP payment client and calls `datetime.now()`?** **Answer.** Define ports for the repository, payment gateway and clock; implement adapters for production; change `OrderService` to receive them via its constructor; wire them in a composition root; in tests pass an in-memory repository, a fake gateway and a fixed clock. Add contract tests so the fakes match the real adapters.

### Advanced

**Q5. Design the in-process notification pipeline for a service that sends 2,000 receipts per second at peak through a provider with 100 ms latency and a 1,500 requests/s limit.** **Answer.** Request threads produce Commands into a bounded queue (producer–consumer); a sender pool consumes them. By Little's Law the provider limit allows $1{,}500 \times 0.1 = 150$ requests in flight, so about 150 sender threads (fewer with an asynchronous client). Because 2,000/s exceeds 1,500/s, the queue grows at 500/s during the peak; bound it by memory (100,000 items ≈ 200 s of peak excess), and beyond that reject or spill to a durable broker. Wrap the client in decorators for retry with jitter and a circuit breaker, and make sends idempotent by order ID.

**Q6. A Java service occasionally reads a configuration timeout of 0 under load. The config is lazily created with double-checked locking. Explain and fix.** **Answer.** Without `volatile`, the reference to the config can be published before its constructor's writes are visible; a thread on the unlocked fast path sees a non-null, partially constructed object with default field values. Fix by declaring the field `volatile`, or better, use the initialization-on-demand holder idiom or eager initialization, and make the config's fields `final`.

## 37.21 Practical exercises

1. Add a `WhatsAppNotifier` to §37.3 by registering it from a separate module at import time. Which files changed?
2. Add a cloud family to the abstract factory in §37.4 with fake network latency, and write one contract test that runs against all three families.
3. Reorder the decorators in §37.10 to `RetryingPriceSource(CachingPriceSource(db))` and predict, then measure, the database call count.
4. Extend the Command example with an `ApplyCoupon` command whose undo restores the previous total, and persist the history to a JSON file.
5. Replace the read-write lock in §37.16.4 with copy-on-write (build a new dictionary, swap a reference) and compare reader throughput with 8 readers.
6. Vary `max_workers` in §37.16.2 from 1 to 64 and plot elapsed time; explain the curve with the sizing formula.

## 37.22 Design challenges

1. **Pluggable payments.** Design the payment module of a store that supports three processors, per-country routing, retries with idempotency keys, and a test mode. Identify where you would use Adapter, Strategy, Decorator, Abstract Factory and DI, and draw the class diagram.
2. **Collaborative editor backend.** Support undo/redo per user, an audit log, and asynchronous persistence of edits. Decide what the Command objects contain, where they are queued, and how undo interacts with other users' later edits.

## 37.23 References

1. Gamma, E., Helm, R., Johnson, R., Vlissides, J. *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley, 1994.
2. Freeman, E., Robson, E. *Head First Design Patterns*, 2nd ed. O'Reilly Media, 2020.
3. Fowler, M. *Patterns of Enterprise Application Architecture*. Addison-Wesley, 2002.
4. Fowler, M. "Inversion of Control Containers and the Dependency Injection pattern." martinfowler.com, 2004. https://martinfowler.com/articles/injection.html
5. Goetz, B., Peierls, T., Bloch, J., Bowbeer, J., Holmes, D., Lea, D. *Java Concurrency in Practice*. Addison-Wesley, 2006.
6. Schmidt, D., Stal, M., Rohnert, H., Buschmann, F. *Pattern-Oriented Software Architecture, Volume 2: Patterns for Concurrent and Networked Objects*. Wiley, 2000.
7. Bloch, J. *Effective Java*, 3rd ed. Addison-Wesley, 2018.
8. Evans, E. *Domain-Driven Design: Tackling Complexity in the Heart of Software*. Addison-Wesley, 2003.
9. Bacon, D., Bloch, J., Bogda, J., et al. "The 'Double-Checked Locking is Broken' Declaration." https://www.cs.umd.edu/~pugh/java/memoryModel/DoubleCheckedLocking.html
10. Manson, J., Pugh, W., Adve, S. "The Java Memory Model." *ACM POPL*, 2005.
11. Norvig, P. "Design Patterns in Dynamic Programming." Presentation, Object World, 1996. https://norvig.com/design-patterns/
12. Brooker, M. "Exponential Backoff And Jitter." AWS Architecture Blog, 2015.
13. Smith, K. D., et al. "PEP 318 – Decorators for Functions and Methods." 2003. https://peps.python.org/pep-0318/
14. Gross, S. "PEP 703 – Making the Global Interpreter Lock Optional in CPython." 2023. https://peps.python.org/pep-0703/
15. Django Software Foundation. *Django documentation: Middleware*. https://docs.djangoproject.com/en/stable/topics/http/middleware/
16. Spring. *Spring Framework Reference: The IoC Container; Proxying Mechanisms*. https://docs.spring.io/spring-framework/reference/
17. Spring. *Spring Data JPA Reference: Repositories*. https://docs.spring.io/spring-data/jpa/reference/
18. Python Software Foundation. *Python 3 Standard Library: `queue`, `concurrent.futures`, `threading`, `functools`, `logging`*. https://docs.python.org/3/library/

## 37.24 Open verification items

- Norvig (1996): exact presentation title, venue and the "16 of 23 patterns" figure; URL of the slides.
- Bacon et al. declaration: full author list and date.
- PEP 318 author attribution (Kevin D. Smith, Jim Jewett, Skip Montanaro, Anthony Baxter).
- Spring documentation wording recommending constructor injection for mandatory dependencies (as of 2026).
- Spring proxy defaults: JDK dynamic proxy for interface-implementing beans in Spring Framework versus class-based (CGLIB) proxies by default in Spring Boot (as of 2026).
- PEP 703 free-threaded build status in current CPython releases (experimental in 3.13; status as of 2026).
