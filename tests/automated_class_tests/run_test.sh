#!/usr/bin/env bash
###########
# SUMMARY #
###########
# This script serves as the groundworks of an alternative automated testing scheme to Pytest
# for class docstrings made by DYC.
# This is useful for testing methods that require large amounts of user input and
# an oracle to test the output against.
#
# Further modificaiton is likely needed

################
# INSTRUCTIONS #
################
# 0. This script require pre-creation of the following:
#     - A test case python file.
#         - Follows the naming convention of "class_test_<file_num>.py".
#           where <file_num> is some integer.
#         - Store the file in "input_files_original/".
#     - A text file with user input pre-entered.
#         - Follows the naming convention of "class_test_<file_num>.in" 
#           where <file_num> is some integer.
#         - Store the file in "user_input/".
#     - An oracle of the desired output for the test case to be
#       compared against.
#         - Follows the naming convention of "class_test_<file_num>_correct.py" 
#           where <file_num> is some integer.
#         - Store the file in "oracles/".
# 1. Ensure your test cases are in the 'input_files_original/' folder'.
# 2. Navigate to the 'input_files/' folder. Make the folder if needed.
# 3. Run this script on a single file by calling '../run_test.sh <file_num>'
#    Make sure you are within the 'input_files/' folder when you run the command!
#
################
# SCRIPT START #
################
# Copy the files of the originals to this directory to use them.
# Originals are the backups. The copies here will be modified.
cp ../input_files_original/class_test_$1.py .

# Use the '--test' flag to bypass the text editor opened by Click
# in the DYC program as it's problematic for automated testing and 
# is not needed anyway.
dyc start --test < ../user_input/class_test_$1.in

# Move the modified files to the 'outputs' folder.
mv ./class_test_$1.py ../outputs

# Compare the modified test case to the oracle
diff --ignore-trailing-space ../outputs/class_test_$1.py ../oracles/class_test_$1_correct.py && \
( echo "" && \
echo "========== TEST CASE PASS ==========" ) || \
echo "\nX X X X X TEST CASE FAIL X X X X X" 