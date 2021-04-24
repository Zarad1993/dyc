#!/usr/bin/env bash

# IGNORE THIS
# Make ../input_files_original if it doesn't already exist
# [ -d "../input_files_original" ] || mkdir ../input_files_original


# RUN BY CALLING '../run_test.sh' WITHIN the input_files FOLDER
# Copy the files of the originals over since the current ones will be mutated by dyc
cp ../input_files_original/* .

dyc start --test < ../user_input/class_test_1.in

cp ./* ../outputs && rm ./*

diff ../outputs/* ../oracles/* && \
echo "========== TEST CASE PASS ==========" || \
echo "\nX X X X X TEST CASE FAIL X X X X X" 