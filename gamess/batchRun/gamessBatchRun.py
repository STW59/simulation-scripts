#!/usr/bin/python3
"""
Written by Stephen E. White
Last updated : 22NOV2017

This script is designed to run all gamess .inp files in the directory from
which the script is run. It will not double-process data if a .log file for the
data set is present.

To run this script:
sudo python3 gamessBatchRun.py
In linux, always run this script as a superuser (su or sudo).
"""

import datetime
import logging
import os
import shutil
import subprocess
import time

# Constants that should be edited based on your system
PATH_TO_GAMESS = "/home/asher/Programs/gamess/"  # Full path to gamess folder
TEMP_BINARY_DIR = "/scr/asher/"  # Directory for binary output files
SUPP_OUTPUT_DIR = "/home/asher/scr/"  # Directory for supplemental output files
VERSION = "01"  # Version number for gamess
DATETIME = datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%S")


def process_data(input_file, number_of_processors=4):
    name = input_file.split("Input.inp")[0]
    output_name = name + "Output.log"

    input_directory = os.getcwd()

    # Copy input file to gamess directory
    try:
        logging.debug("Copying input data file to gamess directory.")
        shutil.copyfile(os.path.join(input_directory, input_file),
                        os.path.join(PATH_TO_GAMESS, input_file))
    except FileNotFoundError:
        logging.error("{} not found in gamess directory. Moving to next file.")
        return

    os.chdir(PATH_TO_GAMESS)

    # Check for and remove all residual files from previous gamess runs
    supp_out_files = os.listdir(SUPP_OUTPUT_DIR)
    for file in supp_out_files:
        if file.startswith(name):
            os.remove(os.path.join(SUPP_OUTPUT_DIR, file))
            logging.warning("Removed {} from supplemental output directory."
                            .format(file))

    temp_binary_files = os.listdir(TEMP_BINARY_DIR)
    for file in temp_binary_files:
        if file.startswith(name):
            os.remove(os.path.join(TEMP_BINARY_DIR, file))
            logging.warning("Removed {} from temporary binary directory."
                            .format(file))

    # Run gamess job
    logging.info("Beginning gamess process.")
    output_log = open(output_name, 'w')
    subprocess.call(["./rungms", input_file, VERSION,
                     str(number_of_processors)], stdout=output_log)
    output_log.close()
    logging.info("gamess process complete.")

    # Clean up files from run and copy output to input directory
    try:
        os.remove(os.path.join(PATH_TO_GAMESS, input_file))
        shutil.copyfile(os.path.join(PATH_TO_GAMESS, output_name),
                        os.path.join(input_directory, output_name))
        logging.info("Output file copied to starting directory.")
        os.remove(os.path.join(PATH_TO_GAMESS, output_name))
    except FileNotFoundError:
        logging.warning("Output file not found.")
    finally:
        os.chdir(input_directory)  # Return to input directory for next job


def main():
    # Set up log file for batch process.
    # NOTE: this is different than the gamess .log files.
    log_filename = DATETIME + ".log"

    file_out = logging.FileHandler(log_filename)
    console_out = logging.StreamHandler()
    handlers = [file_out, console_out]
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s: %(levelname)s: %(message)s',
                        handlers=handlers)

    logging.info("Beginning log for batch started {}."
                 .format(DATETIME.replace("_", ":")))

    # Read all files in working directory
    data_sets = []
    processed_data_sets = []
    input_dir_list = os.listdir(os.getcwd())

    # Put gamess input and log files into data structures for processing
    for file in input_dir_list:
        if file.endswith(".inp"):
            data_sets.append(file)
        elif file.endswith(".log"):
            processed_data_sets.append(file)
    logging.debug("Input read complete.")

    # Check to see if file was processed (check .inp against .log)
    for data_set in data_sets:
        if (data_set.split(".inp")[0] + ".log") in processed_data_sets:
            data_sets.remove(data_set)
            logging.info("{} already processed. Removing from queue."
                         .format(data_set))
    data_sets.sort()
    logging.debug("Processed files removed from queue.")

    # Run each unprocessed input file
    for input_file in data_sets:
        logging.info("Beginning gamess job for {}."
                     .format(input_file))

        start_time = time.time()
        process_data(input_file, 4)
        end_time = time.time()

        logging.info("gamess job for {} complete.".format(input_file))
        logging.info("Run time: {} hours.".
                     format((end_time - start_time) / (60 * 60)))

    logging.info("Batch process complete.")


main()
