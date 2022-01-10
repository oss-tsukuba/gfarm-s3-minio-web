#! /bin/bash

set -eu -o pipefail
#set -x
DEBUG=0

# usage:
# inotify_copy.sh <timeout>

### interval to add new directories and synchronize all
### (default 30min.)
timeout=${1:-1800}

src="/host_home"
dst="/copy_home"

INITIALIZED_FILE="$dst/_copy_home_initialized"

rm -f "$INITIALIZED_FILE"

### under ${src}
# directory is: .../
# copy_targets is also used in [[ ... =~ $patt ]]
copy_targets=(
    /*/.gfarm_shared_key
    /*/.gfarm2rc
    /*/.globus/
)

debug() {
    [ $DEBUG -eq 1 ] && echo "DEBUG: $1"
}

watch_list=$(mktemp)

watch_list_init() {
    #truncate --size 0 "$watch_list"
    # watch directly under $src and $src/*
    echo "${src}/" > "$watch_list"
    # Do not use double quote
    for p in $(find ${src}/ -maxdepth 1); do
        echo "${p}" >> "$watch_list"
    done
    for L in "${copy_targets[@]}"; do
        # Do not use double quote
        for p in $(find ${src}${L} 2> /dev/null || true); do
            echo "${p}" >> "$watch_list"
        done
    done
}

opt_events=(
    -e CREATE
    -e MODIFY
    -e MOVED_TO
    -e DELETE
    -e ATTRIB
)

sync_list=$(mktemp)

copy_all() {
    #truncate --size 0 "$sync_list"
    echo "*/" > "$sync_list"
    for L in "${copy_targets[@]}"; do
        if [ ${L: -1} = "/" ]; then  # last character
            L="${L}**"
        fi
        echo "${L}" >> "$sync_list"
    done
    #cat $sync_list  # debug
    rsync -q --one-file-system -amv --delete \
          --include-from="$sync_list" --exclude='*' "$src/" "$dst/"
}

stop() {
    echo "stopped"
    rm -f "$watch_list" "$sync_list"
    exit 0
}

trap stop EXIT 1 2 15

watch_list_init
copy_all

touch "$INITIALIZED_FILE"

FORMAT='%T	%w	%e	%Xe	%f'
TIME_FORMAT='%F-%T'

while true; do
    # new files may be created
    watch_list_init
    # cat "$watch_list" # debug
    SAVE_IFS=$IFS
    IFS='	'
    # Do not use --recursive
    if inotifywait --quiet \
        "${opt_events[@]}" \
        --timeout $timeout \
        --timefmt "$TIME_FORMAT" --format "$FORMAT" \
        --fromfile "$watch_list" |
        while read t watched_path ev1 ev2 event_fname; do
            # echo "$t"
            # echo "$watched_path"
            # echo "$ev1"
            # echo "$ev2"
            # echo "$event_fname"

            debug "[$t] $ev1: {$watched_path} {$event_fname}"
            found=0
            # find home-directories and copy_targets
            for patt in "${copy_targets[@]}" "${src}/[^/]+/?$"; do
                last_char=${patt: -1}
                if [ $last_char != "/" -a $last_char != "$" ]; then
                    # is file
                    patt="${patt}$"
                fi
                debug "check: ${watched_path}${event_fname} =~ $patt"
                if [[ "${watched_path}${event_fname}" =~ $patt ]]; then
                    found=1
                    break
                fi
            done
            if [ $found -eq 0 ]; then
                continue
            fi
            echo "copy_all: $ev1: {$watched_path} {$event_fname}"
            copy_all
            case "$ev1" in
            MODIFY*|ATTRIB*)
                ;;
            *)
                debug "A file may be created or deleted. re-set inotifywait"
                break
                ;;
            esac
        done
    then
        :
    else # timeout or break
        copy_all
    fi
    IFS=$SAVE_IFS
done

exit 1
