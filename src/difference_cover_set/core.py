import bisect
import math


class DifferenceCoverSet:
    """A set of integers supporting insert, delete, and k-th-smallest-in-range queries.

    Design decision: We use a block-decomposition approach where the universe of
    stored keys is divided into consecutive blocks of width √U. Within each block
    we store a sorted list of elements and a prefix count. Querying the k-th
    smallest element in [l, r] is done by locating the block that contains the
    answer via accumulated prefix counts, then performing a binary search inside
    that block.

    The block width grows with the maximum value seen so far, keeping each block's
    span close to √U. This yields O(√n) amortized cost for insert and delete (a
    block split/merge is O(√n)) and O(√n) for k-th-smallest queries (scan blocks
    plus a binary search).

    The structure is purely deterministic; no wall-clock dependence.
    """

    def __init__(self, universe_size: int = 1 << 16):
        if universe_size < 4:
            universe_size = 4
        self._universe = universe_size
        block_count = max(1, int(math.isqrt(universe_size)))
        self._block_width = max(1, (universe_size + block_count - 1) // block_count)
        self._block_count = block_count
        self._blocks: list[list[int]] = [[] for _ in range(block_count)]
        self._total = 0

    # -- internal helpers -------------------------------------------------

    def _block_index(self, value: int) -> int:
        idx = value // self._block_width
        if idx >= self._block_count:
            idx = self._block_count - 1
        return idx

    def _rebuild(self, new_universe: int) -> None:
        all_vals: list[int] = []
        for blk in self._blocks:
            all_vals.extend(blk)
        all_vals.sort()
        self.__init__(new_universe)  # type: ignore[misc]
        for v in all_vals:
            b = self._block_index(v)
            bisect.insort(self._blocks[b], v)
        self._total = len(all_vals)

    def _maybe_grow(self, value: int) -> None:
        if value >= self._universe:
            new_universe = self._universe
            while new_universe <= value:
                new_universe *= 2
            self._rebuild(new_universe)

    # -- public API -------------------------------------------------------

    def insert(self, value: int) -> bool:
        """Insert an integer value. Returns True if inserted, False if already present."""
        if value < 0:
            raise ValueError("values must be non-negative")
        self._maybe_grow(value)
        b = self._block_index(value)
        pos = bisect.bisect_left(self._blocks[b], value)
        if pos < len(self._blocks[b]) and self._blocks[b][pos] == value:
            return False
        self._blocks[b].insert(pos, value)
        self._total += 1
        return True

    def delete(self, value: int) -> bool:
        """Delete value. Returns True if it was present, False otherwise."""
        if value < 0 or value >= self._universe:
            return False
        b = self._block_index(value)
        blk = self._blocks[b]
        pos = bisect.bisect_left(blk, value)
        if pos < len(blk) and blk[pos] == value:
            del blk[pos]
            self._total -= 1
            return True
        return False

    def __contains__(self, value: int) -> bool:
        if value < 0 or value >= self._universe:
            return False
        b = self._block_index(value)
        blk = self._blocks[b]
        pos = bisect.bisect_left(blk, value)
        return pos < len(blk) and blk[pos] == value

    def __len__(self) -> int:
        return self._total

    def count_in_range(self, l: int, r: int) -> int:
        """Return the number of stored elements with l <= value <= r."""
        if l > r:
            return 0
        if r < 0:
            return 0
        if l < 0:
            l = 0
        if r >= self._universe:
            r = self._universe - 1
        bl = self._block_index(l)
        br = self._block_index(r)
        if bl == br:
            blk = self._blocks[bl]
            left = bisect.bisect_left(blk, l)
            right = bisect.bisect_right(blk, r)
            return right - left
        total = 0
        first = self._blocks[bl]
        total += bisect.bisect_right(first, r) - bisect.bisect_left(first, l)
        last = self._blocks[br]
        total += bisect.bisect_right(last, r) - bisect.bisect_left(last, l)
        for i in range(bl + 1, br):
            total += len(self._blocks[i])
        return total

    def kth_smallest_in_range(self, l: int, r: int, k: int) -> int:
        """Return the k-th smallest element in [l, r] (1-indexed).

        Raises ValueError if k is out of range or if no elements fall in [l, r].
        """
        if k < 1:
            raise ValueError("k must be >= 1")
        if l > r:
            raise ValueError("range is empty (l > r)")
        if r < 0:
            raise ValueError("no elements in range")
        if l < 0:
            l = 0
        if r >= self._universe:
            r = self._universe - 1
        bl = self._block_index(l)
        br = self._block_index(r)
        remaining = k
        for bi in range(bl, br + 1):
            blk = self._blocks[bi]
            lo = l if bi == bl else 0
            hi = r if bi == br else self._universe - 1
            start = bisect.bisect_left(blk, lo)
            end = bisect.bisect_right(blk, hi)
            cnt = end - start
            if cnt >= remaining:
                return blk[start + remaining - 1]
            remaining -= cnt
        raise ValueError("k exceeds number of elements in range")

    def __iter__(self):
        for blk in self._blocks:
            yield from blk
