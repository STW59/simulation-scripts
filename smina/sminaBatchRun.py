#!/usr/bin/python3
"""
Written by Stephen E. White
Last updated : 02NOV2017

This script is designed to run the given Smina input files as a batch.

To run this script:
python3 sminaBatchRun.py
"""

import datetime
import logging
import os
import subprocess
import time

# Constants that should be edited based on your system
DATETIME = datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%S")
SMINA_EXECUTABLE = "smina.static"
THREADS = 3


def process_data(test_compound, protein_ligand, ligand):
    name = test_compound.split(".sdf")[0]
    output_name = os.path.join("output", name + "_output.sdf")
    output_log_name = os.path.join("output", name + ".log")

    # Run Smina job
    logging.info("Beginning Smina process.")
    output_log = open(output_log_name, 'w')
    subprocess.call(["./{} -r {} -l {} --autobox_ligand {} -o {} --flexdist_ligand {}"
                     .format(SMINA_EXECUTABLE, protein_ligand, test_compound, ligand, output_name, ligand)],
                    shell=True, stdout=output_log)
    output_log.close()
    logging.info("Smina process complete.")


def main():
    # Set up log file for batch process. NOTE: this is different than the GAMESS .log files.
    log_filename = DATETIME + ".log"

    file_out = logging.FileHandler(log_filename)
    console_out = logging.StreamHandler()
    handlers = [file_out, console_out]
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s: %(levelname)s: %(message)s',
                        handlers=handlers)

    logging.info("Beginning log for batch started {}.".format(DATETIME.replace("_", ":")))

    # Set up input data files
    protein = "REC.pdb"
    ligand = "LIG.sdf"
    # test_compounds = ["compound_1.sdf"]
    test_compounds = ["compound_1.sdf",
                      "compound_2.sdf",
                      "compound_3.sdf",
                      "compound_4.sdf",
                      "compound_5.sdf",
                      "compound_6.sdf",
                      "compound_7.sdf",
                      "compound_8.sdf",
                      "compound_9.sdf",
                      "compound_10.sdf"]

    logging.info("Protein file: {}".format(protein))
    logging.info("Ligand file: {}".format(ligand))
    logging.info("Number of test compounds: {}".format(len(test_compounds)))

    # Run each test compound
    for compound in test_compounds:
        logging.info("Beginning Smina job for {}.".format(compound))

        start_time = time.clock()
        process_data(compound, protein, ligand)
        end_time = time.clock()

        logging.info("Smina job for {} complete.".format(compound))
        logging.info("Run time: {} seconds.".format((end_time - start_time)))

    logging.info("Batch process complete.")


main()
