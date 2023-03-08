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
        for child in self.lst:
            if self.contains_containers:
                sub_result = child.search(other)
                if sub_result in ["NOT_FOUND", "L"]:
                    return "NOT_FOUND"
                elif sub_result == "FOUND":
                    return "FOUND"
                assert sub_result == "R"
            elif other == child:
                return "FOUND"
            elif other < child:
                return "NOT_FOUND"
        assert False

    def successor(self, other):
        for child in self.lst:
            child_min = self.child_min(child)
            if other < child_min:
                return child_min
            
            if self.contains_containers:
                sub_successor = child.successor(other)
                if sub_successor is not None:
                    return sub_successor
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
    assert ss.successor(22) == 33
    assert ss.successor(23) == 33
    assert ss.successor(24) == 33
    assert ss.successor(30) == 33
    assert ss.successor(31) == 33
    assert ss.successor(32) == 33
    assert ss.successor(33) == 44
    assert ss.successor(43) == 44 
    assert ss.successor(44) is None
    assert ss.successor(45) is None

sanity_check(ss)

# Nest the searchers.
ss = SS(SS(22), SS(33, 44))
sanity_check(ss)


def test_easy_numbers(factory):
    M = 1000
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

def make_nested_container(lst):
    assert len(lst) > 0

    if len(lst) < 100:
        return SimpleSearcher(lst)

    sub_lists = []
    i = 0
    chunk_size = 30
    while i < len(lst):
        sub_lists.append(lst[i:i+chunk_size])
        i += chunk_size

    return make_nested_container([make_nested_container(sub_list) for sub_list in sub_lists])

test_easy_numbers(make_nested_container)
