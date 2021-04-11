#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File name:          fasta_header.py
Author:             Ivan Munoz-Gutierrez
Date created:       04/02/2021
Date last modified: 04/11/2021
Python version:     3.9
Description:        Change header's name of the fasta sequences that are inside
                    of the assembly.fasta file created by Unicycler. The
                    headers are renamed following the next style:
                    SWXXXX_method_length_topology
"""

import sys
import os
import argparse
import textwrap

def user_input():
    """
    Parse command line arguments provided by the user.

    Parameters
    ----------
    --input and --output
        Command line arguments provided by the user.

    Returns
    -------
    argparse object (.input and .output)
        .input : string
            Path to the fasta file that will be processed.
        .output : string
            Path to the output directory.
    """
    # Creating a parser object for parsing arguments.
    parser = argparse.ArgumentParser(
        prog="python3 fasta_header.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent("""
        Rename fasta headers of assembly.fasta files created by Unicycler
        following MSP's style.
        """),
        epilog=textwrap.dedent("""
        Headers are renamed following the next style:
        SWXXXX_method_length_topology.
        The "method" tag provides information regarding the methology used in
        the lab for the assembly. An example of a header's name following MSP's
        style is the following:

         isolate                           length  topology
         |----|                            |-----| |------|
        >SW2315_n2760-R136-NB73-L1000-96NB_5000000_circular
                |---------method---------|

        Notice that the information provided by method is conected with dashes.

        Isolate's name and method is provided by the name of the directory that
        contains assembly.fasta. The length and topology is obtained by the
        information provided in the original header created by Unicycler. The
        renamed fasta sequences are saved in a file that follows the next
        style: SWXXXX_method_assembly.fasta. For example, the above header
        would be in a file named as follows:

        SW2315_n2760-R136-NB73-L1000-96NB_assembly.fasta

        Note:
        If the user doesn't provide an output path, the directory of the input
        fasta file will be used as the output path.
        """)
    )
    # Creating required arguments group.
    mandatory_arguments = parser.add_argument_group("required arguments")
    mandatory_arguments.add_argument(
        "-i", "--input", required=True, help="Path to input fasta file"
    )
    # Creating optional arguments.
    parser.add_argument(
       "-o", "--output", help="Path to output directory"
    )
    # Saving parsed arguments.
    args = parser.parse_args()

    return args

def check_name_folder_infile(name_folder_infile):
    """
    Check the correct style of infile's folder name according to MSP.

    Parameters
    ----------
    name_folder_infile : string

    Returns
    -------
    name : string
        Infile's folder name with the correct style.
    """
    # If name has a dash at its end, remove it.
    if name_folder_infile[len(name_folder_infile) - 1:] == '-':
        name_folder_infile = name_folder_infile[: -1]
    # If name_folder_infile has underscore at its end, remove it.
    if name_folder_infile[len(name_folder_infile) - 1:] == '_':
        name_folder_infile = name_folder_infile[: -1]
    # Split name_folder_infile using "_" as delimiter.
    name_folder_infile = name_folder_infile.split("_")
    # Lengh of name_folder_infile.
    length_name_folder_infile = len(name_folder_infile)
    # Iterate over name_folder_infile to reconect tags with the correct style.
    for index, tag in enumerate(name_folder_infile):
        if index == 0:
            name = tag + "_"
        elif index == (length_name_folder_infile - 1):
            name += tag + "_"
        else:
            name += tag + "-"

    return name


def process_arguments(args):
    """
    Process the command line arguments provided by the user.

    Parameters
    ----------
    args : argparse.Namespace
        Object holding the command line arguments provided by the user.

    Returns
    -------
    arguments : dictionary
        Information needed to rename headers of input file.
        Example:
        {"input_file": "~/Documents/assemblies/assembly.fasta",
         "name_folder_infile": "assemblies",
         "output_folder": "~/Documents/results"}
    """
    arguments = {"input_file": args.input}
    # Checking if user provided correct arguments.
    if not os.path.exists(args.input):
        sys.exit(1, message=textwrap.dedent("""\
            Error: path to fasta file doesn't exist\n"""))
    if not os.path.isfile(os.path.abspath(args.input)):
        sys.exit(1, message=textwrap.dedent("""\
            Error: provided input argument is not a file\n"""))
    if (args.output is not None) and (not os.path.exists(args.output)):
        sys.exit(1, message=textwrap.dedent("""\
            Error: path to output directory doesn't exist\n"""))

    # Getting path to folder that contains input file.
    path_folder_infile = os.path.dirname(os.path.abspath(args.input))
    # Getting name of folder that contains input file.
    name_folder_infile = os.path.basename(path_folder_infile)

    # Checking if the name of the infile's folder has correct style name.
    arguments["name_folder_infile"] = check_name_folder_infile(
        name_folder_infile) 

    # Getting path to output folder.
    if args.output is None:
        path_output = path_folder_infile
    else:
        path_output = args.output
    arguments["path_output"] = path_output

    return arguments


def make_new_header(header, name_folder_infile):
    """
    Make new header according to MSP style.

    Parameters
    ----------
    header : string
        Header of fasta sequence.
    name_folder_infile : string
        Name of folder that contains the fasta file being processed.

    Returns
    -------
    new_header : string
        Renamed header of fasta sequence.
    """
    # Information needed.
    length = ""
    topology = ""
    # Spliting header into list.
    header = header.split(" ")
    # Looping over header to get info.
    for info in header:
        if "length" in info:
            info = info.split("=")
            length = info[1].replace("\n", "")
        elif "circular" in info:
            info = info.split("=")
            topology = info[0].replace("\n", "")
    # If no info of topology the molecule is linear.
    if topology == "":
        topology = "linear"

    return ">" + name_folder_infile + length + "_" + topology + "\n"


def rename_headers(input_file, name_folder_infile, path_output):
    """
    Make a fasta file with renamed headers according to MSP's style.

    Parameters
    ----------
    input_file : string
        Path to input fasta file.
    name_folder_infile : string
        Folder's name that contains the input fasta file.
    path_output : string
        Path to output directory.
    """
    # Opening input file for reading.
    with open(input_file, "r") as file_reader:
        # Path to outfile.
        outfile = path_output + "/" + name_folder_infile + "assembly.fasta"
        # Opening output file for writing.
        with open(outfile, "w") as file_writer:
            # Iterating over file_reader.
            for line in file_reader:
                # Checking if line is a header:
                if line.startswith(">"):
                    # Change header's name.
                    new_header = make_new_header(line, name_folder_infile)
                    file_writer.write(new_header)
                else:
                    file_writer.write(line)


# -------------------
# Running the program
# -------------------
# Getting user input.
args = user_input()
# Processing arguments provided by user to get input for the function
# rename_headers.
input_rename_headers = process_arguments(args)
# Renaming headers
rename_headers(
    input_rename_headers["input_file"],
    input_rename_headers["name_folder_infile"],
    input_rename_headers["path_output"])
# If everything went well print a message
print("Headers were succesfully renamed!")
