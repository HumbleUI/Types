#! /usr/bin/env python3
import buildy, functools, os, pathlib, platform, subprocess, urllib.request

basedir = os.path.abspath(os.path.dirname(__file__) + '/..')

version = buildy.get_arg("version") or buildy.parse_ref(buildy.get_arg("ref")) or "0.0.0-SNAPSHOT"

@functools.cache
def deps():
  return [buildy.lombok(), buildy.fetch_maven('org.jetbrains', 'annotations', '23.0.0')]
