#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import update_wrapper


def disable():
    '''
    Disable a decorator by re-assigning the decorator's name
    to this function. For example, to turn off memoization:

    >>> memo = disable

    '''
    return


def decorator(func):
    '''
    Decorate a decorator so that it inherits the docstrings
    and stuff from the function it's decorating.
    '''
    def wrapper(*args):
        return func(*args)
    update_wrapper(wrapper, func)
    return wrapper


@decorator
def countcalls(func):
    '''Decorator that counts calls made to the function decorated.'''
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)
    wrapper.calls = 0
    return wrapper


@decorator
def memo(func):
    '''
    Memoize a function so that it caches all return values for
    faster future lookups.
    '''
    cache_calls = {}

    def wrapper(*args):
        result_key = tuple(args)
        if result_key not in cache_calls:
            result = func(*args)
            cache_calls[result_key] = result
            update_wrapper(wrapper, func)
            return result
        else:
            return cache_calls[result_key]

    return wrapper


def n_ary(func):
    '''
    Given binary function f(x, y), return an n_ary function such
    that f(x, y, z) = f(x, f(y,z)), etc. Also allow f(x) = x.
    '''
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs) if len(args) <= 2 else func(args[0], wrapper(*args[1:]))
    return wrapper


def trace(pattern):
    '''Trace calls made to function decorated.

    @trace("____")
    def fib(n):
        ....

    >>> fib(3)
     --> fib(3)
    ____ --> fib(2)
    ________ --> fib(1)
    ________ <-- fib(1) == 1
    ________ --> fib(0)
    ________ <-- fib(0) == 1
    ____ <-- fib(2) == 2
    ____ --> fib(1)
    ____ <-- fib(1) == 1
     <-- fib(3) == 3

    '''

    @decorator
    def wrapper(func):
        def traced(*args):
            prefix = pattern * wrapper.depth
            arg_str = ", ".join(str(a) for a in args)
            print("{} --> {}({})".format(prefix, func.__name__, arg_str))
            wrapper.depth += 1
            result = func(*args)
            print("{} <-- {}({}) == {}".format(prefix, func.__name__, arg_str, result))
            wrapper.depth -= 1
            return result
        wrapper.depth = 0
        return traced
    return wrapper


@memo
@countcalls
@n_ary
def foo(a, b):
    return a + b


@countcalls
@memo
@n_ary
def bar(a, b):
    return a * b


@countcalls
@trace("####")
@memo
def fib(n):
    """Some doc"""
    return 1 if n <= 1 else fib(n-1) + fib(n-2)


def main():
    print(foo(4, 3))
    print(foo(4, 3, 2))
    print(foo(4, 3))
    print("foo was called", foo.calls, "times")

    print(bar(4, 3))
    print(bar(4, 3, 2))
    print(bar(4, 3, 2, 1))
    print("bar was called", bar.calls, "times")

    print(fib.__doc__)
    fib(3)
    print(fib.calls, 'calls made')


if __name__ == '__main__':
    main()
