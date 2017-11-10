#!/usr/bin/python3
"""
Written by Stephen E. White
Last updated : 09NOV2017

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
TEST = False  # Set to True if you are testing SMINA configurations or debugging


def process_data(test_compound, protein_ligand, ligand):
    name = test_compound.split(".sdf")[0]
    output_name = os.path.join("output", name + "_output.sdf")
    output_log_name = os.path.join("output", name + ".log")

    flex_distance = 7.5
    seed = 0
    exhaustiveness = 32
    scoring = "vinardo"

    # Run Smina job
    logging.info("Beginning Smina process.")
    output_log = open(output_log_name, 'w')

    if not TEST:
        subprocess.call(["./{} --receptor {} --ligand {} --flexdist {} "
                         "--flexdist_ligand {} --autobox_ligand {} "
                         "--scoring {} --out {} --seed {} --exhaustiveness {}"
                        .format(SMINA_EXECUTABLE, protein_ligand, test_compound,
                                flex_distance, ligand, ligand, scoring,
                                output_name, seed, exhaustiveness)],
                        shell=True, stdout=output_log)
    else:
        subprocess.call(["./{} --receptor {} --ligand {} --flexdist {} "
                         "--flexdist_ligand {} --autobox_ligand {} "
                         "--scoring {} --out {} --seed {} --exhaustiveness {}"
                        .format(SMINA_EXECUTABLE, protein_ligand, test_compound,
                                flex_distance, ligand, ligand, scoring,
                                output_name, seed, exhaustiveness)],
                        shell=True, stdout=output_log)

    output_log.close()
    logging.info("Smina process complete.")


def main():
    # Set up log file for batch process.
    log_filename = DATETIME + ".log"

    file_out = logging.FileHandler(log_filename)
    console_out = logging.StreamHandler()
    handlers = [file_out, console_out]
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s: %(levelname)s: %(message)s',
                        handlers=handlers)

    logging.info("Beginning log for batch started {}."
                 .format(DATETIME.replace("_", ":")))

    # Set up input data files
    protein = "REC.pdb"
    ligand = "LIG.sdf"

    if not TEST:
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
    else:
        test_compounds = ["compound_1.sdf"]
    logging.info("Protein file: {}".format(protein))
    logging.info("Ligand file: {}".format(ligand))
    logging.info("Number of test compounds: {}".format(len(test_compounds)))

    # Run each test compound
    for compound in test_compounds:
        logging.info("Beginning Smina job for {}.".format(compound))

        start_time = time.time()
        process_data(compound, protein, ligand)
        end_time = time.time()

        logging.info("Smina job for {} complete.".format(compound))
        logging.info("Run time: {} seconds.".format((end_time - start_time)))

    logging.info("Batch process complete.")


main()
