#! /usr/bin/env python3
import buildy, common, os, sys

def main():
  os.chdir(common.basedir)
  buildy.rmdir("target")
  buildy.rmdir("docs/apidocs")
  return 0

if __name__ == '__main__':
  sys.exit(main())