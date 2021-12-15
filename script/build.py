#! /usr/bin/env python3
import buildy, common, glob, os, sys

def main():
  os.chdir(common.basedir)
  buildy.javac(common.deps(), buildy.files('java/**/*.java'), 'target/classes')
  return 0

if __name__ == '__main__':
  sys.exit(main())
