#!/usr/bin/env python3

import sys
import random
import math
import copy

class SplittingTest:
    """
    Test for splitting a TDIDTNode
    """
    def __init__(self,test,attribute,attribute_type,split_value):
        self.test = test
        self.attribute = attribute
        self.attribute_type = attribute_type
        self.split_value = split_value

    def __str__(self):
        """
        In dependence of the type of the attribute
        different strings are returned to fullfill the required
        output style
        """

        if self.attribute_type == "n":
            return "{} < {}".format(self.attribute, self.split_value)
        elif self.attribute_type == "c":
            return "{} is contained in {}".format(self.attribute,self.split_value)
        else:
            return "{} is true".format(self.attribute)

    def __call__(self,value):
        """
        Can be called as a function, returns the boolean value of the test
        """
        return self.test(value)

class Example:
    """
    example for the training with tdidt
    """
    def __init__(self,attribute_hash,outcome):
        self.attribute_hash = attribute_hash
        self.outcome = outcome

    def __str__(self):
        return str(self.attribute_hash) + "------------" + str(self.outcome)

def get_information_gain(ppos, pneg, npos, nneg):
    """
    compute the information gain given with the four parameters
    :param ppos: number of positive examples with outcome "yes"
    :param pneg: number of positive examples with outcome "no"
    :param npos: number of negative examples with outcome "yes"
    :param nneg: number of negative examples with outcome "no"
    """
    print("Ppos: {}, Pneg: {}, Npos: {}, Nneg: {}".format(ppos,pneg,npos,nneg))
    total = float(ppos + pneg + npos + nneg)
    p_total = float(ppos + pneg)
    n_total = float(npos + nneg)
    information_gain = entropy((ppos+npos)/total,(pneg + nneg)/total)
    if p_total > 0:
        information_gain -= p_total/total * entropy(ppos/p_total,pneg/p_total)
    if n_total > 0:
        information_gain -= n_total/total * entropy(npos/n_total,nneg/n_total)
    return information_gain

def entropy(p,n):
    """
    compute the entropy of p and n

    :param p: probability of positives
    :type  p: float
    :param n: probability of negatives
    :type  n: float
    """
    if n == 0:
        return p*math.log(1.0/p, 2)
    elif p == 0:
        return n*math.log(1.0/n, 2)
    return p*math.log(1.0/p, 2) + n*math.log(1.0/n, 2)

class ExampleSet:
    """
    Containes a set of examples this includes the variables

        * examples: a list of all contained examples
        * entropy:  the entropy of all contained examples
        * negatives: the total number of examples with positive outcome
        * positives: the total number of examples with negative outcome
    """
    def __init__(self,examples = []):
        self.examples = []
        self.positives = 0
        self.negatives = 0

    def initialize_from_file(self,filename):
        """
        initialize this example set from a file as specified by the exercise
        """
        input_file = open(filename,'r')

        # read the first line with attributes 
        init_line = input_file.readline()
        #  and parse this line into attribute name and type
        # FIXME this line should be easier to code, right?
        self.attributes = { x[0] : x[1] for x in list(map(lambda s : [s[0],s.rstrip()[-1]], init_line.split(',')))[0:-1]}

        # parse the rest of the file containing the examples
        self.examples = []
        self.positives = 0
        self.negatives = 0
        for line in input_file:
           example_list = list(map(lambda s : s.rstrip() , line.split(',')))
            # FIXME IOOUUUUU there has to be a way which is prettier than this
           example_hash = dict(zip(sorted(self.attributes),example_list))
           for key in example_hash.keys():
               if self.attributes[key] == 'n':# convert all numerical values from str to float
                   example_hash[key] = float(example_hash[key])
               elif self.attributes[key] == 'b': # and all boolean values from str to boolean
                   example_hash[key] = (example_hash[key] == "yes")

           self.examples.append(Example(example_hash,example_list[-1] == "yes"))
           if example_list[-1] =="yes":
               self.positives += 1
           else:
               self.negatives += 1

        self.entropy = entropy(float(self.positives)/len(self.examples), float(self.negatives)/len(self.examples))

    def best_split_numerical(self,attribute):
        """
        compute the best splitting test for the numerical attribute ``attribute``
        this is done by the algorithm given on the exercise sheet
        """
        max_information_gain = None
        splitting_test = None
        split_value = None
        passing_examples = [0,0]
        failing_examples = [self.positives,self.negatives]

        # sort the examples according to the values of the attribute
        self.examples.sort(key=lambda e : e.attribute_hash[attribute])
        for i_idx in range(len(self.examples)-1):
            if self.examples[i_idx].outcome:
                failing_examples[0] -= 1
                passing_examples[0] += 1
            else:
                failing_examples[1] -= 1
                passing_examples[1] += 1
            if not self.examples[i_idx].outcome == self.examples[i_idx+1].outcome:              # update distribution of outcomes
                current_information_gain = get_information_gain(passing_examples[0],passing_examples[1],failing_examples[0],failing_examples[1])
                if max_information_gain is None or max_information_gain < current_information_gain:
                    max_information_gain = current_information_gain
                    mean = (self.examples[i_idx].attribute_hash[attribute] + self.examples[i_idx+1].attribute_hash[attribute])/2
                    split_value = mean
                    splitting_test = lambda x : x.attribute_hash[attribute] < split_value
        return [max_information_gain,SplittingTest(splitting_test,attribute,"n",split_value)]

    def best_split_categorical(self,attribute):
        """
        compute the best splitting test for the categorical attribute ``attribute``
        this is done by the algorithm given on the exercise sheet
        """
        max_information_gain = None
        splitting_test = None
        histograms = {}                 # histogram for each value of the attribute
        information_gain = {}           # information gain for each value of the attribute

        # compute the histograms
        for example in self.examples:
            value = example.attribute_hash[attribute]
            if not value in list(histograms.keys()):
                histograms[value] = [0,0]
            if example.outcome:
                histograms[value][0] += 1
            else:
                histograms[value][1] += 1

        # compute the information gain for each attribute
        for value in histograms.keys():
            ppos = histograms[value][0]
            pneg = histograms[value][1]
            npos = self.positives - ppos
            nneg = self.negatives - pneg
            information_gain[value] = get_information_gain(ppos,pneg,npos,nneg)


        # sort the values of the attribute descending after their information gain
        sorted_values = sorted(information_gain.keys(),key=lambda x : information_gain[x],reverse=True)

        s = []
        s_histogram = [0,0]
        # add the values to S while the information gain of x \in S still rises
        previous_gain = 0
        for value in sorted_values:
            cur_histogram = copy.deepcopy(s_histogram)
            cur_histogram[0] += histograms[value][0]
            cur_histogram[1] += histograms[value][1]
            cur_info_gain = get_information_gain(cur_histogram[0],cur_histogram[1],self.positives-cur_histogram[0],self.negatives-cur_histogram[1])
            if previous_gain < cur_info_gain:
                previous_gain = copy.deepcopy(cur_info_gain)
                # add the value to s
                s.append(value)
                # update the histogram of s
                s_histogram[0] += histograms[value][0]
                s_histogram[1] += histograms[value][1]

        max_information_gain = previous_gain
        splitting_test = lambda x : x.attribute_hash[attribute] in s
        return [max_information_gain,SplittingTest(splitting_test,attribute,"c",s)]


    def split_boolean(self,attribute):
        """
        compute the information_gain and splitting test according to the boolean attribute ``attribute``
        """
        passing = [0,0]
        failing = [self.positives,self.negatives]
        for example in self.examples:
            if example.attribute_hash[attribute]:
                if example.outcome:
                    passing[0] += 1
                else:
                    passing[1] += 1
        failing[0] -= passing[0]
        failing[1] -= passing[1]
        information_gain = get_information_gain(passing[0],passing[1],failing[0],failing[1])
        test = lambda e : e.attribute_hash[attribute]
        splitting_test = SplittingTest(test,attribute,"b",True)
        #print("Information gain: {}, splitting test: {}".format(information_gain,splitting_test))
        return [information_gain,splitting_test]


    def get_split(self,attribute):
        """
        Computes the best splitting test for the given attribute. This method is a wrapper for the 
        methods ``best_split_numerical`` , ``best_split_categorical`` and ``split_boolean``
        In either case is the running time linear with respect to the number of examples
        """
        max_information_gain = None
        splitting_test       = None
        if self.attributes[attribute] == 'n': # find the best split for numerical attributes
            [max_information_gain,splitting_test] = self.best_split_numerical(attribute)
        elif self.attributes[attribute] == 'c': # find the best split for categorical attributes
            [max_information_gain,splitting_test] = self.best_split_categorical(attribute)
        else: # there is only boolean values left which have only one possible splitting test
            [max_information_gain,splitting_test] = self.split_boolean(attribute)
        return [max_information_gain,splitting_test]


    def get_test_instances(self,quantity):
        """
        Deletes ``quantity`` examples from the list of examples and returns an ``ExampleSet`` containing those examples.
        This is intended for supplying an ExampleSet for testing an learned decision tree
        """
        random.seed()
        test_examples = ExampleSet()
        for i in range(quantity):
            rand = random.randint(0,len(self.examples)-1)
            test_examples.examples.append(self.examples.pop(rand))

        return test_examples

    def split(self,test):
        """
        Split the example_set in examples which fullfill the test and those which do not fullfill the test.
        Two example sets are returned. The first one containes the examples which fullfill the test.
        """
        succeeding_example_set = ExampleSet()
        failing_example_set = ExampleSet()

        for example in self.examples:
            if test(example):
                succeeding_example_set.examples.append(example)
                if example.outcome:
                    succeeding_example_set.positives += 1
                else:
                    succeeding_example_set.negatives += 1
            else:
                failing_example_set.examples.append(example)
                if example.outcome:
                    failing_example_set.positives += 1
                else:
                    failing_example_set.negatives += 1

        succeeding_example_set.attributes = self.attributes
        failing_example_set.attributes = self.attributes
        return [succeeding_example_set, failing_example_set]


class TDIDTNode:
    """
    a node in a decision tree as used by TDIDT
    """
    def __init__(self,example_set,parent_idx=None,left_child_idx=None,right_child_idx=None):
        self.example_set     = example_set
        self.parent_idx      = parent_idx
        self.left_child_idx  = left_child_idx
        self.right_child_idx = right_child_idx
        self.is_leaf         = False
        self.test            = None
        self.outcome         = None
        # only needed to fullfill exercise requirements
        self.identifier      = None
        self.parent_test_outcome = None

    def setParent(self,idx):
        self.parent_idx = idx

    def setLeftChild(self,idx):
        self.left_child_idx = idx

    def setRightChild(self,idx):
        self.right_child_idx = idx

    def __str__(self):
        return "{} {} {} {} {}".format(self.identifier,self.parent_test_outcome,self.test,self.left_child_idx,self.right_child_idx)

def TDIDT(node_list,attribute_list,current_node_idx):
    """
    TDIDT algorithm for learning a decision tree given the examples contained in the root node

    :param node_list: list of nodes in the decision tree
    :param attribute_list: list of attributes not yet used on the current path to the root
    :param current_node_idx: index of the node which should be considered
    """
    current_node = node_list[current_node_idx]

    # if the current node has only true or false example outcomes
    # it is perfectly classified and we can return
    if current_node.example_set.positives == 0 and current_node.example_set.negatives > 0:
        current_node.is_leaf    = True
        current_node.outcome = False
        return

    if current_node.example_set.positives > 0 and current_node.example_set.negatives == 0:
        current_node.is_leaf    = True
        current_node.outcome = True
        return

    # if no attriubute is left to classify the data we considere
    # the node to be classified with the majorit of outcomes
    if not attribute_list:
        current_node.is_leaf = True
        current_node.outcome = (current_node.example_set.positives > current_node.example_set.negatives)
        return

    # if there are no examples left, then use the majority of the parent node
    if len(current_node.example_set.examples) == 0:
        current_node.is_leaf = True
        parent_node = node_list[current_node.parent_idx]
        current_node.outcome = (parent_node.example_set.positives >= parent_node.example_set.negatives)
        return

    print("Lengt: {}, Sum of pos and neg: {}".format(len(current_node.example_set.examples),current_node.example_set.positives + current_node.example_set.negatives))

    # now there is certenly something left to be classified
    # calculate the information gain of every attribute
    max_information_gain = None
    splitting_test       = None
    for attribute in attribute_list:
        information_gain , test = current_node.example_set.get_split(attribute)
        # only needed to fullfill the exercise requirements
        print("Information gain: {}, Test: {}".format(information_gain,test))
        if max_information_gain is None or information_gain > max_information_gain:
            max_information_gain = information_gain
            splitting_test       = test
    # only needed to fullfill the exercise requirements
    print("Maximum Information gain {}, Test {}".format(max_information_gain,splitting_test))

    # split the example set with the given test with the maximum information gain
    succeeding_example_set , failing_example_set = current_node.example_set.split(splitting_test)
    current_node.test = splitting_test

    # remove the attribute from the list of possible attributes
    next_attribute_list = copy.deepcopy(attribute_list)
    next_attribute_list.remove(splitting_test.attribute)
    #print(next_attribute_list)

    # make decision tree nodes for each new example set
    left_node = TDIDTNode(succeeding_example_set,current_node_idx)
    right_node = TDIDTNode(failing_example_set,current_node_idx)

    current_node.left_child_idx = len(node_list)
    current_node.right_child_idx = len(node_list)+1

    # only needed to fullfill exercise requirements
    left_node.identifier = current_node.left_child_idx
    right_node.identifier = current_node.right_child_idx
    left_node.parent_test_outcome = "yes"
    right_node.parent_test_outcome = "no"

    node_list.append(left_node)
    node_list.append(right_node)

    # and invoke TDIDT on each node
    TDIDT(node_list,next_attribute_list,current_node.left_child_idx)
    TDIDT(node_list,next_attribute_list,current_node.right_child_idx)


def classify(example,node_list):
    """
    traverses with the given example the decision tree and returns the outcome
    """
    current_node = node_list[0]
    while not current_node.is_leaf:
        if current_node.test(example):
            current_node = node_list[current_node.left_child_idx]
        else:
            current_node = node_list[current_node.right_child_idx]
    return current_node.outcome


if len(sys.argv) != 2:
    print("Usage {} FILENAME".format(sys.argv[0]))
    sys.exit(1)

# create Example Set from given file
e = ExampleSet()
e.initialize_from_file(sys.argv[1])

# get a third of the examples for testing
test_set = e.get_test_instances(int((1.0/3)*len(e.examples)))

# run TDIDT
node_list = [TDIDTNode(e)]
attribute_list = list(e.attributes.keys())
TDIDT(node_list,attribute_list,0)

# print all nodes created by TDIDT
for node in node_list:
    print(node)

# classify the test examples and cound how many were corretly classified
correct_classified = 0
wrong_classified = 0
for example in test_set.examples:
    if classify(example,node_list) == example.outcome:
        correct_classified += 1
    else:
        wrong_classified += 1

# print the success rate
print("Success rate: {:.2%}".format(correct_classified/float(len(test_set.examples))))
