#!/bin/bash

echo

function verbose_eval {
    echo
    echo _____________________________________________________________________
    echo $*
    echo - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    eval $*
    echo ---------------------------------------------------------------------
    echo
}

if [ -e .git ];
then
    echo ".git directory found"
    verbose_eval git pull origin master  
elif [ -e .svn ];
then
    echo ".svn directory found"
    verbose_eval svn update
else
    echo "no .git or .svn directory found. Can't update"
fi