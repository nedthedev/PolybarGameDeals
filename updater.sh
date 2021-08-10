#!/usr/bin/sh

_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
$($_dir/main.py -s)
echo ""
