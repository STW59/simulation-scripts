#!/usr/bin/python3
"""
Written by Stephen E. White
Last updated : 30OCT2017

In linux, always run this script as a superuser (su or sudo).
This script is designed to run all GAMESS .inp files in the directory from which the script is run.
It will not double-process data if a .log file for the data set is present.

To run this script:
sudo python3 gamessSingleRun.py filename.inp number_of_processors
"""

import os
import shutil
import subprocess
import sys
import time

start_time = time.clock()

# Constants that should be edited based on your system
PATH_TO_GAMESS = "/home/asher/Programs/gamess/"  # Full path to GAMESS folder
TEMP_BINARY_DIR = "/scr/asher/"  # Directory for binary output files
SUPP_OUTPUT_DIR = "/home/asher/scr/"  # Directory for supplemental output files
VERSION = "01"  # Version number for GAMESS

if len(sys.argv) <= 1:
    input_file = input("Enter path to input: ")
else:
    input_file = sys.argv[1]

try:
    number_of_processors = sys.argv[2]
except IndexError:
    number_of_processors = 1
    print('NUMBER OF PROCESSORS NOT SUPPLIED. DEFAULTING TO 1.')

print('>> INPUT FILE: {}'.format(input_file))

name = input_file.split(".inp")[0]
output_name = name + ".log"

input_directory = os.getcwd()

# Copy input file to GAMESS directory
try:
    shutil.copyfile(os.path.join(input_directory, input_file), os.path.join(PATH_TO_GAMESS, input_file))
except FileNotFoundError:
    print("{} NOT FOUND IN DIRECTORY. TERMINATING.".format(input_file))
    exit()

# Check for and remove all residual files from previous GAMESS runs
supp_out_files = os.listdir(SUPP_OUTPUT_DIR)
for file in supp_out_files:
    if file.startswith(name):
        os.remove(os.path.join(SUPP_OUTPUT_DIR, file))

temp_binary_files = os.listdir(TEMP_BINARY_DIR)
for file in temp_binary_files:
    if file.startswith(name):
        os.remove(os.path.join(TEMP_BINARY_DIR, file))

# Run GAMESS job
output_log = open(output_name, 'w')
subprocess.call(["./rungms", input_file, VERSION, str(number_of_processors)], stdout=output_log)
output_log.close()

# Clean up files from run and copy output to input directory
try:
    os.remove(os.path.join(PATH_TO_GAMESS, input_file))
    shutil.copyfile(os.path.join(PATH_TO_GAMESS, output_name), os.path.join(input_directory, output_name))
    os.remove(os.path.join(PATH_TO_GAMESS, output_name))
except FileNotFoundError:
    pass

end_time = time.clock()

print(">> COMPLETE.")
print(">> RUN TIME: {} HOURS".format((end_time - start_time) / (60 * 60)))
