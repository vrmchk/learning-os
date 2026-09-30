# Glossary

Terms worth knowing and being able to explain. Alphabetical. Never graded,
never queued — a term that deserves depth becomes a concept. Format and rules:
`.claude/skills/define/SKILL.md`. Link an entry as `[[glossary#Term]]`.

### Address space
*OS · first met: [[threads-and-scheduling]]*

**What it is:** The full range of memory addresses a process is allowed to
use. Each process gets its own, and it is mostly empty: addresses only turn
into real memory (RAM) when the process actually uses them.

**Say it like this:** "The address space is the range of addresses a process
can use, not memory it owns. A thread reserves 1 MB of address space for its
stack, but only the pages it actually writes to take up RAM — so a thousand
threads is a gigabyte of addresses, not a gigabyte of memory."

**Not to confuse with:** RAM usage (the working set) — how much physical
memory is really in use.

### Cache
*Hardware · also: CPU cache · first met: [[threads-and-scheduling]]*

**What it is:** A small, very fast memory inside or next to each CPU core that
keeps recently used data close at hand. Reading from it is up to ~100× faster
than reading from RAM.

**Say it like this:** "The CPU cache keeps the data a core just used right next
to it, because main memory is slow in comparison. It's why a context switch
costs more than it looks — the next thread finds the cache full of someone
else's data and runs slowly until it warms up."

**Not to confuse with:** an application cache (`IMemoryCache`, Redis) — your
code storing results so it doesn't recompute them.

### COM
*Windows · also: Component Object Model · first met: [[threads-and-scheduling]]*

**What it is:** An old Windows technology (1990s) that lets components written
in different languages call each other. Office automation and some Windows
system APIs are still exposed through it.

**Say it like this:** "COM is Windows' old component model — how you drive
Excel from code, for example. In .NET you meet it through interop, and it
brings threading rules of its own, like STA."

**Not to confuse with:** a COM port — a serial port, unrelated.

### Context switch
*OS · first met: [[threads-and-scheduling]]*

**What it is:** The OS taking one thread off a CPU core and putting another
one on: it saves the first thread's registers and loads the second's.

**Say it like this:** "A context switch is the OS swapping which thread runs on
a core. The direct cost is a few microseconds; the real cost is that the new
thread starts with a cold cache. Too many CPU-hungry threads on too few cores
means you spend the CPU on switching instead of work."

**Deeper:** [[threads-and-scheduling]]

### Core
*Hardware · first met: [[threads-and-scheduling]]*

**What it is:** One independent execution unit inside a CPU. An 8-core CPU can
run 8 threads truly at the same instant; everything else is waiting its turn.

**Say it like this:** "A core is the part of the CPU that actually executes
instructions. Eight cores means eight threads running at once, no more — so for
CPU-bound work, more threads than cores just adds switching. With
hyper-threading one core shows up as two logical processors, but they share the
same hardware."

### CPU-bound
*General · first met: [[parallelism-vs-concurrency]]*

**What it is:** Work whose speed is limited by computation — the CPU is busy
the whole time. Resizing images, hashing, compressing, heavy calculations.

**Say it like this:** "CPU-bound work is limited by how fast the processor can
compute. It holds a thread the whole time it runs, so the tools are threads and
parallelism, bounded by the number of cores. Making it async doesn't help —
there's nothing to wait for."

**Not to confuse with:** [[glossary#I/O-bound]].

### Device poller
*General · first met: [[threads-and-scheduling]]*

**What it is:** A loop that keeps asking a device or external system "anything
new?" every few milliseconds, forever — reading a scale, a barcode scanner, a
sensor.

**Say it like this:** "A poller is a loop that checks a device for new data on
a timer instead of being notified. It never finishes, so it belongs on its own
thread, not on the thread pool."

**Not to confuse with:** an event or callback — the device telling you, rather
than you asking.

### Handle
*OS · first met: [[threads-and-scheduling]]*

**What it is:** An ID the OS gives your process for a resource the OS manages —
a file, a thread, a lock, a network socket. You pass it back to the OS whenever
you use the resource, and close it when done.

**Say it like this:** "A handle is a ticket to something the OS owns. Your code
never touches the file or thread directly — it holds the handle and asks the OS.
Forgetting to close handles is a real leak: the handle count climbs until the
process runs out."

**Not to confuse with:** a .NET object reference — a handle points into the
OS's world, not the managed heap. Linux calls them file descriptors.

### HTTP 429
*Web · also: Too Many Requests · first met: [[threads-and-scheduling]]*

**What it is:** The HTTP status code a server returns when a client is sending
more requests than it will accept. Often comes with a `Retry-After` header.

**Say it like this:** "429 means 'slow down' — the server is protecting itself
by rejecting some requests instead of letting everything get slow. It's how you
shed load deliberately, and clients are expected to back off and retry."

**Not to confuse with:** 503 Service Unavailable — the server can't serve at
all, rather than refusing *you*.

### I/O-bound
*General · first met: [[parallelism-vs-concurrency]]*

**What it is:** Work whose speed is limited by waiting for input/output — the
network, a disk, a database — while the CPU sits idle.

**Say it like this:** "I/O-bound work spends its time waiting for something
outside the CPU. It doesn't need a thread while it waits, which is exactly what
async exploits — the same box can hold thousands of these operations in flight.
A faster CPU wouldn't help."

**Not to confuse with:** [[glossary#CPU-bound]].

### Kernel
*OS · first met: [[threads-and-scheduling]]*

**What it is:** The core part of the operating system. It runs with full
privileges and controls the CPU, memory and devices. Your application runs with
limited privileges and has to ask the kernel for anything that touches
hardware — a file, the network, a new thread.

**Say it like this:** "The kernel is the part of the OS that actually owns the
machine. Apps run in user mode and ask it for things through system calls —
open this file, send these bytes, create a thread. Crossing into the kernel is
more expensive than a normal function call, which is one reason threads cost
what they do."

**Not to confuse with:** other uses of the word — "the Linux kernel" is the
kernel of Linux; libraries like Semantic Kernel just borrowed the name.

### Kernel object
*OS · first met: [[threads-and-scheduling]]*

**What it is:** A small record the OS keeps in its own protected memory to
track something it manages — a thread, a file, a lock. Your code never sees it;
it gets a [[glossary#Handle]] to it.

**Say it like this:** "A kernel object is the OS's bookkeeping for a resource.
Every thread has one holding its state, priority and saved registers. So
creating a thread isn't just a stack — it's another entry the OS has to keep
and schedule."

### Latency
*General · first met: [[threads-and-scheduling]]*

**What it is:** How long one operation takes from start to finish — for a web
request, the time from the request arriving to the response being sent.

**Say it like this:** "Latency is how long *one* request takes. It's usually
reported as percentiles — p50, p99 — because the average hides the slow ones.
Async doesn't lower latency; parallelism can, by splitting one job across
cores."

**Not to confuse with:** [[glossary#Throughput]] — how *many* operations per
second.

### Little's Law
*General · first met: [[parallelism-vs-concurrency]]*

**What it is:** Operations in flight = arrival rate × how long each takes. At
500 requests/s and 200 ms each, 100 requests are in progress at any moment.

**Say it like this:** "Little's Law says how many things are in the system at
once: arrival rate times time in the system. Traffic fixes that number — so the
only question is what each in-flight request costs you. As a blocked thread it's
expensive; as an async state machine it's a few hundred bytes."

### p99
*General · also: 99th percentile, tail latency · first met: [[2026-09-13-gc-triggers-and-budgets]]*

**What it is:** The latency that 99% of requests beat and 1% don't. p50 is the
median; p99 and p999 describe the slow tail.

**Say it like this:** "p99 is the slowest 1% of requests. It matters because at
scale 1% is a lot of users, and because the tail is where GC pauses, lock
contention and pool starvation show up first — averages hide all of that."

**Not to confuse with:** the average (mean), which a few very slow requests
barely move.

### Page
*OS · first met: [[threads-and-scheduling]]*

**What it is:** The unit the OS hands out memory in — 4 KB on x64. Addresses
are mapped to physical memory one page at a time, and a page only gets real RAM
the first time it is touched.

**Say it like this:** "Memory is managed in 4 KB pages. Reserving memory just
claims addresses; the first write to a page triggers a page fault and the OS
backs it with RAM. That's why a thread's 1 MB stack usually costs a few pages,
not a megabyte."

**Not to confuse with:** a web page, or pagination in an API.

### Registers
*Hardware · first met: [[threads-and-scheduling]]*

**What it is:** A handful of tiny storage slots inside a core, holding the
values being worked on right now — plus where the thread is in its code
(instruction pointer) and where its stack is (stack pointer).

**Say it like this:** "Registers are the core's working memory for the current
instruction. A thread's 'state' is largely its registers, so a context switch is
saving one thread's registers and loading another's."

### Scheduler
*OS · first met: [[threads-and-scheduling]]*

**What it is:** The part of the OS that decides which ready thread runs on which
core, and for how long.

**Say it like this:** "The OS scheduler hands out cores to threads in time
slices and takes them back — when the slice runs out, when a higher-priority
thread needs the core, or when the thread blocks. .NET doesn't decide when a
thread runs; the scheduler does."

**Not to confuse with:** job schedulers (cron, Hangfire, Quartz) that run tasks
at set times, or .NET's `TaskScheduler`, which decides where a `Task` is queued.

**Deeper:** [[threads-and-scheduling]]

### SDK
*General · also: Software Development Kit · first met: [[threads-and-scheduling]]*

**What it is:** A package a vendor ships so you can build against their
product: a library to call, plus docs, samples and often tools.

**Say it like this:** "An SDK is the vendor's ready-made code for talking to
their product. Instead of calling their API or device directly, you reference
their library and call its methods — the Stripe SDK, the AWS SDK, a card
reader's native driver library."

**Not to confuse with:** an API — the API is the contract (what you can call);
the SDK is code that calls it for you. The .NET SDK is the same idea: the
compiler and tools for building .NET apps.

### STA
*Windows · also: Single-Threaded Apartment · first met: [[threads-and-scheduling]]*

**What it is:** A [[glossary#COM]] threading rule: an object living in an STA
may only be called from the thread that created it. The thread is marked before
it starts — `SetApartmentState(ApartmentState.STA)`.

**Say it like this:** "STA is COM's 'one thread only' rule. WinForms and WPF UI
threads are STA, and Office interop needs it. In backend code you almost never
meet it — it's one of the few reasons to create a thread yourself."

### Thread affinity
*.NET · first met: [[threads-and-scheduling]]*

**What it is:** A requirement that some code or object is only ever used from
one specific thread — a native driver, a UI control, an STA object.

**Say it like this:** "Thread affinity means 'always call me from the same
thread'. Async can't promise that — after an `await` you may resume on any pool
thread — so the fix is one dedicated thread that owns the resource, with other
code sending work to it through a queue."

**Not to confuse with:** CPU affinity — pinning a thread to a particular core.

### Throughput
*General · first met: [[threads-and-scheduling]]*

**What it is:** How many operations a system completes per unit of time —
requests per second, messages per minute.

**Say it like this:** "Throughput is how much work gets done per second.
Async raises the throughput a box can sustain for I/O-bound work; it doesn't
make any single request faster. Oversubscription is the case where throughput
falls even though the CPU is at 100%."

**Not to confuse with:** [[glossary#Latency]] — how long one operation takes.

### Time slice
*OS · also: quantum · first met: [[threads-and-scheduling]]*

**What it is:** How long the scheduler lets a thread run on a core before it
may be swapped out — a few to tens of milliseconds.

**Say it like this:** "Each running thread gets a time slice; when it's used
up, the scheduler can give the core to another ready thread. Your code never
controls when that happens, which is why a race can happen even on one core."
