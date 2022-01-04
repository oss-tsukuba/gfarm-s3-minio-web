#! /bin/bash

set -eu -o pipefail
#set -x

src="/host_home"
dst="/copy_home"

# under ${src}
### directory: .../
copy_targets=(
    /*/.gfarm_shared_key
    /*/.gfarm2rc
    /*/.globus/
)

### interval to add new directories and synchronize all
### (default 30min.)
timeout=1800

watch_list=$(mktemp)

watch_list_create() {
    truncate --size 0 "$watch_list"
    for L in "${copy_targets[@]}"; do
        # Do not use double quote
        for p in $(ls -1 -d ${src}${L} 2> /dev/null || true); do
            echo "${p}" >> "$watch_list"
        done
    done
}

opt_events=(
    -e CREATE
    -e MODIFY
    -e MOVED_TO
    -e DELETE
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
    rsync -q -amv --include-from="$sync_list" --exclude='*' "$src/" "$dst/"
}

stop() {
    echo "stopped"
    rm -f "$watch_list" "$sync_list"
    exit 0
}

trap stop EXIT 1 2 15

watch_list_create
copy_all

FORMAT='%T	%w	%e	%Xe	%f'
TIME_FORMAT='%F-%T'

while true; do
    # new files may be created
    watch_list_create
    # cat "$watch_list" # debug
    SAVE_IFS=$IFS
    IFS='	'
    if inotifywait --quiet --recursive \
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
            echo "[$t] $ev1: {$watched_path} {$event_fname}"
            copy_all
        done
    then
        :
    else # timeout
        copy_all
    fi
    IFS=$SAVE_IFS
done

exit 1
