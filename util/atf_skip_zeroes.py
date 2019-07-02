#! /usr/bin/python
'''Collate multiple atf files, regenerating time column'''

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
from lib import tabdata, tabdata_io


# ------------------------------------------------
# helper functions

def ProcessCommandLine():
    parser = argparse.ArgumentParser(description='''Remove zero regions from a file.

Creates a shortened atf file from the one passed by removing sequences of zeroes
in the selecetd column. The time column can be recalculated to be continous or left as is
(concatenating discrete regions directly - WARNING! will cause trouble with pClamp!).
''')
    parser.add_argument('fn',  help="input file name")
    parser.add_argument('-n',  type=int,   help="column number to use for 0-skipping (1 if omitted)")
    parser.add_argument('-s0', type=int,   help="number of consequtive 0's to count as beginning of 0-block (default: 3)")
    parser.add_argument('-t0', type=float, help="initial time (if omitted, start at initial time)")
    parser.add_argument('-dt', type=float, help="time step (if omitted, autocalc based on first 2 entries)")
    parser.add_argument('-o',  help="name of output file. If omitted, use fn1[:-3]_cut.atf")
    parser.add_argument('-ts', help="do not omit time gaps, glue directly. WARNING: incompatible with pClamp!!!")
    return parser.parse_args()



# ------------------------------------------------
#main block
args = ProcessCommandLine()

Ncol = args.n if args.n else 0  # index inside data table, 0-based
Nbeg, Nend = 0, 0 # tracking scan progress
N0 = args.s0 if args.s0 else 3

# read the 1st file and init the time column params
with open(args.fn) as F:
    data = tabdata.from_atf(F, strict_rect = True)
    print("read data from ", args.fn)

LastIdx = data.Npts - N0 # last index to check..


def find_zero_block(data, start):
    "scan through data from start position t fin N0 consequtive 0's"
    curpos = start
    while curpos < LastIdx:
        incomplete = False
        for i in range(curpos, LastIdx):
            if data.data[Ncol][i] == 0:
                # found 1st zero, scan to check if its a block or an occasional 0..
                #print("found 0 at ", i)
                for j in range(i+1, i+N0):
                    if data.data[Ncol][j] != 0:
                        curpos = j
                        incomplete = True
                        break
                if incomplete:
                    # restart the i-loop from new curpos (already set)
                    #print("incomplete block, curpos = ", curpos)
                    break
                else:
                    # found block of N0 consequtive zeros..
                    #print("complete block, returning ", i)
                    return i # index of 1st zero
        # end of "for i" loop,
        if not incomplete:
            # either no zeros were found, or last 0-block was too short..
            #print("no zero-blocks found")
            return LastIdx


Nend = find_zero_block(data, 0)

if Nend == LastIdx:
    print('no zero fragments found in requested column. Aborting..')
    sys.exit(0)
else:
    print("1st zero block found with Nend=", Nend)
    newdat = data.extract_rows(0, Nend, do_headers=True)

while Nend < data.Npts:
    # first find the beginning of the next non-zero block..
    for i in range(Nend+N0, data.Npts):
        if data.data[Ncol][i] != 0:
            Nbeg = i
            break
    if Nbeg < Nend:
        # Nbeg was not reset, so we are at the end (found tail of zeros..)
        # nothing to do, last block is already copied over
        break
    #
    # now scan again until we encoutner zeros..
    #print("scanning for new zero-block starting at ", Nbeg)
    Nend = find_zero_block(data, Nbeg+1)
    if Nend == LastIdx:
        # no zeros found above, so we are at the end. Set Nbeg appropriately.
        Nend = data.Npts
    # block found, copy data over
    print("non-zero block at:", Nbeg, Nend, ";  newdat.Npts=", newdat.Npts)
    blk = data.extract_rows(Nbeg, Nend, do_headers=False)
    newdat.append_rows(blk)


if args.ts:
    # time-skip is requested, but the underlying library does not handle copying time correctly
    # plus the pClamp would have trouble with such files quite likely too..
    print("atf files with breaks are not implemented (and can cause problems with pClamp!)")
    print("Aborting..")
    sys.exit()
else:
    # regenerate time column with given or derived params
    t0 = args.t0 if args.t0 else data.time[0]
    dt = args.dt if args.dt else data.time[1] - data.time[0]
    newdat.regenerate_time_uniform(t0=t0,dt=dt)

fn = args.o if args.o else args.fn[:-4]+"_cut.atf"
with open(fn, mode='w') as F:
    newdat.write_atf(F)
