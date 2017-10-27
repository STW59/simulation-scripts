#!/usr/bin/python3
"""
Written by Stephen E. White
Last updated : 27OCT2017

In linux, always run this script as a superuser (su or sudo).
This script is designed to run all GAMESS .inp files in the directory from which the script is run.
It will not double-process data if a .log file for the data set is present.
"""

# import logger
import os
import shutil
import subprocess
import time

# Constants that should be edited based on your system
PATH_TO_GAMESS = '/home/asher/Programs/gamess/'  # Full path to GAMESS folder
TEMP_BINARY_DIR = '/scr/asher/'  # Directory for binary output files
SUPP_OUTPUT_DIR = '/home/asher/scr/'  # Directory for supplemental output files
VERSION = '01'  # Version number for GAMESS


def process_data(input_file, number_of_processors=4):
    start_time = time.clock()
    print('>> INPUT FILE: {}'.format(input_file))

    name = input_file.split(".inp")[0]
    output_name = name + ".log"

    input_directory = os.getcwd()

    # Copy input file to GAMESS directory
    try:
        shutil.copyfile(os.path.join(input_directory, input_file), os.path.join(PATH_TO_GAMESS, input_file))
    except FileNotFoundError:
        print('>> FILE {} NOT FOUND'.format(input_file))
        print('>> MOVING TO NEXT FILE')
        return

    os.chdir(PATH_TO_GAMESS)

    # Check for and remove all residual files from previous GAMESS runs
    file = ''
    supp_out_files = os.listdir(SUPP_OUTPUT_DIR)
    for file in supp_out_files:
        if file.startswith(name):
            os.remove(os.path.join(SUPP_OUTPUT_DIR, file))

    file = ''
    temp_binary_files = os.listdir(TEMP_BINARY_DIR)
    for file in temp_binary_files:
        if file.startswith(name):
            os.remove(os.path.join(TEMP_BINARY_DIR, file))

    # Run GAMESS job
    # subprocess.call(["./rungms", input_file, VERSION, str(number_of_processors), output_name])

    # Clean up files from run and copy output to input directory
    try:
        os.remove(os.path.join(PATH_TO_GAMESS, input_file))
        shutil.copyfile(os.path.join(PATH_TO_GAMESS, output_name), os.path.join(input_directory, output_name))
    except FileNotFoundError:
        pass
    finally:
        os.chdir(input_directory)  # Return to input directory for next job

    end_time = time.clock()

    print(">> COMPLETE.")
    print(">> RUN TIME: {} HOURS".format((end_time - start_time) / (60 * 60)))


def main():
    # TODO: Set up logger

    # Read all files in working directory
    data_sets = []
    processed_data_sets = []
    input_dir_list = os.listdir(os.getcwd())

    # Put GAMESS input and log files into data structures for processing
    for file in input_dir_list:
        if file.endswith('.inp'):
            data_sets.append(file)
        elif file.endswith('.log'):
            processed_data_sets.append(file)

    # Check to see if file was processed (check .inp against .log)
    for data_set in data_sets:
        if (data_set.split('.inp')[0] + '.log') in processed_data_sets:
            data_sets.remove(data_set)
    data_sets.sort()

    # Run each unprocessed input file
    for input_file in data_sets:
        process_data(input_file)


main()
