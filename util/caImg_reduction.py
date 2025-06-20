#! /usr/bin/python
"""Process the calcium imaging log file to create csv data easily understood by graph programs.

Removes all the "extras" and outputs just the titles and the data, in matching columns, csv format.
Also drops all the region averages and only outputs the ratios.
"""

import sys,argparse, csv


def ProcessCommandLine():
    "goes through command line, returns opts,FileName pair"
    #lets parse the arguments
    parser = argparse.ArgumentParser(description='''Process the Ca2+ imagindlog file to output csv data understood by graph softwre.

Removes all the "extras" and outputsjust the titles and the data, in matching columns, csv format.
Also drops all the region averages and only outputs the ratios.''')
    parser.add_argument('fn', help="file name to process; use '-' for standard input")
    parser.add_argument('-d', action='store_true', help="generic data file, no extra headers, just column select")
    parser.add_argument('-k', action='store_true', help="keep all: keep all data columns, not just ratios")
    parser.add_argument('-o', help="name of output file. If omitted, creates a file with a csv extension")
    parser.add_argument('-z', action='store_true', help="keep zero: do not discard the baseline region, the 0.0 column")
    #parser.add_argument('-g', default='grid_table.lst', help="name of the file with the grid of the aspect factors, defaults to 'grid_table.lst'")
    #parser.add_argument('-t', default=0.0, help="start at particular time, default = 0, if omitted keep reported wall time'")
    #parser.add_argument('-s', help="skip S header lines")
    return parser.parse_args()



# ------------------------------------------------
#
# NOTE: the zero time button can be pressed at any time apparently!
# when pressed before start of acquisition is seems to always go as line #3
# all further presses, however, seem to get dumped into file immediately, resetting the clock each time
# so need to check for rezero time press and keep track of actual run time in some way..
#
# This script will implement the most common use-case, of uniform time starting at 0, with a fixed step
# and just accountingfor user clicking rezero time button indisciminantely.
# Anyway, each click leads to loss of info and unclear intent, so better be handled manually..
# The algorithm is:
# 1. calculate the interval
# 2. autocalcall further times, ignoring 1st column
#
# -------------------------------------------------


##########################
### main block ###

# arguments and prepping
args = ProcessCommandLine()
#print("args.d =", args.d)
#print("args.k =", args.k)

if args.fn == '-':
    Fin = sys.stdin
else:
    Fin = open(args.fn, encoding='latin-1') #ATTN! may need adjusting if used on other PC


if args.o:
	Fout = open(args.o, mode='w')
else:
	Fout = open(args.fn[:-3]+"csv", mode='w')


### start the reading ###
reader = csv.reader(Fin)
line = next(reader)

# proc the headers
# first stripping the region definitions and other cruft
header = line[0][:4]
#print(line, "\n'", header, "'", sep='')

if not args.d and (header == "File"):
    "regular log file supposedly, skip extra headers"
    #print("log file detected, skipping extra headers")
    # skip descriptor lines
    line = next(reader)
    if line[0][:4] != "Date":
        print("format mismatch detected (line 2 should contain Date), aborting!")
        sys.exit()
    line = next(reader)
    while line[0][:4] != "Regi":
        # optional line, seems only to be added on "zero watch", seems to always start with 0.00, but safer to check for Region
        # also, there are cases with multiple resets at this position. The program seems to generate reset notification line
        # for each press of a button and dump here all presses done before actual start
        line = next(reader)
    #
    # read and skip regions (add region count? no direct use)
    while line[0][:6] == "Region":
        line = next(reader)


### titles row ###
#print(line)
if line[0][:4] != "Time":
    print("format mismatch detected (titles line expected), aborting!")
    sys.exit()

# if we got here, we are done with headers and this is a title line
idxRatios = [i for i in range(len(line)) if line[i][-3:] == 'R1"'] # list of indices containing ratios
#print(idxRatios)
if args.k:
    idxToTake = range(1,len(line)) # taking all (except 1st, which is time)
else:
    idxToTake = idxRatios


###########################
### data block analysis ###
line = next(reader)
timeStart = float(line[0])
values = [] # list of individual rows of data (lists)
values.append([str(float(line[i])) for i in idxToTake]) # split off for readability (instead of [ [] ])
# NOTE: ATTN!! values is a list of row, not columns, like in TabData !!! ###
print("t0 = ", timeStart, ";  vals = ", values)
# we need to collect all data until we determine timestep, before we can output

# below is handling for arbitrary time start, which is niche, just commenting out for now..
# need to get initial time, so special proc for 1st data line
#
# if args.t:
#     timeStart = args.t
# else:
#     timeStart = float(line[0])

# The calc step part
timeReset = False
timeCur = timeStart # can just reuse timeStart,
# the initial idea was to reset the start point and subtract it, to keep minor variation of each reading timing
# but with the arbitrary and multiple time resets this is impractical
#
# 0-time press can and does come in some files between rows 1 and 2, and can, in principle, come between many
# consequtive lines. So need to loop until we find at least 2 uninterupted data points..
for line in reader:
    if len(line) == 2 and line[1][2:7] == "Clock":
        # time was reset, set flags and skip the line; there can be multiple resets in a row, so nothing fancy here
        timeReset = True
        continue
    # if we are here, then supposedly we have a data row
    time = float(line[0])
    values.append([str(float(line[i])) for i in idxToTake])
    if timeReset:
        #yet another interrupted line, store data and keep going
        timeCur = time
        timeReset = False
        #continue # NOTE: implicit as this is the end of the loop, but don't forget to uncomment if logic changes!'
    else:
        # finally two consequtive data rows, can end this loop
        timeStep = round(time - timeCur, 2)
        break
print("values after step detection: ", values)

# before starting output, we need to check and process the 0.0 - baseline region
# normally this is the 1st data (not time) column, but program allows arbitrary entry
# so we have to scan and mark accordingly
# On the other hand, there supposed to be only 1 such zone, which implies
# either a single or up to 3 *consequtive* columns with 0s
idxZero = []
for i in range(len(values)):
    if values[i][0] == 0.0: # use precise ==, to only match explicit 0.0 in background columns
        idxZero.append(i)
#
if len(idxZero) > 0:
    idxZeroRemove = [] #should not remove entries of a list inside a cycle over it
    for i in range(len(idxZero)):
        for j in range(1,len(values[0])):
            if values[idxZero[i]][j] != 0.0:
                idxZeroRemove.append(i)
    if len(idxZeroRemove) > 0:
        # should pretty much never get here
        idxZero = [x for x in idxZero if x not in idxZeroRemove]
#
if len(idxZero) > 3:
    # may want to expand tests, e.g. for sequential indices
    print("Data consistency check: more than 3 columns for background!!\nAborting..")
    sys.exit()
#
# 0s are detected and validated (very basic check atm),
# remove 0 columns from idxToTake and values
idxToTake = [x for x in idxToTake if x not in idxZero]
values    = [[y for y in x if y not in idxZero] for x in values]
print("values with 0s eliminated", values)
sys.exit()



#########################################
### Output start ###
#
# First the title row
# create it here, as idxToTake has only been stabilized above
if args.k:
    newTitle = ["time"] + [line[i].strip(' "') for i in idxToTake]
else:
    newTitle = ["time"] + [line[i].split()[0][1:] for i in idxToTake]
#print(",".join(newTitle) + "\n")
Fout.write(",".join(newTitle) + "\n")

# we got our timestep and zero columns, now prep and output the collected data rows
#
for i in range(len(values)):
    # values copntains list of columns, need to iterate over rows
    for j in range(len(values[0])):
        Fout.write(",".join([str(i*timeStep)] + values[i]) + "\n")

# the rest of file contains just the data rows, so use for iterator until EOF
Nrow = len(values) - 1 # 0-base indexing
for line in reader:
    # program seems to like to dump bunch of "events" at random into the log file,
    # so, check for time reset or some event dump and just ignore it
    #print(line[1][2:7])
    if len(line) == 2 and line[1][1] == '"':
        #print("short line: ", line, ";  ", line[1][1])
        continue
    # time = round(float(line[0]) - timeStart, 2) # stale, we regenerate time
    Nrow += 1
    rowVals = [str(float(line[i])) for i in idxToTake]
    Fout.write(",".join([str(Nrow*timeStep)] + rowVals) + "\n")

Fout.close()
Fin.close()
