#!/usr/bin/python

from __future__ import print_function
import argparse
import os
import platform
import re
import subprocess
import sys
from multiprocessing import cpu_count


def prompt(p):
  re_y = re.compile('^(Y|y|yes)$', re.IGNORECASE)
  re_n = re.compile('^(N|n|no)$', re.IGNORECASE)
  cont = False
  while not cont:
    key_input = raw_input(p)
    if re_n.match(key_input):
      return False
    if re_y.match(key_input):
      return True


def clean(wd):
  return subprocess.call(['git', 'clean', '-dfx'], cwd=wd)


def check(ret):
  if ret != 0:
    raise Exception('Failed to build emacs.')
  return ret


def env():
  e = os.environ
  v = '-pipe -march=native'
  flag = e.get('CFLAGS')
  if not flag:
    e.update(CFLAGS=v)
  elif v not in flag:
    e.update(CFLAGS=' '.join([flag, v]))
  return e


def linux_env():
  e = env()
  v = '-Wl,-flto -Wl,-O2'
  flag = e.get('LDFLAGS')
  if not flag:
    e.update(LDFLAGS=v)
  elif v not in flag:
    e.update(LDFLAGS=' '.join([flag, v]))
  return e


def main(argv):
  wd = os.getcwd()

  ret = subprocess.call(['git', 'rev-parse', '--is-inside-work-tree'], cwd=wd)
  if ret != 0 or not os.path.exists(os.path.join(wd, 'src', 'emacs-icon.h')):
    print('Not in emacs repository.', file=sys.stderr)
    return 1

  parser = argparse.ArgumentParser()
  parser.add_argument('-p', '--pull', action='store_true')
  parser.add_argument('-b', '--build', action='store_true')
  parser.add_argument('-j', '--job', type=int, default=cpu_count(), choices=range(1, cpu_count() + 1))
  parser.add_argument('-D', '--install-directory')
  parser.add_argument('-I', '--install', action='store_true')
  parser.add_argument('-l', '--clean', action='store_true')
  parser.add_argument('-i', '--interactive', action='store_true')
  args = parser.parse_args(argv)

  cleaned = False
  if args.pull or (args.interactive and prompt('Continue to pull? (y/n): ')):
    check(subprocess.call(['git', 'fetch', '--all'], cwd=wd))
    if args.clean:
      check(clean(wd))
      cleaned = True
    check(subprocess.call(['git', 'reset', '--hard'], cwd=wd))
    check(subprocess.call(['git', 'pull'], cwd=wd))

  if args.build or (args.interactive and prompt('Continue to build? (y/n): ')):
    if args.clean and not cleaned:
      check(clean(wd))
    with open(os.path.join(wd, 'emacs_autogen.log'), 'w') as fp:
      ret = subprocess.call('./autogen.sh', cwd=wd, stdout=fp, stderr=fp)
      subprocess.call(['cat', 'emacs_autogen.log'], cwd=wd)
      check(ret)

    e, cmd = {
      'Linux': (linux_env(), ['./configure']),
      'Darwin': (env(), ['./configure', '--with-ns', '--without-x'])
    }[platform.system()]
    if args.install_directory:
      if os.path.isabs(args.install_directory):
        d = args.install_directory
      else:
        d = os.path.abspath(os.path.expanduser(args.install_directory))
      cmd.append('--prefix=%s' % d)
    with open(os.path.join(wd, 'emacs_configure.log'), 'w') as fp:
      ret = subprocess.call(cmd, cwd=wd, env=e, stdout=fp, stderr=fp)
      subprocess.call(['cat', 'emacs_configure.log'], cwd=wd)
      check(ret)

    cnt = 0
    ret = 1
    cmd = ['make']
    if args.install:
      cmd.append('install')
    cmd.extend(['-j%s' % args.job])
    while ret != 0 and cnt < 5:
      cnt += 1
      fn = 'emacs_make.log.%s' % cnt
      with open(os.path.join(wd, fn), 'w') as fp:
        ret = subprocess.call(cmd, cwd=wd, env=e, stdout=fp, stderr=fp)
        subprocess.call(['cat', fn], cwd=wd)
  return ret

if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))
