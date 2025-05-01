#! /usr/bin/env bash

if [ $# -ne 2 ]; then
    echo usage: $0 domainname path/to/trainconfig
    exit
fi 

bughivedir=$(dirname $(realpath $0))
echo bughivedir=$bughivedir

domaindir=$bughivedir/benchmarks/$1
echo domaindir=$domaindir

if [ ! -d $domaindir ]; then
    echo $domaindir not found
    exit 1
fi

if [ ! -e $2 ]; then
    echo $2 not found
    exit 1
fi

ln -s $bughivedir
ln -s $domaindir/domain.pddl
ln -s $domaindir/train
ln -s $domaindir/validate
ln -s $bughivedir/scripts/* .
ln -s $bughivedir/asnets-cpddl/bin/pddl-asnets
ln -s $2 train.config
