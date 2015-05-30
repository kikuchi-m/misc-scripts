#!/usr/bin/env python

from __future__ import print_function
import argparse
import fnmatch
import os
import subprocess
import sys


def find_project_file(wd):
  files = os.listdir(wd)
  pro_files = []
  for f in files:
    if fnmatch.fnmatch(f, '*.pro') or fnmatch.fnmatch(f, '*.qproj'):
      pro_files.append(f)
  if len(pro_files) == 0:
    raise IOError('Not found any project file')
  if len(pro_files) > 1:
    raise IOError('Found two or more files which may be project file')
  return pro_files[0]


def build_qtproject(wd, qproj, build_dir, force):
  if qproj is None:
    qproj = os.path.abspath(find_project_file(wd))
  else:
    qproj = os.path.abspath(qproj)

  print('project file:  %s' % qproj)
  print('working dir:   %s' % wd)
  print('build dir:     %s' % os.path.abspath(build_dir))

  build_dir = os.path.abspath(build_dir)
  if not os.path.exists(build_dir):
    if force:
      os.makedirs(build_dir)
    else:
      raise IOError('Not found build directory: %s' % build_dir)

  print('continue to qmake...')
  subprocess.call(['qmake', qproj], cwd=build_dir)

  print('continue to make...')
  subprocess.call(['make'], cwd=build_dir)


def main(argv):
  parser = argparse.ArgumentParser()
  parser.add_argument('-p', '--qproj')
  parser.add_argument('-d', '--build-dir', default='out/Default')
  parser.add_argument('-f', '--force', action='store_true')

  args = parser.parse_args(argv)
  build_qtproject(os.getcwd(), args.qproj, args.build_dir, args.force)
  return 0

if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))
