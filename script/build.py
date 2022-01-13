#! /usr/bin/env python3
import build_utils, common, glob, os, subprocess, sys

def test():
  classpath = [
    *common.deps('-clojure'),
    "target/classes-clojure",
    "test-clojure",
  ]
  subprocess.check_call(["java",
    "--class-path", build_utils.classpath_join(classpath),
    "clojure.main",
    "-m", "io.github.humbleui.test"])
  return 0

def main(classifier=''):
  os.chdir(common.basedir)
  build_utils.javac(build_utils.files(f'java{classifier}/**/*.java'),
                    f'target/classes{classifier}',
                    classpath=common.deps(classifier),
                    modulepath=common.deps(classifier),
                    release='9')
  if '-clojure' == classifier:
    test()
  return 0

if __name__ == '__main__':
  main('')
  main('-clojure')
  sys.exit(0)
