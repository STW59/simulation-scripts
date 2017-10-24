#!/usr/bin/python3
# Anna Tomberg
# run GAMESS-US job like a normal person

# Updated by Stephen White
# Last updated : 23OCT2017

# TO RUN THIS SCRIPT:
# sudo python3 D2Q10K2_Run.py filename.inp number_of_processors

import sys
import os
import shutil
import time

from subprocess import call

start_time = time.clock()

# HERE GIVE THE FULL PATH TO GAMESS FOLDER:
path_to_gamess = '/home/asher/Programs/gamess/'  # DEFAULT

# HERE GIVE THE VERSION OF GAMESS YOU HAVE:
version = "01"

if len(sys.argv) <= 1:
    input_file = input("Enter path to input: ")
else:
    input_file = sys.argv[1]

try:
    number_of_processors = sys.argv[2]
except:
    number_of_processors = 1

print('>> INPUT FILE: {}'.format(input_file))

name = input_file.split(".inp")[0]
output_name = name + ".log"

input_directory = os.getcwd()

shutil.copyfile(os.path.join(input_directory, input_file), os.path.join(path_to_gamess, input_file))
os.chdir(path_to_gamess)

# CHECKING THAT THERE ARE NO OLD RESIDUAL FILES
file = ''
supp_out_files = os.listdir("/home/asher/scr/")
for file in supp_out_files:
    if file.startswith(name):
        os.remove(os.path.join('/home/asher/scr/', file))

file = ''
temp_binary_files = os.listdir('/scr/asher/')
for file in temp_binary_files:
    if file.startswith(name):
        os.remove(os.path.join('/scr/asher/', file))

# RUNNING GAMESS JOB
call(["./rungms", input_file, version, str(number_of_processors), output_name])

try:
    os.remove(os.path.join(path_to_gamess, input_file))
    shutil.copyfile(os.path.join(path_to_gamess, output_name), os.path.join(input_directory, output_name))
except FileNotFoundError:
    pass

end_time = time.clock()

print(">> COMPLETE.")
print(">> RUN TIME: {} MINUTES".format((end_time - start_time) / 60))
