#
# Copyright (C) 2018  George Shapovalov <gshapovalov@gmail.com>
#
# The IO routines for various file formats (may split off too if it grows too much).
# These are "mix-in" methods. Deriving classes for each format would complicate conversions
# (as python's objects cannot mutate - there are no "class-wide" vars), but it allows to
# simply call whatever literal method, so we use mix-ins here.
# 
# For each data format 3 methods are provided:
#   read_xxx(dat, F, extras) - a mix-in reader procedure; data is read into a pre-initialized dat
#   from_xxx(F,extras,inits) - a reader function; constructs dat and return is, passing inits as init params
#   write_xxx(dat,F, extras) - a writer procedure, dat shoul be unchanged
#
# for all methods:  
#   dat    - contains the pre-initialized Tabular_Data object
#   file F should apready be open
#   extras - extra params, usually format specific (separator, etc)
#   inits  = for from_xxx, params (that make sense) to be passed to constructor
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

import csv
from .tabdata_common import *


def read_csv(self, F, Separator = ','):
    """read a basic csv file into self = Tabular_Data:
        optional headers line, followed by 1 entry  per line.
        All lines are supposed to have the same amount of entries (otherwise CSV_Error is raised).
        Signal "no time column" condition when calling constructor.
        sep  - separator to be used,
    """
    reader = csv.reader(F, delimiter=Separator)
    line1 = next(reader)
    NCols = len(line1)
    # initialize base structure
    if self.has_time():
        self.data = [[] for i in range(NCols - 1)]
    else:
        self.data = [[] for i in range(NCols)]
    #
    # local function to pack data line (to avoid code duplication)
    def line2data(items):
        "distribute list of strings into time/data entries"
        if self.has_time():
            if len(items) != len(self.data)+1:
                raise FormatMismatch
            self.time.append(float(items[0]))
            for i in range(1,len(items)):
                self.data[i-1].append(float(items[i]))
        else:
            if len(items) != len(self.data):
                raise FormatMismatch
            for i in range(len(items)):
                self.data[i].append(float(items[i]))
    #
    # try to detect if 1st line contains a header or data
    try:
        ff = float(line1[0])
        # still here? no header then, only data; pack the already read entries
        line2data(line1)
    except ValueError:
        # we got a proper header, just use it directly
        self.colID = line1
    #
    # we are all set now, just run to the end reading data line by line
    for line in reader:
        line2data(line)

def write_csv(self, F, Separator = ','):
    """write a basic csv file. Presence of headers or separate time should already be known..
        sep  - separator to be used,
    """
    writer = csv.writer(F, delimiter=Separator)
    if self.colID != []:
        # we have headers
        writer.writerow(self.colID)
    for i in range(len(self.data[0])):
        line = [] # we need to form a list to pass to a csv.writer
        if hasattr(self,'time'):
            line.append(self.time[i])
        for j in range(len(self.data)):
            line.append(self.data[j][i])
        writer.writerow(line)


def read_atf(self, F):
    "read an ATF file, store headers as-is"
    if F.readline() != "ATF\t1.0\n": raise ATF_Error
    sNhdr, sNcol = F.readline().strip().split()
    Nhdr = int(sNhdr)
    Ncol = int(sNcol)
    for i in range(Nhdr):
        self.headers.append(F.readline().strip())
    # should be done with generic headers, now the column titles
    for col in F.readline().strip().split("\t"): # \t is used as the separator in ATF throughout
        # ATF format uses quotes in title row for each entry, other formats don't, so strip them here
        newCol = col
        if col[0] == '"':
            newCol = col[1:-1]
            #print("removing quotes, newCol=" + newCol)
        self.colID.append(newCol)
    if len(self.colID) != Ncol: raise ATF_Error
    # now just run until the end line by line..
    # prepare the empty data columns (only data, no time here)
    for i in range(Ncol-1):
        self.data.append([])
    for line in F:
        items = line.split("\t")
        self.time.append(float(items[0]))
        for j in range(Ncol-1):
            self.data[j].append(float(items[j+1]))

def write_atf(self, F):
    "writes the collected data out in an atf format"
    # first the general headers
    F.write("ATF\t1.0\n")
    F.write("{}\t{}\n".format(len(self.headers), len(self.data)+1 ))
    for hdr in self.headers:
        F.write(hdr + "\n")
    # next form the column titles
    for col in self.colID[:-1]:
        # readd quotes in titles
        F.write('"' + col + '"' + "\t")
    F.write('"' + self.colID[-1] + '"' + "\n")
    #
    # now dump the data
    for i in range(len(self.time)):
        #F.write("{:01.4e}".format(self.time[i]))
        F.write("{0}".format(self.time[i]))
        for j in range(len(self.data)):
            F.write("\t{0:e}".format(self.data[j][i]))
        F.write("\n")


def read_xvg_gmx(self, F):
    """reader for an xvg (xmgrace) file format produced by gromacs

    XVG format is rather complex, may have multiple sequential entries. And there already
    exists an interpreter {ref}, so no point to reimplement entire thing.
    This is designed to specifically read files produced by gromacs analysis (rmsd, values output, etc..)
    """
    # first we have a bunch of comments. Each line starts with '#'
    line = F.readline().strip()
    while line[0] == '#':
        self.comments.append(line[1:])
        line = F.readline().strip()
    # next it typically has a bunch of grace directives
    if line[0] != '@':
        # we are supposed to have a few headers here, at least column names..
        raise XVG_Error
    # these headers may have some useful info for plotting, but only a few fields are guaranteed
    # and there is a full parser already done apparently (gromacs.formats)
    # so we do a very basic thing here:
    # use x,y lables to populate colIDs and just store the rest
    #
    # 1st @-line is usually title
    self.headers.append(line[1:])
    #
    line = F.readline().strip()
    if line[0:18] == "@    xaxis  label ":
        # we have x and yaxis labels, record these
        self.colID.append('"' + line.split('"')[-2] + '"')
        line = F.readline().strip().split('"')
        self.colID.append('"' + line[-2] + '"')
        line = F.readline().strip()
    else:
        # for compatibility with other formats, we add empty colIDs, even if nothing was found
        self.colID.append("")
        self.colID.append("")
    # we gotta have at least 1 y, so we are safe here,
    # but the rest of colIDs have to wait until we know N of columns
    while line[0] == '@':
        self.headers.append(line[1:])
        line = F.readline().strip()
    # now this should be the start of data block
    items = line.split()
    try:
        self.time.append(float(items[0]))
        for item in items[1:]:
            self.data.append([float(item)])
    except ValueError:
        raise XVG_Error
    # now, after processing the 1st data line, we know N of columns,
    # so we can finish populating the colIDs
    for j in range(2,len(self.data)):
        self.colID.append(self.colID[1])
    # now we are all set with headers and data struct, process the rest of it
    for line in F:
        items = line.split()
        self.time.append(float(items[0]))
        for j in range(len(self.data)):
            self.data[j].append(float(items[j+1]))


def write_xvg_gmx(self, F):
    "write out data in xvg format (gromacs output like)"
    # no special header;
    # comments on top
    for line in self.comments:
        F.write('#' + line + '\n')
    # headers - xmgrace scripting
    for line in self.headers:
        F.write('@' + line + '\n')
    # no column title line; if anything there, it is set via headers scripting
    # finally the data itself
    for i in range(len(self.data[0])):
        # xvgs seem to start with whitespace, try to preserve this in case this matters somewhere
        # actually this happens automatically if every write is preceded by whitespace
        # (which is likely why that format is this way)
        if self.has_time():
            F.write("  {}".format(self.time[i]))
        for j in range(len(self.data)):
            F.write("  {}".format(self.data[j][i]))
        F.write("\n")


def read_HEKA_csv(self, F):
    "reads the csv file exported by HEKA and constructs the proper table"
    reader = csv.reader(F)
    # 1st line is different, do special processing before the cycle
    line1 = next(reader)
    if len(line1) != 1 or line1[0][:6] != "Series":
        raise HEKA_CSV_Error
    last_row_empty = True # to signal the start of new episode
    #
    firstSweep = True
    #iSweep = -1 # N of the episode
    i, NSmpl  = 0, 0 # cycle index and total samples in single episode
    # max i and NSmpl need to match at the end of each episode!
    #
    for row in reader:
        #main cycle
        #print("main cycle, ep ", len(self.data)-1,";  row = ", row)
        if len(row) == 0: #empty line - end of an episode"
            if last_row_empty:
                # two empty lines in a row signal the end of file
                break
            last_row_empty = True
            firstSweep = False
            if len(self.data[-1]) != len(self.time):
                # sweep length mismatch!
                # This will generally create problems for Axon later,
                # so we raise an exception in this version
                #print(self.time)
                #print(self.data)
                raise HEKA_CSV_Error
            #
            continue # processing of the end of an episode finished
        #
        # all the other lines should have 3 elements
        if len(row) != 3:
            raise HEKA_CSV_Error
        #
        # check for possible start of new episode
        if last_row_empty:
            if row[0][:5] == "Sweep":
                # beginning of a new episode/sweep, reset/increment indeces
                self.data.append([])
                #iSweep = len(self.data) - 1
                last_row_empty = False
                # and skip the next line which should contain column headers
                # ATTN!!
                # now, for quickness we just assume time (s) and current (A)
                # add some checks/conversions to produce more generic code if/when needed!!
                if next(reader)[0] != "Index": raise HEKA_CSV_Error
                continue
            else:
                # unexpected mismatch of format
                raise HEKA_CSV_Error
        #
        # the regular iteration
        if firstSweep:
            # time in milliseconds by convention
            self.time.append(float(row[1])*1000)
        # current in pA by convention
        self.data[-1].append(float(row[2])*1e12)
    #
    # done with data, need to recreate headers and column names
    # just use most common ATF values here for Episodic data..
    self.headers.append('"AcquisitionMode=Episodic Stimulation"')
    self.colID.append('"Time (ms)"')
    for i in range(len(self.data)):
        self.colID.append('"pA"')
    # should be all done now


