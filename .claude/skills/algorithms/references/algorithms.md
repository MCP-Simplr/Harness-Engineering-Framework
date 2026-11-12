# Algorithms & data structures — reference

## Complexity cheatsheet

| Notation | Meaning | Example |
|---|---|---|
| O(1) | constant | hash map lookup, array index |
| O(log n) | logarithmic | binary search, balanced tree ops |
| O(n) | linear | single pass over a list |
| O(n log n) | linearithmic | comparison sort, merge/heap-based algorithms |
| O(n²) | quadratic | nested loop over the same collection |
| O(2ⁿ) / O(n!) | exponential/factorial | naive brute-force search — avoid past trivial n |

Rule of thumb: match the target complexity to your actual data sizes —
for anything on a hot request path handling thousands to millions of rows,
aim for O(n log n) or better; O(n²) is fine only for genuinely small,
bounded n (e.g. scoring a handful of report widgets), not for anything
that scales with user/record count.

## Data structure choice

- **Hash map/set** (`dict`/`set`) — O(1) average lookup, membership test,
  dedup. Default choice for "have I seen this" or "look up by key" instead
  of scanning a list (`x in some_list` on a large list is an O(n) smell —
  use a set).
- **List/array** — ordered, O(1) index access, O(n) search/insert-in-middle.
  Fine when you always iterate the whole thing or only append/pop at the
  end.
- **Heap / priority queue** (`heapq`) — O(log n) push/pop-min. Use for
  "top-k" or "always process the smallest/largest next" instead of
  re-sorting a list on every iteration.
- **Tree / balanced tree** — ordered traversal + O(log n) ops. Rarely
  hand-rolled in application code; a database index or a sorted structure
  from a library usually does this job already.
- **Graph** — model explicit relationships (dependency chains, agent call
  graphs, geographic adjacency). Use BFS/DFS for reachability/traversal,
  Dijkstra/A* for shortest weighted path — don't reach for these until the
  relationship is actually graph-shaped, not just "a few nested lookups."
- **Trie** — prefix search over a large string set (autocomplete, address
  matching). Only worth the complexity when a plain `LIKE 'prefix%'` query
  or in-memory list scan is a measured bottleneck.

## Algorithmic techniques

- **Two pointers / sliding window** — linear-time scans over sorted data or
  a fixed-size window, replacing an O(n²) nested loop.
- **Divide and conquer** — split, solve independently, merge (merge sort,
  most O(n log n) algorithms). Recognize it in library functions
  (`sorted()`, tree operations) rather than reimplementing.
- **Dynamic programming** — cache subproblem results when the same
  subproblem recurs (overlapping subproblems + optimal substructure). A
  strong signal you need it: a naive recursive solution that's exponential
  because it recomputes the same inputs repeatedly. Most straightforward
  business-rule arithmetic isn't DP — don't force-fit it.
- **Greedy** — take the locally-best choice at each step; correct only when
  the problem has the greedy-choice property (interval scheduling, some
  graph algorithms). Verify this property before trusting a greedy
  solution — it's an easy source of subtly-wrong "optimal" results.
- **Memoization / caching** — cache a pure function's result by input.
  Applies directly to expensive, repeatable calls: embedding generation,
  external API calls, LLM calls with identical prompts within a request.

## Common correctness/perf smells to catch in review

- A loop that does a DB query per iteration (N+1 queries) instead of one
  batched query — very easy to introduce in a repository method called
  from inside a loop.
- Membership testing (`in`) against a `list` inside a hot loop instead of a
  `set`/`dict`.
- Re-sorting a collection on every iteration instead of once up front, or
  using a heap when only the top-k matters.
- String concatenation in a loop (`s += ...`) instead of building a list
  and joining once, for anything beyond a handful of iterations.
- Recomputing the same expensive, deterministic result (an LLM call, an
  external API call, an embedding) instead of caching it within the
  request/session.
