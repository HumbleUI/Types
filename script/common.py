#! /usr/bin/env python3
import build_utils, functools, os, pathlib, platform, subprocess, urllib.request

basedir = os.path.abspath(os.path.dirname(__file__) + '/..')

version = build_utils.get_arg("version") or build_utils.parse_ref(build_utils.get_arg("ref")) or "0.0.0-SNAPSHOT"

@functools.cache
def deps():
  return [
    build_utils.lombok(),
    build_utils.fetch_maven('org.jetbrains', 'annotations', '23.0.0')
  ]
