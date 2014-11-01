#!/usr/bin/env python

import sys

# Example class 
# corresponds to one line in the input file
class Example:
    def __init__(self,attribute_hash,outcome):
        self.attribute_hash = attribute_hash
        self.outcome = outcome

    def __str__(self):
        return str(self.attribute_hash) + "------------" + str(self.outcome)

def strip_and_split(s):
    s = s.rstrip()
    return [s[0],s[-1]]

def initialize_from_file(filename):
    input_file = open(filename,'r')
    init_line = input_file.readline()
    attributes = map(lambda s : [s[0],s.rstrip()[-1]], init_line.split(','))[0:-1]

    examples = []
    for line in input_file:
        example_list = map(lambda s : s.rstrip() , line.split(','))
        examples.append(Example(example_list[1:-1],example_list[-1] == "yes"))

    return [attributes, examples]


attributes, examples = initialize_from_file(sys.argv[1])

