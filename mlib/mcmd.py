#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import yaml
import codecs
from functools import wraps

from mlib.mcommon import concat_dicts

# trace
# mlog.logconfigure(yaml.load('{enabled: true, basicconfig: {level: 10}, patch: {enabled: true, style: color, targets: [[mcmd]] } }'), lambda x: globals()[x])

class CfgMustBeDict(Exception):
    def __init__(self, text):
        self._text = text
    def __str__(self):
        return 'Configuration element must be dict: {0} \n {0} may configure as filename. But not exists'.format(self._text)


def parse( st ):
    if not st: return None
    if str_to_dict(_try_open( st )): return str_to_dict(_try_open( st ))
    if _try_json(st): return _try_json(st)
    if _try_yaml(st): return _try_yaml(st)
    return None

def str_to_dict( st ):
    if _try_json(st): return _try_json(st)
    if _try_yaml(st): return _try_yaml(st)
    return None

def _try_yaml( st ):
    if not isinstance(st, basestring): return None
    try:
        rslt = yaml.load(st)
        if isinstance(rslt, (dict)):
            return rslt
        else:
            raise CfgMustBeDict(st)
    except yaml.scanner.ScannerError as e:
        return None
    return None

def _try_json( st ):
    if not isinstance(st, basestring): return None
    try:
        rslt = json.loads(st)
        if isinstance(rslt, (dict)):
            return rslt
        else:
            raise CfgMustBeDict(st)
    except (TypeError, ValueError) as e:
        return None
    return None

def _try_open( st ):
    if not isinstance(st, basestring): return None
    try:
        return codecs.open(st,'r', 'utf_8').read()
    except (TypeError, IOError) as e:
        return None

def _convert_to_dicts( cfg_list ):
    return map(parse, cfg_list)

def get_cfgdict( cfg_list ):
    return concat_dicts([ x for x in _convert_to_dicts( cfg_list ) if x ] )

def put_dict(st, status, encode):
    try:
        codecs.open(st, 'w', 'utf_8').write(encode(status))
    except IOError as e:
        return None

def store_lastfunc( f, fname=None ):
    fname = f.__name__ if not fname else fname
    @wraps(f)
    def _f(*args, **kwargs):
        put_dict( 'tmp/{0}.args.dump'.format(fname), kwargs if kwargs else args, json.dumps )
        result = f(*args, **kwargs)
        put_dict( 'tmp/{0}.rslt.dump'.format(fname), result, json.dumps )
        return result
    return _f

def chgext(filename,ext):
    return '{0}.{1}'.format(os.path.splitext(filename)[0],ext)

def real_filepath(filepath):
    return filepath if os.path.exists(filepath) else None

def maybe_cfgfile(filename, ext):
    return real_filepath(chgext(filename,ext))


class DynamicLoad(object):
  def __init__(self, pathes=[]):
      print [(n,t,c) for n,t,c in pathes]
      self.kls = dict([ (name, self._get_kls_tuple( name, target.split('.'), cfg)) for (name, target, cfg) in pathes ])
      print dict([ (t[0], t[1] ) for t in self.kls.items()])
      self.obj = dict([ (t[0],t[1][0](**t[1][1]) ) for t in self.kls.items()])

  def _get_kls_tuple(self,name, target, cfg):
      return (getattr(__import__('.'.join(target[:-1]), fromlist=[target[0]]),target[-1]), cfg)

  def post(self,target):
      self.obj.update( dict([_get_kls_tuple(target)]))

