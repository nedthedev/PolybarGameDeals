#!/usr/bin/sh

_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
output=$($_dir/main.py -s)
echo ""
