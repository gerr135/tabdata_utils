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
    parser = argparse.ArgumentParser(description='''Collate multiple atf files in order.

Creates a single sequentional atf file from the list passed. The X column is extended,
incrementing to the end with the given step (uses sX in 1st file if omitted).
Y clumns are collated.
''')
    parser.add_argument('fn', nargs="+", help="list of file names to collate")
    parser.add_argument('-t0', type=float, help="initial time (use t0 i 1st file if omitted)")
    parser.add_argument('-dt', type=float, help="time step (use dt in 1st file if omitted)")
    parser.add_argument('-o',  help="name of output file. If omitted, uses fn1[:-3]_combined.atf")
    return parser.parse_args()



# ------------------------------------------------
#main block
args = ProcessCommandLine()

# read the 1st file and init the time column params
with open(args.fn[0]) as F:
    data = tabdata.from_atf(F, strict_rect = True)

t0 = args.t0 if args.t0 else data.time[0]
dt = args.dt if args.dt else data.time[1] - data.time[0]

# now process the rest
for fn in args.fn[1:]:
    with open(fn) as F:
        newdat = tabdata.from_atf(F)
        if (newdat.Nvars != data.Nvars):
            print("file ", fn, " has mismatching number of columns!")
            sys.exit()
        # now append column
        data.extend_columns(newdat)

# regenerate time column with given params
data.regenerate_time_uniform(t0=t0,dt=dt)

fn = args.o if args.o else args.fn[0][:-4]+"_combined.atf"
with open(fn, mode='w') as F:
    data.write_atf(F)
