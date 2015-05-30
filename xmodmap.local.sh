#!/bin/bash
MAP="$(dirname $(readlink -f "${BASH_SOURCE}"))"/.xmodmap.local
if [ -f "$MAP" ]; then
  xmodmap "$MAP"
fi
