#!/usr/bin/env python
# -*- coding: utf-8 -*-

from logging import getLogger,basicConfig
logger = getLogger(__name__)

from functools import wraps

formats="""---
default:
  format: "%(asctime)s%(msecs).03d %(process)d %(thread)x %(levelname).4s;%(module)s(%(lineno)d/%(funcName)s) %(message)s"
  datefmt: "%Y%m%d %H%M%S"
json:
  format: '{ "time": "%(asctime)s.%(msecs).03dZ", "pid": %(process)d, "tid": "%(thread)x", "loglevel": "%(levelname).4s", "module": { "name": "%(module)s", "line": %(lineno)d, "funcname": "%(funcName)s", "msg": "%(message)s" }}'
  datefmt: "%Y/%m/%dT%H:%M:%S"
"""

import sys
import json
import yaml
import inspect
import codecs

class color:
    BLUE = '\033[1;34m'
    BLUEL = '\033[0;34m'
    GREEN = '\033[1;32m'
    GREENL = '\033[0;32m'
    CYAN = '\033[1;36m'
    CYANL = '\033[0;36m'
    RED = '\033[1;31m'
    REDL = '\033[0;31m'
    PURPLE = '\033[1;35m'
    PURPLEL = '\033[0;35m'
    YELLOW = '\033[1;33m'
    BROWN = '\033[0;33m'
    WHITE = '\033[1;37m'
    GRAYL = '\033[0;37m'
    GRAYD = '\033[1;30m'
    BLACK = '\033[0;30m'
    ENDC = '\033[0m'


class Style:
    @classmethod
    def color(self, x, case='default'):
        col = { 'enter':color.GREEN, 'retrn':color.BLUE, 'default':'' }
        return  '{1}{0}{2}'.format(x.__repr__(), col[case], color.ENDC )

    @classmethod
    def plain(self, x, case=None):
        return '{0}'.format(x.__repr__())

    @classmethod
    def pretty(self, x, case=None):
        import pp
        return pp.pprintf(x)

    @classmethod
    def json(self, x, case=None):
        return json.dumps(json_convert(x))
    


def traclog( f, modname, log_style ):
    style = getattr(Style, log_style)
    @wraps(f)
    def _f(*args, **kwargs):
        logger.debug("ENTER:{0}.{1} {2}".format(modname, f.__name__, style(kwargs, 'enter') if kwargs else style(args, 'enter')))
        result = f(*args, **kwargs)
        logger.debug("RETRN:{0}.{1} {2}".format(modname, f.__name__, style(result, 'retrn')))
        return result
    return _f

def dictmerge(old, new):
    return dict([(k,v) for k,v in old.items()+new.items()])

def openstream(stream_name = "sys.stderr"):
    if not stream_name or stream_name == "sys.stderr": return codecs.getwriter('utf_8')(sys.stderr)
    if stream_name == "sys.stdout": return codecs.getwriter('utf_8')(sys.stdout)
    return codecs.open(stream_name, 'a', 'utf_8')

def logging_init(logcfg={'level': 30 }, fmt="default"):
    logcfg_dict = dictmerge(yaml.load(formats)[fmt],logcfg)
    basicConfig(**dictmerge( logcfg_dict, { "stream": openstream() if not 'stream' in logcfg_dict else openstream(logcfg_dict['stream'])} ) )

def isclassmethod( m ):
    return inspect.ismethod(m) and inspect.isclass(m.__self__)

def loggify(obj, objlist_tail, wrapper, log_style):
    target = reduce( getattr,  [obj] + objlist_tail )
    if not inspect.ismodule(target) or inspect.isclass(target):
        target = wrapper(target,target.__name__, log_style)
    else:
        for attr in [ a for (a,b) in inspect.getmembers(target) if inspect.ismethod(b) or inspect.isfunction(b) ]:
            if inspect.ismethod(getattr(target, attr)) : print "ismethod"
            if inspect.isfunction(getattr(target, attr)) : print "isfunction"
            print "target,target.__name__,attr:",target,target.__name__,attr
            setattr(target, attr, wrapper(getattr(target, attr),target.__name__, log_style))

def logconfigure(mlogcfg, get_mainglobs):
    if not ('enabled',True) in mlogcfg.items(): return
    logging_init(mlogcfg['basicconfig'], 'default' if not 'fmt' in mlogcfg else mlogcfg['fmt'])

    if not ('enabled',True) in mlogcfg['patch'].items(): return
    for objlist in mlogcfg['patch']['targets']:
        loggify( get_mainglobs(objlist[0]), objlist[1:], traclog,  mlogcfg['patch']['style'] )

def json_convert(obj):
    if isinstance(obj, (float)):
        return obj
    elif isinstance(obj, ( bool )):
        return obj
    elif isinstance(obj, ( int, long, complex )):
        return obj
    elif isinstance(obj, ( unicode )):
        return obj
    elif isinstance(obj, ( str )):
        return obj
    elif isinstance(obj, ( dict )):
        return dict((k, json_convert(v)) for k, v in obj.items())
    elif isinstance(obj, (list, tuple)):
        return map(json_convert, obj)
    elif isinstance(obj, type(None)):
        return 'None'
    elif hasattr(obj, '__dict__') :
        return dict((k, json_convert(v)) for k, v in obj.__dict__.items())
    else:
        return '"json_convert: cannot decode"'

