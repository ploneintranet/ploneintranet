#!/bin/sh

for i in . src/*
do
    if [ -d $i ]; then
        if [ -d $i/.git ]; then
            cat $PWD/pre-commit/pre-commit > $i/.git/hooks/pre-commit
	    sed -i -e "s#{PWD}#${PWD}#g" $i/.git/hooks/pre-commit
	    chmod +x $i/.git/hooks/pre-commit
        fi
    fi
done
