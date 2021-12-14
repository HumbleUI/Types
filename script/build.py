#! /usr/bin/env python3
import common, glob, os, sys

def main():
  os.chdir(common.basedir)
  sources = glob.glob('java/**/*.java', recursive=True)
  common.javac(common.deps(), sources, 'target/classes')
  return 0  

if __name__ == '__main__':
  sys.exit(main())
