#!/bin/bash

# update ctags
ctags -R *

curr_dir=$(pwd)
root_dir=$(git rev-parse --show-toplevel)

cd $root_dir
mfiles=$(git ls-files -m)
for file in $mfiles
do
    git vimdiff $file
    git commit $file
done

cd $curr_dir

git status
git push
