#!/usr/bin/env python3

import os
import subprocess

build_root = os.environ.get('MESON_BUILD_ROOT')
source_root = os.environ.get('MESON_SOURCE_ROOT')

print('Install schemas in build dir…')

source_datadir = os.path.join(source_root, 'data')
source_file = os.path.join(source_datadir, 'gschemas.compiled')
targetdir = os.path.join(build_root, 'data', 'glib-2.0', 'schemas')

subprocess.call(['glib-compile-schemas', source_datadir])
subprocess.call(['mkdir', '-p', targetdir])
subprocess.call(['mv', source, targetdir])
