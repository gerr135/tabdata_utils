#! /usr/bin/python
'''Recombine xvg files holding rmsd calcs for individual runs into structure-related bundles.
The indices are specific for a certain collection of runs,
but should be extendable to 2 classes of trajectories in general
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

import sys, argparse
import os, subprocess
from lib import tabdata, tabdata_io

# Here the curve classes are defined
#Colors=[1,2,3] # a list of per-class colors
FNclasses = [["b1","b2","b3","b4"], ["c1","c2","c3"]] # "file name classes"

Colors=[1,2] # a list of per-class colors
#FNclasses = [["b1","b4"], ["c1","c3"]] # "file name classes"

# png layout for gracebat
# the image grid; set these accordingly to fit all the pairs
grcNrow, grcNcol = 4,2

# scaling parameters maxT and max amplitude
IgrcT, IgrcA = 100, 1.5



FNStub = "all-"
GraceBase = "grace_"   # basename for grace list files

# the N of classes should match colors
if len(Colors) != len(FNclasses):
    print("incorrect parameters defined in script file (check the top)")
    print("len(Colors)  should match len(FNclasses)")
    sys.exit()


Descr = '''Recombine xvgs for individual rmsds into bundles, setting colors by classes.

ATTN! All file patterns and colors are preset inside. The current patters are as follows:
'''
for i in range(len(FNclasses)):
    Descr += "class: {};  color: {};  list: {}\n".format(i, Colors[i], FNclasses[i])

Descr += '''
If you need to change that, edit the code directly.
The output goes to fnbase+stub+"by_str"/"by_trj"+fclass+".xvg".
You can change the stub part with -s option.
'''
Descr += "Active output pattern looks like: base-" + FNStub + "by_str.xvg\n"

def ProcessCommandLine():
    "goes through command line, returns opts,FileName pair"
    #lets parse the arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, description=Descr)
    parser.add_argument('fb', help="file name base to process")
    parser.add_argument('-s', default=FNStub, help="file name pattern to append (in case multiple reruns with different subsets over the same files are needed)")
    #parser.add_argument('-grc', action='count', help="create the grace_str and grace_trj list files and the")
    parser.add_argument('-gas', action='store_true', help="autoscale y value for grace batch files (ignore value set in the script)")
    parser.add_argument('-v',   action='count', help="be verbose")
    return parser.parse_args()



Tokens = [item for sublist in FNclasses for item in sublist]
ColorDict = {}
for i in range(len(Colors)):
    for fnc in FNclasses[i]:
        ColorDict[fnc] = Colors[i]


class Gracebat:
    "just a way to combine common code for gracebat file creation to avoid duplication"
    def __init__(self, fn):
        '''init internal vars, open file and write opening stuff.
        fn - base of the generated gracebat and png files'''
        self.fn = fn + ".gracebat"
        self.F = open(self.fn, mode='w')
        self.F.write('gracebat -fixed 1600 1100 -pexec "arrange ({},{},.1,.1,.1)" -hdevice PNG'
                ' -hardcopy -printfile {} '.format(grcNrow, grcNcol, fn + ".png"))
        self.counter = 0;
        self.grcT = IgrcT
        self.grcA = IgrcA

    def setScale(self,t,a):
        "set the local scale params"
        self.grcA = a
        self.grcT = t

    def append(self, fn):
        "append file string"
        self.F.write("-graph {} -nxy {} -world 0 0 {} {} ".format(self.counter, fn, self.grcT, self.grcA))
        self.counter += 1

    def finish (self):
        "close the file and call gracebat to generate png"
        self.F.close()
        subprocess.run(["sh",self.fn])


def combine_files(inOrder, GG):
    '''core method, does all the reading and recombining.
    inOrder: Boolean, controls the order of tokens in cycles
    GG: Gracebat, pass the gracebat handling class instance'''
    # set the name consts:
    if inOrder: byStr = "by_str-"
    else: byStr = "by_trj-"
    #
    for tok in Tokens:
        #get the 1st file in to serve as a base to collate upon
        if inOrder:
            combo = tok+"_"+Tokens[0]
            title = tok
        else:
            combo = Tokens[0]+"_"+tok
            title = Tokens[0]
        #
        with open(args.fb+combo+".xvg") as F:
            data = tabdata.TabData()
            tabdata_io.read_xvg_gmx(data, F)
            # disable subtitle and replace title with something meaningful
            for i in range(len(data.headers)):
                if data.headers[i].find("   title") != -1:
                    data.headers[i] = '    title "{}"'.format(title)
                if data.headers[i].find("subtitle") != -1:
                    data.headers[i] = ' subtitle ""'
            # set the color of the 1st dataset
            data.headers.append("s0 line color {}".format(ColorDict[Tokens[0]]))
        # now process the rest
        for i in range(1,len(Tokens)):
            if inOrder: combo = tok+"_"+Tokens[i]
            else: combo = Tokens[i]+"_"+tok
            with open(args.fb+combo+".xvg") as F:
                newdat = tabdata.TabData()
                tabdata_io.read_xvg_gmx(newdat, F)
                #if (newdat.Npts != data.Npts):
                    #print("lengths of supplied files do not match!")
                    #sys.exit()
                # now append column
                data.append_columns(newdat, ncols=1, shorten=True)
                data.headers.append("s{} line color {}".format(i, ColorDict[Tokens[i]]))
                #data.headers.append("s{} hidden false".format(i))
                #data.headers.append("s{} type xy".format(i))
        # now we are ready to output
        with open(outName(tok,byStr), mode='w') as F:
            tabdata_io.write_xvg_gmx(data, F)
        #
        # grace list files
        #if args.grc:
        if args.gas:
            GG.setScale(IgrcT,1.1 * data.max_data())
        GG.append(outName(tok,byStr))

# ------------------------------------------------
#main block
args = ProcessCommandLine()

if args.v:
    print("params check:")
    print("list of file tokens: ", Tokens)
    print("dict of colors:", ColorDict)

def outName(tok, byStr = "by_str-"):
    return args.fb + args.s + byStr + tok + ".xvg"

def outGraceName(byStr):
    return GraceBase + args.fb + args.s + byStr


#if args.grc:
Gs = Gracebat(outGraceName("str"))
Gt = Gracebat(outGraceName("trj"))

# group by structure and by trajectory
combine_files(True, Gs)
combine_files(False, Gt)

#if args.grc:
Gs.finish()
Gt.finish()
