#! /usr/bin/env python3
import argparse, build, build_utils, common, glob, os, re, subprocess, sys
from typing import List, Tuple

def main() -> Tuple[str, str, str]:
  build.main()

  os.chdir(common.basedir)

  build_utils.copy_replace(
    "deploy/META-INF/maven/io.github.humbleui.core/core/pom.xml",
    "target/maven/META-INF/maven/io.github.humbleui.core/core/pom.xml",
    {"${version}": common.version}
  )

  build_utils.copy_replace(
    "deploy/META-INF/maven/io.github.humbleui.core/core/pom.properties",
    "target/maven/META-INF/maven/io.github.humbleui.core/core/pom.properties",
    {"${version}": common.version}
  )
  
  jar = build_utils.jar(f"target/core-{common.version}.jar", ("target/classes", "."), ("target/maven", "META-INF"))

  build_utils.delombok(common.deps(), ["java"], "target/delomboked/io/github/humbleui/core")
  sources = build_utils.jar(f"target/core-{common.version}-sources.jar", ("target/delomboked", "."), ("target/maven", "META-INF"))

  build_utils.javadoc(common.deps(), ["target/delomboked"], "docs/apidocs")
  javadoc = build_utils.jar(f"target/core-{common.version}-javadoc.jar", ("docs/apidocs", "."), ("target/maven", "META-INF"))

  return (jar, sources, javadoc)

if __name__ == "__main__":
  main()
  sys.exit(0)
