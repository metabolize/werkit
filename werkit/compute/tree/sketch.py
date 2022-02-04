"""
References:

https://github.com/ivankorobkov/python-inject
https://github.com/illuin-tech/opyoid
https://github.com/ets-labs/python-dependency-injector
"""
 

class MyComputeProcess:
    a = Input(_type="number")
    b = Input(_type="number")

    @intermediate(_type="number")
    def i(self, a):
        return a

    @intermediate(_type="number")
    def j(self, b):
        return b

    @output(_type="number")
    def r(self, i, j):
        return i + j
