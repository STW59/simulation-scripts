#!/usr/bin/python3
"""
Written by Stephen E. White
Last updated : 01DEC2017

This script is designed to run all gamess .inp files as a series of energy
optimizations running through different levels of DFT basis sets.

This script will run all gamess .inp files in the directory from which the
script is run. It will not double-process data if a .log file for the data
set is present.

To run this script:
sudo python3 optimizeBatchRun.py
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

# Logging constants
DATETIME = datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%S")
LOGGING_LEVEL = logging.INFO

# Basis Set constants
# Processing order for basis sets.
B3LYP_BASIS_SETS = ["4-31G",
                    "5-31G",
                    "6-31G",
                    "6-311G",
                    "6-311G(d)",
                    "6-311G(d,p)",
                    "6-311+G(d,p)",
                    "6-311++G(d,p)"]  # TODO: Add test conditions for CCnWC -> ACCnWC and PCseg-n -> APCseg-n basis sets
# Parameters for basis sets
# "Basis set": (GBASIS, NGAUSS, NDFUNC, NPFUNC, DIFFSP, DIFFS)
B3LYP_BASIS_DICT = {"4-31G": ("N31", "4", "", "", "", ""),
                    "5-31G": ("N31", "5", "", "", "", ""),
                    "6-31G": ("N31", "6", "", "", "", ""),
                    "6-311G": ("N311", "5", "", "", "", ""),
                    "6-311G(d)": ("N311", "6", "1", "", "", ""),
                    "6-311G(d,p)": ("N311", "6", "1", "1", "", ""),
                    "6-311+G(d,p)": ("N311", "6", "1", "1", ".TRUE.", ""),
                    "6-311++G(d,p)": ("N311", "6", "1", "1", ".TRUE.", ".TRUE.")}


def build_data_sets():
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
        if (data_set.split("Input.inp")[0] + "Output.log") in processed_data_sets:
            data_sets.remove(data_set)
            logging.info("{} already processed. Removing from queue."
                         .format(data_set))
    data_sets.sort()
    logging.debug("Processed files removed from queue.")
    return data_sets


def build_next_input(name, basis_set_index, next_basis_set):
    gamess_output_name = name + "Output.log"
    new_input_name = name + str(basis_set_index) + "-Input.inp"
    old_input_name = name + "Input.log"

    # Read required data from files
    gamess_header = read_gamess_header(old_input_name)
    atom_coords = read_atom_coords(gamess_output_name)

    # Open new input file
    new_input_file = open(new_input_name, 'w')

    # Write new gamess input file
    header_line_index = 0
    for header_line in gamess_header:
        if "$BASIS" in header_line:
            new_line = " $BASIS GBASIS={} NGAUSS={} " \
                .format(B3LYP_BASIS_DICT[next_basis_set][0],
                        B3LYP_BASIS_DICT[next_basis_set][1])

            # Add heavy atom polarization
            if "d" in next_basis_set:
                new_line += "NDFUNC={} ".format(B3LYP_BASIS_DICT[next_basis_set][2])

            # Add hydrogen polarization
            if "p" in next_basis_set:
                new_line += "NPFUNC={} ".format(B3LYP_BASIS_DICT[next_basis_set][3])

            # Add heavy atom diffuse functions
            if "1+g" in next_basis_set:
                new_line += "DIFFSP={} ".format(B3LYP_BASIS_DICT[next_basis_set][4])

            # Add hydrogen diffuse functions
            if "1++g" in next_basis_set:
                new_line += "DIFFS={}".format(B3LYP_BASIS_DICT[next_basis_set][5])

            new_line += "$END\n"
        elif "$CONTRL" in header_line:
            new_line = " $CONTRL SCFTYP=RHF RUNTYP=OPTIMIZE DFTTYP=B3LYP "

            # Convert from cartesian to internal coordinates
            # if basis_set_index == len(B3LYP_BASIS_SETS)-1:
            #     new_line += "COORD=ZMT "

            new_line += "$END\n"
        elif header_line_index == len(B3LYP_BASIS_SETS) - 2:
            # Append latest basis set to title
            new_line = header_line + next_basis_set
        else:
            new_line = header_line

        new_input_file.write(new_line)
        header_line_index += 1

    coord_line = 0
    for coordinate in atom_coords:
        if coord_line > 2:
            new_input_file.write(coordinate[1:])
        coord_line += 1

    new_input_file.write(" $END")
    new_input_file.close()


def main():
    batch_start_time = time.time()
    # Set up log file for batch process.
    # NOTE: this is different than the gamess .log files.
    log_filename = DATETIME + ".log"

    file_out = logging.FileHandler(log_filename)
    console_out = logging.StreamHandler()
    handlers = [file_out, console_out]
    logging.basicConfig(level=LOGGING_LEVEL,
                        format='%(asctime)s: %(levelname)s: %(message)s',
                        handlers=handlers)

    logging.info("Beginning log for batch started {}."
                 .format(DATETIME.replace("_", ":")))

    # Read all files in working directory
    data_sets = build_data_sets()

    # Run each unprocessed input file
    for input_file in data_sets:
        # Generates gamess inputs for each of the given basis sets
        # Subsequently runs the gamess calculations for the inputs
        basis_set_index = 0
        for basis_set in B3LYP_BASIS_SETS:
            logging.info("Beginning gamess job for {} with {} basis set."
                         .format(input_file, basis_set))

            start_time = time.time()
            process_data(input_file, 4)
            end_time = time.time()

            logging.info("gamess job for {} complete.".format(input_file))
            logging.info("Run time: {} hours.".
                         format((end_time - start_time) / (60 * 60)))

            # Create new gamess inputs for next basis set
            try:
                # Determine next basis set
                basis_set_index += 1
                next_basis_set = B3LYP_BASIS_SETS[basis_set_index]
            except IndexError:
                logging.info("All basis sets complete.")
                # Process next data set
                continue

            # Determine file names
            name = input_file.split("Input.inp")[0]
            new_input_name = name + "-" + str(basis_set_index) + "-Input.inp"
            gamess_output_name = name + "Output.log"

            # Check to see if gamess "exited gracefully"
            exited_gracefully = False
            gamess_output_file = open(gamess_output_name, 'r')
            for output_line in gamess_output_file:
                if "exited gracefully" in output_line:
                    exited_gracefully = True
            gamess_output_file.close()
            if not exited_gracefully:
                logging.warning("gamess did not exit gracefully.")
                logging.warning("Check the gamess output file for details.")
                logging.warning("Continuing to next input file.")
                break

            # Build next GAMESS input file
            logging.info("Generating input for {} basis set.".format(next_basis_set))
            build_next_input(name, basis_set_index, next_basis_set)
            logging.info("Input generation complete.")

            input_file = new_input_name

    batch_end_time = time.time()
    logging.info("Batch process complete.")
    logging.info("Total batch processing time: {} hours"
                 .format((batch_end_time - batch_start_time) / (60 * 60)))


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

    remove_residuals(name)

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


def read_atom_coords(gamess_output_name):
    gamess_output = open(gamess_output_name, 'r')
    atom_coords = []
    for output_line in gamess_output:
        if "EQUILIBRIUM GEOMETRY LOCATED" in output_line:
            while True:
                for selected_line in gamess_output:
                    if selected_line is not "\n":
                        atom_coords.append(output_line)
                    else:
                        logging.debug("Extracted atom coordinates from gamess output file.")
                        gamess_output.close()
                        return atom_coords


def read_gamess_header(old_input_name):
    old_input_file = open(old_input_name, 'r')
    header = []
    for header_line in old_input_file:
        if "C1" not in header_line:
            header.append(header_line)
        else:
            header.append(header_line)
            logging.debug("Extracted header from gamess input file.")
            break
    return header


def remove_residuals(name):
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


main()
