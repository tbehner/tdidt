#!/usr/bin/env python3

import sys
import random
import math
import copy

# Example class 
# corresponds to one line in the input file
class Example:
    def __init__(self,attribute_hash,outcome):
        self.attribute_hash = attribute_hash
        self.outcome = outcome

    def __str__(self):
        return str(self.attribute_hash) + "------------" + str(self.outcome)

def get_information_gain(ppos, pneg, npos, nneg):
    total = float(ppos + pneg + npos + nneg)
    p_total = float(ppos + pneg)
    n_total = float(npos + nneg)
    information_gain = entropy((ppos+npos)/total,(pneg + nneg)/total)
    information_gain -= p_total/total * entropy(ppos/p_total,pneg/p_total)
    information_gain -= n_total/total * entropy(npos/n_total,nneg/n_total)
    return information_gain

def entropy(p,n):
    if n == 0:
        return p*math.log2(1.0/p)
    elif p == 0:
        return n*math.log2(1.0/n)
    return p*math.log2(1.0/p) + n*math.log2(1.0/n)

# ExampleSet class
# contains all examples and attributes
class ExampleSet:
    def __init__(self,examples = []):
        self.examples = []

    def initialize_from_file(self,filename):
        input_file = open(filename,'r')

        # read the first line with attributes 
        init_line = input_file.readline()
        #  and parse this line into attribute name and type
        # FIXME this line should be easier to code, right?
        self.attributes = { x[0] : x[1] for x in list(map(lambda s : [s[0],s.rstrip()[-1]], init_line.split(',')))[0:-1]}
        print(self.attributes)

        # parse the rest of the file containing the examples
        self.examples = []
        self.positives = 0
        self.negatives = 0
        for line in input_file:
            example_list = list(map(lambda s : s.rstrip() , line.split(',')))
            # FIXME IOOUUUUU there has to be a way which is prettier than this
            example_hash = dict(zip(sorted(self.attributes),example_list))
            for key in example_hash.keys(): # convert all numerical values from str to float
                if self.attributes[key] == 'n':
                    example_hash[key] = float(example_hash[key])
            self.examples.append(Example(example_hash,example_list[-1] == "yes"))
            if example_list[-1] =="yes":
                self.positives += 1
            else:
                self.negatives += 1

        self.entropy = entropy(float(self.positives)/len(self.examples), float(self.negatives)/len(self.examples))

    def best_split(self,attribute):
        max_information_gain = None
        splitting_test = None
        passing_examples = [0,0]
        failing_examples = [self.positives,self.negatives]

        if self.attributes[attribute] == 'n': # find the best split for numerical attributes

            # sort the examples according to the values of the attribute
            self.examples.sort(key=lambda e : e.attribute_hash[attribute])
            for i_idx in range(len(self.examples)-1):
                if self.examples[i_idx].outcome == self.examples[i_idx+1].outcome:              # update distribution of outcomes
                    if self.examples[i_idx].outcome:
                        failing_examples[0] -= 1
                        passing_examples[0] += 1
                    else:
                        failing_examples[1] -= 1
                        passing_examples[1] += 1
                else:
                    # information gain
# FIXME hierfür habe ich jetzt auch eine Funktion -> das geht schöner
                    total_passing = float(passing_examples[0] + passing_examples[1])
                    total_failing = float(failing_examples[0] + failing_examples[1])
                    current_entropy = self.entropy 
                    current_entropy -= total_passing/len(self.examples)*entropy(passing_examples[0]/total_passing,passing_examples[1]/total_passing)
                    current_entropy -= total_failing/len(self.examples)*entropy(failing_examples[0]/total_failing,failing_examples[1]/total_failing)

                    if max_information_gain is None or max_information_gain < current_entropy:
                        max_information_gain = current_entropy
                        mean = (self.examples[i_idx].attribute_hash[attribute] + self.examples[i_idx+1].attribute_hash[attribute])/2
                        # FIXME if the code should brake, I should consider this line as the problem
                        splitting_test = lambda x : x < mean

        elif self.attributes[attribute] == 'c': # find the best split for categorical attributes
            # compute information gain for every single value of the attribute 
            histograms = {}                 # histogram for each value of the attribute
            information_gain = {}           # information gain for each value of the attribute
            # compute the histograms
            for example in self.examples:   
                value = example.attribute_hash[attribute]
                if value in histograms.keys():
                    if example.outcome:
                        histograms[value][0] += 1
                    else:
                        histograms[value][1] += 1
                else:
                    histograms[value] = [0,0]

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
                    s.append(value)

            max_information_gain = previous_gain
            splitting_test = lambda x : x in s

        return [max_information_gain,splitting_test]
        

    # returns a part of the examples in an independend ExampleSet for evaluation of a decision tree
    def get_test_instances(self,quantity):
        random.seed()
        
        test_examples = ExampleSet()
        for i in range(quantity):
            rand = random.randint(0,len(self.examples)-1)
            test_examples.examples.append(self.examples.pop(rand))

        return test_examples
# END class ExampleSet         

test = ExampleSet()
test.initialize_from_file(sys.argv[1])
print(test.best_split("b"))
