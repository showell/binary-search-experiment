import random
import time
import gc

"""

STEP ONE:

Try to implement the simplest possible class to implement search.

    MAIN DATA STRUCTURE: Ordinary Python list of ordered elements:

        [22, 33, 44]


    PROTOCOL:

        Search returns LEFT, RIGHT, FOUND, or NOT_FOUND:

            <---------------------------------------------------------------------->
                      22      ...            33          ...         44

            ...LEFT  (22=FOUND) ...NOT_FOUND (33=FOUND) ...NOT_FOUND (44=FOUND) ...RIGHT

        Successor returns either an element or None:

            <---------------------------------------------------------------------->
                         22                33                44

             s=22      s=22     s=33      s=33        s=44 s=44  None

    ALGORITHM: Just use a simple linear search that exits as early as possible.

    MINOR THINGS TO NOTE:
        We have the LEFT/RIGHT values mostly for optimization purposes when
        we embed ourselves into bigger collections (more on that to come).

        We track min/max both for convenience sake, and to help us quickly
        short-circuit computations for values "outside" our range of elements.

    PROS:
        1. It's easy to understand.
        2. We can use this later to verify more complicated approachs.
        3. It uses O(N) space (and is probably close to the most compact way to store an
           arbitrary number of comparable elements in Python).

    CONS:
        1. Search is O(N), not O(log N). [We will discuss binary search later.]
        2. If we stick with a single big Python list, then operations like insert and
           delete will have worst-case O(N) time, and we know we can do much better.
"""

class SimpleSearch:
    def __init__(self, lst):
        assert len(lst) > 0
        for i in range(len(lst) - 1):
            assert lst[i] < lst[i+1]

        self.lst = lst
        self.min = self.lst[0]
        self.max = self.lst[-1]

    def search(self, other):
        if other < self.min:
            return "LEFT"
        if other > self.max:
            return "RIGHT"

        for child in self.lst:
            if other == child:
                return "FOUND"
            elif other < child:
                return "NOT_FOUND"

        assert False

    def successor(self, other):
        # return smallest value x in lst such that other <= x
        if other <= self.min:
            return self.min
        if other > self.max:
            return None

        for child in self.lst:
            if other <= child:
                return child
        return None


"""
STEP TWO:

    Create a NestedSearchTree class that can not only wrap N elements
    of SimpleSearch objects (giving you a way to store NxN elements in
    a two-level tree), but also wrap list of elements of itself (giving
    you an arbitrarily tall tree).


    Make this function support the same protocol as SimpleSearch, but
    we recursively call our children at times.

    THINGS TO NOTE:

        1) The NestedSearchTree class has very similar structure to
           SimpleSearch in terms of the algorithms.

        2) We do **linear** search at each level of the tree, but if we
           take an N-sized data set and build up a data structure with a
           tree of NestedSearchTree objects that each contain some bounded
           constant number of nodes, then the searches will run in logN
           time.

        3) Our space usage is still O(N), which is good, but if we go
           for super-granular nesting, we will probably double or triple
           the constant factor for the upper bound.

        4) We don't directly store any "leaf" elements (unless you count
           "min" and max").  We are basically just a controller class
           for our child containers.
"""

class NestedSearchTree:
    def __init__(self, lst):
        assert len(lst) > 0
        assert type(lst[0]) in [SimpleSearch, NestedSearchTree]

        for i in range(len(lst) - 1):
            child1, child2 = lst[i], lst[i+1]
            assert child1.max < child2.min

        self.lst = lst
        self.min = self.lst[0].min
        self.max = self.lst[-1].max

    def search(self, other):
        if other < self.min:
            return "LEFT"
        if other > self.max:
            return "RIGHT"

        for child in self.lst:
            sub_result = child.search(other)
            if sub_result in ["NOT_FOUND", "LEFT"]:
                return "NOT_FOUND"
            elif sub_result == "FOUND":
                return "FOUND"
        assert False

    def successor(self, other):
        # return smallest value x in lst such that other <= x
        if other <= self.min:
            return self.min
        if other > self.max:
            return None

        for child in self.lst:
            sub_successor = child.successor(other)
            if sub_successor is not None:
                return sub_successor
        return None


"""
TESTING!!!!

Since this is just kind of a one-day experiment, I don't get too
bureaucratic about setting up unit tests.

Instead, I rely heavily on a bunch of in-line assertions.
"""

def sanity_check(s):
    assert s.search(20) == "LEFT"
    assert s.search(22) == "FOUND"
    assert s.search(30) == "NOT_FOUND"
    assert s.search(33) == "FOUND"
    assert s.search(40) == "NOT_FOUND"
    assert s.search(44) == "FOUND"
    assert s.search(50) == "RIGHT"

    assert s.successor(20) == 22
    assert s.successor(21) == 22
    assert s.successor(22) == 22
    assert s.successor(23) == 33
    assert s.successor(24) == 33
    assert s.successor(30) == 33
    assert s.successor(31) == 33
    assert s.successor(32) == 33
    assert s.successor(33) == 33
    assert s.successor(43) == 44 
    assert s.successor(44) == 44 
    assert s.successor(45) is None

SS = lambda *lst: SimpleSearch(lst)
NST = lambda *lst: NestedSearchTree(lst)

# Use a flat searcher
sanity_check(SS(22, 33, 44))

# Nest the searchers.
sanity_check(NST(SS(22), SS(33, 44)))
sanity_check(NST(NST(SS(22), SS(33, 44))))

def test_easy_numbers(factory):
    M = 1500
    numbers = [100 * (i) for i in range(M)]
    searcher = factory(numbers)
    assert searcher.search(-1) == "LEFT"
    assert searcher.search(M*100) == "RIGHT"
    assert searcher.successor(M*100) == None
    
    for i in range(M-1):
        assert searcher.search(float(100 * i)) == "FOUND"
        assert searcher.successor(100 * i - 7) == 100 * i
        assert searcher.search(100 * i + 17) == "NOT_FOUND"
        
    for i in range(1, M):
        assert searcher.search(100 * i) == "FOUND"
        assert searcher.search(100 * i - 17) == "NOT_FOUND"

test_easy_numbers(SimpleSearch)

"""

    NEXT STEP: Add BinarySearcher

    One of the shortcomings of SimpleSearch is that it's slow, so
    I decided to address the slowness by arranging the **data** into
    a tree of NestedSearchTree nodes.

    I didn't **need** to re-arrange the data if all I cared about was
    the speed of searches.  Instead, I can just do binary search on
    a single Python list that stores ALL of my elements.  I can rely
    on binary search running in log-time since accessing a random element
    of a Python list requires O(1) time.

    The drawback of BinarySearcher is that it doesn't allow for future
    growth in terms of adding quick insert/delete/update operations.
    (I didn't explore those in my one-day exoeriment, to be clear, but
    I know that a tree-based structure is gonna be more flexible.)

    NOTE:

        1. The algorithms here are very vanilla, and then we also
           support the "LEFT" and "RIGHT" protocols.

        2. I did not micro-optimize the binary searches here at all.

    GOAL:

        We will use this class as a baseline for performance
        measurements.
"""

class BinarySearcher:
    def __init__(self, lst):
        self.lst = lst
        assert len(lst) > 0
        self.min = self.lst[0]
        self.max = self.lst[-1]

    def search(self, other):
        if other < self.min:
            return "LEFT"
        if other > self.max:
            return "RIGHT"

        def f(i, j):
            if i >= j:
                return "NOT_FOUND"
            mid = (i + j) // 2
            if self.lst[mid] == other:
                return "FOUND"
            if other < self.lst[mid]:
                return f(i, mid)
            else:
                return f(mid+1, j)

        return f(0, len(self.lst))

    def successor(self, other):
        if other <= self.min:
            return self.min
        if other > self.max:
            return None

        def f(i, j, successor):
            if i >= j:
                return successor
            mid = (i + j) // 2
            if self.lst[mid] == other:
                return other
            if other < self.lst[mid]:
                return f(i, mid, self.lst[mid])
            else:
                return f(mid+1, j, successor)

        return f(0, len(self.lst), None)


test_easy_numbers(BinarySearcher)

"""

    UGLINESS: Build up trees of NestedSearchTree objects.

        If this were production code, I would try to be a lot cleaner,
        but for the purpose of gathering measurements, I want a quick
        and dirty way to build up search trees.

        MOST COMPLICATED TREE:

            After recursion, this function could return something like:


                A root NestedSearchTree
                    containing a list of K
                        NestedSearch elements, each of which
                            contain a list of L NestedSearchTrees,
                                each containing M BinarySearchers,
                                    each containg P elements of some
                                        comparable data type

            Or more concisely:

                NestedSearchTree (single root)
                NestedSearchTree (K)
                NestedSearchTree (K*L)
                SimpleSearch     (K*L*M)
                integers         (K*L*M*P)

            (And, of course, we are not constrained to integers; we just
            need our data type to support comparisons.)


""" 
    
def build_searcher(lst, chunk_size):
    assert len(lst) > 0

    if chunk_size == 0:
        return BinarySearcher(lst)

    assert chunk_size > 1

    if len(lst) <= chunk_size:
        if type(lst[0]) in [SimpleSearch, NestedSearchTree]:
            return NestedSearchTree(lst)
        else:
            return SimpleSearch(lst)

    recurse = lambda lst: build_searcher(lst, chunk_size)

    sub_lists = []
    i = 0
    while i < len(lst):
        sub_lists.append(lst[i:i+chunk_size])
        i += chunk_size

    return recurse([recurse(sub_list) for sub_list in sub_lists])

"""

AND FINALLY!!!

    Stress test various configurations.

"""

test_easy_numbers(lambda lst: build_searcher(lst, 10))

U = 100_000_000 # universe of ints

def test_random_equivalencies():
    for i in range(10):
        numbers = sorted(random.sample(range(U), k=500))
        lst1 = SimpleSearch(numbers) 
        lst2 = build_searcher(numbers, 5)
        lst3 = BinarySearcher(numbers)

        test_numbers = random.sample(range(U), k=200)
        for number in test_numbers:
            assert lst1.search(number) == lst2.search(number) == lst3.search(number)
            assert lst1.successor(number) == lst2.successor(number) == lst3.successor(number)
        

test_random_equivalencies()

# Make our test numbers floats so that comparisons are perhaps
# more expensive than normal int comparisons.
TEST_NUMBERS = [float(n) for n in random.sample(range(U), k=6000)]

def stress_test(numbers, chunk_size):
    lst = build_searcher(numbers, chunk_size)

    # Make sure our lst is at least plausibly correct.
    assert lst.search(numbers[0]) == "FOUND"
    assert lst.search(-27.0) == "LEFT"
    assert lst.search(U+1) == "RIGHT"
    assert lst.successor(0) == numbers[0]
    assert lst.successor(U+1) == None

    gc.collect()
    t = time.time()
    for n in TEST_NUMBERS:
        _ = lst.successor(n)
        _ = lst.search(n)
    delay = time.time() - t
    delay = (delay * 1_000_000) / len(TEST_NUMBERS)
    flavor = f"chunk size {chunk_size: 3d}" if chunk_size else " binary search"
    print(f"done with {flavor}: {delay: .1f} microseconds per trial")

print("Building sample data")
numbers = sorted(random.sample(range(U), k=1_500_000))

stress_test(numbers, 0)
for i in range(2, 17):
    stress_test(numbers, i)
print("Re-test binary for another data point")
stress_test(numbers, 0)
print("Try some big numbers")
stress_test(numbers, 32)
stress_test(numbers, 64)
stress_test(numbers, 128)
stress_test(numbers, 500)
stress_test(numbers, 3000)
stress_test(numbers, 6000)

""" See the readme in this project for sample output. """
