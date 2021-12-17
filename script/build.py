#! /usr/bin/env python3
import build_utils, common, glob, os, sys

def main():
  os.chdir(common.basedir)
  build_utils.javac(build_utils.files('java/**/*.java'),
                    'target/classes',
                    classpath=common.deps(),
                    modulepath=common.deps(),
                    release='9')
  return 0

if __name__ == '__main__':
  sys.exit(main())
