#!/bin/sh
#
# autogen.sh
# $Id$
#
# Generates initial makefiles etc
#

[ -f autogen.sh ] || { echo "autogen.sh should be run from srcdir"; exit 1; }

echo "Running glib-gettextize..."
glib-gettextize --copy --force || { echo "glib-gettextize failed"; exit 1; }

echo "Running intltoolize..."
intltoolize --automake --copy --force || { echo "intltoolize failed"; exit 1; }

echo "Running autoreconf..."
autoreconf --force --install || { echo "autoreconf failed"; exit 1; }
