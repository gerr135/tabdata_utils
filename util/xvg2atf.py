#! /usr/bin/python
'''Convert xvg (xmgrace) file to (axon's) atf'''

# Copyright (C) 2018  George Shapovalov <gshapovalov@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys,argparse
from tabular_data import *


# ------------------------------------------------
# helper functions

def ProcessCommandLine():
    "goes through command line, returns opts,FileName pair"
    #lets parse the arguments
    parser = argparse.ArgumentParser(description='''Convert an xvg file produced by gromacs to Axon's atf.

Simply reads a given xvg file and write out an atf.
''')
    parser.add_argument('fn', help="file name to process; use '-' for standard input")
    #parser.add_argument('-g', default='grid_table.lst', help="name of the file with the grid of the aspect factors, defaults to 'grid_table.lst'")
    #parser.add_argument('-p', action='store_true', help="print the table with weights as well")
    parser.add_argument('-o', help="name of output file. If omitted, creates a file with an .atf extension")
    #parser.add_argument('-s', help="skip S header lines")
    return parser.parse_args()



# ------------------------------------------------
#main block
args = ProcessCommandLine()

if args.fn == '-':
    F = sys.stdin
else:
    F = open(args.fn)

data = Tabular_Data()
data.read_xvg(F)
F.close()

if args.o:
	F = open(args.o, mode='w')
else:
	F = open(args.fn[:-3]+"atf", mode='w')

data.write_atf(F)
F.close()
