#! /usr/bin/python
'''"smart" decimate utility.
This performs the "decimate" routine - trows away the amjority of data, retaining evry Nth,
but it tries to do it in a smarter way - trying to retain as much of "activity" as possible.
Often direct decimation routine (especially with high N) removes completely short openings,
in the traces with low Po, where there are very short-lived states that may only take 1-2 datapoints.
This procedure will try to keep the visual appearance by trying to retain peaks: returning the max
point over certain threshold. This should reduce the size of strongly "oversampled" traces
in a "safer" way..
'''

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

File_Formats = ['csv','atf']

def ProcessCommandLine():
    parser = argparse.ArgumentParser(description='''"smart" decimate utility.

This performs the "decimate" routine - trows away the majority of data, retaining every Nth point,
but it tries to do it in a smarter way - trying to retain as much of "activity" as possible.
'''
)
    parser.add_argument('fn',  help="file names to process. Type is determined form the extension or given by an option")
    parser.add_argument('dec', type=int, help="decimation factor (int)")
    parser.add_argument('dir', choices=["pos","neg"], help="activity direction (one of pos or neg)")
    parser.add_argument('-c', type=float, help="threshold crossing, above which  a max instead of regular is taken. Number between 0 and 1, 0.5 is the default (if omitted)")
    parser.add_argument('-o', help="name of output file. If omitted, adds _dec before extension")
    parser.add_argument('-t', choices=File_Formats, help="specify the input data format")
    parser.add_argument('-v', action='store_true', help="be verbose")
    return parser.parse_args()



# ------------------------------------------------
#main block
args = ProcessCommandLine()

# split off extension from fname
dotpos = args.fn.rfind('.')
FName = args.fn[:dotpos]
FExt  = args.fn[dotpos+1:]

print("file name = ", FName, " + ", FExt)

# determine the input format
if args.t:
    fFmt = args.t
else:
    if FExt not in File_Formats:
        print("cannot process input file of type ", FExt)
        sys.exit()
    fFmt = FExt

#get the 1st file in to serve as a base to collate upon
with open(args.fn) as F:
    data = tabdata.TabData()
    tabdata_io.read_xvg_byGmx(data, F)

# incomplete?


tabdata_io.write_xvg_byGmx(data, F)
F.close()
