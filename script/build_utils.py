#! /usr/bin/env python3
import argparse, base64, functools, glob, itertools, json, os, pathlib, platform, re, shutil, subprocess, tempfile, time, urllib.request, zipfile
from typing import List, Tuple

def get_arg(name):
  parser = argparse.ArgumentParser()
  parser.add_argument(f'--{name}')
  (args, _) = parser.parse_known_args()
  return vars(args).get(name)

arch   = get_arg("arch") or {'AMD64': 'x64', 'x86_64': 'x64', 'arm64': 'arm64'}[platform.machine()]
system = get_arg("system") or {'Darwin': 'macos', 'Linux': 'linux', 'Windows': 'windows'}[platform.system()]
classpath_separator = ';' if platform.system() == 'Windows' else ':'
mvn = "mvn.cmd" if platform.system() == "Windows" else "mvn"

def classpath_join(entries):
  return classpath_separator.join(entries)

def parse_ref(ref: str) -> str:
  if ref and (match := re.fullmatch("refs/[^/]+/([^/]+)", ref)):
    return match.group(1)

def makedirs(path):
  os.makedirs(path, exist_ok=True)

def rmdir(path):
  shutil.rmtree(path, ignore_errors=True)

def files(*patterns):
  return sum([glob.glob(pattern, recursive=True) for pattern in patterns], start=[])

def slurp(path):
  if os.path.exists(path):
    with open(path, 'r') as f:
      return f.read()

def copy_replace(src, dst, replacements):
  original = slurp(src)
  updated = original
  for key, value in replacements.items():
    updated = updated.replace(key, value)
  makedirs(os.path.dirname(dst))
  if updated != slurp(dst):
    print("Writing", dst)
    with open(dst, 'w') as f:
      f.write(updated)

def copy_newer(src, dst):
  if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst):
    if os.path.exists(dst):
      os.remove(dst)
    shutil.copy2(src, dst)
    return True

def has_newer(sources, targets):
  mtime = time.time()
  for target in targets:
    if os.path.exists(target):
      mtime = min(mtime, os.path.getmtime(target))
    else:
      mtime = 0
  for path in sources:
    if os.path.getmtime(path) > mtime:
      return True
  return False

def fetch(url, file):
  if not os.path.exists(file):
    print('Downloading', url)
    if os.path.dirname(file):
      makedirs(os.path.dirname(file))
    with open(file, 'wb') as f:
      f.write(urllib.request.urlopen(url).read())

def fetch_maven(group, name, version, classifier=None, repo='https://repo1.maven.org/maven2'):
  path = '/'.join([group.replace('.', '/'), name, version, name + '-' + version + ('-' + classifier if classifier else '') + '.jar'])
  file = os.path.join(os.path.expanduser('~'), '.m2', 'repository', path)
  fetch(repo + '/' + path, file)
  return file

def javac(classpath, sources, target, release='11', opts=[]):
  makedirs(target)
  classes = {path.stem: path.stat().st_mtime for path in pathlib.Path(target).rglob('*.class') if '$' not in path.stem}
  newer = lambda path: path.stem not in classes or path.stat().st_mtime > classes.get(path.stem)
  new_sources = [path for path in sources if newer(pathlib.Path(path))]
  if new_sources:
    print('Compiling', len(new_sources), 'java files to', target + ':', new_sources)
    subprocess.check_call([
      'javac',
      '-encoding', 'UTF8',
      *opts,
      '--release', release,
      '--class-path', classpath_join(classpath + [target]),
      '-d', target,
      *new_sources])

def jar(target: str, *content: List[Tuple[str, str]]) -> str:
  if has_newer(files(*[dir + "/" + subdir + "/**" for (dir, subdir) in content]), [target]):
    print(f"Packaging {os.path.basename(target)}")
    makedirs(os.path.dirname(target))
    subprocess.check_call(["jar",
      "--create",
      "--file", target] + sum([["-C", dir, file] for (dir, file) in content], start=[]))
    return target
  return target

@functools.cache
def lombok():
  return fetch_maven('org.projectlombok', 'lombok', '1.18.22')

def delombok(classpath: str, dirs: List[str], target: str):
  sources = files(*[dir + "/**/*.java" for dir in dirs])
  if has_newer(sources, files(target + "/**")):
    print("Delomboking", *dirs, "to", target)
    subprocess.check_call(["java",
      "-jar", lombok(),
      "delombok",
      *dirs,
      "--classpath", classpath_join(classpath),
      "-d", target
    ])

def javadoc(classpath: str, dirs: List[str], target: str):
  sources = files(*[dir + "/**/*.java" for dir in dirs])
  if has_newer(sources, files(target + "/**")):
    print("Generating JavaDoc", *dirs, "to", target)
    subprocess.check_call(["javadoc",
      "--class-path", classpath_join(classpath),
      "-d", target,
      "-quiet",
      "-Xdoclint:all,-missing",
      *sources])

def deploy(jar,
           tempdir = tempfile.gettempdir(),
           classifier = None,
           ossrh_username = os.getenv('OSSRH_USERNAME'),
           ossrh_password = os.getenv('OSSRH_PASSWORD'),
           repo="https://s01.oss.sonatype.org/service/local/staging"):
  makedirs(tempdir)
  settings = tempdir + "/settings.xml"
  with open(settings, 'w') as f:
    f.write("""
      <settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0
                                http://maven.apache.org/xsd/settings-1.0.0.xsd">
          <servers>
              <server>
                  <id>ossrh</id>
                  <username>${ossrh.username}</username>
                  <password>${ossrh.password}</password>
              </server>
          </servers>
      </settings>
    """)

  mvn_settings = [
    '--settings', settings,
    '-Dossrh.username=' + ossrh_username,
    '-Dossrh.password=' + ossrh_password,
    '-Durl=' + repo + "/deploy/maven2/",
    '-DrepositoryId=ossrh'
  ]

  with zipfile.ZipFile(jar, 'r') as f:
    pom = [path for path in f.namelist() if re.fullmatch(r"META-INF/maven/.*/pom\.xml", path)][0]
    f.extract(pom, tempdir)

  classifier = classifier or (re.fullmatch(r".*-\d+\.\d+\.\d+(?:-SNAPSHOT)?(?:-([a-z0-9\-]+))?\.jar", os.path.basename(jar))[1])

  print(f'Deploying {jar}', classifier, pom)
  subprocess.check_call(
    [mvn, 'gpg:sign-and-deploy-file'] + \
    mvn_settings + \
    [f'-DpomFile={tempdir}/{pom}',
     f'-Dfile={jar}']
    + ([f"-Dclassifier={classifier}"] if classifier else []))

def release(ossrh_username = os.getenv('OSSRH_USERNAME'),
            ossrh_password = os.getenv('OSSRH_PASSWORD'),
            repo="https://s01.oss.sonatype.org/service/local/staging"):
  headers = {
    'Accept': 'application/json',
    'Authorization': 'Basic ' + base64.b64encode((ossrh_username + ":" + ossrh_password).encode('utf-8')).decode('utf-8'),
    'Content-Type': 'application/json',
  }

  def fetch(path, data = None):
    req = urllib.request.Request(repo + path,
                                 headers=headers,
                                 data = json.dumps(data).encode('utf-8') if data else None)
    resp = urllib.request.urlopen(req).read().decode('utf-8')
    print(' ', path, "->", resp)
    return json.loads(resp) if resp else None

  print('Finding staging repo')
  resp = fetch('/profile_repositories')
  repo_id = resp['data'][0]["repositoryId"]
  
  print('Closing repo', repo_id)
  resp = fetch('/bulk/close', data = {"data": {"description": "", "stagedRepositoryIds": [repo_id]}})

  while True:
    print('Checking repo', repo_id, 'status')
    resp = fetch('/repository/' + repo_id + '/activity')
    close_events = [e for e in resp if e['name'] == 'close']
    close_events = close_events[0]['events'] if close_events else []
    fail_events = [e for e in close_events if e['name'] == 'ruleFailed']
    if fail_events:
      print(fail_events)
      return 1

    if close_events and close_events[-1]['name'] == 'repositoryClosed':
      break

    time.sleep(0.5)

  print('Releasing staging repo', repo_id)
  resp = fetch('/bulk/promote', data = {"data": {
              "autoDropAfterRelease": True,
              "description": "",
              "stagedRepositoryIds":[repo_id]
        }})
  print('Success! Just released', repo_id)