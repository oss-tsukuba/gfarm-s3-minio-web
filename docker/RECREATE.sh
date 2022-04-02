#!/bin/bash

COMPOSE=$(make -s ECHO_COMPOSE)

[ $# = 1 ] || exit 1

$COMPOSE build $1
$COMPOSE rm --stop $1
$COMPOSE up -d $1
