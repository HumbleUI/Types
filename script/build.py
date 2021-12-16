#! /usr/bin/env python3
import build_utils, common, glob, os, sys

def main():
  os.chdir(common.basedir)
  build_utils.javac(common.deps(), build_utils.files('java/**/*.java'), 'target/classes')
  return 0

if __name__ == '__main__':
  sys.exit(main())
