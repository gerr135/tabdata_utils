#! /bin/env python
# Basic conversion of HEKA text files to ATF
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

import sys, argparse

#sys.path.append("..")
from lib import tabdata

def ProcessCommandLine():
    parser = argparse.ArgumentParser(description="convert HEKA text output to atf format")
    parser.add_argument('fn',   help="input file name")
    parser.add_argument('-o',  help="name of output file. If omitted replace last 3 chars with atf")
    #parser.add_argument('-nt',  action="store_true", help="no time column")
    return parser.parse_args()

args=ProcessCommandLine()

data = tabdata.TabData()
with open(args.fn) as F:
    #print("reading cvs")
    data.read_HEKA_csv(F)

# all data read, now lets figure output file name
fn = args.o if args.o else args.fn[:-3]+"atf"
with open(fn, mode='w') as F:
    data.write_atf(F)
