import sys
import json
import yaml
from mlib import mcmd,mlog,mcommon

import pp

defaultcfg="""---
mlog:
  enabled: true
  basicconfig:
    level: 10
    stream: sys.stderr
  fmt: default  # default | json
  patch:
    enabled: true
    style: pretty # plain | color | pretty | json
    targets:
    - ["mo['domgr']"]
    - [Subcmd, new_groups]
classes:
- - domgr
  - dopy.manager.DoManager
  - client_id: None
    api_key: apikey
    api_version: 2
"""


def main(cfg):
    mo = mcmd.DynamicLoad(cfg['classes'])
    print yaml.dump(mcommon.usage(mo.obj['domgr']))

if __name__ == "__main__":

    cfg = mcmd.get_cfgdict( [ defaultcfg , mcmd.maybe_cfgfile(__file__, "cfg") ] + sys.argv[1:])
    main(cfg)
