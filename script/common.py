#! /usr/bin/env python3
import build_utils, functools, os, pathlib, platform, subprocess, urllib.request

basedir = os.path.abspath(os.path.dirname(__file__) + '/..')

version = build_utils.get_arg("version") or build_utils.parse_ref() or build_utils.parse_sha() or "0.0.0-SNAPSHOT"

@functools.lru_cache(maxsize=1)
def deps_java():
  return [
    build_utils.lombok(),
    build_utils.fetch_maven('org.jetbrains', 'annotations', '20.1.0')
  ]

@functools.lru_cache(maxsize=1)
def deps_clojure():
  return deps() + [
    build_utils.fetch_maven("org.clojure", "clojure", "1.11.0"),
    build_utils.fetch_maven("org.clojure", "core.specs.alpha", "0.2.62"),
    build_utils.fetch_maven("org.clojure", "spec.alpha", "0.3.218"),
  ]

def deps(classifier=''):
  if classifier == '':
    return deps_java()
  elif classifier == '-clojure':
    return deps_clojure()
