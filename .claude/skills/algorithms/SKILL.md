---
name: algorithms
description: Algorithm and data-structure choice — complexity analysis, when to reach for a hash map/heap/tree/graph algorithm vs. a simple loop. Use when writing code with a performance-sensitive loop, choosing a data structure for lookups/ordering/dedup, evaluating whether an approach will scale with data size, or reviewing a diff for an accidental O(n²)/N+1 query. Not for language syntax or micro-benchmarking specific hardware.
---

# Algorithms

Reference: `references/algorithms.md`.

Default to the simplest correct approach; only reach for a named algorithm
or non-trivial data structure when there's a concrete size/latency reason
to (a loop over a few hundred rows doesn't need one). When you do, name the
complexity in the diff/PR description if it isn't obvious.
