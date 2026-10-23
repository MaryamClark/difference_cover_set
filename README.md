# difference_cover_set

A set data structure supporting insert, delete, and k-th-smallest-element-in-range queries in O(√n) time using block decomposition over the value universe.

```python
from difference_cover_set import DifferenceCoverSet

s = DifferenceCoverSet()
s.insert(10)
s.insert(20)
s.insert(30)
assert s.kth_smallest_in_range(0, 100, 2) == 20
s.delete(20)
assert s.kth_smallest_in_range(0, 100, 2) == 30
```

## Why this exists

The problem: answer "what is the k-th smallest value in [l, r]?" on a dynamic set of integers, with updates and queries interleaved. A plain sorted list gives O(n) updates. A balanced BST gives O(log n) per operation but does not directly support the range-counting prefix needed for k-th-smallest-in-range without augmented order-statistics nodes, which are tedious to implement correctly in pure Python.

This library trades asymptotic optimality for implementation simplicity: it partitions the value universe into √U blocks, each holding a sorted list. Insert and delete are O(√n) due to list insertion cost; k-th-smallest-in-range is O(√n) to scan blocks plus O(log √n) for a binary search inside the target block. For moderate-sized integer sets this is fast in practice and the code is straightforward to audit.

## Edge cases

Inserting a value larger than the initial `universe_size` triggers a rebuild: all elements are reorganized into a wider block structure. This is an O(n) amortized cost paid on growth. If you know your value range in advance, pass a generous `universe_size` to the constructor to avoid mid-run rebuilds.

Negative values are rejected on insert. Queries clamp negative `l` to 0.

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

