#! /usr/bin/python
'''Perform basic normalization on a data table.

This basically calculates mean in the baseline region, divides all data and (optionally) subtracts 1 (to bring bl to 0).
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

import sys, argparse, math
from lib import tabdata, tabdata_io

File_Formats = ['csv', 'atf', 'xvg']
Stats_list   = ['avg', 'sd',  'sem']
SlistStr = "aden"
StatsMap = {'a':"avg",  'd':"stddev", 'e':"s.e.m.", 'n':"N-entries"}

def ProcessCommandLine():
    parser = argparse.ArgumentParser(description='''Perform basic normalization on a data file.

This basically calculates mean in the baseline region, divides all data by it and (optionally) subtracts 1 (to bring bl to 0).
All calculations are done for each column individually. The baseline region is shared.
Definition of baseline region can be done by either index or time boundaries. These can be combined.
Both can be passed, index (-il or ih) takes precedence over times (-tl, -th), so -tX is ignored in -iX is passed.
Missing boundary index means beginning or end of data.
'''
)
    parser.add_argument('fn',  help="file names to process. Type is determined form the extension or given by an option")
    parser.add_argument('-f', choices=File_Formats, help="specify the input data format")
    parser.add_argument('-o', help="Output to this file. If omitted, stdout")
    parser.add_argument('-il', type=float, help="index of the basline region - low")
    parser.add_argument('-ih', type=float, help="index of the basline region - high")
    parser.add_argument('-s', action='store_true', help="subtract baseline")
    parser.add_argument('-tl', type=float, help="timing of the basline region - low")
    parser.add_argument('-th', type=float, help="timing of the basline region - high")
    parser.add_argument('-nh', action='store_true', help="do not print headers, only numbers (for scripted processing of outputs)")
    parser.add_argument('-v', action='store_true', help="be verbose")
    return parser.parse_args()



# ------------------------------------------------
#main block
args = ProcessCommandLine()

# split off extension from fname
dotpos = args.fn.rfind('.')
FName = args.fn[:dotpos]
FExt  = args.fn[dotpos+1:]

if args.v:print("file name = ", FName, " + ", FExt, ";  subtract baseline=",args.s)

# determine the input format
if args.f:
    fFmt = args.f
else:
    if FExt not in File_Formats:
        print("cannot process input file of type ", FExt)
        sys.exit()
    fFmt = FExt

# read the data
with open(args.fn) as F:
    data = tabdata.from_format(F,fFmt)

# setup boundaries
# most (all?) of the data are going to have a time column (as otherwise x bounds make not much sense).
# So, enforce time column presence if boundaries are pased
if (args.tl or args.th) and not hasattr(data,"time"):
    print("timings are passed, but data has no time column!\nAborting..")
    sys.exit()

# now check the low boundary
if args.il:
    Il = i
elif args.tl:
    # iterate over time - less efficient, but we have no to,dt setup and this handles nonuniform time too..
    for i in range(len(data.time)):
        if data.time[i] >= args.tl:
            Il = i
            break
else:
    Il = 0

# now the high boundary
of args.ih:
    Ih = args.ih
elif args.bh:
    for i in range(Il,len(data.time)):
        if data.time[i] >= args.bh:
            Ih = i
            break
else:
    Ih = len(data.time)
# done with baseline indices

#
# now the normalization

##########################################
## main ##
def calcAvg(data, Il, Ih):
    "calc average per column in a given boundary"
    S=[]
    for i in range(len(data.data)):
        S.append(0)
        for j in range(Il, Ih):
            S[i] += data.data[i][j]
        S[i] /= (Ih-Il)
    return S

def calcSD(data, Il, Ih, avg):
    "standard deviation calc. Il,Ih - boundary indices. Avg - vector of averages (which is goonna be computed already)"
    S=[]
    for i in range(len(data.data)):
        S.append(0)
        for j in range(Il, Ih):
            S[i] += (data.data[i][j] - avg[i])**2
        S[i] = math.sqrt(S[i]/(Ih-Il-1))
    return S

def calcSEMfromSD(Il, Ih, SD):
    "just does rescaling (div by sqrt(N))"
    return [S/math.sqrt(Ih-Il) for S in SD]

def calcSEM(data, Il, Ih, avg):
    "a convenience wrapper calling calcSD and doing rescaling. avg is likely already calculated, so it is passed in"
    return [S/math.sqrt(Ih-Il) for S in calcSD(data,Il,Ih,avg)]

# stats on combined columns
def combineAvg(avg):
    "return mean of multi-mean. This is linear, so we can reuse multicolumn calc"
    return sum(avg)/len(avg)

def calcSDcombo(data, Il, Ih, avg):
    """here we have to calculate separately, as our avg is different: a combo average, not per column.
    Yes, we could do via moments (M1, M2, etc), but this is too basic to worry (and same amount of total computation)
    """
    S=0
    for i in range(len(data.data)):
        for j in range(Il, Ih):
            S += (data.data[i][j] - avg)**2
        S = math.sqrt(S/(len(data.data)*(Ih-Il-1)))
    return S


# main action

# we need avg in any case
avg = calcAvg(data,Il,Ih)
avgC = combineAvg(avg)

if 'd' in StatsStr:
    if args.c: SDC  = calcSDcombo(data,Il,Ih,avgC)
    else: SD  = calcSD(data,Il,Ih,avg)
if 'e' in StatsStr:
    # a small optimization, to avoid double SD calc
    if 'd' in StatsStr:
        if args.c: SEMC = SDC/math.sqrt(Ih-Il)
        else: SEM = calcSEMfromSD(Il,Ih,SD)
    else:
        if args.c: SEMC = calcSDcombo(data,Il,Ih,avgC)/math.sqrt(Ih-Il)
        else: SEM = calcSEM(data,Il,Ih,avg)

# finally otput
if args.o:
    Fout = open(args.f,'w')
else:
    Fout = sys.stdout


# headers
if not args.nh:
    Fout.write("entry   ")
    for l in StatsStr:
        Fout.write(StatsMap[l] + "   ")
    Fout.write("\n")

# actual output
if args.c:
    # we output combined results, 1 line only
    Fout.write((args.e + "   " if args.e else FName + "   "))
    for l in StatsStr:
        if   l == 'a': Fout.write(str(avgC))
        elif l == 'd': Fout.write(str(SDC))
        elif l == 'e': Fout.write(str(SEMC))
        elif l == 'n': Fout.write(str(Ih-Il))
        else: print("unexpected output code")
        Fout.write("  ")
    Fout.write("\n")
else:
    for i in range(len(data.data)):
        Fout.write((args.e + "_" + str(i) + "   " if args.e else FName + "-" + str(i) + "   ") )
        for l in StatsStr:
            if   l == 'a': Fout.write(str(avg[i]))
            elif l == 'd': Fout.write(str(SD[i]))
            elif l == 'e': Fout.write(str(SEM[i]))
            elif l == 'n': Fout.write(str(Ih-Il))
            else: print("unexpected output code")
            Fout.write("  ")
        Fout.write("\n")

if args.o:Fout.close()
