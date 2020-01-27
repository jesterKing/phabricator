#!/usr/bin/env python3

from typing import List
from pathlib import Path
import json
import subprocess as sp

def set_config_keys():
  configjson_path = Path(".") / "config.json"
  configjson_path = configjson_path.absolute().resolve()
  print(configjson_path)
  configjson = json.loads(configjson_path.read_text())

  phab_workdir = Path(".") / "phabricator"

  conf_keys = [k for k in configjson]

  for k in conf_keys:
    value = json.dumps(configjson[k])
    cmd = ["./bin/config", "set", k, value]
    res = sp.run(cmd, stdout=sp.PIPE, cwd=phab_workdir, encoding="utf-8")
    print(res, res.stdout)


if __name__ == "__main__":
  set_config_keys()
