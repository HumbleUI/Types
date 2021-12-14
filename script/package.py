#! /usr/bin/env python3
import argparse, common, glob, os, re, subprocess, sys
from typing import List, Tuple
from contextlib import contextmanager 

def parse_version() -> str:
  parser = argparse.ArgumentParser()
  parser.add_argument('--ref')
  parser.add_argument('--version')
  (args, _) = parser.parse_known_args()
  if hasattr(args, 'ref') and args.ref is not None:
    return parse_refs(args)
  if hasattr(args, 'version') and args.version is not None:
    return args.version
  return "0.0.0-SNAPSHOT"

def parse_refs(args: object) -> str:
  return re.fullmatch("refs/[^/]+/([^/]+)", args.ref).group(1)

@contextmanager
def use_pom(
  rev: str="0.0.0-SNAPSHOT",
  pom_src: str = os.path.join(common.basedir, "deploy/META-INF/maven/io.github.humbleui.core/core/pom.xml")) -> None:
  with open(pom_src, "r") as f:
    pom = f.read()
    pom = pom.replace("${version}", rev)
    try:
      yield pom
    finally:
      pass

def package_jar(outjar: str,
                classes: str = os.path.join(common.basedir, "target/classes"),
                jarCmdArgs: List[str] = []) -> str:
  assert os.path.isabs(outjar), "outjar must be absolute path"
  print(f"Packaging {os.path.basename(outjar)}")
  targetmaven = os.path.join(common.basedir,"target/maven")
  subprocess.check_call(["jar",
    "--create",
    "--file", outjar,
    "-C", classes, ".",
    "-C", targetmaven, "META-INF"]
    + jarCmdArgs)
  return outjar

def package(rev: str, jarCmdArgs: List[str] = []) -> Tuple[str, str, str]:
  # Update poms
  target = os.path.join(common.basedir, "target/maven/META-INF/maven/io.github.humbleui.core/core")
  with use_pom(rev) as pom:
    os.makedirs(target, exist_ok=True)
    with open(os.path.join(target,"pom.xml"), "w") as f:
      f.write(pom)

  with open("deploy/META-INF/maven/io.github.humbleui.core/core/pom.properties", "r") as f:
    contents = f.read()
    with open("target/maven/META-INF/maven/io.github.humbleui.core/core/pom.properties", "w") as f:
      f.write(contents.replace("${version}", rev))
  
  classes = os.path.join(common.basedir, "target/classes")
  os.makedirs(classes, exist_ok = True)

  # core-*.jar
  outjar = package_jar(os.path.join(common.basedir, f"target/core-{rev}.jar"), classes, jarCmdArgs = jarCmdArgs)

  # core-*-sources.jar
  print(f"Packaging core-{rev}-sources.jar")
  
  lombok = common.deps()[0]
  subprocess.check_call(["java",
    "-jar", lombok,
    "delombok",
    "java",
    "--classpath", common.classpath_separator.join(common.deps()),
    "-d", "target/delomboked/io/github/humbleui/core"
  ])
  sourcejar = os.path.join(common.basedir,f"target/core-{rev}-sources.jar")
  subprocess.check_call(["jar",
    "--create",
    "--file", sourcejar,
    "-C", "target/delomboked", ".",
    "-C", "target/maven", "META-INF"
  ])

  # core-*-javadoc.jar
  print('Packaging core-' + rev + "-javadoc.jar")

  sources = glob.glob("target/delomboked/**/*.java", recursive=True)
  subprocess.check_call(["javadoc",
    "--class-path", common.classpath_separator.join(common.deps()),
    "-d", "docs/apidocs",
    "-quiet",
    "-Xdoclint:all,-missing"]
    + sources)
  javadoc = os.path.join(common.basedir,f"target/core-{rev}-javadoc.jar")
  subprocess.check_call(["jar",
    "--create",
    "--file", javadoc,
    "-C", "docs/apidocs", ".",
  ])

  return (outjar, sourcejar, javadoc)

def main() -> int:
  os.chdir(common.basedir)
  package(parse_version())
  return 0

if __name__ == "__main__":
  sys.exit(main())
