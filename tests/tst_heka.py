#! /bin/env python
# Tester for HEKA-generated csv file IO
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


fn  = "../dat/test_heka.csv"

print("testing read/write methods")
data = tabdata.TabData(no_time=False)
with open(fn) as F:
    data.read_HEKA_csv(F)
    data.write_atf(sys.stdout)

print("\ntesting read constructor; replacing Separator (, -> ;)")
with open(fn) as F:
    data = tabdata.from_HEKA_csv(F)
    data.write_atf(sys.stdout)
