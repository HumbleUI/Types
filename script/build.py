#! /usr/bin/env python3
import build_utils, common, glob, os, sys

def main(classifier=''):
  os.chdir(common.basedir)
  build_utils.javac(build_utils.files(f'java{classifier}/**/*.java'),
                    f'target/classes{classifier}',
                    classpath=common.deps(classifier),
                    modulepath=common.deps(classifier),
                    release='9')
  return 0

if __name__ == '__main__':
  main('')
  main('-clojure')
  sys.exit(0)
