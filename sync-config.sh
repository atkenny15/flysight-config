#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

set -euo pipefail

function print_help() {
    echo "Usage: $0 [options] <dest>"
    echo ""
    echo "Options:"
    echo "  -n, --dry-run       dry run"
    echo "  -h, --help          display this help info"
}

TEMP=$( \
    getopt \
        -n $(basename "$0") \
        -o hn \
        --long help,dry-run \
        -- "$@"
    )

if [ $? != 0 ]; then echo "Terminating..." >&2; exit 1; fi

eval set -- "$TEMP"

dry_run=
while true; do
    case "$1" in
        -n|--dry-run)   dry_run="--dry-run"     ; shift     ;;
        -h|--help)      print_help              ; exit 0    ;;
        --)             shift                   ; break     ;;
        *)              echo "Internal error!"  ; exit 1    ;;
    esac
done

num_req=1
if [[ $# -ne $num_req ]]; then
    print_help
    echo "ERROR: Script requires $num_req arguments, but got $#"
    exit 1
fi
dest="$1"

cd "${DIR}"

echo sudo rsync -iva $dry_run --progress --stats --no-o --no-g --no-p CONFIG.TXT config "$dest/"
sudo rsync -iva $dry_run --progress --stats --no-o --no-g --no-p CONFIG.TXT config "$dest/"
