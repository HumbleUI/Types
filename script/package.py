#! /usr/bin/env python3
import argparse, build, buildy, common, glob, os, re, subprocess, sys
from typing import List, Tuple

def main() -> Tuple[str, str, str]:
  build.main()

  os.chdir(common.basedir)

  buildy.copy_replace(
    "deploy/META-INF/maven/io.github.humbleui.core/core/pom.xml",
    "target/maven/META-INF/maven/io.github.humbleui.core/core/pom.xml",
    {"${version}": common.version}
  )

  buildy.copy_replace(
    "deploy/META-INF/maven/io.github.humbleui.core/core/pom.properties",
    "target/maven/META-INF/maven/io.github.humbleui.core/core/pom.properties",
    {"${version}": common.version}
  )
  
  jar = buildy.jar(f"target/core-{common.version}.jar", ("target/classes", "."), ("target/maven", "META-INF"))

  buildy.delombok(common.deps(), ["java"], "target/delomboked/io/github/humbleui/core")
  sources = buildy.jar(f"target/core-{common.version}-sources.jar", ("target/delomboked", "."), ("target/maven", "META-INF"))

  buildy.javadoc(common.deps(), ["target/delomboked"], "docs/apidocs")
  javadoc = buildy.jar(f"target/core-{common.version}-javadoc.jar", ("docs/apidocs", "."))

  return (jar, sources, javadoc)

if __name__ == "__main__":
  main()
  sys.exit(0)
