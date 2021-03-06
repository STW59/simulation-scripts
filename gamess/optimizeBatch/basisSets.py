#!/usr/bin/python3
"""
Written by Stephen E. White
Last updated : 06DEC2017

This script contains the basis set parameters for the optimizeBatchRun.py program.
It is not designed to be run independently.
"""


class Pople:
    # Processing order for basis sets.
    pople_basis_sets = ["4-31G",
                        "5-31G",
                        "6-31G",
                        "6-311G",
                        "6-311G(d)",
                        "6-311G(d,p)",
                        "6-311+G(d,p)",
                        "6-311++G(d,p)"]

    # Parameters for basis sets
    # "Basis set": (GBASIS, NGAUSS, NDFUNC, NPFUNC, DIFFSP, DIFFS)
    pople_basis_dict = {"4-31G": ("N31", "4", "", "", "", ""),
                        "5-31G": ("N31", "5", "", "", "", ""),
                        "6-31G": ("N31", "6", "", "", "", ""),
                        "6-311G": ("N311", "5", "", "", "", ""),
                        "6-311G(d)": ("N311", "6", "1", "", "", ""),
                        "6-311G(d,p)": ("N311", "6", "1", "1", "", ""),
                        "6-311+G(d,p)": ("N311", "6", "1", "1", ".TRUE.", ""),
                        "6-311++G(d,p)": ("N311", "6", "1", "1", ".TRUE.", ".TRUE.")}


class Correlation:  # CCnWC
    # Processing order for basis sets.
    correlation_basis_sets = ["cc-pwCVDZ", "cc-pwCVTZ", "cc-pwCVQZ"]

    # Parameters for basis sets
    # "Basis set": (GBASIS, NGAUSS, NDFUNC, NPFUNC, DIFFSP, DIFFS)
    correlation_basis_dict = {"cc-pwCVDZ": "CCnWC",
                              "cc-pwCVTZ": "CCnWC",
                              "cc-pwCVQZ": "CCnWC"}


class Polarization:
    # Processing order for basis sets.
    polarization_basis_sets = []

    # Parameters for basis sets
    # "Basis set": (GBASIS, NGAUSS, NDFUNC, NPFUNC, DIFFSP, DIFFS)
    polarization_basis_dict = {}
