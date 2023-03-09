import random
import time
import gc

class SimpleSearcher:
    def __init__(self, lst):
        self.lst = lst
        assert len(lst) > 0
        self.contains_containers = hasattr(self.lst[0], "is_container")
        for i in range(len(lst) - 1):
            child1, child2 = self.lst[i], self.lst[i+1]
            assert self.child_max(child1) < self.child_min(child2)
        self.min = self.child_min(self.lst[0])
        self.max = self.child_max(self.lst[-1])
        self.is_container = True

    def search(self, other):
        if other < self.min:
            return "L"
        if other > self.max:
            return "R"
        if self.contains_containers:
            for child in self.lst:
                sub_result = child.search(other)
                if sub_result in ["NOT_FOUND", "L"]:
                    return "NOT_FOUND"
                elif sub_result == "FOUND":
                    return "FOUND"
        else:
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

        if self.contains_containers:
            for child in self.lst:
                sub_successor = child.successor(other)
                if sub_successor is not None:
                    return sub_successor
        else:
            for child in self.lst:
                if other <= child:
                    return child
        return None

    def child_min(self, child):
        return child.min if self.contains_containers else child

    def child_max(self, child):
        return child.max if self.contains_containers else child

SS = lambda *lst: SimpleSearcher(lst)

ss = SS(22, 33, 44)

def sanity_check(ss):
    assert ss.search(20) == "L"
    assert ss.search(22) == "FOUND"
    assert ss.search(30) == "NOT_FOUND"
    assert ss.search(33) == "FOUND"
    assert ss.search(40) == "NOT_FOUND"
    assert ss.search(44) == "FOUND"
    assert ss.search(50) == "R"

    assert ss.successor(20) == 22
    assert ss.successor(21) == 22
    assert ss.successor(22) == 22
    assert ss.successor(23) == 33
    assert ss.successor(24) == 33
    assert ss.successor(30) == 33
    assert ss.successor(31) == 33
    assert ss.successor(32) == 33
    assert ss.successor(33) == 33
    assert ss.successor(43) == 44 
    assert ss.successor(44) == 44 
    assert ss.successor(45) is None

sanity_check(ss)

# Nest the searchers.
ss = SS(SS(22), SS(33, 44))
sanity_check(ss)


def test_easy_numbers(factory):
    M = 1500
    numbers = [100 * (i) for i in range(M)]
    searcher = factory(numbers)
    assert searcher.search(-1) == "L"
    assert searcher.search(M*100) == "R"
    assert searcher.successor(M*100) == None
    
    for i in range(M-1):
        assert searcher.search(100 * i) == "FOUND"
        assert searcher.successor(100 * i - 7) == 100 * i
        assert searcher.search(100 * i + 17) == "NOT_FOUND"
        
    for i in range(1, M):
        assert searcher.search(100 * i) == "FOUND"
        assert searcher.search(100 * i - 17) == "NOT_FOUND"

test_easy_numbers(SimpleSearcher)

def make_nested_container(lst, chunk_size):
    assert len(lst) > 0
    assert chunk_size > 1

    if len(lst) <= chunk_size:
        return SimpleSearcher(lst)

    recurse = lambda lst: make_nested_container(lst, chunk_size)

    sub_lists = []
    i = 0
    while i < len(lst):
        sub_lists.append(lst[i:i+chunk_size])
        i += chunk_size

    return recurse([recurse(sub_list) for sub_list in sub_lists])

test_easy_numbers(lambda lst: make_nested_container(lst, 10))

U = 10 * 1000 * 1000 # universe of ints

def test_random_equivalencies():
    for i in range(10):
        numbers = sorted(random.sample(range(U), k=500))
        lst1 = SimpleSearcher(numbers) 
        lst2 = make_nested_container(numbers, 5)
        lst3 = make_nested_container(numbers, 7)

        test_numbers = random.sample(range(U), k=200)
        for number in test_numbers:
            assert lst1.search(number) == lst2.search(number) == lst3.search(number)
            assert lst1.successor(number) == lst2.successor(number) == lst3.successor(number)
        

test_random_equivalencies()

TEST_NUMBERS = random.sample(range(U), k=3000)

def stress_test(numbers, chunk_size):
    lst = make_nested_container(numbers, chunk_size)
    result = []

    gc.collect()
    print(f"Starting chunk size {chunk_size}")
    t = time.time()
    for n in TEST_NUMBERS:
        result.append((lst.search(n), lst.successor(n)))
    delay = time.time() - t
    delay = (delay * 1000000) / len(TEST_NUMBERS)
    print(f"done with chunk size {chunk_size}: {delay: .1f} microseconds per trial")

print("Building sample data")
numbers = sorted(random.sample(range(U), k=1000000))
for i in range(2, 17):
    stress_test(numbers, i)
stress_test(numbers, 32)
stress_test(numbers, 64)
stress_test(numbers, 128)
stress_test(numbers, 500)
stress_test(numbers, 3000)
