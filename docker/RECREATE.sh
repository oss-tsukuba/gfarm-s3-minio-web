#!/bin/bash

COMPOSE=$(make _COMPOSE)

[ $# = 1 ] || exit 1

$COMPOSE build $1
$COMPOSE rm --stop $1
$COMPOSE up -d $1
