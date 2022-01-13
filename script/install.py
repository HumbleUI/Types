#! /usr/bin/env python3
import argparse, build_utils, common, os, sys, shutil, package

def main(classifier: str = '') -> int:
  jars = package.main(classifier)
  os.chdir(common.basedir)

  repo = os.path.expanduser(f"~/.m2/repository/io/github/humbleui/types/{common.version}")
  build_utils.copy_newer(f"target/maven/META-INF/maven/io.github.humbleui/types/pom.xml",
                         f"{repo}/types-{common.version}.pom")
  for jar in jars:
    if build_utils.copy_newer(jar, repo + "/" + os.path.basename(jar)):
      print(f"Installed {os.path.basename(jar)}")

  return 0

if __name__ == "__main__":
  main('')
  main('-clojure')
  sys.exit(0)
