#!/usr/bin/python
# Copyright (c) 2011 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.


"""Argument-less script to select what to run on the buildbots."""


import os
import subprocess
import sys


def GypTestFormat(title, format, msvs_version=None):
  """Run the gyp tests for a given format, emitting annotator tags.

  See annotator docs at:
    https://sites.google.com/a/chromium.org/dev/developers/testing/chromium-build-infrastructure/buildbot-annotations
  Args:
    format: gyp format to test.
  Returns:
    0 for sucesss, 1 for failure.
  """
  print '@@@BUILD_STEP ' + title + '@@@'
  buildbot_dir = os.path.dirname(os.path.abspath(__file__))
  trunk_dir = os.path.dirname(buildbot_dir)
  root_dir = os.path.dirname(trunk_dir)
  if msvs_version:
    env = {
        'GYP_MSVS_VERSION': msvs_version,
    }
  else:
    env = None
  retcode = subprocess.call(
      ['python', 'trunk/gyptest.py',
       '--all',
       '--passed',
       '--format', format,
       '--chdir', 'trunk',
       '--path', '../scons'],
      cwd=root_dir, env=env)
  if retcode:
    # Emit failure tag, and keep going.
    print '@@@STEP_FAILURE@@@'
    return 1


def GypBuild():
  retcode = 0
  if sys.platform in ['linux', 'linux2']:
    retcode += GypTestFormat('scons', format='scons')
    retcode += GypTestFormat('make', format='make')
  elif sys.platform == 'darwin':
    retcode += GypTestFormat('xcode', format='xcode')
  elif sys.platform == 'win32':
    retcode += GypTestFormat('msvs-2008', format='msvs', msvs_version='2008')
    retcode += GypTestFormat('msvs-2010', format='msvs', msvs_version='2010')
  else:
    raise Exception('Unknown platform')
  if retcode:
    # TODO(bradnelson): once the annotator supports a postscript (section for
    #     after the build proper that could be used for cumulative failures),
    #     use that instead of this. This isolates the final return value so
    #     that it isn't misattributed to the last stage.
    print '@@@BUILD_STEP failures@@@'
    sys.exit(retcode)


if __name__ == '__main__':
  GypBuild()
