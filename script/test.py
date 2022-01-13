#! /usr/bin/env python3
import build, build_utils, common, os, subprocess, sys

def main():
  build.main('-clojure')
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
  
if __name__ == '__main__':
  sys.exit(main())
