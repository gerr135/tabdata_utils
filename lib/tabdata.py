#
# Tabular (text) data handling classes
# Copyright (C) 2018  George Shapovalov <gshapovalov@gmail.com>
#
# This is the "main" file defining the base class with core handling methods.
# Some useful functionality is defined in separate files.
# However, as this is not too large a collection and to simplify the conversions
# (and since python does not have "real" polymorphism - no class-wide vars)
# we use dymamic method assignment to attach methods defined in other files
# (instead of mix-in, which could be a better choice if this code grows too much)
#
#  NOTE: This should really be redoe using numpy
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

import sys, csv, copy

from .tabdata_common import *


class TabData:
    """Base data handling class. Keeps data in one place and provides basic access/features.
    Data layout:
    Data is organized in columns. There is an optional "special" time column.
    Data indexing convention (self.data and self.time fields):
        N data points per each column, M columns.
        so time[0..N-1]; data[0..M-1] [0..N-1]; 1st - column index, 2nd - data point in column
        so normally time[i], data[j][i] would be (x,y) for a specific point
        i - data index; i in [0..N-1]
        j - value (column) selection index; j in 0..M-1
    Also provides storage space for extras:
        colID    - textual name for every column (including time if present). Should match width.
        comments - some data formats provide comment entries
        headers  - some formats have "special text fields" used by rendering engine (e.g. xvg or atf)

    some NOTE s:
    In general a "perfect rectangle" data layout is expected. However sometimes
    an uneven csv file is passed or we may need to combine files with different column length.
    A basic provision (essentially via lax checks) is made in order to try to support this.
    Core funtionality focuses on IO only anyway and does not hide data.
    So all the implementation details of data mangling is up to the final scripts..
    """
    def __init__(self, no_time=False, strict_rect = True):
        """Empty field constructor based on generic data model.
        Parameters:
            no_time     - controls creation of a time column. Default yes.
            strict_rect - whether to enforce matching length on all columns.
                          when set to True, checks are performed and exceptions are raised..
        """
        # these (empty) assignments lay out general data representation
        self.strict_rect = strict_rect
        self.comments = [] # some formats may allow a few lines of comments at the top
        self.headers  = [] # some descriptive info of consequence
        self.colID = [] # list of strings representing column names, should match data[+time] in size
        self.data  = [] # list of columns, each holding a single "vector" - list of values
        if not no_time:
            self.time = [] # most files are gonna have special 1st column;


    @property
    def Npts(self):
        """the length of data - N points (or rows).
        NOTE: this assumes "perfect rectangle" (and thus just returns length of data[0]),
        but enfroces no checks. So, getting individual sizes is possible, but has to be done directly
        """
        return len(self.data[0])

    @property
    def Nvars(self):
        "the number of vars (columns) - *not counting* time (1st col)"
        return len(self.data)

    def has_time(self):
        "returns bool indicating if time column is present"
        return hasattr(self,"time")

    def max_in_col(self, ncol):
        "returns max value in a given column"
        return max(self.data[ncol])

    def min_in_col(self, ncol):
        "returns max value in a given column"
        return min(self.data[ncol])

    def max_data(self):
        "returns overal max value in data"
        return max(map(max, self.data))

    def min_data(self):
        "returns overal max value in data"
        return min(map(min, self.data))

    def change_comments(self, comments, clear=False):
        "append or replace (if clear) by list of comment strings"
        if clear:
            self.comments = []
        self.comments.extend(comments)

    def change_headers(self, headers, clear=False):
        "append or replace (if clear) by list of comment strings"
        if clear:
            self.headers = []
        self.headers.extend(headers)

    def regenerate_time_uniform(self, N=0, t0=0, dt=0):
        """Regenerate the time column.
        Obviously this should only be called when no_time == False.
        params:
            N  - generate N total points. Use Npts if omitted
            t0, dt - initial time and step
            If both t0 and dt are 0 then attempt to extend the existing time column.
        """
        if not hasattr(self,"time"):
            raise TabData_Error
        if (t0 == 0) and (dt == 0):
            if len(self.time) < 1:
                raise TabData_Error
            else:
                t0 = self.time[0]
        if dt == 0:
            if len(self.time) < 2:
                raise TabData_Error
            else:
                dt = self.time[1] - self.time[0]
        if N == 0:
            N = self.Npts
        # all params set, ready to gerenate
        self.time=[]
        for i in range(N):
            self.time.append(t0 + i*dt)

    def append_column(self, column, colStr = "", shorten = False):
        """append a passed column = list of numbers to the data.
            If need to append a single column of another tabdata, pass item.data[X]
            or (better) use append_columns..
        colStr - is a string to be passed to colID
        shorten - used only when self.strict_rect == True.
            Then, if True, all columns (including this data object) are shortened to minimal length
            if shorten == False, DimensionMismatch is rased
        """
        # first do all the checks that can raise exception,
        # so that either all modifications succeed, or we leave our object untouched.
        if (self.colID != []) and (colStr == ""):
            raise TabData_Error
        if self.strict_rect and not shorten and (len(column) != self.Npts):
            raise DimensionMismatch
        # done with checks, do the colIDs
        if self.colID != []:
            self.colID.append(colStr)
        #
        Npts = min(self.Npts, len(column))
        if (not self.strict_rect) or (len(column) == self.Npts):
            self.data.append(column)
        else:
            # data differ in length and we shorten
            if len(column) > self.Npts:
                # either we shorten a single new column
                self.data.append(column[:self.Npts])
            else:
                # or or data is too long, so we reconstruct all data
                newdata = []
                for old in self.data:
                    newdata.append(old[:Npts])
                newdata.append(column)
                self.data = newdata


    def append_columns(self, passed, nfirst = 0, ncols = 0, shorten = False):
        '''append ncols columns from a passed Tabular_Data starting with nfirst.
        NOTE s:
            This does not replace/extend time column! Time is always discarded.
            Use separate methods for handling time..
        nfirst counts from the start of data block (so 0 means the 1st data column)
        ncols==0 means add all;
        shorten - same logic (per column) as in append_column
        '''
        #print("merging data with {} and {} rows".format(self.Npts, passed.Npts))
        if ncols == 0:
            nlast = len(passed.data)
        else:
            nlast = nfirst + ncols
        #
        if nlast > len(passed.data):
            raise TabData_Error
        #
        pNptsMax = max(map(len,passed.data[nfirst:nlast]))
        pNptsMin = min(map(len,passed.data[nfirst:nlast]))
        if self.strict_rect and not shorten and (pNptsMax != self.Npts) and (pNptsMin != self.Npts):
            raise DimensionMismatch
        #
        # set the colID
        self.colID.extend(passed.colID[nfirst:nlast])
        #
        if (not self.strict_rect) or ((pNptsMin == self.Npts) and (pNptsMax == self.Npts)):
            self.data.extend(passed.data[nfirst:nlast])
        else:
            # need to do length checks here
            Npts = min(pNptsMin, self.Npts)
            if Npts < self.Npts:
                # before appending new data, we need to shorten ours
                newdata = []
                for old in self.data:
                    newdata.append(old[:Npts])
                self.data = newdata
            # now we can add new data of appropriate length
            for i in range(nfirst,nlast):
                self.data.append(passed.data[i][:Npts])


    def append_rows(self, passed, at = 0, nfirst = 0, ncols = 0):
        '''extend self.data by appending data in 'passed' per-column after the end.
        NOTE:
            1. If strict_rect is set then time (if exists) is auto-regenerated, to keep data consistent.
               If not set, then it is responsibility of a caller to handle time separately.
            2. If self.strict_rect then some consistency checks are performed,
               so you can stack only proper complete blocks..
            3. ColIDs are discarded, comments and headers are appended.
        NOTE: time is not copied in this code!! (but then it should be refactored anyway..)
        params:
            at: add at this column in self.data
            nfirst, ncol: refer to passed
            nfirst counts from the start of data block (so 0 means the 1st data column)
            ncols==0 means use all;
        '''
        #print("extending data of {}x{} by new block of {}x{} rows".format(self.Nvars,self.Npts, passed.Nvars, passed.Npts))
        if ncols == 0:
            nlast = len(passed.data)
        else:
            nlast = nfirst + ncols
        #
        if nlast > len(passed.data):
            raise TabData_Error
        #
        pNptsMax = max(map(len,passed.data[nfirst:nlast]))
        pNptsMin = min(map(len,passed.data[nfirst:nlast]))
        if self.strict_rect and (
                (pNptsMax != pNptsMin ) or
                (at != 0) or (nfirst != 0)
                or (nlast != self.Nvars) ):
            raise DimensionMismatch
        #
        # expand comments and headers
        self.comments.extend(passed.comments)
        self.headers.extend(passed.headers)
        # append the data
        for j in range(nlast-nfirst):
            self.data[at+j].extend(passed.data[nfirst+j])
        # if strict_rect then we need to regenerate time, to keep data always consistent
        if self.strict_rect and hasattr(self, "time"):
            self.regenerate_time_uniform()


    def extract_rows(self, Nfrom, Nto = 0, do_headers = True):
        "create a new table with same heders but containing only rows from..to"
        newdat = TabData(not hasattr(self, "time"), self.strict_rect)
        newdat.colID    = copy.deepcopy(self.colID)
        if do_headers:
            newdat.comments = copy.deepcopy(self.comments)
            newdat.headers  = copy.deepcopy(self.headers)
        else:
            newdat.comments = []
            newdat.headers  = []
        # make empty data columns
        for i in range(self.Nvars):
            newdat.data.append([])
        # now extract and carry over proper data..
        if Nto == 0:
            Nto = self.Npts
        for i in range(Nfrom, Nto):
            for j in range(len(self.data)):
                #print("i={}, j={}".format(i,j))
                newdat.data[j].append(self.data[j][i])
            if hasattr(self, "time"):
                newdat.time.append(self.time[i])
        # all done, return constructed object
        return newdat


#######################################################
#  core class expansion (may be moved to __init__.py ?)

# attach IO methods (dynamic addition)
from .tabdata_io import *

TabData.read_csv  = read_csv
TabData.write_csv = write_csv

TabData.read_atf  = read_atf
TabData.write_atf = write_atf

TabData.read_xvg  = read_xvg_gmx
TabData.write_xvg = write_xvg_gmx

TabData.read_HEKA_csv  = read_HEKA_csv


# constructor functions
def from_csv(F, Separator = ',', no_time=False, strict_rect = True):
    "read csv file and return constructed Tabular_Data object"
    data = TabData(no_time = no_time, strict_rect = strict_rect)
    data.read_csv(F, Separator)
    return data

def from_atf(F, strict_rect = True):
    data = TabData(strict_rect = strict_rect)
    data.read_atf(F)
    return data

def from_HEKA_csv(F, strict_rect = True):
    data = TabData(strict_rect = strict_rect)
    data.read_HEKA_csv(F)
    return data

def from_xvg(F, strict_rect = True):
    data = TabData(strict_rect = strict_rect)
    data.read_xvg(F)
    return data


TabData.constructors = {
    "csv":from_csv,"atf":from_atf,
    "xvg":from_xvg,"heka_csv":from_HEKA_csv
    }

def from_format(F, fmt, strict_rect = True):
    return TabData.constructors[fmt](F,strict_rect = strict_rect)

