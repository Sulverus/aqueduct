#encoding: utf8
import sys
import os

path = os.path.dirname(sys.modules[__name__].__file__)
path = os.path.join(path, '..')
sys.path.insert(0, path)

#just for testing locally
# $python aqueduct
from aqueduct import server
server.main()