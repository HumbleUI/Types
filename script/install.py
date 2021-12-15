#! /usr/bin/env python3
import argparse, buildy, common, os, sys, shutil, package

def main() -> int:
  os.chdir(common.basedir)
  jars = package.main()

  repo = os.path.expanduser(f"~/.m2/repository/io/github/humbleui/core/core/{common.version}")
  buildy.copy_newer("target/maven/META-INF/maven/io.github.humbleui.core/core/pom.xml",
                    f"{repo}/core-{common.version}.pom")  
  for jar in jars:
    if buildy.copy_newer(jar, repo + "/" + os.path.basename(jar)):
      print(f"Installed {os.path.basename(jar)}")

  return 0

if __name__ == "__main__":
  sys.exit(main())
