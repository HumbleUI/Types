#! /usr/bin/env python3
import argparse, build_utils, common, os, sys, shutil, package

def main(classifier: str = '') -> int:
  jars = package.main(classifier)
  os.chdir(common.basedir)

  for jar in jars:
    build_utils.deploy(jar, tempdir = f"target/deploy{classifier}")

if __name__ == "__main__":
  main('')
  main('-clojure')
  sys.exit(build_utils.release())
