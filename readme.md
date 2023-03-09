### Overview ##

This was basically a one-day project to get a rough idea of
how much the granularity of a search tree impacts its performance
for the simple operations of finding an element (search) or
finding a nearby element (successor).

### SPOILER ALERT ###

It seems like branches between 3 and 10 elements
work best for my Python implementation, at least based on the
machine I ran on (as well as the test data that I generated).

### Problem Statement ###

Suppose you have a large set or numbers (or
more generally, any type of data that supports the normal
comparison operators in an algebraically consistent way).
Create a data structure that supports not only search, but
also finding the successor (which rules out a simple hashing
scheme).  Try to build a data structure which will eventually
support reasonably fast inserts and deletes (which rules out
having one giant Python list).

#### Short answer #### 

Build some kind of tree-based data structure
that lets you use divide-and-conquer tactics for basic
operations like searching, inserting, and deleting.

My solution essentially produces this kind of structure:

<pre>
    NestedSearchTree (single root)
    NestedSearchTree (K)
    NestedSearchTree (K*L)
    SimpleSearch     (K*L*M)
    integers         (K*L*M*P)
</pre>

### Discussion ###

#### Prior work ####

Search trees are one of the most well-studied areas of
computer science.  You can see https://en.wikipedia.org/wiki/Search_tree
as an example that is just the tip of the iceberg. (Quick
warning: I did not break any new ground here). My experiment here
basically revolves around a balanced search tree with "wide" nodes. 

#### Zen of Python ####
In the famous PEP20, Tim Peters claims "Flat is
better than nested". It is unclear how broadly he wanted that advice
to be interpreted, but I think it's a good rule of thumb for
thinking about data structures.

#### Asmymtotic performance (Big-O) ####

If the only thing you know about the elements
in a set is that you can perform logical comparison operations on
them in constant time (which is the hypythosis here--i.e. I ignore
other properties of specific data types like integers that could
be exploited for more exotic solutions), then the big-O bounds
are completely well understood in computer science. You clearly
need O(n) space to store your data set, and you clearly can't do
better than worst-case O(log) time for searches (using comparisons alone).
Fortunately, it is super easy to achieve both of those bounds with relatively
simple data structures (including mine).

#### Practical perfomance ("real world") ####

As soon as you start to compare two algorithms (and corresponding data
structures) with the same theoretically big-O complexity
(e.g. linear space and log-time searches), it gets really difficult
to predict which approach actually works better in practice.

The big-O model has two main limitations.  First, it only considers
aymptotic performance bounded by a constant factor, so a theoretically
scalable algorithm may perform terribly for small data sets.  Second,
for big-O time calculations, you often only count a single metric
like the number of element comparisons, and you assume all other
overhead is negligible (such as dispatching functions, updating
counters, doing garbage collection, etc.), which isn't always
realistic.  These two limitations aren't completely unrelated,
but I think of them as somewhat separate concerns.

Having said all that, most reasonable algorithms that work
from a theoretical setting also perform reasonably well in
practical contexts, as long as you use some common sense, and
then you just kinda have to measure stuff and tune stuff to
squeeze out even better performance.

#### Flat vs. nested for search trees ####

The problem with deep trees for search problems is that they
are deep, and usually as you move down the layers of the tree,
you tend to waste time on things like function calls or low-level
cache misses by the processor. 

If you can make the tree more shallow (i.e. with wider nodes),
then you can make shorter traverals down the tree, and maybe
at certain nodes you will get lucky and exploit data locality.

The problem with making nodes wider is that for each reduction
in tree height, you induce an exponential widening of each node.  So, for
example, in order to make a tree six times shorter you would have to
process 64x more items at every node.

Using bigger numbers, consider two approaches for handling a
million items:

* Have roughly 20 levels with basically a single value at each node.
* Have a simple 2-level system with 1000 sublists of 1000 elements each.

The first approach seems clearly superior, unless you imagine that your
computer **strongly** benefits from processing all 1000 elements sort
of as a single unit of work.  It's not a completely preposterous
notion with modern computers, but it would be a big assumption if
you decided to go with the second approach purely for performance reasons.
(There may be other legimitate reasons for the second approach, such
as making it easier for the human to understand the algorithm.)

My hypothesis is that there's a middle ground between 2 and 1000
in terms of granularity.

### My approach ###

I spent a day fiddling with Python to implement three search classes
with the same protocols:

    SimpleSearch
    NestedSearchTree
    BinarySearcher

I then ran some stress tests to see how they perform.

At this point I would go to [the code](https://github.com/showell/binary-search-experiment/blob/main/search.py)
to see the details. (I commented the code heavily after the fact.)
            
### Example output ###

Here is a typical run, but the timings here are not super deterministic.

<pre>
Building sample data
done with  binary search:  33.0 microseconds per trial
done with chunk size   2:  38.5 microseconds per trial
done with chunk size   3:  43.2 microseconds per trial
done with chunk size   4:  37.4 microseconds per trial
done with chunk size   5:  26.8 microseconds per trial
done with chunk size   6:  31.3 microseconds per trial
done with chunk size   7:  35.7 microseconds per trial
done with chunk size   8:  53.0 microseconds per trial
done with chunk size   9:  42.0 microseconds per trial
done with chunk size  10:  41.9 microseconds per trial
done with chunk size  11:  33.5 microseconds per trial
done with chunk size  12:  34.3 microseconds per trial
done with chunk size  13:  31.8 microseconds per trial
done with chunk size  14:  45.1 microseconds per trial
done with chunk size  15:  54.3 microseconds per trial
done with chunk size  16:  63.7 microseconds per trial
Re-test binary for another data point
done with  binary search:  41.7 microseconds per trial
Try some big numbers
done with chunk size  32:  71.9 microseconds per trial
done with chunk size  64:  87.4 microseconds per trial
done with chunk size  128:  137.4 microseconds per trial
done with chunk size  500:  403.6 microseconds per trial
done with chunk size  3000:  1086.5 microseconds per trial
done with chunk size  6000:  2281.9 microseconds per trial
</pre>

### Observations ###

1. Using large chunk sizes (>=32, for example) clearly hurts
   the performance of search and successor.

2. The nested approach gives roughly comparable times to
   BinarySearcher.

3. The sweet spot for this particular run was using a chunk
   size of 5 elements. I ran this many times, and it seems
   pretty consistent that having 2 elements per list is
   slow in my current implementation. The sweet spot between
   reducing the actual number of comparisons to compute
   (i.e small chunks) while being able to efficiently
   compute things in linear loops (i.e. big chunks) seems
   to be about 3 to 10 elements.
