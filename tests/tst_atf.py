#! /bin/env python
# Testing csv IO with tabular data
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

import sys

#sys.path.append("..")
from lib import tabdata

test_file = "../dat/test.atf"

#def ProcessCommandLine():
    #parser = argparse.ArgumentParser(description="check the csv read/write")
    #parser.add_argument('fn',   help="input file name")
    #parser.add_argument('-nt',  action="store_true", help="no time column")
    #return parser.parse_args()

#args=ProcessCommandLine()


data = tabdata.TabData()
with open(test_file) as F:
    print("testing read_atf procedure")
    data.read_atf(F)
    data.write_atf(sys.stdout)
    #
    print("\ntesting from_atf function")
    F.seek(0)
    data=tabdata.from_atf(F)
    data.write_atf(sys.stdout)
