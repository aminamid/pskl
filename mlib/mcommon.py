import itertools

def concat( lsts ):
    return list(itertools.chain(*lsts))

def concat_dicts( dicts ):
    return dict( concat([ d.items() for d in dicts ]) )

from datetime import datetime as dt

def datetimestr():
    return dt.now().strftime("%Y%m%d%H%M%S")

import inspect
def usage(cls):
    rslt = {}
    for k,v in [(k,inspect.getargspec(v).args) for k,v in inspect.getmembers(cls, inspect.ismethod)]:
        rslt[k] = v[1:]
    for k,v in [(k,inspect.getargspec(v).args) for k,v in inspect.getmembers(cls, inspect.isfunction)]:
        rslt[k] = v
    return rslt

def argspec(cls):
    rslt = {}
    for k,v in [(k,inspect.getargspec(v)) for k,v in inspect.getmembers(cls, lambda x: inspect.ismethod(x) or inspect.isfunction(x))]:
        rslt[k] = v
    return rslt

