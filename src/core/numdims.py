from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


# TODO: consider using a named tuple instead?

class NumDims:

    def __init__(self,
                 x=None,
                 pi=None,
                 d=None,
                 pvt=None,
                 ):

        self.x = x  # plant states
        self.pi = pi  # plant disturbance
        self.d = d  # discrete
        self.pvt = pvt  # pvt
        return
