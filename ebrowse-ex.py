#!/usr/bin/env python

from __future__ import print_function
import argparse
import os
import re
import subprocess
import sys


class DirsScanner:
  def __init__(self, dirs, pattern, recursive, exclude, verbose):
    self.dirs = []
    not_found = []
    for d in dirs:
      d = os.path.abspath(os.path.expanduser(d) if d.startswith('~') else d)
      if os.path.exists(d):
        self.dirs.append(d)
      else:
        not_found.append(d)
    if not_found:
      print('Warning: Some directories not found.')
      print(not_found)

    self._match = re.compile(pattern)
    self.recursive = recursive
    self._exclude = re.compile('.*({0}).*'.format(exclude)) if exclude else None
    self.verbose = verbose
    self._files = []

  @property
  def files(self):
    return self._files

  def scan(self):
    print('Scanning directories...')
    for d in self.dirs:
      self._scan_dir(d)
    return self._files

  def _scan_dir(self, d):
    if self.verbose:
      print(d)
    for name in os.listdir(d):
      p = os.path.join(d, name)
      if os.path.isdir(p) and self.recursive:
        if not (self._exclude and self._exclude.match(p)):
          self._scan_dir(p)
      elif os.path.isfile(p) and self._match.match(p):
        if not (self._exclude and self._exclude.match(p)):
          self._files.append(p)


def main(argv):
  parser = argparse.ArgumentParser()
  parser.add_argument('-o', '--output')
  parser.add_argument('-f', '--files', nargs='*')
  parser.add_argument('-d', '--dirs', nargs='*')
  parser.add_argument('-r', '--recursive', action='store_true')
  parser.add_argument('-s', '--suffix', default=['.h'], nargs='*', help='Suffix patterns. ex. .h .cpp .cc')
  parser.add_argument('-x', '--exclude', help='Exclude pattern')
  parser.add_argument('-v', '--verbose', action='store_true')
  args, extra = parser.parse_known_args(argv)

  cmd = ['ebrowse']
  if args.output:
    out_dir = os.path.dirname(os.path.abspath(
      os.path.expanduser(args.output) if args.output.startswith('~') else args.output))
    if not os.path.exists(out_dir):
      print('Output direcory not found. %s' % out_dir, file=sys.stderr)
      return -1
    cmd.extend(['-o', os.path.abspath(args.output)])

  files = args.files if args.files else []
  if args.dirs:
    pattern = '(%s)' % '|'.join(['.*%s$' % '\\' + s if s.startswith('.') else s for s in args.suffix])
    files.extend(DirsScanner(args.dirs, pattern, args.recursive, args.exclude, args.verbose).scan())

  if not files:
    print('No files to browse.')
    return 0

  cmd.extend(extra)
  print('Browsing...')
  if args.verbose:
    for f in files:
      print(f)
  cmd.extend(files)
  return subprocess.call(cmd)

if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))
