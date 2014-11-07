tdidt
=====

This is going to be an implementation of the TDIDT algorithm for decision tree
learning. It is hopefully going to be a solution to the exercise 1 of the
[Machine Learning Lecture][machine_learning] at the University of Bonn.

Contributors:
* Timm Behner
* Philipp Bruckschen
* Patrick Kaster
* Markus Schwalb

The implementation accepts any CSV-file with a format as specified on the
exercise sheet i.e.  
The first line contains a sequence of attribute type declarations of the
form:

  a1 : T1 , a2 : T2, . . . , ak : Tk , ak+1 : Tk+1

where ai is the id of attribute i and Ti is its type (1 ≤ i ≤ k + 1). All
attributes have one of the following types:
– “n”: numerical
– “c”: categorical with at least three attribute values
– “b”: binary with attribute values “yes” and “no”

In the data file “data exercise 2.csv”, the first line looks like this:

  a:n, b:c, c:c, d:n, e:b, f:b, g:c, h:c, i:b, j:t

The last attribute ak+1 (in the example above: “j”) is always the target
attribute and has attribute type “b”.
Each subsequent line describes an example, e.g.,

  24, bb, cc, 3, yes, no, gb, hc, yes, yes
  33, bd, cc, 5, yes, no, gb, hd, yes, no


The output is as stated on the exercise sheet. Every computed information gain
is printed while TDIDT is running. Afterwards the learned dicision tree is
printed. At last the rate of correctly classified examples is printed.


[machine_learning]: http://www-kd.iai.uni-bonn.de/index.php?page=teaching_details&id=83


