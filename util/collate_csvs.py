#! /usr/bin/python
'''Combine multiple CSVs to one file'''

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
from lib import tabdata


# ------------------------------------------------
# helper functions

def ProcessCommandLine():
    "goes through command line, returns opts,FileName pair"
    #lets parse the arguments
    parser = argparse.ArgumentParser(description='''Combine multiple csv files into one.

Reads all csv files passed in cmdline and combines their data blocks. A wildcard (e.g. *.dat)
can be passed, it will be substituted by shell and treated as a list.
There should be a single time column in each file, which (ideally) should match throughout.
''')
    parser.add_argument('fn', nargs="+", help="list of file names to collate or a wildcard")
    #parser.add_argument('-g', default='grid_table.lst', help="name of the file with the grid of the aspect factors, defaults to 'grid_table.lst'")
    #parser.add_argument('-p', action='store_true', help="print the table with weights as well")
    parser.add_argument('-o', help="name of output file. If omitted, uses fn1[:-3].atf")
    #parser.add_argument('-s', help="skip S header lines")
    return parser.parse_args()



# ------------------------------------------------
#main block
args = ProcessCommandLine()

print(args.fn)
sys.exit()

#get the 1st file in to serve as a base to collate upon
with open(args.fn[0]) as F:
    data = tabdata.TabData()
    tabdata_io.read_xvg_byGmx(data, F)

# now process the rest
for fn in args.fn[1:]:
    with open(fn) as F:
        newdat = tabdata.TabData()
        tabdata_io.read_xvg_byGmx(newdat, F)
        if (newdat.Npts != data.Npts):
            print("lengths of supplied files do not match!")
            sys.exit()
        # now append column
        data.append_columns(newdat, ncols=1)


if args.o:
	F = open(args.o, mode='w')
else:
	F = open(args.fn[0][:-4]+"_new.xvg", mode='w')

tabdata_io.write_xvg_byGmx(data, F)
F.close()
