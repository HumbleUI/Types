#! /usr/bin/env python3
import argparse, build, build_utils, common, glob, os, re, subprocess, sys
from typing import List, Tuple

def main(classifier: str = '') -> Tuple[str, str, str]:
  build.main(classifier)

  os.chdir(common.basedir)
  
  build_utils.copy_replace(
    f"deploy/META-INF/maven/io.github.humbleui/types/pom.xml",
    f"target/maven/META-INF/maven/io.github.humbleui/types/pom.xml",
    {"${version}": common.version})

  build_utils.copy_replace(
    f"deploy/META-INF/maven/io.github.humbleui/types/pom.properties",
    f"target/maven/META-INF/maven/io.github.humbleui/types/pom.properties",
    {"${version}": common.version})
  
  jar = build_utils.jar(f"target/types-{common.version}{classifier}.jar",
    (f"target/classes{classifier}", "."),
    (f"target/maven", "META-INF"))

  build_utils.delombok([f"java{classifier}"],
    f"target/delomboked{classifier}/io/github/humbleui/types",
    modulepath=common.deps(classifier))
  sources = build_utils.jar(f"target/types-{common.version}{classifier}-sources.jar",
    (f"target/delomboked{classifier}", "."),
    (f"target/maven", "META-INF"))

  build_utils.javadoc([f"target/delomboked{classifier}"],
    f"target/apidocs{classifier}",
    modulepath=common.deps(classifier))
  javadoc = build_utils.jar(f"target/types-{common.version}{classifier}-javadoc.jar",
    (f"target/apidocs{classifier}", "."),
    (f"target/maven", "META-INF"))

  return (jar, sources, javadoc)

if __name__ == "__main__":
  main('')
  main('-clojure')
  sys.exit(0)
