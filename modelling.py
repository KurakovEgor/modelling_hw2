#!/usr/bin/env python3

import logicmin
import copy
import numpy as np
import math
from functools import reduce

def bug_with(argument = -1):
    def real_decorator(function):
        def wrapper(*args, **kwargs):
            if argument == 1:
                return 1
            elif argument == 0:
                return 0
            else:
                return function(*args)
        return wrapper
    return real_decorator

class Element:
    def __init__(self, name, function=None, signals=None):
        self.name = name
        self.function = function
        self.signals = signals
        self.modification = {}
        self.modification[None] = function

    def add_modification(self, name, function):
        self.modification[name] = function

    def use_modification(self, name=None):
        self.function = self.modification[name]

class InputElement(Element):
    def set_signal(self, signal):
        self.signal = signal

    def result(self):
        return self.signal

class ComplexElement(Element):
    def result(self):
        args = []
        for i in self.signals:
            args.append(i.result())
        return self.function(args)


class Schema:
    def __init__(self, inputs):
        self.elements = {}
        self.reserve_elements = {}
        self.input_signals = list(reversed(inputs))
        self.input_state = 0
        for i in inputs:
            self.elements[i] = InputElement(i)
            self.elements[i].set_signal(0)

    def add_element(self, name, input_signals, function):
        for i in input_signals:
            if not self.is_signal_exist(i):
                raise Exception
        element = ComplexElement(name, function, list(map(lambda sym : self.elements[sym], input_signals)))
        self.elements[name] = element
        self.exit = name
    
    def is_signal_exist(self, sym):
        return sym in self.elements

    def set_input_state(self, num):
        for bit, sym in enumerate(self.input_signals):
            self.elements[sym].set_signal((num >> bit) % 2)
        self.input_state = num

    def next_input_state(self):
        self.input_state = (self.input_state + 1) % (2 ** len(self.input_signals))
        self.set_input_state(self.input_state)
    
    def constant_bug(self, sym, const):
        if sym in self.reserve_elements:
            self.recover_element(sym)
        if not const in self.elements[sym].modification:
            self.elements[sym].add_modification(const, bug_with(const)(self.elements[sym].function))
        self.elements[sym].use_modification(const)

    def recover_element(self, sym):
        self.elements[sym].use_modification()

    def calculate(self):
        for i in self.input_signals:
            self.elements[self.exit]
        return self.elements[self.exit].result()

    def calculate_all(self):
        result = []
        self.set_input_state(0)
        for i in range(2 ** len(self.input_signals)):
            result.append(self.calculate())
            self.next_input_state()
        return(result)

    def check_all_constant(self):
        results = []
        results.append((self.exit, self.calculate_all()))
        for name in self.elements:
            if name in self.input_signals:
                continue
            self.constant_bug(name, 0)
            results.append((name+"0",self.calculate_all()))
            self.constant_bug(name, 1)
            results.append((name+"1",self.calculate_all()))
            self.recover_element(name)
        return results
            
def output_format(results):
    header = ["N"] + list(map(lambda x: x[0],results))
    arr = []
    for i in range(0,len(results[0][1])):
        arr.append([])
        arr[i].append(i)
    for tup in results:
        for state_num, result in enumerate(tup[1]):
            arr[state_num].append(result)
            
    return (header, arr)

def get_formulas(header, arr):
    num_of_inputs = int(math.log(len(arr),2))
    t = logicmin.TT(num_of_inputs, len(arr[0]) - 1)
    for i in range(len(arr)):
        bin_state = bin(arr[i][0])[2:]
        bin_state = bin_state if len(bin_state) == num_of_inputs else "0" * (num_of_inputs-len(bin_state)) + bin_state
        t.add(bin_state,reduce(lambda x, y: str(x)+str(y), arr[i][1:]))
    sols = t.solve()
    print(sols.printN(xnames=[chr(i) for i in range(ord('a'), ord('a') + num_of_inputs)],ynames=headers[1:]))

def print_table(header, table):
    header_str = ("{:>4} " * len(header))
    header_str = header_str.format(*header)
    print(header_str)
    for i in table:
        current_str = ("{:>4} " * len(i))
        current_str = current_str.format(*i)
        print(current_str)

def print_equivalents(headers, arr):
    values = {}
    for i in headers[1:]:
        values[i] = ""
    for i in range(len(arr)):
        for j in range(1,len(arr[i])):
            values[headers[j]] += str(arr[i][j])
    correct = values[headers[1]]
    classes = {}
    for key, value in values.items():
        if key == headers[1]:
            continue
        if value in classes:
            classes[value].append(key)
        else:
            classes[value] = [key]
    if len(classes[correct]) > 0:
        print("Избыточные неисправности:", *classes[correct])
    for k, v in classes.items():
        if k != correct and len(v) > 1:
            print("Класс эквивалентности:", *v)
            tests = []
            for i in range(len(k)):
                if correct[i] != k[i]:
                    bin_state = bin(i)[2:]
                    bin_state = bin_state if len(bin_state) == math.log(len(correct),2) else "0" * (math.log(len(correct),2)-len(bin_state)) + bin_state
                    tests.append(bin_state)
            print("Тестовые наборы: ", *tests)

land = lambda args: int(reduce(lambda x, y: x and y, args))
lnot = lambda args: int(not args[0])
lyes = lambda args: int(args[0])
lor = lambda args: int(reduce(lambda x, y: x or y, args))
lnand = lambda args: int(not reduce(lambda x, y: x and y, args))

schema = Schema(['a','b','c','d','e'])
schema.add_element('q',['b','d'],land)
schema.add_element('g',['c','d'],lnand)
schema.add_element('k',['a','q'],land)
schema.add_element('l',['q','g'],lnand)
schema.add_element('m',['k','g'],lnand)
schema.add_element('n',['l','e'],land)
schema.add_element('p',['k','n'],land)
schema.add_element('z',['m','p'],lor)

results = schema.check_all_constant()
headers, arr = output_format(results)
print_table(headers, arr)
print_equivalents(headers, arr)
get_formulas(headers,arr)
