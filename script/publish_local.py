#! /usr/bin/env python3
import argparse, common,os, sys, shutil, package

def main() -> int:
  os.chdir(common.basedir)
  parser = argparse.ArgumentParser()
  parser.add_argument('--version')
  (args, _) = parser.parse_known_args()
  rev = args.version or "0.0.0-SNAPSHOT"

  (outjar, sourcejar, javadocs) = package.package(rev)

  local_repo = os.path.expanduser(f"~/.m2/repository/io/github/humbleui/core/core/{rev}")
  os.makedirs(local_repo, exist_ok=True)
  
  with package.use_pom(rev) as pom:
    with open(os.path.join(local_repo, f"core-{rev}.pom"), "w") as f:
      f.write(pom)

  print(f"Publishing core-{rev}.jar to {local_repo}")  
  shutil.copy(outjar, os.path.join(local_repo, f"core-{rev}.jar"))

  print(f"Publishing core-{rev}-sources.jar to {local_repo}")
  shutil.copy(sourcejar, os.path.join(local_repo, f"core-{rev}-sources.jar"))

  print(f"Publishing core-{rev}-javadoc.jar to {local_repo}")
  shutil.copy(javadocs, os.path.join(local_repo, f"core-{rev}-javadoc.jar"))
  
  return 0

if __name__ == "__main__":
  sys.exit(main())
