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


Separator = ','
fn  = "../dat/test.csv"
fnt = "../dat/test_t.csv"
fn3 = "../dat/c001.dat"

print("testing read/write methods, no_time case")
data = tabdata.TabData(no_time=True)
with open(fn) as F:
    data.read_csv(F, Separator)
    data.write_csv(sys.stdout, Separator)

print("\ntesting read/write methods, with time column, default separator")
data = tabdata.TabData(no_time=False)
with open(fnt) as F:
    data.read_csv(F)
    data.write_csv(sys.stdout)

print("\ntesting read constructor; replacing Separator (, -> ;)")
with open(fn) as F:
    data = tabdata.from_csv(F)
    data.write_csv(sys.stdout, Separator = ';')


print("\ntesting TAb separated, with spaces and time column")
data = tabdata.TabData(no_time=False)
with open(fn3) as F:
    data.read_csv(F, Separator='\t')
    data.write_csv(sys.stdout)
